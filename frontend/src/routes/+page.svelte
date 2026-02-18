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

  let bannerLoading = $state(true);
  let contentLoading = $state(true);

  let currentSlide = $state(0);
  let slideInterval;

  let musicPage = $state(1);
  let blogPage = $state(1);

  const nextSlide = () => {
    if (banner.slides.length > 0) currentSlide = (currentSlide + 1) % banner.slides.length;
  };
  const prevSlide = () => {
    if (banner.slides.length > 0) currentSlide = (currentSlide - 1 + banner.slides.length) % banner.slides.length;
  };
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
      })
      .catch(() => {})
      .finally(() => { contentLoading = false; });

    slideInterval = setInterval(nextSlide, 5000);
    return () => clearInterval(slideInterval);
  });
</script>

<svelte:head><title>Homepage | TheFoxxStuff</title></svelte:head>

<div class="mx-auto max-w-6xl px-4 pt-5 pb-12 min-[829px]:max-w-[828px] min-[829px]:px-0" style="display: flex; flex-direction: column; gap: 28px;">

  <!-- Banner -->
  <div class="animate-fade-in-up">
    <Banner {banner} {currentSlide} {getImageUrl} {nextSlide} {prevSlide} {goToSlide} />
  </div>

  <!-- Music Section -->
  <section class="animate-fade-in-up delay-100">
    <div class="flex items-center justify-between mb-4">
      <h2 class="font-display text-xl tracking-wide text-[--w]">Music</h2>
      <Button href="/music" iconRight={ChevronRight}>All releases</Button>
    </div>
    {#if contentLoading}
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        {#each Array(4) as _}
          <div class="rounded-[12px] overflow-hidden">
            <div class="aspect-square skeleton"></div>
            <div class="p-3 space-y-2">
              <div class="h-3 skeleton w-3/4"></div>
              <div class="h-2.5 skeleton w-1/2"></div>
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        {#each music.items as release, i}
          <MusicCard {release} eager={i < 4} />
        {/each}
      </div>
      {#if music.pages > 1}
        <div class="mt-3">
          <Pagination currentPage={musicPage} totalPages={music.pages} onPageChange={loadMusic} />
        </div>
      {/if}
    {/if}
  </section>

  <!-- Divider -->
  <div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);"></div>

  <!-- Blog Section -->
  <section class="animate-fade-in-up delay-150">
    <div class="flex items-center justify-between mb-4">
      <h2 class="font-display text-xl tracking-wide text-[--w]">Blog</h2>
      <Button href="/blog" iconRight={ChevronRight}>All posts</Button>
    </div>
    {#if contentLoading}
      <div class="grid md:grid-cols-2 gap-3">
        {#each Array(2) as _}
          <div class="rounded-[14px] overflow-hidden bg-[--w5]">
            <div style="height:180px" class="skeleton"></div>
            <div class="p-4 space-y-2">
              <div class="h-4 skeleton w-5/6"></div>
              <div class="h-3 skeleton w-3/4"></div>
              <div class="h-3 skeleton w-1/2"></div>
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <div class="grid md:grid-cols-2 gap-3">
        {#each blog.items as post}
          <BlogCard {post} />
        {/each}
      </div>
      {#if blog.pages > 1}
        <div class="mt-3">
          <Pagination currentPage={blogPage} totalPages={blog.pages} onPageChange={loadBlog} />
        </div>
      {/if}
    {/if}
  </section>

  <!-- Divider -->
  <div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);"></div>

  <!-- Arts Section -->
  <section class="animate-fade-in-up delay-200">
    <div class="flex items-center justify-between mb-4">
      <h2 class="font-display text-xl tracking-wide text-[--w]">Arts</h2>
      <Button href="/arts" iconRight={ChevronRight}>All arts</Button>
    </div>
    {#if contentLoading}
      <div class="grid grid-cols-4 grid-rows-3 gap-3" style="height: 320px;">
        <div class="col-span-2 row-span-2 skeleton"></div>
        <div class="skeleton"></div>
        <div class="skeleton"></div>
        <div class="col-span-2 row-span-2 skeleton"></div>
        <div class="skeleton"></div>
        <div class="skeleton"></div>
      </div>
    {:else}
      <div class="grid grid-cols-4 grid-rows-3 gap-3" style="height: 320px;">
        {#if arts[0]}<div class="col-span-2 row-span-2"><ArtCard artwork={arts[0]} /></div>{/if}
        {#if arts[1]}<div><ArtCard artwork={arts[1]} /></div>{/if}
        {#if arts[2]}<div><ArtCard artwork={arts[2]} /></div>{/if}
        {#if arts[5]}<div class="col-span-2 row-span-2"><ArtCard artwork={arts[5]} /></div>{/if}
        {#if arts[3]}<div><ArtCard artwork={arts[3]} /></div>{/if}
        {#if arts[4]}<div><ArtCard artwork={arts[4]} /></div>{/if}
      </div>
    {/if}
  </section>

  <!-- Divider -->
  <div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);"></div>

  <!-- Chat -->
  <section class="animate-fade-in-up delay-300">
    <GuestChat />
  </section>

</div>
