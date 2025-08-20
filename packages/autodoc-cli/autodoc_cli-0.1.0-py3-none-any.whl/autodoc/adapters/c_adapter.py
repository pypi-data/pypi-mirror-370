from __future__ import annotations

from typing import Iterable, Optional

from tree_sitter import Language, Parser
from tree_sitter_languages import get_language

from .base import ByteRange, FunctionInfo, LanguageAdapter


class CAdapter(LanguageAdapter):
    language_name = "c"

    def __init__(self) -> None:
        # Initialize parser for C
        self.language: Language = get_language("c")
        self.parser: Parser = Parser()
        self.parser.set_language(self.language)

    def iter_functions(self, source_code: bytes) -> Iterable[FunctionInfo]:
        tree = self.parser.parse(bytes(source_code))
        root = tree.root_node

        # We consider function_definition nodes. We avoid regex; we rely on the grammar.
        for current in self._walk(root):
            if current.type == "function_definition":
                yield self._extract_function_info(source_code, current)

    # Helper traversal to iterate all nodes
    def _walk(self, node) -> Iterable:
        stack = [node]
        while stack:
            n = stack.pop()
            yield n
            for child in reversed(n.children):
                stack.append(child)

    def _extract_function_info(self, source_code: bytes, node) -> FunctionInfo:
        # Extract function information from tree-sitter AST node.
        # Optional preceeding comment nodes will be identified by scanning preceding siblings that are comments.

        # Find name
        name = ""
        body_node = None
        declarator = None
        for child in node.children:
            if child.type == "compound_statement":
                body_node = child
            if "declarator" in child.type:
                declarator = child
        if declarator is not None:
            # search for identifier under declarator
            for d_child in self._walk(declarator):
                if d_child.type == "identifier":
                    name = source_code[d_child.start_byte : d_child.end_byte].decode("utf-8", errors="replace")
                    break

        # Determine ranges
        full_range = ByteRange(start=node.start_byte, end=node.end_byte)
        body_range = ByteRange(start=body_node.start_byte if body_node else node.start_byte, end=body_node.end_byte if body_node else node.end_byte)
        signature_end = declarator.end_byte if declarator else node.start_byte
        signature_range = ByteRange(start=node.start_byte, end=signature_end)

        # Detect leading doc comment range by scanning immediate preceding comments.
        doc_range: Optional[ByteRange] = None
        prev = node.prev_sibling
        if prev is not None and prev.type == "comment":
            # Accumulate contiguous leading comments immediately above, stopping when encountering blank or non-comment
            start = prev.start_byte
            end = prev.end_byte
            cursor = prev.prev_sibling
            contiguous = True
            while cursor is not None and contiguous:
                if cursor.type == "comment":
                    # ensure there is only whitespace/newlines between comments
                    between = source_code[cursor.end_byte : start]
                    if between.strip():
                        break
                    start = cursor.start_byte
                    cursor = cursor.prev_sibling
                else:
                    break
            doc_range = ByteRange(start=start, end=end)

        return FunctionInfo(
            name=name or "",
            signature_range=signature_range,
            body_range=body_range,
            full_range=full_range,
            doc_range=doc_range,
        )


