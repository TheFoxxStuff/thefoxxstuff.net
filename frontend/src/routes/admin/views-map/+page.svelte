<script>
  import { SEO } from "$lib/components";
  import { canonicalUrl } from "$lib/seo.js";
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let { data: pageData } = $props();
  let mapData = $state(pageData.mapData);
  let loading = $state(false);
  let days = $state(30);
  let mapContainer = $state(null);
  let tooltip = $state({ visible: false, x: 0, y: 0, text: '' });
  let selectedCountry = $state(null);
  let worldPaths = $state('');

  const MAP_W = 800, MAP_H = 400;

  async function loadData() {
    loading = true;
    try { mapData = await api.views.map(days); } catch (e) { console.error(e); }
    finally { loading = false; }
  }

  async function loadWorldMap() {
    try {
      const resp = await fetch('https://cdn.jsdelivr.net/npm/world-atlas@2/land-110m.json');
      const topo = await resp.json();
      const land = topo.objects.land, arcs = topo.arcs, tf = topo.transform;
      const decoded = arcs.map(arc => { let x=0,y=0; return arc.map(([dx,dy]) => { x+=dx; y+=dy; return [x*tf.scale[0]+tf.translate[0], y*tf.scale[1]+tf.translate[1]]; }); });
      function arcPts(i) { return i >= 0 ? decoded[i] : [...decoded[~i]].reverse(); }
      function ringPath(ring) {
        const pts = ring.flatMap(i => arcPts(i));
        if (!pts.length) return '';
        return 'M'+pts.map(([lon,lat]) => { const p=project(lat,lon); return `${p.x.toFixed(1)},${p.y.toFixed(1)}`; }).join('L')+'Z';
      }
      function geoPath(g) {
        if (g.type==='Polygon') return g.arcs.map(r=>ringPath(r)).join('');
        if (g.type==='MultiPolygon') return g.arcs.map(p=>p.map(r=>ringPath(r)).join('')).join('');
        if (g.type==='GeometryCollection') return g.geometries.map(gg=>geoPath(gg)).join('');
        return '';
      }
      worldPaths = geoPath(land);
    } catch (e) { console.error('World map load failed:', e); }
  }

  onMount(() => { loadWorldMap(); if (!mapData) loadData(); });
  async function changeDays(d) { days = d; await loadData(); }
  function project(lat, lon) { return { x: ((lon+180)/360)*MAP_W, y: ((90-lat)/180)*MAP_H }; }
  function radius(c) { if (!mapData?.locations?.length) return 4; const mx = Math.max(...mapData.locations.map(l=>l.count),1); return 3+Math.sqrt(c/mx)*14; }
  function showTip(e, loc) { const r = mapContainer?.getBoundingClientRect(); if (!r) return; tooltip = { visible:true, x:e.clientX-r.left+12, y:e.clientY-r.top-8, text:`${loc.city}, ${loc.country} — ${loc.count} view${loc.count!==1?'s':''}` }; }
  function hideTip() { tooltip = { ...tooltip, visible: false }; }
  let topCountries = $derived((mapData?.countries||[]).slice(0,20));
  let filteredLocs = $derived(selectedCountry ? (mapData?.locations||[]).filter(l=>l.country===selectedCountry) : (mapData?.locations||[]));
  function flag(code) { if (!code||code==='XX') return '🌍'; try { return String.fromCodePoint(...[...code.toUpperCase()].map(c=>0x1F1E6+c.charCodeAt(0)-65)); } catch { return '🌍'; } }
</script>
<SEO titleFull="Views Map - Admin" noindex={true} url={canonicalUrl("/admin")} />
<div>
  <div class="flex items-center justify-between mb-6">
    <h1 class="font-display text-[24px] tracking-wide">Views Map</h1>
    <div class="flex items-center gap-2">{#each [7,30,90,365] as d}<button onclick={() => changeDays(d)} class="px-3 py-1.5 text-sm rounded-lg transition-colors {days===d?'bg-accent-green text-dark-950 font-medium':'bg-[--w8] text-[--w60] hover:text-white'}">{d===365?'1Y':`${d}D`}</button>{/each}</div>
  </div>
  {#if loading}<div class="card p-8 animate-pulse"><div class="h-[400px] bg-[--w8] rounded-lg"></div></div>
  {:else if mapData}
    <div class="grid grid-cols-3 gap-[4px] mb-6">
      <div class="card p-4"><div class="text-[--w60] text-sm">Unique Views</div><div class="text-2xl font-bold">{mapData.total_unique_views?.toLocaleString()}</div></div>
      <div class="card p-4"><div class="text-[--w60] text-sm">Countries</div><div class="text-2xl font-bold">{mapData.countries?.length||0}</div></div>
      <div class="card p-4"><div class="text-[--w60] text-sm">Cities</div><div class="text-2xl font-bold">{mapData.locations?.length||0}</div></div>
    </div>
    <div class="card p-4 mb-6"><div bind:this={mapContainer} class="relative w-full overflow-hidden rounded-lg bg-[--bg]" style="aspect-ratio:2/1;">
      <svg viewBox="0 0 {MAP_W} {MAP_H}" class="w-full h-full" xmlns="http://www.w3.org/2000/svg">
        <rect x="0" y="0" width={MAP_W} height={MAP_H} fill="#0a0a0a" />
        {#if worldPaths}<path d={worldPaths} fill="#1a1f1a" stroke="#2a3a2a" stroke-width="0.5" />{/if}
        <line x1="0" y1={MAP_H/2} x2={MAP_W} y2={MAP_H/2} stroke="#1a1a1a" stroke-width="0.5" stroke-dasharray="4,4" />
        {#each filteredLocs as loc}{@const pos=project(loc.lat,loc.lon)}{@const r=radius(loc.count)}
          <circle cx={pos.x} cy={pos.y} r={r*2} fill="rgba(74,222,128,0.08)" />
          <circle cx={pos.x} cy={pos.y} r={r} fill="rgba(74,222,128,0.35)" stroke="rgba(74,222,128,0.7)" stroke-width="0.8" class="cursor-pointer hover:fill-[rgba(74,222,128,0.6)]" role="button" tabindex="0" aria-label="View location data" onmouseenter={(e)=>showTip(e,loc)} onmouseleave={hideTip} onkeydown={(e)=>e.key==='Enter'&&showTip(e,loc)} />
          <circle cx={pos.x} cy={pos.y} r="1.5" fill="#4ade80" />
        {/each}
      </svg>
      {#if tooltip.visible}<div class="absolute pointer-events-none bg-[--w5] border border-[--w12] rounded-lg px-3 py-1.5 text-xs text-white shadow-lg whitespace-nowrap z-10" style="left:{tooltip.x}px;top:{tooltip.y}px;">{tooltip.text}</div>{/if}
    </div></div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-[4px]">
      <div class="card"><div class="px-4 py-3 border-b border-[--w8] flex items-center justify-between"><h3 class="font-medium text-sm">Countries</h3>{#if selectedCountry}<button onclick={() => selectedCountry=null} class="text-xs text-accent-green hover:underline">Show all</button>{/if}</div>
        <div class="max-h-[400px] overflow-y-auto">{#each topCountries as c}<button onclick={() => selectedCountry=selectedCountry===c.country?null:c.country} class="w-full flex items-center justify-between px-4 py-2.5 text-sm hover:bg-[--w8] transition-colors border-b border-[--w8]/50 {selectedCountry===c.country?'bg-[--w8] text-accent-green':'text-dark-300'}"><span class="flex items-center gap-2"><span class="text-base">{flag(c.country_code)}</span><span>{c.country}</span></span><span class="font-mono text-[--w60]">{c.count}</span></button>{/each}{#if topCountries.length===0}<div class="px-4 py-8 text-center text-[--w30] text-sm">No data</div>{/if}</div></div>
      <div class="card"><div class="px-4 py-3 border-b border-[--w8]"><h3 class="font-medium text-sm">{selectedCountry?`Cities in ${selectedCountry}`:'Top Cities'}</h3></div>
        <div class="max-h-[400px] overflow-y-auto">{#each filteredLocs.slice(0,30) as loc}<div class="flex items-center justify-between px-4 py-2.5 text-sm border-b border-[--w8]/50"><span class="text-dark-300"><span class="text-[--w30]">{loc.country_code}</span> · {loc.city}</span><div class="flex items-center gap-3"><span class="font-mono text-[--w60]">{loc.count}</span><div class="w-16 h-1.5 bg-[--w8] rounded-full overflow-hidden"><div class="h-full bg-accent-green/60 rounded-full" style="width:{Math.min(100,(loc.count/(mapData.locations[0]?.count||1))*100)}%"></div></div></div></div>{/each}{#if filteredLocs.length===0}<div class="px-4 py-8 text-center text-[--w30] text-sm">No data</div>{/if}</div></div>
    </div>
  {/if}
</div>
