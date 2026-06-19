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
    BUDGET_CATEGORIES,
    DATA_SOURCES,
    LEARNING_SOURCES,
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
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_sources (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    status TEXT NOT NULL,
                    privacy_level TEXT NOT NULL,
                    consent_required INTEGER NOT NULL DEFAULT 0,
                    detail TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    detail TEXT NOT NULL,
                    confidence REAL NOT NULL DEFAULT 0.5,
                    source_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    privacy_level TEXT NOT NULL DEFAULT 'private',
                    evidence TEXT NOT NULL DEFAULT '[]',
                    payload TEXT NOT NULL DEFAULT '{}',
                    FOREIGN KEY (source_id) REFERENCES learning_sources(id)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS budget_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    name TEXT NOT NULL UNIQUE,
                    category_type TEXT NOT NULL,
                    monthly_limit REAL NOT NULL DEFAULT 0,
                    spent_this_month REAL NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'active'
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    spent_at TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'manual',
                    payload TEXT NOT NULL DEFAULT '{}'
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS savings_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    title TEXT NOT NULL,
                    target_amount REAL NOT NULL,
                    current_amount REAL NOT NULL DEFAULT 0,
                    target_date TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    notes TEXT NOT NULL DEFAULT ''
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS investment_positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    name TEXT NOT NULL,
                    symbol TEXT,
                    position_type TEXT NOT NULL DEFAULT 'manual',
                    current_value REAL NOT NULL DEFAULT 0,
                    cost_basis REAL NOT NULL DEFAULT 0,
                    risk_level TEXT NOT NULL DEFAULT 'unknown',
                    notes TEXT NOT NULL DEFAULT ''
                )
                """
            )
            self._seed_agents(connection)
            self._seed_data_sources(connection)
            self._seed_learning_sources(connection)
            self._seed_budget_categories(connection)

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

    def _seed_learning_sources(self, connection: sqlite3.Connection) -> None:
        now = utc_now()
        for source in LEARNING_SOURCES:
            connection.execute(
                """
                INSERT INTO learning_sources (
                    id, name, kind, status, privacy_level, consent_required,
                    detail, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    kind = excluded.kind,
                    status = excluded.status,
                    privacy_level = excluded.privacy_level,
                    consent_required = excluded.consent_required,
                    detail = excluded.detail,
                    updated_at = excluded.updated_at
                """,
                (
                    source["id"],
                    source["name"],
                    source["kind"],
                    source["status"],
                    source["privacy_level"],
                    1 if source["consent_required"] else 0,
                    source["detail"],
                    now,
                    now,
                ),
            )

    def _seed_budget_categories(self, connection: sqlite3.Connection) -> None:
        now = utc_now()
        for category in BUDGET_CATEGORIES:
            connection.execute(
                """
                INSERT INTO budget_categories (
                    created_at, updated_at, name, category_type, monthly_limit, spent_this_month
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    category_type = excluded.category_type,
                    updated_at = excluded.updated_at
                """,
                (
                    now,
                    now,
                    category["name"],
                    category["category_type"],
                    category["monthly_limit"],
                    0.0,
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
                "learning_sources",
                "learning_insights",
                "budget_categories",
                "expenses",
                "savings_goals",
                "investment_positions",
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
            "learning": self.learning_snapshot(limit=limit),
            "finance": self.finance_snapshot(limit=limit),
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

    def approval_detail(self, approval_id: int) -> dict | None:
        with self._connect() as connection:
            row = self._approval_detail(connection, approval_id)

        return dict(row) if row else None

    def resolve_approval(self, approval_id: int, decision: str, decision_note: str = "") -> dict | None:
        if decision not in {"approved", "rejected"}:
            raise ValueError("Approval decision must be approved or rejected.")

        resolved_at = utc_now()
        task_status = "approved" if decision == "approved" else "rejected"
        log_status = "complete" if decision == "approved" else "blocked"

        with self._connect() as connection:
            approval = connection.execute(
                """
                SELECT id, task_id, status, title, requested_action, risk_level
                FROM approval_requests
                WHERE id = ?
                """,
                (approval_id,),
            ).fetchone()
            if approval is None:
                return None

            if approval["status"] != "requested":
                detail = self._approval_detail(connection, approval_id)
                return dict(detail) if detail else None

            note = decision_note.strip() or f"Daniel {decision} this request."
            connection.execute(
                """
                UPDATE approval_requests
                SET status = ?, resolved_at = ?, decision_note = ?
                WHERE id = ?
                """,
                (decision, resolved_at, note, approval_id),
            )
            connection.execute(
                """
                UPDATE tasks
                SET status = ?, updated_at = ?
                WHERE id = ?
                """,
                (task_status, resolved_at, approval["task_id"]),
            )
            connection.execute(
                """
                INSERT INTO agent_logs (
                    task_id, created_at, agent_id, status, message, risk_level, payload
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    approval["task_id"],
                    resolved_at,
                    "sentinel",
                    log_status,
                    f"Daniel {decision} approval request {approval_id}.",
                    approval["risk_level"],
                    self._to_json({"approval_id": approval_id, "decision": decision, "note": note}),
                ),
            )
            connection.execute(
                """
                INSERT INTO memory_entries (
                    task_id, created_at, kind, title, content, importance, source, tags, payload
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    approval["task_id"],
                    resolved_at,
                    "decision",
                    f"Approval {decision}: {approval['title']}",
                    f"{note} Requested action: {approval['requested_action']}",
                    3,
                    "sentinel",
                    self._to_json(["approval", decision, approval["risk_level"]]),
                    self._to_json({"approval_id": approval_id, "decision": decision}),
                ),
            )

            detail = self._approval_detail(connection, approval_id)

        return dict(detail) if detail else None

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

    def learning_snapshot(self, limit: int = 8) -> dict:
        with self._connect() as connection:
            source_rows = connection.execute(
                """
                SELECT id, name, kind, status, privacy_level, consent_required, detail
                FROM learning_sources
                ORDER BY
                    CASE status
                        WHEN 'active' THEN 0
                        WHEN 'approval_required' THEN 1
                        ELSE 2
                    END,
                    name
                """
            ).fetchall()
            insight_rows = connection.execute(
                """
                SELECT id, created_at, updated_at, category, title, detail,
                    confidence, source_id, status, privacy_level, evidence
                FROM learning_insights
                WHERE status = 'active'
                ORDER BY confidence DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return {
            "sources": [self._decode_learning_source(row) for row in source_rows],
            "insights": [self._decode_evidence(row) for row in insight_rows],
            "guardrail": "Connected plugin learning requires explicit approval before N.E.X.U.S reads personal connector data.",
        }

    def record_learning_from_goal(self, goal: str) -> list[dict]:
        text = goal.lower()
        candidates = [
            (
                "financial_growth",
                "Daniel wants stronger financial awareness",
                "Daniel is asking about budgeting, spending, savings, investments, or financial guidance.",
                ["budget", "spending", "savings", "investment", "investments", "finance", "financial", "expenses"],
                0.72,
            ),
            (
                "business_building",
                "Daniel is building business and operating systems",
                "Daniel often frames requests around business, systems, strategy, and durable execution.",
                ["business", "company", "startup", "revenue", "customer", "market", "strategy"],
                0.68,
            ),
            (
                "self_improvement",
                "Daniel values self-improvement and personal operating structure",
                "Daniel is asking N.E.X.U.S to learn preferences, improve routines, and understand him over time.",
                ["learn me", "learning me", "self", "habit", "routine", "person", "over time", "improve"],
                0.7,
            ),
            (
                "technical_builder",
                "Daniel is hands-on with technical build work",
                "Daniel asks for implementation, dashboards, agents, schemas, and local development workflows.",
                ["implement", "build", "dashboard", "agent", "schema", "github", "code"],
                0.66,
            ),
        ]

        saved: list[dict] = []
        for category, title, detail, keywords, confidence in candidates:
            matches = [keyword for keyword in keywords if keyword in text]
            if not matches:
                continue
            saved.append(
                self.upsert_learning_insight(
                    category=category,
                    title=title,
                    detail=detail,
                    confidence=confidence,
                    source_id="local_goals",
                    evidence=[{"goal": goal, "matched_terms": matches}],
                )
            )

        return saved

    def upsert_learning_insight(
        self,
        category: str,
        title: str,
        detail: str,
        confidence: float,
        source_id: str,
        evidence: list[dict],
        privacy_level: str = "private",
    ) -> dict:
        now = utc_now()
        confidence = max(0.0, min(confidence, 1.0))
        with self._connect() as connection:
            existing = connection.execute(
                """
                SELECT id, confidence, evidence
                FROM learning_insights
                WHERE category = ? AND title = ? AND source_id = ? AND status = 'active'
                """,
                (category, title, source_id),
            ).fetchone()
            if existing:
                try:
                    old_evidence = json.loads(existing["evidence"])
                except json.JSONDecodeError:
                    old_evidence = []
                merged_evidence = (old_evidence + evidence)[-8:]
                new_confidence = min(0.95, max(float(existing["confidence"]), confidence) + 0.03)
                connection.execute(
                    """
                    UPDATE learning_insights
                    SET updated_at = ?, detail = ?, confidence = ?, evidence = ?
                    WHERE id = ?
                    """,
                    (now, detail, new_confidence, self._to_json(merged_evidence), existing["id"]),
                )
                insight_id = existing["id"]
            else:
                cursor = connection.execute(
                    """
                    INSERT INTO learning_insights (
                        created_at, updated_at, category, title, detail, confidence,
                        source_id, status, privacy_level, evidence, payload
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        now,
                        now,
                        category,
                        title,
                        detail,
                        confidence,
                        source_id,
                        "active",
                        privacy_level,
                        self._to_json(evidence),
                        self._to_json({}),
                    ),
                )
                insight_id = cursor.lastrowid

            row = connection.execute(
                """
                SELECT id, created_at, updated_at, category, title, detail,
                    confidence, source_id, status, privacy_level, evidence
                FROM learning_insights
                WHERE id = ?
                """,
                (insight_id,),
            ).fetchone()

        return self._decode_evidence(row)

    def finance_snapshot(self, limit: int = 8) -> dict:
        with self._connect() as connection:
            budget_rows = connection.execute(
                """
                SELECT id, name, category_type, monthly_limit, spent_this_month, status
                FROM budget_categories
                WHERE status = 'active'
                ORDER BY id
                """
            ).fetchall()
            expense_rows = connection.execute(
                """
                SELECT id, created_at, spent_at, category, amount, description, source
                FROM expenses
                ORDER BY spent_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            goal_rows = connection.execute(
                """
                SELECT id, title, target_amount, current_amount, target_date, status, notes
                FROM savings_goals
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            investment_rows = connection.execute(
                """
                SELECT id, name, symbol, position_type, current_value, cost_basis, risk_level, notes
                FROM investment_positions
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        budgets = [dict(row) for row in budget_rows]
        expenses = [dict(row) for row in expense_rows]
        savings_goals = [dict(row) for row in goal_rows]
        investments = [dict(row) for row in investment_rows]
        total_budget = sum(item["monthly_limit"] for item in budgets)
        total_spent = sum(item["spent_this_month"] for item in budgets)
        total_savings_target = sum(item["target_amount"] for item in savings_goals)
        total_savings_current = sum(item["current_amount"] for item in savings_goals)
        total_investments = sum(item["current_value"] for item in investments)

        return {
            "summary": {
                "monthly_budget": total_budget,
                "spent_this_month": total_spent,
                "remaining_budget": total_budget - total_spent,
                "savings_goal_total": total_savings_target,
                "savings_current_total": total_savings_current,
                "investment_value_total": total_investments,
                "mode": "manual_mock",
            },
            "budgets": budgets,
            "recent_expenses": expenses,
            "savings_goals": savings_goals,
            "investments": investments,
            "guardrail": "Steward tracks and guides; it does not move money, trade, or connect accounts without approval.",
        }

    def add_expense(self, amount: float, category: str, description: str, spent_at: str | None = None) -> dict:
        created_at = utc_now()
        spent_at = spent_at or created_at
        category = category.strip() or "Uncategorized"
        description = description.strip() or "Manual expense"
        with self._connect() as connection:
            category_row = connection.execute(
                """
                SELECT id
                FROM budget_categories
                WHERE lower(name) = lower(?)
                """,
                (category,),
            ).fetchone()
            if category_row is None:
                connection.execute(
                    """
                    INSERT INTO budget_categories (
                        created_at, updated_at, name, category_type, monthly_limit, spent_this_month
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (created_at, created_at, category, "manual", 0.0, 0.0),
                )

            cursor = connection.execute(
                """
                INSERT INTO expenses (created_at, spent_at, category, amount, description, source, payload)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (created_at, spent_at, category, amount, description, "manual", self._to_json({})),
            )
            connection.execute(
                """
                UPDATE budget_categories
                SET spent_this_month = spent_this_month + ?, updated_at = ?
                WHERE lower(name) = lower(?)
                """,
                (amount, created_at, category),
            )
            expense_id = cursor.lastrowid
            row = connection.execute(
                """
                SELECT id, created_at, spent_at, category, amount, description, source
                FROM expenses
                WHERE id = ?
                """,
                (expense_id,),
            ).fetchone()

        self.upsert_learning_insight(
            category="financial_tracking",
            title="Daniel is tracking expenses with Steward",
            detail="Daniel is starting to use N.E.X.U.S for expense awareness and budgeting.",
            confidence=0.78,
            source_id="local_goals",
            evidence=[{"category": category, "amount": amount, "description": description}],
        )
        return dict(row)

    def set_budget_category(self, name: str, monthly_limit: float, category_type: str = "manual") -> dict:
        now = utc_now()
        name = name.strip()
        category_type = category_type.strip() or "manual"
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO budget_categories (
                    created_at, updated_at, name, category_type, monthly_limit, spent_this_month
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    updated_at = excluded.updated_at,
                    category_type = excluded.category_type,
                    monthly_limit = excluded.monthly_limit,
                    status = 'active'
                """,
                (now, now, name, category_type, monthly_limit, 0.0),
            )
            row = connection.execute(
                """
                SELECT id, name, category_type, monthly_limit, spent_this_month, status
                FROM budget_categories
                WHERE name = ?
                """,
                (name,),
            ).fetchone()

        return dict(row)

    def add_savings_goal(
        self,
        title: str,
        target_amount: float,
        current_amount: float = 0.0,
        target_date: str | None = None,
        notes: str = "",
    ) -> dict:
        now = utc_now()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO savings_goals (
                    created_at, updated_at, title, target_amount, current_amount, target_date, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (now, now, title.strip(), target_amount, current_amount, target_date, notes.strip()),
            )
            row = connection.execute(
                """
                SELECT id, title, target_amount, current_amount, target_date, status, notes
                FROM savings_goals
                WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()

        return dict(row)

    def add_investment_position(
        self,
        name: str,
        symbol: str | None = None,
        position_type: str = "manual",
        current_value: float = 0.0,
        cost_basis: float = 0.0,
        risk_level: str = "unknown",
        notes: str = "",
    ) -> dict:
        now = utc_now()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO investment_positions (
                    created_at, updated_at, name, symbol, position_type,
                    current_value, cost_basis, risk_level, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    now,
                    now,
                    name.strip(),
                    symbol.strip().upper() if symbol else None,
                    position_type.strip() or "manual",
                    current_value,
                    cost_basis,
                    risk_level.strip() or "unknown",
                    notes.strip(),
                ),
            )
            row = connection.execute(
                """
                SELECT id, name, symbol, position_type, current_value, cost_basis, risk_level, notes
                FROM investment_positions
                WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()

        return dict(row)

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

    def _approval_detail(self, connection: sqlite3.Connection, approval_id: int) -> sqlite3.Row | None:
        return connection.execute(
            """
            SELECT
                approval_requests.id,
                approval_requests.task_id,
                approval_requests.created_at,
                approval_requests.resolved_at,
                agents.name AS requested_by,
                approval_requests.title,
                approval_requests.requested_action,
                approval_requests.reason,
                approval_requests.risk_level,
                approval_requests.approval_type,
                approval_requests.status,
                approval_requests.decision_note
            FROM approval_requests
            JOIN agents ON agents.id = approval_requests.requested_by_agent_id
            WHERE approval_requests.id = ?
            """,
            (approval_id,),
        ).fetchone()

    def _decode_learning_source(self, row: sqlite3.Row) -> dict:
        item = dict(row)
        item["consent_required"] = bool(item["consent_required"])
        return item

    def _decode_evidence(self, row: sqlite3.Row) -> dict:
        item = dict(row)
        try:
            item["evidence"] = json.loads(item["evidence"])
        except json.JSONDecodeError:
            item["evidence"] = []
        return item

    def _decode_tags(self, row: sqlite3.Row) -> dict:
        item = dict(row)
        try:
            item["tags"] = json.loads(item["tags"])
        except json.JSONDecodeError:
            item["tags"] = []
        return item
