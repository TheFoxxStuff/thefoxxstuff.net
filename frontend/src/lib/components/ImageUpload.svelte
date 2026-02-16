<script>
  import { api, getImageUrl } from '$lib/api';
  
  let { 
    value = $bindable(null), // Image ID or info object
    imageInfo = $bindable(null), // Full image info object
    label = 'Image',
    accept = 'image/*',
    category = 'markdown', // Category: music, blog, arts, markdown, banner
    customName = null, // Custom name for the file
    parentId = null // Parent entity ID
  } = $props();
  
  let fileInput;
  let uploading = $state(false);
  let dragOver = $state(false);
  let error = $state('');
  
  // Compute preview URL
  let previewUrl = $derived.by(() => {
    if (imageInfo) return getImageUrl(imageInfo, 'thumb');
    if (value && typeof value === 'string' && value.startsWith('http')) return value;
    return null;
  });
  
  async function handleUpload(file) {
    if (!file) return;
    uploading = true;
    error = '';
    try {
      // Use custom name or file name without extension
      const name = customName || file.name.replace(/\.[^/.]+$/, '');
      const result = await api.upload.image(file, category, name, parentId, false);
      value = result._id;
      imageInfo = result;
    } catch (err) {
      error = err.message;
    } finally {
      uploading = false;
    }
  }
  
  function handleFileSelect(e) {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
  }
  
  function handleDrop(e) {
    e.preventDefault();
    dragOver = false;
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) handleUpload(file);
  }
  
  function handleDragOver(e) {
    e.preventDefault();
    dragOver = true;
  }
  
  function handleDragLeave(e) {
    e.preventDefault();
    dragOver = false;
  }
  
  function clearImage() {
    value = null;
    imageInfo = null;
    if (fileInput) fileInput.value = '';
  }
</script>

<div class="image-upload">
  <label class="label">{label}</label>
  
  <div 
    class="upload-zone {dragOver ? 'drag-over' : ''}"
    ondrop={handleDrop}
    ondragover={handleDragOver}
    ondragleave={handleDragLeave}
  >
    {#if uploading}
      <div class="flex flex-col items-center gap-2 py-8">
        <svg class="w-8 h-8 animate-spin text-accent-green" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <span class="text-sm text-dark-400">Uploading...</span>
      </div>
    {:else if previewUrl}
      <div class="relative">
        <img src={previewUrl} alt="Preview" class="max-h-48 rounded-lg mx-auto" />
        <button type="button" onclick={clearImage} class="absolute top-2 right-2 p-1 bg-dark-900/80 rounded-full hover:bg-accent-red/80 transition-colors">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
      </div>
    {:else}
      <div class="flex flex-col items-center gap-2 py-8">
        <svg class="w-12 h-12 text-dark-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <span class="text-sm text-dark-400">Drag & drop or click to upload</span>
        <button type="button" onclick={() => fileInput.click()} class="btn btn-secondary text-sm">
          Choose File
        </button>
      </div>
    {/if}
    
    <input 
      type="file" 
      bind:this={fileInput}
      onchange={handleFileSelect}
      {accept}
      class="hidden" 
    />
  </div>
  
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
