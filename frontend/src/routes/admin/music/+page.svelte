<script>
  import { api, getImageUrl, generateSlug } from '$lib/api';
  import { ImageUpload, MarkdownEditor } from '$lib/components';

  let { data } = $props();
  let releases = $state(data.releases);
  let loading = $state(false);
  let showForm = $state(false);
  let editingId = $state(null);
  let form = $state({
    title: '',
    slug: '',
    release_date: '',
    genre: '',
    release_type: 'Album',
    price: 'Name your price',
    is_new: false,
    description: '',
    cover_image: '',
    bandcamp_url: '',
    production_notes: '',
    liner_notes: '',
    download_mp3: '',
    download_flac: '',
    tracks: [],
    gallery: [],
    meta_title: '',
    meta_description: '',
    meta_keywords: '',
    og_image: ''
  });
  let coverImageInfo = $state(null);
  let galleryImages = $state([]);
  let ogImageInfo = $state(null);
  let error = $state('');
  let showSeo = $state(false);
  
  // Gallery upload
  let galleryFileInput = $state(null);
  let uploadingGallery = $state(false);
  
  // Audio upload tracking
  let uploadingAudioIndex = $state(-1);
  
  const loadReleases = async () => {
    try {
      releases = (await api.music.list(1, 100)).items;
    } catch (e) {
      console.error(e);
    }
  };
  
  const resetForm = () => {
    form = {
      title: '',
      slug: '',
      release_date: '',
      genre: '',
      release_type: 'Album',
      price: 'Name your price',
      is_new: false,
      description: '',
      cover_image: '',
      bandcamp_url: '',
      production_notes: '',
      liner_notes: '',
      download_mp3: '',
      download_flac: '',
      tracks: [],
      gallery: [],
      meta_title: '',
      meta_description: '',
      meta_keywords: '',
      og_image: ''
    };
    coverImageInfo = null;
    galleryImages = [];
    ogImageInfo = null;
    editingId = null;
    showForm = false;
    showSeo = false;
  };

  let metadataWriting = $state(false);
  let metadataResult = $state('');

  const writeAllMetadata = async () => {
    if (!editingId || !form.tracks?.length) {
      metadataResult = 'Save the release first, then write metadata.';
      return;
    }
    metadataWriting = true;
    metadataResult = '';
    const year = form.release_date ? new Date(form.release_date).getFullYear().toString() : '';
    let successCount = 0;
    let errorCount = 0;

    for (let i = 0; i < form.tracks.length; i++) {
      const track = form.tracks[i];
      const paths = {};
      if (track.audio_original) paths.original_path = track.audio_original;
      if (track.audio_mp3_320) paths.mp3_320_path = track.audio_mp3_320;
      if (track.audio_mp3_128) paths.mp3_128_path = track.audio_mp3_128;
      if (track.audio_opus) paths.opus_path = track.audio_opus;

      if (Object.keys(paths).length === 0) continue;

      try {
        await api.upload.writeMetadata({
          track_paths: paths,
          title: track.title,
          artist: 'TheFoxxStuff',
          album_artist: 'TheFoxxStuff',
          album: form.title,
          year: year,
          track_number: i + 1,
          genre: form.genre || '',
          comment: form.production_notes || '',
          cover_image_id: form.cover_image || null,
          publisher: 'TheFoxxStuff',
          copyright: 'TheFoxxStuff',
          url: 'https://thefoxxstuff.net'
        });
        successCount++;
      } catch (e) {
        errorCount++;
        console.error(`Metadata error for track ${i + 1}:`, e);
      }
    }
    metadataWriting = false;
    metadataResult = `Done! ${successCount} track(s) tagged${errorCount > 0 ? `, ${errorCount} error(s)` : ''}.`;
    setTimeout(() => { metadataResult = ''; }, 5000);
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    error = '';
    try {
      const data = {
        ...form,
        release_date: new Date(form.release_date).toISOString(),
        tracks: form.tracks.map((t, i) => ({
          number: i + 1,
          title: t.title,
          duration: t.duration || '00:00',
          audio_original: t.audio_original || null,
          audio_mp3_320: t.audio_mp3_320 || null,
          audio_mp3_128: t.audio_mp3_128 || null,
          audio_opus: t.audio_opus || null,
          has_mp3_128: t.has_mp3_128 || false
        }))
      };
      if (!data.slug) {
        data.slug = generateSlug(data.title);
      }
      if (editingId) await api.music.update(editingId, data);
      else await api.music.create(data);
      resetForm();
      loadReleases();
    } catch (err) {
      error = err.message;
    }
  };
  
  const editRelease = async (r) => {
    editingId = r._id;
    form = {
      ...r,
      slug: r.slug || '',
      release_date: r.release_date.split('T')[0],
      tracks: (r.tracks || []).map(t => ({
        ...t,
        audio_original: t.audio_original || null,
        audio_mp3_320: t.audio_mp3_320 || null,
        audio_mp3_128: t.audio_mp3_128 || null,
        audio_opus: t.audio_opus || null,
        has_mp3_128: t.has_mp3_128 || false
      })),
      gallery: r.gallery || [],
      meta_title: r.meta_title || '',
      meta_description: r.meta_description || '',
      meta_keywords: r.meta_keywords || '',
      og_image: r.og_image || ''
    };
    coverImageInfo = r.cover_image_info || null;
    galleryImages = r.gallery_images || [];
    if (r.og_image) {
      try {
        ogImageInfo = await api.upload.getInfo(r.og_image);
      } catch {
        ogImageInfo = null;
      }
    }
    showForm = true;
    showSeo = !!(r.meta_title || r.meta_description || r.meta_keywords);
  };
  
  const deleteRelease = async (id) => {
    if (!confirm('Delete this release?')) return;
    try {
      await api.music.delete(id);
      loadReleases();
    } catch (err) {
      alert(err.message);
    }
  };
  
  // Track management
  const addTrack = () => {
    form.tracks = [...form.tracks, {
      number: form.tracks.length + 1,
      title: '',
      duration: '00:00',
      audio_original: null,
      audio_mp3_320: null,
      audio_mp3_128: null,
      audio_opus: null,
      has_mp3_128: false
    }];
  };
  
  const removeTrack = (index) => {
    form.tracks = form.tracks.filter((_, i) => i !== index);
  };
  
  const moveTrack = (fromIndex, toIndex) => {
    if (toIndex < 0 || toIndex >= form.tracks.length) return;
    const newTracks = [...form.tracks];
    [newTracks[fromIndex], newTracks[toIndex]] = [newTracks[toIndex], newTracks[fromIndex]];
    form.tracks = newTracks;
  };
  
  // Audio upload for a track
  async function handleAudioUpload(e, trackIndex) {
    const file = e.target.files?.[0];
    if (!file) return;
    
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['flac', 'mp3'].includes(ext)) {
      alert('Only FLAC and MP3 files are allowed');
      e.target.value = '';
      return;
    }
    
    uploadingAudioIndex = trackIndex;
    try {
      const track = form.tracks[trackIndex];
      const customName = track.title || `track_${trackIndex + 1}`;
      const result = await api.upload.audio(file, customName, track.has_mp3_128);
      
      form.tracks[trackIndex] = {
        ...form.tracks[trackIndex],
        duration: result.duration || form.tracks[trackIndex].duration,
        audio_original: result.original_path || null,
        audio_mp3_320: result.mp3_320_path || null,
        audio_mp3_128: result.mp3_128_path || null,
        audio_opus: result.opus_path || null,
        _audio_id: result._id
      };
      form.tracks = [...form.tracks];
    } catch (err) {
      alert('Audio upload failed: ' + err.message);
    } finally {
      uploadingAudioIndex = -1;
      e.target.value = '';
    }
  }
  
  // Toggle MP3 128 for a track
  async function toggleMp3128(trackIndex) {
    const track = form.tracks[trackIndex];
    const newValue = !track.has_mp3_128;
    form.tracks[trackIndex].has_mp3_128 = newValue;
    
    if (track._audio_id) {
      try {
        const result = await api.upload.audioToggleMp3128(track._audio_id, newValue);
        form.tracks[trackIndex].audio_mp3_128 = result.mp3_128_path || null;
        form.tracks = [...form.tracks];
      } catch (err) {
        console.error('Toggle MP3 128 failed:', err);
      }
    }
  }
  
  // Remove audio from track
  async function removeAudio(trackIndex) {
    const track = form.tracks[trackIndex];
    if (track._audio_id) {
      try {
        await api.upload.audioDelete(track._audio_id);
      } catch (err) {
        console.error('Audio delete failed:', err);
      }
    }
    form.tracks[trackIndex] = {
      ...form.tracks[trackIndex],
      audio_original: null,
      audio_mp3_320: null,
      audio_mp3_128: null,
      audio_opus: null,
      _audio_id: null
    };
    form.tracks = [...form.tracks];
  }
  
  // Gallery management
  async function handleGalleryUpload(e) {
    const files = e.target.files;
    if (!files?.length) return;
    
    uploadingGallery = true;
    try {
      for (const file of files) {
        const result = await api.upload.image(file, 'music', null, editingId, true);
        const galleryItem = {
          image_id: result._id,
          name: file.name.replace(/\.[^/.]+$/, '')
        };
        form.gallery = [...form.gallery, galleryItem];
        galleryImages = [...galleryImages, { ...result, gallery_name: galleryItem.name }];
      }
    } catch (err) {
      console.error(err);
      alert('Failed to upload some images');
    } finally {
      uploadingGallery = false;
      if (galleryFileInput) galleryFileInput.value = '';
    }
  }
  
  function removeGalleryImage(index) {
    form.gallery = form.gallery.filter((_, i) => i !== index);
    galleryImages = galleryImages.filter((_, i) => i !== index);
  }
  
  function updateGalleryName(index, name) {
    form.gallery[index].name = name;
    galleryImages[index].gallery_name = name;
  }
  
  function handleTitleChange() {
    if (!editingId && form.title && !form.slug) {
      form.slug = generateSlug(form.title);
    }
  }
</script>

<svelte:head><title>Music Admin - TheFoxxStuff</title></svelte:head>

<div>
  <div class="flex justify-between mb-8">
    <h1 class="font-display text-[24px]">Music</h1>
    <button onclick={() => { resetForm(); showForm = true; }} class="btn btn-primary">Add Release</button>
  </div>
  
  {#if showForm}
    <div class="card p-6 mb-8">
      <h2 class="font-display text-xl mb-4">{editingId ? 'Edit' : 'New'} Release</h2>
      {#if error}<div class="mb-4 p-3 bg-accent-red/10 border border-accent-red/50 rounded-lg text-accent-red text-sm">{error}</div>{/if}
      
      <form onsubmit={handleSubmit} class="space-y-6">
        <!-- Basic Info -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label" for="title">Title</label>
            <input type="text" bind:value={form.title} oninput={handleTitleChange} required class="input" />
          </div>
          <div>
            <label class="label" for="slug">Slug (URL)</label>
            <div class="flex gap-2">
              <input type="text" bind:value={form.slug} class="input flex-1" placeholder="auto-generated" />
              <button type="button" onclick={() => form.slug = generateSlug(form.title)} class="btn btn-secondary text-sm">Gen</button>
            </div>
          </div>
          <div>
            <label class="label" for="release_date">Release Date</label>
            <input type="date" bind:value={form.release_date} required class="input" />
          </div>
          <div>
            <label class="label" for="genre">Genre</label>
            <input type="text" bind:value={form.genre} required class="input" />
          </div>
          <div>
            <label class="label" for="release_type">Type</label>
            <select bind:value={form.release_type} class="input">
              <option>Album</option>
              <option>EP</option>
              <option>Single</option>
            </select>
          </div>
          <div>
            <label class="label" for="price">Price</label>
            <input type="text" bind:value={form.price} class="input" />
          </div>
          <div>
            <label class="label" for="bandcamp_url">Bandcamp URL</label>
            <input type="text" bind:value={form.bandcamp_url} class="input" />
          </div>
          <div>
            <label class="label" for="download_mp3">Download MP3 URL</label>
            <input type="text" bind:value={form.download_mp3} class="input" />
          </div>
          <div>
            <label class="label" for="download_flac">Download FLAC URL</label>
            <input type="text" bind:value={form.download_flac} class="input" />
          </div>
          <div class="flex items-center gap-2">
            <input type="checkbox" id="is_new" bind:checked={form.is_new} class="rounded" />
            <label for="is_new">Featured (New Release)</label>
          </div>
        </div>
        
        <!-- Cover Image -->
        <ImageUpload 
          label="Cover Image" 
          bind:value={form.cover_image} 
          bind:imageInfo={coverImageInfo}
          category="music"
          customName={form.title}
        />
        
        <!-- Description (Markdown) -->
        <div>
          <span class="label">Description (Markdown)</span>
          <MarkdownEditor bind:value={form.description} rows={4} placeholder="Describe your release..." />
        </div>
        
        <!-- Track List with Audio Upload -->
        <div>
          <div class="flex justify-between items-center mb-3">
            <label class="label mb-0">Track List</label>
            <button type="button" onclick={addTrack} class="btn btn-secondary text-sm">+ Add Track</button>
          </div>
          {#if form.tracks.length > 0}
            <div class="space-y-3">
              {#each form.tracks as track, i}
                <div class="p-4 bg-[--w8] rounded-lg space-y-3">
                  <!-- Track info row -->
                  <div class="flex items-center gap-3">
                    <span class="text-[--w30] w-6 text-sm">{i + 1}.</span>
                    <input type="text" bind:value={track.title} placeholder="Track title" class="input flex-1" />
                    <input type="text" bind:value={track.duration} placeholder="00:00" class="input w-20 text-center" />
                    <div class="flex gap-1">
                      <button type="button" onclick={() => moveTrack(i, i - 1)} disabled={i === 0} class="p-1 hover:bg-[--w12] rounded disabled:opacity-30">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" /></svg>
                      </button>
                      <button type="button" onclick={() => moveTrack(i, i + 1)} disabled={i === form.tracks.length - 1} class="p-1 hover:bg-[--w12] rounded disabled:opacity-30">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
                      </button>
                      <button type="button" onclick={() => removeTrack(i)} class="p-1 hover:bg-accent-red/50 rounded">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                      </button>
                    </div>
                  </div>
                  
                  <!-- Audio upload row -->
                  <div class="flex items-center gap-3 pl-9">
                    {#if track.audio_opus}
                      <!-- Audio uploaded -->
                      <div class="flex items-center gap-2 flex-1">
                        <svg class="w-4 h-4 text-accent-green flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                        <span class="text-sm text-dark-300 truncate">Audio uploaded</span>
                        <div class="flex items-center gap-1 text-xs text-[--w30]">
                          {#if track.audio_mp3_320}<span class="px-1.5 py-0.5 bg-[--w12] rounded">MP3 320</span>{/if}
                          {#if track.audio_mp3_128}<span class="px-1.5 py-0.5 bg-[--w12] rounded">MP3 128</span>{/if}
                          {#if track.audio_opus}<span class="px-1.5 py-0.5 bg-accent-green/20 text-accent-green rounded">Opus</span>{/if}
                        </div>
                        <button type="button" onclick={() => removeAudio(i)} class="text-xs text-accent-red hover:underline ml-2">Remove</button>
                      </div>
                    {:else}
                      <!-- Upload input -->
                      <label class="flex items-center gap-2 cursor-pointer flex-1">
                        <div class="btn btn-secondary text-xs py-1 px-3">
                          {#if uploadingAudioIndex === i}
                            <svg class="w-3 h-3 animate-spin inline mr-1" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" /><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                            Uploading & Converting...
                          {:else}
                            <svg class="w-3 h-3 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                            Upload FLAC / MP3
                          {/if}
                        </div>
                        <input 
                          type="file" 
                          accept=".flac,.mp3" 
                          class="hidden" 
                          onchange={(e) => handleAudioUpload(e, i)}
                          disabled={uploadingAudioIndex >= 0}
                        />
                        <span class="text-xs text-[--w30]">→ MP3 320kbps + Opus 128kbps</span>
                      </label>
                    {/if}
                    
                    <!-- MP3 128 checkbox -->
                    <div class="flex items-center gap-1.5 flex-shrink-0">
                      <input 
                        type="checkbox" 
                        id="mp3_128_{i}" 
                        checked={track.has_mp3_128}
                        onchange={() => toggleMp3128(i)}
                        class="rounded"
                      />
                      <label for="mp3_128_{i}" class="text-xs text-[--w60]">MP3 128kbps</label>
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          {:else}
            <p class="text-[--w30] text-sm">No tracks added yet.</p>
          {/if}
        </div>
        
        <!-- Gallery with naming -->
        <div>
          <div class="flex justify-between items-center mb-3">
            <label class="label mb-0">Gallery</label>
            <label class="btn btn-secondary text-sm cursor-pointer">
              {uploadingGallery ? 'Uploading...' : '+ Add Images'}
              <input 
                type="file" 
                accept="image/*" 
                multiple 
                class="hidden" 
                bind:this={galleryFileInput}
                onchange={handleGalleryUpload}
                disabled={uploadingGallery}
              />
            </label>
          </div>
          
          {#if galleryImages.length > 0}
            <div class="grid grid-cols-4 gap-3">
              {#each galleryImages as img, i}
                <div class="relative group">
                  <div class="aspect-square bg-[--w8] rounded-lg overflow-hidden">
                    <img src={getImageUrl(img, 'thumb')} alt="" class="w-full h-full object-cover" />
                  </div>
                  <input 
                    type="text" 
                    value={form.gallery[i]?.name || ''} 
                    oninput={(e) => updateGalleryName(i, e.target.value)}
                    placeholder="Image name"
                    class="mt-1 w-full text-xs input p-1"
                  />
                  <button 
                    type="button" 
                    onclick={() => removeGalleryImage(i)}
                    class="absolute top-1 right-1 p-1 bg-accent-red/80 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              {/each}
            </div>
          {:else}
            <p class="text-[--w30] text-sm">No gallery images added yet.</p>
          {/if}
        </div>
        
        <!-- Notes (Markdown) -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <span class="label">Production Notes (Markdown)</span>
            <MarkdownEditor bind:value={form.production_notes} rows={4} placeholder="Production notes..." />
          </div>
          <div>
            <span class="label">Liner Notes (Markdown)</span>
            <MarkdownEditor bind:value={form.liner_notes} rows={4} placeholder="Liner notes..." />
          </div>
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
                <label class="label" for="meta_title">Meta Title</label>
                <input type="text" bind:value={form.meta_title} class="input" placeholder="Custom title for search engines" />
              </div>
              <div>
                <label class="label" for="meta_description">Meta Description</label>
                <textarea bind:value={form.meta_description} rows="2" class="textarea" placeholder="Description for search engines"></textarea>
              </div>
              <div>
                <label class="label" for="meta_keywords">Meta Keywords</label>
                <input type="text" bind:value={form.meta_keywords} class="input" placeholder="keyword1, keyword2, keyword3" />
              </div>
              <ImageUpload 
                label="Open Graph Image" 
                bind:value={form.og_image} 
                bind:imageInfo={ogImageInfo}
                category="music"
                customName={form.title ? `${form.title}-og` : null}
              />
            </div>
          {/if}
        </div>
        
        <div class="flex gap-2 items-center flex-wrap">
          <button type="submit" class="btn btn-primary">{editingId ? 'Update' : 'Create'}</button>
          {#if editingId}
            <button
              type="button"
              onclick={writeAllMetadata}
              disabled={metadataWriting}
              class="btn btn-secondary"
            >
              {metadataWriting ? 'Writing...' : '🏷️ Write Metadata'}
            </button>
          {/if}
          <button type="button" onclick={resetForm} class="btn btn-secondary">Cancel</button>
          {#if metadataResult}
            <span class="text-sm text-accent-green">{metadataResult}</span>
          {/if}
        </div>
      </form>
    </div>
  {/if}
  
    <div class="space-y-2">
      {#each releases as release}
        <div class="card p-4 flex justify-between items-center">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-[--w8] rounded-lg flex items-center justify-center overflow-hidden">
              {#if release.cover_image_info}
                <img src={getImageUrl(release.cover_image_info, 'thumb')} alt="" class="w-full h-full object-cover" />
              {:else}
                <svg class="w-6 h-6 text-[--w30]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 19V6l12-3v13" />
                </svg>
              {/if}
            </div>
            <div>
              <h3 class="font-medium">{release.title}</h3>
              <p class="text-sm text-[--w60]">
                {#if release.slug}<span class="text-accent-green">/music/{release.slug}</span> • {/if}
                {release.genre} • {release.release_type} • {release.tracks?.length || 0} tracks
                {#if release.tracks?.some(t => t.audio_opus)}
                  • <span class="text-accent-green">♪ audio</span>
                {/if}
              </p>
            </div>
            {#if release.is_new}
              <span class="px-2 py-1 text-xs bg-accent-green text-dark-950 rounded">FEATURED</span>
            {/if}
          </div>
          <div class="flex gap-2">
            <a href="/music/{release.slug || release._id}" target="_blank" class="btn btn-secondary text-sm">View</a>
            <button onclick={() => editRelease(release)} class="btn btn-secondary text-sm">Edit</button>
            <button onclick={() => deleteRelease(release._id)} class="btn btn-danger text-sm">Delete</button>
          </div>
        </div>
      {/each}
    </div>
</div>
