<script>
  import { player, currentTrack } from '$lib/stores/player.js';
  import { API_BASE, getImageUrl } from '$lib/api';
  import { onMount, onDestroy } from 'svelte';
  import { fly, fade } from 'svelte/transition';

  let audioEl = $state(null);
  let preloadEl = $state(null);
  let currentTime = $state(0);
  let duration = $state(0);
  let prevTrackKey = $state(null);
  let showVolume = $state(false);
  let previousVolume = $state(1);
  let rippleActive = $state(false);

  // Progress hover
  let hoverPct = $state(0);       // 0-100, позиция курсора на полоске
  let hoverTime = $state(0);      // время в секундах в точке курсора
  let progressHovering = $state(false);
  let titleSelected = $state(false);

  // Dragging
  let pos = $state({ x: null, y: null });
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

  function onProgressMouseMove(e) {
    const r = e.currentTarget.getBoundingClientRect();
    const pct = Math.max(0, Math.min((e.clientX - r.left) / r.width, 1));
    hoverPct = pct * 100;
    hoverTime = pct * (duration || 0);
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
    if (preloadEl.src !== nextAudioUrl) { preloadEl.src = nextAudioUrl; preloadEl.load(); }
  });

  $effect(() => { if (!audioEl || !audioUrl) return; if (state.isPlaying) audioEl.play().catch(() => {}); else audioEl.pause(); });
  $effect(() => { if (audioEl) audioEl.volume = state.volume; });

  function handleKeydown(e) {
    if (!state.visible || e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.code === 'Space') { e.preventDefault(); triggerRipple(); player.togglePlay(); }
    // Volume control with arrow keys
    if (e.code === 'ArrowUp') { e.preventDefault(); player.setVolume(Math.min(1, state.volume + 0.05)); }
    if (e.code === 'ArrowDown') { e.preventDefault(); player.setVolume(Math.max(0, state.volume - 0.05)); }
    // Mute toggle
    if (e.code === 'KeyM') { e.preventDefault(); toggleMute(); }
  }

  function onDragStart(e) {
    const el = e.currentTarget.closest('[data-player]');
    const rect = el.getBoundingClientRect();

    // Устанавливаем dragging и позицию одновременно
    dragging = true;

    // Если позиция еще не установлена, зафиксируем текущую позицию
    if (pos.x === null) {
      pos = { x: rect.left, y: rect.top };
    }

    dragOffset = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    e.preventDefault();
  }

  function onMouseMove(e) {
    if (!dragging) return;
    pos = { x: e.clientX - dragOffset.x, y: e.clientY - dragOffset.y };
  }

  function onMouseUp() { dragging = false; }

  function toggleMute() {
    if (state.volume === 0) {
      player.setVolume(previousVolume || 0.5);
    } else {
      previousVolume = state.volume;
      player.setVolume(0);
    }
  }

  function handleVolumeWheel(e) {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.05 : 0.05;
    player.setVolume(Math.max(0, Math.min(1, state.volume + delta)));
  }

  function triggerRipple() {
    rippleActive = true;
    setTimeout(() => rippleActive = false, 600);
  }

  function handlePlayPause() {
    triggerRipple();
    player.togglePlay();
  }

  function handleSelectionChange() {
    const selection = window.getSelection();
    titleSelected = selection && selection.toString().length > 0;
  }

  // Load volume from localStorage on mount
  onMount(() => {
    const savedVolume = localStorage.getItem('musicPlayerVolume');
    if (savedVolume !== null) {
      const vol = parseFloat(savedVolume);
      if (!isNaN(vol) && vol >= 0 && vol <= 1) {
        player.setVolume(vol);
      }
    }
  });

  // Save volume to localStorage when it changes
  $effect(() => {
    if (state.volume !== undefined) {
      localStorage.setItem('musicPlayerVolume', state.volume.toString());
    }
  });

  let repeatIcon = $derived(
    state.repeat === 'none' ? 'text-white/30' :
    state.repeat === 'one' ? 'text-[#1e6fff]' : 'text-[#1e6fff] opacity-80'
  );

  let playerStyle = $derived(
    pos.x !== null
      ? `left:0;top:0;transform:translate(${pos.x}px,${pos.y}px) scale(${dragging ? 1.05 : 1});transition:scale 0.15s;`
      : `left:50%;bottom:1.5rem;transform:translateX(-50%) scale(${dragging ? 1.05 : 1});transition:scale 0.15s;`
  );

  let playerClasses = $derived(
    pos.x !== null
      ? 'fixed z-[9999] w-[776px] will-change-transform'
      : 'fixed z-[9999] w-[776px]'
  );

  onMount(() => {
    window.addEventListener('keydown', handleKeydown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    document.addEventListener('selectionchange', handleSelectionChange);
  });
  onDestroy(() => {
    if (typeof window !== 'undefined') {
      window.removeEventListener('keydown', handleKeydown);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      document.removeEventListener('selectionchange', handleSelectionChange);
    }
  });
</script>

{#if state.visible && track}
  <audio bind:this={audioEl} bind:currentTime bind:duration onended={onEnded} preload="auto"></audio>
  <audio bind:this={preloadEl} preload="auto" style="display:none" aria-hidden="true"></audio>

  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div
    data-player
    class="{playerClasses} select-none"
    style={playerStyle}
  >
    <div class="h-[76px] flex items-center gap-3 px-[6px] py-[6px] rounded-[10px] border border-white/[0.06] bg-[rgba(10,10,10,0.92)] backdrop-blur-[32px] shadow-[0_4px_24px_rgba(0,0,0,0.5)]">

      <!-- Drag + Close -->
      <div class="flex flex-col justify-between h-full py-[3px] min-w-[30px] items-center">
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div
          class="w-[30px] h-[30px] flex items-center justify-center cursor-grab active:cursor-grabbing text-white/20 hover:text-white/50 transition-colors"
          onmousedown={onDragStart}
          title="Перетащить"
        >
          <!-- Dots grid drag icon -->
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <circle cx="5" cy="4" r="1.3"/><circle cx="11" cy="4" r="1.3"/>
            <circle cx="5" cy="8" r="1.3"/><circle cx="11" cy="8" r="1.3"/>
            <circle cx="5" cy="12" r="1.3"/><circle cx="11" cy="12" r="1.3"/>
          </svg>
        </div>
        <button
          class="w-[30px] h-[30px] flex items-center justify-center text-white/20 hover:text-[#c0253a] transition-colors"
          onclick={() => { if (audioEl) { audioEl.pause(); audioEl.src = ''; } player.close(); pos = { x: null, y: null }; }}
          aria-label="Закрыть"
        >
          <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24">
            <path d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- Main -->
      <div class="flex-1 h-[64px] flex flex-col gap-1">

        <!-- Progress bar -->
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div
          class="relative w-full h-5 flex items-center cursor-pointer group/prog"
          onclick={seek}
          onmousemove={onProgressMouseMove}
          onmouseenter={() => progressHovering = true}
          onmouseleave={() => progressHovering = false}
          onkeydown={(e) => e.key === 'Enter' && seek(e)}
          role="slider"
          tabindex="0"
          aria-label="Seek"
          aria-valuenow={currentTime}
          aria-valuemax={duration}
        >
          <!-- Track -->
          <div class="absolute w-full h-[3px] group-hover/prog:h-[5px] bg-white/[0.07] rounded-full transition-all duration-150 overflow-hidden">
            <div
              class="h-full rounded-full bg-gradient-to-r from-[#1e6fff] to-[#0056d6]"
              style="width:{progressPct}%"
            ></div>
          </div>

          <!-- Thumb — visible on hover -->
          <div
            class="absolute w-[13px] h-[13px] bg-white rounded-full shadow-[0_0_8px_rgba(0,0,0,0.8)]
                   pointer-events-none opacity-0 group-hover/prog:opacity-100 transition-opacity duration-150"
            style="left:{progressPct}%;transform:translateX(-50%);"
          ></div>

          <!-- Time tooltip (follows cursor) -->
          <div
            class="absolute bottom-[calc(100%+8px)] pointer-events-none
                   bg-[rgba(15,15,15,0.95)] border border-white/10 text-white text-[11px] font-semibold
                   px-2 py-[3px] rounded-md shadow-[0_4px_12px_rgba(0,0,0,0.6)]
                   opacity-0 group-hover/prog:opacity-100 transition-opacity duration-150
                   tracking-wide font-mono -translate-x-1/2 whitespace-nowrap"
            style="left:{hoverPct}%"
          >
            {fmt(hoverTime)}
          </div>

          <!-- End time tooltip (fixed right) -->
          <div
            class="absolute right-0 bottom-[calc(100%+8px)] pointer-events-none
                   bg-[rgba(15,15,15,0.95)] border border-white/10 text-white/50 text-[11px] font-semibold
                   px-2 py-[3px] rounded-md shadow-[0_4px_12px_rgba(0,0,0,0.6)]
                   transition-opacity duration-150
                   tracking-wide font-mono whitespace-nowrap"
            style="opacity: {progressHovering && hoverPct > 90 ? 0 : (progressHovering ? 1 : 0)}"
          >
            {fmt(duration)}
          </div>

          <!-- Invisible range for accessibility -->
          <input
            type="range" min="0" max={duration || 100} value={currentTime}
            oninput={(e) => { if (audioEl) audioEl.currentTime = parseFloat(e.target.value); }}
            class="absolute w-full h-full opacity-0 cursor-pointer z-10"
          />
        </div>

        <!-- Bottom row -->
        <div class="flex-1 bg-white/[0.04] rounded-md flex items-center justify-between px-3 shadow-[-1px_0_12px_rgba(0,0,0,0.5)]">

          <!-- Track info -->
          <a
            href="/music/{state.release?.slug || state.release?._id}"
            class="flex items-center gap-[10px] min-w-[190px] group/info"
          >
            {#if coverUrl}
              <img src={coverUrl} alt="" class="w-12 h-12 rounded-[3px] object-cover flex-shrink-0" />
            {:else}
              <div class="w-12 h-12 rounded-[3px] bg-white/5 flex items-center justify-center flex-shrink-0">
                <svg class="w-5 h-5 text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19V6l12-3v13"/>
                </svg>
              </div>
            {/if}
            <div class="min-w-0">
              <p class="text-[14px] font-bold text-white leading-tight truncate group-hover/info:text-[#1e6fff] transition-colors select-text">{track.title}</p>
              <p class="text-[10px] text-white/40 leading-tight truncate uppercase tracking-[0.05em]">{state.release?.title}</p>
            </div>
          </a>

          <!-- Controls -->
          <div class="flex items-center gap-0.5">
            <button onclick={() => player.prev()}
              class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/[0.06] text-white/45 hover:text-white transition-all"
              aria-label="Предыдущий">
              <svg class="w-5 h-5 fill-current" viewBox="0 0 24 24"><path d="M6 6h2v12H6zm3.5 6 8.5 6V6z"/></svg>
            </button>

            <button onclick={handlePlayPause}
              class="w-10 h-10 flex items-center justify-center rounded-full bg-white/10 hover:bg-white/20 text-white transition-all relative overflow-hidden"
              aria-label={state.isPlaying ? 'Пауза' : 'Воспроизвести'}>
              {#if rippleActive}
                <span class="absolute inset-0 rounded-full bg-white/30 animate-ping"></span>
              {/if}
              {#if state.isPlaying}
                <svg class="w-5 h-5 fill-current relative z-10" viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
              {:else}
                <svg class="w-5 h-5 fill-current ml-0.5 relative z-10" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
              {/if}
            </button>

            <button onclick={() => player.next()}
              class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/[0.06] text-white/45 hover:text-white transition-all"
              aria-label="Следующий">
              <svg class="w-5 h-5 fill-current" viewBox="0 0 24 24"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
            </button>
          </div>

          <!-- Time + Volume + Repeat -->
          <div class="flex items-center gap-1 min-w-[190px] justify-end">
            <span class="text-[12px] text-white/50 font-mono tabular-nums transition-opacity duration-200 {titleSelected || progressHovering ? 'opacity-0' : 'opacity-100'}">{fmt(currentTime)}</span>
            <span class="text-white/15 text-xs transition-opacity duration-200 {titleSelected || progressHovering ? 'opacity-0' : 'opacity-100'}">·</span>
            <span class="text-[12px] text-white/25 font-mono tabular-nums transition-opacity duration-200 {titleSelected || progressHovering ? 'opacity-0' : 'opacity-100'}">{fmt(duration)}</span>

            <!-- Volume -->
            <!-- svelte-ignore a11y_no_static_element_interactions -->
            <div
              class="relative w-8 h-8"
              onmouseenter={() => showVolume = true}
              onmouseleave={() => showVolume = false}
              onwheel={handleVolumeWheel}
            >
              <div
                class="absolute bottom-0 left-0
                       rounded-[10px] backdrop-blur-[32px]
                       flex flex-col items-center justify-end overflow-hidden
                       transition-all duration-300 ease-out z-50"
                style="width: 32px; height: {showVolume ? '150px' : '32px'};
                       background: {showVolume ? 'rgba(12,12,12,0.96)' : 'transparent'};
                       border: {showVolume ? '1px solid rgba(255,255,255,0.08)' : 'none'};
                       box-shadow: {showVolume ? '0 8px 24px rgba(0,0,0,0.6)' : 'none'};"
              >
                <!-- Slider area -->
                <div
                  class="flex flex-col items-center gap-2 px-2 pb-2 transition-opacity duration-200"
                  style="opacity: {showVolume ? 1 : 0}; pointer-events: {showVolume ? 'auto' : 'none'};"
                >
                  <span class="text-[11px] font-semibold text-white/50 tabular-nums pt-2">{Math.round(state.volume * 100)}</span>
                  <div class="relative w-1 h-[80px] cursor-pointer">
                    <div class="absolute w-full h-full bg-white/[0.06] rounded-full"></div>
                    <div
                      class="absolute bottom-0 w-full bg-gradient-to-t from-[#1e6fff] to-[#0056d6] rounded-full transition-all duration-150"
                      style="height:{state.volume * 100}%"
                    ></div>
                    <div
                      class="absolute w-[13px] h-[13px] bg-white rounded-full left-1/2 -translate-x-1/2 shadow-[0_0_8px_rgba(0,0,0,0.8)] pointer-events-none transition-all duration-150"
                      style="bottom:calc({state.volume*100}% - 6.5px)"
                    ></div>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.01"
                      value={state.volume}
                      oninput={(e) => player.setVolume(parseFloat(e.target.value))}
                      class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20"
                      style="writing-mode:vertical-lr;direction:rtl;-webkit-appearance:slider-vertical;appearance:slider-vertical;"
                    />
                  </div>
                </div>

                <!-- Icon button (always visible at bottom) -->
                <button
                  onclick={toggleMute}
                  class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/[0.06] text-white/45 hover:text-white transition-colors flex-shrink-0"
                  aria-label={state.volume === 0 ? 'Включить звук' : 'Выключить звук'}
                >
                  {#if state.volume === 0}
                    <svg class="w-[18px] h-[18px] fill-current" viewBox="0 0 24 24"><path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3 3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4 9.91 6.09 12 8.18V4z"/></svg>
                  {:else if state.volume < 0.5}
                    <svg class="w-[18px] h-[18px] fill-current" viewBox="0 0 24 24"><path d="M18.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM5 9v6h4l5 5V4L9 9H5z"/></svg>
                  {:else}
                    <svg class="w-[18px] h-[18px] fill-current" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
                  {/if}
                </button>
              </div>
            </div>

            <!-- Repeat -->
            <button onclick={() => player.toggleRepeat()}
              class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/[0.06] transition-all {repeatIcon}"
              title="Повтор: {state.repeat}">
              {#if state.repeat === 'one'}
                <svg class="w-[18px] h-[18px] fill-current" viewBox="0 0 24 24">
                  <path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/>
                  <text x="12" y="15.5" font-size="6" text-anchor="middle" fill="currentColor">1</text>
                </svg>
              {:else}
                <svg class="w-[18px] h-[18px] fill-current" viewBox="0 0 24 24"><path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/></svg>
              {/if}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}