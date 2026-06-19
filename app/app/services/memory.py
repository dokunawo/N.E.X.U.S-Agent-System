from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Iterable

from app.services.operating_schema import (
    AGENT_LOG_STATUSES,
    AGENT_ROSTER,
    APPROVAL_STATUSES,
    DATA_SOURCES,
    MEMORY_KINDS,
    RISK_LEVELS,
    TASK_STATUSES,
    agent_id_from_name,
    utc_now,
)


class MemoryStore:
    """SQLite-backed operating backbone for N.E.X.U.S."""

    def __init__(self) -> None:
        db_path = os.getenv("APP_MEMORY_DB", "nexus_memory.sqlite3")
        self.path = Path(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
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
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    role TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    access_scope TEXT NOT NULL,
                    risk_boundary TEXT NOT NULL,
                    default_status TEXT NOT NULL,
                    sort_order INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    title TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL DEFAULT 'normal',
                    risk_level TEXT NOT NULL DEFAULT 'low',
                    owner_agent_id TEXT NOT NULL DEFAULT 'nexus',
                    source TEXT NOT NULL DEFAULT 'dashboard',
                    summary TEXT,
                    payload TEXT NOT NULL DEFAULT '{}',
                    FOREIGN KEY (owner_agent_id) REFERENCES agents(id)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT NOT NULL,
                    risk_level TEXT NOT NULL DEFAULT 'low',
                    payload TEXT NOT NULL DEFAULT '{}',
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                    FOREIGN KEY (agent_id) REFERENCES agents(id)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER,
                    created_at TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    importance INTEGER NOT NULL DEFAULT 1,
                    source TEXT NOT NULL DEFAULT 'nexus',
                    tags TEXT NOT NULL DEFAULT '[]',
                    payload TEXT NOT NULL DEFAULT '{}',
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS approval_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    resolved_at TEXT,
                    requested_by_agent_id TEXT NOT NULL DEFAULT 'sentinel',
                    title TEXT NOT NULL,
                    requested_action TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    approval_type TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'requested',
                    decision_note TEXT,
                    payload TEXT NOT NULL DEFAULT '{}',
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                    FOREIGN KEY (requested_by_agent_id) REFERENCES agents(id)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS data_sources (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    status TEXT NOT NULL,
                    privacy_level TEXT NOT NULL,
                    detail TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    payload TEXT NOT NULL DEFAULT '{}'
                )
                """
            )
            self._seed_agents(connection)
            self._seed_data_sources(connection)

    def _seed_agents(self, connection: sqlite3.Connection) -> None:
        now = utc_now()
        for sort_order, agent in enumerate(AGENT_ROSTER, start=1):
            connection.execute(
                """
                INSERT INTO agents (
                    id, name, role, purpose, access_scope, risk_boundary,
                    default_status, sort_order, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    role = excluded.role,
                    purpose = excluded.purpose,
                    access_scope = excluded.access_scope,
                    risk_boundary = excluded.risk_boundary,
                    default_status = excluded.default_status,
                    sort_order = excluded.sort_order,
                    updated_at = excluded.updated_at
                """,
                (
                    agent["id"],
                    agent["name"],
                    agent["role"],
                    agent["purpose"],
                    agent["access_scope"],
                    agent["risk_boundary"],
                    agent["default_status"],
                    sort_order,
                    now,
                    now,
                ),
            )

    def _seed_data_sources(self, connection: sqlite3.Connection) -> None:
        now = utc_now()
        for source in DATA_SOURCES:
            connection.execute(
                """
                INSERT INTO data_sources (
                    id, name, kind, status, privacy_level, detail,
                    created_at, updated_at, payload
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    kind = excluded.kind,
                    status = excluded.status,
                    privacy_level = excluded.privacy_level,
                    detail = excluded.detail,
                    updated_at = excluded.updated_at,
                    payload = excluded.payload
                """,
                (
                    source["id"],
                    source["name"],
                    source["kind"],
                    source["status"],
                    source["privacy_level"],
                    source["detail"],
                    now,
                    now,
                    self._to_json({}),
                ),
            )

    def schema_overview(self) -> dict:
        return {
            "tables": [
                "agents",
                "tasks",
                "agent_logs",
                "memory_entries",
                "approval_requests",
                "data_sources",
                "runs",
            ],
            "task_statuses": TASK_STATUSES,
            "agent_log_statuses": AGENT_LOG_STATUSES,
            "risk_levels": RISK_LEVELS,
            "approval_statuses": APPROVAL_STATUSES,
            "memory_kinds": MEMORY_KINDS,
        }

    def save_run(
        self,
        goal: str,
        summary: str,
        payload: dict,
        events: list[dict] | None = None,
        suggestions: list[str] | None = None,
        risk_level: str = "low",
        task_status: str = "completed",
        approval: dict | None = None,
    ) -> dict:
        created_at = utc_now()
        title = self._title_from_goal(goal)
        events = events or []
        suggestions = suggestions or []

        with self._connect() as connection:
            task_cursor = connection.execute(
                """
                INSERT INTO tasks (
                    created_at, updated_at, title, goal, status, priority,
                    risk_level, owner_agent_id, source, summary, payload
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    created_at,
                    title,
                    goal,
                    task_status,
                    "normal",
                    self._known_risk_level(risk_level),
                    "nexus",
                    "dashboard",
                    summary,
                    self._to_json({"suggestions": suggestions}),
                ),
            )
            task_id = task_cursor.lastrowid

            for event in events:
                connection.execute(
                    """
                    INSERT INTO agent_logs (
                        task_id, created_at, agent_id, status, message, risk_level, payload
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        task_id,
                        created_at,
                        agent_id_from_name(str(event.get("agent", "N.E.X.U.S"))),
                        self._known_log_status(str(event.get("status", "complete"))),
                        str(event.get("message", "")),
                        self._known_risk_level(risk_level),
                        self._to_json(event),
                    ),
                )

            memory_cursor = connection.execute(
                """
                INSERT INTO memory_entries (
                    task_id, created_at, kind, title, content, importance, source, tags, payload
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    created_at,
                    "run_summary",
                    title,
                    summary,
                    2 if risk_level in {"medium", "high", "critical"} else 1,
                    "nexus",
                    self._to_json(["run", risk_level]),
                    self._to_json({"goal": goal, "suggestions": suggestions}),
                ),
            )
            memory_entry_id = memory_cursor.lastrowid

            approval_entry = None
            if approval:
                approval_cursor = connection.execute(
                    """
                    INSERT INTO approval_requests (
                        task_id, created_at, requested_by_agent_id, title,
                        requested_action, reason, risk_level, approval_type, status, payload
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        task_id,
                        created_at,
                        approval.get("requested_by_agent_id", "sentinel"),
                        approval["title"],
                        approval["requested_action"],
                        approval["reason"],
                        self._known_risk_level(approval["risk_level"]),
                        approval["approval_type"],
                        "requested",
                        self._to_json(approval.get("payload", {})),
                    ),
                )
                approval_entry = {
                    "id": approval_cursor.lastrowid,
                    "status": "requested",
                    **approval,
                }

            cursor = connection.execute(
                """
                INSERT INTO runs (created_at, goal, summary, payload)
                VALUES (?, ?, ?, ?)
                """,
                (created_at, goal, summary, self._to_json(payload)),
            )
            run_id = cursor.lastrowid

        return {
            "id": run_id,
            "task_id": task_id,
            "memory_entry_id": memory_entry_id,
            "created_at": created_at,
            "goal": goal,
            "summary": summary,
            "status": task_status,
            "risk_level": risk_level,
            "approval_request": approval_entry,
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

    def operating_snapshot(self, limit: int = 8) -> dict:
        return {
            "schema": self.schema_overview(),
            "agents": self.list_agents(),
            "tasks": self.recent_tasks(limit=limit),
            "logs": self.recent_logs(limit=limit * 2),
            "memory_entries": self.recent_memory_entries(limit=limit),
            "approvals": self.pending_approvals(limit=limit),
            "data_sources": self.list_data_sources(),
        }

    def list_agents(self) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, name, role, purpose, access_scope, risk_boundary, default_status
                FROM agents
                ORDER BY sort_order
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def recent_tasks(self, limit: int = 10) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    tasks.id,
                    tasks.created_at,
                    tasks.updated_at,
                    tasks.title,
                    tasks.goal,
                    tasks.status,
                    tasks.priority,
                    tasks.risk_level,
                    tasks.summary,
                    agents.name AS owner_agent
                FROM tasks
                JOIN agents ON agents.id = tasks.owner_agent_id
                ORDER BY tasks.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]

    def recent_logs(self, limit: int = 20) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    agent_logs.id,
                    agent_logs.task_id,
                    agent_logs.created_at,
                    agents.name AS agent,
                    agent_logs.status,
                    agent_logs.message,
                    agent_logs.risk_level
                FROM agent_logs
                JOIN agents ON agents.id = agent_logs.agent_id
                ORDER BY agent_logs.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]

    def recent_memory_entries(self, limit: int = 10) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    task_id,
                    created_at,
                    kind,
                    title,
                    content,
                    importance,
                    source,
                    tags
                FROM memory_entries
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [self._decode_tags(row) for row in rows]

    def pending_approvals(self, limit: int = 10) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    approval_requests.id,
                    approval_requests.task_id,
                    approval_requests.created_at,
                    agents.name AS requested_by,
                    approval_requests.title,
                    approval_requests.requested_action,
                    approval_requests.reason,
                    approval_requests.risk_level,
                    approval_requests.approval_type,
                    approval_requests.status
                FROM approval_requests
                JOIN agents ON agents.id = approval_requests.requested_by_agent_id
                WHERE approval_requests.status = 'requested'
                ORDER BY approval_requests.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]

    def list_data_sources(self) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, name, kind, status, privacy_level, detail
                FROM data_sources
                ORDER BY
                    CASE status
                        WHEN 'active' THEN 0
                        WHEN 'planned' THEN 1
                        ELSE 2
                    END,
                    name
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def clear(self) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM approval_requests")
            connection.execute("DELETE FROM memory_entries")
            connection.execute("DELETE FROM agent_logs")
            connection.execute("DELETE FROM tasks")
            connection.execute("DELETE FROM runs")

    def _title_from_goal(self, goal: str) -> str:
        clean = " ".join(goal.strip().split())
        if len(clean) <= 72:
            return clean
        return f"{clean[:69]}..."

    def _known_risk_level(self, risk_level: str) -> str:
        return risk_level if risk_level in RISK_LEVELS else "low"

    def _known_log_status(self, status: str) -> str:
        return status if status in AGENT_LOG_STATUSES else "complete"

    def _to_json(self, value: object) -> str:
        return json.dumps(value, ensure_ascii=True)

    def _decode_tags(self, row: sqlite3.Row) -> dict:
        item = dict(row)
        try:
            item["tags"] = json.loads(item["tags"])
        except json.JSONDecodeError:
            item["tags"] = []
        return item
