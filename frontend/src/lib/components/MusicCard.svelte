<script>
  import { getImageUrl } from '$lib/api';
  let { release } = $props();
  const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  
  // Get cover image URL from either new image info or legacy URL
  const coverUrl = $derived.by(() => {
    if (release.cover_image_info) return getImageUrl(release.cover_image_info, 'thumb');
    if (release.cover_image && release.cover_image.startsWith('http')) return release.cover_image;
    return null;
  });
</script>

<a href="/music/{release._id}" class="block group rounded-[8px] px-[18px] py-[18px] bg-[--w5] hover:bg-[--w8] duration-100">
  <div class="aspect-square bg-dark-800 rounded-[8px] overflow-hidden mb-[14px] relative">
    {#if coverUrl}
      <img loading="lazy" src={coverUrl} alt={release.title} class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200" />
    {:else}
      <div class="w-full h-full flex items-center justify-center text-dark-600">
        <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
        </svg>
      </div>
    {/if}
    {#if release.is_new}
      <span class="absolute top-2 right-2 px-2 py-1 text-xs font-medium bg-[--green] text-[--b] rounded">NEW RELEASE</span>
    {/if}
  </div>
  <span class="text-[18px] text-[--w] tracking-wide truncate">{release.title}</span>
  <p class="text-[14px] text-[--w60]">{formatDate(release.release_date)}</p>
</a>
