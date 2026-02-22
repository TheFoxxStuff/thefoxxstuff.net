/**
 * Helper for client-side load functions that need auth.
 * Works fine with adapter-static (SPA) — always runs in browser.
 */
export function getToken() {
  try { return JSON.parse(localStorage.getItem('auth'))?.token ?? null; } catch { return null; }
}

export function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function authedFetch(fetch, url, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(url, { ...options, headers });
  if (!res.ok) return null;
  return res.json().catch(() => null);
}
