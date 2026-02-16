<script>
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { auth, isAdmin } from '$lib/stores/auth.js';
  let { children } = $props();
  const navItems = [
    { href: '/admin', label: 'Dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
    { href: '/admin/banner', label: 'Banner', icon: 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01' },
    { href: '/admin/music', label: 'Music', icon: 'M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2z' },
    { href: '/admin/blog', label: 'Blog', icon: 'M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1' },
    { href: '/admin/arts', label: 'Arts', icon: 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586' },
    { href: '/admin/links', label: 'Links', icon: 'M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656' },
    { href: '/admin/users', label: 'Users', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1z' },
    { href: '/admin/media', label: 'Media', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10' },
    { href: '/admin/views-map', label: 'Views Map', icon: 'M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
  ];
  const isActive = (href) => href === '/admin' ? $page.url.pathname === '/admin' : $page.url.pathname.startsWith(href);
  onMount(() => { if (!$auth.user || !isAdmin($auth.user)) goto('/auth/login'); });
</script>
{#if $auth.user && isAdmin($auth.user)}
<div class="min-h-screen flex">
  <aside class="w-56 bg-dark-900 border-r border-dark-800 p-4 flex flex-col flex-shrink-0">
    <a href="/" class="flex items-center gap-2 mb-8">
      <svg class="h-8 w-auto" viewBox="0 0 32 32" fill="none"><path d="M16 2L4 8v16l12 6 12-6V8L16 2z" fill="url(#lg2)" /><defs><linearGradient id="lg2" x1="4" y1="2" x2="28" y2="30"><stop stop-color="#4ade80" /><stop offset="1" stop-color="#22d3ee" /></linearGradient></defs></svg>
      <span class="font-display text-xl">Admin</span>
    </a>
    <nav class="space-y-1 flex-1">
      {#each navItems as item}
        <a href={item.href} class="admin-link {isActive(item.href) ? 'admin-link-active' : ''}">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={item.icon} /></svg>
          {item.label}
        </a>
      {/each}
    </nav>
    <a href="/" class="admin-link mt-4 border-t border-dark-800 pt-4">← Back to site</a>
  </aside>
  <main class="flex-1 p-8 overflow-auto">
    <div class="max-w-5xl mx-auto">
      {@render children()}
    </div>
  </main>
</div>
{/if}
