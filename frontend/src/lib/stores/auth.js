import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const KEY = 'auth';

function load() {
  if (!browser) return { token: null, user: null };
  try {
    const r = localStorage.getItem(KEY);
    if (r) {
      const p = JSON.parse(r);
      // FIX: валидируем структуру — не принимаем мусор из localStorage
      if (p && typeof p.token === 'string' && p.token.length > 0) return p;
    }
  } catch {}
  return { token: null, user: null };
}

function save(s) {
  if (!browser) return;
  try { localStorage.setItem(KEY, JSON.stringify(s)); } catch {}
}

const createAuthStore = () => {
  const { subscribe, set, update } = writable(load());

  return {
    subscribe,

    login: (token, user) => {
      // FIX: валидируем токен перед сохранением
      if (!token || typeof token !== 'string') return;
      const s = { token, user };
      save(s);
      set(s);
    },

    logout: () => {
      if (browser) localStorage.removeItem(KEY);
      set({ token: null, user: null });
    },

    setUser: (user) => update(s => {
      if (!s.token) return s; // FIX: не обновляем если уже разлогинились
      const n = { ...s, user };
      save(n);
      return n;
    }),

    updateUser: (partial) => update(s => {
      if (!s.user || !s.token) return s; // FIX: не обновляем если нет юзера или токена
      const n = { ...s, user: { ...s.user, ...partial } };
      save(n);
      return n;
    }),
  };
};

export const auth = createAuthStore();
export const isAdmin = (user) => user?.role === 'admin';
