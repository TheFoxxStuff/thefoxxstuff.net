<script>
  import { onMount, onDestroy, tick } from 'svelte';
  import { auth } from '$lib/stores/auth.js';
  import { API_BASE } from '$lib/api';
  import { Send, MessageCircle, Users, Shield } from 'lucide-svelte';

  let messages = $state([]);
  let inputText = $state('');
  let ws = $state(null);
  let connected = $state(false);
  let onlineCount = $state(0);
  let error = $state('');
  let messagesContainer = $state(null);
  let isAtBottom = $state(true);
  let sending = $state(false);

  // Таймер переподключения
  let reconnectTimer = null;
  // Флаг «пользователь закрыл вкладку / уничтожил компонент»
  let destroyed = false;

  const WS_BASE = API_BASE.replace('http', 'ws');

  function getAvatarUrl(path) {
    if (!path) return null;
    return `${API_BASE}/upload/file/${path}`;
  }

  function formatTime(isoStr) {
    const d = new Date(isoStr);
    const now = new Date();
    const diff = now - d;
    const mins = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    if (mins < 1) return 'now';
    if (mins < 60) return `${mins}m ago`;
    if (hours < 24) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' }) + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function groupMessages(msgs) {
    const groups = [];
    for (let i = 0; i < msgs.length; i++) {
      const msg = msgs[i];
      const prev = i > 0 ? msgs[i - 1] : null;
      const sameUser = prev && prev.username === msg.username;
      const withinTime = prev && (new Date(msg.created_at) - new Date(prev.created_at)) < 300_000;
      if (sameUser && withinTime) {
        groups[groups.length - 1].messages.push(msg);
      } else {
        groups.push({
          username: msg.username,
          display_name: msg.display_name,
          avatar_thumb: msg.avatar_thumb,
          role: msg.role,
          created_at: msg.created_at,
          messages: [msg],
        });
      }
    }
    return groups;
  }

  let grouped = $derived(groupMessages(messages));

  function scheduleReconnect() {
    if (destroyed) return;
    clearTimeout(reconnectTimer);
    reconnectTimer = setTimeout(() => {
      if (!destroyed && (!ws || ws.readyState === WebSocket.CLOSED)) connect();
    }, 3000);
  }

  function connect() {
    if (destroyed) return;
    const token = $auth?.token;
    const url = `${WS_BASE}/chat/ws${token ? `?token=${token}` : ''}`;
    try {
      ws = new WebSocket(url);
    } catch {
      scheduleReconnect();
      return;
    }

    ws.onopen = () => { connected = true; error = ''; };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'history') {
          messages = data.messages || [];
          tick().then(scrollToBottom);
        } else if (data.type === 'message') {
          messages = [...messages, data];
          if (isAtBottom) tick().then(scrollToBottom);
        } else if (data.type === 'online_count') {
          onlineCount = data.count;
        } else if (data.type === 'error') {
          error = data.text;
          setTimeout(() => error = '', 4000);
        }
      } catch {}
    };

    ws.onclose = () => { connected = false; scheduleReconnect(); };
    ws.onerror = () => { connected = false; };
  }

  function disconnect() {
    clearTimeout(reconnectTimer);
    if (ws) {
      ws.onclose = null; // отключаем авто-переподключение
      ws.close();
      ws = null;
    }
    connected = false;
  }

  function sendMessage() {
    if (!inputText.trim() || !ws || ws.readyState !== WebSocket.OPEN) return;
    if (!$auth?.token) {
      error = 'Please login to send messages';
      setTimeout(() => error = '', 3000);
      return;
    }
    ws.send(JSON.stringify({ type: 'message', text: inputText.trim() }));
    inputText = '';
  }

  function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  }

  function handleScroll() {
    if (!messagesContainer) return;
    const { scrollTop, scrollHeight, clientHeight } = messagesContainer;
    isAtBottom = scrollHeight - scrollTop - clientHeight < 40;
  }

  function scrollToBottom() {
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
      isAtBottom = true;
    }
  }

  function getRoleColor(role) {
    return role === 'admin' ? 'text-accent-green' : 'text-[--w]';
  }

  // Чат теперь всегда открыт — подключаемся сразу при монтировании.
  onMount(() => {
    connect();
  });

  onDestroy(() => {
    destroyed = true;
    disconnect();
  });
</script>

<section class="card overflow-hidden flex flex-col h-full">
  <!-- Header -->
  <div class="flex items-center justify-between px-4 py-3 border-b border-[--w8] select-none">
    <div class="flex items-center gap-2.5">
      <MessageCircle size={16} class="text-accent-green" />
      <span class="text-sm font-medium text-[--w60] uppercase tracking-wider">Guest Chat</span>
      <span class="text-xs text-[--w60] bg-[--w8] px-2 py-0.5 rounded-[8px]">{messages.length}</span>
    </div>
    <div class="flex items-center gap-1.5 text-xs text-[--w40]">
      <span class="w-2 h-2 rounded-full {connected ? 'bg-accent-green animate-pulse' : 'bg-accent-red'}"></span>
      <Users size={12} />
      {onlineCount}
    </div>
  </div>

  <!-- Messages Area -->
  <div
    bind:this={messagesContainer}
    onscroll={handleScroll}
    class="flex-1 min-h-[360px] overflow-y-auto px-2 py-2 space-y-0 chat-scroll"
  >
    {#if messages.length === 0}
      <div class="flex flex-col items-center justify-center h-full text-[--w30] text-sm gap-2">
        <MessageCircle size={32} />
        <span>{connected ? 'No messages yet. Start the conversation!' : 'Connecting...'}</span>
      </div>
    {:else}
      {#each grouped as group}
        <div class="flex gap-3 px-3 py-1.5 rounded-[8px] hover:bg-[--w5] transition group/msg">
          <!-- Avatar -->
          <div class="flex-shrink-0 mt-0.5">
            {#if group.avatar_thumb}
              <a href="/profile/{group.username}" class="block">
                <img
                  loading="lazy"
                  src={getAvatarUrl(group.avatar_thumb)}
                  alt={group.username}
                  class="w-9 h-9 rounded-full object-cover"
                />
              </a>
            {:else}
              <a href="/profile/{group.username}" class="block w-9 h-9 rounded-full bg-[--w8] flex items-center justify-center text-[--w50] text-xs font-bold uppercase">
                {group.username.charAt(0)}
              </a>
            {/if}
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0">
            <div class="flex items-baseline gap-2">
              <a href="/profile/{group.username}" class="font-medium text-sm {getRoleColor(group.role)} hover:underline">
                {group.display_name || group.username}
              </a>
              {#if group.role === 'admin'}
                <span class="inline-flex items-center gap-0.5 text-[10px] text-accent-green bg-accent-green/10 px-1.5 py-0 rounded">
                  <Shield size={9} />
                  ADMIN
                </span>
              {/if}
              <span class="text-[11px] text-[--w30]">{formatTime(group.created_at)}</span>
            </div>
            {#each group.messages as msg, idx}
              <div class="text-sm text-[--w60] leading-[1.4] {idx > 0 ? 'mt-0.5' : 'mt-0'} break-words">{msg.text}</div>
            {/each}
          </div>
        </div>
      {/each}
    {/if}

    {#if !isAtBottom && messages.length > 0}
      <button
        onclick={scrollToBottom}
        class="sticky bottom-2 left-1/2 -translate-x-1/2 bg-[--w8] border border-[--w12] text-xs text-[--w60] px-3 py-1 rounded-full hover:text-[--w] transition z-10"
      >
        ↓ New messages
      </button>
    {/if}
  </div>

  <!-- Error -->
  {#if error}
    <div class="px-4 py-1.5 text-xs text-accent-red bg-accent-red/10">{error}</div>
  {/if}

  <!-- Input Area -->
  <div class="px-3 py-2.5 border-t border-[--w8]">
    {#if $auth?.token}
      <div class="flex items-center gap-2">
        <input
          type="text"
          class="flex-1 bg-[--w5] border border-[--w8] rounded-[8px] px-3 py-2 text-sm text-[--w] placeholder-[--w30] focus:outline-none focus:border-[--w] transition"
          placeholder="Type a message..."
          maxlength="500"
          bind:value={inputText}
          onkeydown={handleKeydown}
        />
        <button
          onclick={sendMessage}
          disabled={!inputText.trim() || sending}
          class="w-9 h-9 flex items-center justify-center rounded-[8px] bg-accent-green text-dark-950 hover:bg-accent-green/90 disabled:opacity-30 transition shrink-0"
        >
          <Send size={16} />
        </button>
      </div>
    {:else}
      <div class="text-center py-2">
        <a href="/auth/login" class="text-sm text-accent-green hover:underline">Login to send messages</a>
      </div>
    {/if}
  </div>
</section>

<style>
  .chat-scroll::-webkit-scrollbar { width: 6px; }
  .chat-scroll::-webkit-scrollbar-track { background: transparent; }
  .chat-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
  .chat-scroll::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
</style>
