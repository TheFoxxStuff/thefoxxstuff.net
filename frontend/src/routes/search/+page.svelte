<script>
  import { api } from '$lib/api';
  import { goto } from '$app/navigation';
  import { Search } from 'lucide-svelte';
  import { SEO } from '$lib/components';
  import { canonicalUrl } from '$lib/seo.js';

  let { data: pageData } = $props();

  let query = $derived(pageData.query);
  let results = $derived(pageData.results);
  let loading = $state(false);

  async function doSearch(q) {
    if (!q || !q.trim()) { results = null; return; }
    loading = true;
    try { results = await api.stats.search(q); }
    catch (e) { console.error(e); }
    finally { loading = false; }
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (query.trim()) {
      goto(`/search?q=${encodeURIComponent(query.trim())}`, { replaceState: true });
      doSearch(query.trim());
    }
  }

  let total = $derived(results ? (results.music?.length || 0) + (results.blog?.length || 0) + (results.arts?.length || 0) : 0);
</script>

<SEO
  title={query ? `Search: ${query}` : 'Search'}
  description={query ? `Search results for "${query}" on TheFoxxStuff` : 'Search music, blog posts and artworks on TheFoxxStuff'}
  url={canonicalUrl(query ? `/search?q=${encodeURIComponent(query)}` : '/search')}
  noindex={true}
/>

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0">
  <h1 class="font-display text-[24px] tracking-wide mb-6">Search</h1>

  <form onsubmit={handleSubmit} class="flex gap-2 mb-8">
    <div class="flex-1 relative">
      <Search size={18} class="absolute left-3 top-1/2 -translate-y-1/2 text-dark-500" />
      <input type="text" bind:value={query} placeholder="Search music, blog, arts..." class="input pl-10 w-full" autofocus />
    </div>
    <button type="submit" class="btn btn-primary">Search</button>
  </form>

  {#if loading}
    <div class="space-y-4">
      {#each Array(4) as _}<div class="card p-4 animate-pulse"><div class="h-5 bg-dark-800 rounded w-1/3"></div></div>{/each}
    </div>
  {:else if results}
    <p class="text-dark-400 text-sm mb-6">{total} result{total !== 1 ? 's' : ''} for "{query}"</p>

    {#if results.music?.length > 0}
      <section class="mb-8">
        <h2 class="font-display text-xl mb-3 text-accent-green">Music</h2>
        <div class="space-y-2">
          {#each results.music as item}
            <a href="/music/{item.slug || item._id}" class="card p-4 flex items-center justify-between hover:bg-dark-800/50 transition">
              <div><div class="text-[--w] font-medium">{item.title}</div><div class="text-xs text-dark-400">{item.genre}</div></div>
              <span class="text-dark-500 text-sm">{item.views} views</span>
            </a>
          {/each}
        </div>
      </section>
    {/if}

    {#if results.blog?.length > 0}
      <section class="mb-8">
        <h2 class="font-display text-xl mb-3 text-accent-cyan">Blog</h2>
        <div class="space-y-2">
          {#each results.blog as item}
            <a href="/blog/{item.slug || item._id}" class="card p-4 flex items-center justify-between hover:bg-dark-800/50 transition">
              <div><div class="text-[--w] font-medium">{item.title}</div>{#if item.excerpt}<div class="text-xs text-dark-400 line-clamp-1">{item.excerpt}</div>{/if}</div>
              <span class="text-dark-500 text-sm">{item.views} views</span>
            </a>
          {/each}
        </div>
      </section>
    {/if}

    {#if results.arts?.length > 0}
      <section class="mb-8">
        <h2 class="font-display text-xl mb-3 text-purple-400">Arts</h2>
        <div class="space-y-2">
          {#each results.arts as item}
            <a href="/arts/{item.slug || item._id}" class="card p-4 flex items-center justify-between hover:bg-dark-800/50 transition">
              <div><div class="text-[--w] font-medium">{item.title}</div><div class="text-xs text-dark-400">{item.year}</div></div>
              <span class="text-dark-500 text-sm">{item.views} views</span>
            </a>
          {/each}
        </div>
      </section>
    {/if}

    {#if total === 0}
      <div class="text-center text-dark-500 py-12">No results found for "{query}"</div>
    {/if}
  {/if}
</div>
