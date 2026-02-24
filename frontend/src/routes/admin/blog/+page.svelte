<script>
  import { SEO } from "$lib/components";
  import { canonicalUrl } from "$lib/seo.js";
  import { api, getImageUrl, generateSlug } from '$lib/api';
  import { invalidateAll } from '$app/navigation';
  import { ImageUpload, MarkdownEditor } from '$lib/components';

  let { data: pageData } = $props();
  // $derived — посты всегда в синхронизации с SvelteKit load() после invalidateAll()
  let posts = $derived(pageData.posts);
  let loading = $state(false);
  let showForm = $state(false);
  let editingId = $state(null);
  let form = $state({ 
    title: '', 
    slug: '',
    content: '', 
    excerpt: '', 
    cover_image: '',
    meta_title: '',
    meta_description: '',
    meta_keywords: '',
    og_image: ''
  });
  let coverImageInfo = $state(null);
  let ogImageInfo = $state(null);
  let error = $state('');
  let showSeo = $state(false);
  
  const loadPosts = async () => {
    // invalidateAll перезапускает +page.js load() — посты обновятся через $derived
    await invalidateAll();
  };
  
  const resetForm = () => {
    form = { 
      title: '', 
      slug: '',
      content: '', 
      excerpt: '', 
      cover_image: '',
      meta_title: '',
      meta_description: '',
      meta_keywords: '',
      og_image: ''
    };
    coverImageInfo = null;
    ogImageInfo = null;
    editingId = null;
    showForm = false;
    showSeo = false;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    error = '';
    try {
      // Auto-generate slug if empty
      if (!form.slug) {
        form.slug = generateSlug(form.title);
      }
      if (editingId) await api.blog.update(editingId, form);
      else await api.blog.create(form);
      resetForm();
      await loadPosts();
    } catch (err) {
      error = err.message;
    }
  };
  
  const editPost = async (p) => {
    editingId = p._id;
    form = {
      title: p.title,
      slug: p.slug || '',
      content: p.content,
      excerpt: p.excerpt || '',
      cover_image: p.cover_image || '',
      meta_title: p.meta_title || '',
      meta_description: p.meta_description || '',
      meta_keywords: p.meta_keywords || '',
      og_image: p.og_image || ''
    };
    // Try to load cover image info
    if (p.cover_image) {
      try {
        coverImageInfo = await api.upload.getInfo(p.cover_image);
      } catch {
        coverImageInfo = null;
      }
    }
    if (p.og_image) {
      try {
        ogImageInfo = await api.upload.getInfo(p.og_image);
      } catch {
        ogImageInfo = null;
      }
    }
    showForm = true;
    showSeo = !!(p.meta_title || p.meta_description || p.meta_keywords);
  };
  
  const deletePost = async (id) => {
    if (!confirm('Delete this post?')) return;
    try {
      await api.blog.delete(id);
      await loadPosts();
    } catch (err) {
      alert(err.message);
    }
  };
  
  // Auto-generate slug from title
  function handleTitleChange() {
    if (!editingId && form.title && !form.slug) {
      form.slug = generateSlug(form.title);
    }
  }
</script>

<SEO titleFull="Blog Admin - TheFoxxStuff" noindex={true} url={canonicalUrl("/admin")} />

<div>
  <div class="flex justify-between mb-8">
    <h1 class="font-display text-[24px]">Blog</h1>
    <button onclick={() => { resetForm(); showForm = true; }} class="btn btn-primary">Add Post</button>
  </div>
  
  {#if showForm}
    <div class="card p-6 mb-8">
      <h2 class="font-display text-xl mb-4">{editingId ? 'Edit' : 'New'} Post</h2>
      {#if error}<div class="mb-4 p-3 bg-accent-red/10 border border-accent-red/50 rounded-lg text-accent-red text-sm">{error}</div>{/if}
      
      <form onsubmit={handleSubmit} class="space-y-6">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label" for="fl-title-1">Title</label>
            <input id="fl-title-1" type="text" bind:value={form.title} oninput={handleTitleChange} required class="input" />
          </div>
          <div>
            <label class="label" for="fl-slug-url-2">Slug (URL)</label>
            <div class="flex gap-2">
              <input id="fl-slug-url-2" type="text" bind:value={form.slug} class="input flex-1" placeholder="auto-generated-from-title" />
              <button type="button" onclick={() => form.slug = generateSlug(form.title)} class="btn btn-secondary text-sm">Generate</button>
            </div>
          </div>
        </div>
        
        <ImageUpload 
          label="Cover Image" 
          bind:value={form.cover_image} 
          bind:imageInfo={coverImageInfo}
          category="blog"
          customName={form.title}
        />
        
        <div>
          <label class="label" for="fl-excerpt-3">Excerpt</label>
          <textarea id="fl-excerpt-3" bind:value={form.excerpt} rows="2" class="textarea" placeholder="Brief description for post preview..."></textarea>
        </div>
        
        <div>
          <label class="label">Content (Markdown)</label>
          <MarkdownEditor bind:value={form.content} rows={15} placeholder="Write your blog post in Markdown..." />
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
                <label class="label" for="fl-meta-title-4">Meta Title</label>
                <input id="fl-meta-title-4" type="text" bind:value={form.meta_title} class="input" placeholder="Custom title for search engines" />
                <p class="text-xs text-[--w30] mt-1">Leave empty to use post title</p>
              </div>
              
              <div>
                <label class="label" for="fl-meta-description-5">Meta Description</label>
                <textarea id="fl-meta-description-5" bind:value={form.meta_description} rows="2" class="textarea" placeholder="Description for search engines (150-160 characters recommended)"></textarea>
                {#if form.meta_description}
                  <p class="text-xs text-[--w30] mt-1">{form.meta_description.length}/160 characters</p>
                {/if}
              </div>
              
              <div>
                <label class="label" for="fl-meta-keywords-6">Meta Keywords</label>
                <input id="fl-meta-keywords-6" type="text" bind:value={form.meta_keywords} class="input" placeholder="keyword1, keyword2, keyword3" />
              </div>
              
              <ImageUpload 
                label="Open Graph Image" 
                bind:value={form.og_image} 
                bind:imageInfo={ogImageInfo}
                category="blog"
                customName={form.title ? `${form.title}-og` : null}
              />
              <p class="text-xs text-[--w30] -mt-2">Image shown when sharing on social media (1200x630 recommended)</p>
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
  
    <div class="space-y-2">
      {#each posts as post}
        <div class="card p-4 flex justify-between items-center">
          <div class="flex items-center gap-4">
            <div class="w-16 h-12 bg-[--w8] rounded-lg flex items-center justify-center overflow-hidden">
              {#if post.cover_image}
                {#await api.upload.getInfo(post.cover_image) then imgInfo}
                  <img src={getImageUrl(imgInfo, 'thumb')} alt="" class="w-full h-full object-cover" />
                {:catch}
                  <svg class="w-6 h-6 text-[--w30]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1" />
                  </svg>
                {/await}
              {:else}
                <svg class="w-6 h-6 text-[--w30]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1" />
                </svg>
              {/if}
            </div>
            <div>
              <h3 class="font-medium">{post.title}</h3>
              <p class="text-sm text-[--w60]">
                {#if post.slug}<span class="text-accent-green">/blog/{post.slug}</span> • {/if}
                {new Date(post.created_at).toLocaleDateString()} • {post.views} views
              </p>
            </div>
          </div>
          <div class="flex gap-2">
            <a href="/blog/{post.slug || post._id}" target="_blank" class="btn btn-secondary text-sm">View</a>
            <button onclick={() => editPost(post)} class="btn btn-secondary text-sm">Edit</button>
            <button onclick={() => deletePost(post._id)} class="btn btn-danger text-sm">Delete</button>
          </div>
        </div>
      {/each}
    </div>
</div>
