<script>
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { api, getImageUrl, API_BASE } from '$lib/api';
  import { Breadcrumb } from '$lib/components';
  import { player, currentTrack } from '$lib/stores/player.js';
  
  let release = $state(null);
  let loading = $state(true);
  let lightboxImage = $state(null);
  let coverImageUrl = $state(null);
  let ogImageUrl = $state(null);
  
  const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  
  function parseMarkdown(md) {
    if (!md) return '';
    return md
      .replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold mt-4 mb-2 text-white">$1</h3>')
      .replace(/^## (.+)$/gm, '<h2 class="text-xl font-semibold mt-6 mb-3 text-white">$1</h2>')
      .replace(/^# (.+)$/gm, '<h1 class="text-2xl font-bold mt-8 mb-4 text-white">$1</h1>')
      .replace(/\*\*(.+?)\*\*/g, '<strong class="text-white font-bold">$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/`(.+?)`/g, '<code class="px-1 py-0.5 bg-dark-800 rounded text-sm">$1</code>')
      .replace(/!\[(.+?)\]\((.+?)\)/g, '<img src="$2" alt="$1" class="rounded-lg max-w-full my-4" />')
      .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" class="text-accent-green hover:underline">$1</a>')
      .replace(/^- (.+)$/gm, '<li class="ml-4">$1</li>')
      .replace(/(<li.*<\/li>)/s, '<ul class="list-disc my-2">$1</ul>')
      .replace(/\n\n/g, '</p><p class="my-3">')
      .replace(/\n/g, '<br>');
  }
  
  function fileUrl(path) {
    if (!path) return null;
    return `${API_BASE}/upload/file/${path}`;
  }
  
  // Use global player to play tracks
  function playTrack(index) {
    if (!release) return;
    const playerState = $player;
    
    // If same release and same track, just toggle
    if (playerState.release?._id === release._id && playerState.currentIndex === index) {
      player.togglePlay();
      return;
    }
    
    // If same release but different track
    if (playerState.release?._id === release._id) {
      player.playIndex(index);
      return;
    }
    
    // New release
    player.playRelease(release, index);
  }
  
  function downloadTrack(path, trackTitle, ext) {
    if (!path) return;
    const a = document.createElement('a');
    a.href = fileUrl(path);
    a.download = `${trackTitle || 'track'}.${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
  
  // Check if this track is currently playing in global player
  function isTrackPlaying(index) {
    const s = $player;
    return s.release?._id === release?._id && s.currentIndex === index && s.isPlaying;
  }
  
  function isTrackActive(index) {
    const s = $player;
    return s.release?._id === release?._id && s.currentIndex === index;
  }
  
  let hasAnyAudio = $derived(release?.tracks?.some(t => t.audio_opus));
  
  onMount(async () => {
    try {
      release = await api.music.get($page.params.id);
      if (release.cover_image_info) {
        coverImageUrl = getImageUrl(release.cover_image_info, 'medium');
      }
      if (release.og_image) {
        try {
          const imgInfo = await api.upload.getInfo(release.og_image);
          ogImageUrl = getImageUrl(imgInfo, 'original');
        } catch {}
      }
      // Record view with IP tracking
      if (release._id) {
        api.views.record('music', release._id).catch(() => {});
      }
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  });
  
  const openLightbox = (img) => { lightboxImage = img; };
  const closeLightbox = () => { lightboxImage = null; };
  
  let seoTitle = $derived(release?.meta_title || release?.title || 'Music');
  let seoDescription = $derived(release?.meta_description || release?.description?.substring(0, 160) || '');
  let seoImage = $derived(ogImageUrl || coverImageUrl || '');
  let seoKeywords = $derived(release?.meta_keywords || '');
</script>

<svelte:head>
  <title>{seoTitle} | TheFoxxStuff</title>
  {#if seoDescription}<meta name="description" content={seoDescription} />{/if}
  {#if seoKeywords}<meta name="keywords" content={seoKeywords} />{/if}
  <meta property="og:title" content={seoTitle} />
  {#if seoDescription}<meta property="og:description" content={seoDescription} />{/if}
  {#if seoImage}<meta property="og:image" content={seoImage} />{/if}
  <meta property="og:type" content="music.album" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content={seoTitle} />
  {#if seoDescription}<meta name="twitter:description" content={seoDescription} />{/if}
  {#if seoImage}<meta name="twitter:image" content={seoImage} />{/if}
</svelte:head>

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0">
  {#if loading}
    <div class="animate-pulse"><div class="h-8 w-64 bg-dark-800 rounded mb-8"></div></div>
  {:else if release}
    <h1 class="font-display text-3xl tracking-wide mb-2">{release.title} ({new Date(release.release_date).getFullYear()})</h1>
    <Breadcrumb items={[{ href: '/music', label: 'Music' }, { href: `/music/${release.slug || release._id}`, label: release.title }]} />
    
    <div class="mt-8 flex flex-col md:flex-row gap-8">
      <!-- Cover Image -->
      <div class="w-full md:w-80 aspect-square bg-dark-800 rounded-xl overflow-hidden flex-shrink-0">
        {#if release.cover_image_info}
          <img loading="lazy" src={getImageUrl(release.cover_image_info, 'medium')} alt={release.title} class="w-full h-full object-cover" />
        {:else}
          <div class="w-full h-full flex items-center justify-center text-dark-600">
            <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 19V6l12-3v13" />
            </svg>
          </div>
        {/if}
      </div>
      
      <!-- Info -->
      <div class="flex-1">
        <h2 class="font-display text-4xl tracking-wide mb-4">{release.title}</h2>
        <div class="space-y-1 text-sm text-dark-400 mb-6">
          <p>Released: {formatDate(release.release_date)}</p>
          <p>Number of tracks: {release.tracks?.length || 0}</p>
          <p>Genre: {release.genre}</p>
          <p>Type: {release.release_type}</p>
          <p>Price: {release.price}</p>
        </div>
        <div class="flex gap-3 flex-wrap">
          {#if release.download_flac}
            <a href={release.download_flac} class="btn btn-secondary">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
              DOWNLOAD FLAC
            </a>
          {/if}
          {#if release.download_mp3}
            <a href={release.download_mp3} class="btn btn-secondary">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
              DOWNLOAD MP3
            </a>
          {/if}
          {#if release.bandcamp_url}
            <a href={release.bandcamp_url} target="_blank" rel="noopener" class="btn btn-primary">
              BUY ON BANDCAMP
            </a>
          {/if}
        </div>
      </div>
    </div>
    
    <!-- Description (Markdown) -->
    {#if release.description}
      <section class="mt-12">
        <h3 class="font-display text-2xl tracking-wide mb-4">Description</h3>
        <div class="prose prose-invert max-w-none text-dark-300 leading-relaxed">
          {@html parseMarkdown(release.description)}
        </div>
      </section>
    {/if}
    
    <!-- Track List -->
    {#if release.tracks?.length > 0}
      <section class="mt-12">
        <h3 class="font-display text-2xl tracking-wide mb-4">Track List</h3>
        <div class="space-y-1">
          {#each release.tracks as track, i}
            <div class="group rounded-lg transition-colors {isTrackActive(i) ? 'bg-dark-800' : 'hover:bg-dark-900'}">
              <div class="flex items-center py-3 px-4 gap-3">
                {#if track.audio_opus}
                  <button 
                    onclick={() => playTrack(i)} 
                    class="w-8 h-8 flex items-center justify-center rounded-full flex-shrink-0 transition-colors {isTrackActive(i) ? 'bg-accent-green text-dark-950' : 'bg-dark-800 text-dark-300 group-hover:bg-dark-700'}"
                  >
                    {#if isTrackPlaying(i)}
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16" /><rect x="14" y="4" width="4" height="16" /></svg>
                    {:else}
                      <svg class="w-4 h-4 ml-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>
                    {/if}
                  </button>
                {:else}
                  <span class="w-8 h-8 flex items-center justify-center text-dark-500 flex-shrink-0 text-sm">{track.number || i + 1}</span>
                {/if}
                
                <span class="flex-1 text-dark-300 {isTrackActive(i) ? 'text-accent-green font-medium' : ''}">{track.title}</span>
                
                <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {#if track.audio_original?.endsWith('.flac')}
                    <button onclick={() => downloadTrack(track.audio_original, track.title, 'flac')} class="px-2 py-0.5 text-xs bg-dark-700 hover:bg-dark-600 rounded transition-colors text-dark-300" title="Download FLAC">
                      FLAC
                    </button>
                  {/if}
                  {#if track.audio_mp3_320}
                    <button onclick={() => downloadTrack(track.audio_mp3_320, track.title, 'mp3')} class="px-2 py-0.5 text-xs bg-dark-700 hover:bg-dark-600 rounded transition-colors text-dark-300" title="Download MP3 320kbps">
                      MP3 320
                    </button>
                  {/if}
                  {#if track.audio_mp3_128}
                    <button onclick={() => downloadTrack(track.audio_mp3_128, track.title, 'mp3')} class="px-2 py-0.5 text-xs bg-dark-700 hover:bg-dark-600 rounded transition-colors text-dark-300" title="Download MP3 128kbps">
                      MP3 128
                    </button>
                  {/if}
                </div>
                
                <span class="text-dark-500 font-mono text-sm flex-shrink-0">{track.duration}</span>
              </div>
            </div>
          {/each}
        </div>
      </section>
    {/if}
    
    <!-- Gallery -->
    {#if release.gallery_images?.length > 0}
      <section class="mt-12">
        <h3 class="font-display text-2xl tracking-wide mb-4">Gallery</h3>
        <div class="grid grid-cols-4 gap-4">
          {#each release.gallery_images as img}
            <button 
              onclick={() => openLightbox(img)}
              class="aspect-square bg-dark-800 rounded-lg overflow-hidden hover:ring-2 hover:ring-accent-green/50 transition-all"
            >
              <img loading="lazy" src={getImageUrl(img, 'thumb')} alt={img.gallery_name || ''} class="w-full h-full object-cover" />
            </button>
          {/each}
        </div>
      </section>
    {/if}
    
    <!-- Production Notes & Liner Notes -->
    <div class="mt-12 grid md:grid-cols-2 gap-8">
      {#if release.production_notes}
        <section>
          <h3 class="font-display text-2xl tracking-wide mb-4">Production Notes</h3>
          <div class="prose prose-invert max-w-none text-dark-300 leading-relaxed">
            {@html parseMarkdown(release.production_notes)}
          </div>
        </section>
      {/if}
      {#if release.liner_notes}
        <section>
          <h3 class="font-display text-2xl tracking-wide mb-4">Liner Notes</h3>
          <div class="prose prose-invert max-w-none text-dark-300 italic leading-relaxed">
            {@html parseMarkdown(release.liner_notes)}
          </div>
        </section>
      {/if}
    </div>
    
    <!-- Bottom padding for floating player -->
    <div class="h-20"></div>
  {/if}
</div>

<!-- Lightbox -->
{#if lightboxImage}
  <div 
    class="fixed inset-0 bg-dark-950/95 z-50 flex items-center justify-center p-8"
    onclick={closeLightbox}
    onkeydown={(e) => e.key === 'Escape' && closeLightbox()}
    role="dialog"
    tabindex="-1"
  >
    <button onclick={closeLightbox} class="absolute top-4 right-4 p-2 hover:bg-dark-800 rounded-full">
      <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
    <img loading="lazy" src={getImageUrl(lightboxImage, 'original')} alt={lightboxImage.gallery_name || ''} class="max-w-full max-h-full object-contain" />
  </div>
{/if}
