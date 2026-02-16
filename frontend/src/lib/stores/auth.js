import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const KEY = 'auth';
function load() {
  if (!browser) return { token: null, user: null };
  try { const r = localStorage.getItem(KEY); if (r) { const p = JSON.parse(r); if (p.token) return p; } } catch {}
  return { token: null, user: null };
}
function save(s) { if (browser) try { localStorage.setItem(KEY, JSON.stringify(s)); } catch {} }

const createAuthStore = () => {
  const { subscribe, set, update } = writable(load());
  return {
    subscribe,
    login: (token, user) => { const s = { token, user }; save(s); set(s); },
    logout: () => { if (browser) localStorage.removeItem(KEY); set({ token: null, user: null }); },
    setUser: (user) => update(s => { const n = { ...s, user }; save(n); return n; }),
    updateUser: (partial) => update(s => {
      if (!s.user) return s;
      const n = { ...s, user: { ...s.user, ...partial } };
      save(n);
      return n;
    }),
  };
};

export const auth = createAuthStore();
export const isAdmin = (user) => user?.role === 'admin';
