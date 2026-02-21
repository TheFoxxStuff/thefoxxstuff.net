<script>
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { api, getImageUrl } from '$lib/api';
  import { Breadcrumb, MarkdownRenderer } from '$lib/components';
  import { Calendar, Eye, Maximize, Download, Image as ImageIcon } from 'lucide-svelte';
  import Badge from '../../../lib/components/Badge.svelte';
  
  let artwork = $state(null);
  let loading = $state(true);
  let imageUrl = $state(null);
  let ogImageUrl = $state(null);
  
  let aspectRatio = $derived.by(() => {
    if (!artwork?.dimensions) return '1/1';
    const [w, h] = artwork.dimensions.split('x').map(Number);
    return `${w} / ${h}`;
  });

  const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { 
    year: 'numeric', month: 'long', day: 'numeric' 
  });

  async function handleDownload() {
    const url = getImageUrl(artwork.image_info, 'medium');
    const fileName = `${artwork.title.replace(/[/\\?%*:|"<>]/g, '-') || 'artwork'}.png`;

    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
      console.error('Download error:', error);
      window.open(url, '_blank');
    }
  }
  
  
  onMount(async () => {
    try {
      artwork = await api.arts.get($page.params.id);

      // fire-and-forget: не блокирует рендер (api.views.record уже void)
      if (artwork._id) api.views.record('arts', artwork._id);

      // image_info уже в ответе — дополнительный запрос не нужен
      if (artwork.image_info) {
        imageUrl = getImageUrl(artwork.image_info, 'medium');
        // og_image fallback: используем основное изображение если og_image_info нет
        ogImageUrl = artwork.og_image_info
          ? getImageUrl(artwork.og_image_info, 'original')
          : imageUrl;
      }
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  });
  
  // SEO computed values
  let seoTitle = $derived(artwork?.meta_title || artwork?.title || 'Artwork');
  let seoDescription = $derived(artwork?.meta_description || artwork?.description?.substring(0, 160) || '');
  let seoImage = $derived(ogImageUrl || imageUrl || '');
  let seoKeywords = $derived(artwork?.meta_keywords || '');
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
  {#if loading}
    <div class="animate-pulse space-y-6">
      <div class="h-8 w-48 bg-white/5 rounded"></div>
      <div class="w-full bg-white/5 rounded-xl aspect-square"></div>
    </div>
  {:else if artwork}
    <a href="/arts" class="inline-flex items-center text-[--w60] hover:text-[--w] transition-all duration-100 gap-2 px-4 py-2 bg-[--w5] hover:bg-[--w8] rounded-lg text-sm mb-2">
      ← Back to arts
    </a>
    <Breadcrumb items={[{ href: '/arts', label: 'Arts' }, { href: `/arts/${artwork.slug || artwork._id}`, label: artwork.title }]} />
    
    <div class="flex flex-col mt-[20px] gap-[12px]">
      <div 
        class="w-full bg-white-[--w8] rounded-[8px] overflow-hidden shadow-2xl"
        style="aspect-ratio: {aspectRatio};"
      >
        {#if artwork.image_info}
          <img 
            src={getImageUrl(artwork.image_info, 'medium')} 
            alt={artwork.title} 
            class="w-full h-full object-contain"
            loading="eager"
          />
        {:else}
          <div class="w-full h-full flex items-center justify-center text-white-[--w60]">
            <ImageIcon size={64} strokeWidth={1} />
          </div>
        {/if}
      </div>
      
      <div class="rounded-[8px] bg-[--w5] pt-[36px] pr-[36px] pb-[42px] pl-[36px]">
        <h1 style="font-family: 'DrukWideCyr';" class="font-display text-[24px] tracking-wide font-black uppercase text-[--w] mb-[16px]">
          {artwork.title}
        </h1>
        
        <div class="flex flex-wrap items-center gap-[8px] mb-8">
          <Badge text={formatDate(artwork.created_at)} icon={Calendar} />
          <Badge text="{artwork.views} views" icon={Eye} />
          
          <div class="flex-1"></div>
          <Badge text="{artwork.dimensions || 'Original Size'}" icon={Maximize} />
          {#if artwork.image_info}
            <button 
              onclick={handleDownload}
              class="hover:bg-[--w12] rounded-[5px] transition-all duration-100 cursor-pointer"
            >
              <Badge text="Download ({artwork.file_size || 'Original'})" icon={Download} />
            </button>
          {/if}
        </div>
        
        {#if artwork.description}
          <h2 class="text-xl font-bold text-[--w] mb-4">Description</h2>
          <div class="prose prose-invert max-w-none text-[--w60] font-light leading-relaxed">
            <MarkdownRenderer content={artwork.description} />
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .font-display {
    font-family: 'Inter', sans-serif;
  }
</style>
