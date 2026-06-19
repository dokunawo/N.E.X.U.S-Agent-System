from __future__ import annotations

from dataclasses import dataclass

from app.services.analytics import AnalyticsService
from app.services.memory import MemoryStore
from app.services.openai_bridge import OpenAIBridge


@dataclass
class AgentEvent:
    agent: str
    status: str
    message: str

    def as_dict(self) -> dict:
        return {
            "agent": self.agent,
            "status": self.status,
            "message": self.message,
        }


class AnalyticsAgent:
    name = "Analyst"

    def run(self, snapshot: dict) -> AgentEvent:
        active_users = snapshot["metrics"][0]["value"]
        revenue = snapshot["metrics"][2]["value"]
        return AgentEvent(
            self.name,
            "complete",
            f"Found {active_users} active users and {revenue} revenue today.",
        )


class ReliabilityAgent:
    name = "Sentinel"

    def run(self, snapshot: dict) -> AgentEvent:
        errors = next(metric for metric in snapshot["metrics"] if metric["label"] == "Error events")
        return AgentEvent(
            self.name,
            "attention" if errors["tone"] == "watch" else "complete",
            f"Error events are at {errors['value']} with trend {errors['delta']}.",
        )


class GrowthAgent:
    name = "Architect"

    def run(self, snapshot: dict) -> AgentEvent:
        conversion = next(metric for metric in snapshot["metrics"] if metric["label"] == "Conversion")
        return AgentEvent(
            self.name,
            "complete",
            f"Conversion is {conversion['value']} today, moving {conversion['delta']}.",
        )


class StrategyAgent:
    name = "Pilot"

    def run(self, snapshot: dict) -> tuple[AgentEvent, list[str]]:
        suggestions = [
            "Investigate checkout errors before scaling acquisition spend.",
            "Promote the onboarding flow that is converting best this week.",
            "Create a daily N.E.X.U.S status report comparing priorities, risks, and opportunities.",
        ]
        return (
            AgentEvent(
                self.name,
                "complete",
                "Prepared the highest-impact next actions for N.E.X.U.S.",
            ),
            suggestions,
        )


class StandbyAgent:
    def __init__(self, name: str, message: str) -> None:
        self.name = name
        self.message = message

    def run(self, snapshot: dict) -> AgentEvent:
        return AgentEvent(self.name, "standby", self.message)


class Orchestrator:
    def __init__(self, analytics: AnalyticsService, memory: MemoryStore) -> None:
        self.analytics = analytics
        self.memory = memory
        self.openai = OpenAIBridge()
        self.agents = [
            StandbyAgent("N.E.X.U.S", "Coordinated the active agent pass."),
            StandbyAgent("Architect", "Reviewed the request for planning context."),
            AnalyticsAgent(),
            ReliabilityAgent(),
            StandbyAgent("Engineer", "No code action required for this status request."),
            StandbyAgent("Seeker", "No external research source connected yet."),
            StandbyAgent("Link", "Integration work is queued for Calendar, Gmail, Notes, and Tasks."),
            StandbyAgent("Keeper", "Prepared the run for memory storage."),
            StandbyAgent("Echo", "Prepared the user-facing summary language."),
        ]
        self.strategy = StrategyAgent()

    @property
    def mode(self) -> str:
        return "openai" if self.openai.enabled else "mock"

    def handle_goal(self, goal: str) -> dict:
        snapshot = self.analytics.get_snapshot()

        events = [agent.run(snapshot).as_dict() for agent in self.agents]
        strategy_event, suggestions = self.strategy.run(snapshot)
        events.append(strategy_event.as_dict())

        summary = self.openai.create_executive_summary(goal, snapshot, events)
        if not summary:
            summary = self._mock_summary(goal, snapshot)

        payload = {
            "goal": goal,
            "summary": summary,
            "analytics": snapshot,
            "events": events,
            "suggestions": suggestions,
            "mode": self.mode,
        }
        saved = self.memory.save_run(goal=goal, summary=summary, payload=payload)
        payload["memory_entry"] = saved
        payload["recent_memory"] = self.memory.recent_runs(limit=8)
        return payload

    def _mock_summary(self, goal: str, snapshot: dict) -> str:
        metrics = {metric["label"]: metric for metric in snapshot["metrics"]}
        return (
            f"For '{goal}', the app looks healthy overall: active users are "
            f"{metrics['Active users']['value']} ({metrics['Active users']['delta']}), revenue is "
            f"{metrics['Revenue today']['value']} ({metrics['Revenue today']['delta']}), and conversion is "
            f"{metrics['Conversion']['value']}. The main thing to watch is checkout reliability, with "
            f"{metrics['Error events']['value']} error events today. N.E.X.U.S would fix that before pushing a bigger "
            "growth campaign."
        )
