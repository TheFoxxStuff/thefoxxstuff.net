<script>
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { api, getImageUrl, API_BASE } from '$lib/api';
  import { Breadcrumb, MarkdownRenderer, SEO } from '$lib/components';
  import { SITE, canonicalUrl, truncate } from '$lib/seo.js';
  import { player } from '$lib/stores/player.js';
  import ImageLightbox from '$lib/components/ImageLightbox.svelte';

  let release = $state(null);
  let track = $state(null);
  let trackIndex = $state(0);
  let loading = $state(true);
  let coverImageUrl = $state(null);
  let lbOpen = $state(false);
  let lbSrc = $state('');
  let lbOriginalSrc = $state('');
  let lbAlt = $state('');

  const formatDate = (d) => d ? new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : '';

  function fileUrl(path) {
    return path ? `${API_BASE}/upload/file/${path}` : null;
  }

  function isPlaying() {
    const s = $player;
    return s.release?._id === release?._id && s.currentIndex === trackIndex && s.isPlaying;
  }

  function isActive() {
    const s = $player;
    return s.release?._id === release?._id && s.currentIndex === trackIndex;
  }

  function playTrack() {
    if (!release || !track) return;
    const s = $player;
    if (s.release?._id === release._id && s.currentIndex === trackIndex) {
      player.togglePlay();
    } else if (s.release?._id === release._id) {
      player.playIndex(trackIndex);
    } else {
      player.playRelease(release, trackIndex);
    }
  }

  function downloadTrack(path, title, ext) {
    if (!path) return;
    const a = document.createElement('a');
    a.href = fileUrl(path);
    a.download = `${title || 'track'}.${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  onMount(async () => {
    try {
      release = await api.music.get($page.params.id);
      if (release.cover_image_info) coverImageUrl = getImageUrl(release.cover_image_info, 'medium');

      const trackId = $page.params.trackId;
      const idx = release.tracks?.findIndex(
        (t, i) => String(t._id || t.id || i) === trackId || String(i) === trackId
      );
      trackIndex = idx >= 0 ? idx : 0;
      track = release.tracks?.[trackIndex];
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  });

  let seoTitle   = $derived(track ? `${track.title} — ${release?.title}` : 'Track');
  let seoDesc    = $derived(truncate(track?.notes || `${track?.title || 'Track'} from "${release?.title || ''}" by TheFoxxStuff`, 160));
  let seoImg     = $derived(coverImageUrl || SITE.defaultImage);
  let seoUrl     = $derived(release ? canonicalUrl(`/music/${release.slug || release._id}/track/${$page.params.trackId}`) : '');
  let trackJsonLd = $derived(track && release ? {
    '@context': 'https://schema.org',
    '@type': 'MusicRecording',
    name: track.title,
    description: seoDesc,
    image: seoImg,
    url: seoUrl,
    duration: track.duration,
    inAlbum: { '@type': 'MusicAlbum', name: release.title, url: canonicalUrl(`/music/${release.slug || release._id}`) },
    byArtist: { '@type': 'MusicGroup', name: SITE.name, url: SITE.url },
  } : null);
</script>

<SEO
  title={seoTitle}
  description={seoDesc}
  image={seoImg}
  imageAlt={seoTitle}
  type="music.song"
  url={seoUrl}
  jsonLd={trackJsonLd}
/>

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-28 min-[829px]:max-w-[828px] min-[829px]:px-0">
  {#if loading}
    <div class="animate-pulse space-y-4">
      <div class="h-6 w-48 bg-dark-800 rounded"></div>
      <div class="h-48 bg-dark-800 rounded-xl"></div>
    </div>
  {:else if track && release}
    <Breadcrumb items={[
      { href: '/music', label: 'Music' },
      { href: `/music/${release.slug || release._id}`, label: release.title },
      { href: '#', label: track.title }
    ]} />

    <!-- Hero: bandcamp-style -->
    <div class="mt-6 flex flex-col sm:flex-row gap-6 bg-dark-900 rounded-2xl overflow-hidden border border-white/5">
      <!-- Cover -->
      <div class="sm:w-64 sm:flex-shrink-0">
        {#if coverImageUrl}
          <img src={coverImageUrl} alt={release.title} class="w-full aspect-square object-cover" loading="lazy" />
        {:else}
          <div class="w-full aspect-square bg-dark-800 flex items-center justify-center text-dark-600">
            <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 19V6l12-3v13"/></svg>
          </div>
        {/if}
      </div>

      <!-- Info -->
      <div class="flex-1 p-6 flex flex-col justify-between">
        <div>
          <p class="text-sm text-dark-400 mb-1">
            <a href="/music/{release.slug || release._id}" class="hover:text-accent-green transition-colors">{release.title}</a>
            · {release.genre} · {new Date(release.release_date).getFullYear()}
          </p>
          <h1 class="font-display text-3xl md:text-4xl tracking-wide text-white mb-4">{track.title}</h1>

          {#if track.duration}
            <p class="text-sm text-dark-400 mb-4">Duration: {track.duration}</p>
          {/if}

          <!-- Play button -->
          <button
            onclick={playTrack}
            class="flex items-center gap-3 px-6 py-3 rounded-full font-semibold text-sm transition-all
              {isActive() ? 'bg-accent-green text-dark-950' : 'bg-dark-700 hover:bg-dark-600 text-white'}"
          >
            {#if isPlaying()}
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
              Pause
            {:else}
              <svg class="w-5 h-5 ml-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
              Play
            {/if}
          </button>
        </div>

        <!-- Download buttons -->
        <div class="flex gap-2 flex-wrap mt-4">
          {#if track.audio_original?.endsWith('.flac')}
            <button onclick={() => downloadTrack(track.audio_original, track.title, 'flac')}
              class="flex items-center gap-1.5 px-4 py-2 bg-dark-800 hover:bg-dark-700 rounded-lg text-xs font-medium text-dark-300 transition-colors border border-white/5">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              FLAC
            </button>
          {/if}
          {#if track.audio_mp3_320}
            <button onclick={() => downloadTrack(track.audio_mp3_320, track.title, 'mp3')}
              class="flex items-center gap-1.5 px-4 py-2 bg-dark-800 hover:bg-dark-700 rounded-lg text-xs font-medium text-dark-300 transition-colors border border-white/5">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              MP3 320
            </button>
          {/if}
          {#if track.audio_mp3_128}
            <button onclick={() => downloadTrack(track.audio_mp3_128, track.title, 'mp3')}
              class="flex items-center gap-1.5 px-4 py-2 bg-dark-800 hover:bg-dark-700 rounded-lg text-xs font-medium text-dark-300 transition-colors border border-white/5">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              MP3 128
            </button>
          {/if}
        </div>
      </div>
    </div>

    <!-- Track notes / lyrics -->
    {#if track.notes || track.lyrics}
      <div class="mt-8 grid md:grid-cols-2 gap-6">
        {#if track.notes}
          <section class="bg-dark-900 rounded-xl p-6 border border-white/5">
            <h2 class="font-display text-xl tracking-wide mb-4 text-white">Notes</h2>
            <MarkdownRenderer content={track.notes} />
          </section>
        {/if}
        {#if track.lyrics}
          <section class="bg-dark-900 rounded-xl p-6 border border-white/5">
            <h2 class="font-display text-xl tracking-wide mb-4 text-white">Lyrics</h2>
            <div class="whitespace-pre-wrap font-mono text-sm text-dark-300 leading-relaxed">{track.lyrics}</div>
          </section>
        {/if}
      </div>
    {/if}

    <!-- Other tracks from album -->
    {#if release.tracks?.length > 1}
      <section class="mt-8">
        <h2 class="font-display text-xl tracking-wide mb-4 text-white">More from "{release.title}"</h2>
        <div class="bg-dark-900 rounded-xl border border-white/5 overflow-hidden divide-y divide-white/5">
          {#each release.tracks as t, i}
            <a
              href="/music/{release.slug || release._id}/track/{i}"
              class="flex items-center gap-4 px-4 py-3 hover:bg-dark-800 transition-colors
                {i === trackIndex ? 'bg-dark-800' : ''}"
            >
              <span class="w-6 text-center text-sm {i === trackIndex ? 'text-accent-green font-bold' : 'text-dark-500'}">{t.number || i + 1}</span>
              <span class="flex-1 text-sm {i === trackIndex ? 'text-accent-green font-medium' : 'text-dark-300'}">{t.title}</span>
              {#if t.audio_opus}
                <svg class="w-4 h-4 text-dark-500" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
              {/if}
              <span class="text-dark-500 font-mono text-xs">{t.duration || ''}</span>
            </a>
          {/each}
        </div>
      </section>
    {/if}

    <!-- Back to release -->
    <div class="mt-8">
      <a href="/music/{release.slug || release._id}" class="inline-flex items-center gap-2 text-sm text-dark-400 hover:text-accent-green transition-colors">
        ← Back to {release.title}
      </a>
    </div>
  {:else if !loading}
    <p class="text-dark-400">Track not found.</p>
  {/if}
</div>

<ImageLightbox bind:open={lbOpen} src={lbSrc} originalSrc={lbOriginalSrc} alt={lbAlt} />
