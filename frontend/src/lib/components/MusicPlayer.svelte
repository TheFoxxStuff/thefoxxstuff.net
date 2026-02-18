<script>
  import { player, currentTrack } from '$lib/stores/player.js';
  import { API_BASE, getImageUrl } from '$lib/api';
  import { onMount, onDestroy } from 'svelte';

  let audioEl = $state(null);
  let currentTime = $state(0);
  let duration = $state(0);
  let prevTrackKey = $state(null);
  let showVolume = $state(false);
  let isDragging = $state(false);

  let state = $derived($player);
  let track = $derived($currentTrack);
  let coverUrl = $derived(state.release?.cover_image_info ? getImageUrl(state.release.cover_image_info, 'thumb') : null);
  let audioUrl = $derived(track?.audio_opus ? `${API_BASE}/upload/file/${track.audio_opus}` : null);
  let trackKey = $derived(track ? `${state.release?._id}-${state.currentIndex}` : null);
  let progressPct = $derived(duration > 0 ? (currentTime / duration) * 100 : 0);

  function fmt(s) {
    if (!s || isNaN(s)) return '0:00';
    return `${Math.floor(s/60)}:${Math.floor(s%60).toString().padStart(2,'0')}`;
  }

  function seek(e) {
    if (!audioEl || !duration) return;
    const r = e.currentTarget.getBoundingClientRect();
    audioEl.currentTime = Math.max(0, Math.min(((e.clientX - r.left) / r.width) * duration, duration));
  }

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

  function handleKeydown(e) {
    if (!state.visible || e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.code === 'Space') { e.preventDefault(); player.togglePlay(); }
    if (e.code === 'ArrowRight') { if (audioEl) audioEl.currentTime = Math.min(duration, currentTime + 5); }
    if (e.code === 'ArrowLeft') { if (audioEl) audioEl.currentTime = Math.max(0, currentTime - 5); }
  }

  onMount(() => { window.addEventListener('keydown', handleKeydown); });
  onDestroy(() => { if (typeof window !== 'undefined') window.removeEventListener('keydown', handleKeydown); });

  let repeatIcon = $derived(state.repeat === 'none' ? 'opacity-30' : state.repeat === 'one' ? 'text-accent-green' : 'text-accent-green opacity-70');
</script>

{#if state.visible && track}
  <audio bind:this={audioEl} bind:currentTime bind:duration onended={onEnded} preload="auto"></audio>

  <div class="fixed bottom-4 left-1/2 -translate-x-1/2 z-[9999] w-[calc(100%-2rem)] max-w-[560px] animate-slide-in-bottom">
    <div class="overflow-hidden rounded-[18px] shadow-2xl" style="background: rgba(12,12,12,0.96); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.08);">

      <!-- Progress bar -->
      <div
        class="relative h-[3px] cursor-pointer group/prog"
        style="background: rgba(255,255,255,0.08);"
        onclick={seek}
        role="slider"
        tabindex="0"
        aria-label="Seek"
        aria-valuenow={currentTime}
        aria-valuemax={duration}
      >
        <div
          class="h-full transition-[width] duration-100 relative"
          style="width:{progressPct}%; background: linear-gradient(90deg, #73EE07, #47ADFF);"
        >
          <div class="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-white opacity-0 group-hover/prog:opacity-100 transition-opacity shadow-lg translate-x-1/2"></div>
        </div>
      </div>

      <div class="flex items-center gap-3 px-3 py-2.5">
        <!-- Cover -->
        <a href="/music/{state.release?.slug || state.release?._id}" class="flex-shrink-0 relative block">
          <div class="w-11 h-11 rounded-[10px] overflow-hidden bg-dark-800">
            {#if coverUrl}
              <img src={coverUrl} alt="" class="w-full h-full object-cover" />
            {:else}
              <div class="w-full h-full flex items-center justify-center" style="background: #1a1a1a;">
                <svg class="w-5 h-5 text-dark-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19V6l12-3v13" />
                </svg>
              </div>
            {/if}
          </div>
          {#if state.isPlaying}
            <div class="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full flex items-center justify-center" style="background: #73EE07;">
              <div class="w-1.5 h-1.5 rounded-full bg-black"></div>
            </div>
          {/if}
        </a>

        <!-- Track info -->
        <div class="flex-1 min-w-0">
          <p class="text-[13px] font-medium text-white truncate leading-[1.3]">{track.title}</p>
          <p class="text-[11px] truncate leading-[1.3] mt-[1px]" style="color: rgba(255,255,255,0.4);">{state.release?.title}</p>
        </div>

        <!-- Time -->
        <span class="text-[10px] font-mono hidden sm:flex items-center gap-0.5 flex-shrink-0" style="color: rgba(255,255,255,0.3);">
          <span>{fmt(currentTime)}</span>
          <span>/</span>
          <span>{fmt(duration)}</span>
        </span>

        <!-- Controls -->
        <div class="flex items-center gap-0.5 flex-shrink-0">
          <!-- Repeat -->
          <button
            onclick={() => player.toggleRepeat()}
            class="w-7 h-7 flex items-center justify-center transition-all hover:text-white {repeatIcon}"
            title="Repeat: {state.repeat}"
          >
            {#if state.repeat === 'one'}
              <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/>
                <text x="12" y="16" font-size="6" text-anchor="middle" fill="currentColor">1</text>
              </svg>
            {:else}
              <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/>
              </svg>
            {/if}
          </button>

          <!-- Prev -->
          <button
            onclick={() => player.prev()}
            class="w-8 h-8 flex items-center justify-center transition-colors hover:text-white"
            style="color: rgba(255,255,255,0.5);"
            aria-label="Previous"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/>
            </svg>
          </button>

          <!-- Play/Pause -->
          <button
            onclick={() => player.togglePlay()}
            class="w-9 h-9 flex items-center justify-center rounded-full text-black transition-all hover:scale-105 active:scale-95"
            style="background: white;"
            aria-label={state.isPlaying ? 'Pause' : 'Play'}
          >
            {#if state.isPlaying}
              <svg class="w-[15px] h-[15px]" fill="currentColor" viewBox="0 0 24 24">
                <rect x="6" y="4" width="4" height="16"/>
                <rect x="14" y="4" width="4" height="16"/>
              </svg>
            {:else}
              <svg class="w-[15px] h-[15px] ml-0.5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z"/>
              </svg>
            {/if}
          </button>

          <!-- Next -->
          <button
            onclick={() => player.next()}
            class="w-8 h-8 flex items-center justify-center transition-colors hover:text-white"
            style="color: rgba(255,255,255,0.5);"
            aria-label="Next"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
            </svg>
          </button>

          <!-- Volume -->
          <div class="relative" onmouseenter={() => showVolume = true} onmouseleave={() => showVolume = false}>
            <button class="w-7 h-7 flex items-center justify-center transition-colors hover:text-white" style="color: rgba(255,255,255,0.4);" aria-label="Volume">
              {#if state.volume === 0}
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/></svg>
              {:else if state.volume < 0.5}
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M18.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM5 9v6h4l5 5V4L9 9H5z"/></svg>
              {:else}
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
              {/if}
            </button>
            {#if showVolume}
              <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 rounded-[10px] p-2.5 shadow-2xl animate-scale-in" style="background: rgba(20,20,20,0.98); border: 1px solid rgba(255,255,255,0.1);">
                <input
                  type="range" min="0" max="1" step="0.01" value={state.volume}
                  oninput={(e) => player.setVolume(parseFloat(e.target.value))}
                  class="volume-slider w-20 cursor-pointer"
                />
              </div>
            {/if}
          </div>

          <!-- Close -->
          <button
            onclick={() => { if(audioEl){audioEl.pause();audioEl.src='';} player.close(); }}
            class="w-7 h-7 flex items-center justify-center transition-colors ml-0.5 hover:text-white rounded-[6px] hover:bg-white/8"
            style="color: rgba(255,255,255,0.3);"
            aria-label="Close"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  .volume-slider {
    -webkit-appearance: none;
    appearance: none;
    height: 3px;
    border-radius: 99px;
    background: rgba(255,255,255,0.15);
    outline: none;
    display: block;
  }
  .volume-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: white;
    cursor: pointer;
  }
</style>
