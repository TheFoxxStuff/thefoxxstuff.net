<script>
  import { onMount } from 'svelte';
  import { api, getImageUrl, API_BASE } from '$lib/api';

  let activeTab = $state('images'); // 'images' | 'audio'

  // ── Images ──────────────────────────────────────────
  let images = $state({ items: [], total: 0, page: 1, pages: 1 });
  let loadingImages = $state(true);
  let imgPage = $state(1);
  let category = $state('');
  let unusedOnly = $state(false);
  let cleanupResult = $state(null);
  let cleaning = $state(false);
  let selectedImage = $state(null);

  // ── Audio ────────────────────────────────────────────
  let audioFiles = $state([]);
  let loadingAudio = $state(false);
  let audioCleanupResult = $state(null);
  let cleaningAudio = $state(false);
  let selectedAudio = $state(null);

  async function loadImages() {
    loadingImages = true;
    try {
      images = await api.upload.list(imgPage, 24, category || null, unusedOnly);
    } catch (e) { console.error(e); }
    finally { loadingImages = false; }
  }

  async function loadAudio() {
    loadingAudio = true;
    try {
      // Get all audio used by music releases to identify unused
      const musicData = await api.music.list(1, 200);
      const usedAudioPaths = new Set();
      for (const release of musicData.items || []) {
        for (const track of release.tracks || []) {
          if (track.audio_original) usedAudioPaths.add(track.audio_original);
          if (track.audio_opus) usedAudioPaths.add(track.audio_opus);
          if (track.audio_mp3_320) usedAudioPaths.add(track.audio_mp3_320);
          if (track.audio_mp3_128) usedAudioPaths.add(track.audio_mp3_128);
        }
      }
      // Fetch audio from API if endpoint exists, else show info
      // The backend stores audio in db.audio_files
      // We'll use the upload.audioInfo but need a list endpoint - call via direct fetch
      const token = localStorage.getItem('auth') ? JSON.parse(localStorage.getItem('auth')).token : null;
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const res = await fetch(`${API_BASE}/upload/audio/list?limit=200`, { headers });
      if (res.ok) {
        const data = await res.json();
        audioFiles = (data.items || data).map(a => ({
          ...a,
          _used: usedAudioPaths.has(a.original_path) || usedAudioPaths.has(a.opus_path) ||
                 usedAudioPaths.has(a.mp3_320_path) || usedAudioPaths.has(a.mp3_128_path)
        }));
      } else {
        audioFiles = [];
      }
    } catch (e) {
      console.error(e);
      audioFiles = [];
    }
    finally { loadingAudio = false; }
  }

  onMount(() => loadImages());

  $effect(() => {
    if (activeTab === 'images') loadImages();
    else loadAudio();
  });

  async function changePage(p) { imgPage = p; await loadImages(); }
  async function applyFilter() { imgPage = 1; await loadImages(); }

  async function deleteImage(id) {
    if (!confirm('Delete this image? This cannot be undone.')) return;
    try {
      await api.upload.delete(id);
      await loadImages();
      if (selectedImage?._id === id) selectedImage = null;
    } catch (e) { alert(e.message); }
  }

  async function deleteAudio(id) {
    if (!confirm('Delete this audio file and all its conversions? This cannot be undone.')) return;
    try {
      await api.upload.audioDelete(id);
      audioFiles = audioFiles.filter(a => a._id !== id);
      if (selectedAudio?._id === id) selectedAudio = null;
    } catch (e) { alert(e.message); }
  }

  async function runCleanup() {
    if (!confirm('Delete ALL unused images? This cannot be undone.')) return;
    cleaning = true;
    try {
      cleanupResult = await api.upload.cleanup();
      await loadImages();
    } catch (e) { alert(e.message); }
    finally { cleaning = false; }
  }

  async function runAudioCleanup() {
    const unused = audioFiles.filter(a => !a._used);
    if (!unused.length) { alert('No unused audio files found.'); return; }
    if (!confirm(`Delete ${unused.length} unused audio file(s)? This cannot be undone.`)) return;
    cleaningAudio = true;
    let deleted = 0;
    for (const a of unused) {
      try {
        await api.upload.audioDelete(a._id);
        deleted++;
      } catch {}
    }
    audioCleanupResult = { deleted_count: deleted };
    await loadAudio();
    cleaningAudio = false;
  }

  function thumbUrl(img) {
    if (img.thumb) return `${API_BASE}/upload/file/${img.thumb}`;
    if (img.medium) return `${API_BASE}/upload/file/${img.medium}`;
    if (img.original) return `${API_BASE}/upload/file/${img.original}`;
    return null;
  }

  function formatSize(bytes) {
    if (!bytes) return '—';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  }

  function formatDate(d) {
    return d ? new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '—';
  }

  let unusedAudioCount = $derived(audioFiles.filter(a => !a._used).length);
  let totalAudioSize = $derived(audioFiles.reduce((s, a) => s + (a.size || 0), 0));
</script>

<svelte:head><title>Media Manager - Admin</title></svelte:head>

<div>
  <div class="flex items-center justify-between mb-6">
    <h1 class="font-display text-[24px] tracking-wide">Media Manager</h1>
    <div class="flex gap-2">
      {#if activeTab === 'images'}
        <button onclick={runCleanup} disabled={cleaning} class="btn btn-danger text-sm">
          {cleaning ? 'Cleaning...' : '🗑 Cleanup Unused Images'}
        </button>
      {:else}
        <button onclick={runAudioCleanup} disabled={cleaningAudio || unusedAudioCount === 0} class="btn btn-danger text-sm">
          {cleaningAudio ? 'Cleaning...' : `🗑 Delete ${unusedAudioCount} Unused Audio`}
        </button>
      {/if}
    </div>
  </div>

  <!-- Tabs -->
  <div class="flex gap-1 mb-6 bg-dark-900 p-1 rounded-lg w-fit">
    <button onclick={() => activeTab = 'images'} class="px-5 py-2 rounded-md text-sm font-medium transition {activeTab === 'images' ? 'bg-dark-700 text-white' : 'text-dark-400 hover:text-white'}">
      🖼 Images ({images.total})
    </button>
    <button onclick={() => activeTab = 'audio'} class="px-5 py-2 rounded-md text-sm font-medium transition {activeTab === 'audio' ? 'bg-dark-700 text-white' : 'text-dark-400 hover:text-white'}">
      🎵 Audio ({audioFiles.length})
    </button>
  </div>

  {#if cleanupResult}
    <div class="card p-4 mb-4 bg-accent-green/10 text-accent-green text-sm flex items-center gap-2">
      <span>✓</span> Cleaned up {cleanupResult.deleted_count ?? 0} unused images ({cleanupResult.total_used ?? 0} in use)
    </div>
  {/if}
  {#if audioCleanupResult}
    <div class="card p-4 mb-4 bg-accent-green/10 text-accent-green text-sm flex items-center gap-2">
      <span>✓</span> Deleted {audioCleanupResult.deleted_count} unused audio files
    </div>
  {/if}

  <!-- ═══ IMAGES TAB ═══════════════════════════════════════════ -->
  {#if activeTab === 'images'}
    <!-- Filters -->
    <div class="flex items-center gap-3 mb-4 flex-wrap">
      <select bind:value={category} onchange={applyFilter} class="input w-40 text-sm">
        <option value="">All Categories</option>
        <option value="music">Music</option>
        <option value="blog">Blog</option>
        <option value="arts">Arts</option>
        <option value="banner">Banner</option>
        <option value="markdown">Markdown</option>
      </select>
      <label class="flex items-center gap-2 text-sm text-dark-400 cursor-pointer select-none">
        <input type="checkbox" bind:checked={unusedOnly} onchange={applyFilter} class="accent-green-400" />
        Unused only
      </label>
      <span class="text-sm text-dark-500 ml-auto">{images.total} images</span>
    </div>

    {#if loadingImages}
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {#each Array(12) as _}<div class="aspect-square bg-dark-800 rounded-lg animate-pulse"></div>{/each}
      </div>
    {:else}
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {#each images.items as img}
          <button
            onclick={() => selectedImage = selectedImage?._id === img._id ? null : img}
            class="group aspect-square bg-dark-800 rounded-lg overflow-hidden relative border-2 transition
              {selectedImage?._id === img._id ? 'border-accent-green' : 'border-transparent hover:border-dark-600'}"
          >
            {#if thumbUrl(img)}
              <img src={thumbUrl(img)} alt="" class="w-full h-full object-cover" loading="lazy" />
            {:else}
              <div class="w-full h-full flex items-center justify-center text-dark-500 text-xs">No preview</div>
            {/if}
            <div class="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/80 to-transparent p-2 opacity-0 group-hover:opacity-100 transition">
              <div class="text-xs text-white truncate">{img.custom_name || img.filename || 'Untitled'}</div>
              <div class="text-[10px] text-dark-400">{formatSize(img.size)}</div>
            </div>
            {#if img.category}
              <span class="absolute top-1 left-1 px-1.5 py-0.5 text-[10px] bg-dark-900/80 text-dark-300 rounded">{img.category}</span>
            {/if}
          </button>
        {/each}
      </div>

      {#if images.items.length === 0}
        <div class="text-center text-dark-500 py-12">No images found</div>
      {/if}

      {#if images.pages > 1}
        <div class="flex items-center justify-center gap-2 mt-6">
          {#each Array(images.pages) as _, i}
            <button onclick={() => changePage(i+1)} class="px-3 py-1 text-sm rounded-lg {imgPage === i+1 ? 'bg-accent-green text-dark-950' : 'bg-dark-800 text-dark-400 hover:text-white'}">{i+1}</button>
          {/each}
        </div>
      {/if}
    {/if}

    <!-- Image detail panel -->
    {#if selectedImage}
      <div class="card p-4 mt-4">
        <div class="flex gap-4">
          <div class="w-32 h-32 bg-dark-800 rounded-lg overflow-hidden flex-shrink-0">
            {#if thumbUrl(selectedImage)}<img src={thumbUrl(selectedImage)} alt="" class="w-full h-full object-cover" />{/if}
          </div>
          <div class="flex-1 text-sm space-y-1">
            <div class="text-white font-medium">{selectedImage.custom_name || selectedImage.filename || 'Untitled'}</div>
            <div class="text-dark-400">Category: <span class="text-dark-300">{selectedImage.category || '—'}</span></div>
            <div class="text-dark-400">Size: <span class="text-dark-300">{formatSize(selectedImage.size)}</span></div>
            <div class="text-dark-400">Dimensions: <span class="text-dark-300">{selectedImage.width}×{selectedImage.height}</span></div>
            <div class="text-dark-400">Uploaded: <span class="text-dark-300">{formatDate(selectedImage.created_at)}</span></div>
            <div class="text-dark-600 text-xs break-all mt-1">ID: {selectedImage._id}</div>
            <div class="flex gap-2 mt-2">
              <a href="{API_BASE}/upload/file/{selectedImage.medium || selectedImage.original}" target="_blank" class="btn text-xs py-1.5 px-3">View</a>
              <button onclick={() => deleteImage(selectedImage._id)} class="btn btn-danger text-xs py-1.5 px-3">Delete</button>
            </div>
          </div>
        </div>
      </div>
    {/if}

  <!-- ═══ AUDIO TAB ═══════════════════════════════════════════ -->
  {:else}
    <div class="flex items-center gap-4 mb-4 text-sm text-dark-400">
      <span>{audioFiles.length} files · {formatSize(totalAudioSize)} total</span>
      {#if unusedAudioCount > 0}
        <span class="text-yellow-400">{unusedAudioCount} unused</span>
      {:else}
        <span class="text-accent-green">All in use</span>
      {/if}
    </div>

    {#if loadingAudio}
      <div class="space-y-2">
        {#each Array(6) as _}
          <div class="h-16 bg-dark-800 rounded-lg animate-pulse"></div>
        {/each}
      </div>
    {:else if audioFiles.length === 0}
      <div class="text-center text-dark-500 py-12">
        <p class="text-4xl mb-3">🎵</p>
        <p>No audio files found. Upload audio via the Music admin page.</p>
      </div>
    {:else}
      <div class="space-y-2">
        {#each audioFiles as audio}
          <div class="card p-4 flex items-center gap-4 {!audio._used ? 'border border-yellow-500/20' : ''}">
            <!-- Icon -->
            <div class="w-10 h-10 rounded-lg bg-dark-800 flex items-center justify-center flex-shrink-0 text-lg">
              🎵
            </div>

            <!-- Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="text-sm font-medium text-white truncate">{audio.custom_name || audio.original_filename || 'Untitled'}</span>
                {#if !audio._used}
                  <span class="text-[10px] px-1.5 py-0.5 bg-yellow-500/20 text-yellow-400 rounded flex-shrink-0">UNUSED</span>
                {/if}
              </div>
              <div class="text-xs text-dark-400 flex gap-3 mt-0.5 flex-wrap">
                <span>{audio.duration || '—'}</span>
                <span>{formatSize(audio.size)}</span>
                {#if audio.mp3_320_path}<span class="text-accent-green">MP3 320 ✓</span>{/if}
                {#if audio.opus_path}<span class="text-accent-green">OPUS ✓</span>{/if}
                {#if audio.mp3_128_path}<span class="text-accent-green">MP3 128 ✓</span>{/if}
                <span>{formatDate(audio.created_at)}</span>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex gap-2 flex-shrink-0">
              {#if audio.opus_path}
                <a href="{API_BASE}/upload/audio/file/{audio.opus_path}" class="btn text-xs py-1.5 px-3" target="_blank">▶ Play</a>
              {/if}
              <button
                onclick={() => { if (confirm(`Delete "${audio.custom_name || audio.original_filename}" and all its conversions?`)) deleteAudio(audio._id); }}
                class="btn btn-danger text-xs py-1.5 px-3"
              >Delete</button>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</div>
