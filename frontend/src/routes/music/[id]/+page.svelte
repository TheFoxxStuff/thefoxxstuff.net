<script>
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { api, getImageUrl, API_BASE } from '$lib/api';
  import { Breadcrumb, MarkdownRenderer } from '$lib/components';
  import { player } from '$lib/stores/player.js';
  import ImageLightbox from '$lib/components/ImageLightbox.svelte';

  let release = $state(null);
  let loading = $state(true);
  let coverImageUrl = $state(null);
  let ogImageUrl = $state(null);
  let shareCopied = $state(false);

  // Lightbox state
  let lbOpen = $state(false);
  let lbSrc = $state('');
  let lbOriginalSrc = $state('');
  let lbAlt = $state('');

  function openGalleryImage(img) {
    lbSrc = getImageUrl(img, 'medium') || getImageUrl(img, 'thumb') || '';
    lbOriginalSrc = getImageUrl(img, 'original') || lbSrc;
    lbAlt = img.gallery_name || '';
    lbOpen = true;
  }

  const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

  function fileUrl(path) { return path ? `${API_BASE}/upload/file/${path}` : null; }

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

  // Share with timestamp
  function shareTrackAt(index) {
    const s = $player;
    const t = (s.release?._id === release?._id && s.currentIndex === index)
      ? Math.floor(s.currentTime || 0)
      : 0;
    const url = `${window.location.origin}/music/${release.slug || release._id}?t=${t}&track=${index}`;
    if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(() => {
        shareCopied = index;
        setTimeout(() => shareCopied = false, 2000);
      });
    }
  }

  onMount(async () => {
    try {
      release = await api.music.get($page.params.id);
      if (release.cover_image_info) coverImageUrl = getImageUrl(release.cover_image_info, 'medium');
      if (release.og_image_info) ogImageUrl = getImageUrl(release.og_image_info, 'original');
      else if (coverImageUrl) ogImageUrl = coverImageUrl;
      if (release._id) api.views.record('music', release._id);

      // Handle ?t= and ?track= query params
      const searchParams = new URLSearchParams(window.location.search);
      const trackIdx = parseInt(searchParams.get('track') || '0');
      const timeOffset = parseInt(searchParams.get('t') || '0');
      if (trackIdx >= 0 && release.tracks?.[trackIdx]?.audio_opus) {
        player.playRelease(release, trackIdx);
        // TODO: seek to timeOffset once audio loads
      }
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  });

  let seoTitle = $derived(release?.meta_title || release?.title || 'Music');
  let seoDescription = $derived(release?.meta_description || release?.description?.substring(0, 160) || '');
  let seoImage = $derived(ogImageUrl || coverImageUrl || '');
  let seoKeywords = $derived(release?.meta_keywords || '');

  // Streaming services links (from model or hardcoded fallback)
  const STREAMING = [
    { key: 'spotify', label: 'Spotify', color: '#1DB954', icon: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/></svg>` },
    { key: 'apple_music', label: 'Apple Music', color: '#FA233B', icon: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23.994 6.124a9.23 9.23 0 00-.24-2.19c-.317-1.31-1.062-2.31-2.18-3.043a5.022 5.022 0 00-1.877-.726 10.496 10.496 0 00-1.564-.15c-.04-.003-.083-.01-.124-.013H5.986c-.152.01-.303.017-.455.026C4.786.07 4.043.15 3.34.428 2.067.986 1.134 1.887.524 3.147A6.963 6.963 0 00.09 5.19 55.648 55.648 0 000 6.834v10.582c.01.582.074 1.16.18 1.73.29 1.68 1.157 2.957 2.556 3.86a6.14 6.14 0 001.987.651 15.77 15.77 0 001.792.163c.206.01.41.011.614.011h10.28c.432 0 .864-.007 1.296-.035a11.09 11.09 0 001.707-.214c1.467-.382 2.517-1.23 3.182-2.578a7.348 7.348 0 00.598-2.163c.07-.475.102-.954.107-1.433 0-.073.007-.147.007-.22V6.985c-.002-.29-.007-.578-.016-.862zM12.03 7.588v6.126c0 .657-.183 1.14-.554 1.447-.42.349-1.007.444-1.762.283-.515-.11-1.004-.497-1.198-1.01-.224-.584-.085-1.26.362-1.697.25-.243.657-.44 1.222-.591.234-.063.694-.197.694-.197V8.68a.247.247 0 00-.198-.243l-3.11.54a.238.238 0 00-.197.237v5.82c0 .676-.195 1.163-.588 1.46-.42.322-.99.406-1.714.25-.54-.12-1.012-.52-1.193-1.041-.198-.59-.036-1.258.41-1.683.254-.24.66-.44 1.222-.587.234-.064.694-.198.694-.198V7.237c0-.118.085-.22.203-.238l4.822-.84a.24.24 0 01.283.238v.19l.602-.062v.063z"/></svg>` },
    { key: 'youtube_music', label: 'YouTube', color: '#FF0000', icon: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>` },
    { key: 'soundcloud', label: 'SoundCloud', color: '#FF5500', icon: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M1.175 12.225c-.057 0-.11.02-.148.06-.037.04-.056.09-.056.145l.215 2.207-.215 2.184c0 .057.02.107.056.148.038.04.09.06.148.06.11 0 .197-.09.215-.2l.247-2.192-.247-2.22c-.02-.11-.106-.192-.215-.192zm1.72-.5c-.084 0-.15.032-.198.082-.05.05-.077.12-.077.203l.196 2.724-.196 2.682c0 .083.027.155.077.205.048.05.114.077.198.077.15 0 .267-.11.285-.26l.222-2.704-.222-2.755c-.02-.15-.135-.254-.285-.254zm8.337-5.49c-.145 0-.29.03-.428.086-1.135-1.262-2.73-2.059-4.52-2.059C2.787 4.262 0 7.05 0 10.5c0 .144.008.287.02.428 0 0 .04 2.29.04 2.33 0 .05.02.098.054.133.036.035.083.054.133.054h10.985c.06 0 .116-.024.157-.065.04-.04.063-.097.063-.157V8.235c0-1.105-.895-2-2-2z"/></svg>` },
    { key: 'bandcamp', label: 'Bandcamp', color: '#1DA0C3', icon: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M0 18.75l7.437-13.5H24l-7.438 13.5z"/></svg>` },
  ];

  const streamingLinks = $derived.by(() => {
    if (!release?.streaming_links) return [];
    return STREAMING.filter(s => release.streaming_links[s.key]);
  });
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

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-28 min-[829px]:max-w-[828px] min-[829px]:px-0">
  {#if loading}
    <div class="animate-pulse space-y-4">
      <div class="h-6 w-48 bg-dark-800 rounded"></div>
      <div class="flex gap-6">
        <div class="w-64 aspect-square bg-dark-800 rounded-xl flex-shrink-0"></div>
        <div class="flex-1 space-y-3 pt-2">
          <div class="h-5 bg-dark-800 rounded w-3/4"></div>
          <div class="h-4 bg-dark-800 rounded w-1/2"></div>
        </div>
      </div>
    </div>
  {:else if release}
    <Breadcrumb items={[{ href: '/music', label: 'Music' }, { href: `/music/${release.slug || release._id}`, label: release.title }]} />

    <!-- Hero -->
    <div class="mt-6 flex flex-col md:flex-row gap-8">
      <!-- Cover -->
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
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>
            </div>
          </div>
        {:else}
          <div class="w-full h-full flex items-center justify-center text-dark-600">
            <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 19V6l12-3v13" /></svg>
          </div>
        {/if}
      </button>

      <!-- Meta -->
      <div class="flex-1 flex flex-col justify-between min-w-0">
        <div>
          <p class="text-xs text-dark-500 mb-1 uppercase tracking-widest">{release.release_type || 'Release'}</p>
          <h1 class="font-display text-3xl md:text-4xl tracking-wide mb-3 text-white leading-tight">{release.title}</h1>
          <div class="space-y-1 text-sm text-dark-400 mb-5">
            <p>Released: {formatDate(release.release_date)}</p>
            {#if release.genre}<p>Genre: {release.genre}</p>{/if}
            <p>{release.tracks?.length || 0} track{release.tracks?.length !== 1 ? 's' : ''}</p>
          </div>

          <!-- Streaming links -->
          {#if streamingLinks.length > 0}
            <div class="mb-5">
              <p class="text-[12px] text-[--w60] uppercase tracking-wide mb-2">Listen on</p>
              <div class="flex gap-2 flex-wrap">
                {#each streamingLinks as s}
                  <a
                    href={release.streaming_links[s.key]}
                    target="_blank"
                    rel="noopener noreferrer"
                    class="flex items-center gap-2 px-3 py-1.5 bg-[--w8] hover:bg-[--w12] rounded-lg text-[13px] text-[--w] transition-all"
                    style="border-left: 2px solid {s.color};"
                  >
                    <span class="w-4 h-4">{@html s.icon}</span>
                    {s.label}
                  </a>
                {/each}
              </div>
            </div>
          {/if}
        </div>

        <div class="flex gap-3 flex-wrap">
          {#if release.tracks?.find(t => t.audio_opus)}
            <button
              onclick={() => player.playRelease(release, 0)}
              class="btn btn-primary gap-2"
            >
              <svg class="w-4 h-4 ml-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
              Play All
            </button>
          {/if}
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

    <!-- Description -->
    {#if release.description}
      <section class="mt-10">
        <h2 class="font-display text-2xl tracking-wide mb-4 text-white">About</h2>
        <MarkdownRenderer content={release.description} />
      </section>
    {/if}

    <!-- Tracklist -->
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
                  class="w-8 h-8 flex items-center justify-center rounded-full flex-shrink-0 transition-all
                    {isTrackActive(i) ? 'bg-accent-green text-dark-950' : 'bg-dark-700 text-dark-300 group-hover:bg-dark-600'}"
                  aria-label="{isTrackPlaying(i) ? 'Pause' : 'Play'} {track.title}"
                >
                  {#if isTrackPlaying(i)}
                    <div class="equalizer">
                      <span class="bar"></span><span class="bar"></span><span class="bar"></span>
                    </div>
                  {:else}
                    <svg class="w-3.5 h-3.5 ml-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                  {/if}
                </button>
              {:else}
                <span class="w-8 h-8 flex items-center justify-center text-dark-500 flex-shrink-0 text-sm tabular-nums">{track.number || i + 1}</span>
              {/if}

              <!-- Title -->
              <span class="flex-1 text-sm truncate transition-colors {isTrackActive(i) ? 'text-accent-green font-medium' : 'text-dark-300'}">
                {track.title}
              </span>

              <!-- Share this track at current time -->
              <button
                onclick={() => shareTrackAt(i)}
                class="w-7 h-7 flex items-center justify-center text-dark-600 hover:text-dark-300 transition-colors opacity-0 group-hover:opacity-100 flex-shrink-0"
                title="Share link to this track"
              >
                {#if shareCopied === i}
                  <svg class="w-3.5 h-3.5 text-accent-green" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
                {:else}
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/></svg>
                {/if}
              </button>

              <!-- Downloads -->
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

    <!-- Gallery -->
    {#if release.gallery_images?.length > 0}
      <section class="mt-10">
        <h2 class="font-display text-2xl tracking-wide mb-4 text-white">Gallery</h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {#each release.gallery_images as img}
            <button
              type="button"
              onclick={() => openGalleryImage(img)}
              class="group aspect-square bg-dark-800 rounded-xl overflow-hidden relative cursor-zoom-in hover:ring-2 hover:ring-accent-green/40 transition-all duration-200"
              aria-label="View {img.gallery_name || 'image'}"
            >
              <img src={getImageUrl(img, 'thumb')} alt={img.gallery_name || ''} class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
              <div class="absolute inset-0 flex items-end justify-end p-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <div class="w-7 h-7 rounded-lg bg-black/60 backdrop-blur-sm flex items-center justify-center">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>
                </div>
              </div>
            </button>
          {/each}
        </div>
      </section>
    {/if}

    <!-- Production / Liner notes -->
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

<ImageLightbox bind:open={lbOpen} src={lbSrc} originalSrc={lbOriginalSrc} alt={lbAlt} />
