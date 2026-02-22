<script>
  import { page } from '$app/stores';

  const NAV = [
    { href: '/', label: 'Home', icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>` },
    { href: '/music', label: 'Music', icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>` },
    { href: '/arts', label: 'Art', icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8.56 2.75c4.37 6.03 6.02 9.42 8.03 17.72m2.54-15.38c-3.72 4.35-8.94 5.66-16.88 5.85m19.5 1.9c-3.5-.93-6.63-.82-8.94 0-2.58.92-5.01 2.86-7.44 6.32"/></svg>` },
    { href: '/blog', label: 'Blog', icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/></svg>` },
    { href: '/about', label: 'About', icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>` },
  ];

  const isActive = (href) => href === '/' ? $page.url.pathname === '/' : $page.url.pathname.startsWith(href);
</script>

<!-- Mobile bottom navigation — only visible on small screens -->
<nav class="fixed bottom-0 left-0 right-0 z-[9998] md:hidden bg-[rgba(6,6,6,0.95)] backdrop-blur-xl border-t border-[--w8]">
  <div class="flex items-center justify-around px-2 py-1 safe-area-pb">
    {#each NAV as item}
      <a
        href={item.href}
        class="flex flex-col items-center gap-0.5 px-3 py-2 rounded-xl transition-all min-w-0 flex-1
          {isActive(item.href) ? 'text-[--green]' : 'text-[--w60]'}"
      >
        <span class="w-5 h-5 flex-shrink-0">{@html item.icon}</span>
        <span class="text-[10px] font-medium truncate">{item.label}</span>
        {#if isActive(item.href)}
          <span class="w-1 h-1 rounded-full bg-[--green]"></span>
        {:else}
          <span class="w-1 h-1"></span>
        {/if}
      </a>
    {/each}
  </div>
</nav>

<style>
  .safe-area-pb {
    padding-bottom: max(8px, env(safe-area-inset-bottom));
  }
</style>
