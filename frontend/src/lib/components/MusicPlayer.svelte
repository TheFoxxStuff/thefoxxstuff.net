<script>
  import { player, currentTrack } from '$lib/stores/player.js';
  import { API_BASE, getImageUrl } from '$lib/api';
  import { onMount, onDestroy } from 'svelte';
  import { fly } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';

  let audioEl = $state(null);
  let currentTime = $state(0);
  let duration = $state(0);
  let prevTrackKey = $state(null);
  let showVolume = $state(false);
  let touchStartX = $state(null);
  let isSeeking = $state(false);

  let state = $derived($player);
  let track = $derived($currentTrack);
  let coverUrl = $derived(state.release?.cover_image_info ? getImageUrl(state.release.cover_image_info, 'thumb') : null);
  let audioUrl = $derived(track?.audio_opus ? `${API_BASE}/upload/file/${track.audio_opus}` : null);
  let trackKey = $derived(track ? `${state.release?._id}-${state.currentIndex}` : null);
  let progressPct = $derived(duration > 0 ? (currentTime / duration) * 100 : 0);

  // Share with timestamp
  let shareUrl = $derived(() => {
    if (!state.release) return '';
    const base = `/music/${state.release.slug || state.release._id}`;
    return `${window?.location?.origin || ''}${base}?t=${Math.floor(currentTime)}`;
  });

  function fmt(s) {
    if (!s || isNaN(s)) return '0:00';
    return `${Math.floor(s / 60)}:${Math.floor(s % 60).toString().padStart(2, '0')}`;
  }

  function seek(e) {
    if (!audioEl || !duration) return;
    const r = e.currentTarget.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    audioEl.currentTime = Math.max(0, Math.min(((clientX - r.left) / r.width) * duration, duration));
  }

  function copyShareLink() {
    const url = shareUrl();
    if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(() => {
        showCopied = true;
        setTimeout(() => showCopied = false, 2000);
      });
    }
  }
  let showCopied = $state(false);

  function onEnded() {
    if (state.repeat === 'one') {
      if (audioEl) { audioEl.currentTime = 0; audioEl.play().catch(() => {}); }
    } else {
      player.next();
    }
  }

  $effect(() => {
    if (!audioEl || !audioUrl) return;
    if (trackKey !== prevTrackKey) {
      prevTrackKey = trackKey;
      audioEl.src = audioUrl;
      audioEl.load();
      if (state.isPlaying) audioEl.play().catch(() => {});
    }
  });

  $effect(() => {
    if (!audioEl || !audioUrl) return;
    if (state.isPlaying) audioEl.play().catch(() => {});
    else audioEl.pause();
  });

  $effect(() => { if (audioEl) audioEl.volume = state.volume; });

  // Keyboard shortcuts
  function handleKeydown(e) {
    if (!state.visible || e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.code === 'Space') { e.preventDefault(); player.togglePlay(); }
    if (e.code === 'ArrowRight') { e.preventDefault(); if (audioEl) audioEl.currentTime = Math.min(duration, currentTime + 5); }
    if (e.code === 'ArrowLeft') { e.preventDefault(); if (audioEl) audioEl.currentTime = Math.max(0, currentTime - 5); }
    if (e.code === 'ArrowUp') { e.preventDefault(); player.setVolume(state.volume + 0.05); }
    if (e.code === 'ArrowDown') { e.preventDefault(); player.setVolume(state.volume - 0.05); }
  }

  // Touch swipe for next/prev
  function handleTouchStart(e) { touchStartX = e.touches[0].clientX; }
  function handleTouchEnd(e) {
    if (touchStartX === null) return;
    const dx = e.changedTouches[0].clientX - touchStartX;
    if (Math.abs(dx) > 60) {
      if (dx < 0) player.next(); else player.prev();
    }
    touchStartX = null;
  }

  onMount(() => { window.addEventListener('keydown', handleKeydown); });
  onDestroy(() => { if (typeof window !== 'undefined') window.removeEventListener('keydown', handleKeydown); });

  let repeatIcon = $derived(state.repeat === 'none' ? 'opacity-30' : state.repeat === 'one' ? 'text-accent-green' : 'text-accent-green opacity-80');
</script>

{#if state.visible && track}
  <audio bind:this={audioEl} bind:currentTime bind:duration onended={onEnded} preload="auto"></audio>

  <div
    class="fixed bottom-4 left-1/2 -translate-x-1/2 z-[9999] w-[calc(100%-2rem)] max-w-[560px]"
    transition:fly={{ y: 100, duration: 320, easing: cubicOut }}
    ontouchstart={handleTouchStart}
    ontouchend={handleTouchEnd}
  >
    <div class="bg-dark-900/95 backdrop-blur-xl border border-dark-700/50 rounded-2xl shadow-2xl shadow-black/50 overflow-hidden">

      <!-- Progress bar — taller for easier touch -->
      <div
        class="h-2 bg-dark-800 cursor-pointer group/prog relative touch-none"
        onclick={seek}
        ontouchstart={(e) => { isSeeking = true; seek(e); }}
        ontouchmove={(e) => { if (isSeeking) seek(e); }}
        ontouchend={() => isSeeking = false}
        role="slider"
        tabindex="0"
        aria-label="Seek"
        aria-valuenow={currentTime}
        aria-valuemax={duration}
        onkeydown={(e) => {
          if (e.key === 'ArrowRight' && audioEl) audioEl.currentTime = Math.min(duration, currentTime + 5);
          if (e.key === 'ArrowLeft' && audioEl) audioEl.currentTime = Math.max(0, currentTime - 5);
        }}
      >
        <!-- Track fill -->
        <div class="h-full bg-accent-green transition-[width] duration-100 rounded-r-full" style="width:{progressPct}%"></div>
        <!-- Thumb dot -->
        <div
          class="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-white shadow-lg opacity-0 group-hover/prog:opacity-100 transition-opacity"
          style="left:{progressPct}%"
        ></div>
      </div>

      <div class="flex items-center gap-3 px-3 py-2.5">
        <!-- Cover -->
        <a href="/music/{state.release?.slug || state.release?._id}" class="w-10 h-10 rounded-lg overflow-hidden flex-shrink-0 bg-dark-800 block">
          {#if coverUrl}
            <img src={coverUrl} alt="" class="w-full h-full object-cover" />
          {:else}
            <div class="w-full h-full flex items-center justify-center text-dark-600">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19V6l12-3v13" /></svg>
            </div>
          {/if}
        </a>

        <!-- Info + equalizer -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <p class="text-sm text-white truncate leading-tight">{track.title}</p>
            {#if state.isPlaying}
              <div class="equalizer flex-shrink-0">
                <span class="bar"></span>
                <span class="bar"></span>
                <span class="bar"></span>
              </div>
            {/if}
          </div>
          <p class="text-xs text-dark-400 truncate leading-tight">{state.release?.title}</p>
        </div>

        <!-- Controls -->
        <div class="flex items-center gap-0.5 flex-shrink-0">
          <!-- Repeat -->
          <button onclick={() => player.toggleRepeat()} class="w-7 h-7 flex items-center justify-center transition-colors {repeatIcon}" title="Repeat: {state.repeat}">
            {#if state.repeat === 'one'}
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/>
                <text x="12" y="15.5" font-size="6.5" text-anchor="middle" fill="currentColor" font-weight="bold">1</text>
              </svg>
            {:else}
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/></svg>
            {/if}
          </button>

          <button onclick={() => player.prev()} class="w-8 h-8 flex items-center justify-center text-dark-400 hover:text-white transition-colors" aria-label="Previous">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/></svg>
          </button>

          <button onclick={() => player.togglePlay()} class="w-9 h-9 flex items-center justify-center bg-white rounded-full text-dark-950 hover:bg-dark-200 transition-all hover:scale-105 active:scale-95" aria-label={state.isPlaying ? 'Pause' : 'Play'}>
            {#if state.isPlaying}
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
            {:else}
              <svg class="w-4 h-4 ml-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
            {/if}
          </button>

          <button onclick={() => player.next()} class="w-8 h-8 flex items-center justify-center text-dark-400 hover:text-white transition-colors" aria-label="Next">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
          </button>

          <!-- Volume — tap toggle on mobile -->
          <div class="relative">
            <button
              onclick={() => showVolume = !showVolume}
              class="w-7 h-7 flex items-center justify-center text-dark-400 hover:text-white transition-colors"
              aria-label="Volume"
            >
              {#if state.volume === 0}
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/></svg>
              {:else if state.volume < 0.5}
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M18.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM5 9v6h4l5 5V4L9 9H5z"/></svg>
              {:else}
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
              {/if}
            </button>

            {#if showVolume}
              <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 bg-dark-800 border border-dark-700 rounded-xl p-3 shadow-xl z-10">
                <input
                  type="range" min="0" max="1" step="0.02"
                  value={state.volume}
                  oninput={(e) => player.setVolume(parseFloat(e.target.value))}
                  class="w-24 h-1.5 accent-green-400 cursor-pointer"
                />
                <p class="text-center text-[10px] text-dark-400 mt-1">{Math.round(state.volume * 100)}%</p>
              </div>
            {/if}
          </div>

          <!-- Share with timestamp -->
          <button
            onclick={copyShareLink}
            class="w-7 h-7 flex items-center justify-center transition-colors {showCopied ? 'text-accent-green' : 'text-dark-500 hover:text-white'}"
            title="Copy link at {fmt(currentTime)}"
            aria-label="Share at current time"
          >
            {#if showCopied}
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
            {:else}
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/></svg>
            {/if}
          </button>

          <!-- Time -->
          <span class="text-[10px] text-dark-500 font-mono w-16 text-center hidden sm:inline tabular-nums">{fmt(currentTime)} / {fmt(duration)}</span>

          <!-- Close -->
          <button
            onclick={() => { if(audioEl){audioEl.pause();audioEl.src='';} player.close(); }}
            class="w-7 h-7 flex items-center justify-center text-dark-500 hover:text-white transition-colors ml-0.5"
            aria-label="Close player"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}
