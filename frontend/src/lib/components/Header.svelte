<script>
  import { page } from '$app/stores';
  import { auth, isAdmin } from '$lib/stores/auth.js';
  import { onMount, tick } from 'svelte';
  import { goto } from '$app/navigation';
  import { api, API_BASE } from '$lib/api';
  import { Copy, Home, Info, LogOut, Settings, Shield, Search, X } from 'lucide-svelte';

  const navItems = [
    { href: '/music', label: 'Music' },
    { href: '/blog', label: 'Blog' },
    { href: '/arts', label: 'Arts' },
    { href: '/links', label: 'Links' },
    { href: '/about', label: 'About' },
  ];

  const isActive = (href, pathname) => href === '/' ? pathname === '/' : pathname.startsWith(href);

  let navElement, indicatorElement, logoElement, contextMenuElement, userMenuElement, searchInputElement;
  let searchContainerElement;
  let userMenuTriggerElement;
  let navWrapperElement; // НОВОЕ: ref для обёртки позиционирования меню
  
  let activeIndex = $state(-1);
  let lastTime = performance.now();
  let contextMenuVisible = $state(false);
  let contextMenuPos = $state({ x: -9999, y: -9999 });
  let userMenuVisible = $state(false);
  let searchOpen = $state(false);
  let searchQuery = $state('');
  let authChecking = $state(true);

  let indicatorReady = false;
  let lastActiveIndex = -1;

  let isSearchPage = $derived(
    $page.url.pathname === '/search' && !!$page.url.searchParams.get('q')
  );

  let blurTimeout = null;

  function avatarUrl(path) { return path ? `${API_BASE}/upload/file/${path}` : null; }

  function hideInd() {
    if (!indicatorElement) return;
    indicatorElement.style.transition = 'opacity 200ms ease-out';
    indicatorElement.style.opacity = '0';
  }

  function showInstant(i) {
    if (!navElement || !indicatorElement) return;
    const items = navElement.querySelectorAll('.nav-item');
    const t = items[i];
    if (!t) return;
    const nr = navElement.getBoundingClientRect();
    const tr = t.getBoundingClientRect();
    const x = tr.left - nr.left;

    indicatorElement.style.transition = 'none';
    indicatorElement.style.width = tr.width + 'px';
    indicatorElement.style.transform = `translateX(${x}px) scaleX(1)`;
    indicatorElement.style.opacity = '1';

    requestAnimationFrame(() => requestAnimationFrame(() => {
      if (indicatorElement) indicatorElement.style.transition = '';
      indicatorReady = true;
      lastActiveIndex = i;
    }));
  }

  function moveInd(toIdx, fromIdx) {
    if (!navElement || !indicatorElement || toIdx === -1) return;
    const items = navElement.querySelectorAll('.nav-item');
    const to = items[toIdx];
    if (!to) return;
    const nr = navElement.getBoundingClientRect();
    const toR = to.getBoundingClientRect();
    const x = toR.left - nr.left;

    indicatorElement.style.width = toR.width + 'px';
    indicatorElement.style.opacity = '1';

    if (fromIdx === -1 || fromIdx === null) {
      indicatorElement.style.transition = 'transform 260ms cubic-bezier(.22,1,.36,1)';
      indicatorElement.style.transform = `translateX(${x}px) scaleX(1)`;
      lastActiveIndex = toIdx;
      return;
    }

    const from = items[fromIdx];
    const fromR = from?.getBoundingClientRect();
    const fx = fromR ? fromR.left - nr.left : x;
    const dist = Math.abs(x - fx);
    const dir = x > fx ? 1 : -1;

    lastTime = performance.now();
    const sc = dist < 80 ? 1.02 : dist < 160 ? 1.05 : 1.08;
    indicatorElement.style.transformOrigin = dir === 1 ? 'left center' : 'right center';
    indicatorElement.style.transition = 'transform 160ms cubic-bezier(.22,1,.36,1)';
    indicatorElement.style.transform = `translateX(${x}px) scaleX(${sc})`;

    setTimeout(() => {
      if (!indicatorElement) return;
      indicatorElement.style.transition = 'transform 220ms cubic-bezier(.22,1.25,.36,1)';
      indicatorElement.style.transform = `translateX(${x}px) scaleX(1)`;
    }, 160);

    lastActiveIndex = toIdx;
  }

  let mounted = false;
  let prevActiveIndex = -1;

  $effect(() => {
    const pathname = $page.url.pathname;
    if (!mounted) return;

    const i = navItems.findIndex(item => isActive(item.href, pathname));
    if (i === activeIndex) return;
    
    const prev = activeIndex;
    activeIndex = i;

    if (!navElement || !indicatorElement) return;
    if (i === -1) { hideInd(); prevActiveIndex = i; return; }
    if (!indicatorReady) { showInstant(i); prevActiveIndex = i; return; }
    moveInd(i, prev);
    prevActiveIndex = i;
  });

  onMount(async () => {
    mounted = true;

    await Promise.allSettled([document.fonts.ready, tick()]);

    const i = navItems.findIndex(item => isActive(item.href, $page.url.pathname));
    activeIndex = i;
    prevActiveIndex = i;
    if (i !== -1) showInstant(i);

    if ($auth.token && $auth.user) {
      api.profile.me()
        .then(p => auth.updateUser({
          avatar_thumb: p.avatar_thumb,
          avatar_original: p.avatar_original,
          display_name: p.display_name
        }))
        .catch(() => {})
        .finally(() => { authChecking = false; });
    } else {
      authChecking = false;
    }

    const onResize = () => {
      if (navElement && indicatorElement && lastActiveIndex !== -1) showInstant(lastActiveIndex);
    };
    
    const onClick = (e) => {
      if (contextMenuElement && !contextMenuElement.contains(e.target)) contextMenuVisible = false;
      
      // Проверяем клик вне меню И вне кнопки триггера
      if (userMenuVisible && userMenuElement && !userMenuElement.contains(e.target)) {
        const isTrigger = userMenuTriggerElement?.contains(e.target);
        if (!isTrigger) {
          userMenuVisible = false;
        }
      }
      
      if (searchOpen && searchContainerElement && !searchContainerElement.contains(e.target)) {
        const isSearchButton = e.target.closest('button[title*="search" i], button[title*="Search" i]');
        if (!isSearchButton) {
          closeSearch();
        }
      }
    };
    
    const onScroll = () => { 
      contextMenuVisible = false; 
      userMenuVisible = false; 
    };

    window.addEventListener('resize', onResize);
    document.addEventListener('click', onClick);
    window.addEventListener('scroll', onScroll);
    
    return () => {
      window.removeEventListener('resize', onResize);
      document.removeEventListener('click', onClick);
      window.removeEventListener('scroll', onScroll);
      if (blurTimeout) clearTimeout(blurTimeout);
    };
  });

  function logoDown() { if (logoElement) { logoElement.style.transition = 'transform 90ms cubic-bezier(.4,0,1,1)'; logoElement.style.transform = 'scale(.94)'; } }
  function logoUp() { if (logoElement) { logoElement.style.transition = 'transform 180ms cubic-bezier(.22,1.4,.36,1)'; logoElement.style.transform = 'scale(1.02)'; setTimeout(() => { logoElement.style.transition = 'transform 220ms cubic-bezier(.22,1,.36,1)'; logoElement.style.transform = 'scale(1)'; }, 120); } }
  function logoLeave() { if (logoElement) logoElement.style.transform = 'scale(1)'; }
  function logoCtx(e) { e.preventDefault(); let x = e.clientX, y = e.clientY; if (x + 220 > window.innerWidth) x = window.innerWidth - 228; if (y + 200 > window.innerHeight) y = window.innerHeight - 208; contextMenuPos = { x, y }; contextMenuVisible = true; }
  function copyLogo() { navigator.clipboard.writeText(`<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg "><path d="M16 2L4 8v16l12 6 12-6V8L16 2z" fill="url(#lg)"/><path d="M10 12l6 3 6-3M16 15v9" stroke="#0a0a0a" stroke-width="2" stroke-linecap="round"/><defs><linearGradient id="lg" x1="4" y1="2" x2="28" y2="30"><stop stop-color="#4ade80"/><stop offset="1" stop-color="#22d3ee"/></linearGradient></defs></svg>`); contextMenuVisible = false; }

  function toggleUser(e) { e.stopPropagation(); userMenuVisible = !userMenuVisible; }
  function doLogout() { userMenuVisible = false; auth.logout(); goto('/'); }

  async function openSearch() {
    searchOpen = true;
    await tick();
    searchInputElement?.focus();
  }

  function closeSearch() {
    searchOpen = false;
    searchQuery = '';
  }

  function doSearch(e) {
    if (e.key === 'Enter' && searchQuery.trim()) {
      const q = searchQuery.trim();
      closeSearch();
      goto(`/search?q=${encodeURIComponent(q)}`);
    }
    if (e.key === 'Escape') closeSearch();
  }

  function handleSearchBlur() {
    blurTimeout = setTimeout(() => {
      if (searchOpen) closeSearch();
    }, 150);
  }

  function handleSearchFocus() {
    if (blurTimeout) {
      clearTimeout(blurTimeout);
      blurTimeout = null;
    }
  }
</script>

<svelte:head>
  <style>
    .nav-item { position: relative; }
    .nav-item::after {
      content: '';
      position: absolute;
      inset: 0;
      border-radius: 0.5rem;
      background: rgba(255,255,255,0.04);
      opacity: 0;
      transition: opacity 150ms;
      z-index: -1;
    }
    .nav-item:hover::after { opacity: 1; }

    #logo { transform-origin: center; transition: transform 350ms cubic-bezier(.22,1,.36,1); }
    #nav-indicator { will-change: transform, width, opacity; transform-origin: left center; }

    .nav-container {
      display: flex;
      align-items: center;
      gap: 4px;
      overflow: hidden;
    }

    .nav-block {
      display: flex;
      align-items: center;
      overflow: hidden;
      flex: 0 1 auto;
      max-width: 400px;
      opacity: 1;
      transform: scaleX(1);
      transform-origin: left center;
      transition: 
        max-width 300ms cubic-bezier(.4, 0, .2, 1),
        opacity 250ms cubic-bezier(.4, 0, .2, 1),
        transform 300ms cubic-bezier(.4, 0, .2, 1),
        margin 300ms cubic-bezier(.4, 0, .2, 1);
    }
    
    .nav-block.collapsed {
      max-width: 0;
      opacity: 0;
      transform: scaleX(0.8);
      margin-right: 0;
      pointer-events: none;
    }

    .nav-divider {
      width: 1px;
      height: 20px;
      background: var(--w18, rgba(255,255,255,0.18));
      margin-left: 8px;
      flex-shrink: 0;
      transition: opacity 200ms ease;
    }

    .search-block {
      display: flex;
      align-items: center;
      overflow: hidden;
      max-width: 0;
      opacity: 0;
      transform: scaleX(0.9) translateX(-10px);
      transform-origin: left center;
      transition: 
        max-width 300ms cubic-bezier(.4, 0, .2, 1),
        opacity 250ms cubic-bezier(.4, 0, .2, 1),
        transform 300ms cubic-bezier(.4, 0, .2, 1),
        margin 300ms cubic-bezier(.4, 0, .2, 1);
    }
    
    .search-block.open {
      max-width: 220px;
      opacity: 1;
      transform: scaleX(1) translateX(0);
    }

    .search-inner {
      width: 220px;
      flex-shrink: 0;
    }

    .search-btn-icon {
      transition: opacity 150ms, transform 150ms;
    }
    .search-btn-icon.hidden-icon {
      opacity: 0;
      transform: rotate(90deg) scale(.7);
      position: absolute;
      pointer-events: none;
    }

    /* Меню позиционируется absolute относительно nav-wrapper */
    .user-menu-dropdown {
      position: absolute;
      top: calc(100% + 8px);
      right: 0;
      width: 224px;
      z-index: 10000;
    }
  </style>
</svelte:head>

<div class="mx-auto mt-[33px] w-full max-w-[828px] relative z-[9998]">
  <header class="w-full">
    <div class="mx-auto flex max-w-7xl items-center justify-between">

      <!-- Логотип -->
      <a href="/" bind:this={logoElement} id="logo"
        class="select-none flex items-center gap-[12px] cursor-pointer"
        onmousedown={logoDown} onmouseup={logoUp} onmouseleave={logoLeave} oncontextmenu={logoCtx}>
        <img src="/Logo.svg" alt="logo" class="h-[48px] w-auto">
      </a>

      <!-- ОБЁРТКА с relative для позиционирования меню -->
      <div bind:this={navWrapperElement} class="relative">
        <nav class="nav-container rounded-[8px] px-[16px] py-[6px] backdrop-blur-[5px] bg-[--w8]">

          <!-- Nav блок -->
          <div class="nav-block {searchOpen ? 'collapsed' : ''}">
            <div bind:this={navElement} id="nav" class="relative flex items-center gap-[4px]">
              <div bind:this={indicatorElement} id="nav-indicator"
                class="pointer-events-none absolute top-0 left-0 h-full rounded-[8px] bg-[--w8] shadow-inner">
              </div>
              {#each navItems as item}
                <a href={item.href}
                  class="nav-item select-none text-sm leading-5 rounded-[8px] relative z-10 px-2 py-1.5 transition whitespace-nowrap
                    {isActive(item.href, $page.url.pathname) ? 'text-[--w]' : 'text-[--w60] hover:bg-[--w8] hover:text-[--w]'}">
                  {item.label}
                </a>
              {/each}
            </div>
            
            <div class="nav-divider"></div>
          </div>

          <!-- Поиск блок -->
          <div bind:this={searchContainerElement} 
               class="search-block {searchOpen ? 'open' : ''}">
            <div class="search-inner">
              <div class="relative">
                <input
                  bind:this={searchInputElement}
                  type="text"
                  bind:value={searchQuery}
                  onkeydown={doSearch}
                  onblur={handleSearchBlur}
                  onfocus={handleSearchFocus}
                  placeholder="Search..."
                  class="filter search pr-9 pl-3 h-[32px] w-full"
                />
                <button
                  type="button"
                  onclick={() => {
                    if (searchQuery.trim()) {
                      const q = searchQuery.trim();
                      closeSearch();
                      goto(`/search?q=${encodeURIComponent(q)}`);
                    }
                  }}
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-[--w60] hover:text-[--w] transition"
                >
                  <Search size={16} />
                </button>
              </div>
            </div>
          </div>

          <!-- Кнопка поиска -->
          <button
            onclick={searchOpen ? closeSearch : openSearch}
            disabled={!searchOpen && isSearchPage}
            class="relative w-[32px] h-[32px] flex items-center justify-center rounded-[8px] transition-colors shrink-0
              {(!searchOpen && isSearchPage)
                ? 'text-[--w20] opacity-30 cursor-not-allowed'
                : 'text-[--w60] hover:text-[--w] hover:bg-[--w8] cursor-pointer'}"
            title={searchOpen ? 'Close search' : isSearchPage ? 'Already on search page' : 'Search'}
          >
            <span class="search-btn-icon {searchOpen ? 'hidden-icon' : ''}"><Search size={16} /></span>
            <span class="search-btn-icon {searchOpen ? '' : 'hidden-icon'}"><X size={16} /></span>
          </button>

          <!-- Auth -->
          <div class="flex items-center shrink-0 ml-[4px]">
            {#if authChecking}
              <div class="w-[60px] h-[28px] rounded-[8px] bg-[--w8] animate-pulse"></div>
            {:else if $auth.user}
              <button 
                bind:this={userMenuTriggerElement}
                onclick={toggleUser}
                class="select-none flex items-center gap-2 rounded-[8px] px-2 py-1 transition hover:bg-[--w8] cursor-pointer border border-[--w8]">
                {#if $auth.user.avatar_thumb}
                  <img src={avatarUrl($auth.user.avatar_thumb)} alt="" class="w-6 h-6 rounded-full object-cover" />
                {:else}
                  <div class="w-6 h-6 rounded-full bg-[--w12] flex items-center justify-center">
                    <span class="text-xs text-[--w60] font-medium">
                      {($auth.user.display_name || $auth.user.username || '?')[0].toUpperCase()}
                    </span>
                  </div>
                {/if}
                <span class="text-sm text-[--w60] hidden sm:inline">
                  {($auth.user.display_name || $auth.user.username || '').slice(0, 14)}
                  {($auth.user.display_name || $auth.user.username || '').length > 14 ? '…' : ''}
                </span>
                <svg class="w-3 h-3 text-[--w60] transition-transform {userMenuVisible ? 'rotate-180' : ''}"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            {:else}
              <a href="/auth/login"
                class="select-none text-sm leading-5 rounded-[8px] border border-[--w12] px-2 py-1.5 text-[--w60] transition hover:border-[--w18] hover:text-[--w]">
                Login
              </a>
            {/if}
          </div>

        </nav>

        <!-- МЕНЮ СНАРУЖИ NAV — не обрезается overflow -->
        {#if userMenuVisible && $auth.user}
          <div 
            bind:this={userMenuElement}
            class="user-menu-dropdown bg-[--select] backdrop-blur-xl border border-[--w12] rounded-2xl shadow-2xl overflow-hidden"
          >
            <!-- Шапка -->
            <a href="/profile/{$auth.user.username}" onclick={() => userMenuVisible = false}
              class="block no-underline">
              <div class="mx-2 mt-2 mb-0 rounded-xl bg-[--w8] hover:bg-[--w12] transition px-4 py-4 flex flex-col items-center gap-2.5 cursor-pointer">
                {#if $auth.user.avatar_thumb}
                  <img src={avatarUrl($auth.user.avatar_thumb)} alt=""
                    class="w-[56px] h-[56px] rounded-full object-cover"/>
                {:else}
                  <div class="w-[56px] h-[56px] rounded-full bg-[--w18] flex items-center justify-center">
                    <span class="text-xl text-[--w60] font-medium">
                      {($auth.user.display_name || $auth.user.username || '?')[0].toUpperCase()}
                    </span>
                  </div>
                {/if}
                <div class="text-center">
                  <div class="text-sm text-[--w] font-bold leading-tight">
                    {$auth.user.display_name || $auth.user.username}
                  </div>
                  <div class="text-xs text-[--w60] leading-tight mt-0.5">
                    @{$auth.user.username}
                  </div>
                </div>
              </div>
            </a>

            <!-- Пункты меню -->
            <div class="p-1.5 mt-1 flex flex-col gap-0.5">
              <a href="/profile/settings" onclick={() => userMenuVisible = false}
                class="flex items-center gap-2.5 px-2.5 py-2 text-sm text-[--w60] rounded-[10px] transition hover:bg-[--w8] hover:text-[--w] no-underline">
                <Settings size={16} /> Settings
              </a>
              {#if isAdmin($auth.user)}
                <a href="/admin" onclick={() => userMenuVisible = false}
                  class="flex items-center gap-2.5 px-2.5 py-2 text-sm text-[--w60] rounded-[10px] transition hover:bg-[--w8] hover:text-[--w] no-underline">
                  <Shield size={16} /> Admin
                </a>
              {/if}

              <div class="h-px bg-[--w8] my-0.5 mx-1"></div>

              <button onclick={doLogout}
                class="w-full flex items-center gap-2.5 px-2.5 py-2 text-sm text-red-400 rounded-[10px] transition hover:bg-red-500/10 hover:text-red-300 cursor-pointer">
                <LogOut size={16} /> Log Out
              </button>
            </div>
          </div>
        {/if}
      </div>

    </div>
  </header>
</div>

{#if contextMenuVisible}
  <div bind:this={contextMenuElement}
    class="fixed z-[10001] min-w-[200px] bg-[--select] backdrop-blur-xl border border-[--w12] rounded-xl p-1.5 shadow-2xl select-none"
    style="left:{contextMenuPos.x}px;top:{contextMenuPos.y}px;">
    <button onclick={copyLogo}
      class="w-full flex items-center gap-2.5 px-2.5 py-2 text-sm text-[--w60] rounded-[8px] cursor-pointer transition hover:bg-[--w8] hover:text-[--w]">
      <Copy size={16} /> Copy Logo SVG
    </button>
    <a href="/" onclick={() => contextMenuVisible = false}
      class="flex items-center gap-2.5 px-2.5 py-2 text-sm text-[--w60] rounded-[8px] transition hover:bg-[--w8] hover:text-[--w]">
      <Home size={16} /> Home
    </a>
    <a href="/about" onclick={() => contextMenuVisible = false}
      class="flex items-center gap-2.5 px-2.5 py-2 text-sm text-[--w60] rounded-[8px] transition hover:bg-[--w8] hover:text-[--w]">
      <Info size={16} /> About
    </a>
  </div>
{/if}