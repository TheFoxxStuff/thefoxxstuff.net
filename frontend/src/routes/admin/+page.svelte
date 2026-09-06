<script>
  import { SEO } from "$lib/components";
  import { canonicalUrl } from "$lib/seo.js";
  import { api } from '$lib/api';
  import { LayoutDashboard, Music, FileText, Palette, Users, Image, Zap, Eye, ArrowUpRight } from "lucide-svelte";

  let { data: pageData } = $props();
  let stats = $derived(pageData.stats);
  let chartData = $derived(pageData.chartData);
  let topContent = $derived(pageData.topContent);
  let chartDays = $state(30);
  let chartLoading = $state(false);

  async function loadChart(days) {
    chartDays = days;
    chartLoading = true;
    try {
      chartData = await api.stats.viewsChart(days);
    } catch (e) {
      console.error(e);
    } finally {
      chartLoading = false;
    }
  }

  function getChartPath(data, key, maxValue, width, height) {
    if (!data || data.length === 0) return '';
    const points = data.map((d, i) => {
      const x = (i / Math.max(data.length - 1, 1)) * width;
      const y = height - (d[key] / Math.max(maxValue, 1)) * height;
      return `${x},${y}`;
    });
    return `M ${points.join(' L ')}`;
  }

  function getAreaPath(data, key, maxValue, width, height) {
    if (!data || data.length === 0) return '';
    const points = data.map((d, i) => {
      const x = (i / Math.max(data.length - 1, 1)) * width;
      const y = height - (d[key] / Math.max(maxValue, 1)) * height;
      return `${x},${y}`;
    });
    return `M 0,${height} L ${points.join(' L ')} L ${width},${height} Z`;
  }

  let statCards = $derived(stats ? [
    {
      label: 'Music Releases', value: stats.music.count, href: '/admin/music',
      subtitle: `${stats.music.views.toLocaleString()} views`,
      icon: Music, color: 'from-[#00FF88]/20 to-[#00FF88]/0', accent: 'text-[#00FF88]'
    },
    {
      label: 'Blog Posts', value: stats.blog.count, href: '/admin/blog',
      subtitle: `${stats.blog.views.toLocaleString()} views`,
      icon: FileText, color: 'from-[#00D4FF]/20 to-[#00D4FF]/0', accent: 'text-[#00D4FF]'
    },
    {
      label: 'Artworks', value: stats.arts.count, href: '/admin/arts',
      subtitle: `${stats.arts.views.toLocaleString()} views`,
      icon: Palette, color: 'from-purple-500/20 to-purple-500/0', accent: 'text-purple-400'
    },
    {
      label: 'Users', value: stats.users.count, href: '/admin/users',
      subtitle: 'Total accounts',
      icon: Users, color: 'from-pink-500/20 to-pink-500/0', accent: 'text-pink-400'
    },
    {
      label: 'Images', value: stats.images?.count || 0, href: '/admin/media',
      subtitle: 'Media files',
      icon: Image, color: 'from-cyan-400/20 to-cyan-400/0', accent: 'text-cyan-400'
    },
  ] : null);
</script>

<SEO titleFull="Admin Dashboard - TheFoxxStuff" noindex={true} url={canonicalUrl("/admin")} />

<div class="dashboard-v2">

  <!-- Hero Header -->
  <div class="dashboard-hero">
    <div class="dashboard-hero-content">
      <h1 class="font-display text-[28px] tracking-wide">
        Admin <span class="text-gradient">Dashboard</span>
      </h1>
      <div class="hero-subtitle">
        <Zap size="15" /> Site overview & quick stats
      </div>
    </div>
    <div class="hero-glow"></div>
    <div class="hero-glow hero-glow--right"></div>
  </div>

  {#if stats}

    <!-- Stat Cards Grid -->
    <div class="stats-grid">
      {#each statCards as card}
        <a href={card.href} class="stat-card">
          <div class="stat-card-bg bg-gradient-to-br {card.color}"></div>
          <div class="stat-card-content">
            <div class="stat-icon">
              <card.icon size={18} class={card.accent} />
            </div>
            <div class="stat-info">
              <div class="stat-label">{card.label}</div>
              <div class="stat-value">{card.value}</div>
              <div class="stat-subtitle">{card.subtitle}</div>
            </div>
          </div>
          <div class="stat-arrow">
            <ArrowUpRight size="16" />
          </div>
        </a>
      {/each}

      <!-- Total views card -->
      <a href="/admin" class="stat-card total-card">
        <div class="stat-card-bg bg-gradient-to-br from-[#00FF88]/10 via-[#00D4FF]/10 to-purple-500/10"></div>
        <div class="stat-card-content">
          <div class="stat-icon">
            <Eye size="18" class="text-gradient" />
          </div>
          <div class="stat-info">
            <div class="stat-label">Total Views</div>
            <div class="stat-value text-gradient">{stats.total_views.toLocaleString()}</div>
            <div class="stat-subtitle">Across all content</div>
          </div>
        </div>
        <div class="stat-arrow">
          <ArrowUpRight size="16" />
        </div>
      </a>
    </div>

    <!-- Chart Section -->
    <div class="section">
      <div class="section-card chart-card">
        <div class="section-header">
          <h2 class="section-title">
            <Eye size="16" class="text-[--w40]" />
            Views Over Time
          </h2>
          <div class="chart-filters">
            {#each [7, 14, 30, 90] as days}
              <button
                onclick={() => loadChart(days)}
                class="chart-filter-btn {chartDays === days ? 'active' : ''}"
              >
                {days}d
              </button>
            {/each}
          </div>
        </div>

        {#if chartLoading}
          <div class="chart-loading">
            <div class="spinner"></div>
            <span>Loading chart...</span>
          </div>
        {:else if chartData?.data}
          {@const data = chartData.data}
          {@const maxValue = Math.max(...data.map(d => d.total), 1)}
          {@const width = 800}
          {@const height = 220}

          <!-- Chart Legend -->
          <div class="chart-legend">
            <div class="legend-item">
              <span class="legend-dot" style="--c: #00FF88"></span>
              <span>Music ({chartData.summary.music.toLocaleString()})</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot" style="--c: #00D4FF"></span>
              <span>Blog ({chartData.summary.blog.toLocaleString()})</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot" style="--c: #A855F7"></span>
              <span>Arts ({chartData.summary.arts.toLocaleString()})</span>
            </div>
          </div>

          <div class="chart-wrapper">
            <svg viewBox="0 0 {width} {height + 30}" class="chart-svg">
              <defs>
                <linearGradient id="greenGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="#00FF88" stop-opacity="0.35"/>
                  <stop offset="100%" stop-color="#00FF88" stop-opacity="0"/>
                </linearGradient>
                <linearGradient id="cyanGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="#00D4FF" stop-opacity="0.35"/>
                  <stop offset="100%" stop-color="#00D4FF" stop-opacity="0"/>
                </linearGradient>
                <linearGradient id="purpleGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="#A855F7" stop-opacity="0.35"/>
                  <stop offset="100%" stop-color="#A855F7" stop-opacity="0"/>
                </linearGradient>
                <!-- Dot glow -->
                <filter id="dotGlow">
                  <feGaussianBlur stdDeviation="2" result="blur"/>
                  <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                </filter>
              </defs>

              <!-- Grid lines -->
              {#each [0, 0.25, 0.5, 0.75, 1] as ratio}
                <line x1="0" y1={height - ratio * height} x2={width} y2={height - ratio * height} stroke="rgba(255,255,255,0.04)" stroke-width="1"/>
                <text x="4" y={height - ratio * height - 6} fill="rgba(255,255,255,0.25)" font-size="9" font-family="Golos-Text, sans-serif">{Math.round(maxValue * ratio)}</text>
              {/each}

              <!-- Area fills -->
              <path d={getAreaPath(data, 'arts', maxValue, width, height)} fill="url(#purpleGrad)"/>
              <path d={getAreaPath(data, 'blog', maxValue, width, height)} fill="url(#cyanGrad)"/>
              <path d={getAreaPath(data, 'music', maxValue, width, height)} fill="url(#greenGrad)"/>

              <!-- Lines -->
              <path d={getChartPath(data, 'arts', maxValue, width, height)} fill="none" stroke="#A855F7" stroke-width="1.5" opacity="0.4"/>
              <path d={getChartPath(data, 'blog', maxValue, width, height)} fill="none" stroke="#00D4FF" stroke-width="1.5" opacity="0.5"/>
              <path d={getChartPath(data, 'music', maxValue, width, height)} fill="none" stroke="#00FF88" stroke-width="2"/>

              <!-- Date labels -->
              {#each data as d, i}
                {#if i % Math.ceil(data.length / 6) === 0 || i === data.length - 1}
                  <text x={(i / Math.max(data.length - 1, 1)) * width} y={height + 22} fill="rgba(255,255,255,0.22)" font-size="9" font-family="Golos-Text, sans-serif" text-anchor="middle">
                    {d.date.split('-').slice(1).join('/')}
                  </text>
                {/if}
              {/each}
            </svg>
          </div>
        {:else}
          <div class="chart-empty">No data available</div>
        {/if}
      </div>
    </div>

    <!-- Bottom Section: Top Content + Quick Actions -->
    <div class="bottom-grid">

      <!-- Quick Actions -->
      <div class="section-card">
        <div class="section-header">
          <h2 class="section-title">
            <Zap size="16" class="text-[--w40]" />
            Quick Actions
          </h2>
        </div>
        <div class="actions-grid">
          <a href="/admin/music" class="action-btn action-btn--music">
            <Music size="18" />
            <span>Add Music Release</span>
          </a>
          <a href="/admin/blog" class="action-btn action-btn--blog">
            <FileText size="18" />
            <span>Write Blog Post</span>
          </a>
          <a href="/admin/arts" class="action-btn action-btn--arts">
            <Palette size="18" />
            <span>Upload Artwork</span>
          </a>
          <a href="/admin/banner" class="action-btn action-btn--banner">
            <Image size="18" />
            <span>Manage Banner</span>
          </a>
          <a href="/admin/media" class="action-btn action-btn--media">
            <Image size="18" />
            <span>Media Library</span>
          </a>
        </div>
      </div>

      <!-- Top Content -->
      {#if topContent}
        <div class="section-card top-content-card">
          <div class="section-header">
            <h2 class="section-title">
              <LayoutDashboard size="16" class="text-[--w40]" />
              Top Content
            </h2>
          </div>
          {#each [
            { items: topContent.music, title: 'Music', accent: 'text-[#00FF88]', bg: 'bg-[#00FF88]/10', type: 'music' },
            { items: topContent.blog, title: 'Blog', accent: 'text-[#00D4FF]', bg: 'bg-[#00D4FF]/10', type: 'blog' },
            { items: topContent.arts, title: 'Arts', accent: 'text-purple-400', bg: 'bg-purple-500/10', type: 'arts' },
          ] as group}
            <div class="top-group">
              <div class="top-group-header {group.bg} {group.accent}">
                <span>{group.title}</span>
              </div>
              {#each group.items as item, i}
                <div class="top-item">
                  <span class="top-rank">#{i + 1}</span>
                  <span class="top-item-title truncate">{item.title}</span>
                  <span class="top-item-views">{item.views.toLocaleString()}</span>
                </div>
              {/each}
            </div>
          {/each}
        </div>
      {/if}
    </div>

  {/if}
</div>

<style>
  /* ===== Main Layout ===== */
  .dashboard-v2 {
    display: flex;
    flex-direction: column;
    gap: 28px;
  }

  /* ===== Hero Header ===== */
  .dashboard-hero {
    position: relative;
    padding: 36px 32px 28px;
    border-radius: 16px;
    border: 1px solid var(--w8);
    background: var(--w5);
    overflow: hidden;
  }
  .dashboard-hero-content {
    position: relative;
    z-index: 2;
  }
  .dashboard-hero h1 {
    margin-bottom: 6px;
  }
  .hero-subtitle {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 14px;
    color: var(--w40);
    margin-top: 4px;
  }
  .hero-glow {
    position: absolute;
    bottom: -60px;
    width: 260px;
    height: 260px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0, 255, 136, 0.06) 0%, transparent 70%);
    pointer-events: none;
  }
  .hero-glow--right {
    left: auto;
    right: -80px;
    background: radial-gradient(circle, rgba(0, 212, 255, 0.06) 0%, transparent 70%);
  }

  /* ===== Stats Grid ===== */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr) 1fr;
    gap: 8px;
    grid-auto-rows: auto;
  }
  .stat-card {
    position: relative;
    background: var(--w5);
    border: 1px solid var(--w8);
    border-radius: 12px;
    overflow: hidden;
    display: flex;
    align-items: flex-start;
    transition: background 0.2s, transform 0.15s, border-color 0.2s;
    cursor: pointer;
    text-decoration: none;
    color: var(--w);
    padding: 16px;
  }
  .stat-card:hover {
    transform: translateY(-2px);
    border-color: var(--w12);
    background: var(--w8);
  }
  .stat-card-bg {
    position: absolute;
    inset: 0;
    opacity: 0;
    transition: opacity 0.3s;
  }
  .stat-card:hover .stat-card-bg {
    opacity: 1;
  }
  .stat-card-content {
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;
    min-width: 0;
  }
  .stat-icon {
    flex-shrink: 0;
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: var(--w8);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .stat-info {
    min-width: 0;
  }
  .stat-label {
    font-size: 12px;
    color: var(--w40);
    margin-bottom: 2px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }
  .stat-value {
    font-family: 'DrukWideCyr', sans-serif;
    font-size: 22px;
    line-height: 1;
    margin-bottom: 1px;
  }
  .stat-subtitle {
    font-size: 12px;
    color: var(--w30);
  }
  .stat-arrow {
    flex-shrink: 0;
    margin-left: 8px;
    margin-top: 2px;
    opacity: 0;
    transform: translate(4px, -4px);
    color: var(--w30);
    transition: opacity 0.2s, transform 0.2s;
  }
  .stat-card:hover .stat-arrow {
    opacity: 1;
    transform: translate(0, 0);
  }
  .stat-card-link {
    position: absolute;
    inset: 0;
    z-index: 3;
    text-decoration: none;
  }

  /* Total card */
  .total-card {
    grid-column: 2 / 5;
  }

  /* ===== Section + Section Cards ===== */
  .section {
    display: flex;
    flex-direction: column;
  }
  .section-card {
    background: var(--w5);
    border: 1px solid var(--w8);
    border-radius: 14px;
    padding: 24px;
  }
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    gap: 12px;
  }
  .section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 15px;
    font-weight: 500;
    letter-spacing: 0.02em;
  }

  /* ===== Chart ===== */
  .chart-card {
    padding: 24px 24px 20px;
  }
  .chart-filters {
    display: flex;
    gap: 4px;
    background: var(--w5);
    border: 1px solid var(--w8);
    border-radius: 10px;
    padding: 3px;
  }
  .chart-filter-btn {
    padding: 6px 14px;
    font-size: 13px;
    border: none;
    background: transparent;
    color: var(--w40);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.15s;
    font-family: inherit;
  }
  .chart-filter-btn:hover {
    color: var(--w);
    background: var(--w8);
  }
  .chart-filter-btn.active {
    background: var(--w);
    color: var(--bg);
    font-weight: 600;
  }
  .chart-legend {
    display: flex;
    gap: 20px;
    margin-bottom: 14px;
  }
  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--w40);
  }
  .legend-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--c);
    box-shadow: 0 0 6px var(--c);
  }
  .chart-wrapper {
    overflow-x: auto;
  }
  .chart-svg {
    width: 100%;
    min-width: 500px;
  }
  .chart-loading {
    height: 200px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    color: var(--w30);
    font-size: 14px;
  }
  .spinner {
    width: 24px;
    height: 24px;
    border: 2px solid var(--w8);
    border-top-color: var(--w50);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  .chart-empty {
    height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--w30);
    font-size: 14px;
  }

  /* ===== Bottom Grid ===== */
  .bottom-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }

  /* ===== Quick Actions ===== */
  .actions-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  .action-btn {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 16px;
    border-radius: 10px;
    background: var(--w5);
    border: 1px solid var(--w8);
    color: var(--w60);
    text-decoration: none;
    font-size: 14px;
    font-family: inherit;
    transition: all 0.15s;
  }
  .action-btn:hover {
    background: var(--w8);
    border-color: var(--w12);
    color: var(--w);
    transform: translateY(-1px);
  }

  /* ===== Top Content ===== */
  .top-content-card {
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0;
  }
  .top-content-card > .section-header {
    padding: 24px 24px 16px;
  }
  .top-group {
    border-top: 1px solid var(--w5);
    padding: 4px 24px 8px;
  }
  .top-group-header {
    display: inline-block;
    font-size: 12px;
    padding: 3px 10px;
    border-radius: 6px;
    margin-bottom: 6px;
    font-weight: 500;
  }
  .top-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 4px;
    transition: background 0.15s;
    border-radius: 8px;
  }
  .top-item:hover {
    background: var(--w5);
  }
  .top-rank {
    font-family: 'DrukWideCyr', sans-serif;
    font-size: 12px;
    color: var(--w30);
    width: 28px;
    flex-shrink: 0;
  }
  .top-item-title {
    flex: 1;
    font-size: 14px;
  }
  .top-item-views {
    font-size: 13px;
    color: var(--w40);
    flex-shrink: 0;
    font-family: 'DrukWideCyr', sans-serif;
  }

  /* ===== Responsive ===== */
  @media (max-width: 860px) {
    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
    }
    .total-card {
      grid-column: 1 / -1;
    }
    .bottom-grid {
      grid-template-columns: 1fr;
    }
  }
  @media (max-width: 600px) {
    .stats-grid {
      grid-template-columns: 1fr;
    }
    .dashboard-hero {
      padding: 28px 20px 20px;
    }
    .section-card, .stat-card {
      padding: 16px;
    }
    .chart-card {
      padding: 16px 16px 12px;
    }
    .section-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 8px;
    }
    .actions-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
