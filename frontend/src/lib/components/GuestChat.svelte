<script>
  import { onMount, onDestroy, tick } from 'svelte';
  import { auth } from '$lib/stores/auth.js';
  import { API_BASE } from '$lib/api';
  import { Send, MessageCircle, Users, Shield, ChevronDown } from 'lucide-svelte';

  let messages = $state([]);
  let inputText = $state('');
  let ws = $state(null);
  let connected = $state(false);
  let onlineCount = $state(0);
  let error = $state('');
  let messagesContainer;
  let isAtBottom = $state(true);
  let sending = $state(false);
  let collapsed = $state(false);

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
    if (mins < 1) return 'just now';
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
      const withinTime = prev && (new Date(msg.created_at) - new Date(prev.created_at)) < 300000;
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

  function connect() {
    const token = $auth?.token;
    const url = `${WS_BASE}/chat/ws${token ? `?token=${token}` : ''}`;
    try { ws = new WebSocket(url); } catch { return; }

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
    ws.onclose = () => {
      connected = false;
      setTimeout(() => { if (!ws || ws.readyState === WebSocket.CLOSED) connect(); }, 3000);
    };
    ws.onerror = () => { connected = false; };
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

  onMount(() => { connect(); });
  onDestroy(() => { if (ws) { ws.onclose = null; ws.close(); } });
</script>

<div class="rounded-[14px] overflow-hidden" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);">
  <!-- Header -->
  <button
    class="w-full flex items-center justify-between px-5 py-3.5 cursor-pointer hover:bg-[--w5] transition-colors select-none"
    onclick={() => collapsed = !collapsed}
    style="border-bottom: {collapsed ? 'none' : '1px solid rgba(255,255,255,0.06)'};"
  >
    <div class="flex items-center gap-2.5">
      <div class="w-7 h-7 rounded-[7px] flex items-center justify-center" style="background: rgba(115,238,7,0.1);">
        <MessageCircle size={14} style="color: #73EE07;" />
      </div>
      <span class="font-display text-[13px] tracking-wide text-[--w]">Live Chat</span>
      {#if messages.length > 0}
        <span class="text-[11px] px-1.5 py-[2px] rounded-full" style="background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.5);">{messages.length}</span>
      {/if}
    </div>
    <div class="flex items-center gap-3">
      <div class="flex items-center gap-1.5">
        <div class="w-1.5 h-1.5 rounded-full {connected ? 'bg-[--green]' : 'bg-red-500'}" style="box-shadow: {connected ? '0 0 6px rgba(115,238,7,0.5)' : 'none'};"></div>
        <div class="flex items-center gap-1" style="color: rgba(255,255,255,0.4);">
          <Users size={11} />
          <span class="text-[11px]">{onlineCount}</span>
        </div>
      </div>
      <ChevronDown size={15} style="color: rgba(255,255,255,0.4); transition: transform 200ms; transform: rotate({collapsed ? '-90deg' : '0deg'});" />
    </div>
  </button>

  {#if !collapsed}
    <!-- Messages -->
    <div
      bind:this={messagesContainer}
      onscroll={handleScroll}
      class="overflow-y-auto px-2 py-2 chat-scroll"
      style="height: 340px;"
    >
      {#if messages.length === 0}
        <div class="flex flex-col items-center justify-center h-full gap-3" style="color: rgba(255,255,255,0.2);">
          <MessageCircle size={28} />
          <span class="text-[13px]">No messages yet. Be the first!</span>
        </div>
      {:else}
        {#each grouped as group, gi}
          <div class="flex gap-3 px-3 py-2 rounded-[10px] hover:bg-[--w5] transition-colors group/msg">
            <!-- Avatar -->
            <div class="flex-shrink-0 mt-0.5">
              {#if group.avatar_thumb}
                <a href="/profile/{group.username}" class="block">
                  <img
                    src={getAvatarUrl(group.avatar_thumb)}
                    alt={group.username}
                    class="w-8 h-8 rounded-full object-cover"
                  />
                </a>
              {:else}
                <a href="/profile/{group.username}" class="w-8 h-8 rounded-full flex items-center justify-center text-[11px] font-bold uppercase block" style="background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.5);">
                  {group.username.charAt(0)}
                </a>
              {/if}
            </div>

            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-1.5 mb-[3px]">
                <a
                  href="/profile/{group.username}"
                  class="text-[13px] font-semibold hover:underline {group.role === 'admin' ? 'text-[--green]' : 'text-[--w]'}"
                >
                  {group.display_name || group.username}
                </a>
                {#if group.role === 'admin'}
                  <span class="inline-flex items-center gap-[3px] text-[9px] font-bold px-1.5 py-[1px] rounded-[4px]" style="background: rgba(115,238,7,0.1); color: #73EE07;">
                    <Shield size={8} />ADMIN
                  </span>
                {/if}
                <span class="text-[11px]" style="color: rgba(255,255,255,0.25);">{formatTime(group.created_at)}</span>
              </div>
              {#each group.messages as msg}
                <p class="text-[13px] leading-[1.45] break-words" style="color: rgba(255,255,255,0.65);">{msg.text}</p>
              {/each}
            </div>
          </div>
        {/each}
      {/if}
    </div>

    <!-- New messages scroll button -->
    {#if !isAtBottom && messages.length > 0}
      <div class="flex justify-center pb-1">
        <button
          onclick={scrollToBottom}
          class="flex items-center gap-1.5 text-[12px] px-3 py-1.5 rounded-full transition-all hover:bg-[--w8] animate-fade-in"
          style="background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.5);"
        >
          <ChevronDown size={12} />
          New messages
        </button>
      </div>
    {/if}

    <!-- Error -->
    {#if error}
      <div class="px-4 py-2 text-[12px] text-red-400 animate-fade-in" style="background: rgba(239,68,68,0.08);">{error}</div>
    {/if}

    <!-- Input -->
    <div class="px-3 py-3" style="border-top: 1px solid rgba(255,255,255,0.06);">
      {#if $auth?.token}
        <div class="flex items-center gap-2">
          <input
            type="text"
            class="flex-1 rounded-[10px] px-3 py-2 text-[13px] text-[--w] placeholder-[--w40] focus:outline-none transition-all"
            style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);"
            style:border-color={inputText ? 'rgba(115,238,7,0.3)' : undefined}
            placeholder="Type a message..."
            maxlength="500"
            bind:value={inputText}
            onkeydown={handleKeydown}
          />
          <button
            onclick={sendMessage}
            disabled={!inputText.trim() || sending}
            class="w-9 h-9 flex items-center justify-center rounded-[10px] transition-all hover:scale-105 active:scale-95 disabled:opacity-30"
            style="background: {inputText.trim() ? '#73EE07' : 'rgba(115,238,7,0.3)'}; color: black;"
          >
            <Send size={15} />
          </button>
        </div>
      {:else}
        <div class="text-center py-1.5">
          <a href="/auth/login" class="text-[13px] hover:underline" style="color: #73EE07;">Login to join the chat</a>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .chat-scroll::-webkit-scrollbar { width: 4px; }
  .chat-scroll::-webkit-scrollbar-track { background: transparent; }
  .chat-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 99px; }
  .chat-scroll::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.15); }
</style>
