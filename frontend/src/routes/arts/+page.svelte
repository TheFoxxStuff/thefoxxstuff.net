<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { Breadcrumb, ArtCard, Pagination } from '$lib/components';

  let grouped = $state({});
  let years = $state([]);
  let categories = $state([]);
  let selectedYear = $state(null);
  let selectedCategory = $state(null);
  let loading = $state(true);
  let currentPage = $state(1);
  let totalPages = $state(1);

  const loadArts = async () => {
    loading = true;
    try {
      if (selectedYear) {
        const data = await api.arts.list(currentPage, 24, selectedYear, selectedCategory);
        grouped = { [selectedYear]: data.items };
        totalPages = data.pages;
      } else if (selectedCategory) {
        const data = await api.arts.list(currentPage, 24, null, selectedCategory);
        grouped = { 'Filtered': data.items };
        totalPages = data.pages;
      } else {
        grouped = await api.arts.grouped(100);
      }
      years = await api.arts.years();
      // Extract categories from grouped items (client-side if backend doesn't support it)
      const allItems = Object.values(grouped).flat();
      const cats = [...new Set(allItems.map(a => a.category).filter(Boolean))];
      if (cats.length) categories = cats;
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  };

  onMount(loadArts);

  const selectYear = (y) => {
    selectedYear = selectedYear === y ? null : y;
    currentPage = 1;
    loadArts();
  };

  const selectCategory = (c) => {
    selectedCategory = selectedCategory === c ? null : c;
    currentPage = 1;
    loadArts();
  };

  const clearFilters = () => {
    selectedYear = null;
    selectedCategory = null;
    currentPage = 1;
    loadArts();
  };

  const hasFilters = $derived(selectedYear !== null || selectedCategory !== null);
</script>

<svelte:head><title>Arts | TheFoxxStuff</title></svelte:head>

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0">
  <div class="flex items-center justify-between mb-2">
    <h1 class="font-display text-[24px] tracking-wide text-[--w]">Arts</h1>
    {#if hasFilters}
      <button onclick={clearFilters} class="text-[13px] text-[--w60] hover:text-[--w] transition-colors">
        Clear filters ×
      </button>
    {/if}
  </div>
  <Breadcrumb items={[{ href: '/arts', label: 'Arts' }]} />

  <!-- Filters -->
  <div class="mt-6 space-y-3">
    <!-- Year filter -->
    {#if years.length > 1}
      <div class="flex gap-2 flex-wrap items-center">
        <span class="text-[12px] text-[--w60] uppercase tracking-wide">Year:</span>
        {#each years as year}
          <button
            onclick={() => selectYear(year)}
            class="tag {selectedYear === year ? 'tag-active' : ''}"
          >
            {year}
          </button>
        {/each}
      </div>
    {/if}

    <!-- Category filter -->
    {#if categories.length > 1}
      <div class="flex gap-2 flex-wrap items-center">
        <span class="text-[12px] text-[--w60] uppercase tracking-wide">Category:</span>
        {#each categories as cat}
          <button
            onclick={() => selectCategory(cat)}
            class="tag {selectedCategory === cat ? 'tag-active' : ''}"
          >
            {cat}
          </button>
        {/each}
      </div>
    {/if}
  </div>

  <div class="mt-8 space-y-12">
    {#if loading}
      {#each [2025, 2024] as year}
        <section>
          <h2 class="font-display text-2xl mb-6">{year}</h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {#each Array(8) as _}
              <div class="aspect-square bg-dark-800 rounded-xl animate-pulse"></div>
            {/each}
          </div>
        </section>
      {/each}
    {:else}
      {#each Object.entries(grouped).sort((a, b) => Number(b[0]) - Number(a[0])) as [year, artworks]}
        <section>
          <h2 class="font-display text-2xl mb-6 text-[--w]">{year}</h2>
          <!-- Masonry-style grid using columns -->
          <div class="columns-2 sm:columns-3 md:columns-4 gap-4 space-y-4">
            {#each artworks as artwork, i}
              <div class="break-inside-avoid fade-in" style="animation-delay: {Math.min(i * 40, 400)}ms">
                <ArtCard {artwork} showLightbox={true} />
              </div>
            {/each}
          </div>
        </section>
      {/each}

      {#if (selectedYear || selectedCategory) && totalPages > 1}
        <Pagination {currentPage} {totalPages} onPageChange={(p) => { currentPage = p; loadArts(); }} />
      {/if}

      {#if Object.values(grouped).flat().length === 0}
        <div class="text-center py-16 text-[--w60]">
          <p class="text-[18px]">No artworks found</p>
          <button onclick={clearFilters} class="mt-4 text-[--green] hover:underline">Clear filters</button>
        </div>
      {/if}
    {/if}
  </div>
</div>
