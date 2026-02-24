/**
 * Presence store — WebSocket + Redis Pub/Sub.
 *
 * - Одно постоянное WS-соединение на весь сеанс (стартует из +layout.svelte)
 * - Сервер пушит обновления мгновенно через Redis Pub/Sub — polling убран
 * - Grace period: при уходе юзера не убираем его сразу из UI (4 сек дебаунс)
 *   → исчезают прыжки при reload/переходах между страницами
 * - Heartbeat раз в 30 сек держит TTL в Redis
 */

import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';

const HEARTBEAT_INTERVAL = 20_000;  // каждые 20 сек — запас до TTL в Redis
const RECONNECT_BASE     = 2_000;   // базовая задержка реконнекта
const MAX_RECONNECT      = 12;
const DISAPPEAR_DELAY    = 4_000;   // мс — ждём перед тем как убрать юзера из UI

function wsUrl(token) {
  const base = API_BASE.replace(/^http/, 'ws');
  const url  = `${base}/presence/ws`;
  return token ? `${url}?token=${encodeURIComponent(token)}` : url;
}

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
  const store = writable({
    online:       [],
    onlineCount:  0,
    viewing:      [],
    viewingCount: 0,
    connected:    false,
    ready:        false,
  });
  const { subscribe, update } = store;

  let _ws             = null;
  let _heartbeatId    = null;
  let _reconnectId    = null;
  let _reconnectCount = 0;
  let _entityType     = null;
  let _entityId       = null;
  let _globalStarted  = false;
  let _globalStopped  = false;
  let _listenersAdded = false;

  // Дебаунс исчезновения юзеров
  let _disappearTimer = null;
  let _pendingUpdate  = null;

  // ── Отправить если соединение открыто ────────────────────────────────
  function _send(msg) {
    if (_ws && _ws.readyState === WebSocket.OPEN) {
      _ws.send(JSON.stringify(msg));
    }
  }

  // ── Применение обновления с дебаунсом ────────────────────────────────
  function _commitUpdate(msg) {
    update(s => ({
      ...s,
      online:       msg.online       ?? s.online,
      onlineCount:  msg.onlineCount  ?? s.onlineCount,
      viewing:      msg.viewing      ?? s.viewing,
      viewingCount: msg.viewingCount ?? s.viewingCount,
      ready:        true,
    }));
  }

  function _applyUpdate(msg) {
    const newOnline  = msg.online  ?? [];
    const newViewing = msg.viewing ?? [];

    const current    = get(store);
    const prevOnline  = current.online  ?? [];
    const prevViewing = current.viewing ?? [];

    const onlineShrunk  = newOnline.length  < prevOnline.length;
    const viewingShrunk = newViewing.length < prevViewing.length;

    if (onlineShrunk || viewingShrunk) {
      // Кто-то пропал — держим дебаунс, вдруг он переподключается
      clearTimeout(_disappearTimer);
      _pendingUpdate = msg;

      // Сразу добавляем новых юзеров (без задержки), но не убираем старых
      const onlineIds  = new Set(newOnline.map(u => u.user_id));
      const viewingIds = new Set(newViewing.map(u => u.user_id));

      // Мёрджим: старые остаются пока не истечёт таймер, новые добавляются сразу
      const mergedOnline  = [...prevOnline];
      const mergedViewing = [...prevViewing];

      newOnline.forEach(u => {
        if (!mergedOnline.find(o => o.user_id === u.user_id)) mergedOnline.push(u);
      });
      newViewing.forEach(u => {
        if (!mergedViewing.find(o => o.user_id === u.user_id)) mergedViewing.push(u);
      });

      update(s => ({
        ...s,
        online:       mergedOnline,
        onlineCount:  Math.max(msg.onlineCount ?? 0, mergedOnline.length),
        viewing:      mergedViewing,
        viewingCount: Math.max(msg.viewingCount ?? 0, mergedViewing.length),
        ready:        true,
      }));

      // Через DISAPPEAR_DELAY применяем реальное состояние
      _disappearTimer = setTimeout(() => {
        if (_pendingUpdate) {
          _commitUpdate(_pendingUpdate);
          _pendingUpdate = null;
        }
      }, DISAPPEAR_DELAY);

    } else {
      // Кто-то пришёл или ничего не изменилось — применяем мгновенно
      clearTimeout(_disappearTimer);
      _pendingUpdate = null;
      _commitUpdate(msg);
    }
  }

  // ── Heartbeat ─────────────────────────────────────────────────────────
  function _startHeartbeat() {
    _stopHeartbeat();
    _send({ type: 'heartbeat', entity_type: _entityType, entity_id: _entityId });
    _heartbeatId = setInterval(() => {
      _send({ type: 'heartbeat', entity_type: _entityType, entity_id: _entityId });
    }, HEARTBEAT_INTERVAL);
  }

  function _stopHeartbeat() {
    if (_heartbeatId) {
      clearInterval(_heartbeatId);
      _heartbeatId = null;
    }
  }

  // ── Подключение ───────────────────────────────────────────────────────
  function _connect() {
    if (!browser) return;
    if (_ws && (_ws.readyState === WebSocket.OPEN || _ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const token = getToken();
    const url   = wsUrl(token);

    try {
      _ws = new WebSocket(url);
    } catch {
      _scheduleReconnect();
      return;
    }

    _ws.onopen = () => {
      _reconnectCount = 0;
      update(s => ({ ...s, connected: true }));
      // Сразу регистрируем entity (важно после reconnect — entity не должен теряться)
      _startHeartbeat();
    };

    _ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'update') {
          _applyUpdate(msg);
        }
        // pong — просто подтверждение живости
      } catch {}
    };

    _ws.onclose = (event) => {
      _stopHeartbeat();
      update(s => ({ ...s, connected: false }));
      if (!_globalStopped && event.code !== 1000) {
        _scheduleReconnect();
      }
    };

    _ws.onerror = () => {
      // onclose сработает следом
    };
  }

  // ── Реконнект с экспоненциальной задержкой ────────────────────────────
  function _scheduleReconnect() {
    if (_globalStopped || _reconnectCount >= MAX_RECONNECT) return;
    const delay = Math.min(RECONNECT_BASE * Math.pow(1.5, _reconnectCount), 30_000);
    _reconnectCount++;
    _reconnectId = setTimeout(() => {
      if (!_globalStopped) _connect();
    }, delay);
  }

  // ── Видимость вкладки ─────────────────────────────────────────────────
  function _setupListeners() {
    if (!browser || _listenersAdded) return;
    _listenersAdded = true;

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        _stopHeartbeat();
      } else {
        if (!_ws || _ws.readyState !== WebSocket.OPEN) {
          _connect();
        } else {
          _send({ type: 'heartbeat', entity_type: _entityType, entity_id: _entityId });
          _startHeartbeat();
        }
      }
    });

    window.addEventListener('beforeunload', () => {
      // НЕ шлём leave — браузер режет WS до того как send отработает.
      // Сервер сам поймёт через onclose → grace period → TTL в Redis.
    });
  }

  // ── Публичное API ─────────────────────────────────────────────────────

  /**
   * Глобальный старт из +layout.svelte.
   * Подключается один раз и живёт весь сеанс.
   */
  function startGlobal() {
    if (!browser) return;
    _globalStopped = false;
    _globalStarted = true;
    _setupListeners();
    _connect();
  }

  /**
   * Вызывается из страниц с контентом (blog/[id], arts/[id], music/[id]).
   * Обновляет entity_type/entity_id — сервер узнает что ты сейчас смотришь.
   */
  function start(entityType = null, entityId = null) {
    if (!browser) return () => {};

    _entityType = entityType;
    _entityId   = entityId;

    if (_ws && _ws.readyState === WebSocket.OPEN) {
      _send({ type: 'heartbeat', entity_type: _entityType, entity_id: _entityId });
      _startHeartbeat();
    } else if (!_globalStarted) {
      _globalStopped = false;
      _setupListeners();
      _connect();
    }

    return () => {
      _entityType = null;
      _entityId   = null;

      // Сразу сбрасываем viewing локально
      update(s => ({ ...s, viewing: [], viewingCount: 0 }));

      // Сообщаем серверу что ушли с контента
      // Соединение НЕ закрываем — переиспользуем на следующей странице
      _send({ type: 'leave' });
    };
  }

  function stop() {
    _globalStopped = true;
    _globalStarted = false;
    _stopHeartbeat();
    clearTimeout(_disappearTimer);
    if (_reconnectId) { clearTimeout(_reconnectId); _reconnectId = null; }
    if (_ws) {
      if (_ws.readyState === WebSocket.OPEN) {
        _ws.close(1000, 'stopped');
      } else {
        _ws.close();
      }
      _ws = null;
    }
    update(s => ({ ...s, connected: false }));
  }

  /**
   * Переподключение с новым токеном (вызывается после логина/логаута).
   * Закрывает текущий WS и сразу открывает новый с актуальным токеном.
   */
  function reconnect() {
    if (!browser) return;
    _stopHeartbeat();
    clearTimeout(_reconnectId);
    _reconnectId = null;
    _reconnectCount = 0;
    if (_ws) {
      _ws.onclose = null; // отключаем авто-реконнект из старого onclose
      _ws.close();
      _ws = null;
    }
    _globalStopped = false;
    _connect();
  }

  return { subscribe, start, startGlobal, stop, reconnect };
}

export const presence = createPresenceStore();
