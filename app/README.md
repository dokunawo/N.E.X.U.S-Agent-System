# N.E.X.U.S Dashboard MVP

A local N.E.X.U.S operating system dashboard scaffold.

This v0 gives you the core shape of the system:

- FastAPI backend
- Browser dashboard
- N.E.X.U.S orchestrator
- Specialized mock agents
- Mock app analytics
- SQLite task, agent, log, memory, approval, and source schema
- Optional OpenAI-powered narrative when `OPENAI_API_KEY` is set

The app runs without an API key. It uses deterministic mock data until you connect real services.

## Project Layout

```text
nexus-dashboard-mvp/
  app/
    main.py
    services/
      analytics.py
      memory.py
      openai_bridge.py
      orchestrator.py
  static/
    index.html
    styles.css
    app.js
  .env.example
  requirements.txt
  run.ps1
```

## Run Locally

From this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

From the project root, you can also use the N.E.X.U.S launcher:

```powershell
powershell -ExecutionPolicy Bypass -File .\Start-NEXUS.ps1
```

To start it in the background:

```powershell
powershell -ExecutionPolicy Bypass -File .\Start-NEXUS.ps1 -Background
```

The background launcher writes the server PID and logs into the `data` folder.

If you are using the bundled Codex Python runtime on this machine, the executable is:

```powershell
C:\Users\dokun\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
```

## Optional OpenAI Setup

Copy `.env.example` to `.env`, then set:

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.5
```

Without `OPENAI_API_KEY`, the app keeps working in mock mode.

## Main Endpoints

- `GET /` - dashboard UI
- `GET /api/health` - service status
- `GET /api/dashboard` - initial analytics and memory snapshot
- `POST /api/run` - run the orchestrator for a goal
- `GET /council/` - The Round Table council UI with separate agent pages
- `GET /api/schema` - current operating schema values
- `GET /api/agents` - official agent roster
- `GET /api/tasks` - recent task records
- `GET /api/logs` - recent agent activity logs
- `GET /api/memory` - recent memory log
- `GET /api/memory/entries` - structured memory entries
- `GET /api/approvals` - pending approval requests
- `GET /api/learning` - local learning sources and active insights
- `GET /api/finance` - Steward finance snapshot
- `POST /api/finance/expenses` - add a manual expense
- `POST /api/finance/budget-categories` - set a manual budget category
- `POST /api/finance/savings-goals` - add a savings goal
- `POST /api/finance/investments` - add a manual investment position
- `POST /api/approvals/{id}/approve` - mark an approval request as approved
- `POST /api/approvals/{id}/reject` - mark an approval request as rejected
- `DELETE /api/memory` - clear memory log

## Example Goal

```text
How is my app doing today, and what should we do next?
```

## Next Build Steps

1. Add dashboard views for tasks, approvals, and memory entries.
2. Add approval actions so Daniel can approve or reject pending requests.
3. Connect Calendar in read-only mode first.
4. Connect Gmail in read-only mode after Calendar works.
5. Add WebSocket streaming for live agent status.
6. Add OpenAI-powered planning on top of the stored task and memory history.
7. Add speech-to-text, text-to-speech, and wake phrases after the data loop is reliable.
