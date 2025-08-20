from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

from .adapters import CAdapter, LanguageAdapter
from .db.sqlite import HashDatabase
from .editing.editor import Editor, PlanEdit, ReplaceEdit
from .llm.ollama import OllamaClient


SUPPORTED_EXTENSIONS = {
    ".c": CAdapter,
    ".h": CAdapter,
}


def discover_files(root: Path) -> List[Path]:
    ignore_file = root / ".gitignore"
    spec = PathSpec.from_lines(GitWildMatchPattern, ignore_file.read_text().splitlines()) if ignore_file.exists() else None
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
    return "block"


def build_comment_block(language_name: str, content: str, indentation: str = "") -> str:
    style = extract_doc_comment_language_style(language_name)
    stripped = content.strip()
    # If the model returned a full block comment, indent it and return
    if stripped.startswith("/*"):
        # Ensure newline termination and indent each line
        text = content
        if not text.endswith("\n"):
            text += "\n"
        indented = "\n".join((indentation + line) if line else line for line in text.splitlines())
        if not indented.endswith("\n"):
            indented += "\n"
        return indented
    if style == "block":
        lines = [line.rstrip() for line in content.splitlines()]
        if not lines:
            return ""
        body = "\n".join(f"{indentation} * {line}" if line else f"{indentation} *" for line in lines)
        return f"{indentation}/**\n{body}\n{indentation} */\n"
    # fallback
    return content


def sanitize_llm_comment(raw: str) -> str:
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
                stripped = stripped[1:]
                if stripped.startswith(" "):
                    stripped = stripped[1:]
            cleaned.append(stripped)
        text = "\n".join(cleaned).strip("\n")
    return text


def process_file(path: Path, db: HashDatabase, llm: OllamaClient, dry_run: bool = False) -> Tuple[Dict[str, int], List[str]]:
    adapter = pick_adapter(path)
    if adapter is None:
        return {"functions": 0, "new": 0, "updated": 0, "skipped": 0}, []

    source = path.read_bytes()

    # Pre-sanitize any problematic existing comments that could break parsing (e.g., nested comment markers or code fences)
    pre_sanitized_edits: List[ReplaceEdit | PlanEdit] = []
    plans: List[str] = []
    tree = adapter.parser.parse(source)  # type: ignore[attr-defined]
    root = tree.root_node
    stack = [root]
    while stack:
        n = stack.pop()
        if n.type == "comment":
            raw = source[n.start_byte : n.end_byte].decode("utf-8", errors="replace")
            if ("```" in raw) or ("/*" in raw[2:] or "*/" in raw[:-2]):
                sanitized = sanitize_llm_comment(raw)
                if sanitized:
                    # Preserve indentation
                    line_start = source.rfind(b"\n", 0, n.start_byte) + 1
                    indent_slice = source[line_start : n.start_byte]
                    indentation = indent_slice.decode("utf-8", errors="ignore")
                    indentation = indentation[: len(indentation) - len(indentation.lstrip(" \t"))]
                    new_block = build_comment_block("c", sanitized, indentation)
                    pre_sanitized_edits.append(ReplaceEdit(file_path=path, start_byte=n.start_byte, end_byte=n.end_byte, content=new_block))
        for child in n.children:
            stack.append(child)

    if pre_sanitized_edits and not dry_run:
        Editor().apply(pre_sanitized_edits, dry_run=False)
        source = path.read_bytes()
    elif pre_sanitized_edits and dry_run:
        # report planned sanitizations
        plans.append(f"sanitize: {path}")
    functions = list(adapter.iter_functions(source))

    planned: List[PlanEdit] = []
    new = updated = skipped = 0
    # Continue with planned function-level changes

    # First pass: stage replacements for existing docs (no in-place writes) to avoid offset drift
    staged_edits: List[ReplaceEdit | PlanEdit] = []
    # First pass: handle updates (existing docs)
    for func in functions:
        body = adapter.get_function_body(source, func)
        current_hash = db.compute_hash(body)
        record = db.get(path, func.name)
        has_doc = func.has_doc()

        # If there is a stray prototype between doc and definition that matches signature, remove it
        if has_doc and func.doc_range:
            gap_bytes = source[func.doc_range.end : func.full_range.start]
            gap_text = gap_bytes.decode("utf-8", errors="ignore").strip()
            sig_text = source[func.signature_range.start : func.signature_range.end].decode("utf-8", errors="ignore").strip()
            if gap_text == f"{sig_text};":
                if dry_run:
                    plans.append(f"clean: {path} :: {func.name}")
                else:
                    staged_edits.append(
                        ReplaceEdit(
                            file_path=path,
                            start_byte=func.doc_range.end,
                            end_byte=func.full_range.start,
                            content="\n",
                        )
                    )

        if has_doc and record and record.body_hash == current_hash:
            skipped += 1
            continue

        # Build signature text for LLM context
        signature = source[func.signature_range.start : func.signature_range.end].decode("utf-8", errors="replace")
        # Determine indentation at insertion point (start of function)
        line_start = source.rfind(b"\n", 0, func.full_range.start) + 1
        line_slice = source[line_start : func.full_range.start]
        indentation = line_slice.decode("utf-8", errors="ignore")
        indentation = indentation[: len(indentation) - len(indentation.lstrip(" \t"))]

        if has_doc:
            if dry_run:
                plans.append(f"update: {path} :: {func.name}")
            else:
                doc = llm.generate_doc(adapter.language_name, func.name, signature, body)
                doc = sanitize_llm_comment(doc)
                comment_block = build_comment_block(adapter.language_name, doc, indentation)
                if func.doc_range:
                    staged_edits.append(
                        ReplaceEdit(file_path=path, start_byte=func.doc_range.start, end_byte=func.doc_range.end, content=comment_block)
                    )
            updated += 1
            if not dry_run:
                db.upsert(path, func.name, current_hash)

    # Second pass: plan inserts for those without docs using current source
    functions = list(adapter.iter_functions(source))
    for func in functions:
        if func.has_doc():
            continue
        body = adapter.get_function_body(source, func)
        current_hash = db.compute_hash(body)
        signature = source[func.signature_range.start : func.signature_range.end].decode("utf-8", errors="replace")
        line_start = source.rfind(b"\n", 0, func.full_range.start) + 1
        line_slice = source[line_start : func.full_range.start]
        indentation = line_slice.decode("utf-8", errors="ignore")
        indentation = indentation[: len(indentation) - len(indentation.lstrip(" \t"))]
        # If there's a prototype exactly between the most recent closing comment and function start, remove it and do not insert a new doc
        before_func = source[: func.full_range.start]
        last_comment_end = before_func.rfind(b"*/")
        if last_comment_end != -1:
            gap_bytes = source[last_comment_end + 2 : func.full_range.start]
            if gap_bytes.decode("utf-8", errors="ignore").strip() == f"{signature};":
                if dry_run:
                    plans.append(f"clean: {path} :: {func.name}")
                else:
                    staged_edits.append(
                        ReplaceEdit(
                            file_path=path,
                            start_byte=last_comment_end + 2,
                            end_byte=func.full_range.start,
                            content="\n",
                        )
                    )
                # Skip generating a new doc; the existing comment will now attach to the function
                continue
        if dry_run:
            plans.append(f"insert: {path} :: {func.name}")
        else:
            doc = llm.generate_doc(adapter.language_name, func.name, signature, body)
            doc = sanitize_llm_comment(doc)
            comment_block = build_comment_block(adapter.language_name, doc, indentation)
            planned.append(PlanEdit(file_path=path, insert_at_byte=func.full_range.start, content=comment_block))
        new += 1
        if not dry_run:
            db.upsert(path, func.name, current_hash)

    all_edits: List[ReplaceEdit | PlanEdit] = []
    all_edits.extend(staged_edits)
    all_edits.extend(planned)
    if all_edits and not dry_run:
        Editor().apply(all_edits, dry_run=False)

    return {"functions": len(functions), "new": new, "updated": updated, "skipped": skipped}, plans


def process_directory(root: Path, db: HashDatabase, llm: OllamaClient, dry_run: bool = False) -> Dict[str, int | List[str]]:
    files = discover_files(root)
    total: Dict[str, int | List[str]] = {"files": 0, "functions": 0, "new": 0, "updated": 0, "skipped": 0, "plans": []}
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


