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

  // Раздельные состояния загрузки: баннер виден сразу, контент подтягивается
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
    // Баннер грузим ПЕРВЫМ — он в viewport сразу
    api.banner.get()
      .then(b => { banner = b; })
      .catch(() => {})
      .finally(() => { bannerLoading = false; });

    // Контент грузим параллельно, но отдельно от баннера
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

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0 space-y-[20px]">

  <!-- Banner: грузится первым, независимо от контента -->
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
          <!-- Первые 4 карточки в viewport — eager, остальные lazy -->
          <MusicCard {release} eager={i < 4} />
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
        {#if arts[0]}<div class="col-span-2 row-span-2"><ArtCard artwork={arts[0]} /></div>{/if}
        {#if arts[1]}<div><ArtCard artwork={arts[1]} /></div>{/if}
        {#if arts[2]}<div><ArtCard artwork={arts[2]} /></div>{/if}
        {#if arts[5]}<div class="col-span-2 row-span-2"><ArtCard artwork={arts[5]} /></div>{/if}
        {#if arts[3]}<div><ArtCard artwork={arts[3]} /></div>{/if}
        {#if arts[4]}<div><ArtCard artwork={arts[4]} /></div>{/if}
      </div>
    {/if}
  </section>

  <!-- Chat -->
  <section>
    <GuestChat />
  </section>

</div>
