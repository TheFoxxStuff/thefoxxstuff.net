/**
 * Presence store — WebSocket + Redis Pub/Sub.
 *
 * Принцип работы:
 *   - Одно постоянное WS-соединение на всё время пребывания на сайте
 *   - Запускается из +layout.svelte → работает на каждой странице
 *   - Отдельные страницы вызывают presence.start('blog', id) для "is here"
 *   - Сервер пушит обновления мгновенно через Redis Pub/Sub — polling убран
 *   - Heartbeat раз в 30 сек держит TTL в Redis и сообщает текущую страницу
 *
 * Клиент → сервер:
 *   { type: "heartbeat", entity_type: "blog", entity_id: "abc" }
 *   { type: "ping" }
 *
 * Сервер → клиент:
 *   { type: "update", online: [...], onlineCount: N, viewing: [...], viewingCount: N }
 *   { type: "pong" }
 */

import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';

const HEARTBEAT_INTERVAL = 30_000;  // 30 сек — держит TTL в Redis
const RECONNECT_BASE     = 2_000;   // базовая задержка реконнекта
const MAX_RECONNECT      = 12;      // макс. попыток до паузы

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
  let _globalStarted  = false;
  let _listenersAdded = false;

  // ── Отправить если соединение открыто ────────────────────────────────
  function _send(msg) {
    if (_ws && _ws.readyState === WebSocket.OPEN) {
      _ws.send(JSON.stringify(msg));
    }
  }

  // ── Heartbeat — держим TTL в Redis и сообщаем текущую страницу ───────
  function _startHeartbeat() {
    _stopHeartbeat();
    // Отправляем сразу
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
        // pong — просто подтверждение живости, ничего не делаем
      } catch {}
    };

    _ws.onclose = (event) => {
      _stopHeartbeat();
      update(s => ({ ...s, connected: false }));
      // Переподключаемся кроме случаев: явное закрытие или сказали stop()
      if (!_globalStopped && event.code !== 1000) {
        _scheduleReconnect();
      }
    };

    _ws.onerror = () => {
      // onclose сработает следом — там делаем реконнект
    };
  }

  let _globalStopped = false;

  // ── Экспоненциальный реконнект ────────────────────────────────────────
  function _scheduleReconnect() {
    if (_globalStopped || _reconnectCount >= MAX_RECONNECT) return;
    const delay = Math.min(RECONNECT_BASE * Math.pow(1.5, _reconnectCount), 30_000);
    _reconnectCount++;
    _reconnectId = setTimeout(() => {
      if (!_globalStopped) _connect();
    }, delay);
  }

  // ── Слушаем видимость вкладки ─────────────────────────────────────────
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
      // Уведомляем сервер немедленно (sendBeacon не нужен — WS onclose работает быстро)
      _send({ type: 'leave' });
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
   * Вызывается из отдельных страниц с контентом (blog/[id], arts/[id], music/[id]).
   * Обновляет entity_type/entity_id — сервер узнает что ты сейчас смотришь.
   * Возвращает cleanup-функцию для onMount.
   */
  function start(entityType = null, entityId = null) {
    if (!browser) return () => {};

    _entityType = entityType;
    _entityId   = entityId;

    // Если соединение уже открыто — сразу шлём heartbeat с новой страницей
    if (_ws && _ws.readyState === WebSocket.OPEN) {
      _send({ type: 'heartbeat', entity_type: _entityType, entity_id: _entityId });
      _startHeartbeat(); // перезапускаем таймер чтобы интервал отсчитывался заново
    } else if (!_globalStarted) {
      // Если layout ещё не подключился (edge-case) — подключаемся сами
      _globalStopped = false;
      _setupListeners();
      _connect();
    }

    // Cleanup при уходе со страницы
    return () => {
      // Сбрасываем entity — пользователь больше не смотрит этот контент
      _entityType = null;
      _entityId   = null;

      // Обнуляем viewing в сторе сразу, не ждём следующего push
      update(s => ({ ...s, viewing: [], viewingCount: 0 }));

      // Сервер узнает через следующий heartbeat (entity_type=null)
      _send({ type: 'heartbeat', entity_type: null, entity_id: null });
    };
  }

  function stop() {
    _globalStopped = true;
    _globalStarted = false;
    _stopHeartbeat();
    if (_reconnectId) { clearTimeout(_reconnectId); _reconnectId = null; }
    if (_ws) {
      if (_ws.readyState === WebSocket.OPEN) {
        _send({ type: 'leave' });
        _ws.close(1000, 'stopped');
      } else {
        _ws.close();
      }
      _ws = null;
    }
    update(s => ({ ...s, connected: false }));
  }

  return { subscribe, start, startGlobal, stop };
}

export const presence = createPresenceStore();
