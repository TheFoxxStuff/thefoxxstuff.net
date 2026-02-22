<script>
  import { SEO } from "$lib/components";
  import { canonicalUrl } from "$lib/seo.js";
  import { api, API_BASE } from '$lib/api';
  import { auth } from '$lib/stores/auth.js';
  import { Shield, Trash2, User } from 'lucide-svelte';

  let { data: pageData } = $props();
  let users = $state(pageData.users);

  const loadUsers = async () => { users = await api.auth.users().catch(() => users); };
  const updateRole = async (userId, role) => {
    try { await api.auth.updateRole(userId, role); await loadUsers(); }
    catch (err) { alert(err.message); }
  };
  const deleteUser = async (userId) => {
    if (!confirm('Delete this user?')) return;
    try { await api.auth.deleteUser(userId); await loadUsers(); }
    catch (err) { alert(err.message); }
  };

  function avatarUrl(path) {
    return path ? `${API_BASE}/upload/file/${path}` : null;
  }

  function formatDate(d) {
    if (!d) return '—';
    return new Date(d).toLocaleString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  }

  // generate a deterministic hue from username for avatar placeholder
  function nameHue(name) {
    let h = 0;
    for (let i = 0; i < (name||'').length; i++) h = (h * 31 + name.charCodeAt(i)) % 360;
    return h;
  }

  function initials(user) {
    const n = user.display_name || user.username || '?';
    return n.slice(0, 2).toUpperCase();
  }
</script>

<SEO titleFull="Users — Admin" noindex={true} url={canonicalUrl("/admin")} />

<div>
  <div class="flex items-center justify-between mb-8">
    <h1 class="font-display text-[24px] tracking-wide">Users</h1>
    <span class="count-badge">{users.length} total</span>
  </div>

    <div class="users-list">
      {#each users as user}
        {@const isMe = user._id === $auth.user?._id}
        {@const isAdm = user.role === 'admin'}
        {@const hue = nameHue(user.username)}
        {@const thumb = avatarUrl(user.avatar_thumb)}

        <div class="user-card {isMe ? 'is-me' : ''}">

          <!-- Avatar -->
          <div class="avatar-wrap">
            {#if thumb}
              <img src={thumb} alt="" class="avatar-img" />
            {:else}
              <div class="avatar-placeholder" style="--hue:{hue}">
                {initials(user)}
              </div>
            {/if}
            {#if isAdm}
              <div class="avatar-admin-ring" title="Admin"></div>
            {/if}
          </div>

          <!-- Info -->
          <div class="user-info">
            <div class="user-name-row">
              <span class="user-name">{user.display_name || user.username}</span>
              {#if user.display_name && user.display_name !== user.username}
                <span class="user-handle">@{user.username}</span>
              {/if}
              {#if isAdm}
                <span class="role-admin"><Shield size={10} /> ADMIN</span>
              {/if}
              {#if isMe}
                <span class="role-you">you</span>
              {/if}
            </div>
            <div class="user-meta">
              <span class="meta-email">{user.email}</span>
              <span class="meta-sep">·</span>
              <span class="meta-date" title="Joined">Joined {formatDate(user.created_at)}</span>
              {#if user.last_login}
                <span class="meta-sep">·</span>
                <span class="meta-date" title="Last login">Last seen {formatDate(user.last_login)}</span>
              {/if}
            </div>
          </div>

          <!-- Actions -->
          {#if !isMe}
            <div class="user-actions">
              <div class="role-select-wrap">
                <select
                  onchange={(e) => updateRole(user._id, e.target.value)}
                  value={user.role}
                  class="role-select"
                >
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <button
                onclick={() => deleteUser(user._id)}
                class="delete-btn"
                title="Delete user"
              >
                <Trash2 size={14} />
              </button>
            </div>
          {/if}

        </div>
      {/each}
    </div>
</div>

<style>
  /* ── Header count ── */
  .count-badge {
    font-size: 13px;
    color: var(--w60);
    background: var(--w5);
    border: 1px solid var(--w8);
    padding: 4px 12px;
    border-radius: 20px;
  }

  /* ── List ── */
  .users-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  /* ── Card ── */
  .user-card {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 14px 16px;
    background: var(--w5);
    border: 1px solid var(--w8);
    border-radius: 12px;
    transition: border-color 0.15s, background 0.15s;
  }
  .user-card:hover {
    border-color: var(--w12);
    background: var(--w8);
  }
  .user-card.is-me {
    border-color: rgba(74,222,128,0.2);
    background: rgba(74,222,128,0.03);
  }

  /* ── Avatar ── */
  .avatar-wrap {
    position: relative;
    flex-shrink: 0;
  }
  .avatar-img,
  .avatar-placeholder {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .avatar-img {
    object-fit: cover;
    border: 2px solid var(--w8);
  }
  .avatar-placeholder {
    background: hsl(var(--hue), 45%, 22%);
    border: 2px solid hsl(var(--hue), 45%, 30%);
    font-size: 15px;
    font-weight: 700;
    color: hsl(var(--hue), 60%, 75%);
    letter-spacing: 0.02em;
    font-family: DrukWideCyr, sans-serif;
  }
  .avatar-admin-ring {
    position: absolute;
    inset: -3px;
    border-radius: 50%;
    border: 2px solid #4ade80;
    pointer-events: none;
  }

  /* ── Info ── */
  .user-info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 5px;
  }
  .user-name-row {
    display: flex;
    align-items: center;
    gap: 7px;
    flex-wrap: wrap;
  }
  .user-name {
    font-size: 15px;
    font-weight: 600;
    color: var(--w);
    line-height: 1;
  }
  .user-handle {
    font-size: 13px;
    color: var(--w30);
    line-height: 1;
  }
  .role-admin {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    font-family: DrukWideCyr, sans-serif;
    font-size: 10px;
    letter-spacing: 0.06em;
    color: #4ade80;
    background: rgba(74,222,128,0.1);
    border: 1px solid rgba(74,222,128,0.2);
    padding: 2px 7px;
    border-radius: 4px;
    line-height: 1.4;
  }
  .role-you {
    font-size: 12px;
    color: var(--w30);
    line-height: 1;
  }
  .user-meta {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
  }
  .meta-email {
    font-size: 13px;
    color: var(--w60);
  }
  .meta-sep {
    font-size: 12px;
    color: var(--w18);
  }
  .meta-date {
    font-size: 12px;
    color: var(--w30);
    font-variant-numeric: tabular-nums;
  }

  /* ── Actions ── */
  .user-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }
  .role-select-wrap {
    position: relative;
  }
  .role-select {
    appearance: none;
    -webkit-appearance: none;
    background: var(--w8);
    border: 1px solid var(--w12);
    color: var(--w60);
    font-size: 13px;
    padding: 6px 28px 6px 10px;
    border-radius: 8px;
    cursor: pointer;
    outline: none;
    font-family: inherit;
    transition: border-color 0.12s, color 0.12s;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='rgba(255,255,255,0.3)' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 8px center;
  }
  .role-select:hover {
    border-color: var(--w18);
    color: var(--w);
  }
  .role-select option {
    background: #1a1a1a;
    color: #fff;
  }

  .delete-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 8px;
    border: 1px solid transparent;
    background: transparent;
    color: var(--w30);
    cursor: pointer;
    transition: background 0.12s, color 0.12s, border-color 0.12s;
  }
  .delete-btn:hover {
    background: rgba(239,68,68,0.1);
    border-color: rgba(239,68,68,0.2);
    color: #ef4444;
  }

  /* ── Mobile ── */
  @media (max-width: 600px) {
    .user-card { gap: 12px; padding: 12px; }
    .meta-date { display: none; }
    .meta-sep:last-of-type { display: none; }
  }
</style>
