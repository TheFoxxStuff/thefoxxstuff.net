<script>
  import { onMount } from 'svelte';
  import { api, API_BASE } from '$lib/api';
  import { auth, isAdmin } from '$lib/stores/auth.js';
  import { goto } from '$app/navigation';
  import { SEO } from '$lib/components';
  import { canonicalUrl } from '$lib/seo.js';
  import { AvatarCropper } from '$lib/components';
  import { Camera, Save, Trash2, Check, LogOut, Shield, Image } from 'lucide-svelte';
  import { presence } from '$lib/stores/presence.js';

  let { data: pageData } = $props();

  let profile     = $state(null);
  let loading     = $state(false);
  let saving      = $state(false);
  let error       = $state('');
  let success     = $state('');
  let displayName = $state('');
  let bio         = $state('');

  // Кроппер
  let cropFile    = $state(null);  // File object — открывает кроппер
  let bioWords    = $derived(bio.trim() ? bio.trim().split(/\s+/).length : 0);

  // Banner
  let bannerFile  = $state(null);
  let bannerPreview = $state(null);
  let bannerUploading = $state(false);
  let bannerSaving = $state(false);

  function avUrl(p) { return p ? `${API_BASE}/upload/file/${p}` : null; }
  function bannerUrl(p) { return p ? `${API_BASE}/upload/file/${p}` : null; }

  function nameHue(name) {
    let h = 0;
    for (let i = 0; i < (name || '').length; i++) h = (h * 31 + name.charCodeAt(i)) % 360;
    return h;
  }

  onMount(() => {
    if (!$auth.user) goto('/auth/login');
    // Данные загружены на клиенте (ssr=false) до mount — снимаем снимок
    profile = pageData.profile ?? null;
    displayName = profile?.display_name || '';
    bio = profile?.bio || '';
  });

  async function saveProfile() {
    saving = true; error = ''; success = '';
    try {
      profile = await api.profile.update({ display_name: displayName, bio });
      auth.updateUser({ display_name: displayName });
      // FIX: инвалидируем кэш профиля в presence для других юзеров
      presence.reconnect();
      success = 'Saved!';
      setTimeout(() => success = '', 3000);
    } catch (e) { error = e.message; }
    finally { saving = false; }
  }

  function pickFile(e) {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 10 * 1024 * 1024) { error = 'File too large (max 10 MB)'; return; }
    error = '';
    cropFile = f;
    // сбрасываем input чтобы можно было выбрать тот же файл повторно
    e.target.value = '';
  }

  async function onCropConfirm(file, cx, cy, cs) {
    try {
      const result = await api.profile.uploadAvatar(file, cx, cy, cs);
      profile = { ...profile, avatar_original: result.avatar_original, avatar_thumb: result.avatar_thumb };
      auth.updateUser({ avatar_thumb: result.avatar_thumb, avatar_original: result.avatar_original });
      // FIX: инвалидируем кэш профиля в presence
      presence.reconnect();
      cropFile = null;
      success = 'Avatar updated!';
      setTimeout(() => success = '', 3000);
    } catch (e) {
      error = e.message;
      cropFile = null;
    }
  }

  function onCropCancel() { cropFile = null; }

  async function deleteAvatar() {
    if (!confirm('Remove avatar?')) return;
    try {
      await api.profile.deleteAvatar();
      profile = { ...profile, avatar_original: null, avatar_thumb: null };
      auth.updateUser({ avatar_thumb: null, avatar_original: null });
      presence.reconnect();
      success = 'Avatar removed';
      setTimeout(() => success = '', 3000);
    } catch (e) { error = e.message; }
  }

  // Banner functions
  function pickBannerFile(e) {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 10 * 1024 * 1024) { error = 'Banner file too large (max 10 MB)'; return; }
    error = '';
    bannerFile = f;
    // Create preview
    const reader = new FileReader();
    reader.onload = (ev) => { bannerPreview = ev.target.result; };
    reader.readAsDataURL(f);
    e.target.value = '';
  }

  async function uploadBanner() {
    if (!bannerFile) return;
    bannerUploading = true;
    error = '';
    try {
      const result = await api.profile.uploadBanner(bannerFile);
      profile = { ...profile, banner_image: result.banner_image };
      bannerFile = null;
      bannerPreview = null;
      presence.reconnect();
      success = 'Banner updated!';
      setTimeout(() => success = '', 3000);
    } catch (e) {
      error = e.message;
    } finally {
      bannerUploading = false;
    }
  }

  function cancelBannerUpload() {
    bannerFile = null;
    bannerPreview = null;
  }

  async function deleteBanner() {
    if (!confirm('Remove banner?')) return;
    try {
      await api.profile.deleteBanner();
      profile = { ...profile, banner_image: null };
      presence.reconnect();
      success = 'Banner removed';
      setTimeout(() => success = '', 3000);
    } catch (e) { error = e.message; }
  }

  function doLogout() { auth.logout(); goto('/'); }
</script>

<SEO
  title="Profile Settings"
  description="Edit your TheFoxxStuff profile"
  url={canonicalUrl("/profile/settings")}
  noindex={true}
/>

<!-- Кроппер рендерится поверх всего когда выбран файл -->
{#if cropFile}
  <AvatarCropper file={cropFile} onconfirm={onCropConfirm} oncancel={onCropCancel} />
{/if}

<div class="page-wrap">

  <!-- Breadcrumb -->
  <div class="breadcrumb">
    <a href={profile ? `/profile/${profile.username}` : '/profile'} class="bc-link">← Profile</a>
    <span class="bc-sep">·</span>
    <span class="bc-cur">Settings</span>
  </div>

  {#if profile}
    {@const hue = nameHue(profile.username)}
    {@const thumb = avUrl(profile.avatar_thumb)}
    {@const banner = bannerPreview || (profile.banner_image ? bannerUrl(profile.banner_image) : null)}

    <!-- Banner card -->
    <div class="card">
      <div class="card-label">Banner</div>
      
      {#if banner}
        <div class="banner-preview">
          <img src={banner} alt="Banner preview" class="banner-preview-img" />
        </div>
      {:else}
        <div class="banner-placeholder">
          <span class="banner-placeholder-icon"><Image size={32} /></span>
          <span>No banner image</span>
        </div>
      {/if}

      <div class="banner-actions">
        <label class="banner-upload-btn">
          <input type="file" accept="image/*" onchange={pickBannerFile} class="hidden" />
          <Camera size={14} />
          <span>{banner ? 'Change banner' : 'Upload banner'}</span>
        </label>
        {#if banner || profile.banner_image}
          <button onclick={deleteBanner} class="banner-delete-btn" title="Remove banner">
            <Trash2 size={14} />
            <span>Remove</span>
          </button>
        {/if}
      </div>

      {#if bannerFile}
        <div class="banner-upload-actions">
          <button onclick={uploadBanner} disabled={bannerUploading} class="btn btn-primary">
            {bannerUploading ? 'Uploading...' : 'Save Banner'}
          </button>
          <button onclick={cancelBannerUpload} class="btn btn-secondary">Cancel</button>
        </div>
      {/if}
      
      <div class="field-hint muted">Recommended size: 1920×600. Max 10 MB.</div>
    </div>

    <!-- ── Avatar card ── -->
    <div class="card">
      <div class="card-label">Avatar</div>
      <div class="av-row">
        <div class="av-preview-wrap">
          <label class="av-preview" title="Change avatar">
            {#if thumb}
              <img src={thumb} alt="" class="av-img" />
            {:else}
              <div class="av-ph" style="--hue:{hue}">
                {(profile.display_name || profile.username || '?').slice(0,2).toUpperCase()}
              </div>
            {/if}
            <input type="file" accept="image/*" onchange={pickFile} class="hidden" />
            <div class="av-overlay"><Camera size={20}/></div>
          </label>
        </div>
        <div class="av-info">
          <div class="av-hint">Click avatar to upload new photo</div>
          <div class="av-btns">
            <label class="av-btn" for="avatar-input">
              <Camera size={14}/> Change
            </label>
            {#if profile.avatar_thumb}
              <button onclick={deleteAvatar} class="av-btn av-danger">
                <Trash2 size={14}/> Remove
              </button>
            {/if}
          </div>
        </div>
      </div>
      <input id="avatar-input" type="file" accept="image/*" onchange={pickFile} class="hidden" />
    </div>

    <!-- ── Profile info card ── -->
    <div class="card">
      <div class="card-label">Profile Info</div>
      
      <div class="field">
        <label class="field-label" for="fl-display-name">Display Name</label>
        <input id="fl-display-name" type="text" bind:value={displayName} class="field-input" placeholder="Your display name" maxlength="50" />
      </div>

      <div class="field">
        <label class="field-label" for="fl-bio">Bio</label>
        <textarea id="fl-bio" bind:value={bio} class="field-textarea" rows="4" placeholder="Tell us about yourself..." maxlength="1500"></textarea>
        <span class="field-hint {bioWords > 190 ? 'over' : 'muted'}">{bioWords}/190 words</span>
      </div>

      {#if error}<div class="alert error">{error}</div>{/if}
      {#if success}<div class="alert ok"><Check size={14}/> {success}</div>{/if}

      <div class="card-footer">
        <button onclick={saveProfile} disabled={saving} class="save-btn">
          <Save size={16}/> {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </div>

    <!-- ── Account card ── -->
    <div class="card card-account">
      <div class="card-label danger-lbl">Account</div>
      <div class="account-row">
        <button onclick={doLogout} class="acc-link acc-logout">
          <LogOut size={14}/> Log out
        </button>
        {#if isAdmin($auth.user)}
          <a href="/admin" class="acc-link">
            <Shield size={14}/> Admin Panel
          </a>
        {/if}
      </div>
    </div>

  {/if}
</div>

<style>
  .page-wrap {
    max-width: 828px; margin: 0 auto;
    padding: 24px 16px 80px;
    display: flex; flex-direction: column; gap: 6px;
  }
  @media(min-width:829px){ .page-wrap{ padding-left:0; padding-right:0; } }

  /* Breadcrumb */
  .breadcrumb { display:flex; align-items:center; gap:8px; margin-bottom:10px; }
  .bc-link {
    font-size:13px; color:var(--w60); text-decoration:none;
    padding:5px 10px; border-radius:7px; transition:background .12s,color .12s;
  }
  .bc-link:hover { background:var(--w8); color:var(--w); }
  .bc-sep { font-size:12px; color:var(--w18); }
  .bc-cur { font-size:13px; color:var(--w30); }

  /* Card */
  .card {
    background:var(--w5); border:1px solid var(--w8);
    border-radius:14px; padding:20px;
    display:flex; flex-direction:column; gap:14px;
  }
  .card-label {
    font-size:11px; font-weight:600; color:var(--w30);
    text-transform:uppercase; letter-spacing:.09em;
  }
  .card-account { border-color:rgba(239,68,68,.1); }
  .danger-lbl   { color:rgba(239,68,68,.5); }

  /* Banner */
  .banner-preview {
    width: 100%;
    border-radius: 10px;
    overflow: hidden;
    background: var(--w8);
  }
  .banner-preview-img {
    width: 100%;
    max-height: 200px;
    object-fit: cover;
    display: block;
  }
  .banner-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 40px;
    color: var(--w30);
    font-size: 13px;
    background: var(--w8);
    border-radius: 10px;
    border: 1px dashed var(--w12);
  }
  .banner-placeholder-icon { opacity: 0.5; }
  .banner-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  .banner-upload-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    border: 1px solid var(--w12);
    background: var(--w8);
    color: var(--w60);
    transition: background .12s, color .12s;
  }
  .banner-upload-btn:hover {
    background: var(--w12);
    color: var(--w);
  }
  .banner-delete-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    border: 1px solid rgba(239,68,68,.2);
    background: rgba(239,68,68,.07);
    color: #ef4444;
    transition: background .12s;
  }
  .banner-delete-btn:hover {
    background: rgba(239,68,68,.12);
  }
  .banner-upload-actions {
    display: flex;
    gap: 8px;
  }

  /* Avatar */
  .av-row { display:flex; align-items:center; gap:20px; }
  .av-preview-wrap { flex-shrink:0; }
  .av-preview {
    position:relative; display:block;
    width:72px; height:72px; border-radius:50%;
    cursor:pointer; overflow:hidden;
  }
  .av-img {
    width:72px; height:72px; border-radius:50%;
    object-fit:cover; border:2px solid var(--w12); display:block;
  }
  .av-ph {
    width:72px; height:72px; border-radius:50%;
    background:hsl(var(--hue),42%,20%);
    border:2px solid hsl(var(--hue),42%,28%);
    display:flex; align-items:center; justify-content:center;
    font-family:DrukWideCyr,sans-serif; font-size:20px;
    color:hsl(var(--hue),55%,70%);
  }
  .av-overlay {
    position:absolute; inset:0; border-radius:50%;
    background:rgba(0,0,0,.55);
    display:flex; align-items:center; justify-content:center;
    color:#fff; opacity:0; transition:opacity .15s;
  }
  .av-preview:hover .av-overlay { opacity:1; }
  .av-info { display:flex; flex-direction:column; gap:8px; }
  .av-hint { font-size:12px; color:var(--w30); }
  .av-btns { display:flex; gap:8px; flex-wrap:wrap; }
  .av-btn {
    display:inline-flex; align-items:center; gap:5px;
    padding:6px 12px; border-radius:7px; font-size:12px; font-weight:500;
    cursor:pointer; border:1px solid var(--w12); background:var(--w8); color:var(--w60);
    transition:background .12s,color .12s; font-family:inherit;
  }
  .av-btn:hover { background:var(--w12); color:var(--w); }
  .av-danger:hover { background:rgba(239,68,68,.1); border-color:rgba(239,68,68,.2); color:#ef4444; }

  /* Fields */
  .field { display:flex; flex-direction:column; gap:5px; }
  .field-label { font-size:12px; font-weight:600; color:var(--w60); }
  .field-input, .field-textarea {
    width:100%; box-sizing:border-box;
    background:var(--w8); color:var(--w);
    border-radius:9px; padding:10px 13px;
    font-size:14px; font-family:inherit; outline:none;
    transition:box-shadow .12s;
  }
  .field-input:focus, .field-textarea:focus { box-shadow:0 0 0 1px rgba(255,255,255,.45); }
  .field-input:disabled { opacity:.4; cursor:not-allowed; }
  .field-textarea { resize:none; line-height:1.55; }
  .field-hint { font-size:11px; color:var(--w30); align-self:flex-end; }
  .field-hint.muted { color:var(--w18); }
  .field-hint.over  { color:#ef4444; }

  /* Alerts */
  .alert { padding:10px 14px; border-radius:9px; font-size:13px; border:1px solid; }
  .alert.error { background:rgba(239,68,68,.07); border-color:rgba(239,68,68,.2); color:#ef4444; }
  .alert.ok    { background:rgba(74,222,128,.07); border-color:rgba(74,222,128,.2); color:#4ade80; }

  /* Footer */
  .card-footer { display:flex; align-items:center; gap:12px; padding-top:4px; }
  .save-btn {
    display:inline-flex; align-items:center; gap:7px;
    padding:10px 22px; border-radius:9px; font-size:14px; font-weight:600;
    background:#4ade80; color:#0a0a0a; border:none; cursor:pointer;
    transition:background .12s,opacity .12s; font-family:inherit;
  }
  .save-btn:hover { background:#6ee7a0; }
  .save-btn:disabled { opacity:.45; cursor:not-allowed; }

  /* Account */
  .account-row { display:flex; gap:8px; flex-wrap:wrap; }
  .acc-link {
    display:inline-flex; align-items:center; gap:6px;
    padding:8px 14px; border-radius:8px; font-size:13px; font-weight:500;
    border:1px solid var(--w12); background:var(--w8); color:var(--w60);
    text-decoration:none; cursor:pointer;
    transition:background .12s,color .12s; font-family:inherit;
  }
  .acc-link:hover  { background:var(--w12); color:var(--w); }
  .acc-logout:hover { background:rgba(239,68,68,.1); border-color:rgba(239,68,68,.2); color:#ef4444; }

  /* Buttons */
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    border: 1px solid transparent;
    transition: background .12s, color .12s, border-color .12s;
    font-family: inherit;
  }
  .btn-primary {
    background: #4ade80;
    color: #0a0a0a;
    border-color: #4ade80;
  }
  .btn-primary:hover { background: #6ee7a0; }
  .btn-primary:disabled { opacity: 0.45; cursor: not-allowed; }
  .btn-secondary {
    background: var(--w8);
    color: var(--w60);
    border-color: var(--w12);
  }
  .btn-secondary:hover { background: var(--w12); color: var(--w); }

  .hidden { display: none; }
</style>