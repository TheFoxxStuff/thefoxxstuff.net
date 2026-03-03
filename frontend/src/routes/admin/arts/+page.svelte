<script>
  import { SEO } from "$lib/components";
  import { canonicalUrl } from "$lib/seo.js";
  import { api, getImageUrl, generateSlug } from '$lib/api';
  import { ImageUpload, MarkdownEditor } from '$lib/components';

  let { data: pageData } = $props();
  let artworks = $state(pageData.artworks);
  let loading = $state(false);
  let showForm = $state(false);
  let editingId = $state(null);
  let form = $state({
    title: '',
    slug: '',
    description: '',
    image: '',
    dimensions: '1024 x 1024',
    file_size: '1.2 MB',
    year: new Date().getFullYear(),
    meta_title: '',
    meta_description: '',
    meta_keywords: '',
    og_image: ''
  });
  let imageInfo = $state(null);
  let ogImageInfo = $state(null);
  let error = $state('');
  let showSeo = $state(false);
  let slugManuallyEdited = $state(false);

  // Auto-generate slug from title reactively
  $effect(() => {
    if (!editingId && form.title && !slugManuallyEdited) {
      form.slug = generateSlug(form.title);
    }
  });
  
  const loadArtworks = async () => {
    try {
      artworks = (await api.arts.list(1, 100)).items;
    } catch (e) {
      console.error(e);
    }
  };
  
  const resetForm = () => {
    form = {
      title: '',
      slug: '',
      description: '',
      image: '',
      dimensions: '1024 x 1024',
      file_size: '1.2 MB',
      year: new Date().getFullYear(),
      meta_title: '',
      meta_description: '',
      meta_keywords: '',
      og_image: ''
    };
    imageInfo = null;
    ogImageInfo = null;
    editingId = null;
    showForm = false;
    showSeo = false;
    slugManuallyEdited = false;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    error = '';
    try {
      const data = { ...form, year: parseInt(form.year) };
      // Auto-fill dimensions and file size from image info
      if (imageInfo) {
        data.dimensions = `${imageInfo.width} x ${imageInfo.height}`;
        data.file_size = formatFileSize(imageInfo.size);
      }
      // Auto-generate slug if empty
      if (!data.slug) {
        data.slug = generateSlug(data.title);
      }
      if (editingId) await api.arts.update(editingId, data);
      else await api.arts.create(data);
      resetForm();
      loadArtworks();
    } catch (err) {
      error = err.message;
    }
  };
  
  const editArtwork = async (a) => {
    editingId = a._id;
    slugManuallyEdited = true; // Don't auto-generate when editing
    form = {
      title: a.title,
      slug: a.slug || '',
      description: a.description || '',
      image: a.image || '',
      dimensions: a.dimensions,
      file_size: a.file_size,
      year: a.year,
      meta_title: a.meta_title || '',
      meta_description: a.meta_description || '',
      meta_keywords: a.meta_keywords || '',
      og_image: a.og_image || ''
    };
    imageInfo = a.image_info || null;
    if (a.og_image) {
      try {
        ogImageInfo = await api.upload.getInfo(a.og_image);
      } catch {
        ogImageInfo = null;
      }
    }
    showForm = true;
    showSeo = !!(a.meta_title || a.meta_description || a.meta_keywords);
  };
  
  const deleteArtwork = async (id) => {
    if (!confirm('Delete this artwork?')) return;
    try {
      await api.arts.delete(id);
      loadArtworks();
    } catch (err) {
      alert(err.message);
    }
  };

  function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }
  
  // Auto-update dimensions when image is uploaded
  $effect(() => {
    if (imageInfo) {
      form.dimensions = `${imageInfo.width} x ${imageInfo.height}`;
      form.file_size = formatFileSize(imageInfo.size);
    }
  });
</script>

<SEO titleFull="Arts Admin - TheFoxxStuff" noindex={true} url={canonicalUrl("/admin")} />

<div>
  <div class="flex justify-between mb-8">
    <h1 class="font-display text-[24px]">Arts</h1>
    <button onclick={() => { resetForm(); showForm = true; }} class="btn btn-primary">Add Artwork</button>
  </div>
  
  {#if showForm}
    <div class="card p-6 mb-8">
      <h2 class="font-display text-xl mb-4">{editingId ? 'Edit' : 'New'} Artwork</h2>
      {#if error}<div class="mb-4 p-3 bg-accent-red/10 border border-accent-red/50 rounded-lg text-accent-red text-sm">{error}</div>{/if}
      
      <form onsubmit={handleSubmit} class="space-y-6">
        <div class="grid grid-cols-3 gap-4">
          <div class="col-span-2">
            <label class="label" for="fl-title-1">Title</label>
            <input id="fl-title-1" type="text" bind:value={form.title} required class="input" />
          </div>
          <div>
            <label class="label" for="fl-year-2">Year</label>
            <input id="fl-year-2" type="number" bind:value={form.year} required class="input" />
          </div>
        </div>
        
        <div>
          <label class="label" for="fl-slug-url-3">Slug (URL)</label>
          <div class="flex gap-2">
            <input id="fl-slug-url-3" type="text" bind:value={form.slug} class="input flex-1" placeholder="auto-generated-from-title" />
            <button type="button" onclick={() => form.slug = generateSlug(form.title)} class="btn btn-secondary text-sm">Generate</button>
          </div>
        </div>
        
        <ImageUpload 
          label="Image" 
          bind:value={form.image} 
          bind:imageInfo={imageInfo}
          category="arts"
          customName={form.title}
        />
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label" for="fl-dimensions-auto-filled-4">Dimensions (auto-filled)</label>
            <input id="fl-dimensions-auto-filled-4" type="text" bind:value={form.dimensions} class="input bg-[--w5]" readonly />
          </div>
          <div>
            <label class="label" for="fl-file-size-auto-filled-5">File Size (auto-filled)</label>
            <input id="fl-file-size-auto-filled-5" type="text" bind:value={form.file_size} class="input bg-[--w5]" readonly />
          </div>
        </div>
        
        <div>
          <label class="label">Description (Markdown)</label>
          <MarkdownEditor bind:value={form.description} rows={6} placeholder="Describe your artwork..." />
        </div>
        
        <!-- SEO Section -->
        <div class="border-t border-[--w8] pt-6">
          <button type="button" onclick={() => showSeo = !showSeo} class="flex items-center gap-2 text-[--w60] hover:text-white transition-colors">
            <svg class="w-5 h-5 transition-transform {showSeo ? 'rotate-90' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            <span class="font-medium">SEO Settings</span>
          </button>
          
          {#if showSeo}
            <div class="mt-4 space-y-4 pl-7">
              <div>
                <label class="label" for="fl-meta-title-6">Meta Title</label>
                <input id="fl-meta-title-6" type="text" bind:value={form.meta_title} class="input" placeholder="Custom title for search engines" />
              </div>
              
              <div>
                <label class="label" for="fl-meta-description-7">Meta Description</label>
                <textarea id="fl-meta-description-7" bind:value={form.meta_description} rows="2" class="textarea" placeholder="Description for search engines"></textarea>
                {#if form.meta_description}
                  <p class="text-xs text-[--w30] mt-1">{form.meta_description.length}/160 characters</p>
                {/if}
              </div>
              
              <div>
                <label class="label" for="fl-meta-keywords-8">Meta Keywords</label>
                <input id="fl-meta-keywords-8" type="text" bind:value={form.meta_keywords} class="input" placeholder="keyword1, keyword2, keyword3" />
              </div>
              
              <ImageUpload 
                label="Open Graph Image" 
                bind:value={form.og_image} 
                bind:imageInfo={ogImageInfo}
                category="arts"
                customName={form.title ? `${form.title}-og` : null}
              />
            </div>
          {/if}
        </div>
        
        <div class="flex gap-2">
          <button type="submit" class="btn btn-primary">{editingId ? 'Update' : 'Create'}</button>
          <button type="button" onclick={resetForm} class="btn btn-secondary">Cancel</button>
        </div>
      </form>
    </div>
  {/if}
  
    <div class="grid grid-cols-4 gap-4">
      {#each artworks as artwork}
        <div class="card p-2 group relative">
          <div class="aspect-square bg-[--w8] rounded-lg overflow-hidden mb-2">
            {#if artwork.image_info}
              <img src={getImageUrl(artwork.image_info, 'thumb')} alt="" class="w-full h-full object-cover" />
            {:else if artwork.image}
              {#await api.upload.getInfo(artwork.image) then imgInfo}
                <img src={getImageUrl(imgInfo, 'thumb')} alt="" class="w-full h-full object-cover" />
              {:catch}
                <div class="w-full h-full flex items-center justify-center">
                  <svg class="w-8 h-8 text-[--w30]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16" />
                  </svg>
                </div>
              {/await}
            {:else}
              <div class="w-full h-full flex items-center justify-center">
                <svg class="w-8 h-8 text-[--w30]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16" />
                </svg>
              </div>
            {/if}
          </div>
          <p class="text-sm truncate">{artwork.title}</p>
          <p class="text-xs text-[--w60]">{artwork.year} {artwork.slug ? `• /${artwork.slug}` : ''}</p>
          <div class="absolute top-4 right-4 opacity-0 group-hover:opacity-100 flex gap-1 transition-opacity">
            <a href="/arts/{artwork.slug || artwork._id}" target="_blank" class="p-1 bg-[--w8] rounded hover:bg-[--w12]" aria-label="View">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </a>
            <button onclick={() => editArtwork(artwork)} class="p-1 bg-[--w8] rounded hover:bg-[--w12]" aria-label="Edit">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5" />
              </svg>
            </button>
            <button onclick={() => deleteArtwork(artwork._id)} class="p-1 bg-accent-red/20 rounded hover:bg-accent-red/40" aria-label="Delete">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6" />
              </svg>
            </button>
          </div>
        </div>
      {/each}
    </div>
</div>
