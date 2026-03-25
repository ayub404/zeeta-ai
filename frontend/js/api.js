/**
 * Zeeta — js/api.js
 * Central API handler. All fetch calls go through here.
 */

const API_BASE = 'http://localhost:8000';

function getToken() {
  return localStorage.getItem('zeeta_token');
}

function getHeaders(isForm = false) {
  const headers = {};
  if (!isForm) headers['Content-Type'] = 'application/json';
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

/**
 * Core fetch wrapper.
 * Returns { ok, status, data } — never throws.
 */
async function apiFetch(path, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: getHeaders(options.isForm),
    });

    let data;
    try { data = await res.json(); }
    catch { data = {}; }

    if (res.status === 401) {
      // Token expired — clear and redirect to login
      localStorage.removeItem('zeeta_token');
      localStorage.removeItem('zeeta_user');
      if (!window.location.pathname.includes('login')) {
        window.location.href = 'login.html';
      }
    }

    return { ok: res.ok, status: res.status, data };
  } catch (err) {
    return {
      ok: false,
      status: 0,
      data: { detail: 'Cannot connect to server. Is the backend running on port 8000?' },
    };
  }
}

// ── Auth API ──────────────────────────────────────────────────────────────────

async function apiRegister(email, password, full_name, company = null) {
  return apiFetch('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, full_name, company }),
  });
}

async function apiLogin(email, password) {
  const form = new URLSearchParams();
  form.append('username', email);
  form.append('password', password);
  return apiFetch('/api/auth/login', { method: 'POST', body: form, isForm: true });
}

async function apiMe() {
  return apiFetch('/api/auth/me');
}

// ── Dashboard API ─────────────────────────────────────────────────────────────

async function apiStats() {
  return apiFetch('/api/stats');
}

async function apiShipments() {
  return apiFetch('/api/shipments');
}

async function apiAlerts() {
  return apiFetch('/api/alerts');
}

async function apiGetDecision(shipmentId) {
  return apiFetch(`/api/decisions/${shipmentId}`, { method: 'POST' });
}

async function apiApplyDecision(decisionId, outcome = '') {
  return apiFetch(`/api/decisions/${decisionId}/apply`, {
    method: 'PATCH',
    body: JSON.stringify({ outcome }),
  });
}
