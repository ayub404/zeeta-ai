/**
 * Zeeta — js/auth.js
 * Token storage, session management, page guards.
 */

function saveSession(data) {
  localStorage.setItem('zeeta_token', data.access_token);
  localStorage.setItem('zeeta_user', JSON.stringify({
    id:       data.user_id,
    email:    data.email,
    name:     data.full_name,
    role:     data.role,
  }));
}

function getSession() {
  const token = localStorage.getItem('zeeta_token');
  const user  = localStorage.getItem('zeeta_user');
  if (!token || !user) return null;
  try { return { token, user: JSON.parse(user) }; }
  catch { return null; }
}

function clearSession() {
  localStorage.removeItem('zeeta_token');
  localStorage.removeItem('zeeta_user');
}

function logout() {
  clearSession();
  window.location.href = 'index.html';
}

/** Call at top of dashboard.html — redirects to login if not authenticated */
function requireAuth() {
  const session = getSession();
  if (!session) {
    window.location.href = 'login.html';
    return null;
  }
  return session;
}

/** Call at top of login.html/signup.html — redirects to dashboard if already logged in */
function redirectIfLoggedIn() {
  const session = getSession();
  if (session) {
    window.location.href = 'dashboard.html';
  }
}

// ── UI helpers ────────────────────────────────────────────────────────────────

function showError(elementId, message) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.textContent = message;
  el.style.display = 'block';
}

function hideError(elementId) {
  const el = document.getElementById(elementId);
  if (el) el.style.display = 'none';
}

function showSuccess(elementId, message) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.textContent = message;
  el.style.display = 'block';
}

function setLoading(btnId, textId, loading, defaultText) {
  const btn = document.getElementById(btnId);
  const txt = document.getElementById(textId);
  if (!btn || !txt) return;
  btn.disabled = loading;
  txt.innerHTML = loading
    ? '<span class="spinner"></span>'
    : defaultText;
}

function extractError(data) {
  if (!data) return 'Something went wrong.';
  if (typeof data.detail === 'string') return data.detail;
  if (Array.isArray(data.detail)) {
    return data.detail.map(e => e.msg).join(', ');
  }
  return 'Something went wrong.';
}
