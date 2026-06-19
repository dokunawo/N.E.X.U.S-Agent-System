# Migration Tools

This file is the handoff bundle for continuing N.E.X.U.S from another AI or session.

## Project Identity

- Project: N.E.X.U.S
- Brand line: Everything Connects Here.
- Council surface: N.E.X.U.S home and the dedicated Round Table page
- Primary goal: a voice-capable, multi-agent personal operating system with approvals, memory, learning, and financial stewardship.

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
- [round-table/README.md](C:/Users/dokun/Documents/Codex/Jarvis-Agent/round-table/README.md)

## What Already Exists

### N.E.X.U.S App

- FastAPI backend running in mock mode without API keys.
- SQLite memory for tasks, logs, approvals, learning, and finance.
- Dashboard sections for approvals, learning, Steward finance, agents, and memory.
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

- `index.html` is now the centralized `N.E.X.U.S` home page.
- `round-table.html` is the dedicated council overview page.
- Each agent has a separate page with avatar-based identity visuals.
- Approvals and Learning have separate pages with their own orb panels.
- Steward has a manual-entry budget planner and a downloadable copy.
- The home page now uses a single large globe section first, with Council data below it.
- The home page includes a direct `View Council Members` button instead of duplicating the roster there.
- The home page now includes a `N.E.X.U.S COMMAND SEAT` section below Council Data, carrying the old Overseer role, critical tier, task stats, core directives, and mission journal from the shared `nexus` agent record.
- Globe nodes now open hover/click bubbles that show the agent's current work.
- Round Table agents now orbit the globe instead of stacking into the center.
- Each agent page now has one centered avatar scene with orbiting task stats.
- Sidebar navigation now keeps `N.E.X.U.S` as a standalone home/overseer item, with only `Round Table` inside the `COUNCIL` group.
- The globe/core animation renders on every page that uses `core-canvas`.

## Agent Roster

- N.E.X.U.S
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

## Current State Summary

- The core N.E.X.U.S backend is working.
- The council UI has been imported and converted into a Codex-owned local site.
- The home page now says `N.E.X.U.S` in bold and uses the Round Table globe as the central visual.
- The standalone N.E.X.U.S home page now includes the old Overseer data below Council Data.
- Each agent page includes the globe motif, a tailored avatar, and a short live-info list.
- The sidebar now combines the old standalone/Overseer duplicate by keeping one standalone `N.E.X.U.S` item and removing the old `OVERSEER` group.
- Steward has a downloadable HTML planner file in `round-table/downloads/steward-budget-planner.html`.
- The latest handoff note is `docs/ROADMAP_12_2026-06-19_09-16-29.md`.

## Recommended Next Steps

1. Move the council journals from baked sample content into SQLite-backed live memory.
2. Add live data panels to the N.E.X.U.S home page from actual task and approval records.
3. Persist Steward planner entries into the backend instead of only static/downloadable pages.
4. Wire the N.E.X.U.S command-seat stats and journal to live SQLite data.
5. Add a reliable local server start/stop helper for the desktop workflow on port `8004`.
6. Wire a lightweight export path for the budget planner if you want XLSX or CSV later.
7. Continue into real integration work only after the approval boundary is ready.

## Commands

```powershell
.\.venv\Scripts\python.exe round-table\build_pages.py
.\.venv\Scripts\python.exe -m compileall app\app
```

## Notes

- `files.zip` has already been imported and removed from the workspace.
- The current Round Table site is the Codex version of the imported council, not the raw archive.
