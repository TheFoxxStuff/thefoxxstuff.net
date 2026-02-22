<script>
  import { getImageUrl } from '$lib/api';
  import ImageLightbox from '$lib/components/ImageLightbox.svelte';

  let { artwork, showLightbox = true } = $props();

  const imageUrl = $derived.by(() => {
    if (artwork.image_info) return getImageUrl(artwork.image_info, 'thumb');
    if (artwork.image_url) return artwork.image_url;
    return null;
  });

  const originalUrl = $derived.by(() => {
    if (artwork.image_info) return getImageUrl(artwork.image_info, 'original') || imageUrl;
    return imageUrl;
  });

  let lbOpen = $state(false);

  function handleClick(e) {
    if (showLightbox) {
      e.preventDefault();
      lbOpen = true;
    }
  }
</script>

<a
  href="/arts/{artwork.slug || artwork._id}"
  class="block group relative"
  onclick={handleClick}
>
  <div class="aspect-square bg-dark-800 rounded-xl overflow-hidden relative">
    {#if imageUrl}
      <img
        loading="lazy"
        src={imageUrl}
        alt={artwork.title || 'Artwork'}
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
      />
    {:else}
      <div class="w-full h-full flex items-center justify-center text-dark-600">
        <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
    {/if}

    <!-- Hover overlay with title -->
    <div class="absolute inset-0 bg-gradient-to-t from-black/75 via-black/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end">
      <div class="p-3 w-full">
        {#if artwork.title}
          <p class="text-white text-sm font-medium leading-tight truncate">{artwork.title}</p>
        {/if}
        {#if artwork.category}
          <p class="text-white/60 text-xs mt-0.5">{artwork.category}</p>
        {/if}
      </div>

      <!-- Zoom/link icon -->
      <div class="absolute top-2 right-2 w-7 h-7 bg-black/60 backdrop-blur-sm rounded-lg flex items-center justify-center">
        {#if showLightbox}
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
            <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
          </svg>
        {:else}
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
          </svg>
        {/if}
      </div>
    </div>
  </div>
</a>

{#if showLightbox}
  <ImageLightbox
    bind:open={lbOpen}
    src={imageUrl || ''}
    originalSrc={originalUrl || ''}
    alt={artwork.title || ''}
  />
{/if}
