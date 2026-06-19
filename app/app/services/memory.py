from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


class MemoryStore:
    """Small SQLite-backed memory log for agent runs."""

    def __init__(self) -> None:
        db_path = os.getenv("APP_MEMORY_DB", "nexus_memory.sqlite3")
        self.path = Path(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )

    def save_run(self, goal: str, summary: str, payload: dict) -> dict:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO runs (created_at, goal, summary, payload)
                VALUES (?, ?, ?, ?)
                """,
                (created_at, goal, summary, json.dumps(payload)),
            )
            run_id = cursor.lastrowid

        return {
            "id": run_id,
            "created_at": created_at,
            "goal": goal,
            "summary": summary,
        }

    def recent_runs(self, limit: int = 10) -> list[dict]:
        with self._connect() as connection:
            rows: Iterable[sqlite3.Row] = connection.execute(
                """
                SELECT id, created_at, goal, summary
                FROM runs
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]

    def clear(self) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM runs")
