<script>
  import { getImageUrl } from '$lib/api';
  import { player } from '$lib/stores/player.js';

  let { release, eager = false } = $props();

  const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

  const coverUrl = $derived.by(() => {
    if (release.cover_image_info) return getImageUrl(release.cover_image_info, 'thumb');
    if (release.cover_image && release.cover_image.startsWith('http')) return release.cover_image;
    return null;
  });

  // Check if this release is currently playing
  const isPlaying = $derived(
    $player.release?._id === release._id && $player.isPlaying
  );
  const isActive = $derived(
    $player.release?._id === release._id
  );

  function handlePlayClick(e) {
    e.preventDefault();
    e.stopPropagation();
    if (isActive) {
      player.togglePlay();
    } else {
      player.playRelease(release, 0);
    }
  }
</script>

<a href="/music/{release.slug || release._id}" class="block group rounded-[8px] px-[18px] py-[18px] bg-[--w5] hover:bg-[--w8] duration-200 transition-colors relative">
  <!-- Cover image -->
  <div class="aspect-square bg-dark-800 rounded-[8px] overflow-hidden mb-[14px] relative">
    {#if coverUrl}
      <img
        loading={eager ? 'eager' : 'lazy'}
        src={coverUrl}
        alt={release.title}
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
      />
    {:else}
      <div class="w-full h-full flex items-center justify-center text-dark-600">
        <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
        </svg>
      </div>
    {/if}

    <!-- NEW badge -->
    {#if release.is_new}
      <span class="absolute top-2 left-2 px-2 py-1 text-xs font-medium bg-[--green] text-[--b] rounded z-10">NEW</span>
    {/if}

    <!-- Play overlay on hover -->
    <div class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-[8px]">
      <button
        onclick={handlePlayClick}
        class="w-12 h-12 flex items-center justify-center bg-white rounded-full shadow-xl hover:scale-110 transition-transform duration-150"
        aria-label="{isPlaying ? 'Pause' : 'Play'} {release.title}"
      >
        {#if isPlaying}
          <!-- Pause icon -->
          <svg class="w-5 h-5 text-dark-950" fill="currentColor" viewBox="0 0 24 24">
            <rect x="6" y="4" width="4" height="16"/>
            <rect x="14" y="4" width="4" height="16"/>
          </svg>
        {:else}
          <!-- Play icon -->
          <svg class="w-5 h-5 ml-0.5 text-dark-950" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z"/>
          </svg>
        {/if}
      </button>
    </div>

    <!-- Equalizer when actively playing (not on hover) -->
    {#if isPlaying}
      <div class="absolute bottom-2 right-2 equalizer pointer-events-none">
        <span class="bar"></span>
        <span class="bar"></span>
        <span class="bar"></span>
        <span class="bar"></span>
      </div>
    {/if}
  </div>

  <!-- Title + meta -->
  <div class="flex items-start justify-between gap-2">
    <div class="min-w-0">
      <span class="text-[16px] text-[--w] tracking-wide truncate block leading-tight" class:text-accent-green={isActive}>
        {release.title}
      </span>
      <p class="text-[13px] text-[--w60] mt-0.5">{formatDate(release.release_date)}</p>
    </div>
    {#if release.genre}
      <span class="text-[11px] text-[--w60] bg-[--w8] px-2 py-0.5 rounded flex-shrink-0 mt-0.5">{release.genre}</span>
    {/if}
  </div>
</a>
