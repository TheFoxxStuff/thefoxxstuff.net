<script>
  import { page } from '$app/stores';
  import { auth, isAdmin } from '$lib/stores/auth.js';
  import { onMount, tick } from 'svelte';
  import { goto } from '$app/navigation';
  import { api, API_BASE } from '$lib/api';
  import { 
    Copy, 
    Home, 
    Info, 
    LogOut, 
    Settings, 
    Shield, 
    Search, 
    X, 
    ChevronDown, 
    User 
  } from 'lucide-svelte';

  // === Константы ===
  const NAV_ITEMS = [
    { href: '/music', label: 'Music' },
    { href: '/blog', label: 'Blog' },
    { href: '/arts', label: 'Arts' },
    { href: '/links', label: 'Links' },
    { href: '/about', label: 'About' },
  ];

  const LOGO_SVG = `<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M16 2L4 8v16l12 6 12-6V8L16 2z" fill="url(#lg)"/><path d="M10 12l6 3 6-3M16 15v9" stroke="#0a0a0a" stroke-width="2" stroke-linecap="round"/><defs><linearGradient id="lg" x1="4" y1="2" x2="28" y2="30"><stop stop-color="#4ade80"/><stop offset="1" stop-color="#22d3ee"/></linearGradient></defs></svg>`;

  // === Рефы ===
  let navElement = $state(null);
  let indicatorElement = $state(null);
  let logoElement = $state(null);
  let contextMenuElement = $state(null);
  let userMenuElement = $state(null);
  let searchInputElement = $state(null);
  let searchContainerElement = $state(null);
  let userMenuTriggerElement = $state(null);
  let navWrapperElement = $state(null);

  // === Состояния ===
  let activeIndex = $state(-1);
  let contextMenuVisible = $state(false);
  let contextMenuPos = $state({ x: -9999, y: -9999 });
  let userMenuVisible = $state(false);
  let searchOpen = $state(false);
  let searchQuery = $state('');
  let authChecking = $state(true);
  let indicatorReady = $state(false);
  let lastActiveIndex = $state(-1);
  let blurTimeout = $state(null);
  let mounted = $state(false);

  // === Деривированные значения ===
  const isActive = (href, pathname) => 
    href === '/' ? pathname === '/' : pathname.startsWith(href);

  const isSearchPage = $derived(
    $page.url.pathname === '/search' && !!$page.url.searchParams.get('q')
  );

  const userInitials = $derived(
    ($auth.user?.display_name || $auth.user?.username || '?')[0].toUpperCase()
  );

  const displayName = $derived(
    ($auth.user?.display_name || $auth.user?.username || '').slice(0, 14)
  );

  const isLongName = $derived(
    ($auth.user?.display_name || $auth.user?.username || '').length > 14
  );

  // === Функции индикатора ===
  function hideIndicator() {
    if (!indicatorElement) return;
    indicatorElement.style.transition = 'opacity 200ms ease-out';
    indicatorElement.style.opacity = '0';
  }

  function showInstant(index) {
    if (!navElement || !indicatorElement) return;
    
    const items = navElement.querySelectorAll('.nav-item');
    const target = items[index];
    if (!target) return;

    const navRect = navElement.getBoundingClientRect();
    const targetRect = target.getBoundingClientRect();
    const x = targetRect.left - navRect.left;

    indicatorElement.style.transition = 'none';
    indicatorElement.style.width = `${targetRect.width}px`;
    indicatorElement.style.transform = `translateX(${x}px) scaleX(1)`;
    indicatorElement.style.opacity = '1';

    requestAnimationFrame(() => requestAnimationFrame(() => {
      indicatorElement.style.transition = '';
      indicatorReady = true;
      lastActiveIndex = index;
    }));
  }

  function moveIndicator(toIndex, fromIndex) {
    if (!navElement || !indicatorElement || toIndex === -1) return;
    
    const items = navElement.querySelectorAll('.nav-item');
    const toEl = items[toIndex];
    if (!toEl) return;

    const navRect = navElement.getBoundingClientRect();
    const toRect = toEl.getBoundingClientRect();
    const x = toRect.left - navRect.left;

    indicatorElement.style.width = `${toRect.width}px`;
    indicatorElement.style.opacity = '1';

    if (fromIndex === -1 || fromIndex === null) {
      indicatorElement.style.transition = 'transform 260ms cubic-bezier(.22,1,.36,1)';
      indicatorElement.style.transform = `translateX(${x}px) scaleX(1)`;
      lastActiveIndex = toIndex;
      return;
    }

    const fromEl = items[fromIndex];
    const fromRect = fromEl?.getBoundingClientRect();
    const fromX = fromRect ? fromRect.left - navRect.left : x;
    const distance = Math.abs(x - fromX);
    const direction = x > fromX ? 1 : -1;

    const scale = distance < 80 ? 1.02 : distance < 160 ? 1.05 : 1.08;
    
    indicatorElement.style.transformOrigin = direction === 1 ? 'left center' : 'right center';
    indicatorElement.style.transition = 'transform 160ms cubic-bezier(.22,1,.36,1)';
    indicatorElement.style.transform = `translateX(${x}px) scaleX(${scale})`;

    setTimeout(() => {
      if (!indicatorElement) return;
      indicatorElement.style.transition = 'transform 220ms cubic-bezier(.22,1.25,.36,1)';
      indicatorElement.style.transform = `translateX(${x}px) scaleX(1)`;
    }, 160);

    lastActiveIndex = toIndex;
  }

  // === Обработчики логотипа ===
  function handleLogoMouseDown() {
    if (!logoElement) return;
    logoElement.style.transition = 'transform 90ms cubic-bezier(.4,0,1,1)';
    logoElement.style.transform = 'scale(0.94)';
  }

  function handleLogoMouseUp() {
    if (!logoElement) return;
    logoElement.style.transition = 'transform 180ms cubic-bezier(.22,1.4,.36,1)';
    logoElement.style.transform = 'scale(1.02)';
    
    setTimeout(() => {
      if (!logoElement) return;
      logoElement.style.transition = 'transform 220ms cubic-bezier(.22,1,.36,1)';
      logoElement.style.transform = 'scale(1)';
    }, 120);
  }

  function handleLogoMouseLeave() {
    if (logoElement) logoElement.style.transform = 'scale(1)';
  }

  function handleLogoContextMenu(e) {
    e.preventDefault();
    let x = e.clientX;
    let y = e.clientY;
    
    if (x + 220 > window.innerWidth) x = window.innerWidth - 228;
    if (y + 200 > window.innerHeight) y = window.innerHeight - 208;
    
    contextMenuPos = { x, y };
    contextMenuVisible = true;
  }

  function copyLogoSvg() {
    navigator.clipboard.writeText(LOGO_SVG);
    contextMenuVisible = false;
  }

  // === Поиск ===
  async function openSearch() {
    searchOpen = true;
    await tick();
    searchInputElement?.focus();
  }

  function closeSearch() {
    searchOpen = false;
    searchQuery = '';
  }

  function handleSearchKeydown(e) {
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

  function submitSearch() {
    if (searchQuery.trim()) {
      const q = searchQuery.trim();
      closeSearch();
      goto(`/search?q=${encodeURIComponent(q)}`);
    }
  }

  // === Пользователь ===
  function toggleUserMenu(e) {
    e.stopPropagation();
    userMenuVisible = !userMenuVisible;
  }

  function handleLogout() {
    userMenuVisible = false;
    auth.logout();
    goto('/');
  }

  // === URL аватара ===
  function getAvatarUrl(path) {
    return path ? `${API_BASE}/upload/file/${path}` : null;
  }

  // === Эффекты ===
  $effect(() => {
    const pathname = $page.url.pathname;
    if (!mounted) return;

    const index = NAV_ITEMS.findIndex(item => isActive(item.href, pathname));
    if (index === activeIndex) return;
    
    const prev = activeIndex;
    activeIndex = index;

    if (!navElement || !indicatorElement) return;
    if (index === -1) {
      hideIndicator();
      return;
    }
    if (!indicatorReady) {
      showInstant(index);
      return;
    }
    moveIndicator(index, prev);
  });

  // === Жизненный цикл ===
  onMount(async () => {
    mounted = true;

    await Promise.allSettled([document.fonts.ready, tick()]);

    const index = NAV_ITEMS.findIndex(item => isActive(item.href, $page.url.pathname));
    activeIndex = index;
    if (index !== -1) showInstant(index);

    if ($auth.token && $auth.user) {
      // FIX: таймаут 5 сек — authChecking не зависает если сервер недоступен
      const timeout = setTimeout(() => { authChecking = false; }, 5000);
      try {
        const profile = await api.profile.me();
        auth.updateUser({
          avatar_thumb:    profile.avatar_thumb,
          avatar_original: profile.avatar_original,
          display_name:    profile.display_name,
        });
      } catch {
        // При ошибке просто продолжаем — закешированные данные остаются
      } finally {
        clearTimeout(timeout);
        authChecking = false;
      }
    } else {
      authChecking = false;
    }

    const handleResize = () => {
      if (navElement && indicatorElement && lastActiveIndex !== -1) {
        showInstant(lastActiveIndex);
      }
    };

    const handleClick = (e) => {
      if (contextMenuElement && !contextMenuElement.contains(e.target)) {
        contextMenuVisible = false;
      }
      
      if (userMenuVisible && userMenuElement && !userMenuElement.contains(e.target)) {
        const isTrigger = userMenuTriggerElement?.contains(e.target);
        if (!isTrigger) userMenuVisible = false;
      }
      
      if (searchOpen && searchContainerElement && !searchContainerElement.contains(e.target)) {
        const isSearchButton = e.target.closest('button[title*="search" i], button[title*="Search" i]');
        if (!isSearchButton) closeSearch();
      }
    };

    const handleScroll = () => {
      contextMenuVisible = false;
      userMenuVisible = false;
    };

    window.addEventListener('resize', handleResize);
    document.addEventListener('click', handleClick);
    window.addEventListener('scroll', handleScroll);

    return () => {
      window.removeEventListener('resize', handleResize);
      document.removeEventListener('click', handleClick);
      window.removeEventListener('scroll', handleScroll);
      if (blurTimeout) clearTimeout(blurTimeout);
    };
  });
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

    .search-inner { width: 220px; flex-shrink: 0; }

    .search-btn-icon {
      transition: opacity 150ms, transform 150ms;
    }
    
    .search-btn-icon.hidden-icon {
      opacity: 0;
      transform: rotate(90deg) scale(0.7);
      position: absolute;
      pointer-events: none;
    }

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
      <a 
        href="/" 
        bind:this={logoElement} 
        id="logo"
        class="select-none flex items-center gap-[12px] cursor-pointer"
        onmousedown={handleLogoMouseDown} 
        onmouseup={handleLogoMouseUp} 
        onmouseleave={handleLogoMouseLeave} 
        oncontextmenu={handleLogoContextMenu}
      >
        <img src="/Logo.svg" alt="logo" class="h-[48px] w-auto">
      </a>

      <!-- Навигация -->
      <div bind:this={navWrapperElement} class="relative">
        <nav class="nav-container rounded-[8px] px-[16px] py-[6px] backdrop-blur-[5px] bg-[--w8]">
          
          <!-- Навигационные ссылки -->
          <div class="nav-block {searchOpen ? 'collapsed' : ''}">
            <div bind:this={navElement} id="nav" class="relative flex items-center gap-[4px]">
              <div 
                bind:this={indicatorElement} 
                id="nav-indicator"
                class="pointer-events-none absolute top-0 left-0 h-full rounded-[8px] bg-[--w8] shadow-inner"
              ></div>
              
              {#each NAV_ITEMS as item}
                <a 
                  href={item.href}
                  class="nav-item select-none text-sm leading-5 rounded-[8px] relative z-10 px-2 py-1.5 transition whitespace-nowrap
                    {isActive(item.href, $page.url.pathname) ? 'text-[--w]' : 'text-[--w60] hover:bg-[--w8] hover:text-[--w]'}"
                >
                  {item.label}
                </a>
              {/each}
            </div>
            
            <div class="nav-divider"></div>
          </div>

          <!-- Поиск -->
          <div 
            bind:this={searchContainerElement} 
            class="search-block {searchOpen ? 'open' : ''}"
          >
            <div class="search-inner">
              <div class="relative me-1">
                <input
                  bind:this={searchInputElement}
                  type="text"
                  bind:value={searchQuery}
                  onkeydown={handleSearchKeydown}
                  onblur={handleSearchBlur}
                  onfocus={handleSearchFocus}
                  placeholder="Search..."
                  class="filter search pr-9 pl-3 h-[32px] w-full"
                />
                <button
                  type="button"
                  onclick={submitSearch}
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
            <span class="search-btn-icon {searchOpen ? 'hidden-icon' : ''}">
              <Search size={16} />
            </span>
            <span class="search-btn-icon {searchOpen ? '' : 'hidden-icon'}">
              <X size={16} />
            </span>
          </button>

          <!-- Аутентификация -->
          <div class="flex items-center shrink-0 ml-[4px]">
            {#if authChecking}
              <div class="w-[60px] h-[28px] rounded-[8px] bg-[--w8] animate-pulse"></div>
            {:else if $auth.user}
              <button 
                bind:this={userMenuTriggerElement}
                onclick={toggleUserMenu}
                class="select-none flex items-center gap-2 rounded-[8px] px-2 py-1 transition hover:bg-[--w8] cursor-pointer border border-[--w8]"
              >
                {#if $auth.user.avatar_thumb}
                  <img 
                    src={getAvatarUrl($auth.user.avatar_thumb)} 
                    alt="" 
                    class="w-6 h-6 rounded-full object-cover" 
                  />
                {:else}
                  <div class="w-6 h-6 rounded-full bg-[--w12] flex items-center justify-center">
                    <span class="text-xs text-[--w60] font-medium">{userInitials}</span>
                  </div>
                {/if}
                
                <span class="text-sm text-[--w60] hidden sm:inline">
                  {displayName}{isLongName ? '…' : ''}
                </span>
                
                <ChevronDown 
                  size={14} 
                  class="text-[--w60] transition-transform {userMenuVisible ? 'rotate-180' : ''}" 
                />
              </button>
            {:else}
              <a 
                href="/auth/login"
                class="select-none text-sm leading-5 rounded-[8px] border border-[--w12] px-2 py-1.5 text-[--w60] transition hover:border-[--w18] hover:text-[--w]"
              >
                Login
              </a>
            {/if}
          </div>
        </nav>

        <!-- Выпадающее меню пользователя -->
        {#if userMenuVisible && $auth.user}
          <div 
            bind:this={userMenuElement}
            class="user-menu-dropdown backdrop-blur-[20px] border-[--w12] rounded-[8px] shadow-2xl overflow-hidden" 
style="background: rgba(0, 0, 0, 0.6), linear-gradient(0deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.12));"
          >
            <!-- Профиль -->
            <a 
              href="/profile/{$auth.user.username}" 
              onclick={() => userMenuVisible = false}
              class="block no-underline"
            >
              <div class="mx-[6px] mt-[6px] rounded-[6px] transition hover:bg-[--w5] px-[8px] py-[12px] flex flex-col items-center gap-[4px] cursor-pointer">
                {#if $auth.user.avatar_thumb}
                  <img 
                    src={getAvatarUrl($auth.user.avatar_thumb)} 
                    alt=""
                    class="w-[56px] h-[56px] rounded-full object-cover"
                  />
                {:else}
                  <div class="w-[56px] h-[56px] rounded-full bg-[--w18] flex items-center justify-center">
                    <User size={28} class="text-[--w60]" />
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

            <!-- Меню -->
            <div class="px-[6px] pb-[6px] pt-[4px] flex flex-col gap-0.5">
              <a 
                href="/profile/settings" 
                onclick={() => userMenuVisible = false}
                class="flex items-center gap-[4px] px-[12px] py-[6px] text-[14px] text-[--w60] rounded-[6px] transition hover:bg-[--w8] hover:text-[--w] no-underline"
              >
                <Settings size={16} /> 
                <span>Profile settings</span>
              </a>
              
              {#if isAdmin($auth.user)}
                <a 
                  href="/admin" 
                  onclick={() => userMenuVisible = false}
                  class="flex items-center gap-[4px] px-[12px] py-[6px] text-[14px] text-[--w60] rounded-[6px] transition hover:bg-[--w8] hover:text-[--w] no-underline"
                >
                  <Shield size={16} /> 
                  <span>Admin</span>
                </a>
              {/if}

              <div class="h-px bg-[--w8] my-0.5"></div>

              <button 
                onclick={handleLogout}
                class="flex items-center gap-[4px] px-[12px] py-[6px] text-[14px] text-[--w60] rounded-[6px] transition hover:bg-[--w8] hover:text-[--w] no-underline"
              >
                <LogOut size={16} /> 
                <span>Log Out</span>
              </button>
            </div>
          </div>
        {/if}
      </div>
    </div>
  </header>
</div>

<!-- Контекстное меню -->
{#if contextMenuVisible}
  <div 
    bind:this={contextMenuElement}
    class="fixed z-[10001] min-w-[200px] bg-[--select] backdrop-blur-xl border border-[--w12] rounded-xl p-1.5 shadow-2xl select-none"
    style="left:{contextMenuPos.x}px;top:{contextMenuPos.y}px;"
  >
    <button 
      onclick={copyLogoSvg}
      class="w-full flex items-center gap-2.5 px-2.5 py-2 text-sm text-[--w60] rounded-[8px] cursor-pointer transition hover:bg-[--w8] hover:text-[--w]"
    >
      <Copy size={16} /> 
      <span>Copy Logo SVG</span>
    </button>
    
    <a 
      href="/" 
      onclick={() => contextMenuVisible = false}
      class="flex items-center gap-2.5 px-2.5 py-2 text-sm text-[--w60] rounded-[8px] transition hover:bg-[--w8] hover:text-[--w]"
    >
      <Home size={16} /> 
      <span>Home</span>
    </a>
    
    <a 
      href="/about" 
      onclick={() => contextMenuVisible = false}
      class="flex items-center gap-2.5 px-2.5 py-2 text-sm text-[--w60] rounded-[8px] transition hover:bg-[--w8] hover:text-[--w]"
    >
      <Info size={16} /> 
      <span>About</span>
    </a>
  </div>
{/if}