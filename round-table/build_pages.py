#!/usr/bin/env python3
"""
build_pages.py — generates every page of The Round Table from data/agents.json.

Run this any time agents.json changes (new journal entry, new Brain, edited
description) instead of hand-editing HTML. Requires nothing but Python 3
(no pip installs).

Usage:  python3 build_pages.py
"""
import json
import math
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT, "data", "agents.json")

GOOGLE_FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&'
    'family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" '
    'rel="stylesheet">'
)
THREEJS_CDN = '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'


def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def esc(s):
    if s is None:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def nav_link(href, label, color, active, perm=None, dot=True, icon_text=None, icon_html=None):
    cls = "nav-item active" if active else "nav-item"
    style = f' style="--node-color:{color}"' if color else ""
    perm_html = f'<span class="nav-perm">{esc(perm)}</span>' if perm else ""
    dot_html = '<span class="nav-dot"></span>' if dot else ""
    if icon_html is None and icon_text:
        icon_html = f'<span class="nav-icon">{esc(icon_text)}</span>'
    return f'<a class="{cls}" href="{href}"{style}>{dot_html}{icon_html or ""}<span>{esc(label)}</span>{perm_html}</a>'


def avatar_class(agent_id):
    return f"avatar-{agent_id}"


def render_avatar(agent, size="md"):
    return f"""
    <div class="avatar {avatar_class(agent['id'])} avatar-{size}" aria-hidden="true">
      <span class="avatar-halo"></span>
      <span class="avatar-head"></span>
      <span class="avatar-body"></span>
      <span class="avatar-accent"></span>
      <span class="avatar-glyph">{esc(agent['glyph'])}</span>
    </div>"""


def current_work(agent):
    journal = agent.get("journal", {})
    in_progress = journal.get("inProgress") or []
    if in_progress:
        item = in_progress[0]
        return item.get("title") or item.get("note") or "Active work in progress"
    queued = journal.get("queued") or []
    if queued:
        item = queued[0]
        return item.get("title") or item.get("note") or "Queued for next pass"
    return "Standing by for the next request"


def render_agent_scene(agent):
    bubbles = []
    labels = [
        ("Tasks completed", str(agent["stats"]["tasksCompleted"])),
        ("Tasks queued", str(agent["stats"]["tasksQueued"])),
        ("Success rate", f"{agent['stats']['successRate']}%"),
    ]
    angles = [-55, 5, 65]
    for (label, value), angle in zip(labels, angles):
        bubbles.append(
            f"""<div class="agent-orbit-bubble" style="--orbit-angle:{angle}deg;">
              <div>
                <span>{esc(label)}</span>
                <strong>{esc(value)}</strong>
              </div>
            </div>"""
        )
    return f"""
    <section class="agent-scene">
      <div class="agent-node-stage">
        <canvas id="core-canvas" class="core-canvas"></canvas>
        <div class="ring-static"></div>
        <div class="ring-static r2"></div>
        <div class="agent-scene-core">{render_avatar(agent, "lg")}</div>
        <div class="agent-scene-orbits">{''.join(bubbles)}</div>
      </div>
    </section>"""


def render_system_scene(page):
    bubbles = []
    angles = [-70, -18, 28, 76]
    for item, angle in zip(system_hub_items(page), angles):
        bubbles.append(
            f"""<div class="agent-orbit-bubble system-orbit-bubble" style="--orbit-angle:{angle}deg;">
              <div>
                <span>{esc(item['label'])}</span>
                <strong>{esc(item['value'])}</strong>
              </div>
            </div>"""
        )
    return f"""
    <section class="agent-scene system-scene">
      <div class="agent-node-stage system-node-stage">
        <canvas id="core-canvas" class="core-canvas"></canvas>
        <div class="ring-static"></div>
        <div class="ring-static r2"></div>
        <div class="agent-scene-core system-scene-core">
          {render_avatar(page, "lg")}
          <div class="system-core-label">
            <strong>{esc(page["name"])}</strong>
            <span>{esc(page["title"])}</span>
          </div>
        </div>
        <div class="agent-scene-orbits system-scene-orbits">{''.join(bubbles)}</div>
      </div>
    </section>"""


def render_sidebar(data, active_id, base):
    agents = sorted(data["agents"], key=lambda a: a["order"])
    specialists = [a for a in agents if a["id"] != "rambo"]
    sys_pages = data["systemPages"]

    items = []
    items.append(nav_link(f"{base}index.html", "R.A.M.B.O.", "#FF2E2E", active_id in ("home", "rambo"), dot=False, icon_text="RB"))
    items.append('<div class="nav-group-label">COUNCIL</div>')
    items.append(nav_link(f"{base}round-table.html", "Round Table", "#FF7A00", active_id == "round-table", dot=False, icon_text="RT"))
    items.append('<div class="nav-group-label">BRAINS</div>')
    for a in specialists:
        items.append(nav_link(f"{base}agents/{a['id']}.html", a["name"], a["color"], active_id == a["id"], a["permissionTier"], icon_html=render_avatar(a, "nav")))
    items.append('<div class="nav-group-label">SYSTEM</div>')
    for s in sys_pages:
        items.append(nav_link(f"{base}system/{s['id']}.html", s["name"], s["color"], active_id == s["id"], icon_html=render_avatar(s, "nav")))

    return f"""<aside class="sidebar">
  <div class="brand">
    <div class="brand-mark">R</div>
    <div class="brand-text"><div class="t1">R.A.M.B.O.</div></div>
  </div>
  <nav>{''.join(items)}</nav>
</aside>"""


def render_topbar(crumb, page_title):
    crumb_html = ""
    if crumb and page_title:
        crumb_html = f'<div class="crumb">{esc(crumb)} / <b>{esc(page_title)}</b></div>'
    elif page_title:
        crumb_html = f'<div class="crumb"><b>{esc(page_title)}</b></div>'
    return f"""<div class="topbar">
    {crumb_html}
    <div style="display:flex;align-items:center;">
      <div class="status-pill"><span class="dot"></span>R.A.M.B.O. ONLINE</div>
      <div class="clock" id="sys-clock">--:--:--</div>
    </div>
  </div>"""


def render_footer(build_date):
    return f"""<footer class="foot">
    <span>R.A.M.B.O. &mdash; Autonomy. Precision. Execution.</span>
    <span>Build {esc(build_date)}</span>
  </footer>"""


def page_shell(title, base, body, extra_head="", extra_scripts=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
{GOOGLE_FONTS}
<link rel="stylesheet" href="{base}assets/style.css">
{extra_head}
</head>
<body>
<div class="app-shell">
{body}
</div>
<script src="{base}assets/app.js"></script>
{extra_scripts}
</body>
</html>"""


def render_orb_panel(title, subtitle, items, size_class="medium", list_class="orb-list"):
    satellite_count = max(len(items), 1)
    satellites = []
    for idx, item in enumerate(items):
        angle = -120 + (240 / max(satellite_count - 1, 1)) * idx if satellite_count > 1 else -90
        satellites.append(
            f"""<div class="orb-satellite" style="--sat-angle:{angle:.2f};--sat-color:var(--node-color, var(--cyan))">
              <span class="orb-satellite-dot"></span>
              <span class="orb-satellite-copy">
                <b>{esc(item['label'])}</b>
                <em>{esc(item['value'])}</em>
              </span>
            </div>"""
        )
    item_rows = "".join(
        f"""<div class="orb-item">
        <span class="orb-label">{esc(item['label'])}</span>
        <span class="orb-value">{esc(item['value'])}</span>
      </div>"""
        for item in items
    )
    return f"""<section class="orb-panel {size_class}">
      <div class="orb-panel-head">
        <div class="orb-panel-title">{esc(title)}</div>
        <div class="orb-panel-subtitle">{esc(subtitle)}</div>
      </div>
      <div class="orb-stage">
        <canvas id="core-canvas" class="core-canvas"></canvas>
        <div class="orb-satellites">{''.join(satellites)}</div>
        <div class="ring-static"></div>
        <div class="ring-static r2"></div>
        <div class="table-center"><div class="label mono">R.A.M.B.O.</div></div>
      </div>
      <div class="{list_class}">
        {item_rows}
      </div>
    </section>"""


def agent_hub_items(agent):
    stats = agent["stats"]
    return [
        {"label": "Role", "value": agent["title"]},
        {"label": "Tasks", "value": f"{stats['tasksCompleted']} complete"},
        {"label": "Queue", "value": f"{stats['tasksQueued']} waiting"},
        {"label": "Success", "value": f"{stats['successRate']}%"},
    ]


def system_hub_items(page):
    if page["id"] == "approvals":
        return [
            {"label": "Queue", "value": "Pending approval checks"},
            {"label": "Owner", "value": "Sentinel"},
            {"label": "Risk", "value": "Money, messages, deletion"},
            {"label": "State", "value": "Ready"},
        ]
    return [
        {"label": "Source", "value": "Local learning log"},
        {"label": "Guardrail", "value": "Approval-gated plugins"},
        {"label": "Scope", "value": "Patterns, corrections, signals"},
        {"label": "State", "value": "Ready"},
    ]


def render_journal_column(title_cls, label, entries, empty_msg, live_key=None):
    live_attr = f' data-journal-column="{esc(live_key)}"' if live_key else ""
    if not entries:
        return f'<div class="journal-col {title_cls}"{live_attr}><h4>{label}</h4><div class="j-empty">{esc(empty_msg)}</div></div>'
    rows = []
    for e in entries:
        date_html = f'<div class="j-date">{esc(e["date"])}</div>' if e.get("date") else ""
        rows.append(f"""<div class="j-entry">{date_html}
      <div class="j-title">{esc(e["title"])}</div>
      <div class="j-note">{esc(e["note"])}</div>
    </div>""")
    return f'<div class="journal-col {title_cls}"{live_attr}><h4>{label}</h4>{"".join(rows)}</div>'


def render_agent_page(agent, data, out_dir):
    base = "../"
    j = agent["journal"]
    journal_html = f"""<div class="journal-cols" data-agent-journal="{agent["id"]}">
    {render_journal_column("completed", "COMPLETED", j.get("completed", []), "Nothing logged yet.", "completed")}
    {render_journal_column("inprogress", "IN PROGRESS", j.get("inProgress", []), "Nothing in motion right now.", "inProgress")}
    {render_journal_column("queued", "QUEUED", j.get("queued", []), "Queue is empty.", "queued")}
  </div>"""

    directives_html = "".join(f"<li>{esc(d)}</li>" for d in agent["directives"])
    stats = agent["stats"]

    budget_html = ""
    if agent["id"] == "steward":
        budget_html = render_budget_section() + """
    <div class="section fade-in">
      <div class="section-title">DOWNLOAD</div>
      <a class="download-link" href="../downloads/steward-budget-planner.html" download>Download Steward budget planner</a>
    </div>"""

    style = f'style="--node-color:{agent["color"]};--accent:{agent["color"]}"'

    body = f"""{render_sidebar(data, agent["id"], base)}
  <main class="main" {style}>
    {render_topbar("", agent["name"])}
    {render_agent_scene(agent)}

    <div class="page-head fade-in">
      {render_avatar(agent, "lg")}
      <div>
        <h1>{esc(agent["name"])}</h1>
        <div class="role">{esc(agent["title"])}</div>
        <div class="summary">{esc(agent["description"])}</div>
      </div>
      <div class="tier-badge">
        <div class="tier-label">PERMISSION TIER</div>
        <div class="tier-value tier-{esc(agent["permissionTier"])}">{esc(agent["permissionTier"]).upper()}</div>
      </div>
    </div>

    <div class="stat-row fade-in">
      <div class="stat-card"><div class="num" data-count="{stats["tasksCompleted"]}">0</div><div class="lbl">Tasks Completed</div></div>
      <div class="stat-card"><div class="num" data-count="{stats["tasksQueued"]}">0</div><div class="lbl">Tasks Queued</div></div>
      <div class="stat-card"><div class="num" data-count="{stats["successRate"]}" data-suffix="%">0</div><div class="lbl">Success Rate</div></div>
    </div>

    <div class="section fade-in">
      <div class="section-title">CORE DIRECTIVES</div>
      <ul class="directives">{directives_html}</ul>
    </div>

    <div class="section fade-in">
      <div class="section-title">MISSION JOURNAL</div>
      {journal_html}
    </div>

    {budget_html}

    {render_footer(data["meta"]["buildDate"])}
  </main>"""

    extra_scripts = f'{THREEJS_CDN}\n<script src="../assets/core3d.js"></script>'
    if agent["id"] == "steward":
        extra_scripts += '\n<script src="../assets/budget.js"></script>'
    html = page_shell(agent["name"], base, body, extra_scripts=extra_scripts)
    with open(os.path.join(out_dir, f'{agent["id"]}.html'), "w", encoding="utf-8") as f:
        f.write(html)


def render_budget_section():
    formulas = [
        ("Total Income", "Sum of every income row.", "=SUM(IncomeRange)"),
        ("Total Actual Expenses", "Sum of the Actual column across all categories.", "=SUM(ExpenseActualRange)"),
        ("Net Cash Flow", "Income minus actual expenses for the period.", "=TotalIncome-TotalExpenses"),
        ("Savings Rate", "Net cash flow as a percentage of income.", "=(TotalIncome-TotalExpenses)/TotalIncome"),
        ("Category Remaining", "Budgeted minus actual, per category row.", "=Budgeted-Actual"),
        ("% of Income (per category)", "Share of total income a single category consumed.", "=Actual/TotalIncome"),
        ("Cash Runway (months)", "Checking + savings balance divided by average monthly spend.", "=(Checking+Savings)/AvgMonthlyExpense"),
        ("Goal % Complete", "Amount saved so far over the goal target.", "=Current/Target"),
        ("Monthly Needed for Goal", "What's left to save, divided by months remaining to the target date.", "=(Target-Current)/MonthsRemaining"),
        ("Investment Future Value", "Compound growth of a balance plus monthly contributions.", "=FV(Rate/12, Months, -Contribution, -Balance)"),
        ("Debt Payoff Time (months)", "How long it takes to clear a balance at a fixed monthly payment.", "=NPER(APR/12, -MinPayment, Balance)"),
    ]
    formula_rows = "".join(
        f"""<div class="formula-row">
        <div><div class="fname">{esc(n)}</div><div class="fwhat">{esc(w)}</div></div>
        <div class="fexcel">{esc(x)}</div>
      </div>"""
        for n, w, x in formulas
    )

    return f"""<div id="budget-planner" class="section fade-in">
      <div class="section-title">STEWARD BUDGET PLANNER &mdash; MANUAL ENTRY</div>

      <div class="note-callout">
        <b>Manual entry only.</b> Nothing here connects to a real bank, card, or Notion account yet &mdash;
        by design, per Sentinel's permission rules. Numbers typed here save to local SQLite through
        R.A.M.B.O. so the planner survives reloads. Seeded balances below match the
        "Configure" section of your existing Google Sheet.
      </div>
      <div class="planner-save-status" id="budget-save-status">Loading Steward planner memory...</div>

      <div class="kpi-row">
        <div class="kpi-card"><div class="lbl">Total Income</div><div class="val neutral" id="kpi-income">$0.00</div></div>
        <div class="kpi-card"><div class="lbl">Total Expenses</div><div class="val neutral" id="kpi-expense">$0.00</div></div>
        <div class="kpi-card"><div class="lbl">Net Cash Flow</div><div class="val pos" id="kpi-net">$0.00</div></div>
        <div class="kpi-card"><div class="lbl">Savings Rate</div><div class="val neutral" id="kpi-rate">0%</div></div>
        <div class="kpi-card"><div class="lbl">Cash Runway</div><div class="val neutral" id="kpi-runway">0 mo</div></div>
      </div>

      <div class="section">
        <div class="section-title">INCOME</div>
        <div class="planner-table-wrap">
          <div class="planner-table-scroll" style="max-height:220px;">
            <table class="planner">
              <thead><tr><th>Source</th><th style="width:160px;">Monthly Amount</th><th style="width:40px;"></th></tr></thead>
              <tbody id="income-body"></tbody>
            </table>
          </div>
          <div class="planner-actions"><button class="btn" data-action="add-income">+ Add Income Source</button></div>
        </div>
      </div>

      <div class="section">
        <div class="section-title">EXPENSES &mdash; BUDGET VS. ACTUAL</div>
        <div class="planner-table-wrap">
          <div class="planner-table-scroll">
            <table class="planner">
              <thead><tr><th>Category</th><th style="width:130px;">Budgeted</th><th style="width:130px;">Actual</th><th style="width:120px;">Remaining</th><th style="width:100px;">% of Income</th></tr></thead>
              <tbody id="expense-body"></tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-title">SAVINGS GOALS</div>
        <div class="goal-grid" id="goals-grid"></div>
        <div class="planner-actions" style="border:none;background:none;padding-top:10px;"><button class="btn" data-action="add-goal">+ Add Savings Goal</button></div>
      </div>

      <div class="section">
        <div class="section-title">INVESTMENTS &amp; PROJECTED GROWTH</div>
        <div class="invest-grid" id="invest-grid"></div>
        <div class="planner-actions" style="border:none;background:none;padding-top:10px;"><button class="btn" data-action="add-investment">+ Add Investment</button></div>
      </div>

      <div class="section">
        <div class="section-title">DEBT PAYOFF</div>
        <div class="planner-table-wrap">
          <table class="planner">
            <thead><tr><th>Debt</th><th style="width:120px;">Balance</th><th style="width:90px;">APR %</th><th style="width:120px;">Min Payment</th><th style="width:120px;">Payoff Time</th></tr></thead>
            <tbody id="debt-body"></tbody>
          </table>
          <div class="planner-actions"><button class="btn" data-action="add-debt">+ Add Debt</button></div>
        </div>
      </div>

      <details class="formula-ref">
        <summary>&#9656; FORMULA REFERENCE &mdash; live calc next to its Excel/Sheets equivalent</summary>
        <div class="formula-ref-body">{formula_rows}</div>
      </details>
    </div>"""


def render_budget_download_page(data, out_path):
    steward = next(a for a in data["agents"] if a["id"] == "steward")
    body = f"""{render_sidebar(data, "steward", "../")}
  <main class="main" style="--node-color:#39FF88;--accent:#39FF88">
    {render_topbar("", "Steward Budget Planner")}
    <div class="page-head fade-in">
      {render_avatar(steward, "lg")}
      <div>
        <h1>Steward Budget Planner</h1>
        <div class="role">Downloadable manual-entry budget workspace</div>
        <div class="summary">This standalone HTML file mirrors the Steward budgeting tools so you can save or move it as a single artifact.</div>
      </div>
    </div>
    {render_budget_section()}
    {render_footer(data["meta"]["buildDate"])}
  </main>"""
    html = page_shell("Steward Budget Planner", "../", body, extra_scripts='<script src="../assets/budget.js"></script>')
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)


def render_system_page(page, data, out_dir):
    base = "../"
    style = f'style="--node-color:{page["color"]};--accent:{page["color"]}"'
    system_node_html = render_system_scene(page)

    if page["id"] == "approvals":
        rows = "".join(f"""<div class="j-entry"><div class="j-title">{esc(q["title"])}</div><div class="j-note">{esc(q["note"])}</div></div>""" for q in page["queue"])
        decisions = "".join(f"""<div class="j-entry"><div class="j-date">{esc(d["date"])}</div><div class="j-title">{esc(d["title"])}</div><div class="j-note">{esc(d["decision"])}</div></div>""" for d in page["recentDecisions"])
        content = f"""<div class="section fade-in"><div class="section-title">PENDING QUEUE</div><div class="journal-col">{rows}</div></div>
    <div class="section fade-in"><div class="section-title">RECENT DECISIONS</div><div class="journal-col">{decisions}</div></div>"""
    else:
        entries = "".join(f"""<div class="j-entry"><div class="j-date">{esc(e["date"])}</div><div class="j-title">{esc(e["title"])}</div><div class="j-note">{esc(e["note"])}</div></div>""" for e in page["entries"])
        content = f"""<div class="section fade-in"><div class="section-title">RECENT LEARNINGS</div><div class="journal-col">{entries}</div></div>"""

    body = f"""{render_sidebar(data, page["id"], base)}
  <main class="main" {style}>
    {render_topbar("THE ROUND TABLE", page["name"])}
    {system_node_html}
    <div class="page-head fade-in">
      {render_avatar(page, "lg")}
      <div>
        <h1>{esc(page["title"])}</h1>
        <div class="summary">{esc(page["description"])}</div>
      </div>
    </div>
    {content}
    {render_footer(data["meta"]["buildDate"])}
  </main>"""

    html = page_shell(page["name"], base, body, extra_scripts=f'{THREEJS_CDN}\n<script src="../assets/core3d.js"></script>')
    with open(os.path.join(out_dir, f'{page["id"]}.html'), "w", encoding="utf-8") as f:
        f.write(html)


def render_agent_card(agent):
    return f"""<a class="agent-card" href="agents/{agent['id']}.html" style="--node-color:{agent['color']}">
      <div class="ac-top">
        {render_avatar(agent, "sm")}
        <div>
          <h3>{esc(agent['name'])}</h3>
          <div class="ac-title">{esc(agent['title'])}</div>
        </div>
      </div>
      <div class="ac-stats">
        <div><span>DONE</span><strong>{agent['stats']['tasksCompleted']}</strong></div>
        <div><span>QUEUE</span><strong>{agent['stats']['tasksQueued']}</strong></div>
        <div><span>SCORE</span><strong>{agent['stats']['successRate']}%</strong></div>
      </div>
      <div class="ac-bar"><span style="width:{agent['stats']['successRate']}%"></span></div>
      <p>{esc(agent['summary'])}</p>
    </a>"""


def render_home_page(data, out_path):
    agents = sorted(data["agents"], key=lambda a: a["order"])
    center_agent = next(a for a in agents if a["id"] == "rambo")
    specialist_agents = [a for a in agents if a["id"] != "rambo"]
    center_stats = center_agent["stats"]
    center_journal = center_agent["journal"]
    center_directives = "".join(f"<li>{esc(d)}</li>" for d in center_agent["directives"])
    center_journal_html = f"""<div class="journal-cols compact-journal" data-agent-journal="{center_agent["id"]}">
    {render_journal_column("completed", "RECENTLY COMPLETED", center_journal.get("completed", []), "Nothing logged yet.", "completed")}
    {render_journal_column("inprogress", "IN PROGRESS", center_journal.get("inProgress", []), "Nothing in motion right now.", "inProgress")}
    {render_journal_column("queued", "QUEUED", center_journal.get("queued", []), "Queue is empty.", "queued")}
  </div>"""
    agent_rows = "".join(
        f"""<tr>
        <td><span class="table-swatch" style="background:{esc(agent['color'])}"></span>{esc(agent['name'])}</td>
        <td>{agent['stats']['tasksCompleted']}</td>
        <td>{agent['stats']['tasksQueued']}</td>
        <td><div class="bar tiny"><span style="width:{agent['stats']['successRate']}%"></span></div></td>
        <td>{agent['stats']['successRate']}%</td>
      </tr>"""
        for agent in agents
    )
    node_lines = []
    node_bits = []
    node_count = len(specialist_agents)
    radius = 39
    for i, agent in enumerate(specialist_agents):
        angle = -96 + (360 / node_count) * i
        rad = math.radians(angle)
        x = 50 + radius * math.cos(rad)
        y = 50 + radius * math.sin(rad)
        node_lines.append(
            f'<line x1="50" y1="50" x2="{x:.2f}" y2="{y:.2f}" class="home-link" style="--node-color:{agent["color"]}" />'
        )
        work = current_work(agent)
        bubble = f"""
          <div class="node-bubble">
            {render_avatar(agent, "sm")}
            <div class="node-bubble-copy">
              <strong>{esc(agent['name'])}</strong>
              <span>{esc(agent['title'])}</span>
              <p>{esc(agent['summary'])}</p>
              <small>Working on: {esc(work)}</small>
            </div>
            <a class="node-bubble-link" href="agents/{agent['id']}.html">Open profile</a>
          </div>"""
        node_bits.append(
            f"""<div class="home-node" style="left:{x:.2f}%;top:{y:.2f}%;--node-color:{agent['color']};--node-angle:{angle:.2f}">
              <button type="button" class="home-node-toggle" data-node-toggle aria-label="Toggle {esc(agent['name'])}">
                <span class="home-node-dot">{render_avatar(agent, "nav")}</span>
              </button>
              <span class="home-node-label">{esc(agent['name'])}</span>
              {bubble}
            </div>"""
        )
    node_lines.append('<circle cx="50" cy="50" r="3.5" class="home-core-point"></circle>')

    body = f"""{render_sidebar(data, "home", "")}
  <main class="main rambo-home">
    {render_topbar("", "R.A.M.B.O.")}

    <section class="daily-briefing-panel fade-in" data-daily-briefing>
      <div class="daily-briefing-head">
        <div>
          <div class="section-title">DAILY BRIEFING</div>
          <h2 data-briefing-greeting>R.A.M.B.O. is coming online...</h2>
        </div>
        <div class="briefing-pill" data-briefing-clock>Detroit status pending</div>
      </div>
      <div class="briefing-grid">
        <div class="briefing-card"><span>Weather</span><strong data-briefing-weather>Loading Detroit weather...</strong></div>
        <div class="briefing-card"><span>Calendar</span><strong data-briefing-calendar>Calendar not checked yet</strong></div>
        <div class="briefing-card"><span>Today</span><strong data-briefing-focus>Preparing daily focus...</strong></div>
        <div class="briefing-card"><span>Approvals</span><strong data-briefing-approvals>Checking Sentinel queue...</strong></div>
      </div>
      <div class="briefing-body">
        <div>
          <div class="section-title small">BRAIN BRIEFING</div>
          <div class="briefing-agent-list" data-briefing-agents></div>
        </div>
        <div>
          <div class="section-title small">TODAY'S OPERATING LOOP</div>
          <div class="briefing-task-list" data-briefing-tasks></div>
        </div>
      </div>
    </section>

    <div class="home-banner fade-in">
      <div class="home-title">
        <h1><b>R.A.M.B.O.</b></h1>
      </div>
      <p>Responsive Autonomous Multi-Brain Operator. A tactical command surface that routes Sir's intent through specialized Brains, then synthesizes one clear answer.</p>
    </div>

    <div class="home-layout landscape">
      <section class="orb-panel large home-orb">
        <div class="orb-panel-head">
          <div class="orb-panel-title">R.A.M.B.O.</div>
          <div class="orb-panel-subtitle">Tactical command core</div>
        </div>
        <div class="table-stage home-stage">
          <canvas id="core-canvas" class="core-canvas"></canvas>
          <svg class="home-map" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
            {''.join(node_lines)}
          </svg>
          <div class="ring-static"></div>
          <div class="ring-static r2"></div>
          <div class="table-center">
            {render_avatar(center_agent, "lg")}
            <div class="label mono">R.A.M.B.O.</div>
          </div>
          <div class="home-node-wrap">{''.join(node_bits)}</div>
        </div>
      </section>

      <section class="panel-card council-panel">
        <div class="section-title">BRAIN DATA</div>
        <div class="council-overview">
          <div class="mini-stat"><span>Seats</span><strong>11</strong></div>
          <div class="mini-stat"><span>Mode</span><strong>{esc(data["meta"]["tagline"])}</strong></div>
          <div class="mini-stat"><span>Learning</span><strong>Local memory + approvals</strong></div>
          <div class="mini-stat"><span>Steward</span><strong>Manual finance tracking</strong></div>
        </div>
        <a class="home-cta" href="round-table.html">View Brain Roster</a>
        <table class="home-table">
          <thead>
            <tr><th>Brain</th><th>Done</th><th>Queued</th><th>Signal</th><th>Rate</th></tr>
          </thead>
          <tbody>{agent_rows}</tbody>
        </table>
      </section>

      <section class="workflow-panel fade-in">
        <div class="section-title">OPERATING LOOP</div>
        <div class="workflow-intro">
          Devchain-style routing translated into R.A.M.B.O.: each request moves through capture, planning, validation, build, review, and memory. Sensitive actions still stop at Sentinel.
        </div>
        <div class="workflow-steps" data-workflow-steps>
          <div class="workflow-step"><span>01</span><strong>R.A.M.B.O.</strong><p>Capture the request and define success.</p></div>
          <div class="workflow-step"><span>02</span><strong>Architect</strong><p>Plan the sequence and dependencies.</p></div>
          <div class="workflow-step"><span>03</span><strong>Seeker + Analyst</strong><p>Validate facts, data, and assumptions.</p></div>
          <div class="workflow-step"><span>04</span><strong>Engineer + Link</strong><p>Build the local capability or integration.</p></div>
          <div class="workflow-step"><span>05</span><strong>Sentinel</strong><p>Review risk and approval boundaries.</p></div>
          <div class="workflow-step"><span>06</span><strong>Keeper + Pilot</strong><p>Record the handoff and queue next work.</p></div>
        </div>
      </section>

      <section class="rambo-overseer-panel fade-in" style="--node-color:{center_agent["color"]};--accent:{center_agent["color"]}">
        <div class="section-title">R.A.M.B.O. COMMAND SEAT</div>
        <div class="rambo-overseer-grid">
          <div class="rambo-overseer-identity">
            {render_avatar(center_agent, "lg")}
            <div>
              <h2>{esc(center_agent["name"])}</h2>
              <div class="overseer-role">{esc(center_agent["title"])}</div>
              <p>{esc(center_agent["description"])}</p>
            </div>
          </div>
          <div class="rambo-overseer-stats">
            <div class="rambo-stat"><span>Tasks completed</span><strong>{center_stats["tasksCompleted"]}</strong></div>
            <div class="rambo-stat"><span>Tasks queued</span><strong>{center_stats["tasksQueued"]}</strong></div>
            <div class="rambo-stat"><span>Success rate</span><strong>{center_stats["successRate"]}%</strong></div>
            <div class="rambo-stat tier"><span>Permission tier</span><strong>Critical</strong></div>
          </div>
        </div>
        <div class="rambo-overseer-body">
          <div class="directive-block">
            <div class="section-title small">CORE DIRECTIVES</div>
            <ul class="directives">{center_directives}</ul>
          </div>
          <div class="home-journal-block">
            <div class="section-title small">MISSION JOURNAL</div>
            {center_journal_html}
          </div>
        </div>
      </section>
    </div>

    {render_footer(data["meta"]["buildDate"])}
  </main>"""

    html = page_shell("R.A.M.B.O.", "", body, extra_scripts=f'{THREEJS_CDN}\n<script src="assets/core3d.js"></script>')
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)


def render_round_table_page(data, out_path):
    base = ""
    agents = sorted(data["agents"], key=lambda a: a["order"])
    specialists = [a for a in agents if a["id"] != "rambo"]
    n = len(specialists)
    nodes_html = []
    radius = 42
    for i, a in enumerate(specialists):
        angle = -90 + (360 / n) * i
        rad = math.radians(angle)
        x = 50 + radius * math.cos(rad)
        y = 50 + radius * math.sin(rad)
        nodes_html.append(
            f'<div class="node node-orbit" style="left:{x:.2f}%;top:{y:.2f}%;--node-color:{a["color"]};--orbit-delay:{i * 0.55:.2f}s;--orbit-radius:{28 + (i % 3) * 6}px">'
            f'{render_avatar(a, "sm")}<div class="node-label">{esc(a["name"])}</div></div>'
        )

    cards_html = "".join(render_agent_card(a) for a in agents)

    body = f"""{render_sidebar(data, "round-table", base)}
  <main class="main">
    {render_topbar("", "Round Table")}

    <div class="hero">
      <div class="hero-head">
        <div class="eyebrow">COUNCIL / ROUND TABLE</div>
        <h1>ROUND TABLE</h1>
        <p>One operator, ten specialized Brains. The Round Table shows who is active, what each Brain owns, and how the tactical core keeps the whole system synchronized.</p>
      </div>
      <div class="table-stage">
        <canvas id="core-canvas" class="core-canvas"></canvas>
        <div class="ring-static"></div>
        <div class="ring-static r2"></div>
        <div class="table-center">{render_avatar(next(a for a in agents if a["id"] == "rambo"), "lg")}<div class="label mono">R.A.M.B.O.</div></div>
        <div class="node-wrap">{''.join(nodes_html)}</div>
      </div>
    </div>

    <div class="section fade-in">
      <div class="section-title">BRAIN ROSTER</div>
      <div class="agent-grid">{cards_html}</div>
    </div>

    {render_footer(data["meta"]["buildDate"])}
  </main>"""

    html = page_shell("Round Table", base, body, extra_scripts=f'{THREEJS_CDN}\n<script src="assets/core3d.js"></script>')
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    data = load_data()
    agents_dir = os.path.join(ROOT, "agents")
    system_dir = os.path.join(ROOT, "system")
    downloads_dir = os.path.join(ROOT, "downloads")
    os.makedirs(agents_dir, exist_ok=True)
    os.makedirs(system_dir, exist_ok=True)
    os.makedirs(downloads_dir, exist_ok=True)

    for agent in data["agents"]:
        render_agent_page(agent, data, agents_dir)

    for page in data["systemPages"]:
        render_system_page(page, data, system_dir)

    render_home_page(data, os.path.join(ROOT, "index.html"))
    render_round_table_page(data, os.path.join(ROOT, "round-table.html"))
    render_budget_download_page(data, os.path.join(downloads_dir, "steward-budget-planner.html"))

    total = 2 + len(data["agents"]) + len(data["systemPages"]) + 1
    print(f"Built {total} pages.")


if __name__ == "__main__":
    main()
