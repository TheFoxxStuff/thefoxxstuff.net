<script>
  import { player, currentTrack } from '$lib/stores/player.js';
  import { API_BASE, getImageUrl } from '$lib/api';
  import { onMount, onDestroy } from 'svelte';

  let audioEl = $state(null);
  let preloadEl = $state(null); // скрытый элемент для предзагрузки следующего трека
  let currentTime = $state(0);
  let duration = $state(0);
  let prevTrackKey = $state(null);
  let showVolume = $state(false);

  let state = $derived($player);
  let track = $derived($currentTrack);
  let coverUrl = $derived(state.release?.cover_image_info ? getImageUrl(state.release.cover_image_info, 'thumb') : null);
  let audioUrl = $derived(track?.audio_opus ? `${API_BASE}/upload/file/${track.audio_opus}` : null);
  let trackKey = $derived(track ? `${state.release?._id}-${state.currentIndex}` : null);
  let progressPct = $derived(duration > 0 ? (currentTime / duration) * 100 : 0);

  // URL следующего трека для предзагрузки
  let nextAudioUrl = $derived.by(() => {
    const tracks = state.tracks;
    if (!tracks?.length) return null;
    let nextIdx = state.currentIndex + 1;
    // Ищем следующий трек с opus
    while (nextIdx < tracks.length && !tracks[nextIdx]?.audio_opus) nextIdx++;
    if (nextIdx >= tracks.length) return null;
    return `${API_BASE}/upload/file/${tracks[nextIdx].audio_opus}`;
  });

  function fmt(s) { if (!s || isNaN(s)) return '0:00'; return `${Math.floor(s/60)}:${Math.floor(s%60).toString().padStart(2,'0')}`; }
  function seek(e) { if (!audioEl || !duration) return; const r = e.currentTarget.getBoundingClientRect(); audioEl.currentTime = Math.max(0, Math.min(((e.clientX - r.left) / r.width) * duration, duration)); }

  function onEnded() {
    if (state.repeat === 'one') {
      if (audioEl) { audioEl.currentTime = 0; audioEl.play().catch(() => {}); }
    } else {
      player.next();
    }
  }

  // Смена трека — если следующий трек уже preload-ован, свопаем элементы
  $effect(() => {
    if (!audioEl || !audioUrl) return;
    if (trackKey !== prevTrackKey) {
      prevTrackKey = trackKey;

      // Проверяем: preloadEl уже загрузил этот URL?
      if (preloadEl && preloadEl.src === audioUrl && preloadEl.readyState >= 2) {
        // Своп: берём уже буферизованный источник
        audioEl.src = audioUrl;
        audioEl.currentTime = 0;
      } else {
        audioEl.src = audioUrl;
        audioEl.load();
      }

      if (state.isPlaying) audioEl.play().catch(() => {});
    }
  });

  // Предзагружаем следующий трек когда текущий начал играть
  $effect(() => {
    if (!preloadEl || !nextAudioUrl) return;
    if (preloadEl.src !== nextAudioUrl) {
      preloadEl.src = nextAudioUrl;
      preloadEl.load();
    }
  });

  $effect(() => { if (!audioEl || !audioUrl) return; if (state.isPlaying) audioEl.play().catch(() => {}); else audioEl.pause(); });
  $effect(() => { if (audioEl) audioEl.volume = state.volume; });

  function handleKeydown(e) {
    if (!state.visible || e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.code === 'Space') { e.preventDefault(); player.togglePlay(); }
  }
  onMount(() => { window.addEventListener('keydown', handleKeydown); });
  onDestroy(() => { if (typeof window !== 'undefined') window.removeEventListener('keydown', handleKeydown); });

  let repeatIcon = $derived(state.repeat === 'none' ? 'opacity-40' : state.repeat === 'one' ? 'text-accent-green' : 'text-accent-green opacity-80');
</script>

{#if state.visible && track}
  <audio bind:this={audioEl} bind:currentTime bind:duration onended={onEnded} preload="auto"></audio>
  <!-- Скрытый элемент для предзагрузки следующего трека -->
  <audio bind:this={preloadEl} preload="auto" style="display:none" aria-hidden="true"></audio>

  <div class="fixed bottom-4 left-1/2 -translate-x-1/2 z-[9999] w-[calc(100%-2rem)] max-w-[540px]">
    <div class="backdrop-blur-xl border border-[--w12] bg-[var(--bg)] rounded-2xl shadow-2xl shadow-black/40 overflow-hidden">
      <!-- Progress -->
      <div class="h-1 bg-[--w12] cursor-pointer group/prog relative" onclick={seek} onkeydown={(e) => e.key === "Enter" && seek(e)} role="slider" tabindex="0" aria-label="Seek" aria-valuenow={currentTime} aria-valuemax={duration}>
        <div class="h-full bg-accent-green transition-[width] duration-100" style="width:{progressPct}%"></div>
      </div>

      <div class="flex items-center gap-3 px-3 py-2.5">
        <!-- Cover -->
        <a href="/music/{state.release?.slug || state.release?._id}" class="w-10 h-10 rounded-lg overflow-hidden flex-shrink-0 bg-[--w8] block">
          {#if coverUrl}<img src={coverUrl} alt="" class="w-full h-full object-cover" />
          {:else}<div class="w-full h-full flex items-center justify-center text-dark-600"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19V6l12-3v13" /></svg></div>{/if}
        </a>

        <!-- Info -->
        <div class="flex-1 min-w-0">
          <p class="text-sm text-white truncate leading-tight">{track.title}</p>
          <p class="text-xs text-dark-400 truncate leading-tight">{state.release?.title}</p>
        </div>

        <!-- Controls -->
        <div class="flex items-center gap-1 flex-shrink-0">
          <!-- Repeat -->
          <button onclick={() => player.toggleRepeat()} class="w-7 h-7 flex items-center justify-center transition-colors {repeatIcon}" title="Repeat: {state.repeat}">
            {#if state.repeat === 'one'}
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/><text x="12" y="15" font-size="7" text-anchor="middle" fill="currentColor">1</text></svg>
            {:else}
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/></svg>
            {/if}
          </button>

          <button onclick={() => player.prev()} class="w-8 h-8 flex items-center justify-center text-dark-400 hover:text-white transition-colors" aria-label="Previous">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/></svg>
          </button>
          <button onclick={() => player.togglePlay()} class="w-9 h-9 flex items-center justify-center bg-white rounded-full text-dark-950 hover:bg-dark-300 transition-colors" aria-label={state.isPlaying ? 'Pause' : 'Play'}>
            {#if state.isPlaying}<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
            {:else}<svg class="w-4 h-4 ml-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>{/if}
          </button>
          <button onclick={() => player.next()} class="w-8 h-8 flex items-center justify-center text-dark-400 hover:text-white transition-colors" aria-label="Next">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
          </button>

          <!-- Volume -->
          <div class="relative" role="group" onmouseenter={() => showVolume = true} onmouseleave={() => showVolume = false}>
            <button class="w-7 h-7 flex items-center justify-center text-dark-400 hover:text-white transition-colors" aria-label="Volume">
              {#if state.volume === 0}
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/></svg>
              {:else if state.volume < 0.5}
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M18.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM5 9v6h4l5 5V4L9 9H5z"/></svg>
              {:else}
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
              {/if}
            </button>
            {#if showVolume}
              <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 bg-[--select] border border-[--w12] rounded-lg p-2 shadow-xl">
                <input type="range" min="0" max="1" step="0.01" value={state.volume} oninput={(e) => player.setVolume(parseFloat(e.target.value))}
                  class="w-20 h-1 accent-green-400 cursor-pointer" style="writing-mode: horizontal-tb;" />
              </div>
            {/if}
          </div>

          <span class="text-[10px] text-dark-500 font-mono w-[72px] text-center hidden sm:inline">{fmt(currentTime)} / {fmt(duration)}</span>

          <button onclick={() => { if(audioEl){audioEl.pause();audioEl.src='';} player.close(); }} class="w-7 h-7 flex items-center justify-center text-dark-500 hover:text-white transition-colors ml-1" aria-label="Close">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}
