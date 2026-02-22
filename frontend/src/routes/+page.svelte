<script>
  import { onMount } from 'svelte';
  import { api, getImageUrl } from '$lib/api';
  import { MusicCard, BlogCard, ArtCard, Pagination, HeroSection } from '$lib/components';
  import { ChevronRight } from 'lucide-svelte';
  import Button from '$lib/components/Button.svelte';
  import Banner from '../lib/components/Banner.svelte';
  import GuestChat from '$lib/components/GuestChat.svelte';

  let music = $state({ items: [], page: 1, pages: 1 });
  let blog = $state({ items: [], page: 1, pages: 1 });
  let arts = $state([]);
  let banner = $state({ slides: [] });
  let latestRelease = $state(null);

  let bannerLoading = $state(true);
  let contentLoading = $state(true);

  let currentSlide = $state(0);
  let slideInterval;

  let musicPage = $state(1);
  let blogPage = $state(1);

  const nextSlide = () => { if (banner.slides.length > 0) currentSlide = (currentSlide + 1) % banner.slides.length; };
  const prevSlide = () => { if (banner.slides.length > 0) currentSlide = (currentSlide - 1 + banner.slides.length) % banner.slides.length; };
  const goToSlide = (index) => { currentSlide = index; };

  const loadMusic = async (page) => {
    musicPage = page;
    try { music = await api.music.list(page, 4); } catch {}
  };
  const loadBlog = async (page) => {
    blogPage = page;
    try { blog = await api.blog.list(page, 2); } catch {}
  };

  onMount(() => {
    api.banner.get()
      .then(b => { banner = b; })
      .catch(() => {})
      .finally(() => { bannerLoading = false; });

    Promise.all([
      api.music.list(musicPage, 4),
      api.blog.list(blogPage, 2),
      api.arts.list(1, 6),
    ])
      .then(([m, b, a]) => {
        music = m;
        blog = b;
        arts = a.items;
        // Latest release for Hero play button
        latestRelease = m.items?.[0] || null;
      })
      .catch(() => {})
      .finally(() => { contentLoading = false; });

    slideInterval = setInterval(nextSlide, 5000);
    return () => clearInterval(slideInterval);
  });
</script>

<svelte:head><title>TheFoxxStuff — Musician · Artist · Blogger</title></svelte:head>

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0 space-y-[20px]">

  <!-- Hero section -->
  {#if !contentLoading}
    <HeroSection {latestRelease} />
  {:else}
    <div class="h-[200px] bg-[--w5] rounded-[12px] animate-pulse"></div>
  {/if}

  <!-- Banner -->
  <Banner
    {banner}
    {currentSlide}
    {getImageUrl}
    {nextSlide}
    {prevSlide}
    {goToSlide}
  />

  <!-- Music Section -->
  <section>
    <div class="flex items-center justify-between mb-6">
      <h2 class="font-display text-2xl tracking-wide">Music</h2>
      <Button href="/music" iconRight={ChevronRight}>Show more</Button>
    </div>
    {#if contentLoading}
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        {#each Array(4) as _}
          <div class="aspect-square bg-dark-800 rounded-xl animate-pulse"></div>
        {/each}
      </div>
    {:else}
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        {#each music.items as release, i}
          <div class="fade-in" style="animation-delay: {i * 60}ms">
            <MusicCard {release} eager={i < 4} />
          </div>
        {/each}
      </div>
      {#if music.pages > 1}
        <div class="mt-[12px]">
          <Pagination currentPage={musicPage} totalPages={music.pages} onPageChange={loadMusic} />
        </div>
      {/if}
    {/if}
  </section>

  <!-- Arts Section (moved above blog — best visual hook) -->
  <section>
    <div class="flex items-center justify-between mb-6">
      <h2 class="font-display text-2xl tracking-wide">Arts</h2>
      <Button href="/arts" iconRight={ChevronRight}>Show more</Button>
    </div>
    {#if contentLoading}
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
        {#if arts[0]}<div class="col-span-2 row-span-2 fade-in"><ArtCard artwork={arts[0]} /></div>{/if}
        {#if arts[1]}<div class="fade-in" style="animation-delay: 80ms"><ArtCard artwork={arts[1]} /></div>{/if}
        {#if arts[2]}<div class="fade-in" style="animation-delay: 120ms"><ArtCard artwork={arts[2]} /></div>{/if}
        {#if arts[5]}<div class="col-span-2 row-span-2 fade-in" style="animation-delay: 160ms"><ArtCard artwork={arts[5]} /></div>{/if}
        {#if arts[3]}<div class="fade-in" style="animation-delay: 200ms"><ArtCard artwork={arts[3]} /></div>{/if}
        {#if arts[4]}<div class="fade-in" style="animation-delay: 240ms"><ArtCard artwork={arts[4]} /></div>{/if}
      </div>
    {/if}
  </section>

  <!-- Blog Section -->
  <section>
    <div class="flex items-center justify-between mb-6">
      <h2 class="font-display text-2xl tracking-wide">Blog</h2>
      <Button href="/blog" iconRight={ChevronRight}>Show more</Button>
    </div>
    {#if contentLoading}
      <div class="grid md:grid-cols-2 gap-4">
        {#each Array(2) as _}
          <div class="card p-4"><div class="aspect-video bg-dark-800 rounded-lg animate-pulse"></div></div>
        {/each}
      </div>
    {:else}
      <div class="grid md:grid-cols-2 gap-4">
        {#each blog.items as post, i}
          <div class="fade-in" style="animation-delay: {i * 80}ms">
            <BlogCard {post} />
          </div>
        {/each}
      </div>
      {#if blog.pages > 1}
        <div class="mt-[12px]">
          <Pagination currentPage={blogPage} totalPages={blog.pages} onPageChange={loadBlog} />
        </div>
      {/if}
    {/if}
  </section>

  <!-- Chat -->
  <section>
    <GuestChat />
  </section>

</div>
