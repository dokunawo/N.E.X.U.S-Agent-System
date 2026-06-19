from __future__ import annotations

from datetime import datetime, timezone


TASK_STATUSES = [
    "received",
    "planning",
    "running",
    "waiting_for_approval",
    "completed",
    "blocked",
]

AGENT_LOG_STATUSES = [
    "standby",
    "ready",
    "online",
    "complete",
    "attention",
    "approval_required",
    "blocked",
]

RISK_LEVELS = ["low", "medium", "high", "critical"]

APPROVAL_STATUSES = [
    "requested",
    "approved",
    "rejected",
    "cancelled",
]

MEMORY_KINDS = [
    "run_summary",
    "decision",
    "preference",
    "risk_note",
    "integration_note",
]

AGENT_ROSTER = [
    {
        "id": "nexus",
        "name": "N.E.X.U.S",
        "role": "Overall operator",
        "purpose": "Coordinate the agent network and combine final advice for Daniel.",
        "access_scope": "Can route work, summarize results, and request support from specialized agents.",
        "risk_boundary": "Must ask Sentinel and Daniel before sensitive or difficult-to-reverse actions.",
        "default_status": "online",
    },
    {
        "id": "architect",
        "name": "Architect",
        "role": "Strategy and planning",
        "purpose": "Break goals into clear steps and plan the order of work.",
        "access_scope": "Can inspect task context and propose plans.",
        "risk_boundary": "Does not execute sensitive actions directly.",
        "default_status": "ready",
    },
    {
        "id": "engineer",
        "name": "Engineer",
        "role": "Coding and technical build work",
        "purpose": "Write, edit, debug, and verify project code.",
        "access_scope": "Can modify project files when Daniel asks for implementation.",
        "risk_boundary": "Must ask before deleting files or making broad system-wide changes.",
        "default_status": "standby",
    },
    {
        "id": "seeker",
        "name": "Seeker",
        "role": "Research",
        "purpose": "Find and summarize useful information.",
        "access_scope": "Can use approved sources and cite findings.",
        "risk_boundary": "Must protect private information and avoid unsupported claims.",
        "default_status": "standby",
    },
    {
        "id": "analyst",
        "name": "Analyst",
        "role": "Data analysis",
        "purpose": "Study metrics, patterns, changes, and evidence.",
        "access_scope": "Can read connected data that is relevant to the task.",
        "risk_boundary": "Must separate facts from guesses and flag data gaps.",
        "default_status": "ready",
    },
    {
        "id": "sentinel",
        "name": "Sentinel",
        "role": "Safety and system protection",
        "purpose": "Guard privacy, permissions, sensitive actions, and risk.",
        "access_scope": "Can review any proposed action for risk.",
        "risk_boundary": "Cannot approve actions for Daniel; it can only request approval.",
        "default_status": "ready",
    },
    {
        "id": "link",
        "name": "Link",
        "role": "API and integration design",
        "purpose": "Connect N.E.X.U.S to outside services.",
        "access_scope": "Can design and test integrations in mock mode first.",
        "risk_boundary": "Must ask before connecting accounts or exposing private data.",
        "default_status": "standby",
    },
    {
        "id": "keeper",
        "name": "Keeper",
        "role": "Storage and memory",
        "purpose": "Maintain task history, memory, database structure, and retrieval.",
        "access_scope": "Can store useful local project memory.",
        "risk_boundary": "Must avoid storing secrets and should keep sensitive memory explainable.",
        "default_status": "ready",
    },
    {
        "id": "echo",
        "name": "Echo",
        "role": "User-facing communication",
        "purpose": "Turn system work into clear plain-English answers.",
        "access_scope": "Can prepare summaries, drafts, and status language.",
        "risk_boundary": "Must ask before sending messages to other people.",
        "default_status": "ready",
    },
    {
        "id": "pilot",
        "name": "Pilot",
        "role": "Task management and follow-up",
        "purpose": "Track active tasks, completed work, next steps, and follow-ups.",
        "access_scope": "Can organize task records and suggest next actions.",
        "risk_boundary": "Must ask before scheduling, contacting people, or changing external systems.",
        "default_status": "ready",
    },
]

DATA_SOURCES = [
    {
        "id": "manual",
        "name": "Manual entry",
        "kind": "local_input",
        "status": "active",
        "privacy_level": "private",
        "detail": "Typed goals and dashboard actions Daniel enters directly.",
    },
    {
        "id": "mock_analytics",
        "name": "Mock analytics",
        "kind": "mock_data",
        "status": "active",
        "privacy_level": "demo",
        "detail": "Deterministic sample metrics used until real data sources are connected.",
    },
    {
        "id": "calendar",
        "name": "Calendar",
        "kind": "personal_integration",
        "status": "planned",
        "privacy_level": "sensitive",
        "detail": "Planned source for schedule context after approval.",
    },
    {
        "id": "gmail",
        "name": "Gmail",
        "kind": "personal_integration",
        "status": "planned",
        "privacy_level": "sensitive",
        "detail": "Planned source for inbox context after approval.",
    },
    {
        "id": "notes",
        "name": "Notes",
        "kind": "personal_integration",
        "status": "planned",
        "privacy_level": "private",
        "detail": "Planned source for saved ideas and reference notes.",
    },
    {
        "id": "tasks",
        "name": "Tasks",
        "kind": "personal_integration",
        "status": "planned",
        "privacy_level": "private",
        "detail": "Planned source for reminders, todos, and follow-up tracking.",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def agent_id_from_name(name: str) -> str:
    normalized = name.lower().replace(".", "").replace(" ", "_")
    if normalized == "nexus":
        return "nexus"

    for agent in AGENT_ROSTER:
        if agent["name"].lower() == name.lower():
            return agent["id"]

    return normalized
