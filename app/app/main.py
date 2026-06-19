from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.services.analytics import AnalyticsService
from app.services.memory import MemoryStore
from app.services.orchestrator import Orchestrator


ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "static"
COUNCIL_DIR = ROOT.parent / "round-table"

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
app.mount("/council", StaticFiles(directory=COUNCIL_DIR, html=True), name="council")


class RunRequest(BaseModel):
    goal: str = Field(..., min_length=2, max_length=500)


class ApprovalDecision(BaseModel):
    decision_note: str = Field("", max_length=500)


class ExpenseRequest(BaseModel):
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=80)
    description: str = Field("", max_length=240)
    spent_at: str | None = Field(None, max_length=80)


class BudgetCategoryRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    monthly_limit: float = Field(..., ge=0)
    category_type: str = Field("manual", max_length=60)


class SavingsGoalRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    target_amount: float = Field(..., gt=0)
    current_amount: float = Field(0, ge=0)
    target_date: str | None = Field(None, max_length=80)
    notes: str = Field("", max_length=300)


class InvestmentPositionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    symbol: str | None = Field(None, max_length=20)
    position_type: str = Field("manual", max_length=60)
    current_value: float = Field(0, ge=0)
    cost_basis: float = Field(0, ge=0)
    risk_level: str = Field("unknown", max_length=60)
    notes: str = Field("", max_length=300)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/council")
def council() -> RedirectResponse:
    return RedirectResponse(url="/council/")


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
        "operating": memory.operating_snapshot(limit=8),
        "mode": orchestrator.mode,
    }


@app.post("/api/run")
def run_agent(request: RunRequest) -> dict:
    return orchestrator.handle_goal(request.goal)


@app.get("/api/memory")
def get_memory() -> dict:
    return {"runs": memory.recent_runs(limit=25)}


@app.get("/api/schema")
def get_schema() -> dict:
    return memory.schema_overview()


@app.get("/api/agents")
def get_agents() -> dict:
    return {"agents": memory.list_agents()}


@app.get("/api/tasks")
def get_tasks() -> dict:
    return {"tasks": memory.recent_tasks(limit=25)}


@app.get("/api/logs")
def get_logs() -> dict:
    return {"logs": memory.recent_logs(limit=50)}


@app.get("/api/memory/entries")
def get_memory_entries() -> dict:
    return {"memory_entries": memory.recent_memory_entries(limit=25)}


@app.get("/api/approvals")
def get_approvals() -> dict:
    return {"approvals": memory.pending_approvals(limit=25)}


@app.get("/api/learning")
def get_learning() -> dict:
    return memory.learning_snapshot(limit=25)


@app.get("/api/finance")
def get_finance() -> dict:
    return memory.finance_snapshot(limit=25)


@app.post("/api/finance/expenses")
def add_expense(request: ExpenseRequest) -> dict:
    expense = memory.add_expense(
        amount=request.amount,
        category=request.category,
        description=request.description,
        spent_at=request.spent_at,
    )
    return {"ok": True, "expense": expense, "finance": memory.finance_snapshot(limit=8)}


@app.post("/api/finance/budget-categories")
def set_budget_category(request: BudgetCategoryRequest) -> dict:
    category = memory.set_budget_category(
        name=request.name,
        monthly_limit=request.monthly_limit,
        category_type=request.category_type,
    )
    return {"ok": True, "category": category, "finance": memory.finance_snapshot(limit=8)}


@app.post("/api/finance/savings-goals")
def add_savings_goal(request: SavingsGoalRequest) -> dict:
    goal = memory.add_savings_goal(
        title=request.title,
        target_amount=request.target_amount,
        current_amount=request.current_amount,
        target_date=request.target_date,
        notes=request.notes,
    )
    return {"ok": True, "savings_goal": goal, "finance": memory.finance_snapshot(limit=8)}


@app.post("/api/finance/investments")
def add_investment_position(request: InvestmentPositionRequest) -> dict:
    position = memory.add_investment_position(
        name=request.name,
        symbol=request.symbol,
        position_type=request.position_type,
        current_value=request.current_value,
        cost_basis=request.cost_basis,
        risk_level=request.risk_level,
        notes=request.notes,
    )
    return {"ok": True, "investment": position, "finance": memory.finance_snapshot(limit=8)}


@app.post("/api/approvals/{approval_id}/approve")
def approve_approval(approval_id: int, decision: ApprovalDecision) -> dict:
    approval = memory.resolve_approval(
        approval_id=approval_id,
        decision="approved",
        decision_note=decision.decision_note,
    )
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval request not found.")

    return {
        "ok": True,
        "approval": approval,
        "operating": memory.operating_snapshot(limit=8),
    }


@app.post("/api/approvals/{approval_id}/reject")
def reject_approval(approval_id: int, decision: ApprovalDecision) -> dict:
    approval = memory.resolve_approval(
        approval_id=approval_id,
        decision="rejected",
        decision_note=decision.decision_note,
    )
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval request not found.")

    return {
        "ok": True,
        "approval": approval,
        "operating": memory.operating_snapshot(limit=8),
    }


@app.delete("/api/memory")
def clear_memory() -> dict:
    memory.clear()
    return {"ok": True, "runs": [], "operating": memory.operating_snapshot(limit=8)}
