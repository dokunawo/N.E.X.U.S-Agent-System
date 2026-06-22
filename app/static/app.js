const state = {
  analytics: null,
  operating: null,
  lastResult: null,
};

const elements = {
  mode: document.querySelector("#mode"),
  healthState: document.querySelector("#health-state"),
  healthDetail: document.querySelector("#health-detail"),
  metrics: document.querySelector("#metrics"),
  generatedAt: document.querySelector("#generated-at"),
  summary: document.querySelector("#summary"),
  agentEvents: document.querySelector("#agent-events"),
  approvalCount: document.querySelector("#approval-count"),
  approvalList: document.querySelector("#approval-list"),
  learningCount: document.querySelector("#learning-count"),
  learningList: document.querySelector("#learning-list"),
  financeMode: document.querySelector("#finance-mode"),
  financeSummary: document.querySelector("#finance-summary"),
  suggestions: document.querySelector("#suggestions"),
  memoryList: document.querySelector("#memory-list"),
  chart: document.querySelector("#trend-chart"),
  form: document.querySelector("#goal-form"),
  goal: document.querySelector("#goal"),
  refresh: document.querySelector("#refresh"),
  clearMemory: document.querySelector("#clear-memory"),
};

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}

function escapeHTML(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderMetrics(metrics) {
  elements.metrics.innerHTML = metrics
    .map(
      (metric) => `
        <article class="metric-card ${metric.tone}">
          <span>${metric.label}</span>
          <strong>${metric.value}</strong>
          <small>${metric.delta}</small>
        </article>
      `,
    )
    .join("");
}

function renderChart(series) {
  const canvas = elements.chart;
  const context = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  const padding = 34;
  const values = series.map((point) => point.active_users);
  const min = Math.min(...values) * 0.94;
  const max = Math.max(...values) * 1.04;
  const scaleX = (width - padding * 2) / (series.length - 1);
  const scaleY = (height - padding * 2) / (max - min);

  context.clearRect(0, 0, width, height);
  context.fillStyle = "#111318";
  context.fillRect(0, 0, width, height);

  context.strokeStyle = "rgba(128, 218, 230, 0.18)";
  context.lineWidth = 1;
  for (let row = 0; row < 4; row += 1) {
    const y = padding + row * ((height - padding * 2) / 3);
    context.beginPath();
    context.moveTo(padding, y);
    context.lineTo(width - padding, y);
    context.stroke();
  }

  const points = values.map((value, index) => ({
    x: padding + index * scaleX,
    y: height - padding - (value - min) * scaleY,
    value,
    label: series[index].label,
  }));

  context.strokeStyle = "#e8b15a";
  context.lineWidth = 4;
  context.beginPath();
  points.forEach((point, index) => {
    if (index === 0) {
      context.moveTo(point.x, point.y);
    } else {
      context.lineTo(point.x, point.y);
    }
  });
  context.stroke();

  points.forEach((point) => {
    context.fillStyle = "#ffd98a";
    context.beginPath();
    context.arc(point.x, point.y, 5, 0, Math.PI * 2);
    context.fill();

    context.fillStyle = "#d0d0d0";
    context.font = "700 15px Segoe UI, sans-serif";
    context.textAlign = "center";
    context.fillText(point.label, point.x, height - 8);
  });
}

function renderEvents(events = []) {
  elements.agentEvents.innerHTML = events
    .map(
      (event) => `
        <div class="event ${event.status}">
          <strong>${escapeHTML(event.agent)} - ${escapeHTML(event.status)}</strong>
          <p>${escapeHTML(event.message)}</p>
        </div>
      `,
    )
    .join("");
}

function renderSuggestions(suggestions = []) {
  elements.suggestions.innerHTML = suggestions
    .map((suggestion) => `<li>${escapeHTML(suggestion)}</li>`)
    .join("");
}

function renderApprovals(approvals = []) {
  const count = approvals.length;
  elements.approvalCount.textContent = `${count} pending`;

  if (!count) {
    elements.approvalList.innerHTML = `
      <div class="approval-empty">
        <strong>No pending approvals</strong>
        <p>Sentinel will hold sensitive actions here before anything external happens.</p>
      </div>
    `;
    return;
  }

  elements.approvalList.innerHTML = approvals
    .map(
      (approval) => `
        <article class="approval-item ${escapeHTML(approval.risk_level)}">
          <div>
            <span class="approval-meta">${escapeHTML(approval.risk_level)} risk - ${escapeHTML(approval.approval_type)}</span>
            <strong>${escapeHTML(approval.title)}</strong>
            <p>${escapeHTML(approval.requested_action)}</p>
            <small>${escapeHTML(approval.reason)}</small>
          </div>
          <div class="approval-actions">
            <button class="small-button approve-button" type="button" data-action="approve" data-approval-id="${approval.id}">Approve</button>
            <button class="small-button reject-button" type="button" data-action="reject" data-approval-id="${approval.id}">Reject</button>
          </div>
        </article>
      `,
    )
    .join("");
}

function formatMoney(value = 0) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function renderLearning(learning = {}) {
  const insights = learning.insights || [];
  elements.learningCount.textContent = `${insights.length} insights`;

  if (!insights.length) {
    elements.learningList.innerHTML = `
      <div class="insight-empty">
        <strong>No learning signals yet</strong>
        <p>R.A.M.B.O. will learn from local goals first. Connected plugin learning stays approval-gated.</p>
      </div>
    `;
    return;
  }

  elements.learningList.innerHTML = insights
    .slice(0, 5)
    .map(
      (insight) => `
        <article class="insight-item">
          <span>${escapeHTML(insight.category)} - ${Math.round(insight.confidence * 100)}%</span>
          <strong>${escapeHTML(insight.title)}</strong>
          <p>${escapeHTML(insight.detail)}</p>
        </article>
      `,
    )
    .join("");
}

function renderFinance(finance = {}) {
  const summary = finance.summary || {};
  elements.financeMode.textContent = summary.mode || "manual";

  elements.financeSummary.innerHTML = `
    <div class="finance-metrics">
      <div>
        <span>Budget</span>
        <strong>${formatMoney(summary.monthly_budget || 0)}</strong>
      </div>
      <div>
        <span>Spent</span>
        <strong>${formatMoney(summary.spent_this_month || 0)}</strong>
      </div>
      <div>
        <span>Savings</span>
        <strong>${formatMoney(summary.savings_current_total || 0)}</strong>
      </div>
      <div>
        <span>Invested</span>
        <strong>${formatMoney(summary.investment_value_total || 0)}</strong>
      </div>
    </div>
    <p>${escapeHTML(finance.guardrail || "Steward is running in manual mode.")}</p>
  `;
}

function renderOperating(operating = {}) {
  state.operating = operating;
  renderApprovals(operating.approvals || []);
  renderLearning(operating.learning || {});
  renderFinance(operating.finance || {});
}

function renderMemory(runs = []) {
  if (!runs.length) {
    elements.memoryList.innerHTML = '<div class="memory-item"><strong>No runs yet</strong><p>Memory will appear after the first goal.</p></div>';
    return;
  }

  elements.memoryList.innerHTML = runs
    .map(
      (run) => `
        <div class="memory-item">
          <strong>${escapeHTML(run.goal)}</strong>
          <p>${new Date(run.created_at).toLocaleString()}</p>
        </div>
      `,
    )
    .join("");
}

function renderAnalytics(analytics) {
  state.analytics = analytics;
  renderMetrics(analytics.metrics);
  renderChart(analytics.series);
  elements.generatedAt.textContent = new Date(analytics.generated_at).toLocaleTimeString();
}

async function loadDashboard() {
  const [health, dashboard] = await Promise.all([
    api("/api/health"),
    api("/api/dashboard"),
  ]);

  elements.healthState.textContent = health.ok ? "Online" : "Offline";
  elements.healthDetail.textContent = "FastAPI backend";
  elements.mode.textContent = `${dashboard.mode} mode`;
  renderAnalytics(dashboard.analytics);
  renderEvents(dashboard.analytics.agent_roster.map((agent) => ({
    agent: agent.name,
    status: agent.status,
    message: agent.task,
  })));
  renderSuggestions([
    "Run a R.A.M.B.O. status check.",
    "Connect Calendar, Gmail, Notes, and Tasks first.",
    "Add voice after the dashboard and real data loop works.",
  ]);
  renderOperating(dashboard.operating);
  renderMemory(dashboard.memory);
}

async function runGoal(goal) {
  elements.summary.textContent = "R.A.M.B.O. is routing the request...";
  const result = await api("/api/run", {
    method: "POST",
    body: JSON.stringify({ goal }),
  });

  state.lastResult = result;
  elements.mode.textContent = `${result.mode} mode`;
  elements.summary.textContent = result.summary;
  renderAnalytics(result.analytics);
  renderEvents(result.events);
  renderSuggestions(result.suggestions);
  renderOperating(result.operating);
  renderMemory(result.recent_memory);
}

async function decideApproval(approvalId, action) {
  const decision = action === "approve" ? "approved" : "rejected";
  const result = await api(`/api/approvals/${approvalId}/${action}`, {
    method: "POST",
    body: JSON.stringify({
      decision_note: `Sir ${decision} this request from the dashboard.`,
    }),
  });

  renderOperating(result.operating);
  elements.summary.textContent = `Sentinel recorded approval request ${approvalId} as ${decision}. No external action was executed.`;
}

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const goal = elements.goal.value.trim();
  if (!goal) return;

  try {
    await runGoal(goal);
  } catch (error) {
    elements.summary.textContent = error.message;
  }
});

elements.refresh.addEventListener("click", () => {
  loadDashboard().catch((error) => {
    elements.healthState.textContent = "Error";
    elements.healthDetail.textContent = error.message;
  });
});

elements.clearMemory.addEventListener("click", async () => {
  const result = await api("/api/memory", { method: "DELETE" });
  renderOperating(result.operating);
  renderMemory([]);
});

elements.approvalList.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;

  button.disabled = true;
  try {
    await decideApproval(button.dataset.approvalId, button.dataset.action);
  } catch (error) {
    elements.summary.textContent = error.message;
    button.disabled = false;
  }
});

loadDashboard().catch((error) => {
  elements.healthState.textContent = "Error";
  elements.healthDetail.textContent = error.message;
});
