from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass
class ByteRange:
    start: int
    end: int

    def is_empty(self) -> bool:
        return self.end <= self.start


@dataclass
class FunctionInfo:
    name: str
    signature_range: ByteRange
    body_range: ByteRange
    full_range: ByteRange
    doc_range: Optional[ByteRange]

    def has_doc(self) -> bool:
        return self.doc_range is not None and not self.doc_range.is_empty()


class LanguageAdapter:
    language_name: str

    def iter_functions(self, source_code: bytes) -> Iterable[FunctionInfo]:  # pragma: no cover - interface
        raise NotImplementedError

    def get_function_source(self, source_code: bytes, function: FunctionInfo) -> str:
        return source_code[function.full_range.start : function.full_range.end].decode("utf-8", errors="replace")

    def get_function_body(self, source_code: bytes, function: FunctionInfo) -> str:
        return source_code[function.body_range.start : function.body_range.end].decode("utf-8", errors="replace")


