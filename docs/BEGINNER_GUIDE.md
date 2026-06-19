# Beginner Guide: What N.E.X.U.S Is

This guide explains the project in normal language.

## The Simple Version

N.E.X.U.S is the beginning of your personal operating system.

It is not only a chatbot. It is meant to become a command center that can coordinate different agents, understand your daily priorities, check useful information, remember what happened, and recommend what to do next.

One of the agents inside N.E.X.U.S can be a personal assistant, but N.E.X.U.S itself is bigger than that. N.E.X.U.S is the operator over the full system.

Tagline:

```text
Everything Connects Here.
```

## Why We Are Building It In Layers

The final version you want has many pieces:

- A professional command dashboard.
- Multiple specialized agents.
- Real information from your calendar, email, notes, tasks, and manual entries.
- Memory.
- Safety controls.
- Voice input.
- Spoken responses.
- Approval flows.
- Self-learning and self-improvement.

Trying to build everything at once would make the project confusing and fragile.

So the first goal is the core loop:

```text
Ask -> Route -> Analyze -> Answer -> Remember
```

Once that works well, voice and automation can sit on top of it.

## What We Have Now

The current MVP can:

- Open a dashboard in the browser.
- Accept a question or command.
- Show mock operational stats.
- Route the request through a simple N.E.X.U.S orchestrator.
- Show agent activity.
- Suggest next steps.
- Save recent runs in memory.

Right now, the data is still mock data. That means it is fake but shaped like real data so the system can be built safely before connecting private accounts.

## Main Pieces

### Dashboard

The dashboard is the face of N.E.X.U.S.

It shows:

- Command input.
- Today-style metrics.
- A trend chart.
- N.E.X.U.S response.
- Agent activity.
- Suggestions.
- Recent memory.

### Backend

The backend is the engine running behind the dashboard.

It receives requests from the dashboard and sends back answers, metrics, agent activity, and memory.

### N.E.X.U.S Operator

N.E.X.U.S is the overseer of the whole system.

It should eventually decide:

- Which agent should help.
- What information is needed.
- What needs approval.
- What answer should be shown to you.
- What should be remembered.

### Specialist Agents

The agent roster is:

- Architect: strategy and planning.
- Engineer: coding and technical build work.
- Seeker: research.
- Analyst: data analysis.
- Sentinel: safety and protection.
- Link: API and integrations.
- Keeper: storage, database, and memory.
- Echo: conversation and user-facing communication.
- Pilot: task tracking and follow-up.

Only N.E.X.U.S should give the final advice after weighing what the other agents found.

## Wake Phrase Direction

Primary:

```text
Nexus, come online.
```

Sub phrases:

```text
Nexus, status.
Nexus, lock in.
Nexus, stand by.
```

These phrases imply that you are the owner and N.E.X.U.S is responding to your command.

## Safety Direction

N.E.X.U.S should never do sensitive things without approval.

Examples:

- Delete files.
- Spend money.
- Contact people.
- Send emails or messages.
- Expose private information.
- Connect bank accounts.
- Make major system-wide changes.

Lower-risk helpful changes can be allowed, but N.E.X.U.S should tell you what changed and keep it reversible.

## Best Next Step

The best next step is not voice yet.

The best next step is structure:

```text
Define tasks, agents, logs, approvals, and memory clearly.
```

After that, connect the first real data source. Calendar, Gmail, Notes, Tasks, and Reminders are the best first choices because they contain useful truth about your day without jumping immediately into high-risk financial integrations.
