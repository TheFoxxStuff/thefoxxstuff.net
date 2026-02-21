<script>
  /**
   * ImageLightbox — universal full-screen image viewer
   * Shows `original` variant if available, falls back to current/medium
   *
   * Usage:
   *   <ImageLightbox bind:open src={url} alt="..." />
   *
   * Or via the global helper:
   *   import { openLightbox } from '$lib/components/ImageLightbox.svelte'
   *   openLightbox({ src, alt, originalSrc })
   */
  import { API_BASE } from '$lib/api';

  let {
    open = $bindable(false),
    src = '',
    alt = '',
    originalSrc = null,   // preferred full-res URL
  } = $props();

  // Resolve best URL: prefer originalSrc, else use src
  let displaySrc = $derived(originalSrc || src || '');
  let loading = $state(false);
  let imgLoaded = $state(false);

  function close() { open = false; }

  function handleKeydown(e) {
    if (e.key === 'Escape') close();
  }

  function handleBgClick(e) {
    if (e.target === e.currentTarget) close();
  }

  $effect(() => {
    if (open) {
      imgLoaded = false;
      loading = true;
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  });
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
  <div
    class="lb-backdrop"
    onclick={handleBgClick}
    role="dialog"
    aria-modal="true"
    aria-label="Image preview"
    tabindex="-1"
  >
    <!-- Close button -->
    <button class="lb-close" onclick={close} aria-label="Close lightbox">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M18 6L6 18M6 6l12 12"/>
      </svg>
    </button>

    <!-- Image container -->
    <div class="lb-stage" onclick={(e) => e.stopPropagation()} role="presentation">
      {#if loading && !imgLoaded}
        <div class="lb-spinner">
          <svg class="spin" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="2">
            <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="12"/>
          </svg>
        </div>
      {/if}

      <img
        src={displaySrc}
        {alt}
        class="lb-img"
        class:lb-img--loaded={imgLoaded}
        onload={() => { imgLoaded = true; loading = false; }}
        onerror={() => { loading = false; }}
        draggable="false"
      />
    </div>

    {#if alt}
      <div class="lb-caption">{alt}</div>
    {/if}

    <!-- Original quality badge -->
    {#if originalSrc && originalSrc !== src}
      <div class="lb-badge">ORIGINAL</div>
    {/if}
  </div>
{/if}

<style>
  .lb-backdrop {
    position: fixed;
    inset: 0;
    z-index: 10200;
    background: rgba(0, 0, 0, 0.93);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    padding: 60px 24px 40px;
    cursor: zoom-out;
    animation: lb-fade 0.18s ease;
  }

  @keyframes lb-fade {
    from { opacity: 0; }
    to   { opacity: 1; }
  }

  .lb-close {
    position: absolute;
    top: 16px;
    right: 16px;
    width: 42px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255,255,255,0.07);
    border-radius: 50%;
    color: rgba(255,255,255,0.65);
    cursor: pointer;
    transition: background 0.15s, color 0.15s, transform 0.15s;
  }
  .lb-close:hover {
    background: rgba(255,255,255,0.15);
    color: #fff;
    transform: scale(1.08);
  }

  .lb-stage {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    max-width: 92vw;
    max-height: calc(100vh - 120px);
    cursor: default;
  }

  .lb-spinner {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .spin { animation: spin 0.9s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }

  .lb-img {
    max-width: 92vw;
    max-height: calc(100vh - 120px);
    object-fit: contain;
    border-radius: 6px;
    box-shadow: 0 40px 100px rgba(0,0,0,0.7);
    opacity: 0;
    transition: opacity 0.2s ease;
    animation: lb-pop 0.22s cubic-bezier(0.34, 1.46, 0.64, 1) forwards;
  }
  .lb-img--loaded { opacity: 1; }

  @keyframes lb-pop {
    from { transform: scale(0.93); opacity: 0; }
    to   { transform: scale(1);    opacity: 1; }
  }

  .lb-caption {
    margin-top: 14px;
    font-size: 13px;
    color: rgba(255,255,255,0.4);
    text-align: center;
    font-style: italic;
    max-width: 600px;
    line-height: 1.4;
  }

  .lb-badge {
    position: absolute;
    top: 16px;
    left: 16px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    padding: 4px 8px;
    background: rgba(74, 222, 128, 0.15);
    border: 1px solid rgba(74, 222, 128, 0.3);
    color: #4ade80;
    border-radius: 6px;
  }
</style>
