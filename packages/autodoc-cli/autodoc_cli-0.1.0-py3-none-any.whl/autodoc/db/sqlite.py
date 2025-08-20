from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class HashRecord:
    file_path: str
    function_name: str
    body_hash: str


class HashDatabase:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS function_hashes (
                    file_path TEXT NOT NULL,
                    function_name TEXT NOT NULL,
                    body_hash TEXT NOT NULL,
                    PRIMARY KEY (file_path, function_name)
                )
                """
            )
            conn.commit()

    def compute_hash(self, function_body: str) -> str:
        return hashlib.sha256(function_body.encode("utf-8")).hexdigest()

    def get(self, file_path: Path, function_name: str) -> Optional[HashRecord]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT file_path, function_name, body_hash FROM function_hashes WHERE file_path=? AND function_name=?",
                (str(file_path), function_name),
            )
            row = cur.fetchone()
            if not row:
                return None
            return HashRecord(file_path=row[0], function_name=row[1], body_hash=row[2])

    def upsert(self, file_path: Path, function_name: str, body_hash: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "REPLACE INTO function_hashes (file_path, function_name, body_hash) VALUES (?, ?, ?)",
                (str(file_path), function_name, body_hash),
            )
            conn.commit()


