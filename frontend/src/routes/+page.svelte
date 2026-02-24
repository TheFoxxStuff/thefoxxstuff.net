<script>
  import { onMount } from 'svelte';
  import { api, getImageUrl } from '$lib/api';
  import { MusicCard, BlogCard, ArtCard, Pagination, SEO, OnlineUsers } from '$lib/components';
  import { ChevronRight } from 'lucide-svelte';
  import Button from '$lib/components/Button.svelte';
  import Banner from '../lib/components/Banner.svelte';
  import GuestChat from '$lib/components/GuestChat.svelte';
  import { SITE, canonicalUrl } from '$lib/seo.js';
  import { presence } from '$lib/stores/presence.js';

  let { data: pageData } = $props();

  let music = $derived(pageData.music);
  let blog = $derived(pageData.blog);
  let arts = $derived(pageData.arts);
  let banner = $derived(pageData.banner);

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
    slideInterval = setInterval(nextSlide, 5000);
    // presence.startGlobal() вызывается в +layout.svelte — не нужно здесь
    return () => {
      clearInterval(slideInterval);
    };
  });

  const homeJsonLd = [
    {
      '@context': 'https://schema.org',
      '@type': 'WebSite',
      name: SITE.name,
      url: SITE.url,
      potentialAction: {
        '@type': 'SearchAction',
        target: { '@type': 'EntryPoint', urlTemplate: `${SITE.url}/search?q={search_term_string}` },
        'query-input': 'required name=search_term_string',
      },
    },
    {
      '@context': 'https://schema.org',
      '@type': 'MusicGroup',
      name: SITE.name,
      url: SITE.url,
      description: SITE.description,
      genre: ['Hardcore', 'Breakcore', "Drum'n'Bass"],
      foundingLocation: { '@type': 'Place', name: 'Yakutsk, Republic of Sakha, Russia' },
      sameAs: [SITE.twitterUrl, SITE.vkUrl, SITE.telegramUrl, SITE.bandcamp, SITE.soundcloud],
    },
  ];
</script>

<SEO
  url={canonicalUrl('/')}
  jsonLd={homeJsonLd}
/>

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0 space-y-[20px]">

  <Banner {banner} {currentSlide} {getImageUrl} {nextSlide} {prevSlide} {goToSlide} />

  <!-- Music Section -->
  <section>
    <div class="flex items-center justify-between mb-6">
      <h2 class="font-display text-2xl tracking-wide">Music</h2>
      <Button href="/music" iconRight={ChevronRight}>Show more</Button>
    </div>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      {#each music.items as release, i}
        <MusicCard {release} eager={i < 4} />
      {/each}
    </div>
    {#if music.pages > 1}
      <div class="mt-[12px]">
        <Pagination currentPage={musicPage} totalPages={music.pages} onPageChange={loadMusic} />
      </div>
    {/if}
  </section>

  <!-- Blog Section -->
  <section>
    <div class="flex items-center justify-between mb-6">
      <h2 class="font-display text-2xl tracking-wide">Blog</h2>
      <Button href="/blog" iconRight={ChevronRight}>Show more</Button>
    </div>
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
  </section>

  <!-- Arts Section -->
  <section>
    <div class="flex items-center justify-between mb-6">
      <h2 class="font-display text-2xl tracking-wide">Arts</h2>
      <Button href="/arts" iconRight={ChevronRight}>Show more</Button>
    </div>
    <div class="grid grid-cols-4 grid-rows-3 gap-4">
      {#if arts[0]}<div class="col-span-2 row-span-2"><ArtCard artwork={arts[0]} /></div>{/if}
      {#if arts[1]}<div><ArtCard artwork={arts[1]} /></div>{/if}
      {#if arts[2]}<div><ArtCard artwork={arts[2]} /></div>{/if}
      {#if arts[5]}<div class="col-span-2 row-span-2"><ArtCard artwork={arts[5]} /></div>{/if}
      {#if arts[3]}<div><ArtCard artwork={arts[3]} /></div>{/if}
      {#if arts[4]}<div><ArtCard artwork={arts[4]} /></div>{/if}
    </div>
  </section>

  <!-- Chat -->
  <section>
    <GuestChat />
  </section>

  <!-- Online Users -->
  <section class="card p-4">
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-accent-green animate-pulse"></span>
        <h2 class="text-sm font-medium text-[--w60] uppercase tracking-wider">Who's Online</h2>
      </div>
      <span class="text-xs text-[--w30]">
        {$presence.onlineCount} user{$presence.onlineCount !== 1 ? 's' : ''}
      </span>
    </div>
    {#if $presence.onlineCount > 0}
      <OnlineUsers users={$presence.online} count={$presence.onlineCount} />
    {:else}
      <p class="text-xs text-[--w30] py-2">No users online right now</p>
    {/if}
  </section>

</div>
