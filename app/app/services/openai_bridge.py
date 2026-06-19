from __future__ import annotations

import os
from pathlib import Path


def load_dotenv() -> None:
    """Load a tiny .env file without requiring python-dotenv."""

    env_path = Path(".env")
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class OpenAIBridge:
    """Optional model bridge. The app works without this being configured."""

    def __init__(self) -> None:
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = os.getenv("OPENAI_MODEL", "gpt-5.5").strip()

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def create_executive_summary(self, goal: str, snapshot: dict, events: list[dict]) -> str | None:
        if not self.enabled:
            return None

        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            response = client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You are the concise voice of N.E.X.U.S, a calm personal operating system. "
                            "Summarize product health, risks, and next actions in 4 sentences or fewer."
                        ),
                    },
                    {
                        "role": "user",
                        "content": {
                            "goal": goal,
                            "analytics": snapshot,
                            "agent_events": events,
                        },
                    },
                ],
            )
            return response.output_text
        except Exception:
            return None
