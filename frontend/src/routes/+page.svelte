<script>
  import { onMount } from 'svelte';
  import { api, getImageUrl } from '$lib/api';
  import { MusicCard, BlogCard, ArtCard, Pagination } from '$lib/components';
  import { ChevronRight } from 'lucide-svelte';
  import Button from '$lib/components/Button.svelte';
  import Banner from '../lib/components/Banner.svelte';
  import GuestChat from '$lib/components/GuestChat.svelte';

  let music = $state({ items: [], page: 1, pages: 1 });
  let blog = $state({ items: [], page: 1, pages: 1 });
  let arts = $state([]);
  let banner = $state({ slides: [] });
  let loading = $state(true);
  let currentSlide = $state(0);
  let slideInterval;
  
  // Section pagination
  let musicPage = $state(1);
  let blogPage = $state(1);
  
  const loadData = async () => {
    try {
      const [m, b, a, ban] = await Promise.all([
        api.music.list(musicPage, 4),
        api.blog.list(blogPage, 2),
        api.arts.list(1, 6),
        api.banner.get()
      ]);
      music = m;
      blog = b;
      arts = a.items;
      banner = ban;
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  };
  
  const loadMusic = async (page) => {
    musicPage = page;
    try {
      music = await api.music.list(page, 4);
    } catch (e) {
      console.error(e);
    }
  };
  
  const loadBlog = async (page) => {
    blogPage = page;
    try {
      blog = await api.blog.list(page, 2);
    } catch (e) {
      console.error(e);
    }
  };
  
  // Функции управления слайдером
  const nextSlide = () => {
    if (banner.slides.length > 0) {
      currentSlide = (currentSlide + 1) % banner.slides.length;
    }
  };

  const prevSlide = () => {
    if (banner.slides.length > 0) {
      currentSlide = (currentSlide - 1 + banner.slides.length) % banner.slides.length;
    }
  };

  const goToSlide = (index) => {
    currentSlide = index;
  };
  
  onMount(() => {
    loadData();
    // Автоматическая прокрутка
    slideInterval = setInterval(nextSlide, 5000);
    return () => clearInterval(slideInterval);
  });
</script>

<svelte:head><title>Homepage | TheFoxxStuff</title></svelte:head>

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0 space-y-[20px]">
  <!-- Banner Slider -->

<Banner 
  {banner} 
  {currentSlide} 
  {api} 
  {getImageUrl} 
  {nextSlide} 
  {prevSlide} 
  {goToSlide} 
/>

  <!-- Music Section -->
  <section>
    <div class="flex items-center justify-between mb-6">
      <h2 class="font-display text-2xl tracking-wide">Music</h2>
      <Button href="/music" iconRight={ChevronRight}>
        Show more
      </Button>
    </div>
    {#if loading}
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        {#each Array(4) as _}
          <div class="aspect-square bg-dark-800 rounded-xl animate-pulse"></div>
        {/each}
      </div>
    {:else}
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        {#each music.items as release}
          <MusicCard {release} />
        {/each}
      </div>
      {#if music.pages > 1}
        <div class="mt-[12px]">
          <Pagination currentPage={musicPage} totalPages={music.pages} onPageChange={loadMusic} />
        </div>
      {/if}
    {/if}
  </section>

  <!-- Blog Section -->
  <section>
    <div class="flex items-center justify-between mb-6">
      <h2 class="font-display text-2xl tracking-wide">Blog</h2>
      <Button href="/blog" iconRight={ChevronRight}>
        Show more
      </Button>
    </div>
    {#if loading}
      <div class="grid md:grid-cols-2 gap-4">
        {#each Array(2) as _}
          <div class="card p-4"><div class="aspect-video bg-dark-800 rounded-lg animate-pulse"></div></div>
        {/each}
      </div>
    {:else}
      <div class="grid md:grid-cols-2 gap-4">
        {#each blog.items as post}
          <BlogCard {post} />
        {/each}
      </div>
      {#if blog.pages > 1}
        <div class="mt-[12px]">
          <Pagination currentPage={blogPage} totalPages={blog.pages} onPageChange={loadBlog} />
        </div>
      {/if}
    {/if}
  </section>

  <!-- Arts Section -->
<section>
  <div class="flex items-center justify-between mb-6">
    <h2 class="font-display text-2xl tracking-wide">Arts</h2>
    <Button href="/arts" iconRight={ChevronRight}>
      Show more
    </Button>
  </div>

  {#if loading}
    <!-- Skeleton под ту же сетку -->
    <div class="grid grid-cols-4 grid-rows-3 gap-4">
      <div class="col-span-2 row-span-2 bg-dark-800 rounded-xl animate-pulse"></div>
      <div class="bg-dark-800 rounded-xl animate-pulse"></div>
      <div class="bg-dark-800 rounded-xl animate-pulse"></div>
      <div class="col-span-2 row-span-2 bg-dark-800 rounded-xl animate-pulse"></div>
      <div class="bg-dark-800 rounded-xl animate-pulse"></div>
      <div class="bg-dark-800 rounded-xl animate-pulse"></div>
    </div>
  {:else}
    <div class="grid grid-cols-4 grid-rows-3 gap-4">
      <!-- 1 -->
      {#if arts[0]}
        <div class="col-span-2 row-span-2">
          <ArtCard artwork={arts[0]} />
        </div>
      {/if}

      <!-- 2 -->
      {#if arts[1]}
        <div>
          <ArtCard artwork={arts[1]} />
        </div>
      {/if}

      <!-- 3 -->
      {#if arts[2]}
        <div>
          <ArtCard artwork={arts[2]} />
        </div>
      {/if}

      <!-- 6 -->
      {#if arts[5]}
        <div class="col-span-2 row-span-2">
          <ArtCard artwork={arts[5]} />
        </div>
      {/if}

      <!-- 4 -->
      {#if arts[3]}
        <div>
          <ArtCard artwork={arts[3]} />
        </div>
      {/if}

      <!-- 5 -->
      {#if arts[4]}
        <div>
          <ArtCard artwork={arts[4]} />
        </div>
      {/if}
    </div>
  {/if}
</section>

  <!-- Guest Chat Section -->
  <section>
    <GuestChat />
  </section>

</div>
