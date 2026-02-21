<script>
  import { Sun, Moon, Copy, Check, ChevronRight, Calendar, Eye, Download, ExternalLink, Search, Music, Image, FileText, Heart, Star, Play, Pause, SkipForward, Volume2, Shield, Home, Info } from 'lucide-svelte';

  // ─── Theme ───────────────────────────────────────────────────────────
  let theme = $state('dark');
  function toggleTheme() { theme = theme === 'dark' ? 'light' : 'dark'; }

  // ─── Copy to clipboard ───────────────────────────────────────────────
  let copiedKey = $state(null);
  async function copy(text, key) {
    await navigator.clipboard.writeText(text);
    copiedKey = key;
    setTimeout(() => { copiedKey = null; }, 1500);
  }

  // ─── Active section (sidebar nav) ───────────────────────────────────
  let activeSection = $state('colors');

  const sections = [
    { id: 'colors',     label: 'Colors' },
    { id: 'typography', label: 'Typography' },
    { id: 'spacing',    label: 'Spacing & Radius' },
    { id: 'buttons',    label: 'Buttons' },
    { id: 'badges',     label: 'Badges & Tags' },
    { id: 'cards',      label: 'Cards' },
    { id: 'inputs',     label: 'Inputs' },
    { id: 'navigation', label: 'Navigation' },
    { id: 'layout',     label: 'Layout' },
  ];

  // ─── Color tokens ────────────────────────────────────────────────────
  const colorTokens = [
    { name: 'Background', var: '--bg', dark: '#111111', light: '#f4f4f2', desc: 'Page background' },
    { name: 'Text primary', var: '--w', dark: '#FFFFFF', light: '#111111', desc: 'Primary text' },
    { name: 'Text 60%', var: '--w60', dark: 'rgba(255,255,255,0.60)', light: 'rgba(0,0,0,0.55)', desc: 'Secondary text, labels' },
    { name: 'Text 30%', var: '--w30', dark: 'rgba(255,255,255,0.30)', light: 'rgba(0,0,0,0.30)', desc: 'Placeholder, muted' },
    { name: 'Surface 5%', var: '--w5', dark: 'rgba(255,255,255,0.05)', light: 'rgba(0,0,0,0.04)', desc: 'Card bg, subtle fill' },
    { name: 'Surface 8%', var: '--w8', dark: 'rgba(255,255,255,0.08)', light: 'rgba(0,0,0,0.07)', desc: 'Hover state, active nav' },
    { name: 'Border 12%', var: '--w12', dark: 'rgba(255,255,255,0.12)', light: 'rgba(0,0,0,0.10)', desc: 'Subtle borders' },
    { name: 'Border 18%', var: '--w18', dark: 'rgba(255,255,255,0.18)', light: 'rgba(0,0,0,0.16)', desc: 'Dividers, separators' },
    { name: 'Green', var: '--green', dark: '#73EE07', light: '#4dbd00', desc: 'NEW RELEASE badge, accents' },
    { name: 'Accent Green', var: 'accent.green', dark: '#4ade80', light: '#16a34a', desc: 'Interactive elements, CTAs' },
    { name: 'Accent Cyan', var: 'accent.cyan', dark: '#22d3ee', light: '#0891b2', desc: 'Gradient end, highlights' },
    { name: 'Accent Red', var: 'accent.red', dark: '#ef4444', light: '#dc2626', desc: 'Errors, danger actions' },
    { name: 'Purple', var: '--purple', dark: '#6D07EE', light: '#5b05c7', desc: 'Special accents' },
    { name: 'Blue', var: '--blue', dark: '#47ADFF', light: '#2563eb', desc: 'Links, focus rings' },
  ];

  // ─── Typography scale ────────────────────────────────────────────────
  const typeScale = [
    { label: 'Display / H1', size: '30px', weight: '500', font: 'DrukWideCyr', lineH: '1.1', tracking: 'wide', class: 'font-display text-[24px] tracking-wide', sample: 'ASTRAL SUMMER (2020)' },
    { label: 'Display H2', size: '24px', weight: '500', font: 'DrukWideCyr', lineH: '1.15', tracking: 'wide', class: 'font-display text-2xl tracking-wide', sample: 'Music' },
    { label: 'Display H3', size: '18px', weight: '500', font: 'DrukWideCyr', lineH: '1.2', tracking: 'wide', class: 'font-display text-lg tracking-wide', sample: 'Track List' },
    { label: 'Body Large', size: '18px', weight: '400', font: 'Golos', lineH: '1.5', tracking: 'normal', class: 'text-[18px] text-[--w]', sample: 'Название релиза и карточка' },
    { label: 'Body Base', size: '14px', weight: '400', font: 'Golos', lineH: '1.5', tracking: 'normal', class: 'text-sm text-[--w60]', sample: 'Secondary text, meta information and descriptions' },
    { label: 'Caption / Label', size: '12px', weight: '400', font: 'Golos', lineH: '1.4', tracking: 'normal', class: 'text-xs text-[--w60]', sample: 'Tag, badge, small label text' },
    { label: 'Text Gradient', size: '24px', weight: '500', font: 'DrukWideCyr', lineH: '1.1', tracking: 'wide', class: 'font-display text-2xl tracking-wide bg-gradient-to-r from-[#4ade80] to-[#22d3ee] bg-clip-text text-transparent', sample: 'GRADIENT TEXT' },
  ];

  // ─── Spacing ─────────────────────────────────────────────────────────
  const spacingTokens = [
    { name: '4px', value: '4px', tw: 'p-1', desc: 'Micro gap' },
    { name: '5px', value: '5px', tw: 'gap-[5px]', desc: 'Nav item gap' },
    { name: '8px', value: '8px', tw: 'p-2', desc: 'Icon padding' },
    { name: '12px', value: '12px', tw: 'p-3', desc: 'Small inner pad' },
    { name: '14px', value: '14px', tw: 'px-[14px]', desc: 'Breadcrumb pad-x' },
    { name: '16px', value: '16px', tw: 'px-4', desc: 'Nav pad, base' },
    { name: '18px', value: '18px', tw: 'px-[18px]', desc: 'Card inner pad' },
    { name: '20px', value: '20px', tw: 'pt-[20px]', desc: 'Section top gap' },
    { name: '24px', value: '24px', tw: 'gap-6', desc: 'Section gap' },
    { name: '33px', value: '33px', tw: 'mt-[33px]', desc: 'Header top margin' },
  ];

  const radiusTokens = [
    { name: '5px', tw: 'rounded-[5px]', desc: 'Badge' },
    { name: '8px', tw: 'rounded-[8px]', desc: 'Button, card, nav item' },
    { name: '10px', tw: 'rounded-[10px]', desc: 'Banner nav btn' },
    { name: '12px', tw: 'rounded-xl', desc: 'Blog card' },
    { name: '16px', tw: 'rounded-2xl', desc: 'Banner section' },
    { name: '9999px', tw: 'rounded-full', desc: 'Avatar, dot indicator' },
  ];
</script>

<svelte:head>
  <title>Templates | Design System</title>
</svelte:head>

<!-- Root theme wrapper -->
<div data-theme={theme} class="ds-root">

  <!-- Top bar -->
  <header class="ds-topbar">
    <div class="ds-topbar-inner">
      <div class="ds-logo">
        <span class="ds-logo-dot"></span>
        <span class="ds-logo-text">Design System</span>
        <span class="ds-logo-version">v1.0</span>
      </div>
      <div class="ds-topbar-right">
        <a href="/" class="ds-back-link">← Back to site</a>
        <button class="ds-theme-btn" onclick={toggleTheme} title="Toggle theme">
          {#if theme === 'dark'}
            <Sun size={16} />
            <span>Light</span>
          {:else}
            <Moon size={16} />
            <span>Dark</span>
          {/if}
        </button>
      </div>
    </div>
  </header>

  <div class="ds-layout">

    <!-- Sidebar -->
    <aside class="ds-sidebar">
      <nav class="ds-sidenav">
        <div class="ds-sidenav-group">
          <span class="ds-sidenav-label">Foundations</span>
          {#each sections.slice(0,3) as s}
            <button
              class="ds-sidenav-item {activeSection === s.id ? 'active' : ''}"
              onclick={() => { activeSection = s.id; document.getElementById(s.id)?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }}
            >
              {s.label}
            </button>
          {/each}
        </div>
        <div class="ds-sidenav-group">
          <span class="ds-sidenav-label">Components</span>
          {#each sections.slice(3) as s}
            <button
              class="ds-sidenav-item {activeSection === s.id ? 'active' : ''}"
              onclick={() => { activeSection = s.id; document.getElementById(s.id)?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }}
            >
              {s.label}
            </button>
          {/each}
        </div>
      </nav>
    </aside>

    <!-- Main content -->
    <main class="ds-main">

      <!-- Hero -->
      <div class="ds-hero">
        <h1 class="ds-hero-title">TheFoxxStuff<br><span class="ds-hero-accent">Design System</span></h1>
        <p class="ds-hero-desc">Полная библиотека токенов, компонентов и паттернов дизайна проекта. Тёмная и светлая тема, DrukWideCyr + Golos Text.</p>
      </div>

      <!-- ── COLORS ─────────────────────────────────────────────────── -->
      <section id="colors" class="ds-section">
        <h2 class="ds-section-title">Colors</h2>
        <p class="ds-section-desc">Семантические CSS-переменные, адаптированные под обе темы. Базовая палитра — монохром + три акцентных цвета.</p>
        <div class="ds-color-grid">
          {#each colorTokens as token}
            {@const color = theme === 'dark' ? token.dark : token.light}
            <button class="ds-color-card" onclick={() => copy(token.var, token.var)} title="Copy token name">
              <div class="ds-color-swatch" style="background: {color};"></div>
              <div class="ds-color-info">
                <span class="ds-color-name">{token.name}</span>
                <code class="ds-color-var">{token.var}</code>
                <span class="ds-color-desc">{token.desc}</span>
                <code class="ds-color-hex">{color}</code>
              </div>
              <div class="ds-copy-icon">
                {#if copiedKey === token.var}<Check size={12} />{:else}<Copy size={12} />{/if}
              </div>
            </button>
          {/each}
        </div>
      </section>

      <!-- ── TYPOGRAPHY ────────────────────────────────────────────── -->
      <section id="typography" class="ds-section">
        <h2 class="ds-section-title">Typography</h2>
        <p class="ds-section-desc">Два шрифта: <strong>DrukWideCyr</strong> (Display, заголовки) и <strong>Golos Text</strong> (тело, UI).</p>

        <div class="ds-type-grid">
          {#each typeScale as t}
            <div class="ds-type-card">
              <div class="ds-type-sample">
                <span class="{t.class}">{t.sample}</span>
              </div>
              <div class="ds-type-meta">
                <span class="ds-type-label">{t.label}</span>
                <div class="ds-type-specs">
                  <code>{t.size}</code>
                  <code>{t.font}</code>
                  <code>lh {t.lineH}</code>
                </div>
                <button class="ds-copy-btn" onclick={() => copy(t.class, t.label)}>
                  {#if copiedKey === t.label}<Check size={10} /> Copied{:else}<Copy size={10} /> Copy class{/if}
                </button>
              </div>
            </div>
          {/each}
        </div>

        <!-- Font specimens -->
        <div class="ds-font-specimens">
          <div class="ds-font-specimen">
            <span class="ds-specimen-label">DrukWideCyr — Display font</span>
            <div style="font-family: DrukWideCyr, sans-serif; font-size: 48px; line-height: 1; letter-spacing: 0.02em;" class="text-[--w]">ABCDEFGHIJKLMNOPQRSTUVWXYZ<br>0123456789</div>
          </div>
          <div class="ds-font-specimen">
            <span class="ds-specimen-label">Golos Text — Body font</span>
            <div style="font-family: 'Golos-Regular', system-ui, sans-serif; font-size: 18px; line-height: 1.6;" class="text-[--w]">
              The quick brown fox jumps over the lazy dog.<br>
              <span style="font-weight: 600;">Semi-bold weight 600.</span>
              <span style="opacity: 0.6;"> Muted secondary text rgba(255,255,255,0.6).</span>
            </div>
          </div>
        </div>
      </section>

      <!-- ── SPACING & RADIUS ──────────────────────────────────────── -->
      <section id="spacing" class="ds-section">
        <h2 class="ds-section-title">Spacing & Radius</h2>
        <p class="ds-section-desc">Ключевые отступы и радиусы. Базовая единица — 4px/8px, радиусы — 8px для большинства компонентов.</p>

        <div class="ds-subsection">
          <h3 class="ds-subsection-title">Spacing tokens</h3>
          <div class="ds-spacing-list">
            {#each spacingTokens as s}
              <div class="ds-spacing-item">
                <div class="ds-spacing-bar-wrap">
                  <div class="ds-spacing-bar" style="width: {s.value}; height: {s.value}; max-width: 80px; max-height: 20px; min-height: 4px;"></div>
                </div>
                <code class="ds-spacing-val">{s.value}</code>
                <code class="ds-spacing-tw">{s.tw}</code>
                <span class="ds-spacing-desc">{s.desc}</span>
              </div>
            {/each}
          </div>
        </div>

        <div class="ds-subsection">
          <h3 class="ds-subsection-title">Border radius</h3>
          <div class="ds-radius-grid">
            {#each radiusTokens as r}
              <div class="ds-radius-card">
                <div class="ds-radius-demo" style="border-radius: {r.name};"></div>
                <code class="ds-radius-val">{r.name}</code>
                <code class="ds-radius-tw">{r.tw}</code>
                <span class="ds-radius-desc">{r.desc}</span>
              </div>
            {/each}
          </div>
        </div>
      </section>

      <!-- ── BUTTONS ───────────────────────────────────────────────── -->
      <section id="buttons" class="ds-section">
        <h2 class="ds-section-title">Buttons</h2>
        <p class="ds-section-desc">Базовый компонент <code class="ds-inline-code">Button.svelte</code>. Поддерживает <code class="ds-inline-code">href</code>, <code class="ds-inline-code">iconLeft</code>, <code class="ds-inline-code">iconRight</code>.</p>

        <div class="ds-component-row wrap">

          <!-- Default button -->
          <div class="ds-demo-card">
            <div class="ds-demo-preview center">
              <button class="inline-flex items-center justify-center gap-[4px] px-[12px] py-[6px] bg-[--w5] hover:bg-[--w8] text-[--w60] hover:text-[--w] rounded-[8px] transition-all duration-200 text-[14px] font-medium tracking-wide">
                Default Button
              </button>
            </div>
            <div class="ds-demo-code">
              <button class="ds-copy-btn" onclick={() => copy('class="inline-flex items-center justify-center gap-[4px] px-[12px] py-[6px] bg-[--w5] hover:bg-[--w8] text-[--w60] hover:text-[--w] rounded-[8px] transition-all"', 'btn-default')}>
                {#if copiedKey === 'btn-default'}<Check size={10} />Copied{:else}<Copy size={10} />Copy{/if}
              </button>
              <code>bg-[--w5] hover:bg-[--w8]<br>text-[--w60] hover:text-[--w]<br>px-[12px] py-[6px] rounded-[8px]</code>
            </div>
          </div>

          <!-- Button with right icon -->
          <div class="ds-demo-card">
            <div class="ds-demo-preview center">
              <button class="inline-flex items-center justify-center gap-[4px] px-[12px] py-[6px] bg-[--w5] hover:bg-[--w8] text-[--w60] hover:text-[--w] rounded-[8px] transition-all duration-200 group">
                <span class="text-[14px] font-medium tracking-wide">Show more</span>
                <ChevronRight size={20} strokeWidth={2.5} class="group-hover:text-[--w]" />
              </button>
            </div>
            <div class="ds-demo-code">
              <code>iconRight={"{ChevronRight}"}</code>
            </div>
          </div>

          <!-- Primary CTA -->
          <div class="ds-demo-card">
            <div class="ds-demo-preview center">
              <button class="inline-flex items-center justify-center gap-2 px-4 py-2 bg-accent-green text-dark-950 hover:bg-accent-green/90 rounded-lg text-sm font-medium transition-all">
                BUY ON BANDCAMP
              </button>
            </div>
            <div class="ds-demo-code">
              <code>bg-accent-green text-dark-950<br>hover:bg-accent-green/90</code>
            </div>
          </div>

          <!-- Secondary -->
          <div class="ds-demo-card">
            <div class="ds-demo-preview center">
              <button class="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-[8px] border text-sm font-medium transition-all" style="border-color: var(--w18); color: var(--w60);">
                ALBUM PAGE
              </button>
            </div>
            <div class="ds-demo-code">
              <code>border border-[--w18]<br>text-[--w60] rounded-[8px]</code>
            </div>
          </div>

          <!-- Back link -->
          <div class="ds-demo-card">
            <div class="ds-demo-preview center">
              <a href="#" class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all duration-100" style="color: var(--w60); background: var(--w5);">
                ← Back to arts
              </a>
            </div>
            <div class="ds-demo-code">
              <code>bg-[--w5] hover:bg-[--w8]<br>text-[--w60] hover:text-[--w]<br>rounded-lg</code>
            </div>
          </div>

          <!-- Danger -->
          <div class="ds-demo-card">
            <div class="ds-demo-preview center">
              <button class="inline-flex items-center justify-center gap-2 px-4 py-2 bg-accent-red/10 hover:bg-accent-red/20 text-red-400 hover:text-red-300 rounded-[8px] text-sm font-medium transition-all">
                Delete
              </button>
            </div>
            <div class="ds-demo-code">
              <code>bg-accent-red/10<br>text-red-400 rounded-[8px]</code>
            </div>
          </div>

        </div>

        <!-- Filter button (special) -->
        <div class="ds-subsection">
          <h3 class="ds-subsection-title">Filter / Sort button</h3>
          <div class="ds-component-row">
            <div class="ds-demo-card" style="flex: 1">
              <div class="ds-demo-preview center" style="gap: 8px;">
                <button class="filter">
                  Sort by newest
                </button>
                <button class="filter" style="color: var(--w);">
                  Sort by oldest
                </button>
              </div>
              <div class="ds-demo-code">
                <code>.filter class:<br>bg-[--w5] text-[--w60]<br>hover:text-[--w] hover:bg-[--w8]</code>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ── BADGES & TAGS ─────────────────────────────────────────── -->
      <section id="badges" class="ds-section">
        <h2 class="ds-section-title">Badges & Tags</h2>
        <p class="ds-section-desc">Бейджи для статусов, тегов и метрик.</p>

        <div class="ds-component-row wrap">

          <!-- NEW RELEASE badge -->
          <div class="ds-demo-card">
            <div class="ds-demo-preview center">
              <span style="font-family: DrukWideCyr; background: var(--green); color: #000; font-size: 11px; letter-spacing: 0.05em; padding: 4px 10px; border-radius: 5px;">NEW RELEASE</span>
            </div>
            <div class="ds-demo-code">
              <code>bg-[--green] text-black<br>font-display text-[11px]<br>rounded-[5px] px-[10px]</code>
            </div>
          </div>

          <!-- Badge component -->
          <div class="ds-demo-card">
            <div class="ds-demo-preview center" style="gap: 8px; flex-wrap: wrap;">
              <div class="inline-flex items-center gap-[6px] px-[8px] py-[4px] rounded-[5px] h-[26px]" style="background: var(--w5); color: var(--w60);">
                <Calendar size={14} />
                <span style="font-size: 14px; white-space: nowrap;">28 April, 2024</span>
              </div>
              <div class="inline-flex items-center gap-[6px] px-[8px] py-[4px] rounded-[5px] h-[26px]" style="background: var(--w5); color: var(--w60);">
                <Eye size={14} />
                <span style="font-size: 14px; white-space: nowrap;">512 views</span>
              </div>
            </div>
            <div class="ds-demo-code">
              <code>Badge.svelte<br>bg-[--w5] h-[26px]<br>rounded-[5px] text-[14px]</code>
            </div>
          </div>

          <!-- Year pill -->
          <div class="ds-demo-card">
            <div class="ds-demo-preview center" style="gap: 8px;">
              <button style="background: var(--w5); color: var(--w60); border-radius: 8px; padding: 6px 14px; font-size: 14px;">2023</button>
              <button style="background: var(--w8); color: var(--w); border-radius: 8px; padding: 6px 14px; font-size: 14px;">2022</button>
              <button style="background: var(--w5); color: var(--w60); border-radius: 8px; padding: 6px 14px; font-size: 14px;">2021</button>
            </div>
            <div class="ds-demo-code">
              <code>Year filter pill<br>bg-[--w5]/[--w8] rounded-[8px]<br>px-[14px] py-[6px]</code>
            </div>
          </div>

          <!-- Online indicator -->
          <div class="ds-demo-card">
            <div class="ds-demo-preview center" style="gap: 16px;">
              <div class="inline-flex items-center gap-2" style="font-size: 12px; color: var(--w60);">
                <div style="width:8px;height:8px;border-radius:50%;background:#4ade80;" class="animate-pulse"></div>
                Connected
              </div>
              <div class="inline-flex items-center gap-2" style="font-size: 12px; color: var(--w60);">
                <div style="width:8px;height:8px;border-radius:50%;background:#ef4444;" class="animate-pulse"></div>
                Offline
              </div>
            </div>
            <div class="ds-demo-code">
              <code>Status dot<br>w-2 h-2 rounded-full<br>bg-accent-green/red animate-pulse</code>
            </div>
          </div>

          <!-- Admin badge -->
          <div class="ds-demo-card">
            <div class="ds-demo-preview center">
              <span class="inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded" style="color: #4ade80; background: rgba(74,222,128,0.1);">
                <Shield size={9} /> ADMIN
              </span>
            </div>
            <div class="ds-demo-code">
              <code>text-accent-green<br>bg-accent-green/10<br>text-[10px] rounded px-1.5</code>
            </div>
          </div>

        </div>
      </section>

      <!-- ── CARDS ─────────────────────────────────────────────────── -->
      <section id="cards" class="ds-section">
        <h2 class="ds-section-title">Cards</h2>
        <p class="ds-section-desc">Карточные компоненты: Music, Blog, Art, Featured Release.</p>

        <div class="ds-cards-showcase">

          <!-- Music card -->
          <div class="ds-demo-card full">
            <div class="ds-demo-label">MusicCard.svelte</div>
            <div class="ds-demo-preview" style="padding: 24px;">
              <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; max-width: 480px;">
                {#each [1,2,3] as _}
                  <div style="background: var(--w5); border-radius: 8px; padding: 18px; transition: background 0.1s;" class="hover:bg-[--w8]">
                    <div style="aspect-ratio: 1; background: var(--w8); border-radius: 8px; margin-bottom: 14px;"></div>
                    <span style="font-size: 18px; color: var(--w);">Album Title</span>
                    <p style="font-size: 14px; color: var(--w60); margin-top: 2px;">May 25, 2022</p>
                  </div>
                {/each}
              </div>
            </div>
            <div class="ds-demo-code">
              <code>bg-[--w5] hover:bg-[--w8]<br>rounded-[8px] px-[18px] py-[18px]<br>aspect-square cover image<br>text-[18px] + text-[14px] meta</code>
            </div>
          </div>

          <!-- Blog card -->
          <div class="ds-demo-card full">
            <div class="ds-demo-label">BlogCard.svelte</div>
            <div class="ds-demo-preview" style="padding: 24px;">
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; max-width: 600px;">
                {#each [1,2] as _}
                  <div style="background: var(--w5); border-radius: 12px; overflow: hidden;" class="hover:bg-[--w8]">
                    <div style="padding: 18px 18px 0;">
                      <div style="aspect-ratio: 16/10; background: var(--w8); border-radius: 8px;"></div>
                    </div>
                    <div style="padding: 12px 18px 18px;">
                      <h3 style="font-size: 18px; font-weight: 700; color: var(--w); margin-bottom: 4px; line-height: 1.3;">Post title goes here</h3>
                      <p style="font-size: 14px; color: var(--w60); margin-bottom: 8px;">Short excerpt text preview...</p>
                      <div style="display: flex; justify-content: space-between; padding-top: 12px; border-top: 1px solid var(--w8);">
                        <span style="font-size: 14px; color: #4ade80; display: flex; align-items: center; gap: 4px;"><Calendar size={14} /> Apr 28</span>
                        <span style="font-size: 14px; color: var(--w60); display: flex; align-items: center; gap: 4px;"><Eye size={14} /> 512 views</span>
                      </div>
                    </div>
                  </div>
                {/each}
              </div>
            </div>
            <div class="ds-demo-code">
              <code>bg-[--w5] rounded-[12px]<br>16:10 cover ratio<br>px-[18px] pt-[12px] pb-[18px]<br>footer: calendar-green + eye-icon</code>
            </div>
          </div>

          <!-- Art card grid -->
          <div class="ds-demo-card full">
            <div class="ds-demo-label">ArtCard.svelte — Bento grid layout</div>
            <div class="ds-demo-preview" style="padding: 24px;">
              <div style="display: grid; grid-template-columns: repeat(4,1fr); grid-template-rows: repeat(3, 80px); gap: 8px; max-width: 480px;">
                <div style="grid-column: span 2; grid-row: span 2; background: var(--w8); border-radius: 8px;"></div>
                <div style="background: var(--w8); border-radius: 8px;"></div>
                <div style="background: var(--w8); border-radius: 8px;"></div>
                <div style="grid-column: span 2; grid-row: span 2; background: var(--w8); border-radius: 8px;"></div>
                <div style="background: var(--w8); border-radius: 8px;"></div>
                <div style="background: var(--w8); border-radius: 8px;"></div>
              </div>
            </div>
            <div class="ds-demo-code">
              <code>grid-cols-4 grid-rows-3 gap-4<br>arts[0]: col-span-2 row-span-2<br>arts[5]: col-span-2 row-span-2<br>Bento masonry layout</code>
            </div>
          </div>

          <!-- .card class -->
          <div class="ds-demo-card full">
            <div class="ds-demo-label">.card — Base utility class</div>
            <div class="ds-demo-preview center" style="padding: 24px;">
              <div class="card" style="padding: 24px; max-width: 320px; width: 100%;">
                <p style="color: var(--w60); font-size: 14px;">This uses the <code style="color: #4ade80;">.card</code> class which applies <code style="color: #4ade80;">bg-dark-900 rounded-xl overflow-hidden</code>. Used for article wrappers, modals, settings panels.</p>
              </div>
            </div>
            <div class="ds-demo-code">
              <code>.card =<br>bg-dark-900 rounded-xl overflow-hidden<br><br>In light theme: bg-white/bg-gray-50</code>
            </div>
          </div>

        </div>
      </section>

      <!-- ── INPUTS ────────────────────────────────────────────────── -->
      <section id="inputs" class="ds-section">
        <h2 class="ds-section-title">Inputs</h2>
        <p class="ds-section-desc">Поля ввода, поиск, textarea, select.</p>

        <div class="ds-component-row wrap">

          <!-- Search input -->
          <div class="ds-demo-card" style="flex: 1; min-width: 260px;">
            <div class="ds-demo-label">Search field (blog/arts page)</div>
            <div class="ds-demo-preview center">
              <div style="display: flex; align-items: center; background: var(--w5); border: 1px solid var(--w12); border-radius: 8px; padding: 8px 14px; gap: 8px; width: 200px;">
                <Search size={16} style="color: var(--w60); flex-shrink: 0;" />
                <input placeholder="Search..." style="background: transparent; border: none; outline: none; font-size: 14px; color: var(--w); width: 100%;" />
              </div>
            </div>
            <div class="ds-demo-code">
              <code>bg-[--w5] border-[--w12]<br>rounded-[8px] px-[14px] py-2<br>Search icon + text input</code>
            </div>
          </div>

          <!-- Standard input -->
          <div class="ds-demo-card" style="flex: 1; min-width: 260px;">
            <div class="ds-demo-label">.input — Form field</div>
            <div class="ds-demo-preview center">
              <div style="width: 200px;">
                <label style="display: block; font-size: 14px; color: var(--w60); margin-bottom: 4px;">Label</label>
                <input class="input" placeholder="Enter value..." />
              </div>
            </div>
            <div class="ds-demo-code">
              <code>.input =<br>bg-dark-800 border border-dark-700<br>rounded-lg px-4 py-2<br>focus:border-accent-green/50</code>
            </div>
          </div>

          <!-- Nav search -->
          <div class="ds-demo-card" style="flex: 1; min-width: 260px;">
            <div class="ds-demo-label">Inline search (header)</div>
            <div class="ds-demo-preview center">
              <input placeholder="Search..." style="background: transparent; border: none; border-bottom: 1px solid var(--w18); font-size: 14px; color: var(--w); outline: none; padding: 4px 4px; width: 160px;" />
            </div>
            <div class="ds-demo-code">
              <code>bg-transparent<br>border-b border-[--w18]<br>outline-none px-1 py-1<br>placeholder:text-[--w30]</code>
            </div>
          </div>

          <!-- Textarea -->
          <div class="ds-demo-card" style="flex: 1; min-width: 260px;">
            <div class="ds-demo-label">.textarea</div>
            <div class="ds-demo-preview center">
              <textarea class="textarea" rows="3" placeholder="Write something..." style="width: 200px;"></textarea>
            </div>
            <div class="ds-demo-code">
              <code>.textarea =<br>bg-dark-800 border-dark-700<br>rounded-lg px-4 py-3<br>resize-none</code>
            </div>
          </div>

        </div>
      </section>

      <!-- ── NAVIGATION ────────────────────────────────────────────── -->
      <section id="navigation" class="ds-section">
        <h2 class="ds-section-title">Navigation</h2>
        <p class="ds-section-desc">Хедер, breadcrumb, pagination, pagination с вводом.</p>

        <!-- Breadcrumb -->
        <div class="ds-subsection">
          <h3 class="ds-subsection-title">Breadcrumb</h3>
          <div class="ds-demo-card full">
            <div class="ds-demo-preview" style="padding: 20px;">
              <nav style="display: flex; align-items: center; gap: 4px; font-size: 14px; color: var(--w60);">
                <a href="#" style="display: inline-flex; align-items: center; gap: 12px; padding: 8px 14px; border-radius: 8px; color: var(--w60); text-decoration: none; transition: background 0.1s;" class="hover:bg-[--w5]">
                  <Home size={20} /> Home
                </a>
                <ChevronRight size={14} style="color: var(--w30); flex-shrink: 0;" />
                <a href="#" style="display: inline-flex; align-items: center; gap: 12px; padding: 8px 14px; border-radius: 8px; color: var(--w60); text-decoration: none;" class="hover:bg-[--w5]">Music</a>
                <ChevronRight size={14} style="color: var(--w30); flex-shrink: 0;" />
                <span style="display: inline-flex; align-items: center; gap: 12px; padding: 8px 14px; border-radius: 8px; color: var(--w);">ASTRAL SUMMER</span>
              </nav>
            </div>
            <div class="ds-demo-code">
              <code>Breadcrumb.svelte<br>items=[{"{href, label}"}]<br>.btn-breadcrumb: px-[14px] py-[8px]<br>Last item: text-[--w] (active)</code>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div class="ds-subsection">
          <h3 class="ds-subsection-title">Pagination</h3>
          <div class="ds-demo-card full">
            <div class="ds-demo-preview" style="padding: 20px;">
              <div style="display: flex; align-items: center; gap: 12px; height: 36px; font-family: inherit; user-select: none;">
                <div style="display: flex; align-items: center; gap: 5px; padding: 0 12px; height: 36px; border-radius: 8px; background: var(--w5);">
                  <span style="font-size: 14px; color: var(--w60); white-space: nowrap;">Page —</span>
                  <button style="display:flex;align-items:center;justify-content:center;min-width:22px;height:22px;padding:0 6px;font-size:12px;font-weight:500;color:var(--w);background:var(--w12);border-radius:4px;border:none;cursor:pointer;">1</button>
                </div>
                <div style="display: flex; gap: 6px;">
                  {#each [1,2,3,null,5] as p}
                    {#if p === null}
                      <div style="width:36px;height:36px;display:flex;align-items:center;justify-content:center;color:var(--w60);">...</div>
                    {:else}
                      <button style="width:36px;height:36px;display:flex;align-items:center;justify-content:center;border-radius:8px;font-size:14px;font-weight:500;border:none;cursor:pointer;background:{p===1 ? 'var(--w12)' : 'var(--w5)'};color:{p===1 ? 'var(--w)' : 'var(--w60)'};">{p}</button>
                    {/if}
                  {/each}
                </div>
                <div style="display: flex; gap: 6px; margin-left: auto;">
                  <button style="width:36px;height:36px;display:flex;align-items:center;justify-content:center;border-radius:8px;background:var(--w5);color:var(--w60);border:none;cursor:pointer;opacity:0.2;">‹</button>
                  <button style="width:36px;height:36px;display:flex;align-items:center;justify-content:center;border-radius:8px;background:var(--w5);color:var(--w60);border:none;cursor:pointer;">›</button>
                </div>
              </div>
            </div>
            <div class="ds-demo-code">
              <code>Pagination.svelte<br>currentPage + totalPages + onPageChange<br>Click page number → editable input<br>Red highlight on invalid range</code>
            </div>
          </div>
        </div>

      </section>

      <!-- ── LAYOUT ────────────────────────────────────────────────── -->
      <section id="layout" class="ds-section">
        <h2 class="ds-section-title">Layout</h2>
        <p class="ds-section-desc">Контейнеры, сетки, максимальные ширины страниц.</p>

        <div class="ds-layout-tokens">
          <div class="ds-layout-token">
            <div class="ds-layout-demo" style="max-width: 100%; height: 40px; position: relative;">
              <div style="position: absolute; inset: 0; background: var(--w5); border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 12px; color: var(--w60);">max-w-[828px] — Main container</div>
            </div>
            <code class="ds-layout-code">max-width: 828px · px-4 (mobile) · px-0 (pc)</code>
          </div>
          <div class="ds-layout-token">
            <div class="ds-layout-demo">
              <div style="display: grid; grid-template-columns: repeat(4,1fr); gap: 8px; height: 40px;">
                {#each [1,2,3,4] as _}
                  <div style="background: var(--w8); border-radius: 4px;"></div>
                {/each}
              </div>
            </div>
            <code class="ds-layout-code">grid-cols-2 md:grid-cols-4 — Music cards</code>
          </div>
          <div class="ds-layout-token">
            <div class="ds-layout-demo">
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; height: 40px;">
                {#each [1,2] as _}
                  <div style="background: var(--w8); border-radius: 4px;"></div>
                {/each}
              </div>
            </div>
            <code class="ds-layout-code">grid md:grid-cols-2 — Blog cards</code>
          </div>
          <div class="ds-layout-token">
            <div class="ds-layout-demo">
              <div style="display: grid; grid-template-columns: repeat(4,1fr); grid-template-rows: repeat(3, 16px); gap: 4px;">
                <div style="grid-column: span 2; grid-row: span 2; background: var(--w8); border-radius: 3px;"></div>
                <div style="background: var(--w12); border-radius: 3px;"></div>
                <div style="background: var(--w12); border-radius: 3px;"></div>
                <div style="grid-column: span 2; grid-row: span 2; background: var(--w8); border-radius: 3px;"></div>
                <div style="background: var(--w12); border-radius: 3px;"></div>
                <div style="background: var(--w12); border-radius: 3px;"></div>
              </div>
            </div>
            <code class="ds-layout-code">grid-cols-4 grid-rows-3 — Arts bento</code>
          </div>
          <div class="ds-layout-token">
            <div class="ds-layout-demo">
              <div style="display: flex; flex-direction: column; gap: 6px;">
                <div style="height: 12px; background: var(--w8); border-radius: 3px; width: 60%;"></div>
                <div style="display: flex; gap: 8px;">
                  <div style="width: 120px; height: 120px; background: var(--w8); border-radius: 6px; flex-shrink: 0;"></div>
                  <div style="flex: 1; display: flex; flex-direction: column; gap: 6px; padding: 8px 0;">
                    <div style="height: 10px; background: var(--w12); border-radius: 3px; width: 80%;"></div>
                    <div style="height: 8px; background: var(--w5); border-radius: 3px; width: 60%;"></div>
                    <div style="height: 8px; background: var(--w5); border-radius: 3px; width: 50%;"></div>
                  </div>
                </div>
              </div>
            </div>
            <code class="ds-layout-code">flex-col md:flex-row gap-8 — Music detail</code>
          </div>
          <div class="ds-layout-token">
            <div class="ds-layout-demo">
              <div style="height: 40px; background: var(--w5); border-radius: 6px; display: flex; align-items: center; justify-content: space-between; padding: 0 14px;">
                <span style="font-size: 11px; color: var(--w60);">© 2024</span>
                <div style="display: flex; gap: 8px;">
                  <div style="height: 20px; width: 60px; background: var(--w8); border-radius: 4px;"></div>
                  <div style="height: 20px; width: 28px; background: var(--w8); border-radius: 4px;"></div>
                </div>
              </div>
            </div>
            <code class="ds-layout-code">Footer: max-w-[828px] bg-[--w5] p-[14px_30px] rounded-[8px]</code>
          </div>
        </div>
      </section>

    </main>
  </div>

</div>

<style>
  /* ─── Root theme vars ───────────────────────────────────────────────── */
  .ds-root {
    --bg: #111111;
    --fg: #ffffff;
    --fg60: rgba(255,255,255,0.60);
    --fg30: rgba(255,255,255,0.30);
    --fg18: rgba(255,255,255,0.18);
    --fg12: rgba(255,255,255,0.12);
    --fg8: rgba(255,255,255,0.08);
    --fg5: rgba(255,255,255,0.05);
    --card-bg: rgba(255,255,255,0.035);
    --card-border: rgba(255,255,255,0.09);
    --sidebar-bg: rgba(255,255,255,0.03);
    --topbar-bg: rgba(10,10,10,0.85);
    --code-bg: rgba(255,255,255,0.06);
    --accent: #4ade80;
    --accent2: #22d3ee;
    --green: #73EE07;

    /* Override global --w vars for the page scope */
    --w: var(--fg);
    --w60: var(--fg60);
    --w30: var(--fg30);
    --w18: var(--fg18);
    --w12: var(--fg12);
    --w8: var(--fg8);
    --w5: var(--fg5);

    min-height: 100vh;
    background: var(--bg);
    color: var(--fg);
    font-family: 'Golos-Regular', system-ui, sans-serif;
    transition: background 0.25s, color 0.25s;
  }

  .ds-root[data-theme="light"] {
    --bg: #f0efeb;
    --fg: #111111;
    --fg60: rgba(0,0,0,0.55);
    --fg30: rgba(0,0,0,0.30);
    --fg18: rgba(0,0,0,0.16);
    --fg12: rgba(0,0,0,0.10);
    --fg8: rgba(0,0,0,0.07);
    --fg5: rgba(0,0,0,0.04);
    --card-bg: rgba(255,255,255,0.7);
    --card-border: rgba(0,0,0,0.08);
    --sidebar-bg: rgba(255,255,255,0.5);
    --topbar-bg: rgba(240,239,235,0.9);
    --code-bg: rgba(0,0,0,0.06);
    --accent: #16a34a;
    --accent2: #0891b2;
    --green: #4dbd00;
  }

  /* ─── Topbar ────────────────────────────────────────────────────────── */
  .ds-topbar {
    position: sticky;
    top: 0;
    z-index: 100;
    background: var(--topbar-bg);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--fg8);
  }
  .ds-topbar-inner {
    max-width: 1320px;
    margin: 0 auto;
    padding: 12px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .ds-logo {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .ds-logo-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
  }
  .ds-logo-text {
    font-family: DrukWideCyr, sans-serif;
    font-size: 14px;
    letter-spacing: 0.05em;
    color: var(--fg);
  }
  .ds-logo-version {
    font-size: 11px;
    color: var(--fg30);
    background: var(--fg8);
    padding: 2px 6px;
    border-radius: 4px;
  }
  .ds-topbar-right {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .ds-back-link {
    font-size: 13px;
    color: var(--fg60);
    text-decoration: none;
    padding: 6px 12px;
    border-radius: 6px;
    transition: background 0.15s, color 0.15s;
  }
  .ds-back-link:hover {
    background: var(--fg8);
    color: var(--fg);
  }
  .ds-theme-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 14px;
    border-radius: 8px;
    border: 1px solid var(--fg12);
    background: var(--fg5);
    color: var(--fg60);
    font-size: 13px;
    cursor: pointer;
    transition: background 0.15s, color 0.15s, border-color 0.15s;
    font-family: inherit;
  }
  .ds-theme-btn:hover {
    background: var(--fg8);
    color: var(--fg);
    border-color: var(--fg18);
  }

  /* ─── Layout ────────────────────────────────────────────────────────── */
  .ds-layout {
    max-width: 1320px;
    margin: 0 auto;
    padding: 0 32px 80px;
    display: grid;
    grid-template-columns: 220px 1fr;
    gap: 48px;
    align-items: start;
  }

  /* ─── Sidebar ───────────────────────────────────────────────────────── */
  .ds-sidebar {
    position: sticky;
    top: 60px;
    padding: 24px 0;
  }
  .ds-sidenav {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }
  .ds-sidenav-group {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .ds-sidenav-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--fg30);
    padding: 0 12px;
    margin-bottom: 6px;
  }
  .ds-sidenav-item {
    display: block;
    width: 100%;
    text-align: left;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 14px;
    color: var(--fg60);
    background: none;
    border: none;
    cursor: pointer;
    transition: background 0.12s, color 0.12s;
    font-family: inherit;
  }
  .ds-sidenav-item:hover { background: var(--fg5); color: var(--fg); }
  .ds-sidenav-item.active { background: var(--fg8); color: var(--fg); }

  /* ─── Main ──────────────────────────────────────────────────────────── */
  .ds-main {
    padding: 32px 0 0;
    display: flex;
    flex-direction: column;
    gap: 80px;
  }

  /* ─── Hero ──────────────────────────────────────────────────────────── */
  .ds-hero {
    padding: 48px 0 16px;
    border-bottom: 1px solid var(--fg8);
  }
  .ds-hero-title {
    font-family: DrukWideCyr, sans-serif;
    font-size: clamp(36px, 5vw, 64px);
    line-height: 1.0;
    letter-spacing: 0.02em;
    color: var(--fg);
    margin-bottom: 16px;
  }
  .ds-hero-accent {
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .ds-hero-desc {
    font-size: 16px;
    color: var(--fg60);
    max-width: 560px;
    line-height: 1.6;
  }

  /* ─── Section ───────────────────────────────────────────────────────── */
  .ds-section {
    display: flex;
    flex-direction: column;
    gap: 24px;
    scroll-margin-top: 80px;
  }
  .ds-section-title {
    font-family: DrukWideCyr, sans-serif;
    font-size: 22px;
    letter-spacing: 0.04em;
    color: var(--fg);
    padding-bottom: 12px;
    border-bottom: 1px solid var(--fg8);
  }
  .ds-section-desc {
    font-size: 14px;
    color: var(--fg60);
    line-height: 1.6;
    margin-top: -12px;
  }
  .ds-subsection { display: flex; flex-direction: column; gap: 12px; }
  .ds-subsection-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--fg60);
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }

  /* ─── Color grid ────────────────────────────────────────────────────── */
  .ds-color-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 10px;
  }
  .ds-color-card {
    display: flex;
    flex-direction: column;
    gap: 0;
    border-radius: 10px;
    border: 1px solid var(--card-border);
    background: var(--card-bg);
    overflow: hidden;
    cursor: pointer;
    text-align: left;
    position: relative;
    transition: border-color 0.15s, transform 0.15s;
    font-family: inherit;
  }
  .ds-color-card:hover { border-color: var(--fg18); transform: translateY(-1px); }
  .ds-color-swatch { height: 64px; width: 100%; }
  .ds-color-info {
    padding: 10px 12px;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .ds-color-name { font-size: 13px; font-weight: 600; color: var(--fg); }
  .ds-color-var { font-size: 11px; color: var(--accent); font-family: monospace; }
  .ds-color-desc { font-size: 11px; color: var(--fg60); margin-top: 2px; }
  .ds-color-hex { font-size: 10px; color: var(--fg30); font-family: monospace; margin-top: 2px; }
  .ds-copy-icon {
    position: absolute;
    top: 8px;
    right: 8px;
    color: var(--fg30);
    background: var(--fg12);
    border-radius: 4px;
    padding: 3px;
    display: flex;
  }

  /* ─── Typography ────────────────────────────────────────────────────── */
  .ds-type-grid { display: flex; flex-direction: column; gap: 2px; }
  .ds-type-card {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 16px;
    align-items: center;
    padding: 16px 20px;
    border-radius: 10px;
    border: 1px solid var(--card-border);
    background: var(--card-bg);
    transition: border-color 0.15s;
  }
  .ds-type-card:hover { border-color: var(--fg18); }
  .ds-type-sample { overflow: hidden; }
  .ds-type-meta { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; min-width: 120px; }
  .ds-type-label { font-size: 11px; color: var(--fg30); text-transform: uppercase; letter-spacing: 0.08em; }
  .ds-type-specs { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }
  .ds-type-specs code { font-size: 10px; color: var(--fg60); background: var(--code-bg); padding: 2px 6px; border-radius: 3px; font-family: monospace; }

  .ds-font-specimens {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin-top: 8px;
  }
  .ds-font-specimen {
    padding: 24px;
    border-radius: 10px;
    border: 1px solid var(--card-border);
    background: var(--card-bg);
    display: flex;
    flex-direction: column;
    gap: 16px;
    overflow: hidden;
  }
  .ds-specimen-label { font-size: 11px; color: var(--fg30); text-transform: uppercase; letter-spacing: 0.08em; }

  /* ─── Spacing ───────────────────────────────────────────────────────── */
  .ds-spacing-list { display: flex; flex-direction: column; gap: 8px; }
  .ds-spacing-item {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 8px 16px;
    border-radius: 8px;
    border: 1px solid var(--card-border);
    background: var(--card-bg);
  }
  .ds-spacing-bar-wrap { width: 80px; display: flex; align-items: center; }
  .ds-spacing-bar { background: linear-gradient(90deg, var(--accent), var(--accent2)); border-radius: 2px; }
  .ds-spacing-val { font-size: 13px; font-family: monospace; color: var(--accent); width: 40px; }
  .ds-spacing-tw { font-size: 11px; font-family: monospace; color: var(--fg60); background: var(--code-bg); padding: 2px 6px; border-radius: 3px; }
  .ds-spacing-desc { font-size: 12px; color: var(--fg60); margin-left: auto; }

  .ds-radius-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 10px; }
  .ds-radius-card {
    padding: 16px;
    border-radius: 10px;
    border: 1px solid var(--card-border);
    background: var(--card-bg);
    display: flex;
    flex-direction: column;
    gap: 10px;
    align-items: center;
  }
  .ds-radius-demo { width: 48px; height: 48px; background: linear-gradient(135deg, var(--accent), var(--accent2)); opacity: 0.4; }
  .ds-radius-val { font-size: 13px; font-family: monospace; color: var(--accent); }
  .ds-radius-tw { font-size: 10px; font-family: monospace; color: var(--fg60); background: var(--code-bg); padding: 2px 6px; border-radius: 3px; text-align: center; }
  .ds-radius-desc { font-size: 11px; color: var(--fg60); text-align: center; }

  /* ─── Demo cards ────────────────────────────────────────────────────── */
  .ds-component-row {
    display: flex;
    gap: 10px;
  }
  .ds-component-row.wrap { flex-wrap: wrap; }
  .ds-demo-card {
    border-radius: 10px;
    border: 1px solid var(--card-border);
    background: var(--card-bg);
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  .ds-demo-card.full { flex: 1 1 100%; }
  .ds-demo-label {
    padding: 8px 14px;
    font-size: 11px;
    color: var(--fg30);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    border-bottom: 1px solid var(--card-border);
  }
  .ds-demo-preview {
    flex: 1;
    padding: 28px 20px;
    min-height: 80px;
  }
  .ds-demo-preview.center { display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 12px; }
  .ds-demo-code {
    padding: 10px 14px;
    border-top: 1px solid var(--card-border);
    background: var(--code-bg);
    font-size: 11px;
    font-family: monospace;
    color: var(--fg60);
    line-height: 1.6;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  /* ─── Cards showcase ────────────────────────────────────────────────── */
  .ds-cards-showcase { display: flex; flex-direction: column; gap: 10px; }

  /* ─── Copy button ───────────────────────────────────────────────────── */
  .ds-copy-btn {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    border-radius: 5px;
    border: 1px solid var(--card-border);
    background: var(--fg5);
    color: var(--fg60);
    font-size: 10px;
    cursor: pointer;
    transition: background 0.12s, color 0.12s;
    font-family: monospace;
  }
  .ds-copy-btn:hover { background: var(--fg8); color: var(--fg); }

  /* ─── Inline code ───────────────────────────────────────────────────── */
  .ds-inline-code {
    font-family: monospace;
    font-size: 13px;
    color: var(--accent);
    background: var(--code-bg);
    padding: 2px 6px;
    border-radius: 4px;
  }

  /* ─── Layout tokens ─────────────────────────────────────────────────── */
  .ds-layout-tokens { display: flex; flex-direction: column; gap: 10px; }
  .ds-layout-token {
    padding: 16px;
    border-radius: 10px;
    border: 1px solid var(--card-border);
    background: var(--card-bg);
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .ds-layout-demo { padding: 8px 0; }
  .ds-layout-code { font-size: 12px; font-family: monospace; color: var(--fg60); }

  /* ─── Responsive ────────────────────────────────────────────────────── */
  @media (max-width: 768px) {
    .ds-layout {
      grid-template-columns: 1fr;
      padding: 0 16px 60px;
    }
    .ds-sidebar { position: static; padding: 16px 0; }
    .ds-sidenav { flex-direction: row; flex-wrap: wrap; gap: 8px; }
    .ds-sidenav-group { flex-direction: row; flex-wrap: wrap; align-items: center; }
    .ds-sidenav-label { display: none; }
    .ds-topbar-inner { padding: 12px 16px; }
    .ds-color-grid { grid-template-columns: repeat(2, 1fr); }
  }
</style>
