<script>
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { auth, isAdmin } from '$lib/stores/auth.js';
  let { children } = $props();

  const navItems = [
    { href: '/admin',           label: 'Dashboard', short: 'Dash' },
    { href: '/admin/banner',    label: 'Banner',    short: 'Banner' },
    { href: '/admin/music',     label: 'Music',     short: 'Music' },
    { href: '/admin/blog',      label: 'Blog',      short: 'Blog' },
    { href: '/admin/arts',      label: 'Arts',      short: 'Arts' },
    { href: '/admin/links',     label: 'Links',     short: 'Links' },
    { href: '/admin/users',     label: 'Users',     short: 'Users' },
    { href: '/admin/media',     label: 'Media',     short: 'Media' },
    { href: '/admin/views-map', label: 'Views Map', short: 'Map' },
  ];

  const isActive = (href) =>
    href === '/admin'
      ? $page.url.pathname === '/admin'
      : $page.url.pathname.startsWith(href);

  onMount(() => {
    if (!$auth.user || !isAdmin($auth.user)) goto('/auth/login');
  });
</script>

{#if $auth.user && isAdmin($auth.user)}
<div class="admin-root">

  <!-- Admin top bar -->
  <div class="admin-bar-wrap">
    <div class="admin-bar">

      <div class="admin-bar-left">
        <a href="/" class="admin-back">
          <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
          Site
        </a>
        <span class="admin-badge">ADMIN</span>
      </div>

      <nav class="admin-nav">
        {#each navItems as item}
          <a
            href={item.href}
            class="admin-nav-item {isActive(item.href) ? 'active' : ''}"
          >
            <span class="full">{item.label}</span>
            <span class="short">{item.short}</span>
          </a>
        {/each}
      </nav>

      <div class="admin-bar-right">
        <span class="admin-user">{$auth.user?.display_name || $auth.user?.username}</span>
      </div>

    </div>
  </div>

  <!-- Content -->
  <main class="admin-main">
    <div class="admin-container">
      {@render children()}
    </div>
  </main>

</div>
{/if}

<style>
  .admin-root {
    min-height: 100vh;
    background: var(--bg);
  }

  /* ── Sticky top bar ── */
  .admin-bar-wrap {
    position: sticky;
    top: 0;
    z-index: 200;
    background: rgba(6,6,6,0.88);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-bottom: 1px solid rgba(255,255,255,0.07);
  }

  .admin-bar {
    max-width: 828px;
    margin: 0 auto;
    padding: 0 16px;
    height: 50px;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  /* ── Left ── */
  .admin-bar-left {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }

  .admin-back {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 13px;
    color: rgba(255,255,255,0.40);
    text-decoration: none;
    padding: 5px 9px;
    border-radius: 7px;
    transition: background 0.12s, color 0.12s;
    line-height: 1;
  }
  .admin-back:hover {
    background: rgba(255,255,255,0.07);
    color: rgba(255,255,255,0.85);
  }

  .admin-badge {
    font-family: DrukWideCyr, sans-serif;
    font-size: 10px;
    letter-spacing: 0.07em;
    color: #4ade80;
    background: rgba(74,222,128,0.08);
    border: 1px solid rgba(74,222,128,0.18);
    padding: 3px 7px;
    border-radius: 5px;
    line-height: 1.4;
  }

  /* ── Nav ── */
  .admin-nav {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 2px;
    overflow-x: auto;
    scrollbar-width: none;
  }
  .admin-nav::-webkit-scrollbar { display: none; }

  .admin-nav-item {
    display: inline-flex;
    align-items: center;
    flex-shrink: 0;
    padding: 5px 10px;
    border-radius: 7px;
    font-size: 13px;
    font-weight: 500;
    color: rgba(255,255,255,0.45);
    text-decoration: none;
    transition: background 0.12s, color 0.12s;
    white-space: nowrap;
    line-height: 1;
  }
  .admin-nav-item:hover {
    background: rgba(255,255,255,0.07);
    color: rgba(255,255,255,0.9);
  }
  .admin-nav-item.active {
    background: rgba(255,255,255,0.10);
    color: #ffffff;
  }

  /* responsive label switching */
  .admin-nav-item :global(.short) { display: none; }
  @media (max-width: 860px) {
    .admin-nav-item :global(.full) { display: none; }
    .admin-nav-item :global(.short) { display: inline; }
  }

  /* ── Right ── */
  .admin-bar-right {
    flex-shrink: 0;
  }
  .admin-user {
    font-size: 12px;
    color: rgba(255,255,255,0.28);
    max-width: 90px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  /* ── Content ── */
  .admin-main {
    padding: 32px 0 80px;
  }
  .admin-container {
    max-width: 828px;
    margin: 0 auto;
    padding: 0 16px;
  }

  @media (max-width: 600px) {
    .admin-bar { gap: 8px; padding: 0 12px; }
    .admin-badge, .admin-user { display: none; }
  }
</style>
