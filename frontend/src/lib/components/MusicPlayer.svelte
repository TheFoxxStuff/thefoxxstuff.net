<script>
  import { player, currentTrack } from '$lib/stores/player.js';
  import { API_BASE, getImageUrl } from '$lib/api';
  import { onMount, onDestroy } from 'svelte';

  let audioEl = $state(null);
  let preloadEl = $state(null);
  let currentTime = $state(0);
  let duration = $state(0);
  let prevTrackKey = $state(null);
  let showVolume = $state(false);
  let hovering = $state(false);

  // Dragging
  let pos = $state({ x: null, y: null }); // null = centered default
  let dragging = $state(false);
  let dragOffset = $state({ x: 0, y: 0 });

  let state = $derived($player);
  let track = $derived($currentTrack);
  let coverUrl = $derived(state.release?.cover_image_info ? getImageUrl(state.release.cover_image_info, 'thumb') : null);
  let audioUrl = $derived(track?.audio_opus ? `${API_BASE}/upload/file/${track.audio_opus}` : null);
  let trackKey = $derived(track ? `${state.release?._id}-${state.currentIndex}` : null);
  let progressPct = $derived(duration > 0 ? (currentTime / duration) * 100 : 0);

  let nextAudioUrl = $derived.by(() => {
    const tracks = state.tracks;
    if (!tracks?.length) return null;
    let nextIdx = state.currentIndex + 1;
    while (nextIdx < tracks.length && !tracks[nextIdx]?.audio_opus) nextIdx++;
    if (nextIdx >= tracks.length) return null;
    return `${API_BASE}/upload/file/${tracks[nextIdx].audio_opus}`;
  });

  function fmt(s) {
    if (!s || isNaN(s)) return '0:00';
    return `${Math.floor(s / 60)}:${Math.floor(s % 60).toString().padStart(2, '0')}`;
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
      if (preloadEl && preloadEl.src === audioUrl && preloadEl.readyState >= 2) {
        audioEl.src = audioUrl;
        audioEl.currentTime = 0;
      } else {
        audioEl.src = audioUrl;
        audioEl.load();
      }
      if (state.isPlaying) audioEl.play().catch(() => {});
    }
  });

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

  // Drag logic
  function onDragStart(e) {
    dragging = true;
    const el = e.currentTarget.closest('[data-player]');
    const rect = el.getBoundingClientRect();
    dragOffset = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    e.preventDefault();
  }

  function onMouseMove(e) {
    if (!dragging) return;
    pos = {
      x: e.clientX - dragOffset.x,
      y: e.clientY - dragOffset.y
    };
  }

  function onMouseUp() {
    dragging = false;
  }

  let repeatIcon = $derived(
    state.repeat === 'none' ? 'text-white/30' :
    state.repeat === 'one' ? 'text-[#007BFF]' : 'text-[#007BFF] opacity-80'
  );

  let playerStyle = $derived(
    pos.x !== null
      ? `left: ${pos.x}px; top: ${pos.y}px; transform: none; bottom: auto;`
      : `left: 50%; bottom: 1rem; transform: translateX(-50%);`
  );

  onMount(() => {
    window.addEventListener('keydown', handleKeydown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  });

  onDestroy(() => {
    if (typeof window !== 'undefined') {
      window.removeEventListener('keydown', handleKeydown);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    }
  });
</script>

{#if state.visible && track}
  <audio bind:this={audioEl} bind:currentTime bind:duration onended={onEnded} preload="auto"></audio>
  <audio bind:this={preloadEl} preload="auto" style="display:none" aria-hidden="true"></audio>

  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div
    data-player
    class="fixed z-[9999] w-[776px]"
    style={playerStyle}
  >
    <div class="h-[76px] flex items-center gap-4 p-[6px] rounded-lg border border-white/5 bg-black/90 backdrop-blur-[32px] shadow-[0_4px_18px_rgba(0,0,0,0.32)]">

      <!-- Left column: drag handle + close -->
      <div class="flex flex-col justify-between h-full py-1 min-w-[30px]">
        <!-- Drag Handle -->
        <div
          class="w-[30px] h-[30px] flex items-center justify-center cursor-grab active:cursor-grabbing group"
          onmousedown={onDragStart}
          title="Перетащить"
        >
          <svg class="w-5 h-5 text-white/30 group-hover:text-white/60 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 9h14M5 15h14"/>
          </svg>
        </div>

        <!-- Close -->
        <button
          class="w-[30px] h-[30px] flex items-center justify-center cursor-pointer group"
          onclick={() => { if (audioEl) { audioEl.pause(); audioEl.src = ''; } player.close(); pos = { x: null, y: null }; }}
          aria-label="Close"
        >
          <svg class="w-5 h-5 text-white/30 group-hover:text-[#A61530] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- Main player block -->
      <div class="flex-1 h-[64px] flex flex-col gap-1">

        <!-- Progress bar -->
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div
          class="relative w-full h-4 flex items-center cursor-pointer group/prog"
          onclick={seek}
          onkeydown={(e) => e.key === 'Enter' && seek(e)}
          role="slider"
          tabindex="0"
          aria-label="Seek"
          aria-valuenow={currentTime}
          aria-valuemax={duration}
        >
          <!-- Track bg -->
          <div class="absolute w-full h-1 bg-white/5 rounded-full"></div>
          <!-- Filled -->
          <div
            class="absolute h-1 bg-gradient-to-r from-[#007BFF] to-[#0056b3] rounded-full pointer-events-none"
            style="width: {progressPct}%"
          ></div>
          <!-- Thumb — appears on hover -->
          <div
            class="absolute w-3 h-3 bg-white rounded-full shadow-[-3px_0_12px_rgba(0,0,0,1)] pointer-events-none
                   opacity-0 group-hover/prog:opacity-100 transition-opacity duration-150"
            style="left: {progressPct}%; transform: translateX(-50%);"
          ></div>
          <!-- Invisible wide input for seeking -->
          <input
            type="range" min="0" max={duration || 100}
            value={currentTime}
            oninput={(e) => { if (audioEl) audioEl.currentTime = parseFloat(e.target.value); }}
            class="absolute w-full h-4 opacity-0 cursor-pointer z-10"
          />
        </div>

        <!-- Bottom panel -->
        <div class="w-full h-[56px] bg-white/5 rounded flex items-center justify-between px-3 shadow-[-1px_0_12px_rgba(0,0,0,1)]">

          <!-- Track info -->
          <a
            href="/music/{state.release?.slug || state.release?._id}"
            class="flex items-center gap-2 min-w-[180px] group/info"
          >
            {#if coverUrl}
              <img src={coverUrl} alt="" class="w-12 h-12 rounded-[2px] object-cover flex-shrink-0" />
            {:else}
              <div class="w-12 h-12 rounded-[2px] bg-white/5 flex items-center justify-center flex-shrink-0">
                <svg class="w-5 h-5 text-white/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19V6l12-3v13"/>
                </svg>
              </div>
            {/if}
            <div class="flex flex-col justify-center min-w-0">
              <span class="text-[14px] font-bold text-white leading-tight truncate group-hover/info:text-[#007BFF] transition-colors">{track.title}</span>
              <span class="text-[10px] text-white/60 leading-tight truncate">{state.release?.title}</span>
            </div>
          </a>

          <!-- Playback controls -->
          <div class="flex items-center gap-1">
            <!-- Repeat -->
            <button
              onclick={() => player.toggleRepeat()}
              class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/5 transition-all {repeatIcon}"
              title="Повтор: {state.repeat}"
            >
              {#if state.repeat === 'one'}
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/>
                  <text x="12" y="15" font-size="6" text-anchor="middle" fill="currentColor">1</text>
                </svg>
              {:else}
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/>
                </svg>
              {/if}
            </button>

            <!-- Prev -->
            <button
              onclick={() => player.prev()}
              class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/5 transition-all group"
              aria-label="Предыдущий"
            >
              <svg class="w-5 h-5 fill-white/60 text-white/60 group-hover:fill-white group-hover:text-white" viewBox="0 0 24 24">
                <path d="M6 6h2v12H6zm3.5 6 8.5 6V6z"/>
              </svg>
            </button>

            <!-- Play/Pause -->
            <button
              onclick={() => player.togglePlay()}
              class="w-10 h-10 flex items-center justify-center rounded-full bg-white/10 hover:bg-white/20 transition-all"
              aria-label={state.isPlaying ? 'Пауза' : 'Воспроизвести'}
            >
              {#if state.isPlaying}
                <svg class="w-5 h-5 fill-white" viewBox="0 0 24 24">
                  <rect x="6" y="4" width="4" height="16"/>
                  <rect x="14" y="4" width="4" height="16"/>
                </svg>
              {:else}
                <svg class="w-5 h-5 fill-white ml-0.5" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z"/>
                </svg>
              {/if}
            </button>

            <!-- Next -->
            <button
              onclick={() => player.next()}
              class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/5 transition-all group"
              aria-label="Следующий"
            >
              <svg class="w-5 h-5 fill-white/60 text-white/60 group-hover:fill-white group-hover:text-white" viewBox="0 0 24 24">
                <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
              </svg>
            </button>
          </div>

          <!-- Time + Volume -->
          <div class="flex items-center gap-[6px] min-w-[180px] justify-end">
            <span class="text-[12px] text-white/60 font-mono">{fmt(currentTime)}</span>
            <div class="h-3 w-[1px] bg-white/10 mx-1"></div>
            <span class="text-[12px] text-white/60 font-mono">{fmt(duration)}</span>

            <!-- Volume -->
            <!-- svelte-ignore a11y_no_static_element_interactions -->
            <div
              class="relative flex flex-col items-center"
              onmouseenter={() => showVolume = true}
              onmouseleave={() => showVolume = false}
            >
              <!-- Volume panel -->
              {#if showVolume}
                <div
                  class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 flex flex-col items-center
                         bg-black/90 backdrop-blur-[32px] p-2 pt-2 rounded-lg shadow-[0_4px_4px_rgba(0,0,0,0.25)]
                         border border-white/5 z-50 w-10
                         animate-in fade-in zoom-in-75 duration-150 origin-bottom"
                >
                  <span class="text-[11px] text-white/60 font-medium mb-1">{Math.round(state.volume * 100)}</span>
                  <!-- Vertical slider -->
                  <div class="relative w-1 h-[100px] mb-2 flex flex-col-reverse items-center">
                    <div class="absolute w-full h-full bg-white/5 rounded-full"></div>
                    <div
                      class="absolute w-full bg-white rounded-full"
                      style="height: {state.volume * 100}%; bottom: 0;"
                    ></div>
                    <div
                      class="absolute w-3 h-3 bg-white rounded-full shadow-[-3px_0_12px_rgba(0,0,0,1)] z-10"
                      style="bottom: calc({state.volume * 100}% - 6px); left: 50%; transform: translateX(-50%);"
                    ></div>
                    <input
                      type="range" min="0" max="1" step="0.01"
                      value={state.volume}
                      oninput={(e) => player.setVolume(parseFloat(e.target.value))}
                      class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20"
                      style="writing-mode: vertical-lr; direction: rtl; appearance: slider-vertical;"
                    />
                  </div>
                </div>
              {/if}

              <!-- Volume icon -->
              <button class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/5 transition-all group" aria-label="Громкость">
                {#if state.volume === 0}
                  <svg class="w-5 h-5 text-white/60 group-hover:text-white transition-colors" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3 3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4 9.91 6.09 12 8.18V4z"/>
                  </svg>
                {:else if state.volume < 0.5}
                  <svg class="w-5 h-5 text-white/60 group-hover:text-white transition-colors" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M18.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM5 9v6h4l5 5V4L9 9H5z"/>
                  </svg>
                {:else}
                  <svg class="w-5 h-5 text-white/60 group-hover:text-white transition-colors" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                  </svg>
                {/if}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}