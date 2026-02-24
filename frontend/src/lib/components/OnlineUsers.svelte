<script>
  import { fly, fade } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import { API_BASE } from '$lib/api';

  let { users = [], count = 0, compact = false, maxShow = 8 } = $props();

  const visible = $derived(users.slice(0, maxShow));
  const rest    = $derived(Math.max(0, count - maxShow));

  function avUrl(path) {
    return path ? `${API_BASE}/upload/file/${path}` : null;
  }

  function hue(name = '') {
    let h = 0;
    for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) % 360;
    return h;
  }
</script>

{#if compact}
  <!-- ── Compact: стопка аватарок ── -->
  <div class="flex items-center gap-2">
    <div class="flex items-center">
      {#each visible as user, i (user.user_id)}
        <a
          href="/profile/{user.username}"
          title="{user.display_name || user.username}"
          class="relative block rounded-full ring-2 ring-[--ring] hover:z-10 transition-transform hover:scale-110"
          style="margin-left: {i === 0 ? 0 : -8}px; z-index: {visible.length - i};"
          in:fly={{ x: -8, duration: 200 }}
          out:fade={{ duration: 150 }}
          animate:flip={{ duration: 200 }}
        >
          {#if avUrl(user.avatar_thumb)}
            <img src={avUrl(user.avatar_thumb)} alt={user.display_name || user.username} class="w-7 h-7 rounded-full object-cover" />
          {:else}
            <div
              class="w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-bold text-black"
              style="background: hsl({hue(user.username)}, 60%, 55%);"
            >
              {(user.display_name || user.username || '?')[0].toUpperCase()}
            </div>
          {/if}
        </a>
      {/each}
      {#if rest > 0}
        <div
          class="w-7 h-7 rounded-full bg-[--w8] ring-2 ring-[--ring] flex items-center justify-center text-[10px] text-[--w60] font-medium"
          style="margin-left: -8px;"
          in:fade={{ duration: 150 }}
        >
          +{rest}
        </div>
      {/if}
    </div>
    <span class="text-xs text-[--w40] flex items-center gap-1.5">
      <span class="w-1.5 h-1.5 rounded-full bg-accent-green animate-pulse inline-block"></span>
      {count} online
    </span>
  </div>

{:else}
  <!-- ── Full: список с именами ── -->
  <div class="space-y-0.5">
    {#each visible as user (user.user_id)}
      <a
        href="/profile/{user.username}"
        class="flex items-center gap-2.5 px-2 py-1.5 rounded-lg hover:bg-[--w5] transition-colors group"
        in:fly={{ x: -12, duration: 200 }}
        out:fly={{ x: 12, duration: 150 }}
        animate:flip={{ duration: 250 }}
      >
        {#if avUrl(user.avatar_thumb)}
          <img src={avUrl(user.avatar_thumb)} alt={user.display_name || user.username} class="w-8 h-8 rounded-full object-cover flex-shrink-0" />
        {:else}
          <div
            class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-black flex-shrink-0"
            style="background: hsl({hue(user.username)}, 60%, 55%);"
          >
            {(user.display_name || user.username || '?')[0].toUpperCase()}
          </div>
        {/if}
        <div class="flex-1 min-w-0">
          <div class="text-sm text-[--w] truncate group-hover:text-accent-green transition-colors">
            {user.display_name || user.username}
          </div>
          {#if user.display_name}
            <div class="text-xs text-[--w30] truncate">@{user.username}</div>
          {/if}
        </div>
        {#if user.role === 'admin'}
          <span class="text-[10px] text-accent-green/60 font-medium shrink-0">admin</span>
        {/if}
      </a>
    {/each}
    {#if rest > 0}
      <p class="text-xs text-[--w30] px-2 pt-1" in:fade={{ duration: 150 }}>+{rest} more</p>
    {/if}
  </div>
{/if}
