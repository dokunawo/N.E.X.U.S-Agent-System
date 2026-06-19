const state = {
  analytics: null,
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
  context.fillStyle = "#121923";
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

  context.strokeStyle = "#18d6e8";
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
    context.fillStyle = "#34d399";
    context.beginPath();
    context.arc(point.x, point.y, 5, 0, Math.PI * 2);
    context.fill();

    context.fillStyle = "#9aa9b8";
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
          <strong>${event.agent} - ${event.status}</strong>
          <p>${event.message}</p>
        </div>
      `,
    )
    .join("");
}

function renderSuggestions(suggestions = []) {
  elements.suggestions.innerHTML = suggestions
    .map((suggestion) => `<li>${suggestion}</li>`)
    .join("");
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
          <strong>${run.goal}</strong>
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
    "Run a N.E.X.U.S status check.",
    "Connect Calendar, Gmail, Notes, and Tasks first.",
    "Add voice after the dashboard and real data loop works.",
  ]);
  renderMemory(dashboard.memory);
}

async function runGoal(goal) {
  elements.summary.textContent = "N.E.X.U.S is routing the request...";
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
  renderMemory(result.recent_memory);
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
  await api("/api/memory", { method: "DELETE" });
  renderMemory([]);
});

loadDashboard().catch((error) => {
  elements.healthState.textContent = "Error";
  elements.healthDetail.textContent = error.message;
});
