<script>
  import { getImageUrl } from '$lib/api';
  let { release } = $props();
  const coverUrl = $derived.by(() => {
    if (!release) return null;
    if (release.cover_image_info) return getImageUrl(release.cover_image_info, 'medium');
    if (release.cover_image && release.cover_image.startsWith('http')) return release.cover_image;
    return null;
  });
</script>

{#if release}
<section class="card p-6">
  <div class="flex flex-col md:flex-row gap-6">
    <div class="w-full md:w-80 aspect-square rounded-xl overflow-hidden flex-shrink-0 bg-[--w8]">
      {#if coverUrl}<img loading="lazy" src={coverUrl} alt={release.title} class="w-full h-full object-cover" />
      {:else}<div class="w-full h-full flex items-center justify-center text-dark-600"><svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" /></svg></div>{/if}
    </div>
    <div class="flex-1">
      {#if release.is_new}<span class="inline-block px-3 py-1 text-xs font-medium bg-accent-green text-dark-950 rounded mb-4">NEW RELEASE</span>{/if}
      <h2 class="font-display text-4xl md:text-5xl tracking-wide mb-4">{release.title}</h2>
      {#if release.description}<p class="text-dark-400 mb-6 line-clamp-4">{release.description}</p>{/if}
      <div class="flex flex-wrap gap-3">
        {#if release.bandcamp_url}<a href={release.bandcamp_url} target="_blank" rel="noopener noreferrer" class="btn btn-primary">BUY ON BANDCAMP</a>{/if}
        <a href="/music/{release.slug || release._id}" class="btn btn-secondary">ALBUM PAGE</a>
      </div>
    </div>
  </div>
</section>
{/if}
