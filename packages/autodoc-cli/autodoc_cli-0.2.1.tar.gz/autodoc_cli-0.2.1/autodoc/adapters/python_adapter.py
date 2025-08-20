from __future__ import annotations

from typing import Iterable, Optional

from tree_sitter import Language, Parser
from tree_sitter_languages import get_language

from .base import ByteRange, FunctionInfo, LanguageAdapter


class PythonAdapter(LanguageAdapter):
    language_name = "python"

    def __init__(self) -> None:
        self.language: Language = get_language("python")
        self._parser: Parser = Parser()
        self._parser.set_language(self.language)

    @property
    def parser(self) -> Parser:
        return self._parser

    def iter_functions(self, source_code: bytes) -> Iterable[FunctionInfo]:
        tree = self.parser.parse(bytes(source_code))
        root = tree.root_node

        for node in self._walk(root):
            if node.type in ("function_definition", "async_function_definition"):
                yield self._extract_function_info(source_code, node)

    def _walk(self, node):
        stack = [node]
        while stack:
            current = stack.pop()
            yield current
            for child in reversed(current.children):
                stack.append(child)

    def _extract_function_info(self, source_code: bytes, node) -> FunctionInfo:
        # Python function structure (simplified):
        #   def <identifier> <parameters> : <block>
        name = ""
        block_node = None
        identifier_node = None

        for child in node.children:
            if child.type == "identifier":
                identifier_node = child
            if child.type == "block":
                block_node = child

        if identifier_node is not None:
            name = source_code[
                identifier_node.start_byte : identifier_node.end_byte
            ].decode("utf-8", errors="replace")

        # Determine signature range: from def start up to the colon token (end of signature)
        # In tree-sitter, the block begins at the newline/indent after ':' so we can take
        # signature end as the start of the block if present, else node.start_byte
        if block_node is not None:
            signature_end = block_node.start_byte
        else:
            signature_end = node.end_byte

        signature_range = ByteRange(start=node.start_byte, end=signature_end)

        # Body range corresponds to the "block" node if present
        if block_node is not None:
            body_range = ByteRange(start=block_node.start_byte, end=block_node.end_byte)
        else:
            body_range = ByteRange(start=node.end_byte, end=node.end_byte)

        full_range = ByteRange(start=node.start_byte, end=node.end_byte)

        # Detect an existing docstring: first statement in the block that is a string literal
        doc_range: Optional[ByteRange] = None
        if block_node is not None:
            # The block typically contains indentation, newline and then statements
            # We scan for the first expression_statement containing a string
            first_stmt = self._first_real_statement(block_node)
            if first_stmt is not None and self._is_docstring_statement(
                source_code, first_stmt
            ):
                doc_range = ByteRange(
                    start=first_stmt.start_byte, end=first_stmt.end_byte
                )

        return FunctionInfo(
            name=name or "",
            signature_range=signature_range,
            body_range=body_range,
            full_range=full_range,
            doc_range=doc_range,
        )

    def _first_real_statement(self, block_node):
        # Iterate over block children to find the first statement node
        for child in block_node.children:
            # Skip punctuation and indentation tokens; we rely on type naming
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
                return child
        return None

    def _is_docstring_statement(self, source_code: bytes, stmt_node) -> bool:
        if stmt_node.type != "expression_statement":
            return False
        # The expression should be a string literal
        if not stmt_node.children:
            return False
        expr = stmt_node.children[0]
        # tree-sitter-python uses node type 'string' for string literals
        if expr.type == "string":
            # Must be a triple-quoted or simple string; we accept any string literal as docstring
            return True
        return False
