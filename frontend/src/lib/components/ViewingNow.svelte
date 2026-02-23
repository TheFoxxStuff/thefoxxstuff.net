<script>
  /**
   * ViewingNow — кто сейчас смотрит этот контент.
   * Рендерится только если есть хоть один пользователь.
   *
   * Props:
   *   users     — [{user_id, username, display_name, avatar_thumb, role}]
   *   count     — число просматривающих
   *   entityType — 'music' | 'blog' | 'arts'
   */
  import { API_BASE } from '$lib/api';

  let { users = [], count = 0, entityType = 'music' } = $props();

  const MAX_AVATARS = 5;
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

  const label = $derived(
    count === 1 ? 'person is viewing this' : 'people are viewing this'
  );
</script>

{#if count > 0}
  <div class="flex items-center gap-2.5 text-sm text-[--w50]">
    <!-- Живая точка -->
    <span class="relative flex items-center justify-center w-2 h-2 flex-shrink-0">
      <span class="absolute w-full h-full rounded-full bg-accent-green animate-ping opacity-60"></span>
      <span class="w-1.5 h-1.5 rounded-full bg-accent-green relative"></span>
    </span>

    <!-- Аватарки стопкой -->
    <div class="flex items-center">
      {#each visible as user, i}
        <a
          href="/profile/{user.username}"
          title="{user.display_name || user.username}"
          class="relative block rounded-full ring-1 ring-[#080808] hover:z-10 hover:scale-110 transition-transform"
          style="margin-left: {i === 0 ? 0 : -6}px; z-index: {visible.length - i};"
        >
          {#if avUrl(user.avatar_thumb)}
            <img
              src={avUrl(user.avatar_thumb)}
              alt={user.display_name || user.username}
              class="w-6 h-6 rounded-full object-cover"
            />
          {:else}
            <div
              class="w-6 h-6 rounded-full flex items-center justify-center text-[9px] font-bold text-black"
              style="background: hsl({hue(user.username)}, 60%, 55%);"
            >
              {(user.display_name || user.username || '?')[0].toUpperCase()}
            </div>
          {/if}
        </a>
      {/each}
      {#if rest > 0}
        <div
          class="w-6 h-6 rounded-full bg-[--w8] ring-1 ring-[#080808] flex items-center justify-center text-[9px] text-[--w50]"
          style="margin-left: -6px;"
        >
          +{rest}
        </div>
      {/if}
    </div>

    <!-- Текст -->
    <span>
      {#if count === 1}
        <a href="/profile/{users[0].username}" class="text-[--w70] hover:text-accent-green transition-colors font-medium">
          {users[0].display_name || users[0].username}
        </a>
        {' '}is viewing this
      {:else}
        <span class="text-[--w70] font-medium">{count}</span> {label}
      {/if}
    </span>
  </div>
{/if}
