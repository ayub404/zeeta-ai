/**
 * Zeeta — js/dashboard.js
 * All dashboard rendering logic.
 */

// ── Boot ──────────────────────────────────────────────────────────────────────

async function initDashboard() {
  const session = requireAuth();
  if (!session) return;

  // Set user info in sidebar
  const { user } = session;
  const initials = user.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
  const avatarEl = document.getElementById('user-avatar');
  const nameEl   = document.getElementById('user-name');
  if (avatarEl) avatarEl.textContent = initials;
  if (nameEl)   nameEl.textContent   = user.name;

  await loadDashboard();

  // Auto-refresh every 5 minutes
  setInterval(loadDashboard, 5 * 60 * 1000);
}

async function loadDashboard() {
  showLoadingBar(true);

  const [statsRes, shipmentsRes, alertsRes] = await Promise.all([
    apiStats(),
    apiShipments(),
    apiAlerts(),
  ]);

  showLoadingBar(false);

  if (statsRes.ok)     renderStats(statsRes.data);
  if (shipmentsRes.ok) renderShipments(shipmentsRes.data);
  if (alertsRes.ok)    renderAlerts(alertsRes.data);

  updateTimestamp();
}

function showLoadingBar(on) {
  const bar = document.getElementById('loading-bar');
  if (bar) bar.style.display = on ? 'block' : 'none';
}

function updateTimestamp() {
  const el = document.getElementById('last-updated');
  if (!el) return;
  const now = new Date();
  el.textContent = `Live · Updated ${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`;
}

// ── Stats ─────────────────────────────────────────────────────────────────────

function renderStats(s) {
  setText('kpi-total',      s.total_shipments);
  setText('kpi-ontime',     s.on_time);
  setText('kpi-delayed',    s.delayed);
  setText('kpi-critical',   s.critical);
  setText('kpi-risk',       s.avg_risk_score);
  setText('kpi-disruptions', s.disruptions_avoided);
  setText('kpi-savings',    '$' + Number(s.savings_usd).toLocaleString());
  setText('kpi-live-alerts', s.live_alerts);
  setText('alert-badge',    (s.live_alerts || 0) + ' alerts');
  setText('alert-badge-2',  s.live_alerts || 0);
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val ?? '—';
}

// ── Shipments ─────────────────────────────────────────────────────────────────

function riskColor(r) {
  if (r >= 70) return '#f05060';
  if (r >= 40) return '#f0a030';
  return '#00e5b4';
}

function renderShipments(list) {
  const tbody = document.getElementById('shipments-tbody');
  const count = document.getElementById('shipment-count');
  if (!tbody) return;

  if (count) count.textContent = list.length + ' shipments';

  if (!list.length) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;
      color:var(--muted);padding:32px;">No shipments found</td></tr>`;
    return;
  }

  tbody.innerHTML = list.map(s => {
    const r   = s.risk_score || 0;
    const col = riskColor(r);
    const needsDecision = ['critical', 'delayed'].includes(s.status);
    const btn = needsDecision
      ? `<button class="decide-btn" onclick="openDecisionModal('${s.id}')">Decide →</button>`
      : `<span style="color:var(--muted2);font-size:12px;">—</span>`;

    return `
      <tr>
        <td>
          <div class="route-name">${s.origin} <span class="route-arrow">→</span> ${s.destination}</div>
          <div class="route-id">${s.id} · ${s.cargo || ''}</div>
        </td>
        <td style="font-size:12px;color:var(--muted);">${s.carrier}</td>
        <td>
          <span class="status-chip chip-${s.status}">
            <span class="status-dot dot-${s.status}"></span>
            ${s.status.replace('_', ' ')}
          </span>
        </td>
        <td>
          <div style="display:flex;align-items:center;gap:8px;">
            <div class="risk-track">
              <div class="risk-fill" style="width:${r}%;background:${col};"></div>
            </div>
            <span style="font-size:11px;font-family:var(--mono);color:${col};">${r}</span>
          </div>
        </td>
        <td style="font-size:12px;font-family:var(--mono);color:var(--muted);">${s.eta || '—'}</td>
        <td>${btn}</td>
      </tr>`;
  }).join('');
}

// ── Alerts ────────────────────────────────────────────────────────────────────

function renderAlerts(list) {
  const el = document.getElementById('alerts-list');
  if (!el) return;

  if (!list.length) {
    el.innerHTML = `<div style="padding:24px;text-align:center;
      color:var(--muted);font-size:13px;">No active alerts</div>`;
    return;
  }

  el.innerHTML = list.map(a => `
    <div class="alert-item">
      <div class="alert-row1">
        <span class="alert-type-chip chip-${a.type}">${a.type}</span>
        <span class="sev-chip sev-${a.severity}">${a.severity.toUpperCase()}</span>
      </div>
      <div class="alert-msg">${a.message}</div>
      <div class="alert-footer">
        <span>${a.affected_shipments} affected${a.source !== 'internal' ? ' · ' + a.source : ''}</span>
        <span>${a.time || ''}</span>
      </div>
    </div>`).join('');
}

// ── Decision Modal ────────────────────────────────────────────────────────────

async function openDecisionModal(shipmentId) {
  // Reset modal
  setText('modal-title',    `AI Decision · ${shipmentId}`);
  setText('modal-sub',      'Fetching live recommendation...');
  setText('modal-action',   'Analyzing...');
  setText('modal-reason',   '');
  setText('modal-cost',     '—');
  setText('modal-time',     '—');
  setText('modal-conf-val', '—');
  setText('modal-conf-pct', '—');

  const bar = document.getElementById('modal-conf-bar');
  if (bar) bar.style.width = '0%';

  openModal();

  const r = await apiGetDecision(shipmentId);

  if (!r.ok) {
    setText('modal-action', 'Failed to get decision. Check backend.');
    setText('modal-sub', extractError(r.data));
    return;
  }

  const d = r.data;
  setText('modal-sub',      'Zeeta decision engine · Live data');
  setText('modal-action',   d.action);
  setText('modal-reason',   d.reason);
  setText('modal-cost',     d.cost_impact);
  setText('modal-time',     d.time_impact);
  setText('modal-conf-val', d.confidence + '%');
  setText('modal-conf-pct', d.confidence + '%');

  const applyBtn = document.getElementById('modal-apply-btn');
  if (applyBtn) applyBtn.dataset.id = d.id;

  setTimeout(() => {
    if (bar) bar.style.width = d.confidence + '%';
  }, 100);
}

async function applyDecision() {
  const applyBtn = document.getElementById('modal-apply-btn');
  const id = applyBtn?.dataset?.id;
  if (id) {
    await apiApplyDecision(id, 'Applied from dashboard');
  }
  closeModal();
  await loadDashboard();
}

function openModal() {
  const m = document.getElementById('modal');
  if (m) m.classList.add('open');
}

function closeModal() {
  const m = document.getElementById('modal');
  if (m) m.classList.remove('open');
}
