<script>
  import { api, getImageUrl } from '$lib/api';
  
  let { 
    value = $bindable([]), // Array of image IDs
    images = $bindable([]), // Array of image info objects
    label = 'Gallery',
    accept = 'image/*',
    max = 20
  } = $props();
  
  let fileInput = $state();
  let uploading = $state(false);
  let dragOver = $state(false);
  let error = $state('');
  
  async function handleUpload(files) {
    if (!files || files.length === 0) return;
    if (value.length + files.length > max) {
      error = `Maximum ${max} images allowed`;
      return;
    }
    
    uploading = true;
    error = '';
    
    try {
      const results = await api.upload.images(files);
      for (const result of results) {
        if (result._id) {
          value = [...value, result._id];
          images = [...images, result];
        } else if (result.error) {
          error = result.error;
        }
      }
    } catch (err) {
      error = err.message;
    } finally {
      uploading = false;
    }
  }
  
  function handleFileSelect(e) {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) handleUpload(files);
    e.target.value = '';
  }
  
  function handleDrop(e) {
    e.preventDefault();
    dragOver = false;
    const files = Array.from(e.dataTransfer.files || []).filter(f => f.type.startsWith('image/'));
    if (files.length > 0) handleUpload(files);
  }
  
  function removeImage(index) {
    value = value.filter((_, i) => i !== index);
    images = images.filter((_, i) => i !== index);
  }

  function handleZoneKeydown(e) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      fileInput?.click();
    }
  }
  
  function moveImage(fromIndex, toIndex) {
    if (toIndex < 0 || toIndex >= value.length) return;
    const newValue = [...value];
    const newImages = [...images];
    [newValue[fromIndex], newValue[toIndex]] = [newValue[toIndex], newValue[fromIndex]];
    [newImages[fromIndex], newImages[toIndex]] = [newImages[toIndex], newImages[fromIndex]];
    value = newValue;
    images = newImages;
  }
</script>

<div class="multi-image-upload">
  <div class="label">{label} ({value.length}/{max})</div>
  
  {#if images.length > 0}
    <div class="grid grid-cols-4 gap-3 mb-3">
      {#each images as img, i}
        <div class="relative group aspect-square">
          <img src={getImageUrl(img, 'thumb')} alt="" class="w-full h-full object-cover rounded-lg" />
          <div class="absolute inset-0 bg-[--bg] opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-1 rounded-lg">
            <button type="button" onclick={() => moveImage(i, i - 1)} disabled={i === 0} class="p-1 rounded disabled:opacity-30 hover:bg-[--w8]" title="Move left">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
            </button>
            <button type="button" onclick={() => removeImage(i)} class="p-1 hover:bg-accent-red/80 rounded" title="Remove">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
            <button type="button" onclick={() => moveImage(i, i + 1)} disabled={i === value.length - 1} class="p-1 rounded disabled:opacity-30 hover:bg-[--w8]" title="Move right">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
  
  {#if value.length < max}
    <div 
      class="upload-zone {dragOver ? 'drag-over' : ''}"
      ondrop={handleDrop}
      ondragover={(e) => { e.preventDefault(); dragOver = true; }}
      ondragleave={() => dragOver = false}
      role="button"
      tabindex="0"
      onkeydown={handleZoneKeydown}
    >
      {#if uploading}
        <div class="flex items-center justify-center gap-2 py-6">
          <svg class="w-6 h-6 animate-spin text-accent-green" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <span class="text-sm text-dark-400">Uploading...</span>
        </div>
      {:else}
        <div class="flex items-center justify-center gap-4 py-6">
          <svg class="w-8 h-8 text-dark-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          <span class="text-sm text-dark-400">Drag & drop or click to add images</span>
          <button type="button" onclick={() => fileInput.click()} class="btn btn-secondary text-sm">
            Add Images
          </button>
        </div>
      {/if}
      
      <input 
        type="file" 
        bind:this={fileInput}
        onchange={handleFileSelect}
        {accept}
        multiple
        class="hidden" 
      />
    </div>
  {/if}
  
  {#if error}
    <p class="text-sm text-accent-red mt-2">{error}</p>
  {/if}
</div>

<style>
  .upload-zone {
    border: 2px dashed #434343;
    border-radius: 0.5rem;
    transition: all 0.2s;
    cursor: pointer;
  }
  .upload-zone:hover, .upload-zone.drag-over {
    border-color: rgba(74, 222, 128, 0.5);
    background: rgba(56, 56, 56, 0.5);
  }
</style>
