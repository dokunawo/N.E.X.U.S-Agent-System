// app.js — shared across every Round Table page
(function () {
  // Live clock
  function tick() {
    const el = document.getElementById('sys-clock');
    if (!el) return;
    const now = new Date();
    const opts = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
    el.textContent = now.toLocaleTimeString('en-US', opts) + ' LOCAL';
  }
  tick();
  setInterval(tick, 1000);

  // Count-up animation for stat numbers: <span class="num" data-count="142">
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('[data-count]').forEach(function (el) {
    const target = parseInt(el.getAttribute('data-count'), 10) || 0;
    const suffix = el.getAttribute('data-suffix') || '';
    if (reduced) { el.textContent = target + suffix; return; }
    let start = null;
    const duration = 900;
    function frame(ts) {
      if (!start) start = ts;
      const progress = Math.min((ts - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(eased * target) + suffix;
      if (progress < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  });

  // Home globe Brain nodes: click to pin the info bubble, click elsewhere to clear it.
  const homeNodes = Array.from(document.querySelectorAll('[data-node-toggle]'));
  if (homeNodes.length) {
    document.addEventListener('click', function (event) {
      const insideNode = event.target.closest('.home-node');
      if (!insideNode) {
        homeNodes.forEach((node) => node.closest('.home-node')?.classList.remove('is-open'));
        return;
      }

      if (event.target.closest('.node-bubble-link')) {
        return;
      }

      const host = insideNode.closest('.home-node');
      homeNodes.forEach((node) => {
        const parent = node.closest('.home-node');
        if (parent && parent !== host) parent.classList.remove('is-open');
      });
      if (host) host.classList.toggle('is-open');
      event.preventDefault();
    });
  }

  // Live council journals: replace baked sample entries with SQLite-backed logs.
  const journalBlocks = Array.from(document.querySelectorAll('[data-agent-journal]'));
  if (journalBlocks.length) {
    const emptyCopy = {
      completed: 'Nothing logged in SQLite yet.',
      inProgress: 'Nothing in motion right now.',
      queued: 'Queue is empty.'
    };

    function buildEntry(entry) {
      const row = document.createElement('div');
      row.className = 'j-entry';
      if (entry.date) {
        const date = document.createElement('div');
        date.className = 'j-date';
        date.textContent = entry.date;
        row.appendChild(date);
      }
      const title = document.createElement('div');
      title.className = 'j-title';
      title.textContent = entry.title || 'Untitled task';
      const note = document.createElement('div');
      note.className = 'j-note';
      note.textContent = entry.note || entry.status || '';
      row.appendChild(title);
      row.appendChild(note);
      return row;
    }

    function renderJournalColumn(column, entries, key) {
      const heading = column.querySelector('h4');
      column.replaceChildren();
      if (heading) column.appendChild(heading);
      if (!entries || !entries.length) {
        const empty = document.createElement('div');
        empty.className = 'j-empty';
        empty.textContent = emptyCopy[key] || 'No entries yet.';
        column.appendChild(empty);
        return;
      }
      entries.forEach((entry) => column.appendChild(buildEntry(entry)));
    }

    fetch('/api/council/journals')
      .then((response) => response.ok ? response.json() : Promise.reject(new Error('journal fetch failed')))
      .then((payload) => {
        const journals = payload.journals || {};
        journalBlocks.forEach((block) => {
          const agentId = block.getAttribute('data-agent-journal');
          const journal = journals[agentId];
          if (!journal) return;
          block.querySelectorAll('[data-journal-column]').forEach((column) => {
            const key = column.getAttribute('data-journal-column');
            renderJournalColumn(column, journal[key] || [], key);
          });
          block.classList.add('is-live');
        });
      })
      .catch(() => {
        journalBlocks.forEach((block) => block.classList.add('is-offline'));
      });
  }

  // Daily R.A.M.B.O. briefing on the home surface.
  const briefingRoot = document.querySelector('[data-daily-briefing]');
  if (briefingRoot) {
    const setText = (selector, value) => {
      const el = briefingRoot.querySelector(selector);
      if (el) el.textContent = value;
    };
    function renderBriefing(payload) {
      setText('[data-briefing-greeting]', payload.greeting || 'R.A.M.B.O. is online.');
      if (payload.time) {
        setText('[data-briefing-clock]', `${payload.time.day} · ${payload.time.date} · ${payload.time.display}`);
      }

      const weather = payload.weather || {};
      const temp = typeof weather.temperature_f === 'number' ? `${Math.round(weather.temperature_f)}°F` : 'unavailable';
      setText('[data-briefing-weather]', `${weather.summary || 'Weather unavailable'} · ${temp}`);

      const calendar = payload.calendar || {};
      setText('[data-briefing-calendar]', calendar.summary || 'Calendar not connected yet.');

      const today = payload.today || {};
      setText('[data-briefing-focus]', today.focus || 'No daily focus loaded yet.');
      setText('[data-briefing-approvals]', `${today.approvals_waiting || 0} waiting`);

      const agents = briefingRoot.querySelector('[data-briefing-agents]');
      if (agents) {
        agents.replaceChildren();
        (payload.agent_briefing || []).slice(0, 11).forEach((item) => {
          const row = document.createElement('div');
          row.className = 'briefing-agent-row';
          row.innerHTML = `<strong></strong><span></span>`;
          row.querySelector('strong').textContent = item.agent;
          row.querySelector('span').textContent = item.status;
          agents.appendChild(row);
        });
      }

      const tasks = briefingRoot.querySelector('[data-briefing-tasks]');
      if (tasks) {
        tasks.replaceChildren();
        const taskRows = today.tasks && today.tasks.length ? today.tasks : [];
        taskRows.slice(0, 5).forEach((item) => {
          const row = document.createElement('div');
          row.className = 'briefing-task-row';
          row.innerHTML = `<strong></strong><span></span>`;
          row.querySelector('strong').textContent = item.title;
          row.querySelector('span').textContent = `${item.owner} · ${item.status}`;
          tasks.appendChild(row);
        });
        if (!taskRows.length) {
          const row = document.createElement('div');
          row.className = 'briefing-task-row';
          row.innerHTML = `<strong>Build the operating loop</strong><span>Keeper + Pilot · queued</span>`;
          tasks.appendChild(row);
        }
        (today.recommended_next || []).slice(0, 3).forEach((text) => {
          const row = document.createElement('div');
          row.className = 'briefing-task-row next';
          row.innerHTML = `<strong>Next</strong><span></span>`;
          row.querySelector('span').textContent = text;
          tasks.appendChild(row);
        });
      }
    }

    fetch('/api/briefing/daily')
      .then((response) => response.ok ? response.json() : Promise.reject(new Error('briefing failed')))
      .then(renderBriefing)
      .catch(() => {
        setText('[data-briefing-greeting]', 'R.A.M.B.O. online. Systems synchronized. Daily briefing endpoint is offline.');
        setText('[data-briefing-weather]', 'Weather unavailable');
        setText('[data-briefing-calendar]', 'Calendar not connected');
        setText('[data-briefing-focus]', 'Restart the local server to reload the briefing service.');
        setText('[data-briefing-approvals]', 'Unknown');
      });
  }
})();
