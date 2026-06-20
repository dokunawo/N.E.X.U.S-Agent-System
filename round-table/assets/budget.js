// budget.js — Steward's manual budget planner.
// SQLite-backed through /api/steward/budget. No localStorage/sessionStorage.
// Every formula here has a matching Excel/Sheets equivalent in the
// "Formula Reference" panel rendered on steward.html.

(function () {
  const root = document.getElementById('budget-planner');
  if (!root) return; // only runs on steward.html

  const fmt = (n) => {
    const sign = n < 0 ? '-' : '';
    return sign + '$' + Math.abs(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };
  const pct = (n) => (n * 100).toFixed(1) + '%';
  const uid = () => Math.random().toString(36).slice(2, 9);

  // ---- Default categories, matched 1:1 to Daniel's existing
  // "2026 Annual Personal Financial Planner" Google Sheet ----
  const EXPENSE_CATEGORIES = [
    'Asset', 'Auto Fees', 'Auto Insurance', 'Auto Lien', 'Auto Repairs & Maintenance',
    'Clothing', 'Dining & Drinks', 'Education', 'Entertainment', 'Fee & Bank Charges',
    'Fidelis Expenses', 'Fitness', 'Gas & Fuel', 'Groceries', 'Health', 'Subscriptions',
    'Misc Expenses', 'Parking', 'Personal Care', 'Rent', 'Shopping', 'Utilities: Gas',
    'Travel', 'Utilities: Electric', 'Utilities: internet', 'Utilities: Phone',
    'Utilities: Water', 'Other Insurance', 'Supplies', 'Software', 'Gifts'
  ];
  const INCOME_CATEGORIES = ['Paycheck', 'Interest', 'Dividends'];

  const DEFAULT_STATE = {
    balances: { checking: 157, savings: 210 }, // seeded from your sheet's "Configure" section
    income: INCOME_CATEGORIES.map((name) => ({ id: uid(), name, amount: 0 })),
    expenses: EXPENSE_CATEGORIES.map((name) => ({ id: uid(), name, budgeted: 0, actual: 0 })),
    goals: [
      { id: uid(), name: 'Emergency Fund (example — edit me)', target: 10000, current: 2400, targetDate: '2026-12-31' }
    ],
    investments: [
      { id: uid(), name: 'Brokerage (example — edit me)', balance: 5000, monthly: 200, annualReturnPct: 7 }
    ],
    debts: [
      { id: uid(), name: 'Example card (edit me)', balance: 1200, apr: 22, minPayment: 75 }
    ]
  };
  let STATE = cloneState(DEFAULT_STATE);
  let saveTimer = null;
  let lastSavedAt = null;

  function cloneState(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function setSaveStatus(message, mode) {
    const el = document.getElementById('budget-save-status');
    if (!el) return;
    el.textContent = message;
    el.dataset.mode = mode || 'idle';
  }

  function ensureIds(list) {
    return Array.isArray(list) ? list.map((row) => ({ ...row, id: row.id || uid() })) : [];
  }

  function normalizeState(saved) {
    const next = cloneState(DEFAULT_STATE);
    if (!saved || typeof saved !== 'object') return next;
    next.balances = {
      checking: Number(saved.balances?.checking ?? next.balances.checking) || 0,
      savings: Number(saved.balances?.savings ?? next.balances.savings) || 0
    };
    const income = ensureIds(saved.income);
    const expenses = ensureIds(saved.expenses);
    const goals = ensureIds(saved.goals);
    const investments = ensureIds(saved.investments);
    const debts = ensureIds(saved.debts);
    next.income = income.length ? income : next.income;
    next.expenses = expenses.length ? expenses : next.expenses;
    next.goals = goals.length ? goals : next.goals;
    next.investments = investments.length ? investments : next.investments;
    next.debts = debts.length ? debts : next.debts;
    return next;
  }

  async function loadBudgetState() {
    try {
      const response = await fetch('/api/steward/budget');
      if (!response.ok) throw new Error('load failed');
      const payload = await response.json();
      if (payload.state) {
        STATE = normalizeState(payload.state);
        lastSavedAt = payload.updated_at || null;
        setSaveStatus('Loaded Steward planner memory from SQLite' + (lastSavedAt ? ' · ' + lastSavedAt.slice(0, 19).replace('T', ' ') : ''), 'saved');
      } else {
        STATE = cloneState(DEFAULT_STATE);
        setSaveStatus('Using starter planner data · edits will save to SQLite', 'idle');
      }
    } catch (error) {
      STATE = cloneState(DEFAULT_STATE);
      setSaveStatus('SQLite planner memory unavailable · using starter data for this session', 'error');
    }
  }

  async function saveBudgetState() {
    setSaveStatus('Saving Steward planner memory...', 'saving');
    try {
      const response = await fetch('/api/steward/budget', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state: STATE })
      });
      if (!response.ok) throw new Error('save failed');
      const payload = await response.json();
      lastSavedAt = payload.updated_at || new Date().toISOString();
      setSaveStatus('Saved to local SQLite · ' + lastSavedAt.slice(0, 19).replace('T', ' '), 'saved');
    } catch (error) {
      setSaveStatus('Could not save to SQLite. Keep this page open and try again.', 'error');
    }
  }

  function queueSave() {
    clearTimeout(saveTimer);
    setSaveStatus('Unsaved changes...', 'dirty');
    saveTimer = setTimeout(saveBudgetState, 650);
  }

  // ---- Core math (mirrors the Excel formulas shown in the reference panel) ----
  function totals() {
    const totalIncome = STATE.income.reduce((s, r) => s + (Number(r.amount) || 0), 0);
    const totalBudgeted = STATE.expenses.reduce((s, r) => s + (Number(r.budgeted) || 0), 0);
    const totalActual = STATE.expenses.reduce((s, r) => s + (Number(r.actual) || 0), 0);
    const netCashFlow = totalIncome - totalActual;
    const savingsRate = totalIncome > 0 ? netCashFlow / totalIncome : 0;
    return { totalIncome, totalBudgeted, totalActual, netCashFlow, savingsRate };
  }

  // Investment future value with monthly compounding + monthly contribution.
  // Excel equivalent: =FV(rate/12, months, -contribution, -principal)
  function futureValue(principal, monthlyContribution, annualRatePct, months) {
    const r = (Number(annualRatePct) || 0) / 100 / 12;
    const P = Number(principal) || 0;
    const C = Number(monthlyContribution) || 0;
    if (r === 0) return P + C * months;
    return P * Math.pow(1 + r, months) + C * ((Math.pow(1 + r, months) - 1) / r);
  }

  // Months to payoff at a fixed payment.
  // Excel equivalent: =NPER(apr/12, -minPayment, balance)
  function monthsToPayoff(balance, aprPct, payment) {
    const r = (Number(aprPct) || 0) / 100 / 12;
    const B = Number(balance) || 0;
    const Pmt = Number(payment) || 0;
    if (Pmt <= 0) return Infinity;
    if (r === 0) return B / Pmt;
    if (Pmt <= B * r) return Infinity; // payment doesn't even cover interest
    return -Math.log(1 - (r * B) / Pmt) / Math.log(1 + r);
  }

  // ---- Rendering ----
  function renderKPIs() {
    const t = totals();
    const liquid = STATE.balances.checking + STATE.balances.savings;
    const avgMonthlyExpense = t.totalActual > 0 ? t.totalActual : t.totalBudgeted;
    const runway = avgMonthlyExpense > 0 ? liquid / avgMonthlyExpense : 0;

    document.getElementById('kpi-income').textContent = fmt(t.totalIncome);
    document.getElementById('kpi-expense').textContent = fmt(t.totalActual);
    const netEl = document.getElementById('kpi-net');
    netEl.textContent = fmt(t.netCashFlow);
    netEl.className = 'val ' + (t.netCashFlow >= 0 ? 'pos' : 'neg');
    document.getElementById('kpi-rate').textContent = pct(t.savingsRate);
    document.getElementById('kpi-runway').textContent = (runway === Infinity ? '—' : runway.toFixed(1)) + ' mo';
  }

  function renderIncome() {
    const tbody = document.getElementById('income-body');
    tbody.innerHTML = '';
    STATE.income.forEach((row) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td class="cat-name">${row.name}</td>
        <td><input type="number" step="0.01" value="${row.amount}" data-kind="income" data-id="${row.id}" data-field="amount" /></td>
        <td><button class="btn ghost danger" data-action="remove-income" data-id="${row.id}">✕</button></td>`;
      tbody.appendChild(tr);
    });
  }

  function renderExpenses() {
    const tbody = document.getElementById('expense-body');
    tbody.innerHTML = '';
    const t = totals();
    STATE.expenses.forEach((row) => {
      const remaining = (Number(row.budgeted) || 0) - (Number(row.actual) || 0);
      const pctInc = t.totalIncome > 0 ? (Number(row.actual) || 0) / t.totalIncome : 0;
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td class="cat-name">${row.name}</td>
        <td><input type="number" step="0.01" value="${row.budgeted}" data-kind="expense" data-id="${row.id}" data-field="budgeted" /></td>
        <td><input type="number" step="0.01" value="${row.actual}" data-kind="expense" data-id="${row.id}" data-field="actual" /></td>
        <td class="cell-readonly ${remaining < 0 ? 'cell-neg' : 'cell-pos'}">${fmt(remaining)}</td>
        <td class="cell-readonly">${pct(pctInc)}</td>`;
      tbody.appendChild(tr);
    });
  }

  function renderGoals() {
    const wrap = document.getElementById('goals-grid');
    wrap.innerHTML = '';
    STATE.goals.forEach((g) => {
      const complete = g.target > 0 ? Math.min(g.current / g.target, 1) : 0;
      const today = new Date();
      const target = new Date(g.targetDate || today);
      const monthsLeft = Math.max(1, Math.round((target - today) / (1000 * 60 * 60 * 24 * 30.4)));
      const monthlyNeeded = Math.max(0, (g.target - g.current) / monthsLeft);
      const card = document.createElement('div');
      card.className = 'goal-card';
      card.innerHTML = `
        <div class="gname">${g.name}</div>
        <div class="bar"><div class="bar-fill" style="width:${(complete * 100).toFixed(0)}%"></div></div>
        <div class="goal-meta"><span>${fmt(g.current)} / ${fmt(g.target)}</span><span>${(complete * 100).toFixed(0)}%</span></div>
        <div class="goal-meta" style="margin-top:6px;"><span>Target: ${g.targetDate || '—'}</span><span>${fmt(monthlyNeeded)}/mo needed</span></div>`;
      wrap.appendChild(card);
    });
  }

  function renderInvestments() {
    const wrap = document.getElementById('invest-grid');
    wrap.innerHTML = '';
    STATE.investments.forEach((inv) => {
      const fv1 = futureValue(inv.balance, inv.monthly, inv.annualReturnPct, 12);
      const fv5 = futureValue(inv.balance, inv.monthly, inv.annualReturnPct, 60);
      const fv10 = futureValue(inv.balance, inv.monthly, inv.annualReturnPct, 120);
      const card = document.createElement('div');
      card.className = 'invest-card';
      card.innerHTML = `
        <div class="gname">${inv.name}</div>
        <div class="goal-meta"><span>Balance</span><span>${fmt(inv.balance)}</span></div>
        <div class="goal-meta"><span>Monthly contribution</span><span>${fmt(inv.monthly)}</span></div>
        <div class="goal-meta"><span>Assumed return</span><span>${inv.annualReturnPct}%/yr</span></div>
        <div class="bar" style="margin-top:10px;"></div>
        <div class="goal-meta"><span>1 yr</span><span class="cell-pos">${fmt(fv1)}</span></div>
        <div class="goal-meta"><span>5 yr</span><span class="cell-pos">${fmt(fv5)}</span></div>
        <div class="goal-meta"><span>10 yr</span><span class="cell-pos">${fmt(fv10)}</span></div>`;
      wrap.appendChild(card);
    });
  }

  function renderDebts() {
    const tbody = document.getElementById('debt-body');
    tbody.innerHTML = '';
    STATE.debts.forEach((d) => {
      const months = monthsToPayoff(d.balance, d.apr, d.minPayment);
      const monthsText = months === Infinity ? 'Payment too low' : Math.ceil(months) + ' mo';
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td class="cat-name">${d.name}</td>
        <td><input type="number" step="0.01" value="${d.balance}" data-kind="debt" data-id="${d.id}" data-field="balance" /></td>
        <td><input type="number" step="0.01" value="${d.apr}" data-kind="debt" data-id="${d.id}" data-field="apr" /></td>
        <td><input type="number" step="0.01" value="${d.minPayment}" data-kind="debt" data-id="${d.id}" data-field="minPayment" /></td>
        <td class="cell-readonly ${months === Infinity ? 'cell-neg' : ''}">${monthsText}</td>`;
      tbody.appendChild(tr);
    });
  }

  function renderAll() {
    renderKPIs();
    renderIncome();
    renderExpenses();
    renderGoals();
    renderInvestments();
    renderDebts();
  }

  // ---- Event delegation for all editable inputs ----
  root.addEventListener('input', (e) => {
    const t = e.target;
    if (!t.dataset.kind) return;
    const { kind, id, field } = t.dataset;
    const list = kind === 'income' ? STATE.income : kind === 'expense' ? STATE.expenses : kind === 'debt' ? STATE.debts : null;
    if (!list) return;
    const row = list.find((r) => r.id === id);
    if (!row) return;
    row[field] = t.value === '' ? 0 : Number(t.value);
    renderKPIs();
    if (kind === 'expense') renderExpenses();
    queueSave();
  });

  root.addEventListener('click', (e) => {
    const action = e.target.dataset.action;
    if (action === 'remove-income') {
      STATE.income = STATE.income.filter((r) => r.id !== e.target.dataset.id);
      renderIncome(); renderKPIs();
      queueSave();
    }
    if (action === 'add-income') {
      const name = prompt('Income source name (e.g. Freelance, Bonus):');
      if (name) { STATE.income.push({ id: uid(), name, amount: 0 }); renderIncome(); renderKPIs(); queueSave(); }
    }
    if (action === 'add-goal') {
      const name = prompt('Goal name:'); if (!name) return;
      STATE.goals.push({ id: uid(), name, target: 1000, current: 0, targetDate: '' });
      renderGoals();
      queueSave();
    }
    if (action === 'add-investment') {
      const name = prompt('Account name:'); if (!name) return;
      STATE.investments.push({ id: uid(), name, balance: 0, monthly: 0, annualReturnPct: 7 });
      renderInvestments();
      queueSave();
    }
    if (action === 'add-debt') {
      const name = prompt('Debt name:'); if (!name) return;
      STATE.debts.push({ id: uid(), name, balance: 0, apr: 0, minPayment: 0 });
      renderDebts();
      queueSave();
    }
  });

  loadBudgetState().then(renderAll);
})();
