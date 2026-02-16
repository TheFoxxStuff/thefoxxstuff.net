<script>
  import { onMount } from 'svelte';
  import { api, API_BASE } from '$lib/api';
  import { auth, isAdmin } from '$lib/stores/auth.js';
  import { goto } from '$app/navigation';
  import { Camera, Save, Trash2, User, X, Check, ZoomIn, ZoomOut, Move, Shield, ExternalLink } from 'lucide-svelte';

  let profile = $state(null);
  let loading = $state(true);
  let saving = $state(false);
  let error = $state('');
  let success = $state('');
  let displayName = $state('');
  let bio = $state('');

  let avatarFile = $state(null);
  let avatarPreview = $state(null);
  let showCropper = $state(false);
  let imgNW = $state(0);
  let imgNH = $state(0);
  const V = 280;
  let scale = $state(1);
  let panX = $state(0);
  let panY = $state(0);
  let dragging = $state(false);
  let dsx = 0, dsy = 0, dpx = 0, dpy = 0;
  let uploadingAvatar = $state(false);
  let bioWords = $derived(bio.trim() ? bio.trim().split(/\s+/).length : 0);

  function avUrl(p) { return p ? `${API_BASE}/upload/file/${p}` : null; }

  onMount(async () => {
    if (!$auth.user) { goto('/auth/login'); return; }
    try { profile = await api.profile.me(); displayName = profile.display_name || ''; bio = profile.bio || ''; }
    catch (e) { error = e.message; } finally { loading = false; }
  });

  async function saveProfile() {
    saving = true; error = ''; success = '';
    try {
      profile = await api.profile.update({ display_name: displayName, bio });
      auth.updateUser({ display_name: displayName });
      success = 'Saved!'; setTimeout(() => success = '', 3000);
    } catch (e) { error = e.message; } finally { saving = false; }
  }

  function handleFile(e) {
    const f = e.target.files?.[0]; if (!f) return;
    if (f.size > 5*1024*1024) { error = 'Max 5MB'; return; }
    avatarFile = f;
    const r = new FileReader();
    r.onload = (ev) => {
      avatarPreview = ev.target.result; showCropper = true;
      const img = new window.Image();
      img.onload = () => { imgNW = img.naturalWidth; imgNH = img.naturalHeight; scale = V / Math.min(imgNW, imgNH); panX = 0; panY = 0; };
      img.src = ev.target.result;
    };
    r.readAsDataURL(f);
  }

  function closeCrop() { showCropper = false; avatarFile = null; avatarPreview = null; }

  function clamp() {
    const iw = imgNW * scale, ih = imgNH * scale;
    const mx = Math.max(0, (iw - V) / 2), my = Math.max(0, (ih - V) / 2);
    panX = Math.max(-mx, Math.min(mx, panX));
    panY = Math.max(-my, Math.min(my, panY));
  }

  function zoomIn() { scale = Math.min(scale * 1.15, V / Math.min(imgNW, imgNH) * 5); clamp(); }
  function zoomOut() { scale = Math.max(scale / 1.15, V / Math.max(imgNW, imgNH)); clamp(); }
  function wheel(e) { e.preventDefault(); e.deltaY < 0 ? zoomIn() : zoomOut(); }

  function dragStart(e) {
    e.preventDefault(); dragging = true;
    const ev = e.touches ? e.touches[0] : e;
    dsx = ev.clientX; dsy = ev.clientY; dpx = panX; dpy = panY;
  }
  function dragMove(e) {
    if (!dragging) return;
    const ev = e.touches ? e.touches[0] : e;
    panX = dpx + (ev.clientX - dsx); panY = dpy + (ev.clientY - dsy); clamp();
  }
  function dragEnd() { dragging = false; }

  function getCrop() {
    const iw = imgNW * scale, ih = imgNH * scale;
    const il = (V - iw) / 2 + panX, it = (V - ih) / 2 + panY;
    const cx = Math.round(Math.max(0, -il / scale));
    const cy = Math.round(Math.max(0, -it / scale));
    let cs = Math.round(V / scale);
    cs = Math.min(cs, imgNW - cx, imgNH - cy);
    return { cx, cy, cs };
  }

  async function confirmCrop() {
    if (!avatarFile) return;
    uploadingAvatar = true; error = '';
    try {
      const { cx, cy, cs } = getCrop();
      const result = await api.profile.uploadAvatar(avatarFile, cx, cy, cs);
      profile = { ...profile, avatar_original: result.avatar_original, avatar_thumb: result.avatar_thumb };
      auth.updateUser({ avatar_thumb: result.avatar_thumb, avatar_original: result.avatar_original });
      closeCrop(); success = 'Avatar updated!'; setTimeout(() => success = '', 3000);
    } catch (e) { error = e.message; } finally { uploadingAvatar = false; }
  }

  async function deleteAvatar() {
    try {
      await api.profile.deleteAvatar();
      profile = { ...profile, avatar_original: null, avatar_thumb: null };
      auth.updateUser({ avatar_thumb: null, avatar_original: null });
      success = 'Removed'; setTimeout(() => success = '', 3000);
    } catch (e) { error = e.message; }
  }
</script>

<svelte:head><title>Profile Settings | TheFoxxStuff</title></svelte:head>
<svelte:window onmousemove={dragMove} onmouseup={dragEnd} ontouchmove={dragMove} ontouchend={dragEnd} />

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0">
  <h1 class="font-display text-2xl tracking-wide mb-6">Profile Settings</h1>

  {#if loading}
    <div class="card p-8"><div class="animate-pulse space-y-4"><div class="w-24 h-24 rounded-full bg-dark-800 mx-auto"></div><div class="h-4 bg-dark-800 rounded w-1/3 mx-auto"></div></div></div>
  {:else if profile}
    <div class="space-y-4">
      <div class="card p-6">
        <div class="flex items-start gap-6">
          <div class="relative group flex-shrink-0">
            {#if profile.avatar_thumb}
              <img src={avUrl(profile.avatar_thumb)} alt="" class="w-20 h-20 rounded-full object-cover ring-2 ring-[--w12]" />
            {:else}
              <div class="w-20 h-20 rounded-full bg-dark-800 flex items-center justify-center ring-2 ring-[--w12]"><User size={28} class="text-[--w60]" /></div>
            {/if}
            <label class="absolute inset-0 rounded-full bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition cursor-pointer">
              <Camera size={20} class="text-white" /><input type="file" accept="image/*" class="hidden" onchange={handleFile} />
            </label>
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-lg font-medium text-[--w]">{profile.display_name || profile.username}</div>
            <div class="text-[--w60] text-sm">@{profile.username}</div>
            {#if profile.role === 'admin'}<span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full bg-accent-green/10 text-accent-green mt-2"><Shield size={10} /> Admin</span>{/if}
          </div>
          <div class="flex flex-col gap-2">
            <label class="btn btn-secondary text-sm cursor-pointer"><Camera size={14} /> Change<input type="file" accept="image/*" class="hidden" onchange={handleFile} /></label>
            {#if profile.avatar_thumb}<button onclick={deleteAvatar} class="btn btn-danger text-sm"><Trash2 size={14} /></button>{/if}
          </div>
        </div>
      </div>

      <div class="card p-6 space-y-4">
        <div><label class="label">Display Name</label><input type="text" class="input" placeholder="Your display name" maxlength="50" bind:value={displayName} /><div class="text-xs text-dark-500 mt-1">{displayName.length}/50</div></div>
        <div><label class="label">Bio</label><textarea class="textarea" rows="4" placeholder="Tell us about yourself..." bind:value={bio}></textarea><div class="text-xs mt-1 {bioWords > 190 ? 'text-accent-red' : 'text-dark-500'}">{bioWords}/190 words</div></div>
        {#if error}<div class="text-accent-red text-sm bg-accent-red/10 px-4 py-2 rounded-lg">{error}</div>{/if}
        {#if success}<div class="text-accent-green text-sm bg-accent-green/10 px-4 py-2 rounded-lg">{success}</div>{/if}
        <button onclick={saveProfile} class="btn btn-primary w-full" disabled={saving || bioWords > 190}><Save size={16} /> {saving ? 'Saving...' : 'Save'}</button>
      </div>

      <div class="card p-4 flex items-center gap-3 flex-wrap">
        <a href="/profile/{profile.username}" class="btn btn-secondary text-sm"><ExternalLink size={14} /> Public Profile</a>
        {#if isAdmin($auth.user)}<a href="/admin" class="btn btn-secondary text-sm"><Shield size={14} /> Admin</a>{/if}
      </div>
    </div>
  {/if}
</div>

{#if showCropper}
  <div class="fixed inset-0 z-[10001] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
    <div class="bg-dark-900 rounded-2xl border border-[--w12] p-6 w-full max-w-[400px] space-y-4">
      <div class="flex items-center justify-between"><h3 class="font-display text-lg">Crop Avatar</h3><button onclick={closeCrop} class="text-[--w60] hover:text-[--w]"><X size={20} /></button></div>
      <div class="relative mx-auto rounded-full overflow-hidden bg-dark-800 cursor-grab active:cursor-grabbing select-none" style="width:{V}px;height:{V}px;"
        role="img" onmousedown={dragStart} ontouchstart={dragStart} onwheel={wheel}>
        {#if avatarPreview}
          <img src={avatarPreview} alt="crop" class="absolute pointer-events-none" draggable="false"
            style="width:{imgNW*scale}px;height:{imgNH*scale}px;left:{(V-imgNW*scale)/2+panX}px;top:{(V-imgNH*scale)/2+panY}px;" />
        {/if}
        <div class="absolute inset-0 rounded-full ring-2 ring-white/30 pointer-events-none"></div>
      </div>
      <div class="flex items-center justify-center gap-4">
        <button onclick={zoomOut} class="btn btn-secondary p-2"><ZoomOut size={18} /></button>
        <input type="range" min={V/Math.max(imgNW,imgNH)} max={V/Math.min(imgNW,imgNH)*5} step="0.001" bind:value={scale} oninput={clamp} class="w-24 accent-green-400" />
        <button onclick={zoomIn} class="btn btn-secondary p-2"><ZoomIn size={18} /></button>
      </div>
      <div class="text-xs text-dark-500 text-center flex items-center justify-center gap-1"><Move size={12} /> Drag to position, scroll to zoom</div>
      <div class="flex gap-2">
        <button onclick={closeCrop} class="btn btn-secondary flex-1">Cancel</button>
        <button onclick={confirmCrop} class="btn btn-primary flex-1" disabled={uploadingAvatar}><Check size={16} /> {uploadingAvatar ? 'Uploading...' : 'Apply'}</button>
      </div>
    </div>
  </div>
{/if}
