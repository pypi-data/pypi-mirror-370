from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple, Optional

from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

from .adapters import CAdapter, PythonAdapter, LanguageAdapter
from .db.sqlite import HashDatabase
from .editing.editor import Editor, PlanEdit, ReplaceEdit
from .llm.ollama import OllamaClient


SUPPORTED_EXTENSIONS = {
    ".c": CAdapter,
    ".h": CAdapter,
    ".py": PythonAdapter,
}


def discover_files(root: Path) -> List[Path]:
    ignore_file = root / ".gitignore"
    spec = (
        PathSpec.from_lines(GitWildMatchPattern, ignore_file.read_text().splitlines())
        if ignore_file.exists()
        else None
    )
    paths: List[Path] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if spec and spec.match_file(str(p.relative_to(root))):
            continue
        if p.suffix in SUPPORTED_EXTENSIONS:
            paths.append(p)
    return paths


def pick_adapter(path: Path) -> LanguageAdapter | None:
    cls = SUPPORTED_EXTENSIONS.get(path.suffix)
    return cls() if cls else None


def extract_doc_comment_language_style(language_name: str) -> str:
    # For C: prefer block comments with leading * lines
    if language_name == "c":
        return "block"
    # For Python we use triple-quoted strings as docstrings
    if language_name == "python":
        return "docstring"
    return "block"


def build_comment_block_with_tree_sitter(
    content: str, indentation: str = "", adapter=None
) -> str:
    """Build comment block using tree-sitter analysis of the content."""
    if not content.strip():
        return ""

    # Parse the content using adapter's language to analyze structure
    content_bytes = content.encode("utf-8")

    # Use tree-sitter to analyze the content structure
    if adapter and hasattr(adapter, "parser"):
        if isinstance(adapter, PythonAdapter):
            # Build a properly indented triple-quoted docstring
            return _build_python_docstring_with_tree_sitter(
                content, indentation, adapter
            )
        else:
            parsed = adapter.parser.parse(content_bytes)
            # Check if the content already contains a complete block comment using tree-sitter
            comment_nodes = find_comment_nodes_in_tree(parsed, content_bytes)
            if comment_nodes:
                for _s, _e, comment_text in comment_nodes:
                    if comment_text.strip().startswith(
                        "/*"
                    ) and comment_text.strip().endswith("*/"):
                        return _indent_existing_block_comment(comment_text, indentation)
            return _build_new_block_comment_with_tree_sitter(
                content, indentation, adapter
            )

    # Fallback to original logic if no adapter available
    return build_comment_block_fallback("c", content, indentation)


def _indent_existing_block_comment(comment_text: str, indentation: str) -> str:
    """Indent an existing block comment using tree-sitter-aware indentation."""
    lines = comment_text.splitlines()
    if not lines:
        return ""

    # Indent each line properly
    indented_lines = []
    for line in lines:
        if line.strip():  # Non-empty line
            indented_lines.append(indentation + line)
        else:  # Empty line
            indented_lines.append(indentation)

    # Ensure proper termination with newline
    result = "\n".join(indented_lines)
    if not result.endswith("\n"):
        result += "\n"

    return result


def _build_new_block_comment_with_tree_sitter(
    content: str, indentation: str, adapter
) -> str:
    """Build a new block comment using tree-sitter analysis of the content structure."""
    # For comment building, we want to include all content as documentation
    # Tree-sitter analysis is more useful for sanitization, not for building comments
    lines = content.splitlines()
    if not lines:
        return ""

    # Build the block comment - include all content as documentation
    body_lines = []
    for line in lines:
        stripped = line.rstrip()
        if stripped:
            body_lines.append(f"{indentation} * {stripped}")
        else:
            body_lines.append(f"{indentation} *")

    return f"{indentation}/**\n" + "\n".join(body_lines) + f"\n{indentation} */\n"


def _build_python_docstring_with_tree_sitter(
    content: str, indentation: str, adapter
) -> str:
    """Build a Python docstring using triple quotes, preserving indentation and sanitizing content."""
    # Sanitize by removing surrounding fences or triple quotes; then wrap with triple quotes
    text = sanitize_llm_comment_with_tree_sitter(content, adapter)
    lines = text.splitlines()
    if not lines:
        return f"{indentation}" + '"""\n"""\n'
    escaped: list[str] = []
    for line in lines:
        # Avoid ending triple-quote sequences inside the docstring
        escaped.append(line.replace('"""', "\u201c\u201c\u201c"))
    body = "\n".join(
        f"{indentation}{line_escaped}" if line_escaped else f"{indentation}"
        for line_escaped in escaped
    )
    return f'{indentation}"""\n{body}\n{indentation}"""\n'


def _walk_tree(node):
    """Helper function to walk tree-sitter nodes."""
    stack = [node]
    while stack:
        current = stack.pop()
        yield current
        for child in reversed(current.children):
            stack.append(child)


def build_comment_block_fallback(
    language_name: str, content: str, indentation: str = ""
) -> str:
    """Fallback implementation for build_comment_block when tree-sitter is not available."""
    style = extract_doc_comment_language_style(language_name)
    stripped = content.strip()
    # If the model returned a full block comment, indent it and return
    if stripped.startswith("/*"):
        # Ensure newline termination and indent each line
        text = content
        if not text.endswith("\n"):
            text += "\n"
        indented = "\n".join(
            (indentation + line) if line else line for line in text.splitlines()
        )
        if not indented.endswith("\n"):
            indented += "\n"
        return indented
    if style == "docstring":
        lines = [line.rstrip() for line in content.splitlines()]
        body = "\n".join(
            f"{indentation}{line}" if line else f"{indentation}" for line in lines
        )
        return f'{indentation}"""\n{body}\n{indentation}"""\n'
    if style == "block":
        lines = [line.rstrip() for line in content.splitlines()]
        if not lines:
            return ""
        body = "\n".join(
            f"{indentation} * {line}" if line else f"{indentation} *" for line in lines
        )
        return f"{indentation}/**\n{body}\n{indentation} */\n"
    # fallback
    return content


def build_comment_block(language_name: str, content: str, indentation: str = "") -> str:
    """Build comment block using tree-sitter analysis."""
    return build_comment_block_with_tree_sitter(content, indentation, None)


def sanitize_llm_comment_with_tree_sitter(raw: str, adapter=None) -> str:
    """Sanitize LLM comment using tree-sitter analysis."""
    if not raw.strip():
        return raw.strip()

    # Parse using the adapter's language to analyze structure
    raw_bytes = raw.encode("utf-8")

    if adapter and hasattr(adapter, "parser"):
        if isinstance(adapter, PythonAdapter):
            # For Python, strip surrounding code fences or triple quotes, keep inner text
            return _sanitize_python_text(raw)
        else:
            parsed = adapter.parser.parse(raw_bytes)
            comment_nodes = find_comment_nodes_in_tree(parsed, raw_bytes)
            if comment_nodes:
                _s, _e, comment_text = comment_nodes[0]
                return _sanitize_comment_node_content(comment_text, adapter)
            return _sanitize_text_content_with_tree_sitter(raw, adapter)

    # Fallback to original logic if no adapter available
    return sanitize_llm_comment_fallback(raw)


def _sanitize_comment_node_content(comment_text: str, adapter) -> str:
    """Sanitize content from a tree-sitter comment node."""
    # Check if the comment contains code fences
    if "```" in comment_text:
        # Parse the comment to find fence boundaries
        lines = comment_text.splitlines()
        start_idx = 0
        end_idx = len(lines)

        # Find opening fence
        for i, line in enumerate(lines):
            if line.strip().startswith("```"):
                start_idx = i + 1
                break

        # Find closing fence
        for i in range(len(lines) - 1, start_idx - 1, -1):
            if lines[i].strip().startswith("```"):
                end_idx = i
                break

        # Extract content between fences
        content_lines = lines[start_idx:end_idx]
        comment_text = "\n".join(content_lines)

    # Remove existing block comment markers using tree-sitter analysis
    if comment_text.strip().startswith("/*") and comment_text.strip().endswith("*/"):
        # Parse to find the inner content
        inner_content = comment_text.strip()[2:-2]  # Remove /* and */

        # Clean up the inner content
        inner_lines = inner_content.splitlines()
        cleaned_lines = []

        for line in inner_lines:
            stripped = line.strip()
            if stripped.startswith("*"):
                stripped = stripped[1:].lstrip()
            cleaned_lines.append(stripped)

        # Join and clean up any remaining asterisk markers
        result = "\n".join(cleaned_lines).strip()
        # Remove any remaining asterisk markers that might be in the middle
        result = result.replace(" * ", " ").replace("* ", "").replace(" *", "")
        return result

    return comment_text.strip()


def _sanitize_text_content_with_tree_sitter(text: str, adapter) -> str:
    """Sanitize text content using tree-sitter analysis."""
    # Use tree-sitter to identify and remove problematic structures
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line_bytes = line.encode("utf-8")
        line_tree = adapter.parser.parse(line_bytes)

        # Check if this line contains code fences or comment markers
        if (
            "```" in line
            or line.strip().startswith("/*")
            or line.strip().endswith("*/")
        ):
            continue

        # Check if this line contains actual content (not just whitespace or markers)
        has_content = any(
            node.type not in ["comment", "preproc"]
            for node in _walk_tree(line_tree.root_node)
        )

        if has_content or line.strip():
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def sanitize_llm_comment_fallback(raw: str) -> str:
    """Fallback implementation for sanitize_llm_comment when tree-sitter is not available."""
    text = raw.strip()
    if not text:
        return text
    # Strip surrounding triple backtick fences
    lines = text.splitlines()
    if lines and lines[0].lstrip().startswith("```"):
        # drop first line
        lines = lines[1:]
        # drop until closing fence
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
    text = "\n".join(lines).strip("\n")
    if not text:
        return text
    # Strip existing block comment markers
    if text.lstrip().startswith("/*") and text.rstrip().endswith("*/"):
        # remove first and last markers
        inner = text.strip()
        # remove starting /* and trailing */
        if inner.startswith("/*"):
            inner = inner[2:]
        if inner.endswith("*/"):
            inner = inner[:-2]
        inner_lines = [ln.rstrip() for ln in inner.splitlines()]
        cleaned: list[str] = []
        for ln in inner_lines:
            stripped = ln.lstrip()
            if stripped.startswith("*"):
                stripped = stripped[1:].lstrip()
            cleaned.append(stripped)

        # Join and clean up any remaining asterisk markers
        result = "\n".join(cleaned).strip()
        # Remove any remaining asterisk markers that might be in the middle
        result = result.replace(" * ", " ").replace("* ", "").replace(" *", "")
        return result
        text = "\n".join(cleaned).strip("\n")
    return text


def _sanitize_python_text(raw: str) -> str:
    text = raw.strip()
    if not text:
        return text
    lines = text.splitlines()
    # Remove fenced code blocks if present
    if lines and lines[0].lstrip().startswith("```"):
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
    text = "\n".join(lines).strip("\n")
    # Strip surrounding triple quotes if present
    for quote in ('"""', "'''"):
        if text.startswith(quote) and text.endswith(quote):
            inner = text[len(quote) : -len(quote)]
            return inner.strip()
    return text


def sanitize_llm_comment(raw: str) -> str:
    """Sanitize LLM comment using tree-sitter analysis."""
    return sanitize_llm_comment_with_tree_sitter(raw, None)


def get_indentation_from_tree_sitter(source: bytes, node, adapter) -> str:
    """Get indentation using tree-sitter by finding the line start position."""
    # Find the start of the line containing this node
    line_start_byte = source.rfind(b"\n", 0, node.start_byte) + 1
    if line_start_byte == 0:  # No newline found, start from beginning
        line_start_byte = 0

    # Get the whitespace from line start to node start
    indent_bytes = source[line_start_byte : node.start_byte]
    indent_str = indent_bytes.decode("utf-8", errors="ignore")

    # Extract only the leading whitespace
    return indent_str[: len(indent_str) - len(indent_str.lstrip(" \t"))]


def get_python_docstring_insertion(source: bytes, func_node) -> tuple[str, int]:
    """For a Python function node, compute the indentation for the docstring and the byte offset to insert it.

    In Python, the docstring should be inserted right after the function signature (after the colon and newline)
    with the same indentation as the function body statements.
    """
    # Find the block child
    block = None
    for child in func_node.children:
        if child.type == "block":
            block = child
            break
    if block is None:
        # Fallback: insert right after the function header
        # Indentation matches the header line indentation plus 4 spaces
        indent = get_indentation_from_tree_sitter(source, func_node, None) + "    "
        return indent, func_node.end_byte

    # Find the first statement in the block to get the proper indentation
    first_stmt = None
    for child in block.children:
        if child.type in (
            "expression_statement",
            "return_statement",
            "pass_statement",
            "if_statement",
            "for_statement",
            "while_statement",
            "try_statement",
            "with_statement",
            "match_statement",
            "function_definition",
            "async_function_definition",
            "class_definition",
            "nonlocal_statement",
            "global_statement",
            "raise_statement",
            "assert_statement",
            "import_from_statement",
            "import_statement",
            "break_statement",
            "continue_statement",
            "decorated_definition",
        ):
            first_stmt = child
            break

    if first_stmt:
        # Get the indentation from the first statement
        indent = get_indentation_from_tree_sitter(source, first_stmt, None)
        # Insert right after the function signature (after the colon and newline)
        # Find the colon token and insert after it
        colon_pos = None
        for child in func_node.children:
            if child.type == ":":
                colon_pos = child.end_byte
                break

        if colon_pos is not None:
            # Insert after the colon, but we need to ensure there's a newline
            # Check if there's already a newline after the colon
            if colon_pos < len(source) and source[colon_pos : colon_pos + 1] == b"\n":
                insert_at = colon_pos + 1  # Insert after the newline
            else:
                insert_at = colon_pos  # Insert right after colon
        else:
            # Fallback: insert at block start
            insert_at = block.start_byte
    else:
        # No statements in block, insert at the beginning of the block
        # Get indentation from the block start
        i = block.start_byte
        indent_chars: list[str] = []
        while i < len(source):
            ch = source[i : i + 1]
            if ch in (b" ", b"\t"):
                indent_chars.append(ch.decode("utf-8"))
                i += 1
                continue
            if ch == b"\n":
                indent_chars.clear()
                i += 1
                continue
            break
        indent = "".join(indent_chars)
        insert_at = block.start_byte

    return indent, insert_at


def find_comment_nodes_in_tree(tree, source: bytes) -> List[Tuple[int, int, str]]:
    """Find all comment nodes in the tree-sitter AST."""
    comments = []
    stack = [tree.root_node]

    while stack:
        node = stack.pop()
        if node.type == "comment":
            comment_text = source[node.start_byte : node.end_byte].decode(
                "utf-8", errors="replace"
            )
            comments.append((node.start_byte, node.end_byte, comment_text))

        for child in node.children:
            stack.append(child)

    return comments


def find_prototype_between_comments_and_function(
    source: bytes, func_node, adapter
) -> Optional[Tuple[int, int]]:
    """Find prototype between comment and function using tree-sitter."""
    # Get the function's parent node to find siblings
    parent = func_node.parent
    if not parent:
        return None

    # Find the comment node that immediately precedes this function
    prev_sibling = func_node.prev_sibling
    if not prev_sibling or prev_sibling.type != "comment":
        return None

    # Check if there's a prototype between the comment and function
    gap_start = prev_sibling.end_byte
    gap_end = func_node.start_byte

    # Parse the gap to see if it contains a prototype
    gap_text = source[gap_start:gap_end].decode("utf-8", errors="ignore").strip()

    # Get function signature for comparison
    signature_node = None
    for child in func_node.children:
        if "declarator" in child.type:
            signature_node = child
            break

    if not signature_node:
        return None

    signature_text = (
        source[signature_node.start_byte : signature_node.end_byte]
        .decode("utf-8", errors="replace")
        .strip()
    )

    # Check if gap contains exactly the signature with semicolon
    if gap_text == f"{signature_text};":
        return (gap_start, gap_end)

    return None


def find_prototype_after_last_comment(
    source: bytes, func_node, adapter
) -> Optional[Tuple[int, int]]:
    """Find prototype after the last comment before function using tree-sitter."""
    # Find the last comment before this function
    parent = func_node.parent
    if not parent:
        return None

    # Walk backwards through siblings to find the last comment
    last_comment_end = None
    current = func_node.prev_sibling

    while current:
        if current.type == "comment":
            last_comment_end = current.end_byte
            break
        current = current.prev_sibling

    if last_comment_end is None:
        return None

    # Check the gap between last comment and function
    gap_start = last_comment_end
    gap_end = func_node.start_byte

    gap_text = source[gap_start:gap_end].decode("utf-8", errors="ignore").strip()

    # Get function signature for comparison
    signature_node = None
    for child in func_node.children:
        if "declarator" in child.type:
            signature_node = child
            break

    if not signature_node:
        return None

    signature_text = (
        source[signature_node.start_byte : signature_node.end_byte]
        .decode("utf-8", errors="replace")
        .strip()
    )

    # Check if gap contains exactly the signature with semicolon
    if gap_text == f"{signature_text};":
        return (gap_start, gap_end)

    return None


def process_file(
    path: Path, db: HashDatabase, llm: OllamaClient, dry_run: bool = False
) -> Tuple[Dict[str, int], List[str]]:
    adapter = pick_adapter(path)
    if adapter is None:
        return {"functions": 0, "new": 0, "updated": 0, "skipped": 0}, []

    source = path.read_bytes()
    tree = adapter.parser.parse(source)

    # Pre-sanitize problematic comments using tree-sitter (C only)
    pre_sanitized_edits: List[ReplaceEdit | PlanEdit] = []
    plans: List[str] = []
    if isinstance(adapter, CAdapter):
        comment_nodes = find_comment_nodes_in_tree(tree, source)
        for start_byte, end_byte, comment_text in comment_nodes:
            if ("```" in comment_text) or (
                "/*" in comment_text[2:] or "*/" in comment_text[:-2]
            ):
                sanitized = sanitize_llm_comment(comment_text)
                if sanitized:
                    node = tree.root_node.descendant_for_byte_range(
                        start_byte, end_byte
                    )
                    indentation = get_indentation_from_tree_sitter(
                        source, node, adapter
                    )
                    new_block = build_comment_block_with_tree_sitter(
                        sanitized, indentation, adapter
                    )
                    pre_sanitized_edits.append(
                        ReplaceEdit(
                            file_path=path,
                            start_byte=start_byte,
                            end_byte=end_byte,
                            content=new_block,
                        )
                    )

    if pre_sanitized_edits and not dry_run:
        Editor().apply(pre_sanitized_edits, dry_run=False)
        source = path.read_bytes()
        # Re-parse after sanitization
        tree = adapter.parser.parse(source)
    elif pre_sanitized_edits and dry_run:
        plans.append(f"sanitize: {path}")

    # Get functions using tree-sitter
    functions = list(adapter.iter_functions(source))

    planned: List[PlanEdit] = []
    new = updated = skipped = 0
    staged_edits: List[ReplaceEdit | PlanEdit] = []

    # First pass: handle updates (existing docs) using tree-sitter
    for func in functions:
        body = adapter.get_function_body(source, func)
        current_hash = db.compute_hash(body)
        record = db.get(path, func.name)
        has_doc = func.has_doc()

        # Find the function node in the tree
        func_node = tree.root_node.descendant_for_byte_range(
            func.full_range.start, func.full_range.end
        )

        # C-only cleanup of prototypes between comment and definition
        if isinstance(adapter, CAdapter):
            if has_doc and func.doc_range:
                prototype_range = find_prototype_between_comments_and_function(
                    source, func_node, adapter
                )
                if prototype_range:
                    if dry_run:
                        plans.append(f"clean: {path} :: {func.name}")
                    else:
                        staged_edits.append(
                            ReplaceEdit(
                                file_path=path,
                                start_byte=prototype_range[0],
                                end_byte=prototype_range[1],
                                content="\n",
                            )
                        )

        if has_doc and record and record.body_hash == current_hash:
            skipped += 1
            continue

        # Get signature using tree-sitter
        signature = source[
            func.signature_range.start : func.signature_range.end
        ].decode("utf-8", errors="replace")

        # Compute indentation
        if isinstance(adapter, PythonAdapter):
            inner_indent, insert_at = get_python_docstring_insertion(source, func_node)
            indentation = inner_indent
        else:
            indentation = get_indentation_from_tree_sitter(source, func_node, adapter)

        if has_doc:
            if dry_run:
                plans.append(f"update: {path} :: {func.name}")
            else:
                doc = llm.generate_doc(
                    adapter.language_name, func.name, signature, body
                )
                doc = sanitize_llm_comment_with_tree_sitter(doc, adapter)
                comment_block = build_comment_block_with_tree_sitter(
                    doc, indentation, adapter
                )
                if func.doc_range:
                    staged_edits.append(
                        ReplaceEdit(
                            file_path=path,
                            start_byte=func.doc_range.start,
                            end_byte=func.doc_range.end,
                            content=comment_block,
                        )
                    )
            updated += 1
            if not dry_run:
                db.upsert(path, func.name, current_hash)

    # Second pass: plan inserts for those without docs using tree-sitter
    functions = list(adapter.iter_functions(source))
    for func in functions:
        if func.has_doc():
            continue

        body = adapter.get_function_body(source, func)
        current_hash = db.compute_hash(body)
        signature = source[
            func.signature_range.start : func.signature_range.end
        ].decode("utf-8", errors="replace")

        # Find the function node in the tree
        func_node = tree.root_node.descendant_for_byte_range(
            func.full_range.start, func.full_range.end
        )

        # Compute indentation and insertion specifics
        if isinstance(adapter, PythonAdapter):
            indentation, insert_at = get_python_docstring_insertion(source, func_node)
        else:
            indentation = get_indentation_from_tree_sitter(source, func_node, adapter)
            # C-only prototype cleanup
            prototype_range = find_prototype_after_last_comment(
                source, func_node, adapter
            )
            if prototype_range:
                if dry_run:
                    plans.append(f"clean: {path} :: {func.name}")
                else:
                    staged_edits.append(
                        ReplaceEdit(
                            file_path=path,
                            start_byte=prototype_range[0],
                            end_byte=prototype_range[1],
                            content="\n",
                        )
                    )
                # Skip generating a new doc for C prototype case
                continue

        if dry_run:
            plans.append(f"insert: {path} :: {func.name}")
        else:
            doc = llm.generate_doc(adapter.language_name, func.name, signature, body)
            doc = sanitize_llm_comment_with_tree_sitter(doc, adapter)
            comment_block = build_comment_block_with_tree_sitter(
                doc, indentation, adapter
            )
            if isinstance(adapter, PythonAdapter):
                planned.append(
                    PlanEdit(
                        file_path=path,
                        insert_at_byte=insert_at,
                        content=comment_block,
                    )
                )
            else:
                planned.append(
                    PlanEdit(
                        file_path=path,
                        insert_at_byte=func.full_range.start,
                        content=comment_block,
                    )
                )
        new += 1
        if not dry_run:
            db.upsert(path, func.name, current_hash)

    all_edits: List[ReplaceEdit | PlanEdit] = []
    all_edits.extend(staged_edits)
    all_edits.extend(planned)
    if all_edits and not dry_run:
        Editor().apply(all_edits, dry_run=False)

    return {
        "functions": len(functions),
        "new": new,
        "updated": updated,
        "skipped": skipped,
    }, plans


def process_directory(
    root: Path, db: HashDatabase, llm: OllamaClient, dry_run: bool = False
) -> Dict[str, int | List[str]]:
    files = discover_files(root)
    total: Dict[str, int | List[str]] = {
        "files": 0,
        "functions": 0,
        "new": 0,
        "updated": 0,
        "skipped": 0,
        "plans": [],
    }
    for f in files:
        stats, plans = process_file(f, db=db, llm=llm, dry_run=dry_run)
        total["files"] = total["files"] + 1  # type: ignore[operator]
        for k in ("functions", "new", "updated", "skipped"):
            assert isinstance(total[k], int)
            assert isinstance(stats[k], int)
            total[k] = total[k] + stats[k]  # type: ignore[operator]
        total_plans = total["plans"]
        assert isinstance(total_plans, list)
        total_plans.extend(plans)
    return total
