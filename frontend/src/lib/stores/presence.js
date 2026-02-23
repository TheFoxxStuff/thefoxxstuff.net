/**
 * Presence store — управляет heartbeat и real-time состоянием онлайн.
 *
 * Heartbeat: каждые 30 сек (обновляет TTL в Redis)
 * Polling online/viewing: каждые 5 сек (real-time обновление UI)
 */

import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';

const HEARTBEAT_INTERVAL = 30_000; // 30 сек — обновляем TTL в Redis
const POLL_INTERVAL      =  5_000; // 5 сек  — обновляем UI

function getToken() {
  if (!browser) return null;
  try {
    const s = localStorage.getItem('auth');
    if (s) {
      const p = JSON.parse(s);
      if (p?.token) return p.token;
    }
    return localStorage.getItem('auth_token');
  } catch {
    return null;
  }
}

function createPresenceStore() {
  const { subscribe, update } = writable({
    online: [],
    onlineCount: 0,
    viewing: [],
    viewingCount: 0,
    ready: false,
  });

  let _heartbeatId = null;
  let _pollId      = null;
  let _entityType  = null;
  let _entityId    = null;
  let _listenersAdded = false;

  // ── Heartbeat: только сообщаем серверу что живы ──────────────────
  async function beat() {
    const token = getToken();
    if (!token) return;

    const params = new URLSearchParams();
    if (_entityType) params.set('entity_type', _entityType);
    if (_entityId)   params.set('entity_id', _entityId);

    try {
      await fetch(`${API_BASE}/presence/heartbeat?${params}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
    } catch {}
  }

  // ── Polling: читаем актуальное состояние ─────────────────────────
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

  // Первый тик — сразу и heartbeat и fetch
  async function firstTick() {
    await beat();
    await fetchOnline();
    await fetchViewing();
  }

  // Polling тик — только читаем, не шлём heartbeat
  async function pollTick() {
    await fetchOnline();
    await fetchViewing();
  }

  function _stopAll() {
    if (_heartbeatId) { clearInterval(_heartbeatId); _heartbeatId = null; }
    if (_pollId)      { clearInterval(_pollId);      _pollId = null; }
  }

  async function _leave() {
    _stopAll();
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
        _stopAll();
      } else {
        // Вернулись на вкладку — сразу обновляем
        firstTick();
        _heartbeatId = setInterval(beat, HEARTBEAT_INTERVAL);
        _pollId      = setInterval(pollTick, POLL_INTERVAL);
      }
    });

    window.addEventListener('beforeunload', _leave);
  }

  function start(entityType = null, entityId = null) {
    if (!browser) return () => {};

    _stopAll();
    _entityType = entityType;
    _entityId   = entityId;

    _setupListeners();

    // Сразу тикаем
    firstTick();

    // Heartbeat каждые 30 сек
    _heartbeatId = setInterval(beat, HEARTBEAT_INTERVAL);

    // Polling каждые 5 сек
    _pollId = setInterval(pollTick, POLL_INTERVAL);

    // Cleanup при уходе со страницы
    return () => {
      _stopAll();
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
