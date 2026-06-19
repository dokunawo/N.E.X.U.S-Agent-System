# N.E.X.U.S Dashboard MVP

A local N.E.X.U.S operating system dashboard scaffold.

This v0 gives you the core shape of the system:

- FastAPI backend
- Browser dashboard
- N.E.X.U.S orchestrator
- Specialized mock agents
- Mock app analytics
- SQLite memory log
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
- `GET /api/memory` - recent memory log
- `DELETE /api/memory` - clear memory log

## Example Goal

```text
How is my app doing today, and what should we do next?
```

## Next Build Steps

1. Replace mock analytics with real data integrations.
2. Add account/project connectors.
3. Add WebSocket streaming for live agent status.
4. Add OpenAI-powered summaries and planning.
5. Add speech-to-text and text-to-speech.
6. Add wake phrases: "Nexus, come online", "Nexus, status", "Nexus, lock in", and "Nexus, stand by".
7. Deploy the orchestrator in the cloud while keeping local execution sandboxed.
