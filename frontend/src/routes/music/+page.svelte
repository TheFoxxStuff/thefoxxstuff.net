<script>
  import { api } from '$lib/api';
  import { Breadcrumb, FeaturedRelease, MusicCard, Pagination, SEO } from '$lib/components';
  import { canonicalUrl } from '$lib/seo.js';

  let { data: pageData } = $props();

  let featured = $derived(pageData.featured);
  let releases = $derived(pageData.releases);
  let loading = $state(false);
  let page = $state(1);
  const LIMIT = 12;

  const loadPage = async (p) => {
    loading = true;
    page = p;
    try {
      releases = await api.music.list(p, LIMIT);
    } catch {} finally {
      loading = false;
    }
  };
</script>

<SEO
  title="Music"
  description="Discography of TheFoxxStuff — Hardcore, Breakcore and Drum'n'Bass releases. Stream and download."
  keywords="music, discography, hardcore, breakcore, drum and bass, releases, thefoxxstuff"
  url={canonicalUrl('/music')}
  type="website"
  jsonLd={{
    '@context': 'https://schema.org',
    '@type': 'MusicGroup',
    name: 'TheFoxxStuff',
    url: canonicalUrl('/music'),
    genre: ['Hardcore', 'Breakcore', "Drum'n'Bass"],
  }}
/>

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0">
  <h1 class="font-display text-[24px] tracking-wide text-[--w] mb-2">Music</h1>
  <Breadcrumb items={[{ href: '/music', label: 'Music' }]} />

  <div class="mt-8 space-y-10">
    {#if featured}
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
