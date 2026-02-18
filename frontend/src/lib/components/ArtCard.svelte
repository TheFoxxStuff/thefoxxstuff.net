<script>
  import { getImageUrl } from '$lib/api';
  let { artwork } = $props();

  const imageUrl = $derived.by(() => {
    if (artwork.image_info) return getImageUrl(artwork.image_info, 'thumb');
    if (artwork.image_url) return artwork.image_url;
    return null;
  });
</script>

<a href="/arts/{artwork.slug || artwork._id}" class="block group h-full relative rounded-[10px] overflow-hidden bg-dark-800">
  {#if imageUrl}
    <img
      loading="lazy"
      src={imageUrl}
      alt={artwork.title}
      class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-[1.07]"
    />
  {:else}
    <div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-dark-900 to-dark-800">
      <svg class="w-8 h-8 text-dark-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    </div>
  {/if}

  <!-- Overlay with title -->
  <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-250 flex items-end">
    <div class="p-3 w-full">
      {#if artwork.title}
        <p class="text-[13px] font-medium text-white truncate">{artwork.title}</p>
      {/if}
    </div>
  </div>
</a>
