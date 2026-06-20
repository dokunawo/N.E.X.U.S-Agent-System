from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.services.memory import MemoryStore


DETROIT_LAT = 42.3314
DETROIT_LON = -83.0458
DETROIT_TZ = "America/Detroit"
DETROIT_LOCAL = timezone(timedelta(hours=-4), "America/Detroit")


WEATHER_CODES = {
    0: "Clear",
    1: "Mostly clear",
    2: "Partly cloudy",
    3: "Cloudy",
    45: "Fog",
    48: "Freezing fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    80: "Light showers",
    81: "Showers",
    82: "Heavy showers",
    95: "Thunderstorm",
}


WORKFLOW_STAGES = [
    {
        "stage": "Capture",
        "lead": "R.A.M.B.O.",
        "support": ["Echo", "Pilot"],
        "handoff": "Convert the request into a clear task, success condition, and risk note.",
    },
    {
        "stage": "Plan",
        "lead": "Architect",
        "support": ["Pilot"],
        "handoff": "Sequence the work into phases, dependencies, and acceptance checks.",
    },
    {
        "stage": "Validate",
        "lead": "Seeker",
        "support": ["Analyst", "Sentinel"],
        "handoff": "Check facts, current sources, data gaps, and risk boundaries.",
    },
    {
        "stage": "Build",
        "lead": "Engineer",
        "support": ["Link", "Keeper"],
        "handoff": "Implement the change, wire integrations, and store the durable state.",
    },
    {
        "stage": "Review",
        "lead": "Sentinel",
        "support": ["Analyst", "Echo"],
        "handoff": "Review risk, verify behavior, and prepare a plain-English report.",
    },
    {
        "stage": "Remember",
        "lead": "Keeper",
        "support": ["Pilot", "R.A.M.B.O."],
        "handoff": "Record what happened, what is queued, and what should happen next.",
    },
]


class BriefingService:
    def __init__(self, memory: MemoryStore) -> None:
        self.memory = memory

    def daily_briefing(self) -> dict[str, Any]:
        now = datetime.now(DETROIT_LOCAL)
        journals = self.memory.council_journals(limit_per_section=3)["journals"]
        tasks = self.memory.recent_tasks(limit=8)
        approvals = self.memory.pending_approvals(limit=8)
        finance = self.memory.finance_snapshot(limit=6)

        return {
            "greeting": self._greeting(now),
            "location": "Detroit, Michigan",
            "time": {
                "iso": now.isoformat(),
                "display": now.strftime("%I:%M %p").lstrip("0"),
                "day": now.strftime("%A"),
                "date": now.strftime("%B %d, %Y"),
                "timezone": "America/Detroit",
            },
            "weather": self._detroit_weather(),
            "calendar": {
                "status": "not_connected",
                "summary": "Calendar is not connected yet. Link should wire Google Calendar after Sentinel approval.",
                "meetings": [],
            },
            "agent_briefing": self._agent_briefing(journals),
            "today": self._today_summary(tasks, approvals, finance),
            "workflow": {
                "source": "Devchain-inspired operating pattern, translated into R.A.M.B.O. roles.",
                "loop_mode": "approval-gated",
                "stages": WORKFLOW_STAGES,
                "guardrails": [
                    "Sentinel approval is required before money, messages, deletion, private data exposure, or account connections.",
                    "Keeper records task/log/memory entries so the loop can learn from what happened.",
                    "R.A.M.B.O. gives the final synthesized answer after specialist Brains report back.",
                ],
            },
        }

    def _greeting(self, now: datetime) -> str:
        hour = now.hour
        boot = "R.A.M.B.O. online. Systems synchronized. Standing by for your command."
        if hour < 12:
            return f"Good morning, Sir. {boot}"
        if hour < 18:
            return f"Good afternoon, Sir. {boot}"
        return f"Good evening, Sir. {boot}"

    def _detroit_weather(self) -> dict[str, Any]:
        params = urlencode(
            {
                "latitude": DETROIT_LAT,
                "longitude": DETROIT_LON,
                "current": "temperature_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "timezone": DETROIT_TZ,
            }
        )
        url = f"https://api.open-meteo.com/v1/forecast?{params}"
        try:
            request = Request(url, headers={"User-Agent": "RAMBO-local-dashboard/0.1"})
            with urlopen(request, timeout=3.5) as response:
                payload = json.loads(response.read().decode("utf-8"))
            current = payload.get("current", {})
            code = int(current.get("weather_code", -1))
            return {
                "status": "live",
                "source": "Open-Meteo",
                "summary": WEATHER_CODES.get(code, "Weather data available"),
                "temperature_f": current.get("temperature_2m"),
                "feels_like_f": current.get("apparent_temperature"),
                "wind_mph": current.get("wind_speed_10m"),
                "precipitation": current.get("precipitation"),
            }
        except Exception:
            return {
                "status": "unavailable",
                "source": "Open-Meteo",
                "summary": "Weather connection unavailable from this local server right now.",
                "temperature_f": None,
                "feels_like_f": None,
                "wind_mph": None,
                "precipitation": None,
            }

    def _agent_briefing(self, journals: dict[str, dict[str, list[dict]]]) -> list[dict[str, str]]:
        agents = self.memory.list_agents()
        brief: list[dict[str, str]] = []
        for agent in agents:
            journal = journals.get(agent["id"], {})
            completed = journal.get("completed") or []
            in_progress = journal.get("inProgress") or []
            queued = journal.get("queued") or []
            if completed:
                latest = completed[0]
                status = f"Last completed: {latest['title']}."
            elif in_progress:
                latest = in_progress[0]
                status = f"In motion: {latest['title']}."
            elif queued:
                latest = queued[0]
                status = f"Queued: {latest['title']}."
            else:
                status = "No live SQLite journal entries yet."
            brief.append({"agent": agent["name"], "role": agent["role"], "status": status})
        return brief

    def _today_summary(self, tasks: list[dict], approvals: list[dict], finance: dict) -> dict[str, Any]:
        next_tasks = [
            {"title": task["title"], "status": task["status"], "owner": task["owner_agent"]}
            for task in tasks[:5]
        ]
        return {
            "focus": "Build the handoff loop and keep memory live before adding personal account integrations.",
            "tasks": next_tasks,
            "approvals_waiting": len(approvals),
            "finance_mode": finance.get("summary", {}).get("mode", "manual"),
            "recommended_next": [
                "Pilot should create handoff records for each new task.",
                "Keeper should write every handoff into SQLite Brain logs.",
                "Sentinel should gate anything involving accounts, messages, money, deletion, or private data.",
            ],
        }
