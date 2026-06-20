# R.A.M.B.O. - Start Here

This folder is the home base for your R.A.M.B.O. operating system project.

You do not need to be a developer to understand the basic idea:

- The dashboard is the face.
- The backend is the engine.
- R.A.M.B.O. is the overall operator.
- The smaller Brains are specialists with specific jobs.
- The memory database is the notebook.
- Future integrations are the apps and services R.A.M.B.O. will learn from.

Tagline:

```text
Autonomy. Precision. Execution.
```

## Current Status

You have a working MVP.

It can:

- Open a dashboard in the browser.
- Accept a question like "How is my app doing today?"
- Show mock business/app stats.
- Run a simple R.A.M.B.O. orchestrator.
- Show what each specialist Brain did.
- Suggest next steps.
- Save recent runs in memory.
- Run without an OpenAI API key.
- Switch to OpenAI-powered summaries later when `OPENAI_API_KEY` is added.

## How To Start It

Run this from PowerShell:

```powershell
C:\Users\dokun\Documents\Codex\Jarvis-Agent\Start-RAMBO.ps1
```

Then open:

```text
http://127.0.0.1:8000
```

If port 8000 is already being used, the script will try port 8001.

## Main Folder Map

```text
Jarvis-Agent/
  START_HERE.md          You are here.
  AGENTS.md              Instructions Codex should follow in this project.
  Start-RAMBO.ps1        Starts the local dashboard server.
  Start-Jarvis.ps1       Older starter script kept for compatibility.
  app/                   The current working MVP.
  docs/                  Beginner explanations and roadmap.
  data/                  Future real data files or exports.
  integrations/          Future connectors to apps and APIs.
  voice/                 Future wake-word, speech-to-text, and voice output.
  assets/                Future images, icons, screenshots, and UI media.
  .venv/                 Local Python environment for this project.
```

## Best Way To Use Codex With This Project

Yes, you should open this as a project in the Codex app:

```text
C:\Users\dokun\Documents\Codex\Jarvis-Agent
```

That gives Codex a stable project root. It can read the same files, follow the same project instructions, and keep future work organized.

For normal work, use Local mode. Use Worktree mode later when you want Codex to experiment in the background without touching the main project folder.

## Recommended Next Step

Before adding voice, connect one real data source.

The reason is simple: a talking R.A.M.B.O. is cool, but a useful R.A.M.B.O. needs real information first.

Boot phrase:

```text
R.A.M.B.O. online. Systems synchronized. Standing by for your command.
```

Good first integrations:

- Calendar
- Gmail
- Notes
- Tasks or reminders
- A simple manual `data/manual_context.json` file

I would wait on bank integrations until the permission system and approval flow are much stronger.
