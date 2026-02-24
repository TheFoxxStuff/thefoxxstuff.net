<script>
  import { getImageUrl } from '$lib/api';
  let { artwork } = $props();

  // Бэкенд теперь всегда отдаёт image_info через батчевый $in запрос.
  // Fallback через api.upload.getInfo() УБРАН — он создавал N отдельных
  // запросов на странице со списком (N+1 проблема на фронтенде).
  const imageUrl = $derived.by(() => {
    if (artwork.image_info) return getImageUrl(artwork.image_info, 'thumb');
    if (artwork.image_url) return artwork.image_url;
    return null;
  });
</script>

<a href="/arts/{artwork.slug || artwork._id}" class="block group">
  <div class="aspect-square rounded-xl overflow-hidden bg-[--w8]">
    {#if imageUrl}
      <img
        loading="lazy"
        src={imageUrl}
        alt={artwork.title}
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
  </div>
</a>
