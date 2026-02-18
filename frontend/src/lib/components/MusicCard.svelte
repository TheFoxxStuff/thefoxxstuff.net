<script>
  import { getImageUrl } from '$lib/api';
  import { player } from '$lib/stores/player.js';
  import { Play, Pause } from 'lucide-svelte';

  let { release, eager = false } = $props();

  const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short' });

  const coverUrl = $derived.by(() => {
    if (release.cover_image_info) return getImageUrl(release.cover_image_info, 'thumb');
    if (release.cover_image && release.cover_image.startsWith('http')) return release.cover_image;
    return null;
  });

  const isPlaying = $derived($player.visible && $player.release?._id === release._id && $player.isPlaying);
  const isLoaded = $derived($player.visible && $player.release?._id === release._id);

  function handlePlay(e) {
    e.preventDefault();
    e.stopPropagation();
    if (isLoaded) {
      player.togglePlay();
    } else {
      player.load(release);
    }
  }
</script>

<a href="/music/{release.slug || release._id}" class="block group relative rounded-[12px] overflow-hidden bg-[--w5] hover:bg-[--w8] transition-all duration-200 card-lift">
  <!-- Cover -->
  <div class="aspect-square bg-dark-800 overflow-hidden relative">
    {#if coverUrl}
      <img
        loading={eager ? 'eager' : 'lazy'}
        src={coverUrl}
        alt={release.title}
        class="w-full h-full object-cover transition-transform duration-400 group-hover:scale-[1.06]"
      />
    {:else}
      <div class="w-full h-full flex items-center justify-center" style="background: linear-gradient(135deg, #1a1a1a 0%, #222 100%)">
        <svg class="w-10 h-10 text-dark-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
        </svg>
      </div>
    {/if}

    <!-- Overlay gradient on hover -->
    <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200"></div>

    <!-- Play button overlay -->
    <button
      onclick={handlePlay}
      class="absolute bottom-2 right-2 w-9 h-9 rounded-full flex items-center justify-center transition-all duration-200
             {isLoaded ? 'opacity-100 scale-100' : 'opacity-0 scale-90 group-hover:opacity-100 group-hover:scale-100'}
             {isPlaying ? 'bg-[--green] text-black' : 'bg-white/90 text-black hover:bg-white'}"
      aria-label={isPlaying ? 'Pause' : 'Play'}
    >
      {#if isPlaying}
        <Pause size={15} fill="currentColor" />
      {:else}
        <Play size={15} fill="currentColor" class="translate-x-[1px]" />
      {/if}
    </button>

    <!-- NEW badge -->
    {#if release.is_new}
      <span class="absolute top-2 left-2 px-2 py-[3px] text-[10px] font-bold tracking-wider bg-[--green] text-black rounded-[5px] uppercase">NEW</span>
    {/if}

    <!-- Playing indicator -->
    {#if isLoaded && !isPlaying}
      <div class="absolute top-2 right-2 w-2 h-2 rounded-full bg-[--green]" style="box-shadow: 0 0 8px rgba(115,238,7,0.6)"></div>
    {/if}
  </div>

  <!-- Info -->
  <div class="px-3 py-3">
    <p class="text-[15px] font-medium text-[--w] truncate leading-tight {isLoaded ? 'text-gradient' : ''}">{release.title}</p>
    <p class="text-[12px] text-[--w40] mt-[2px]">{formatDate(release.release_date)}</p>
  </div>
</a>

<style>
  .text-gradient {
    background: linear-gradient(90deg, #73EE07, #47ADFF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .duration-400 { transition-duration: 400ms; }
</style>
