from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.services.analytics import AnalyticsService
from app.services.memory import MemoryStore
from app.services.orchestrator import Orchestrator


ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "static"

analytics = AnalyticsService()
memory = MemoryStore()
orchestrator = Orchestrator(analytics=analytics, memory=memory)

app = FastAPI(
    title="N.E.X.U.S Dashboard MVP",
    description="A local multi-agent dashboard scaffold with mock analytics and memory.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class RunRequest(BaseModel):
    goal: str = Field(..., min_length=2, max_length=500)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "mode": orchestrator.mode,
        "service": "nexus-dashboard-mvp",
    }


@app.get("/api/dashboard")
def dashboard() -> dict:
    snapshot = analytics.get_snapshot()
    return {
        "analytics": snapshot,
        "memory": memory.recent_runs(limit=8),
        "mode": orchestrator.mode,
    }


@app.post("/api/run")
def run_agent(request: RunRequest) -> dict:
    return orchestrator.handle_goal(request.goal)


@app.get("/api/memory")
def get_memory() -> dict:
    return {"runs": memory.recent_runs(limit=25)}


@app.delete("/api/memory")
def clear_memory() -> dict:
    memory.clear()
    return {"ok": True, "runs": []}
