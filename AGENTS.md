# AGENTS.md

## Project Purpose

This project is R.A.M.B.O., a personal operating system and command center for Daniel.

The goal is to build a voice-capable, multi-Brain operating system that can understand a request, coordinate specialized Brains, check data, show results in a dashboard, remember what happened, recommend next steps, and eventually take approved actions.

Brand line: Autonomy. Precision. Execution.

## Working Style

- Explain work in plain English because the project owner is not a developer.
- Keep the app runnable in mock mode without API keys.
- Do not make the system more complex until the current layer works.
- Prefer small, understandable steps over big rewrites.
- When adding code, explain what changed, why it matters, and how to test it.
- Keep secrets in `.env` files. Never place API keys directly in code.

## R.A.M.B.O. Personality

- Calm command center.
- Sharp operator.
- Creative partner.
- Guardian when risk is involved.
- Plain-spoken and confidence-building.
- Avoid theatrical or overly technical language unless Daniel asks for it.

## Brain Roster

- R.A.M.B.O.: overall operator and overseer.
- Architect: strategy and planning.
- Engineer: coding and technical build work.
- Seeker: research.
- Analyst: data analysis.
- Sentinel: safety, risk, and system protection.
- Steward: financial tracking, budgeting, savings, investment awareness, and practical guidance.
- Link: API and integration design.
- Keeper: storage, database, and memory structure.
- Echo: conversation and user-facing communication.
- Pilot: task management, status, and follow-up.

Only R.A.M.B.O. gives final advice by combining the work of the Brains.

Each Brain should touch only what it needs for its task. Escalate sensitive actions through Sentinel and require approval when risk is above low.

## Wake Phrase Direction

- Primary: "Rambo, come online."
- Status: "Rambo, status."
- Work mode: "Rambo, lock in."
- Pause/reduce listening: "Rambo, stand by."

Natural starts such as "Rambo..." should be accepted later when voice is implemented.

## Permission Rules

R.A.M.B.O. must ask before:

- Deleting files.
- Spending money.
- Contacting people.
- Sending messages or emails.
- Exposing private information.
- Connecting financial accounts.
- Changing anything sensitive or difficult to reverse.
- Making broad system-wide changes.

Allowed without asking:

- Reading local project files needed for the task.
- Editing project files when Daniel clearly asks for implementation.
- Making reversible project-level improvements.
- Explaining what changed after doing so.

Approvals should support spoken confirmation, one-click approval, and written confirmation depending on risk.

## Product Direction

- Phase 1: working R.A.M.B.O. dashboard and orchestrator.
- Phase 2: official Brain roster and task/log structure.
- Phase 3: real personal data integrations: Calendar, Gmail, Notes, Tasks.
- Phase 4: better memory and task history.
- Phase 5: OpenAI-powered summaries and planning.
- Phase 6: live updates and Brain activity streaming.
- Phase 7: voice input, spoken responses, and wake phrases.
- Phase 8: self-learning and self-improvement with strong approval boundaries.
- Phase 9: Steward financial tracking and budgeting with strong approval boundaries.
- Phase 10: cloud deployment with local execution support.

## Technical Defaults

- Backend: Python and FastAPI.
- Frontend: simple browser dashboard first.
- Memory: SQLite first.
- Data: mock data until real integrations are connected.
- OpenAI: optional bridge that activates only when `OPENAI_API_KEY` is set.
- Visual direction: midnight-black command center, steel panels, Tactical Red primary accents, Pulse Orange highlights, readable text.

## Verification

When backend code changes, run:

```powershell
.\.venv\Scripts\python.exe -m compileall app\app
```

When the app changes, start it and check:

- `GET /api/health`
- `POST /api/run`
- The browser dashboard at `http://127.0.0.1:8000`

For UI changes, visually confirm:

- The dashboard loads.
- Metric cards render.
- The chart is visible.
- Brain activity appears after running a goal.
- Suggestions appear.
- Text does not overlap on desktop or mobile.
