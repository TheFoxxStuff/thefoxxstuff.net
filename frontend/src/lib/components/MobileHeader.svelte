<script>
  import { page } from '$app/stores';
  import { onMount, onDestroy } from 'svelte';
  import { Home, Music, FileText, Palette, Link2, Info, Users, Menu, X } from 'lucide-svelte';

  // Navigation links
  const mainLinks = [
    { text: 'Home', icon: Home, path: '/' },
    { text: 'Blog', icon: FileText, path: '/blog' },
    { text: 'Music', icon: Music, path: '/music' },
    { text: 'Arts', icon: Palette, path: '/arts' },
    { text: 'Links', icon: Link2, path: '/links' },
    { text: 'About', icon: Info, path: '/about' },
  ];

  const otherLinks = [
    { text: 'World', icon: Users, path: '/world' },
  ];

  // State
  let isOpen = $state(false);
  let breadText = $state(null);
  let panelHeader = $state(null);
  let showLeftFade = $state(false);
  let showRightFade = $state(true);

  // Breadcrumbs generation
  const breadcrumbs = $derived.by(() => {
    const pathname = $page.url.pathname;
    const segments = pathname.split('/').filter(Boolean);

    const crumbs = [{ path: '/', title: 'Home' }];

    let currentPath = '';
    for (const segment of segments) {
      currentPath += `/${segment}`;

      // Map paths to readable titles
      let title = segment.charAt(0).toUpperCase() + segment.slice(1);
      if (segment === 'blog') title = 'Blog';
      else if (segment === 'music') title = 'Music';
      else if (segment === 'arts') title = 'Arts';
      else if (segment === 'links') title = 'Links';
      else if (segment === 'about') title = 'About';
      else if (segment === 'world') title = 'World';
      else if (segment === 'profile') title = 'Profile';
      else if (segment === 'admin') title = 'Admin';

      crumbs.push({ path: currentPath, title });
    }

    return crumbs;
  });

  // Toggle menu
  function toggleMenu() {
    isOpen = !isOpen;
    if (isOpen) {
      setTimeout(() => panelHeader?.focus(), 360);
    }
  }

  // Close menu
  function closeMenu() {
    isOpen = false;
  }

  // Check scroll position for fade masks
  function checkScrollPosition() {
    if (!breadText) return;
    const { scrollLeft, scrollWidth, clientWidth } = breadText;
    showLeftFade = scrollLeft > 0;
    showRightFade = scrollLeft < scrollWidth - clientWidth - 1;
  }

  // Keyboard navigation
  function handleKeyDown(e) {
    if (e.key === 'Escape' && isOpen) {
      e.preventDefault();
      closeMenu();
    }
  }

  onMount(() => {
    window.addEventListener('keydown', handleKeyDown);
    if (breadText) {
      breadText.addEventListener('scroll', checkScrollPosition, { passive: true });
      checkScrollPosition();
    }
  });

  onDestroy(() => {
    if (typeof window !== 'undefined') {
      window.removeEventListener('keydown', handleKeyDown);
      breadText?.removeEventListener('scroll', checkScrollPosition);
    }
  });

  // Watch for route changes
  $effect(() => {
    $page.url.pathname;
    setTimeout(checkScrollPosition, 100);
  });
</script>

<header class="mobile-header" aria-label="Mobile navigation">
  <div class="nav-info" aria-live="polite">
    <svg class="sitemap-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <rect x="3" y="3" width="7" height="7" rx="1"/>
      <rect x="14" y="3" width="7" height="7" rx="1"/>
      <rect x="14" y="14" width="7" height="7" rx="1"/>
      <rect x="3" y="14" width="7" height="7" rx="1"/>
    </svg>

    <div class="breadcrumbs-container">
      <div class="bread-text" bind:this={breadText}>
        {#each breadcrumbs as crumb, index}
          <a href={crumb.path} class="breadcrumb-link">
            {crumb.title}
            {#if index < breadcrumbs.length - 1}
              <span class="slash">/</span>
            {/if}
          </a>
        {/each}
      </div>
      <div class="fade-mask fade-left" class:active={showLeftFade}></div>
      <div class="fade-mask fade-right" class:active={showRightFade}></div>
    </div>
  </div>

  <button
    class="menu-toggle"
    aria-controls="mobile-menu"
    aria-expanded={isOpen}
    aria-label={isOpen ? 'Close menu' : 'Open menu'}
    onclick={toggleMenu}
  >
    {#if isOpen}
      <X size={20} />
    {:else}
      <Menu size={20} />
    {/if}
    <span>{isOpen ? 'Close' : 'Menu'}</span>
  </button>
</header>

<nav
  id="mobile-menu"
  class="menu-panel"
  class:active={isOpen}
  aria-label="Mobile navigation menu"
  aria-hidden={!isOpen}
>
  <div class="panel-header" tabindex="-1" bind:this={panelHeader}>Navigation</div>

  <div class="main-links">
    {#each mainLinks as item}
      {@const Icon = item.icon}
      <a
        href={item.path}
        class="btn-link"
        onclick={closeMenu}
      >
        <Icon size={20} />
        {item.text}
      </a>
    {/each}
  </div>

  <div class="subsection-label">Other</div>

  <div class="other-links">
    {#each otherLinks as item}
      {@const Icon = item.icon}
      <a
        href={item.path}
        class="btn-link"
        onclick={closeMenu}
      >
        <Icon size={20} />
        {item.text}
      </a>
    {/each}
  </div>
</nav>

<style>
  .mobile-header {
    display: none;
  }

  @media (max-width: 768px) {
    .mobile-header {
      position: fixed;
      bottom: -1px;
      left: 0;
      width: 100%;
      background: rgba(10, 10, 10, 0.92);
      backdrop-filter: blur(20px);
      border-radius: 14px 14px 0 0;
      padding: 12px 16px calc(16px + env(safe-area-inset-bottom)) 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      user-select: none;
      z-index: 120;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
    }

    .nav-info {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      color: rgba(255, 255, 255, 0.6);
      font-weight: 500;
      min-width: 0;
      flex: 1;
      margin-left: 4px;
    }

    .sitemap-icon {
      width: 18px;
      height: 18px;
      flex-shrink: 0;
      stroke: rgba(255, 255, 255, 0.6);
    }

    .breadcrumbs-container {
      position: relative;
      flex: 1;
      min-width: 0;
      overflow: hidden;
      display: flex;
      align-items: center;
    }

    .bread-text {
      white-space: nowrap;
      overflow-x: auto;
      width: 100%;
      font-size: 12px;
      padding: 0 4px;
      color: rgba(255, 255, 255, 0.6);
      -ms-overflow-style: none;
      scrollbar-width: none;
      touch-action: pan-x;
      -webkit-overflow-scrolling: touch;
    }

    .bread-text::-webkit-scrollbar {
      display: none;
    }

    .breadcrumb-link {
      color: inherit;
      text-decoration: none;
      transition: color 0.2s;
    }

    .breadcrumb-link:hover {
      color: rgba(255, 255, 255, 0.9);
    }

    .slash {
      margin: 0 4px;
      opacity: 0.4;
    }

    .fade-mask {
      position: absolute;
      top: 0;
      bottom: 0;
      width: 20px;
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.3s ease;
    }

    .fade-mask.active {
      opacity: 1;
    }

    .fade-left {
      left: 0;
      background: linear-gradient(90deg, rgba(10, 10, 10, 0.9) 0%, transparent 100%);
    }

    .fade-right {
      right: 0;
      background: linear-gradient(270deg, rgba(10, 10, 10, 0.9) 0%, transparent 100%);
    }

    .menu-toggle {
      display: flex;
      align-items: center;
      gap: 6px;
      background: rgba(255, 255, 255, 0.05);
      border: none;
      padding: 9px 14px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 12px;
      font-weight: 600;
      color: rgba(255, 255, 255, 0.6);
      user-select: none;
      transition: all 0.2s;
      flex-shrink: 0;
      margin-left: 8px;
    }

    .menu-toggle:hover {
      background: rgba(255, 255, 255, 0.08);
      color: rgba(255, 255, 255, 0.9);
    }

    .menu-panel {
      position: fixed;
      bottom: calc(4.6rem + env(safe-area-inset-bottom, 0px));
      left: 50%;
      transform: translateX(-50%) translateY(20px);
      background: rgba(10, 10, 10, 0.95);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 12px;
      padding: 1rem 1.2rem 1.7rem 1.2rem;
      width: 94vw;
      max-width: 480px;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.35s cubic-bezier(0.4, 0, 0.2, 1),
        transform 0.45s cubic-bezier(0.4, 0, 0.2, 1);
      user-select: none;
      z-index: 119;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }

    .menu-panel.active {
      opacity: 1;
      pointer-events: auto;
      transform: translateX(-50%) translateY(0);
    }

    .panel-header {
      font-weight: 900;
      font-size: 20px;
      color: rgba(255, 255, 255, 0.9);
      letter-spacing: -0.04em;
      margin-bottom: 1rem;
    }

    .main-links {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 6px;
      margin-bottom: 1rem;
    }

    .subsection-label {
      font-size: 11px;
      font-weight: 600;
      color: rgba(255, 255, 255, 0.4);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 8px;
      margin-top: 8px;
    }

    .other-links {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 6px;
    }

    .btn-link {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px 12px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 10px;
      color: rgba(255, 255, 255, 0.6);
      font-weight: 600;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.2s;
      text-decoration: none;
    }

    .btn-link:hover {
      background: rgba(255, 255, 255, 0.08);
      color: rgba(255, 255, 255, 0.9);
    }
  }

  /* Hide on desktop */
  @media (min-width: 769px) {
    .mobile-header,
    .menu-panel {
      display: none !important;
    }
  }
</style>
