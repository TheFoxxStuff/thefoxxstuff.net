<script>
  import { page } from '$app/stores';
  import { auth, isAdmin } from '$lib/stores/auth.js';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { api, API_BASE } from '$lib/api';
  import { Copy, Home, Info, LogOut, Settings, Shield, Search, X } from 'lucide-svelte';

  const navItems = [
    { href: '/music', label: 'Music' },
    { href: '/blog', label: 'Blog' },
    { href: '/arts', label: 'Arts' },
    { href: '/links', label: 'Links' },
    { href: '/about', label: 'About' },
    { href: '/ads', label: 'ads' },
  ];

  const isActive = (href, pathname) => href === '/' ? pathname === '/' : pathname.startsWith(href);
  let navElement, indicatorElement, logoElement, contextMenuElement, userMenuElement;
  let activeIndex = $state(-1);
  let lastTime = performance.now();
  let contextMenuVisible = $state(false);
  let contextMenuPos = $state({ x: -9999, y: -9999 });
  let userMenuVisible = $state(false);
  let searchOpen = $state(false);
  let searchQuery = $state('');
  let isInitialLoad = true;

  function avatarUrl(path) { return path ? `${API_BASE}/upload/file/${path}` : null; }

  $effect(() => {
    const i = navItems.findIndex(item => isActive(item.href, $page.url.pathname));
    if (i !== activeIndex) {
      const prev = activeIndex; activeIndex = i;
      if (navElement && indicatorElement) {
        if (i === -1) hideInd();
        else if (isInitialLoad || prev === -1) showInstant(i);
        else moveInd(i, prev);
      }
    }
  });

  onMount(() => {
    if ($auth.token && $auth.user) {
      api.profile.me().then(p => auth.updateUser({ avatar_thumb: p.avatar_thumb, avatar_original: p.avatar_original, display_name: p.display_name })).catch(() => {});
    }
    const i = navItems.findIndex(item => isActive(item.href, $page.url.pathname));
    activeIndex = i;
    if (i !== -1 && navElement && indicatorElement) showInstant(i);
    requestAnimationFrame(() => { isInitialLoad = false; });

    const onResize = () => { if (navElement && indicatorElement && activeIndex !== -1) showInstant(activeIndex); };
    const onClick = (e) => {
      if (contextMenuElement && !contextMenuElement.contains(e.target)) contextMenuVisible = false;
      if (userMenuElement && !userMenuElement.contains(e.target)) userMenuVisible = false;
    };
    const onScroll = () => { contextMenuVisible = false; userMenuVisible = false; };
    window.addEventListener('resize', onResize);
    document.addEventListener('click', onClick);
    window.addEventListener('scroll', onScroll);
    return () => { window.removeEventListener('resize', onResize); document.removeEventListener('click', onClick); window.removeEventListener('scroll', onScroll); };
  });

  function hideInd() { if (!indicatorElement) return; indicatorElement.style.opacity = '0'; indicatorElement.style.transition = 'opacity 200ms ease-out'; }
  function showInstant(i) {
    if (!navElement || !indicatorElement) return;
    const items = navElement.querySelectorAll('.nav-item'), t = items[i]; if (!t) return;
    const nr = navElement.getBoundingClientRect(), tr = t.getBoundingClientRect(), x = tr.left - nr.left;
    indicatorElement.style.transition = 'none'; indicatorElement.style.width = tr.width+'px'; indicatorElement.style.transform = `translateX(${x}px) scaleX(1)`; indicatorElement.style.opacity = '1';
    requestAnimationFrame(() => requestAnimationFrame(() => { indicatorElement.style.transition = ''; }));
  }
  function moveInd(i, fi) {
    if (!navElement || !indicatorElement || i === -1) return;
    const items = navElement.querySelectorAll('.nav-item'), t = items[i]; if (!t) return;
    const nr = navElement.getBoundingClientRect(), tr = t.getBoundingClientRect(), x = tr.left - nr.left;
    indicatorElement.style.width = tr.width+'px'; indicatorElement.style.opacity = '1';
    if (fi === null || fi === -1) { indicatorElement.style.transition = 'transform 260ms cubic-bezier(.22,1,.36,1)'; indicatorElement.style.transform = `translateX(${x}px) scaleX(1)`; return; }
    const f = items[fi], fr = f.getBoundingClientRect(), fx = fr.left - nr.left, dist = Math.abs(x - fx), dir = x > fx ? 1 : -1;
    const now = performance.now(), dt = now - lastTime; lastTime = now;
    const sc = dist < 80 ? 1.02 : dist < 160 ? 1.05 : 1.08;
    indicatorElement.style.transformOrigin = dir === 1 ? 'left center' : 'right center';
    indicatorElement.style.transition = `transform 160ms cubic-bezier(.22,1,.36,1)`;
    indicatorElement.style.transform = `translateX(${x}px) scaleX(${sc})`;
    setTimeout(() => { indicatorElement.style.transition = 'transform 220ms cubic-bezier(.22,1.25,.36,1)'; indicatorElement.style.transform = `translateX(${x}px) scaleX(1)`; }, 160);
  }

  function logoDown() { if (logoElement) { logoElement.style.transition = 'transform 90ms cubic-bezier(.4,0,1,1)'; logoElement.style.transform = 'scale(.94)'; } }
  function logoUp() { if (logoElement) { logoElement.style.transition = 'transform 180ms cubic-bezier(.22,1.4,.36,1)'; logoElement.style.transform = 'scale(1.02)'; setTimeout(() => { logoElement.style.transition = 'transform 220ms cubic-bezier(.22,1,.36,1)'; logoElement.style.transform = 'scale(1)'; }, 120); } }
  function logoLeave() { if (logoElement) logoElement.style.transform = 'scale(1)'; }
  function logoCtx(e) { e.preventDefault(); let x=e.clientX, y=e.clientY; if(x+220>window.innerWidth)x=window.innerWidth-228; if(y+200>window.innerHeight)y=window.innerHeight-208; contextMenuPos={x,y}; contextMenuVisible=true; }
  function copyLogo() { navigator.clipboard.writeText(`<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M16 2L4 8v16l12 6 12-6V8L16 2z" fill="url(#lg)"/><path d="M10 12l6 3 6-3M16 15v9" stroke="#0a0a0a" stroke-width="2" stroke-linecap="round"/><defs><linearGradient id="lg" x1="4" y1="2" x2="28" y2="30"><stop stop-color="#4ade80"/><stop offset="1" stop-color="#22d3ee"/></linearGradient></defs></svg>`); contextMenuVisible=false; }
  function toggleUser(e) { e.stopPropagation(); userMenuVisible = !userMenuVisible; }
  function doLogout() { userMenuVisible = false; auth.logout(); goto('/'); }
  function doSearch(e) { if (e.key === 'Enter' && searchQuery.trim()) { searchOpen = false; goto(`/search?q=${encodeURIComponent(searchQuery.trim())}`); } }
</script>

<svelte:head>
  <style>
    .nav-item { position: relative; }
    .nav-item::after { content:''; position:absolute; inset:0; border-radius:0.5rem; background:rgba(255,255,255,0.04); opacity:0; transition:opacity 150ms; z-index:-1; }
    .nav-item:hover::after { opacity:1; }
    #logo { transform-origin:center; transition:transform 350ms cubic-bezier(.22,1,.36,1); }
    #nav-indicator { will-change:transform,width,opacity; transform-origin:left center; }
  </style>
</svelte:head>

<div class="mx-auto mt-[33px] w-full max-w-[828px] relative z-[9998]">
  <header class="w-full">
    <div class="mx-auto flex max-w-7xl items-center justify-between">
      <a href="/" bind:this={logoElement} id="logo" class="select-none flex items-center gap-[12px] cursor-pointer"
        onmousedown={logoDown} onmouseup={logoUp} onmouseleave={logoLeave} oncontextmenu={logoCtx}>
        <img src="/Logo.svg" alt="logo" class="h-[48px] w-auto">
      </a>

      <nav class="flex items-center gap-[5px] rounded-[8px] bg-[--header] px-[16px] py-[6px] backdrop-blur-[5px]">
        <div bind:this={navElement} id="nav" class="relative flex items-center gap-[5px]">
          <div bind:this={indicatorElement} id="nav-indicator" class="pointer-events-none absolute top-0 left-0 h-full rounded-[8px] bg-[--w8] shadow-inner transition-all duration-300"></div>
          {#each navItems as item, i}
            <a href={item.href} class="nav-item select-none text-sm leading-5 rounded-[8px] relative z-10 px-2 py-1.5 transition {isActive(item.href, $page.url.pathname) ? 'text-[--w]' : 'text-[--w60] hover:bg-[--w8] hover:text-[--w]'}">{item.label}</a>
          {/each}
        </div>
        <span class="mx-1 h-5 w-px bg-[--w18]"></span>

        <!-- Search -->
        {#if searchOpen}
          <div class="flex items-center gap-1">
            <input type="text" bind:value={searchQuery} onkeydown={doSearch} placeholder="Search..." autofocus
              class="w-32 bg-transparent border-b border-[--w18] text-sm text-[--w] outline-none px-1 py-1" />
            <button onclick={() => { searchOpen = false; searchQuery = ''; }} class="text-[--w60] hover:text-[--w]"><X size={14} /></button>
          </div>
        {:else}
          <button onclick={() => searchOpen = true} class="text-[--w60] hover:text-[--w] p-1.5 rounded-[8px] hover:bg-[--w8] transition" title="Search"><Search size={16} /></button>
        {/if}

        {#if $auth.user}
          <div class="relative" bind:this={userMenuElement}>
            <button onclick={toggleUser} class="select-none flex items-center gap-2 rounded-[8px] px-2 py-1 transition hover:bg-[--w8] cursor-pointer">
              {#if $auth.user.avatar_thumb}
                <img src={avatarUrl($auth.user.avatar_thumb)} alt="" class="w-6 h-6 rounded-full object-cover" />
              {:else}
                <div class="w-6 h-6 rounded-full bg-[--w12] flex items-center justify-center">
                  <span class="text-xs text-[--w60] font-medium">{($auth.user.display_name || $auth.user.username || '?')[0].toUpperCase()}</span>
                </div>
              {/if}
              <span class="text-sm text-[--w60] hidden sm:inline max-w-[80px] truncate">{$auth.user.display_name || $auth.user.username}</span>
              <svg class="w-3 h-3 text-[--w60] transition-transform {userMenuVisible ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
            </button>
            {#if userMenuVisible}
              <div class="absolute right-0 top-full mt-2 w-52 bg-[--select] backdrop-blur-xl border border-[--w12] rounded-xl p-1.5 shadow-2xl z-[10000]">
                <div class="px-3 py-2 border-b border-[--w8] mb-1.5">
                  <div class="text-sm text-[--w] font-medium truncate">{$auth.user.display_name || $auth.user.username}</div>
                  <div class="text-xs text-[--w60]">@{$auth.user.username}</div>
                </div>
                <a href="/profile" onclick={() => userMenuVisible = false} class="flex items-center gap-2.5 px-2.5 py-2 text-sm text-[--w60] rounded-[8px] transition hover:bg-[--w8] hover:text-[--w]"><Settings size={16} /> Profile</a>
                {#if isAdmin($auth.user)}
                  <a href="/admin" onclick={() => userMenuVisible = false} class="flex items-center gap-2.5 px-2.5 py-2 text-sm text-[--w60] rounded-[8px] transition hover:bg-[--w8] hover:text-[--w]"><Shield size={16} /> Admin</a>
                {/if}
                <div class="h-px bg-[--w8] my-1 mx-1"></div>
                <button onclick={doLogout} class="w-full flex items-center gap-2.5 px-2.5 py-2 text-sm text-red-400 rounded-[8px] transition hover:bg-red-500/10 hover:text-red-300 cursor-pointer"><LogOut size={16} /> Log Out</button>
              </div>
            {/if}
          </div>
        {:else}
          <a href="/auth/login" class="select-none text-sm leading-5 rounded-[8px] border border-[--w12] px-2 py-1.5 text-[--w60] transition hover:border-[--w18] hover:text-[--w]">Login</a>
        {/if}
      </nav>
    </div>
  </header>
</div>

{#if contextMenuVisible}
  <div bind:this={contextMenuElement} class="fixed z-[10001] min-w-[200px] bg-[--select] backdrop-blur-xl border border-[--w12] rounded-xl p-1.5 shadow-2xl select-none" style="left:{contextMenuPos.x}px;top:{contextMenuPos.y}px;">
    <button onclick={copyLogo} class="w-full flex items-center gap-2.5 px-2.5 py-2 text-sm text-[--w60] rounded-[8px] cursor-pointer transition hover:bg-[--w8] hover:text-[--w]"><Copy size={16} /> Copy Logo SVG</button>
    <a href="/" onclick={() => contextMenuVisible = false} class="flex items-center gap-2.5 px-2.5 py-2 text-sm text-[--w60] rounded-[8px] transition hover:bg-[--w8] hover:text-[--w]"><Home size={16} /> Home</a>
    <a href="/about" onclick={() => contextMenuVisible = false} class="flex items-center gap-2.5 px-2.5 py-2 text-sm text-[--w60] rounded-[8px] transition hover:bg-[--w8] hover:text-[--w]"><Info size={16} /> About</a>
  </div>
{/if}
