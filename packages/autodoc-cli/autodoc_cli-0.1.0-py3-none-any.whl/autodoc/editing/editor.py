from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Union


@dataclass
class PlanEdit:
    file_path: Path
    insert_at_byte: int
    content: str


@dataclass
class ReplaceEdit:
    file_path: Path
    start_byte: int
    end_byte: int
    content: str


class Editor:
    def __init__(self) -> None:
        pass

    def apply(self, planned: List[Union[PlanEdit, ReplaceEdit]], dry_run: bool = False) -> None:
        # Group by file and apply changes from bottom to top to preserve byte offsets
        by_file: dict[Path, List[Union[PlanEdit, ReplaceEdit]]] = {}
        for e in planned:
            by_file.setdefault(e.file_path, []).append(e)
        for path, edits in by_file.items():
            data = path.read_bytes()
            # sort descending by affected start byte
            def start_byte(e: Union[PlanEdit, ReplaceEdit]) -> int:
                return e.insert_at_byte if isinstance(e, PlanEdit) else e.start_byte

            edits.sort(key=start_byte, reverse=True)
            for e in edits:
                if isinstance(e, PlanEdit):
                    before = data[: e.insert_at_byte]
                    after = data[e.insert_at_byte :]
                    insertion = e.content.encode("utf-8")
                    data = before + insertion + after
                else:
                    before = data[: e.start_byte]
                    after = data[e.end_byte :]
                    replacement = e.content.encode("utf-8")
                    data = before + replacement + after
            if dry_run:
                continue
            path.write_bytes(data)


