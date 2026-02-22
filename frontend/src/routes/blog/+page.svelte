<script>
  import { api } from '$lib/api';
  import { Breadcrumb, BlogCard, Pagination, SEO } from '$lib/components';
  import { canonicalUrl } from '$lib/seo.js';

  let { data: pageData } = $props();

  let posts = $state(pageData.posts);
  let search = $state('');
  let sort = $state('newest');
  let loading = $state(false);
  let showSortMenu = $state(false);

  const sortOptions = [
    { value: 'newest', label: 'Newest first' },
    { value: 'oldest', label: 'Oldest first' },
    { value: 'views', label: 'Most viewed' }
  ];

  const loadPosts = async (p = 1) => {
    loading = true;
    try {
      posts = await api.blog.list(p, 6, search, sort);
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  };

  const handleSearch = () => loadPosts(1);
  const handleSort = (value) => {
    sort = value;
    showSortMenu = false;
    loadPosts(1);
  };

  const currentSortLabel = $derived(sortOptions.find(o => o.value === sort)?.label || 'Sort by newest');
</script>

<SEO
  title="Blog"
  description="Articles, thoughts and updates from TheFoxxStuff — music producer from Yakutia."
  keywords="blog, articles, music, hardcore, breakcore, thefoxxstuff"
  url={canonicalUrl('/blog')}
  type="website"
  jsonLd={{
    '@context': 'https://schema.org',
    '@type': 'Blog',
    name: 'TheFoxxStuff Blog',
    url: canonicalUrl('/blog'),
    author: { '@type': 'Person', name: 'TheFoxxStuff' },
  }}
/>

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0">
  <h1 class="font-display text-[24px] tracking-wide mb-2">Blog</h1>
  <Breadcrumb items={[{ href: '/blog', label: 'Blog' }]} />

  <div class="mt-8 flex justify-between gap-4 flex-wrap">
    <!-- Sort Dropdown -->
    <div class="relative">
      <button
        onclick={() => showSortMenu = !showSortMenu}
        class="filter flex items-center gap-2"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
        </svg>
        {currentSortLabel}
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {#if showSortMenu}
        <div class="absolute top-full left-0 mt-[6px] border border-[--w8] bg-[--select] rounded-[8px] p-[6px] min-w-[160px] z-10 shadow-xl backdrop-blur-[6px]">
          {#each sortOptions as option}
            <button
              onclick={() => handleSort(option.value)}
              class="w-full text-left px-[12px] py-[4px] hover:bg-[--w8] rounded-[8px] hover:text-[--w] transition-colors {sort === option.value ? 'text-[--w]' : 'text-[--w60]'}"
            >
              {option.label}
            </button>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Search -->
    <div class="relative">
      <input
        type="text"
        bind:value={search}
        onkeydown={(e) => e.key === 'Enter' && handleSearch()}
        placeholder="Search"
        class="filter search pr-10"
      />
      <button onclick={handleSearch} aria-label="Search" class="absolute right-2 top-1/2 -translate-y-1/2 p-1 hover:text-white text-dark-400">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </button>
    </div>
  </div>

  <div class="mt-8">
    {#if loading}
      <div class="grid md:grid-cols-2 gap-4">
        {#each Array(4) as _}
          <div class="card p-4"><div class="aspect-video bg-dark-800 rounded-lg animate-pulse"></div></div>
        {/each}
      </div>
    {:else if posts.items.length === 0}
      <div class="card p-12 text-center">
        <svg class="w-16 h-16 mx-auto text-dark-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1" />
        </svg>
        <p class="text-dark-400">No posts found</p>
      </div>
    {:else}
      <div class="grid md:grid-cols-2 gap-4">
        {#each posts.items as post}
          <BlogCard {post} />
        {/each}
      </div>
      {#if posts.pages > 1}
        <div class="mt-8">
          <Pagination currentPage={posts.page} totalPages={posts.pages} onPageChange={loadPosts} />
        </div>
      {/if}
    {/if}
  </div>
</div>

{#if showSortMenu}
  <button class="fixed inset-0 z-0" onclick={() => showSortMenu = false} aria-label="Close menu"></button>
{/if}
