<script>
  import { onMount } from 'svelte';
  import { api, getImageUrl } from '$lib/api';
  import { Breadcrumb, MarkdownRenderer, SEO } from '$lib/components';
  import { Calendar, Eye, Maximize, Download, Image as ImageIcon } from 'lucide-svelte';
  import Badge from '../../../lib/components/Badge.svelte';
  import { SITE, canonicalUrl, truncate } from '$lib/seo.js';

  let { data: pageData } = $props();
  let artwork = $state(pageData.artwork);

  let imageUrl = $derived(artwork?.image_info ? getImageUrl(artwork.image_info, 'medium') : null);
  let ogImageUrl = $derived(artwork?.og_image_info ? getImageUrl(artwork.og_image_info, 'original') : imageUrl);

  let aspectRatio = $derived.by(() => {
    if (!artwork?.dimensions) return '1/1';
    const [w, h] = artwork.dimensions.split('x').map(Number);
    return `${w} / ${h}`;
  });

  const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  const isoDate = (d) => d ? new Date(d).toISOString() : '';

  let seoTitle = $derived(artwork?.meta_title || artwork?.title || 'Artwork');
  let seoDescription = $derived(truncate(artwork?.meta_description || artwork?.description?.replace(/[#*`\[\]]/g, '').trim() || `Digital artwork by TheFoxxStuff`, 160));
  let seoImage = $derived(ogImageUrl || imageUrl || SITE.defaultImage);
  let seoKeywords = $derived(artwork?.meta_keywords || `art, digital art, ${artwork?.title || ''}, thefoxxstuff`);
  let seoUrl = $derived(artwork ? canonicalUrl(`/arts/${artwork.slug || artwork._id}`) : canonicalUrl('/arts'));

  let jsonLd = $derived(artwork ? {
    '@context': 'https://schema.org',
    '@type': 'VisualArtwork',
    name: seoTitle,
    description: seoDescription,
    image: seoImage,
    url: seoUrl,
    dateCreated: isoDate(artwork.created_at),
    artMedium: 'Digital',
    creator: { '@type': 'Person', name: SITE.author, url: SITE.url },
  } : null);

  async function handleDownload() {
    const url = getImageUrl(artwork.image_info, 'medium');
    const fileName = `${artwork.title.replace(/[/\\?%*:|"<>]/g, '-') || 'artwork'}.png`;
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl; link.download = fileName;
      document.body.appendChild(link); link.click(); document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    } catch { window.open(url, '_blank'); }
  }

  onMount(() => {
    if (artwork?._id) api.views.record('arts', artwork._id);
  });
</script>

<SEO
  title={seoTitle}
  description={seoDescription}
  keywords={seoKeywords}
  image={seoImage}
  imageAlt={seoTitle}
  type="website"
  url={seoUrl}
  jsonLd={jsonLd}
/>

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0">
  {#if !artwork}
    <div class="card p-12 text-center text-dark-400">Artwork not found</div>
  {:else}
    <a href="/arts" class="inline-flex items-center text-[--w60] hover:text-[--w] transition-all duration-100 gap-2 px-4 py-2 bg-[--w5] hover:bg-[--w8] rounded-lg text-sm mb-2">
      ← Back to arts
    </a>
    <Breadcrumb items={[{ href: '/arts', label: 'Arts' }, { href: `/arts/${artwork.slug || artwork._id}`, label: artwork.title }]} />

    <div class="flex flex-col mt-[20px] gap-[12px]">
      <div class="w-full bg-white-[--w8] rounded-[8px] overflow-hidden shadow-2xl" style="aspect-ratio: {aspectRatio};">
        {#if artwork.image_info}
          <img src={getImageUrl(artwork.image_info, 'medium')} alt={artwork.title} class="w-full h-full object-contain" loading="eager" />
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
          <Badge text={artwork.dimensions || 'Original Size'} icon={Maximize} />
          {#if artwork.image_info}
            <button onclick={handleDownload} class="hover:bg-[--w12] rounded-[5px] transition-all duration-100 cursor-pointer">
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
  .font-display { font-family: 'Inter', sans-serif; }
</style>
