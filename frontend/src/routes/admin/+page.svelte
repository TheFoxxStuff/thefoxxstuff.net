<script>
  import { SEO } from "$lib/components";
  import { canonicalUrl } from "$lib/seo.js";
  import { api } from '$lib/api';
  
  let { data: pageData } = $props();
  let stats = $state(pageData.stats);
  let chartData = $state(pageData.chartData);
  let topContent = $state(pageData.topContent);
  let loading = $state(false);
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
</script>

<SEO titleFull="Admin Dashboard - TheFoxxStuff" noindex={true} url={canonicalUrl("/admin")} />

<div>
  <h1 class="font-display text-[24px] tracking-wide mb-8">Dashboard</h1>
  
  {#if stats}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-[4px] mb-8">
      <div class="card p-6">
        <div class="text-[--w60] text-sm mb-1">Music Releases</div>
        <div class="text-[24px] font-bold">{stats.music.count}</div>
        <div class="text-[--w30] text-sm mt-1">{stats.music.views.toLocaleString()} views</div>
      </div>
      <div class="card p-6">
        <div class="text-[--w60] text-sm mb-1">Blog Posts</div>
        <div class="text-[24px] font-bold">{stats.blog.count}</div>
        <div class="text-[--w30] text-sm mt-1">{stats.blog.views.toLocaleString()} views</div>
      </div>
      <div class="card p-6">
        <div class="text-[--w60] text-sm mb-1">Artworks</div>
        <div class="text-[24px] font-bold">{stats.arts.count}</div>
        <div class="text-[--w30] text-sm mt-1">{stats.arts.views.toLocaleString()} views</div>
      </div>
      <div class="card p-6">
        <div class="text-[--w60] text-sm mb-1">Links</div>
        <div class="text-[24px] font-bold">{stats.links.count}</div>
      </div>
      <div class="card p-6">
        <div class="text-[--w60] text-sm mb-1">Users</div>
        <div class="text-[24px] font-bold">{stats.users.count}</div>
      </div>
      <div class="card p-6">
        <div class="text-[--w60] text-sm mb-1">Images</div>
        <div class="text-[24px] font-bold">{stats.images?.count || 0}</div>
      </div>
      <div class="card p-6 col-span-2 bg-gradient-to-r from-accent-green/10 to-accent-cyan/10">
        <div class="text-[--w60] text-sm mb-1">Total Views</div>
        <div class="text-[24px] font-bold text-gradient">{stats.total_views.toLocaleString()}</div>
      </div>
    </div>
    
    <div class="card p-6 mb-8">
      <div class="flex justify-between items-center mb-6">
        <h2 class="font-display text-xl">Views Over Time</h2>
        <div class="flex gap-2">
          {#each [7, 14, 30, 90] as days}
            <button 
              onclick={() => loadChart(days)}
              class="px-3 py-1 text-sm rounded-lg transition-colors {chartDays === days ? 'bg-accent-green text-dark-950' : 'bg-[--w8] hover:bg-[--w12]'}"
            >
              {days}d
            </button>
          {/each}
        </div>
      </div>
      
      {#if chartLoading}
        <div class="h-64 flex items-center justify-center">
          <div class="w-8 h-8 border-2 border-accent-green border-t-transparent rounded-full animate-spin"></div>
        </div>
      {:else if chartData?.data}
        {@const data = chartData.data}
        {@const maxValue = Math.max(...data.map(d => d.total), 1)}
        {@const width = 800}
        {@const height = 200}
        
        <div class="flex gap-6 mb-4 text-sm">
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-accent-green"></div>
            <span class="text-[--w60]">Music ({chartData.summary.music.toLocaleString()})</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-accent-cyan"></div>
            <span class="text-[--w60]">Blog ({chartData.summary.blog.toLocaleString()})</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-purple-500"></div>
            <span class="text-[--w60]">Arts ({chartData.summary.arts.toLocaleString()})</span>
          </div>
        </div>
        
        <div class="overflow-x-auto">
          <svg viewBox="0 0 {width} {height + 30}" class="w-full min-w-[600px]">
            <defs>
              <linearGradient id="greenGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#00FF88" stop-opacity="0.4"/>
                <stop offset="100%" stop-color="#00FF88" stop-opacity="0"/>
              </linearGradient>
              <linearGradient id="cyanGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#00D4FF" stop-opacity="0.4"/>
                <stop offset="100%" stop-color="#00D4FF" stop-opacity="0"/>
              </linearGradient>
              <linearGradient id="purpleGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#A855F7" stop-opacity="0.4"/>
                <stop offset="100%" stop-color="#A855F7" stop-opacity="0"/>
              </linearGradient>
            </defs>
            
            {#each [0, 0.25, 0.5, 0.75, 1] as ratio}
              <line x1="0" y1={height - ratio * height} x2={width} y2={height - ratio * height} stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
              <text x="0" y={height - ratio * height - 5} fill="rgba(255,255,255,0.3)" font-size="10">{Math.round(maxValue * ratio)}</text>
            {/each}
            
            <path d={getAreaPath(data, 'music', maxValue, width, height)} fill="url(#greenGrad)"/>
            <path d={getAreaPath(data, 'blog', maxValue, width, height)} fill="url(#cyanGrad)"/>
            <path d={getAreaPath(data, 'arts', maxValue, width, height)} fill="url(#purpleGrad)"/>
            
            <path d={getChartPath(data, 'music', maxValue, width, height)} fill="none" stroke="#00FF88" stroke-width="2"/>
            <path d={getChartPath(data, 'blog', maxValue, width, height)} fill="none" stroke="#00D4FF" stroke-width="2"/>
            <path d={getChartPath(data, 'arts', maxValue, width, height)} fill="none" stroke="#A855F7" stroke-width="2"/>
            
            {#each data as d, i}
              {#if i % Math.ceil(data.length / 10) === 0 || i === data.length - 1}
                <text x={(i / Math.max(data.length - 1, 1)) * width} y={height + 20} fill="rgba(255,255,255,0.3)" font-size="10" text-anchor="middle">
                  {d.date.split('-').slice(1).join('/')}
                </text>
              {/if}
            {/each}
          </svg>
        </div>
      {:else}
        <div class="h-64 flex items-center justify-center text-[--w30]">No data available</div>
      {/if}
    </div>
    
    {#if topContent}
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div class="card p-6">
          <h3 class="font-display text-lg mb-4 text-accent-green">Top Music</h3>
          <div class="space-y-3">
            {#each topContent.music as item, i}
              <div class="flex justify-between items-center">
                <div class="flex items-center gap-3">
                  <span class="text-[--w30] w-5">{i + 1}.</span>
                  <span class="truncate max-w-[180px]">{item.title}</span>
                </div>
                <span class="text-[--w60] text-sm">{item.views.toLocaleString()}</span>
              </div>
            {/each}
          </div>
        </div>
        
        <div class="card p-6">
          <h3 class="font-display text-lg mb-4 text-accent-cyan">Top Blog Posts</h3>
          <div class="space-y-3">
            {#each topContent.blog as item, i}
              <div class="flex justify-between items-center">
                <div class="flex items-center gap-3">
                  <span class="text-[--w30] w-5">{i + 1}.</span>
                  <span class="truncate max-w-[180px]">{item.title}</span>
                </div>
                <span class="text-[--w60] text-sm">{item.views.toLocaleString()}</span>
              </div>
            {/each}
          </div>
        </div>
        
        <div class="card p-6">
          <h3 class="font-display text-lg mb-4 text-purple-500">Top Artworks</h3>
          <div class="space-y-3">
            {#each topContent.arts as item, i}
              <div class="flex justify-between items-center">
                <div class="flex items-center gap-3">
                  <span class="text-[--w30] w-5">{i + 1}.</span>
                  <span class="truncate max-w-[180px]">{item.title}</span>
                </div>
                <span class="text-[--w60] text-sm">{item.views.toLocaleString()}</span>
              </div>
            {/each}
          </div>
        </div>
      </div>
    {/if}
    
    <div class="card p-6">
      <h2 class="font-display text-xl mb-4">Quick Actions</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-2">
        <a href="/admin/music" class="btn btn-secondary justify-start">Add Music Release</a>
        <a href="/admin/blog" class="btn btn-secondary justify-start">Write Blog Post</a>
        <a href="/admin/arts" class="btn btn-secondary justify-start">Upload Artwork</a>
      </div>
    </div>
  {/if}
</div>
