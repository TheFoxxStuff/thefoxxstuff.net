<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { Breadcrumb, FeaturedRelease, MusicCard, Pagination } from '$lib/components';

  let featured = $state(null);
  let releases = $state({ items: [], page: 1, pages: 1 });
  let loading = $state(true);
  let page = $state(1);
  const LIMIT = 12;

  const loadPage = async (p) => {
    page = p;
    try {
      releases = await api.music.list(p, LIMIT);
    } catch {}
  };

  onMount(async () => {
    try {
      // Грузим параллельно featured и список
      const [f, m] = await Promise.all([
        api.music.featured(),
        api.music.list(1, LIMIT),
      ]);
      featured = f;
      releases = m;
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  });
</script>

<svelte:head><title>Music | TheFoxxStuff</title></svelte:head>

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0">
  <h1 class="font-display text-[24px] tracking-wide text-[--w] mb-2">Music</h1>
  <Breadcrumb items={[{ href: '/music', label: 'Music' }]} />

  <div class="mt-8 space-y-10">
    {#if !loading && featured}
      <FeaturedRelease release={featured} />
    {/if}

    <section>
      <h2 class="font-display text-2xl tracking-wide mb-6">All Releases</h2>
      {#if loading}
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          {#each Array(8) as _}
            <div class="aspect-square bg-dark-800 rounded-xl animate-pulse"></div>
          {/each}
        </div>
      {:else}
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          {#each releases.items as release, i}
            <MusicCard {release} eager={i < 4} />
          {/each}
        </div>
        {#if releases.pages > 1}
          <div class="mt-6">
            <Pagination currentPage={page} totalPages={releases.pages} onPageChange={loadPage} />
          </div>
        {/if}
      {/if}
    </section>
  </div>
</div>
