<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { Breadcrumb, ArtCard, Pagination } from '$lib/components';
  let grouped = $state({});
  let years = $state([]);
  let selectedYear = $state(null);
  let loading = $state(true);
  let currentPage = $state(1);
  let totalPages = $state(1);
  const loadArts = async () => {
    loading = true;
    try {
      if (selectedYear) { const data = await api.arts.list(currentPage, 24, selectedYear); grouped = { [selectedYear]: data.items }; totalPages = data.pages; }
      else { grouped = await api.arts.grouped(100); }
      years = await api.arts.years();
    } catch (e) { console.error(e); } finally { loading = false; }
  };
  onMount(loadArts);
  const selectYear = (y) => { selectedYear = selectedYear === y ? null : y; currentPage = 1; loadArts(); };
</script>
<svelte:head><title>Arts | TheFoxxStuff</title></svelte:head>
<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0">
  <h1 class="font-display text-3xl tracking-wide text-[--w] mb-2">Arts</h1>
  <Breadcrumb items={[{ href: '/arts', label: 'Arts' }]} />
  <div class="mt-8 flex justify-between gap-4 flex-wrap">
    <button class="btn btn-secondary">Sort by newest</button>
    <div class="flex gap-2 flex-wrap">{#each years as year}<button onclick={() => selectYear(year)} class="tag {selectedYear === year ? 'tag-active' : ''}">{year}</button>{/each}</div>
  </div>
  <div class="mt-8 space-y-12">
    {#if loading}{#each [2025, 2024] as year}<section><h2 class="font-display text-2xl mb-6">{year}</h2><div class="grid grid-cols-4 gap-4">{#each Array(7) as _}<div class="aspect-square bg-dark-800 rounded-xl animate-pulse"></div>{/each}</div></section>{/each}
    {:else}{#each Object.entries(grouped).sort((a, b) => Number(b[0]) - Number(a[0])) as [year, artworks]}<section><h2 class="font-display text-2xl mb-6">{year}</h2><div class="grid grid-cols-4 gap-4">{#each artworks as artwork}<ArtCard {artwork} />{/each}</div></section>{/each}
      {#if selectedYear && totalPages > 1}<Pagination {currentPage} {totalPages} onPageChange={(p) => { currentPage = p; loadArts(); }} />{/if}
    {/if}
  </div>
</div>

