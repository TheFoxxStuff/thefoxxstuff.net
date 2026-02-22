<script>
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { api, getImageUrl, API_BASE } from '$lib/api';
  import { Breadcrumb, MarkdownRenderer, ReadingProgress } from '$lib/components';
  import Badge from '../../../lib/components/Badge.svelte';
  import { Calendar, Eye, Clock, Share2 } from 'lucide-svelte';

  let post = $state(null);
  let loading = $state(true);
  let coverImageUrl = $state(null);
  let ogImageUrl = $state(null);
  let shareCopied = $state(false);

  // Reactions state
  const REACTIONS = [
    { key: 'fire', emoji: '🔥', label: 'Fire' },
    { key: 'music', emoji: '🎵', label: 'Vibes' },
    { key: 'mind', emoji: '🤯', label: 'Mind blown' },
    { key: 'love', emoji: '💜', label: 'Love' },
  ];
  let reactions = $state({ fire: 0, music: 0, mind: 0, love: 0 });
  let myReactions = $state(new Set());

  const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

  const readingTime = $derived.by(() => {
    if (post?.reading_time_min) return post.reading_time_min;
    if (post?.content) return Math.max(1, Math.ceil(post.content.split(/\s+/).length / 200));
    return null;
  });

  function sharePost() {
    const url = window.location.href;
    if (navigator.share) {
      navigator.share({ title: post?.title, url });
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(() => {
        shareCopied = true;
        setTimeout(() => shareCopied = false, 2000);
      });
    }
  }

  async function react(key) {
    if (myReactions.has(key)) return; // already reacted
    myReactions = new Set([...myReactions, key]);
    reactions = { ...reactions, [key]: (reactions[key] || 0) + 1 };
    // Fire and forget to backend
    try {
      await fetch(`${API_BASE}/blog/${post._id}/react`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reaction: key })
      });
    } catch {}
  }

  onMount(async () => {
    try {
      post = await api.blog.get($page.params.id);
      if (post._id) api.views.record('blog', post._id);
      if (post.cover_image_info) coverImageUrl = getImageUrl(post.cover_image_info, 'medium');
      if (post.og_image_info)    ogImageUrl    = getImageUrl(post.og_image_info, 'medium');
      // Load reactions if available
      if (post.reactions) reactions = { ...reactions, ...post.reactions };
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  });

  let seoTitle = $derived(post?.meta_title || post?.title || 'Blog');
  let seoDescription = $derived(post?.meta_description || post?.excerpt || '');
  let seoImage = $derived(ogImageUrl || coverImageUrl || '');
  let seoKeywords = $derived(post?.meta_keywords || '');
</script>

<svelte:head>
  <title>{seoTitle} | TheFoxxStuff</title>
  {#if seoDescription}<meta name="description" content={seoDescription} />{/if}
  {#if seoKeywords}<meta name="keywords" content={seoKeywords} />{/if}
  <meta property="og:title" content={seoTitle} />
  {#if seoDescription}<meta property="og:description" content={seoDescription} />{/if}
  {#if seoImage}<meta property="og:image" content={seoImage} />{/if}
  <meta property="og:type" content="article" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content={seoTitle} />
  {#if seoDescription}<meta name="twitter:description" content={seoDescription} />{/if}
  {#if seoImage}<meta name="twitter:image" content={seoImage} />{/if}
</svelte:head>

<!-- Reading progress bar -->
{#if post && !loading}
  <ReadingProgress />
{/if}

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0">
  {#if loading}
    <div class="animate-pulse"><div class="h-8 w-48 bg-dark-800 rounded"></div></div>
  {:else if post}
    <a href="/blog" class="inline-flex items-center text-[--w60] hover:text-[--w] transition-all duration-100 gap-2 px-4 py-2 bg-[--w5] hover:bg-[--w8] rounded-lg text-sm mb-2">
      ← Back to the blog
    </a>
    <Breadcrumb items={[{ href: '/blog', label: 'Blog' }, { href: `/blog/${post.slug || post._id}`, label: post.title }]} />

    <article class="card mt-8 overflow-hidden">
      {#if coverImageUrl}
        <div class="aspect-video bg-dark-800 overflow-hidden">
          <img loading="lazy" src={coverImageUrl} alt={post.title} class="w-full h-full object-cover" />
        </div>
      {/if}

      <div class="p-[36px] pb-[42px]">
        <!-- Tags -->
        {#if post.tags?.length}
          <div class="flex gap-2 mb-4 flex-wrap">
            {#each post.tags as tag}
              <span class="text-[12px] px-2.5 py-1 bg-[--w8] text-[--w60] rounded-lg border border-[--w8]">{tag}</span>
            {/each}
          </div>
        {/if}

        <h1 class="font-display text-[28px] md:text-4xl tracking-wide mb-[14px] leading-tight">{post.title}</h1>

        <div class="flex flex-wrap gap-[8px] text-sm text-dark-400 mb-[24px] pb-[20px] border-b border-[rgba(255,255,255,0.05)] items-center">
          <Badge text={formatDate(post.created_at)} icon={Calendar} />
          <Badge text="{post.views} views" icon={Eye} />
          {#if readingTime}
            <Badge text="{readingTime} min read" icon={Clock} />
          {/if}
          <div class="ml-auto">
            <button
              onclick={sharePost}
              class="flex items-center gap-1.5 px-3 py-1.5 bg-[--w8] hover:bg-[--w12] rounded-lg text-[13px] text-[--w60] hover:text-[--w] transition-all"
            >
              <Share2 size={13} />
              {shareCopied ? 'Copied!' : 'Share'}
            </button>
          </div>
        </div>

        <MarkdownRenderer content={post.content} />

        <!-- Reactions -->
        <div class="mt-10 pt-6 border-t border-[--w8]">
          <p class="text-[--w60] text-[13px] mb-3">How did this land?</p>
          <div class="flex gap-3 flex-wrap">
            {#each REACTIONS as r}
              <button
                onclick={() => react(r.key)}
                class="flex items-center gap-2 px-4 py-2 rounded-xl text-[15px] border transition-all
                  {myReactions.has(r.key)
                    ? 'bg-[--w8] border-[--green] text-[--w]'
                    : 'bg-[--w5] border-[--w8] text-[--w60] hover:bg-[--w8] hover:border-[--w12] hover:text-[--w]'}
                  active:scale-95"
                title={r.label}
              >
                <span>{r.emoji}</span>
                {#if reactions[r.key]}
                  <span class="text-[13px] font-medium">{reactions[r.key]}</span>
                {/if}
              </button>
            {/each}
          </div>
        </div>
      </div>
    </article>

    <!-- Share CTA -->
    <div class="mt-6 p-5 bg-[--w5] rounded-[12px] flex flex-col sm:flex-row items-start sm:items-center gap-4">
      <div class="flex-1">
        <p class="text-[--w] text-[15px] font-medium">Liked this?</p>
        <p class="text-[--w60] text-[13px]">Share it or follow for more releases and writings.</p>
      </div>
      <div class="flex gap-2">
        <button
          onclick={sharePost}
          class="px-4 py-2 bg-[--green] text-[--b] rounded-lg text-[13px] font-bold hover:opacity-90 transition-opacity"
        >
          {shareCopied ? '✓ Copied!' : '↗ Share Post'}
        </button>
        <a href="https://t.me/thefoxxstuff" target="_blank" rel="noopener" class="px-4 py-2 bg-[--w8] text-[--w] rounded-lg text-[13px] hover:bg-[--w12] transition-colors">
          Follow →
        </a>
      </div>
    </div>
  {/if}
</div>
