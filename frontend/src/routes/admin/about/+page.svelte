<script>
  import { SEO } from "$lib/components";
  import { canonicalUrl } from "$lib/seo.js";
  import { api } from '$lib/api';
  import { onMount } from 'svelte';
  let { data: pageData } = $props();
  let form = $state({ name: '', location: '', genres: [], bio: '', avatar: '', email: '', liner_notes: '', social_links: {} });
  let genresInput = $state('');
  let saving = $state(false);
  let error = $state('');
  let success = $state('');
  onMount(() => {
    const about = pageData.about;
    form = about ? { ...about, social_links: about.social_links || {} } : { name: '', location: '', genres: [], bio: '', avatar: '', email: '', liner_notes: '', social_links: {} };
    genresInput = (about?.genres || []).join(', ');
  });
  const handleSubmit = async (e) => {
    e.preventDefault(); error = ''; success = ''; saving = true;
    try { const payload = { ...form, genres: genresInput.split(',').map(g => g.trim()).filter(Boolean) }; await api.about.update(payload); success = 'Saved!'; }
    catch (err) { error = err.message; } finally { saving = false; }
  };
</script>
<SEO titleFull="About Admin - TheFoxxStuff" noindex={true} url={canonicalUrl("/admin")} />
<div>
  <h1 class="font-display text-[24px] tracking-wide mb-8">About</h1>
  <form onsubmit={handleSubmit} class="card p-6 space-y-6">
    {#if error}<div class="p-3 bg-accent-red/10 border border-accent-red/50 rounded-lg text-accent-red text-sm">{error}</div>{/if}
    {#if success}<div class="p-3 bg-accent-green/10 border border-accent-green/50 rounded-lg text-accent-green text-sm">{success}</div>{/if}
    <div class="grid grid-cols-2 gap-4">
      <div><label class="label" for="f-name">Name</label><input id="f-name" type="text" bind:value={form.name} class="input" /></div>
      <div><label class="label" for="f-location">Location</label><input id="f-location" type="text" bind:value={form.location} class="input" /></div>
      <div><label class="label" for="f-email">Email</label><input id="f-email" type="email" bind:value={form.email} class="input" /></div>
      <div><label class="label" for="f-avatar">Avatar URL</label><input id="f-avatar" type="text" bind:value={form.avatar} class="input" /></div>
      <div class="col-span-2"><label class="label" for="f-genres">Genres (comma separated)</label><input id="f-genres" type="text" bind:value={genresInput} class="input" /></div>
    </div>
    <div><label class="label" for="f-bio">Bio</label><textarea id="f-bio" bind:value={form.bio} rows="4" class="textarea"></textarea></div>
    <div><label class="label" for="f-liner">Liner Notes</label><textarea id="f-liner" bind:value={form.liner_notes} rows="3" class="textarea"></textarea></div>
    <div>
      <h3 class="font-medium mb-3">Social Links</h3>
      <div class="grid grid-cols-2 gap-4">
        <div><label class="label" for="f-bandcamp">Bandcamp</label><input id="f-bandcamp" type="url" bind:value={form.social_links.bandcamp} class="input" /></div>
        <div><label class="label" for="f-soundcloud">SoundCloud</label><input id="f-soundcloud" type="url" bind:value={form.social_links.soundcloud} class="input" /></div>
        <div><label class="label" for="f-twitter">Twitter</label><input id="f-twitter" type="url" bind:value={form.social_links.twitter} class="input" /></div>
        <div><label class="label" for="f-vk">VK</label><input id="f-vk" type="url" bind:value={form.social_links.vk} class="input" /></div>
        <div><label class="label" for="f-telegram">Telegram</label><input id="f-telegram" type="url" bind:value={form.social_links.telegram} class="input" /></div>
      </div>
    </div>
    <button type="submit" disabled={saving} class="btn btn-primary">{saving ? 'Saving...' : 'Save Changes'}</button>
  </form>
</div>
