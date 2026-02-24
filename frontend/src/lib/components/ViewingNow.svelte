<script>
  import { fly, fade } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import { API_BASE } from '$lib/api';

  let { users = [], count = 0, entityType = 'music' } = $props();

  const MAX_AVATARS = 6;
  const visible = $derived(users.slice(0, MAX_AVATARS));
  const rest    = $derived(Math.max(0, count - MAX_AVATARS));

  function avUrl(path) {
    return path ? `${API_BASE}/upload/file/${path}` : null;
  }

  function hue(name = '') {
    let h = 0;
    for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) % 360;
    return h;
  }
</script>

{#if count > 0}
  <div
    class="inline-flex items-center gap-3 px-3 py-2 rounded-xl bg-[--w5] border border-[--w8] text-sm"
    in:fly={{ y: 8, duration: 250 }}
    out:fade={{ duration: 200 }}
  >
    <!-- Живая точка -->
    <span class="relative flex-shrink-0 w-2 h-2">
      <span class="absolute inset-0 rounded-full bg-accent-green animate-ping opacity-50"></span>
      <span class="absolute inset-0.5 rounded-full bg-accent-green"></span>
    </span>

    <!-- Аватарки с анимацией -->
    <div class="flex items-center">
      {#each visible as user, i (user.user_id)}
        <a
          href="/profile/{user.username}"
          title="{user.display_name || user.username}"
          class="relative block rounded-full ring-2 ring-[--ring] hover:z-20 hover:scale-110 transition-transform duration-150"
          style="margin-left: {i === 0 ? 0 : -7}px; z-index: {MAX_AVATARS - i};"
          in:fly={{ x: -10, duration: 200, delay: i * 30 }}
          out:fade={{ duration: 150 }}
          animate:flip={{ duration: 200 }}
        >
          {#if avUrl(user.avatar_thumb)}
            <img
              src={avUrl(user.avatar_thumb)}
              alt={user.display_name || user.username}
              class="w-7 h-7 rounded-full object-cover"
            />
          {:else}
            <div
              class="w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-bold text-black select-none"
              style="background: hsl({hue(user.username)}, 60%, 55%);"
            >
              {(user.display_name || user.username || '?')[0].toUpperCase()}
            </div>
          {/if}
        </a>
      {/each}

      {#if rest > 0}
        <div
          class="w-7 h-7 rounded-full bg-[--w8] ring-2 ring-[--ring] flex items-center justify-center text-[9px] text-[--w50] font-medium"
          style="margin-left: -7px; z-index: 0;"
          in:fade={{ duration: 150 }}
        >
          +{rest}
        </div>
      {/if}
    </div>

    <!-- Текст -->
    <span class="text-[--w50] whitespace-nowrap">
      {#if count === 1}
        <a
          href="/profile/{users[0].username}"
          class="text-[--w80] font-medium hover:text-accent-green transition-colors"
        >
          {users[0].display_name || users[0].username}
        </a>
        <span> is here</span>
      {:else}
        <span class="text-[--w80] font-medium">{count}</span>
        <span> viewing</span>
      {/if}
    </span>
  </div>
{/if}
