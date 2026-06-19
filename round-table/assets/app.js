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

  // Home globe agent nodes: click to pin the info bubble, click elsewhere to clear it.
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
})();
