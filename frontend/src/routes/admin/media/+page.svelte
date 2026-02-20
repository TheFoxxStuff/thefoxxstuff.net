<script>
  import { onMount } from 'svelte';
  import { api, getImageUrl, API_BASE } from '$lib/api';

  let images = $state({ items: [], total: 0, page: 1, pages: 1 });
  let loading = $state(true);
  let page = $state(1);
  let category = $state('');
  let unusedOnly = $state(false);
  let cleanupResult = $state(null);
  let cleaning = $state(false);
  let selectedImage = $state(null);

  async function loadImages() {
    loading = true;
    try {
      images = await api.upload.list(page, 24, category || null, unusedOnly);
    } catch (e) { console.error(e); }
    finally { loading = false; }
  }

  onMount(() => loadImages());

  async function changePage(p) { page = p; await loadImages(); }
  async function applyFilter() { page = 1; await loadImages(); }

  async function deleteImage(id) {
    if (!confirm('Delete this image?')) return;
    try {
      await api.upload.delete(id);
      await loadImages();
      if (selectedImage?._id === id) selectedImage = null;
    } catch (e) { alert(e.message); }
  }

  async function runCleanup() {
    if (!confirm('Delete all unused images? This cannot be undone.')) return;
    cleaning = true;
    try {
      cleanupResult = await api.upload.cleanup();
      await loadImages();
    } catch (e) { alert(e.message); }
    finally { cleaning = false; }
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

  function formatDate(d) { return d ? new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '—'; }
</script>

<svelte:head><title>Media Manager - Admin</title></svelte:head>

<div>
  <div class="flex items-center justify-between mb-6">
    <h1 class="font-display text-3xl tracking-wide">Media Manager</h1>
    <button onclick={runCleanup} disabled={cleaning} class="btn btn-danger text-sm">
      {cleaning ? 'Cleaning...' : 'Cleanup Unused'}
    </button>
  </div>

  {#if cleanupResult}
    <div class="card p-4 mb-4 bg-accent-green/10 text-accent-green text-sm">
      Cleaned up {cleanupResult.deleted_count ?? 0} unused images
    </div>
  {/if}

  <!-- Filters -->
  <div class="flex items-center gap-3 mb-6">
    <select bind:value={category} onchange={applyFilter} class="input w-40 text-sm">
      <option value="">All Categories</option>
      <option value="music">Music</option>
      <option value="blog">Blog</option>
      <option value="arts">Arts</option>
      <option value="banner">Banner</option>
      <option value="markdown">Markdown</option>
    </select>
    <label class="flex items-center gap-2 text-sm text-[--w60] cursor-pointer">
      <input type="checkbox" bind:checked={unusedOnly} onchange={applyFilter} class="accent-green-400" />
      Unused only
    </label>
    <span class="text-sm text-[--w30] ml-auto">{images.total} images</span>
  </div>

  {#if loading}
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
      {#each Array(12) as _}<div class="aspect-square bg-[--w8] rounded-lg animate-pulse"></div>{/each}
    </div>
  {:else}
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
      {#each images.items as img}
        <button
          onclick={() => selectedImage = selectedImage?._id === img._id ? null : img}
          class="group aspect-square bg-[--w8] rounded-lg overflow-hidden relative border-2 transition {selectedImage?._id === img._id ? 'border-accent-green' : 'border-transparent hover:border-dark-600'}"
        >
          {#if thumbUrl(img)}
            <img src={thumbUrl(img)} alt="" class="w-full h-full object-cover" loading="lazy" />
          {:else}
            <div class="w-full h-full flex items-center justify-center text-[--w30] text-xs">No preview</div>
          {/if}
          <div class="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/70 to-transparent p-2 opacity-0 group-hover:opacity-100 transition">
            <div class="text-xs text-white truncate">{img.custom_name || img.filename || 'Untitled'}</div>
            <div class="text-[10px] text-[--w60]">{formatSize(img.size)}</div>
          </div>
          {#if img.category}
            <span class="absolute top-1 left-1 px-1.5 py-0.5 text-[10px] bg-[--w5]/80 text-dark-300 rounded">{img.category}</span>
          {/if}
        </button>
      {/each}
    </div>

    {#if images.items.length === 0}
      <div class="text-center text-[--w30] py-12">No images found</div>
    {/if}

    <!-- Pagination -->
    {#if images.pages > 1}
      <div class="flex items-center justify-center gap-2 mt-6">
        {#each Array(images.pages) as _, i}
          <button onclick={() => changePage(i+1)} class="px-3 py-1 text-sm rounded-lg {page === i+1 ? 'bg-accent-green text-dark-950' : 'bg-[--w8] text-[--w60] hover:text-white'}">{i+1}</button>
        {/each}
      </div>
    {/if}
  {/if}

  <!-- Detail panel -->
  {#if selectedImage}
    <div class="card p-4 mt-4">
      <div class="flex gap-4">
        <div class="w-32 h-32 bg-[--w8] rounded-lg overflow-hidden flex-shrink-0">
          {#if thumbUrl(selectedImage)}<img src={thumbUrl(selectedImage)} alt="" class="w-full h-full object-cover" />{/if}
        </div>
        <div class="flex-1 text-sm space-y-1">
          <div class="text-[--w] font-medium">{selectedImage.custom_name || selectedImage.filename || 'Untitled'}</div>
          <div class="text-[--w60]">Category: {selectedImage.category || '—'}</div>
          <div class="text-[--w60]">Size: {formatSize(selectedImage.size)}</div>
          <div class="text-[--w60]">Dimensions: {selectedImage.width}×{selectedImage.height}</div>
          <div class="text-[--w60]">Uploaded: {formatDate(selectedImage.created_at)}</div>
          <div class="text-[--w30] text-xs break-all mt-2">ID: {selectedImage._id}</div>
          <button onclick={() => deleteImage(selectedImage._id)} class="btn btn-danger text-sm mt-2">Delete Image</button>
        </div>
      </div>
    </div>
  {/if}
</div>
