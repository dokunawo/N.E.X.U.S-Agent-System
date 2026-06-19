# The Round Table — README

Static, dependency-free build of N.E.X.U.S's council UI. Pure HTML/CSS/JS —
no build step, no npm, no framework. Matches AGENTS.md's own technical
default: "Frontend: simple browser dashboard first."

## What's in here

```
round-table/
  index.html              N.E.X.U.S home — landscape council dashboard
  round-table.html        Council hub — radial Round Table + 3D core
  agents/<id>.html         11 pages: nexus, architect, engineer, seeker,
                            analyst, sentinel, steward, link, keeper, echo, pilot
  system/approvals.html    Sentinel's cross-agent approval queue
  system/learning.html     N.E.X.U.S's own learning log
  assets/style.css         Full design system (HUD theme, all components)
  assets/app.js            Live clock + stat counters + home node bubbles
  assets/core3d.js         Three.js core animation (every page with a core-canvas)
  assets/budget.js         Steward's budget planner logic (steward.html only)
  downloads/steward-budget-planner.html
                           Standalone downloadable Steward planner
  data/agents.json         Single source of truth — descriptions, journal
                            entries, stats for every agent and system page
  build_pages.py           Regenerates every HTML page from agents.json
```

## How to open it right now

Just double-click `index.html`. No server needed — every page link, every
stylesheet, and every script works over `file://` because nothing does a
runtime `fetch()` of local JSON (see "Why no fetch()" below).

## How to update content (the right way)

Don't hand-edit the HTML files — they're generated. Edit `data/agents.json`
(add a journal entry, change a description, adjust a stat) then run:

```
python3 build_pages.py
```

That regenerates the full council set in under a second, consistently.

## Wiring this into N.E.X.U.S itself

Two honest options, ranked:

1. **Serve it as static files from FastAPI** (recommended). Mount this
   folder with `app.mount("/council", StaticFiles(directory="round-table"),
   name="council")` and link to it from the existing dashboard. Zero
   rewrite required.
2. **Convert to Jinja2 templates** once agent data needs to come from
   SQLite instead of `agents.json`. At that point `data/agents.json`
   becomes the seed data, and `build_pages.py`'s logic becomes your
   route handler instead of a static generator. Don't do this until
   Keeper's agent-journal table actually exists — converting early
   just adds a template engine for no real benefit yet.

## Why no `localStorage` in the budget planner

Claude's artifact preview environment doesn't support `localStorage`, so
the planner currently holds state in memory only (resets on reload). This
isn't just a tooling workaround — it's also the more correct call
architecturally: per AGENTS.md, memory should live in SQLite, not the
browser, and anything beyond locally-typed numbers should pass through
Sentinel's approval path. The real fix is the `POST /api/steward/budget`
endpoint flagged in Engineer's queue and `budget.js`'s TODO comment, not
`localStorage`.

## Why no runtime `fetch()` of agents.json

Opening HTML files directly via `file://` blocks `fetch()`/`XHR` calls to
sibling local files in most browsers (CORS). So instead of agent pages
fetching `agents.json` at runtime, `build_pages.py` bakes each agent's
content into its own HTML file at *build* time. You still get one source
of truth — you just rebuild instead of re-fetch.

## Known placeholders (intentionally not invented data)

- Every journal entry is sample data shaped to match the agent's role —
  swap for real run history once Keeper's journal table is live.
- Agent identity now uses tailored avatar visuals instead of plain text badges.
- The home page globe has clickable nodes and hover bubbles for each specialist.
- Steward's savings goal, investment, and debt rows are each one labeled
  "(example — edit me)" — replace with your real numbers.
- Checking ($157) and Savings ($210) balances are seeded from the
  "Configure" section of your actual Google Sheet, not invented.
- Approvals queue shows "None pending" — this is correct, not broken;
  there's no live Sentinel backend wired in yet.
