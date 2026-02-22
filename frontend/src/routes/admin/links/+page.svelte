<script>
  import { api } from '$lib/api';
  let { data: pageData } = $props();
  let links = $state(pageData.links);
  let loading = $state(false);
  let showForm = $state(false);
  let editingId = $state(null);
  let form = $state({ title: '', url: '', icon: '', order: 0 });
  let error = $state('');
  const loadLinks = async () => { try { links = await api.links.list(); } catch (e) { console.error(e); } };
  const resetForm = () => { form = { title: '', url: '', icon: '', order: 0 }; editingId = null; showForm = false; };
  const handleSubmit = async (e) => {
    e.preventDefault(); error = '';
    try { const data = { ...form, order: parseInt(form.order) }; if (editingId) await api.links.update(editingId, data); else await api.links.create(data); resetForm(); loadLinks(); }
    catch (err) { error = err.message; }
  };
  const editLink = (l) => { editingId = l._id; form = { title: l.title, url: l.url, icon: l.icon || '', order: l.order }; showForm = true; };
  const deleteLink = async (id) => { if (!confirm('Delete?')) return; try { await api.links.delete(id); loadLinks(); } catch (err) { alert(err.message); } };
</script>
<svelte:head><title>Links Admin - TheFoxxStuff</title></svelte:head>
<div>
  <div class="flex justify-between mb-8"><h1 class="font-display text-[24px]">Links</h1><button onclick={() => { resetForm(); showForm = true; }} class="btn btn-primary">Add Link</button></div>
  {#if showForm}
    <div class="card p-6 mb-8">
      <h2 class="font-display text-xl mb-4">{editingId ? 'Edit' : 'New'} Link</h2>
      {#if error}<div class="mb-4 p-3 bg-accent-red/10 border border-accent-red/50 rounded-lg text-accent-red text-sm">{error}</div>{/if}
      <form onsubmit={handleSubmit} class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div><label class="label">Title</label><input type="text" bind:value={form.title} required class="input" /></div>
          <div><label class="label">URL</label><input type="url" bind:value={form.url} required class="input" /></div>
          <div><label class="label">Icon (bandcamp, soundcloud, twitter, vk, telegram)</label><input type="text" bind:value={form.icon} class="input" /></div>
          <div><label class="label">Order</label><input type="number" bind:value={form.order} class="input" /></div>
        </div>
        <div class="flex gap-2"><button type="submit" class="btn btn-primary">{editingId ? 'Update' : 'Create'}</button><button type="button" onclick={resetForm} class="btn btn-secondary">Cancel</button></div>
      </form>
    </div>
  {/if}
  <div class="space-y-2">{#each links as link}
    <div class="card p-4 flex justify-between items-center">
      <div><h3 class="font-medium">{link.title}</h3><p class="text-sm text-[--w60]">{link.url}</p></div>
      <div class="flex gap-2"><button onclick={() => editLink(link)} class="btn btn-secondary text-sm">Edit</button><button onclick={() => deleteLink(link._id)} class="btn btn-danger text-sm">Delete</button></div>
    </div>
  {/each}</div>
</div>
