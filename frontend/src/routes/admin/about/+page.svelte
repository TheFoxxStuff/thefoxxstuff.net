<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  let form = $state({ name: '', location: '', genres: [], bio: '', avatar: '', email: '', liner_notes: '', social_links: {} });
  let genresInput = $state('');
  let loading = $state(true);
  let saving = $state(false);
  let error = $state('');
  let success = $state('');
  onMount(async () => {
    try { const about = await api.about.get(); form = { ...about, social_links: about.social_links || {} }; genresInput = (about.genres || []).join(', '); }
    catch (e) { console.error(e); } finally { loading = false; }
  });
  const handleSubmit = async (e) => {
    e.preventDefault(); error = ''; success = ''; saving = true;
    try { const data = { ...form, genres: genresInput.split(',').map(g => g.trim()).filter(Boolean) }; await api.about.update(data); success = 'Saved!'; }
    catch (err) { error = err.message; } finally { saving = false; }
  };
</script>
<svelte:head><title>About Admin - TheFoxxStuff</title></svelte:head>
<div>
  <h1 class="font-display text-3xl tracking-wide mb-8">About</h1>
  {#if loading}<div class="card p-6 animate-pulse"><div class="space-y-4">{#each Array(6) as _}<div class="h-10 bg-[--w8] rounded"></div>{/each}</div></div>
  {:else}
    <form onsubmit={handleSubmit} class="card p-6 space-y-6">
      {#if error}<div class="p-3 bg-accent-red/10 border border-accent-red/50 rounded-lg text-accent-red text-sm">{error}</div>{/if}
      {#if success}<div class="p-3 bg-accent-green/10 border border-accent-green/50 rounded-lg text-accent-green text-sm">{success}</div>{/if}
      <div class="grid grid-cols-2 gap-4">
        <div><label class="label">Name</label><input type="text" bind:value={form.name} class="input" /></div>
        <div><label class="label">Location</label><input type="text" bind:value={form.location} class="input" /></div>
        <div><label class="label">Email</label><input type="email" bind:value={form.email} class="input" /></div>
        <div><label class="label">Avatar URL</label><input type="text" bind:value={form.avatar} class="input" /></div>
        <div class="col-span-2"><label class="label">Genres (comma separated)</label><input type="text" bind:value={genresInput} class="input" /></div>
      </div>
      <div><label class="label">Bio</label><textarea bind:value={form.bio} rows="4" class="textarea"></textarea></div>
      <div><label class="label">Liner Notes</label><textarea bind:value={form.liner_notes} rows="3" class="textarea"></textarea></div>
      <div>
        <h3 class="font-medium mb-3">Social Links</h3>
        <div class="grid grid-cols-2 gap-4">
          <div><label class="label">Bandcamp</label><input type="url" bind:value={form.social_links.bandcamp} class="input" /></div>
          <div><label class="label">SoundCloud</label><input type="url" bind:value={form.social_links.soundcloud} class="input" /></div>
          <div><label class="label">Twitter</label><input type="url" bind:value={form.social_links.twitter} class="input" /></div>
          <div><label class="label">VK</label><input type="url" bind:value={form.social_links.vk} class="input" /></div>
          <div><label class="label">Telegram</label><input type="url" bind:value={form.social_links.telegram} class="input" /></div>
        </div>
      </div>
      <button type="submit" disabled={saving} class="btn btn-primary">{saving ? 'Saving...' : 'Save Changes'}</button>
    </form>
  {/if}
</div>
