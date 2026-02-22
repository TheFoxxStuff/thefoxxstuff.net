<script>
  import { onMount } from 'svelte';
  import { api, getImageUrl, API_BASE } from '$lib/api';
  import { Breadcrumb, MarkdownRenderer } from '$lib/components';
  import { player } from '$lib/stores/player.js';
  import ImageLightbox from '$lib/components/ImageLightbox.svelte';

  let { data } = $props();

  let release = $state(data.release);
  let loading = $state(false);

  let coverImageUrl = $derived(release?.cover_image_info ? getImageUrl(release.cover_image_info, 'medium') : null);
  let ogImageUrl = $derived(release?.og_image_info
    ? getImageUrl(release.og_image_info, 'original')
    : coverImageUrl);

  // Lightbox state
  let lbOpen = $state(false);
  let lbSrc = $state('');
  let lbOriginalSrc = $state('');
  let lbAlt = $state('');

  function openGalleryImage(img) {
    lbSrc     = getImageUrl(img, 'medium') || getImageUrl(img, 'thumb') || '';
    lbOriginalSrc = getImageUrl(img, 'original') || lbSrc;
    lbAlt     = img.gallery_name || '';
    lbOpen    = true;
  }

  const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

  function fileUrl(path) {
    return path ? `${API_BASE}/upload/file/${path}` : null;
  }

  function playTrack(index) {
    if (!release) return;
    const s = $player;
    if (s.release?._id === release._id && s.currentIndex === index) {
      player.togglePlay();
    } else if (s.release?._id === release._id) {
      player.playIndex(index);
    } else {
      player.playRelease(release, index);
    }
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

  function isTrackPlaying(index) {
    const s = $player;
    return s.release?._id === release?._id && s.currentIndex === index && s.isPlaying;
  }

  function isTrackActive(index) {
    const s = $player;
    return s.release?._id === release?._id && s.currentIndex === index;
  }

  onMount(() => {
    if (release?._id) api.views.record('music', release._id);
  });

  let seoTitle       = $derived(release?.meta_title || release?.title || 'Music');
  let seoDescription = $derived(release?.meta_description || release?.description?.substring(0, 160) || '');
  let seoImage       = $derived(ogImageUrl || coverImageUrl || '');
  let seoKeywords    = $derived(release?.meta_keywords || '');

  // How many tracks have download options
  let hasDownloads = $derived(release?.tracks?.some(t => t.audio_original || t.audio_mp3_320 || t.audio_mp3_128));
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

<!-- pb-28 = leaves room for the fixed music player at the bottom -->
<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-28 min-[829px]:max-w-[828px] min-[829px]:px-0">
  {#if release}
    <Breadcrumb items={[{ href: '/music', label: 'Music' }, { href: `/music/${release.slug || release._id}`, label: release.title }]} />

    <!-- ── Hero ──────────────────────────────────────────────── -->
    <div class="mt-6 flex flex-col md:flex-row gap-8">
      <!-- Cover (click to enlarge) -->
      <button
        class="w-full md:w-64 aspect-square bg-dark-800 rounded-xl overflow-hidden flex-shrink-0 shadow-2xl group relative cursor-zoom-in"
        onclick={() => {
          if (release.cover_image_info) {
            lbSrc = getImageUrl(release.cover_image_info, 'medium') || '';
            lbOriginalSrc = getImageUrl(release.cover_image_info, 'original') || lbSrc;
            lbAlt = release.title;
            lbOpen = true;
          }
        }}
        aria-label="View cover art"
        type="button"
      >
        {#if release.cover_image_info}
          <img
            src={getImageUrl(release.cover_image_info, 'medium')}
            alt={release.title}
            class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
          <div class="absolute inset-0 flex items-end justify-end p-3 opacity-0 group-hover:opacity-100 transition-opacity">
            <div class="w-8 h-8 rounded-lg bg-black/60 backdrop-blur-sm flex items-center justify-center">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
              </svg>
            </div>
          </div>
        {:else}
          <div class="w-full h-full flex items-center justify-center text-dark-600">
            <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 19V6l12-3v13" />
            </svg>
          </div>
        {/if}
      </button>

      <!-- Meta -->
      <div class="flex-1 flex flex-col justify-between min-w-0">
        <div>
          <p class="text-xs text-dark-500 mb-1 uppercase tracking-widest">{release.release_type}</p>
          <h1 class="font-display text-3xl md:text-4xl tracking-wide mb-3 text-white leading-tight">{release.title}</h1>
          <div class="space-y-1 text-sm text-dark-400 mb-6">
            <p>Released: {formatDate(release.release_date)}</p>
            {#if release.genre}<p>Genre: {release.genre}</p>{/if}
            <p>{release.tracks?.length || 0} track{release.tracks?.length !== 1 ? 's' : ''}</p>
            {#if release.price}<p>{release.price}</p>{/if}
          </div>
        </div>
        <div class="flex gap-3 flex-wrap">
          {#if release.download_flac}
            <a href={release.download_flac} class="btn btn-secondary gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
              FLAC
            </a>
          {/if}
          {#if release.download_mp3}
            <a href={release.download_mp3} class="btn btn-secondary gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
              MP3
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

    <!-- ── Description ───────────────────────────────────────── -->
    {#if release.description}
      <section class="mt-10">
        <h2 class="font-display text-2xl tracking-wide mb-4 text-white">About</h2>
        <MarkdownRenderer content={release.description} />
      </section>
    {/if}

    <!-- ── Tracklist ─────────────────────────────────────────── -->
    {#if release.tracks?.length > 0}
      <section class="mt-10">
        <h2 class="font-display text-2xl tracking-wide mb-4 text-white">Tracklist</h2>
        <div class="bg-dark-900 rounded-xl border border-white/5 overflow-hidden divide-y divide-white/5">
          {#each release.tracks as track, i}
            <div class="group flex items-center gap-3 px-4 py-3 transition-colors {isTrackActive(i) ? 'bg-dark-800' : 'hover:bg-dark-800/50'}">

              <!-- Play / number -->
              {#if track.audio_opus}
                <button
                  onclick={() => playTrack(i)}
                  class="w-8 h-8 flex items-center justify-center rounded-full flex-shrink-0 transition-colors
                    {isTrackActive(i) ? 'bg-accent-green text-dark-950' : 'bg-dark-700 text-dark-300 group-hover:bg-dark-600'}"
                  aria-label="{isTrackPlaying(i) ? 'Pause' : 'Play'} {track.title}"
                >
                  {#if isTrackPlaying(i)}
                    <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
                  {:else}
                    <svg class="w-3.5 h-3.5 ml-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                  {/if}
                </button>
              {:else}
                <span class="w-8 h-8 flex items-center justify-center text-dark-500 flex-shrink-0 text-sm tabular-nums">{track.number || i + 1}</span>
              {/if}

              <!-- Title (links to track page) -->
              <a
                href="/music/{release.slug || release._id}/track/{i}"
                class="flex-1 text-sm truncate transition-colors {isTrackActive(i) ? 'text-accent-green font-medium' : 'text-dark-300 hover:text-white'}"
              >
                {track.title}
              </a>

              <!-- Downloads (hover) -->
              {#if track.audio_original || track.audio_mp3_320 || track.audio_mp3_128}
                <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {#if track.audio_original?.endsWith('.flac')}
                    <button onclick={() => downloadTrack(track.audio_original, track.title, 'flac')}
                      class="px-2 py-0.5 text-xs bg-dark-700 hover:bg-dark-600 rounded transition-colors text-dark-300">FLAC</button>
                  {/if}
                  {#if track.audio_mp3_320}
                    <button onclick={() => downloadTrack(track.audio_mp3_320, track.title, 'mp3')}
                      class="px-2 py-0.5 text-xs bg-dark-700 hover:bg-dark-600 rounded transition-colors text-dark-300">320</button>
                  {/if}
                  {#if track.audio_mp3_128}
                    <button onclick={() => downloadTrack(track.audio_mp3_128, track.title, 'mp3')}
                      class="px-2 py-0.5 text-xs bg-dark-700 hover:bg-dark-600 rounded transition-colors text-dark-300">128</button>
                  {/if}
                </div>
              {/if}

              <span class="text-dark-500 font-mono text-xs flex-shrink-0 tabular-nums">{track.duration || ''}</span>
            </div>
          {/each}
        </div>
      </section>
    {/if}

    <!-- ── Gallery ───────────────────────────────────────────── -->
    {#if release.gallery_images?.length > 0}
      <section class="mt-10">
        <h2 class="font-display text-2xl tracking-wide mb-4 text-white">Gallery</h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {#each release.gallery_images as img}
            <button
              type="button"
              onclick={() => openGalleryImage(img)}
              class="group aspect-square bg-dark-800 rounded-xl overflow-hidden relative cursor-zoom-in
                     hover:ring-2 hover:ring-accent-green/40 transition-all duration-200"
              aria-label="View {img.gallery_name || 'image'}"
            >
              <img
                src={getImageUrl(img, 'thumb')}
                alt={img.gallery_name || ''}
                class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
              />
              <!-- Zoom icon overlay -->
              <div class="absolute inset-0 flex items-end justify-end p-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <div class="w-7 h-7 rounded-lg bg-black/60 backdrop-blur-sm flex items-center justify-center">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
                    <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
                  </svg>
                </div>
              </div>
              <!-- Caption -->
              {#if img.gallery_name}
                <div class="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/70 to-transparent px-2 pt-4 pb-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                  <p class="text-white text-xs truncate">{img.gallery_name}</p>
                </div>
              {/if}
            </button>
          {/each}
        </div>
      </section>
    {/if}

    <!-- ── Production / Liner notes ──────────────────────────── -->
    <div class="mt-10 grid md:grid-cols-2 gap-6">
      {#if release.production_notes}
        <section class="bg-dark-900 rounded-xl p-6 border border-white/5">
          <h2 class="font-display text-xl tracking-wide mb-4 text-white">Production Notes</h2>
          <MarkdownRenderer content={release.production_notes} />
        </section>
      {/if}
      {#if release.liner_notes}
        <section class="bg-dark-900 rounded-xl p-6 border border-white/5">
          <h2 class="font-display text-xl tracking-wide mb-4 text-white">Liner Notes</h2>
          <MarkdownRenderer content={release.liner_notes} />
        </section>
      {/if}
    </div>
  {/if}
</div>

<!-- Universal lightbox (z-10100, above header z-9998 and player z-9999) -->
<ImageLightbox bind:open={lbOpen} src={lbSrc} originalSrc={lbOriginalSrc} alt={lbAlt} />
