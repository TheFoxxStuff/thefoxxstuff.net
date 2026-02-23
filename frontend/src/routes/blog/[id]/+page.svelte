<script>
  import { onMount } from 'svelte';
  import { api, getImageUrl, API_BASE } from '$lib/api';
  import { Breadcrumb, MarkdownRenderer, SEO } from '$lib/components';
  import Badge from '../../../lib/components/Badge.svelte';
  import ViewingNow from '../../../lib/components/ViewingNow.svelte';
  import { Calendar, Eye } from 'lucide-svelte';
  import { SITE, canonicalUrl, truncate } from '$lib/seo.js';
  import { presence } from '$lib/stores/presence.js';

  let { data: pageData } = $props();

  let post = $state(pageData.post);
  let coverImageUrl = $derived(post?.cover_image_info ? getImageUrl(post.cover_image_info, 'medium') : null);
  let ogImageUrl = $derived(post?.og_image_info ? getImageUrl(post.og_image_info, 'medium') : coverImageUrl);

  const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  const isoDate = (d) => d ? new Date(d).toISOString() : '';

  let seoTitle = $derived(post?.meta_title || post?.title || 'Blog');
  let seoDescription = $derived(truncate(post?.meta_description || post?.excerpt || post?.content?.replace(/[#*`\[\]]/g, '').trim() || '', 160));
  let seoImage = $derived(ogImageUrl || coverImageUrl || SITE.defaultImage);
  let seoKeywords = $derived(post?.meta_keywords || SITE.keywords);
  let seoUrl = $derived(post ? canonicalUrl(`/blog/${post.slug || post._id}`) : canonicalUrl('/blog'));

  let articleMeta = $derived(post ? {
    publishedTime: isoDate(post.created_at),
    modifiedTime: isoDate(post.updated_at || post.created_at),
    author: SITE.author,
    section: 'Blog',
    tags: post.meta_keywords ? post.meta_keywords.split(',').map(k => k.trim()) : [],
  } : null);

  let jsonLd = $derived(post ? {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: seoTitle,
    description: seoDescription,
    image: seoImage,
    url: seoUrl,
    datePublished: isoDate(post.created_at),
    dateModified: isoDate(post.updated_at || post.created_at),
    author: { '@type': 'Person', name: SITE.author, url: SITE.url },
    publisher: { '@type': 'Organization', name: SITE.name, url: SITE.url },
    mainEntityOfPage: { '@type': 'WebPage', '@id': seoUrl },
  } : null);

  onMount(() => {
    if (post?._id) {
      api.views.record('blog', post._id);
      const stopPresence = presence.start('blog', post._id);
      return () => stopPresence?.();
    }
  });
</script>

<SEO
  title={seoTitle}
  description={seoDescription}
  keywords={seoKeywords}
  image={seoImage}
  imageAlt={seoTitle}
  type="article"
  url={seoUrl}
  article={articleMeta}
  jsonLd={jsonLd}
/>

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

        {#if $presence.viewingCount > 0}
          <div class="mb-[20px]">
            <ViewingNow users={$presence.viewing} count={$presence.viewingCount} entityType="blog" />
          </div>
        {/if}

        <MarkdownRenderer content={post.content} />
      </div>
    </article>
  {/if}
</div>
