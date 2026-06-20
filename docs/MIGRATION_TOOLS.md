# Migration Tools

This file is the handoff bundle for continuing R.A.M.B.O. from another AI or session.

## Project Identity

- Project: R.A.M.B.O.
- Brand line: Autonomy. Precision. Execution.
- Council surface: R.A.M.B.O. home and the dedicated Round Table page
- Primary goal: a voice-capable, multi-Brain personal operating system with approvals, memory, learning, and financial stewardship.

## Current Live Surfaces

- Dashboard: `http://127.0.0.1:8004/`
- Council home: `http://127.0.0.1:8004/council/`
- Round Table page: `http://127.0.0.1:8004/council/round-table.html`
- Steward budget download: `http://127.0.0.1:8004/council/downloads/steward-budget-planner.html`
- Steward page: `http://127.0.0.1:8004/council/agents/steward.html`

## Key Files

- [AGENTS.md](C:/Users/dokun/Documents/Codex/Jarvis-Agent/AGENTS.md)
- [START_HERE.md](C:/Users/dokun/Documents/Codex/Jarvis-Agent/START_HERE.md)
- [app/app/main.py](C:/Users/dokun/Documents/Codex/Jarvis-Agent/app/app/main.py)
- [app/app/services/memory.py](C:/Users/dokun/Documents/Codex/Jarvis-Agent/app/app/services/memory.py)
- [app/app/services/orchestrator.py](C:/Users/dokun/Documents/Codex/Jarvis-Agent/app/app/services/orchestrator.py)
- [app/static/index.html](C:/Users/dokun/Documents/Codex/Jarvis-Agent/app/static/index.html)
- [round-table/build_pages.py](C:/Users/dokun/Documents/Codex/Jarvis-Agent/round-table/build_pages.py)
- [round-table/data/agents.json](C:/Users/dokun/Documents/Codex/Jarvis-Agent/round-table/data/agents.json)
- [round-table/assets/style.css](C:/Users/dokun/Documents/Codex/Jarvis-Agent/round-table/assets/style.css)
- [round-table/assets/core3d.js](C:/Users/dokun/Documents/Codex/Jarvis-Agent/round-table/assets/core3d.js)
- [round-table/assets/app.js](C:/Users/dokun/Documents/Codex/Jarvis-Agent/round-table/assets/app.js)
- [docs/RAMBO_BRAIN_PROMPTS.md](C:/Users/dokun/Documents/Codex/Jarvis-Agent/docs/RAMBO_BRAIN_PROMPTS.md)
- [round-table/README.md](C:/Users/dokun/Documents/Codex/Jarvis-Agent/round-table/README.md)

## What Already Exists

### R.A.M.B.O. App

- FastAPI backend running in mock mode without API keys.
- SQLite memory for tasks, logs, approvals, learning, and finance.
- Dashboard sections for approvals, learning, Steward finance, Brains, and memory.
- Approval endpoints:
  - `POST /api/approvals/{id}/approve`
  - `POST /api/approvals/{id}/reject`
- Finance endpoints:
  - `GET /api/finance`
  - `POST /api/finance/expenses`
  - `POST /api/finance/budget-categories`
  - `POST /api/finance/savings-goals`
  - `POST /api/finance/investments`

### The Round Table

- `index.html` is now the centralized `R.A.M.B.O.` home page.
- `round-table.html` is the dedicated council overview page.
- Each Brain has a separate page with avatar-based identity visuals.
- Approvals and Learning have separate pages with their own system node scenes.
- Approvals and Learning now use dedicated 3D system node scenes with centered avatars, orbit labels, and cleaner HUD title capsules.
- Steward has a manual-entry budget planner and a downloadable copy.
- The home page now uses a single large globe section first, with Council data below it.
- The home page includes a direct `View Brain Roster` button instead of duplicating the roster there.
- The home page now includes a `R.A.M.B.O. COMMAND SEAT` section below Brain Data, carrying the old Overseer role, critical tier, task stats, core directives, and mission journal from the shared internal `nexus` record.
- Globe nodes now open hover/click bubbles that show the Brain's current work.
- Round Table Brains now orbit the globe instead of stacking into the center.
- Each Brain page now has one centered avatar scene with orbiting task stats.
- Sidebar navigation now keeps `R.A.M.B.O.` as a standalone home/overseer item, with only `Round Table` inside the `COUNCIL` group.
- The globe/core animation renders on every page that uses `core-canvas`.
- The shared `core3d.js` visual now includes an aura shell, denser particles, additive glow, and neural filaments for a more realistic futuristic look.
- Council journals hydrate from SQLite through `GET /api/council/journals` when served by FastAPI.
- Steward planner entries persist to local SQLite through `GET /api/steward/budget` and `PUT /api/steward/budget`.
- R.A.M.B.O. home now has a Daily Briefing panel hydrated by `GET /api/briefing/daily`.
- R.A.M.B.O. home now has a Devchain-inspired Operating Loop panel translated into the local Brain roster.
- Visible branding is now R.A.M.B.O. — Responsive Autonomous Multi-Brain Operator.
- The tactical UI palette now uses Midnight Black, Tactical Red, Steel Gray, Signal White, and Pulse Orange.
- The daily briefing uses the boot phrase: `R.A.M.B.O. online. Systems synchronized. Standing by for your command.`

## Brain Roster

- R.A.M.B.O.
- Architect
- Engineer
- Seeker
- Analyst
- Sentinel
- Steward
- Link
- Keeper
- Echo
- Pilot

## Safety Rules

- Ask before deleting files.
- Ask before spending money.
- Ask before contacting people or sending messages.
- Ask before exposing private information.
- Ask before connecting financial accounts.
- Ask before sensitive or hard-to-reverse actions.
- Keep learning from connected plugins approval-gated.
- Keep Steward in manual or approval-gated mode until stronger financial controls exist.

## Files To Read First

1. `AGENTS.md`
2. `START_HERE.md`
3. `app/app/main.py`
4. `app/app/services/memory.py`
5. `app/app/services/orchestrator.py`
6. `round-table/build_pages.py`
7. `round-table/data/agents.json`
8. `docs/RAMBO_BRAIN_PROMPTS.md`

## Current State Summary

- The core R.A.M.B.O. backend is working.
- The council UI has been imported and converted into a Codex-owned local site.
- The home page now says `R.A.M.B.O.` in bold and uses the Round Table globe as the central visual.
- The standalone R.A.M.B.O. home page now includes the old Overseer data below Brain Data.
- Each Brain page includes the globe motif, a tailored avatar, and a short live-info list.
- Brain mission journals now replace baked sample content with SQLite-backed live journal data at runtime.
- The sidebar now combines the old standalone/Overseer duplicate by keeping one standalone `R.A.M.B.O.` item and removing the old `OVERSEER` group.
- Steward has a downloadable HTML planner file in `round-table/downloads/steward-budget-planner.html`.
- Steward's in-dashboard planner saves manual entries to local SQLite.
- Daily briefing now reports greeting, Detroit time/day/date, weather fallback/live weather, Calendar connection status, Brain briefings, today's task focus, and operating loop guardrails.
- `docs/RAMBO_BRAIN_PROMPTS.md` defines the scalable R.A.M.B.O. Brain identity, routing prompts, master persona, mission statement, branding kit, and loop guardrails.
- The latest handoff note is `docs/ROADMAP_16_2026-06-20_06-05-41.md`.

## Recommended Next Steps

1. Add real Brain handoff/task-loop records so `agent_logs` fills the live journals automatically.
2. Add `POST /api/workflows/dispatch` for low-risk Brain routing.
3. Add a daily briefing history table so R.A.M.B.O. remembers each briefing it gave.
4. Wire Calendar after Sentinel approval so the briefing can show real meetings.
5. Add editable fields for savings goals and investments in Steward, not only add-card buttons.
6. Add animated node trails between Brains during handoff dispatch.
7. Add screenshot QA for desktop/mobile visual alignment.
8. Add a reliable local server start/stop helper for the desktop workflow on port `8004`.
9. Continue into real integration work only after the approval boundary is ready.

## Commands

```powershell
.\.venv\Scripts\python.exe round-table\build_pages.py
.\.venv\Scripts\python.exe -m compileall app\app
```

## Notes

- `files.zip` has already been imported and removed from the workspace.
- The current Round Table site is the Codex version of the imported council, not the raw archive.
