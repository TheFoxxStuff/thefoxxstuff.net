/**
 * Presence store — управляет heartbeat и состоянием онлайн.
 *
 * Использование:
 *   presence.start(entityType, entityId)  — начать heartbeat (вызывается на странице контента)
 *   presence.stop()                        — остановить (при уходе)
 *   presence.startGlobal()                 — только "онлайн", без контента (главная)
 *
 * Автоматически:
 *   - Шлёт heartbeat каждые 30 сек
 *   - Останавливается при скрытии вкладки (visibilitychange)
 *   - Восстанавливается при возврате
 *   - Вызывает DELETE при выходе (beforeunload)
 */

import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';

const INTERVAL = 30_000; // 30 секунд

function getToken() {
  if (!browser) return null;
  try { const s = localStorage.getItem('auth'); if (s) { const p = JSON.parse(s); if (p?.token) return p.token; } return localStorage.getItem('auth_token'); } catch { return null; }
}

function createPresenceStore() {
  const { subscribe, set, update } = writable({
    online: [],        // [{user_id, username, display_name, avatar_thumb, role}]
    onlineCount: 0,
    viewing: [],       // кто смотрит текущий контент
    viewingCount: 0,
    ready: false,
  });

  let _intervalId = null;
  let _entityType = null;
  let _entityId = null;
  let _leaveUrl = null;  // DELETE URL при уходе

  async function beat() {
    const token = getToken();
    if (!token) return; // анонимы не трекаются

    const params = new URLSearchParams();
    if (_entityType) params.set('entity_type', _entityType);
    if (_entityId)   params.set('entity_id', _entityId);

    try {
      await fetch(`${API_BASE}/presence/heartbeat?${params}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
    } catch { /* игнорируем — offline graceful */ }
  }

  async function fetchOnline() {
    try {
      const res = await fetch(`${API_BASE}/presence/online`);
      if (res.ok) {
        const data = await res.json();
        update(s => ({ ...s, online: data.users, onlineCount: data.count, ready: true }));
      }
    } catch { /* игнорируем */ }
  }

  async function fetchViewing() {
    if (!_entityType || !_entityId) return;
    try {
      const res = await fetch(`${API_BASE}/presence/viewing/${_entityType}/${_entityId}`);
      if (res.ok) {
        const data = await res.json();
        update(s => ({ ...s, viewing: data.users, viewingCount: data.count }));
      }
    } catch { /* игнорируем */ }
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
    if (!token || !_leaveUrl) return;
    try {
      navigator.sendBeacon
        ? navigator.sendBeacon(_leaveUrl) // надёжнее при unload
        : await fetch(_leaveUrl, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` }, keepalive: true });
    } catch { /* */ }
  }

  function _setupVisibilityHandler() {
    if (!browser) return;
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

    // URL для DELETE при уходе
    const leaveParams = new URLSearchParams();
    if (entityType) leaveParams.set('entity_type', entityType);
    if (entityId)   leaveParams.set('entity_id', entityId);
    _leaveUrl = `${API_BASE}/presence/heartbeat?${leaveParams}`;

    // Сразу тикаем, потом по интервалу
    tick();
    _intervalId = setInterval(tick, INTERVAL);
    _setupVisibilityHandler();

    // Возвращаем функцию cleanup для onDestroy / $effect cleanup
    return () => {
      _stop();
      // Убираем из viewing но не убиваем глобальное присутствие
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
