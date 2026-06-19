from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class Metric:
    label: str
    value: str
    delta: str
    tone: str


class AnalyticsService:
    """Provides mock app analytics until real integrations are connected."""

    def get_snapshot(self) -> dict:
        now = datetime.now(timezone.utc)
        daily_active = [892, 936, 980, 1044, 1108, 1186, 1248]
        conversion = [4.9, 5.2, 5.8, 6.1, 6.0, 6.5, 6.8]
        revenue = [1490, 1615, 1760, 2010, 2195, 2480, 2840]

        return {
            "generated_at": now.isoformat(),
            "metrics": [
                Metric("Active users", "1,248", "+14.1%", "good").__dict__,
                Metric("Conversion", "6.8%", "+0.7 pts", "good").__dict__,
                Metric("Revenue today", "$2,840", "+12.6%", "good").__dict__,
                Metric("API latency", "183 ms", "-22 ms", "good").__dict__,
                Metric("Error events", "14", "+5", "watch").__dict__,
                Metric("Churn risk", "3.2%", "-0.4 pts", "good").__dict__,
            ],
            "series": [
                {
                    "label": (now - timedelta(days=6 - index)).strftime("%a"),
                    "active_users": daily_active[index],
                    "conversion": conversion[index],
                    "revenue": revenue[index],
                }
                for index in range(7)
            ],
            "integrations": [
                {
                    "name": "Product analytics",
                    "status": "healthy",
                    "detail": "Events are flowing normally.",
                },
                {
                    "name": "Billing",
                    "status": "healthy",
                    "detail": "Revenue and subscription data synced.",
                },
                {
                    "name": "Error tracking",
                    "status": "watch",
                    "detail": "Checkout errors are up over the last hour.",
                },
                {
                    "name": "Repository",
                    "status": "healthy",
                    "detail": "Latest deploy passed automated checks.",
                },
            ],
            "agent_roster": [
                {
                    "name": "N.E.X.U.S",
                    "status": "online",
                    "task": "Operating as the command layer over the agent network.",
                    "confidence": 0.95,
                },
                {
                    "name": "Architect",
                    "status": "ready",
                    "task": "Standing by for strategy, planning, and prioritization.",
                    "confidence": 0.9,
                },
                {
                    "name": "Engineer",
                    "status": "standby",
                    "task": "Ready for coding and technical build work.",
                    "confidence": 0.88,
                },
                {
                    "name": "Seeker",
                    "status": "standby",
                    "task": "Ready for research when live sources are connected.",
                    "confidence": 0.86,
                },
                {
                    "name": "Analyst",
                    "status": "complete",
                    "task": "Reviewed the current operational metrics.",
                    "confidence": 0.92,
                },
                {
                    "name": "Sentinel",
                    "status": "attention",
                    "task": "Flagged the checkout error increase.",
                    "confidence": 0.84,
                },
                {
                    "name": "Steward",
                    "status": "ready",
                    "task": "Ready to track budgets, spending, savings, and investment context in manual mode.",
                    "confidence": 0.86,
                },
                {
                    "name": "Link",
                    "status": "standby",
                    "task": "Waiting for Calendar, Gmail, Notes, and Tasks connection work.",
                    "confidence": 0.82,
                },
                {
                    "name": "Keeper",
                    "status": "ready",
                    "task": "Maintaining memory and storage structure.",
                    "confidence": 0.9,
                },
                {
                    "name": "Echo",
                    "status": "ready",
                    "task": "Preparing clear user-facing summaries.",
                    "confidence": 0.9,
                },
                {
                    "name": "Pilot",
                    "status": "ready",
                    "task": "Queued next-step recommendations.",
                    "confidence": 0.9,
                },
            ],
        }
