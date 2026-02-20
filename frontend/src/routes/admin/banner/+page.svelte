<script>
  import { onMount } from 'svelte';
  import { api, getImageUrl } from '$lib/api';
  import { ImageUpload } from '$lib/components';
  
  let banner = $state({ slides: [] });
  let loading = $state(true);
  let showForm = $state(false);
  let editingIndex = $state(-1);
  let form = $state({ title: '', image: '', link: '' });
  let imageInfo = $state(null);
  let error = $state('');
  let saving = $state(false);
  
  const loadBanner = async () => {
    loading = true;
    try {
      banner = await api.banner.get();
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  };
  
  onMount(loadBanner);
  
  const resetForm = () => {
    form = { title: '', image: '', link: '' };
    imageInfo = null;
    editingIndex = -1;
    showForm = false;
    error = '';
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.image) {
      error = 'Please upload an image';
      return;
    }
    
    saving = true;
    error = '';
    
    try {
      let slides = [...banner.slides];
      const slideData = { title: form.title, image: form.image, link: form.link || null };
      
      if (editingIndex >= 0) {
        slides[editingIndex] = { ...slides[editingIndex], ...slideData };
      } else {
        slides.push({ ...slideData, order: slides.length, id: Date.now().toString() });
      }
      
      await api.banner.update({ slides });
      await loadBanner();
      resetForm();
    } catch (err) {
      error = err.message;
    } finally {
      saving = false;
    }
  };
  
  const editSlide = async (index) => {
    const slide = banner.slides[index];
    editingIndex = index;
    form = {
      title: slide.title,
      image: slide.image,
      link: slide.link || ''
    };
    // Load image info
    try {
      imageInfo = await api.upload.getInfo(slide.image);
    } catch {
      imageInfo = null;
    }
    showForm = true;
  };
  
  const deleteSlide = async (index) => {
    if (!confirm('Delete this slide?')) return;
    try {
      const slides = banner.slides.filter((_, i) => i !== index);
      await api.banner.update({ slides });
      await loadBanner();
    } catch (err) {
      alert(err.message);
    }
  };
  
  const moveSlide = async (fromIndex, toIndex) => {
    if (toIndex < 0 || toIndex >= banner.slides.length) return;
    const slides = [...banner.slides];
    [slides[fromIndex], slides[toIndex]] = [slides[toIndex], slides[fromIndex]];
    // Update order
    slides.forEach((s, i) => s.order = i);
    try {
      await api.banner.update({ slides });
      await loadBanner();
    } catch (err) {
      alert(err.message);
    }
  };
</script>

<svelte:head><title>Banner Admin - TheFoxxStuff</title></svelte:head>

<div>
  <div class="flex justify-between mb-8">
    <h1 class="font-display text-3xl">Banner Slider</h1>
    <button onclick={() => { resetForm(); showForm = true; }} class="btn btn-primary">Add Slide</button>
  </div>
  
  {#if showForm}
    <div class="card p-6 mb-8">
      <h2 class="font-display text-xl mb-4">{editingIndex >= 0 ? 'Edit' : 'New'} Slide</h2>
      {#if error}<div class="mb-4 p-3 bg-accent-red/10 border border-accent-red/50 rounded-lg text-accent-red text-sm">{error}</div>{/if}
      
      <form onsubmit={handleSubmit} class="space-y-6">
        <div>
          <label class="label">Title</label>
          <input type="text" bind:value={form.title} required class="input" placeholder="Slide title" />
        </div>
        
        <ImageUpload 
          label="Banner Image (recommended: 1920x600)" 
          bind:value={form.image} 
          bind:imageInfo={imageInfo}
        />
        
        <div>
          <label class="label">Link (optional)</label>
          <input type="text" bind:value={form.link} class="input" placeholder="/music/release-id" />
        </div>
        
        <div class="flex gap-2">
          <button type="submit" disabled={saving} class="btn btn-primary">
            {saving ? 'Saving...' : (editingIndex >= 0 ? 'Update' : 'Add')}
          </button>
          <button type="button" onclick={resetForm} class="btn btn-secondary">Cancel</button>
        </div>
      </form>
    </div>
  {/if}
  
  {#if loading}
    <div class="space-y-4">
      {#each Array(3) as _}
        <div class="h-32 bg-[--w8] rounded-xl animate-pulse"></div>
      {/each}
    </div>
  {:else if banner.slides.length === 0}
    <div class="card p-12 text-center">
      <svg class="w-16 h-16 mx-auto text-[--w30] mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14" />
      </svg>
      <p class="text-[--w60]">No banner slides yet. Add your first slide!</p>
    </div>
  {:else}
    <div class="space-y-3">
      {#each banner.slides as slide, i}
        <div class="card p-4 flex items-center gap-4">
          <div class="flex flex-col gap-1">
            <button onclick={() => moveSlide(i, i - 1)} disabled={i === 0} class="p-1 hover:bg-[--w12] rounded disabled:opacity-30">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" /></svg>
            </button>
            <button onclick={() => moveSlide(i, i + 1)} disabled={i === banner.slides.length - 1} class="p-1 hover:bg-[--w12] rounded disabled:opacity-30">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
            </button>
          </div>
          
          <div class="w-48 h-24 bg-[--w8] rounded-lg overflow-hidden flex-shrink-0">
            {#await api.upload.getInfo(slide.image) then imgInfo}
              <img src={getImageUrl(imgInfo, 'medium')} alt="" class="w-full h-full object-cover" />
            {:catch}
              <div class="w-full h-full flex items-center justify-center text-[--w30]">No image</div>
            {/await}
          </div>
          
          <div class="flex-1">
            <h3 class="font-medium">{slide.title || 'Untitled'}</h3>
            {#if slide.link}
              <p class="text-sm text-[--w60]">Link: {slide.link}</p>
            {/if}
          </div>
          
          <div class="flex gap-2">
            <button onclick={() => editSlide(i)} class="btn btn-secondary text-sm">Edit</button>
            <button onclick={() => deleteSlide(i)} class="btn btn-danger text-sm">Delete</button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
