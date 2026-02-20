<script>
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { api, getImageUrl, API_BASE } from '$lib/api';
  import { Breadcrumb } from '$lib/components';
  import Badge from '../../../lib/components/Badge.svelte';
  import { Calendar, Eye } from 'lucide-svelte';

  let post = $state(null);
  let loading = $state(true);
  let coverImageUrl = $state(null);
  let ogImageUrl = $state(null);
  
  const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  
  // Simple markdown parser
  function parseMarkdown(md) {
    if (!md) return '';

    let html = md
      .replace(/^### (.+)$/gm, '<h3 class="text-lg text-[#ffffff] font-semibold mt-[12px] mb-[12px]">$1</h3>')
      .replace(/^## (.+)$/gm, '<h2 class="text-xl text-[#ffffff] font-semibold mt-[12px] mb-[12px]">$1</h2>')
      .replace(/^# (.+)$/gm, '<h1 class="text-2xl text-[#ffffff] font-bold mt-[12px] mb-[12px]">$1</h1>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/`(.+?)`/g, '<code class="px-1.5 py-0.5 bg-dark-800 rounded text-sm font-mono">$1</code>')
      .replace(/!\[(.*?)\]\((.*?)\)/g, (match, alt, src) => {
        if (src.startsWith('http')) {
          return `<img loading="lazy" src="${src}" alt="${alt}" class="rounded-lg max-w-full my-6" />`;
        }
        let cleanSrc = src.startsWith('/') ? src.slice(1) : src;
        cleanSrc = cleanSrc.replace(/\\/g, '/');
        const fullUrl = `${API_BASE}/${cleanSrc}`;
        return `<img loading="lazy" src="${fullUrl}" alt="${alt}" class="rounded-lg max-w-full my-6" />`;
      })
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-accent-green hover:underline">$1</a>')
      .replace(/^- (.+)$/gm, '<li class="ml-4 list-disc">$1</li>')
      .split(/\n\n+/).map(p => {
        if (p.trim().startsWith('<')) return p;
        return `<p class="my-4">${p.replace(/\n/g, '<br>')}</p>`;
      }).join('');

    return html;
  }
  
  onMount(async () => {
    try {
      post = await api.blog.get($page.params.id);

      // fire-and-forget: не блокирует рендер
      if (post._id) api.views.record('blog', post._id);

      // cover_image_info и og_image_info уже приходят с бэкенда
      if (post.cover_image_info) coverImageUrl = getImageUrl(post.cover_image_info, 'original');
      if (post.og_image_info)    ogImageUrl    = getImageUrl(post.og_image_info, 'original');
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  });
  
  // Compute SEO values
  let seoTitle = $derived(post?.meta_title || post?.title || 'Blog');
  let seoDescription = $derived(post?.meta_description || post?.excerpt || '');
  let seoImage = $derived(ogImageUrl || coverImageUrl || '');
  let seoKeywords = $derived(post?.meta_keywords || '');
</script>

<svelte:head>
  <title>{seoTitle} | TheFoxxStuff</title>
  {#if seoDescription}
    <meta name="description" content={seoDescription} />
  {/if}
  {#if seoKeywords}
    <meta name="keywords" content={seoKeywords} />
  {/if}
  
  <!-- Open Graph -->
  <meta property="og:title" content={seoTitle} />
  {#if seoDescription}
    <meta property="og:description" content={seoDescription} />
  {/if}
  {#if seoImage}
    <meta property="og:image" content={seoImage} />
  {/if}
  <meta property="og:type" content="article" />
  
  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content={seoTitle} />
  {#if seoDescription}
    <meta name="twitter:description" content={seoDescription} />
  {/if}
  {#if seoImage}
    <meta name="twitter:image" content={seoImage} />
  {/if}
</svelte:head>

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0">
  <!-- Breadcrumb всегда виден — нет layout shift при загрузке -->
  <Breadcrumb
    items={[{ href: '/blog', label: 'Blog' }, { href: '#', label: post?.title ?? '' }]}
    loading={loading || !post}
  />

  {#if loading}
    <div class="animate-pulse mt-2"><div class="h-8 w-48 bg-dark-800 rounded"></div></div>
  {:else if post}
    <a href="/blog" class="inline-flex items-center text-[--w60] hover:text-[--w] transition-all duration-100 gap-2 px-4 py-2 bg-[--w5] hover:bg-[--w8] rounded-lg text-sm mb-2">
      ← Back to the blog
    </a>
    
    <article class="card mt-8 overflow-hidden">
      <!-- Cover Image -->
      {#if coverImageUrl}
        <div class="aspect-video bg-dark-800 overflow-hidden">
          <img loading="lazy" src={coverImageUrl} alt={post.title} class="w-full h-full object-cover" />
        </div>
      {/if}
      
      <div class="p-[36px] pb-[56px] md:p-[36px] md:pb-[42px]">
        <h1 class="font-display text-[24px] md:text-4xl tracking-wide mb-[18px]">{post.title}</h1>
        
        <div class="flex gap-[8px] text-sm text-dark-400 mb-[20px] pb-[20px] border-b border-[rgba(255,255,255,0.05)]">
          <Badge text={formatDate(post.created_at)} icon={Calendar} />
          <Badge text="{post.views} views" icon={Eye} />
        </div>
        
        <!-- Content rendered as markdown -->
        <div class="prose prose-invert prose-green max-w-none text-[rgba(255,255,255,0.6)] text-[16px] leading-relaxed">
          {@html parseMarkdown(post.content)}
        </div>
      </div>
    </article>
  {/if}
</div>

<style>
  .prose :global(img) {
    border-radius: 0.5rem;
    max-width: 100%;
  }
  .prose :global(a) {
    color: #4ade80;
  }
  .prose :global(a:hover) {
    text-decoration: underline;
  }
  .prose :global(code) {
    padding: 0.125rem 0.375rem;
    background: #383838;
    border-radius: 0.25rem;
    font-size: 0.875rem;
    font-family: monospace;
  }
  .prose :global(h2) {
    color: white;
  }
  .prose :global(h3) {
    color: white;
  }
</style>
