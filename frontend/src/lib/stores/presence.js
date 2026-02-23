/**
 * Presence store — управляет heartbeat и состоянием онлайн.
 */

import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';

const INTERVAL = 30_000;

function getToken() {
  if (!browser) return null;
  try {
    // Auth store сохраняет { token, user } под ключом 'auth'
    const s = localStorage.getItem('auth');
    if (s) {
      const p = JSON.parse(s);
      if (p?.token) return p.token;
    }
    // Fallback на старый ключ
    return localStorage.getItem('auth_token');
  } catch {
    return null;
  }
}

function createPresenceStore() {
  const { subscribe, set, update } = writable({
    online: [],
    onlineCount: 0,
    viewing: [],
    viewingCount: 0,
    ready: false,
  });

  let _intervalId = null;
  let _entityType = null;
  let _entityId = null;
  let _listenersAdded = false;

  async function beat() {
    const token = getToken();
    if (!token) return;

    const params = new URLSearchParams();
    if (_entityType) params.set('entity_type', _entityType);
    if (_entityId)   params.set('entity_id', _entityId);

    try {
      const res = await fetch(`${API_BASE}/presence/heartbeat?${params}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        console.warn('[presence] heartbeat failed:', res.status);
      }
    } catch (e) {
      console.warn('[presence] heartbeat error:', e);
    }
  }

  async function fetchOnline() {
    try {
      const res = await fetch(`${API_BASE}/presence/online`);
      if (res.ok) {
        const data = await res.json();
        update(s => ({ ...s, online: data.users, onlineCount: data.count, ready: true }));
      }
    } catch {}
  }

  async function fetchViewing() {
    if (!_entityType || !_entityId) return;
    try {
      const res = await fetch(`${API_BASE}/presence/viewing/${_entityType}/${_entityId}`);
      if (res.ok) {
        const data = await res.json();
        update(s => ({ ...s, viewing: data.users, viewingCount: data.count }));
      }
    } catch {}
  }

  async function tick() {
    await beat();
    await fetchOnline();
    await fetchViewing();
  }

  function _stop() {
    if (_intervalId) {
      clearInterval(_intervalId);
      _intervalId = null;
    }
  }

  async function _leave() {
    _stop();
    const token = getToken();
    if (!token) return;
    const params = new URLSearchParams();
    if (_entityType) params.set('entity_type', _entityType);
    if (_entityId)   params.set('entity_id', _entityId);
    try {
      const url = `${API_BASE}/presence/heartbeat?${params}`;
      if (navigator.sendBeacon) {
        navigator.sendBeacon(url);
      } else {
        fetch(url, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` }, keepalive: true }).catch(() => {});
      }
    } catch {}
  }

  function _setupListeners() {
    if (!browser || _listenersAdded) return;
    _listenersAdded = true;

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        _stop();
      } else {
        tick();
        _intervalId = setInterval(tick, INTERVAL);
      }
    });

    window.addEventListener('beforeunload', _leave);
  }

  function start(entityType = null, entityId = null) {
    if (!browser) return () => {};

    _stop();
    _entityType = entityType;
    _entityId = entityId;

    _setupListeners();
    tick();
    _intervalId = setInterval(tick, INTERVAL);

    return () => {
      _stop();
      if (entityType && entityId) {
        const token = getToken();
        if (token) {
          const params = new URLSearchParams({ entity_type: entityType, entity_id: entityId });
          fetch(`${API_BASE}/presence/heartbeat?${params}`, {
            method: 'DELETE',
            headers: { Authorization: `Bearer ${token}` },
            keepalive: true,
          }).catch(() => {});
        }
      }
    };
  }

  function startGlobal() {
    return start(null, null);
  }

  return { subscribe, start, startGlobal };
}

export const presence = createPresenceStore();
