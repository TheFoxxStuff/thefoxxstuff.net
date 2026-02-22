<script>
  import { onMount } from 'svelte';
  import { api, getImageUrl, API_BASE } from '$lib/api';
  import { Breadcrumb, MarkdownRenderer } from '$lib/components';
  import Badge from '../../../lib/components/Badge.svelte';
  import { Calendar, Eye } from 'lucide-svelte';

  let { data } = $props();

  let post = $state(data.post);
  let coverImageUrl = $derived(post?.cover_image_info ? getImageUrl(post.cover_image_info, 'medium') : null);
  let ogImageUrl = $derived(post?.og_image_info ? getImageUrl(post.og_image_info, 'medium') : coverImageUrl);

  const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

  let seoTitle = $derived(post?.meta_title || post?.title || 'Blog');
  let seoDescription = $derived(post?.meta_description || post?.excerpt || '');
  let seoImage = $derived(ogImageUrl || coverImageUrl || '');
  let seoKeywords = $derived(post?.meta_keywords || '');

  onMount(() => {
    if (post?._id) api.views.record('blog', post._id);
  });
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

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0">
  {#if !post}
    <div class="card p-12 text-center text-dark-400">Post not found</div>
  {:else}
    <a href="/blog" class="inline-flex items-center text-[--w60] hover:text-[--w] transition-all duration-100 gap-2 px-4 py-2 bg-[--w5] hover:bg-[--w8] rounded-lg text-sm mb-2">
      ← Back to the blog
    </a>
    <Breadcrumb items={[{ href: '/blog', label: 'Blog' }, { href: `/blog/${post.slug || post._id}`, label: post.title }]} />

    <article class="card mt-8 overflow-hidden">
      {#if coverImageUrl}
        <div class="aspect-video bg-dark-800 overflow-hidden">
          <img loading="eager" src={coverImageUrl} alt={post.title} class="w-full h-full object-cover" />
        </div>
      {/if}

      <div class="p-[36px] pb-[56px] md:p-[36px] md:pb-[42px]">
        <h1 class="font-display text-[24px] md:text-4xl tracking-wide mb-[18px]">{post.title}</h1>

        <div class="flex gap-[8px] text-sm text-dark-400 mb-[20px] pb-[20px] border-b border-[rgba(255,255,255,0.05)]">
          <Badge text={formatDate(post.created_at)} icon={Calendar} />
          <Badge text="{post.views} views" icon={Eye} />
        </div>

        <MarkdownRenderer content={post.content} />
      </div>
    </article>
  {/if}
</div>
