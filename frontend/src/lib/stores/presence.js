/**
 * Presence store — WebSocket + Redis pub/sub.
 *
 * Одно постоянное WS соединение вместо HTTP polling.
 * Сервер пушит обновления мгновенно при любом изменении.
 * Heartbeat идёт через то же соединение — не создаёт HTTP запросов.
 *
 * Сообщения клиент → сервер:
 *   { type: "heartbeat", entity_type: "blog", entity_id: "abc" }
 *   { type: "leave" }
 *   { type: "ping" }
 *
 * Сообщения сервер → клиент:
 *   { type: "update", online: [...], onlineCount: N, viewing: [...], viewingCount: N }
 *   { type: "pong" }
 */

import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';

const HEARTBEAT_INTERVAL = 30_000; // 30 сек
const RECONNECT_DELAY    = 3_000;  // 3 сек до переподключения
const MAX_RECONNECT      = 10;     // максимум попыток подряд

// ws:// или wss:// из API_BASE (http -> ws, https -> wss)
function wsUrl(token) {
  const base = API_BASE.replace(/^http/, 'ws');
  const url = `${base}/presence/ws`;
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
  const { subscribe, update } = writable({
    online:       [],
    onlineCount:  0,
    viewing:      [],
    viewingCount: 0,
    connected:    false,
    ready:        false,
  });

  let _ws             = null;
  let _heartbeatId    = null;
  let _reconnectId    = null;
  let _reconnectCount = 0;
  let _entityType     = null;
  let _entityId       = null;
  let _stopped        = false;
  let _listenersAdded = false;

  // ── Отправить сообщение если соединение открыто ───────────────────
  function _send(msg) {
    if (_ws && _ws.readyState === WebSocket.OPEN) {
      _ws.send(JSON.stringify(msg));
    }
  }

  // ── Heartbeat через WS ────────────────────────────────────────────
  function _startHeartbeat() {
    _stopHeartbeat();
    _heartbeatId = setInterval(() => {
      _send({
        type:        'heartbeat',
        entity_type: _entityType,
        entity_id:   _entityId,
      });
    }, HEARTBEAT_INTERVAL);
  }

  function _stopHeartbeat() {
    if (_heartbeatId) {
      clearInterval(_heartbeatId);
      _heartbeatId = null;
    }
  }

  // ── Подключение ───────────────────────────────────────────────────
  function _connect() {
    if (!browser || _stopped) return;
    if (_ws && (_ws.readyState === WebSocket.OPEN || _ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const token = getToken();
    const url = wsUrl(token);

    try {
      _ws = new WebSocket(url);
    } catch (e) {
      _scheduleReconnect();
      return;
    }

    _ws.onopen = () => {
      _reconnectCount = 0;

      update(s => ({ ...s, connected: true }));

      // Сразу шлём heartbeat с текущей страницей
      _send({
        type:        'heartbeat',
        entity_type: _entityType,
        entity_id:   _entityId,
      });

      _startHeartbeat();
    };

    _ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);

        if (msg.type === 'update') {
          update(s => ({
            ...s,
            online:       msg.online       ?? s.online,
            onlineCount:  msg.onlineCount  ?? s.onlineCount,
            viewing:      msg.viewing      ?? s.viewing,
            viewingCount: msg.viewingCount ?? s.viewingCount,
            ready:        true,
          }));
        }
        // pong — игнорируем, просто подтверждение живости
      } catch {}
    };

    _ws.onclose = (event) => {
      _stopHeartbeat();
      update(s => ({ ...s, connected: false }));

      // Не переподключаемся если сами закрыли (code 1000) или _stopped
      if (!_stopped && event.code !== 1000) {
        _scheduleReconnect();
      }
    };

    _ws.onerror = () => {
      // onclose вызовется после onerror автоматически
    };
  }

  // ── Переподключение с экспоненциальной задержкой ──────────────────
  function _scheduleReconnect() {
    if (_stopped || _reconnectCount >= MAX_RECONNECT) return;

    const delay = Math.min(RECONNECT_DELAY * Math.pow(1.5, _reconnectCount), 30_000);
    _reconnectCount++;

    _reconnectId = setTimeout(() => {
      if (!_stopped) _connect();
    }, delay);
  }

  // ── Закрытие соединения ───────────────────────────────────────────
  function _disconnect(clean = true) {
    _stopHeartbeat();
    if (_reconnectId) {
      clearTimeout(_reconnectId);
      _reconnectId = null;
    }
    if (_ws) {
      if (clean && _ws.readyState === WebSocket.OPEN) {
        _send({ type: 'leave' });
        _ws.close(1000, 'leaving');
      } else {
        _ws.close();
      }
      _ws = null;
    }
    update(s => ({ ...s, connected: false }));
  }

  // ── Восстановление при возврате на вкладку ────────────────────────
  function _setupListeners() {
    if (!browser || _listenersAdded) return;
    _listenersAdded = true;

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        // Вкладка скрыта — останавливаем heartbeat, но соединение держим
        _stopHeartbeat();
      } else {
        // Вернулись — переподключаемся если надо, шлём heartbeat сразу
        if (!_ws || _ws.readyState !== WebSocket.OPEN) {
          _connect();
        } else {
          _send({
            type:        'heartbeat',
            entity_type: _entityType,
            entity_id:   _entityId,
          });
          _startHeartbeat();
        }
      }
    });

    window.addEventListener('beforeunload', () => {
      _send({ type: 'leave' });
    });
  }

  // ── Публичное API ─────────────────────────────────────────────────

  function start(entityType = null, entityId = null) {
    if (!browser) return () => {};

    _stopped    = false;
    _entityType = entityType;
    _entityId   = entityId;

    _setupListeners();
    _connect();

    // Если уже подключены — обновляем страницу через heartbeat
    if (_ws && _ws.readyState === WebSocket.OPEN) {
      _send({
        type:        'heartbeat',
        entity_type: _entityType,
        entity_id:   _entityId,
      });
    }

    // Cleanup при навигации на другую страницу
    return () => {
      // Сообщаем серверу что ушли с этого контента
      if (entityType && entityId) {
        _send({ type: 'leave' });
      }
      _stopHeartbeat();
      // Соединение не закрываем — переиспользуем на следующей странице
    };
  }

  function startGlobal() {
    return start(null, null);
  }

  function stop() {
    _stopped = true;
    _disconnect(true);
  }

  return { subscribe, start, startGlobal, stop };
}

export const presence = createPresenceStore();
