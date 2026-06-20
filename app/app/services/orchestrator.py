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
            "Create a daily R.A.M.B.O. status report comparing priorities, risks, and opportunities.",
        ]
        return (
            AgentEvent(
                self.name,
                "complete",
                "Prepared the highest-impact next actions for R.A.M.B.O.",
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
            StandbyAgent("R.A.M.B.O.", "Coordinated the active Brain pass."),
            StandbyAgent("Architect", "Reviewed the request for planning context."),
            AnalyticsAgent(),
            ReliabilityAgent(),
            StandbyAgent("Engineer", "No code action required for this status request."),
            StandbyAgent("Seeker", "No external research source connected yet."),
            StandbyAgent("Steward", "Tracking financial context in manual mode until accounts are approved."),
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
        risk = self._assess_risk(goal)
        learning_signals = self.memory.record_learning_from_goal(goal)

        events = [agent.run(snapshot).as_dict() for agent in self.agents]
        if learning_signals:
            events.append(
                AgentEvent(
                    "Keeper",
                    "learning",
                    f"Saved {len(learning_signals)} local learning signal(s) from this request.",
                ).as_dict()
            )
        strategy_event, suggestions = self.strategy.run(snapshot)
        events.append(strategy_event.as_dict())
        suggestions.append("Let Steward build a starter budget once monthly income and major expenses are entered.")

        approval = None
        task_status = "completed"
        if risk["requires_approval"]:
            approval = self._build_approval_request(goal, risk)
            task_status = "waiting_for_approval"
            events.append(
                AgentEvent(
                    "Sentinel",
                    "approval_required",
                    f"Approval required before R.A.M.B.O. takes this {risk['level']} risk action.",
                ).as_dict()
            )
            suggestions.insert(0, "Review the pending approval before any sensitive action is taken.")

        summary = self.openai.create_executive_summary(goal, snapshot, events)
        if not summary:
            summary = self._mock_summary(goal, snapshot)

        if approval:
            summary = (
                f"{summary} Sentinel marked the requested action as {risk['level']} risk, so R.A.M.B.O. "
                "logged an approval request and will wait for Sir before taking action."
            )

        payload = {
            "goal": goal,
            "summary": summary,
            "analytics": snapshot,
            "events": events,
            "suggestions": suggestions,
            "risk": risk,
            "learning_signals": learning_signals,
            "mode": self.mode,
        }
        saved = self.memory.save_run(
            goal=goal,
            summary=summary,
            payload=payload,
            events=events,
            suggestions=suggestions,
            risk_level=risk["level"],
            task_status=task_status,
            approval=approval,
        )
        payload["memory_entry"] = saved
        payload["recent_memory"] = self.memory.recent_runs(limit=8)
        payload["operating"] = self.memory.operating_snapshot(limit=8)
        return payload

    def _mock_summary(self, goal: str, snapshot: dict) -> str:
        metrics = {metric["label"]: metric for metric in snapshot["metrics"]}
        return (
            f"For '{goal}', the app looks healthy overall: active users are "
            f"{metrics['Active users']['value']} ({metrics['Active users']['delta']}), revenue is "
            f"{metrics['Revenue today']['value']} ({metrics['Revenue today']['delta']}), and conversion is "
            f"{metrics['Conversion']['value']}. The main thing to watch is checkout reliability, with "
            f"{metrics['Error events']['value']} error events today. R.A.M.B.O. would fix that before pushing a bigger "
            "growth campaign."
        )

    def _assess_risk(self, goal: str) -> dict:
        text = goal.lower()
        risk_rules = [
            (
                "critical",
                [
                    "delete files",
                    "delete file",
                    "erase",
                    "wipe",
                    "drop table",
                    "reset database",
                    "api key",
                    "password",
                    "secret key",
                ],
            ),
            (
                "high",
                [
                    "send email",
                    "send message",
                    "contact ",
                    "spend",
                    "buy ",
                    "purchase",
                    "bank account",
                    "financial account",
                    "connect gmail",
                    "connect calendar",
                    "connect account",
                    "connect tasks",
                    "connect bank",
                    "connect notion",
                    "trade stock",
                    "buy stock",
                    "sell stock",
                    "move money",
                    "share private",
                    "expose private",
                    "post publicly",
                ],
            ),
            (
                "medium",
                [
                    "gmail",
                    "calendar",
                    "personal data",
                    "private information",
                    "oauth",
                    "external account",
                    "notion",
                    "bank",
                    "investment account",
                ],
            ),
        ]

        for level, keywords in risk_rules:
            matches = [keyword.strip() for keyword in keywords if keyword in text]
            if matches:
                return {
                    "level": level,
                    "requires_approval": True,
                    "matched_rules": matches,
                    "reason": self._risk_reason(level),
                }

        return {
            "level": "low",
            "requires_approval": False,
            "matched_rules": [],
            "reason": "No sensitive action boundary was detected.",
        }

    def _build_approval_request(self, goal: str, risk: dict) -> dict:
        approval_type = "written_confirmation" if risk["level"] in {"high", "critical"} else "one_click_confirmation"
        return {
            "requested_by_agent_id": "sentinel",
            "title": f"Approval needed: {risk['level']} risk action",
            "requested_action": goal,
            "reason": risk["reason"],
            "risk_level": risk["level"],
            "approval_type": approval_type,
            "payload": {"matched_rules": risk["matched_rules"]},
        }

    def _risk_reason(self, level: str) -> str:
        reasons = {
            "critical": "The request may delete data, expose secrets, or change something difficult to reverse.",
            "high": "The request may contact people, spend money, connect an account, or expose private information.",
            "medium": "The request touches personal context or an external account and should be approved first.",
        }
        return reasons[level]
