# R.A.M.B.O. Backbone Schema

Created: 2026-06-19

This is the first real operating backbone for R.A.M.B.O.

The purpose is simple:

```text
Every request should become a task.
Every agent action should become a log.
Every useful result should become memory.
Every sensitive action should create an approval request.
```

## Tables

### agents

The official R.A.M.B.O. agent roster.

Each agent has:

- Name.
- Role.
- Purpose.
- Access scope.
- Risk boundary.
- Default status.

This keeps agents from becoming vague. Each one has a job and a limit.

### tasks

The main record for work R.A.M.B.O. is handling.

Each task has:

- Goal.
- Status.
- Priority.
- Risk level.
- Owner agent.
- Summary.

This gives Pilot and R.A.M.B.O. a real task history to work from.

### agent_logs

The activity trail for agents.

Each log has:

- Task link.
- Agent.
- Status.
- Message.
- Risk level.

This is what later powers live agent activity, audit history, and "what happened?" answers.

### memory_entries

The useful memory R.A.M.B.O. should keep.

Each memory entry has:

- Type.
- Title.
- Content.
- Importance.
- Source.
- Tags.

This is separate from raw logs because memory should be useful, not just noisy.

### approval_requests

The safety gate for sensitive actions.

Each approval request has:

- Requested action.
- Reason.
- Risk level.
- Approval type.
- Status.
- Requesting agent.

Sentinel creates these when a request touches deletion, spending, messages, account connections, private information, or other high-risk boundaries.

### data_sources

The planned and active source list.

Current active sources:

- Manual entry.
- Mock analytics.

Planned sources:

- Calendar.
- Gmail.
- Notes.
- Tasks.

This lets Link connect real data later without guessing where it belongs.

### learning_sources

The allowed places R.A.M.B.O. can learn from.

Current active sources:

- Local goals and prompts.
- Approval decisions.

Approval-gated future sources:

- Connected plugins.
- Personal integrations.

This keeps learning curious but controlled.

### learning_insights

The current things R.A.M.B.O. believes it is learning about Daniel.

Each insight has:

- Category.
- Title.
- Detail.
- Confidence.
- Source.
- Evidence.
- Privacy level.

These are not secret rules. They are inspectable and can be corrected later.

### budget_categories

Steward's budget structure.

Each category has:

- Name.
- Type.
- Monthly limit.
- Spent amount.
- Status.

### expenses

Manual expense entries for Steward.

No bank account connection is required.

### savings_goals

Manual savings targets.

### investment_positions

Manual investment awareness records.

Steward can track and summarize these. It cannot trade or move money.

## API Endpoints

```text
GET /api/schema
GET /api/agents
GET /api/tasks
GET /api/logs
GET /api/memory
GET /api/memory/entries
GET /api/approvals
GET /api/learning
GET /api/finance
POST /api/finance/expenses
POST /api/finance/budget-categories
POST /api/finance/savings-goals
POST /api/finance/investments
POST /api/approvals/{id}/approve
POST /api/approvals/{id}/reject
```

The existing dashboard endpoints still work:

```text
GET /api/health
GET /api/dashboard
POST /api/run
```

## Current Behavior

When `POST /api/run` receives a goal:

1. R.A.M.B.O. checks the risk level.
2. The agent roster runs in mock mode.
3. A task record is created.
4. Agent log rows are created.
5. A memory entry is saved.
6. If risk is medium or higher, Sentinel creates a pending approval request.
7. Daniel can approve or reject the approval request from the dashboard.

No external account is connected yet.

No email, message, purchase, file deletion, or sensitive action is performed automatically.
