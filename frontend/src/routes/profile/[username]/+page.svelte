<script>
  import { page } from '$app/stores';
  import { api, API_BASE } from '$lib/api';
  import { auth } from '$lib/stores/auth.js';
  import { SEO } from '$lib/components';
  import { Shield, Settings, Calendar, ChevronRight } from 'lucide-svelte';
  import { SITE, canonicalUrl } from '$lib/seo.js';

  let { data: pageData } = $props();

  let profile = $state(pageData.profile);
  let loading = $state(false);
  let error = $state(profile ? '' : 'Profile not found');
  let isOwnProfile = $derived($auth.user?.username === profile?.username);

  function avUrl(p) { return p ? `${API_BASE}/upload/file/${p}` : null; }
  function nameHue(name) {
    let h = 0;
    for (let i = 0; i < (name||'').length; i++) h = (h * 31 + name.charCodeAt(i)) % 360;
    return h;
  }
  function formatDate(d) {
    if (!d) return '';
    return new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  }

  let profileName = $derived(profile?.display_name || (profile ? `@${profile.username}` : 'Profile'));
  let profileBio  = $derived(profile?.bio || `${profileName} on TheFoxxStuff`);
  let profileImg  = $derived(profile?.avatar_thumb ? avUrl(profile.avatar_thumb) : SITE.defaultImage);
  let profileUrl  = $derived(profile ? canonicalUrl(`/profile/${profile.username}`) : canonicalUrl('/'));
</script>

<SEO
  title={profileName}
  description={profileBio}
  image={profileImg}
  imageAlt={profileName}
  type="profile"
  url={profileUrl}
  profile={{ username: profile?.username }}
/>

<div class="page-wrap">

  {#if error}
    <div class="profile-card">
      <div class="error-icon">?</div>
      <p class="error-text">User not found</p>
    </div>

  {:else if profile}
    {@const hue = nameHue(profile.username)}
    {@const thumb = avUrl(profile.avatar_thumb)}
    {@const original = avUrl(profile.avatar_original)}

    <div class="profile-card">

      <!-- Avatar: thumb shown, original opens by click -->
      <div class="avatar-wrap" class:admin={profile.role === 'admin'}>
        {#if thumb}
          {#if original}
            <a href={original} target="_blank" rel="noreferrer" class="av-link" title="View full photo">
              <img src={thumb} alt={profile.username} class="avatar-img av-clickable" />
            </a>
          {:else}
            <img src={thumb} alt={profile.username} class="avatar-img" />
          {/if}
        {:else}
          <div class="avatar-placeholder" style="--hue:{hue}">
            {(profile.display_name || profile.username || '?').slice(0,2).toUpperCase()}
          </div>
        {/if}
      </div>

      <!-- Name block -->
      <div class="name-block">
        <h1 class="display-name">
          {profile.display_name || profile.username}
        </h1>
        <div class="username">@{profile.username}</div>
      </div>

      <!-- Admin badge -->
      {#if profile.role === 'admin'}
        <div class="admin-badge"><Shield size={11}/> Administrator</div>
      {/if}

      <!-- Bio -->
      {#if profile.bio}
        <p class="bio">{profile.bio}</p>
      {/if}

      <!-- Joined -->
      {#if profile.created_at}
        <div class="meta-joined">
          <Calendar size={12}/>
          Joined {formatDate(profile.created_at)}
        </div>
      {/if}

      <!-- Own profile CTA -->
      {#if isOwnProfile}
        <div class="own-actions">
          <a href="/profile/settings" class="settings-btn">
            <Settings size={14}/>
            Edit profile
          </a>
        </div>
      {/if}

    </div>

    <!-- Settings card (own only) -->
    {#if isOwnProfile}
      <a href="/profile/settings" class="settings-cta">
        <div class="cta-inner">
          <div class="cta-icon"><Settings size={16}/></div>
          <div class="cta-text">
            <div class="cta-title">Profile Settings</div>
            <div class="cta-desc">Change display name, bio, avatar photo</div>
          </div>
        </div>
        <ChevronRight size={16} class="cta-chevron"/>
      </a>
    {/if}

  {/if}

</div>

<style>
  .page-wrap {
    max-width: 828px;
    margin: 0 auto;
    padding: 24px 16px 80px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  @media(min-width: 829px) { .page-wrap { padding-left: 0; padding-right: 0; } }

  /* ── Profile card ── */
  .profile-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 10px;
    padding: 48px 32px 40px;
    background: var(--w5);
    border: 1px solid var(--w8);
    border-radius: 18px;
  }

  /* ── Avatar ── */
  .avatar-wrap {
    position: relative;
    margin-bottom: 4px;
  }
  .avatar-wrap.admin::after {
    content: '';
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    border: 2px solid #4ade80;
    pointer-events: none;
  }
  .avatar-img, .avatar-placeholder {
    width: 96px;
    height: 96px;
    border-radius: 50%;
    display: block;
  }
  .avatar-img {
    object-fit: cover;
    border: 3px solid var(--w12);
  }
  .av-link { display: block; border-radius: 50%; }
  .av-clickable {
    transition: filter 0.15s, transform 0.15s;
  }
  .av-clickable:hover {
    filter: brightness(1.1);
    transform: scale(1.03);
  }
  .avatar-placeholder {
    background: hsl(var(--hue), 42%, 20%);
    border: 3px solid hsl(var(--hue), 42%, 28%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: DrukWideCyr, sans-serif;
    font-size: 28px;
    color: hsl(var(--hue), 55%, 72%);
  }

  /* ── Name ── */
  .name-block { display: flex; flex-direction: column; gap: 4px; }
  .display-name {
    font-family: DrukWideCyr, sans-serif;
    font-size: 26px;
    letter-spacing: 0.03em;
    color: var(--w);
    line-height: 1.1;
  }
  .username { font-size: 14px; color: var(--w60); }

  /* ── Admin badge ── */
  .admin-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-family: DrukWideCyr, sans-serif;
    font-size: 11px;
    letter-spacing: 0.06em;
    color: #4ade80;
    background: rgba(74,222,128,0.09);
    border: 1px solid rgba(74,222,128,0.22);
    padding: 4px 12px;
    border-radius: 20px;
  }

  /* ── Bio ── */
  .bio {
    font-size: 14px;
    color: var(--w60);
    line-height: 1.65;
    max-width: 380px;
    margin: 4px 0 0;
  }

  /* ── Meta ── */
  .meta-joined {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 12px;
    color: var(--w30);
    margin-top: 2px;
  }

  /* ── Own profile button ── */
  .own-actions { margin-top: 8px; }
  .settings-btn {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 8px 18px;
    border-radius: 9px;
    border: 1px solid var(--w12);
    background: var(--w8);
    color: var(--w60);
    font-size: 13px;
    font-weight: 500;
    text-decoration: none;
    transition: background .12s, color .12s, border-color .12s;
  }
  .settings-btn:hover {
    background: var(--w12);
    border-color: var(--w18);
    color: var(--w);
  }

  /* ── Settings CTA row ── */
  .settings-cta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px;
    background: var(--w5);
    border: 1px solid var(--w8);
    border-radius: 12px;
    text-decoration: none;
    transition: background .12s, border-color .12s;
    cursor: pointer;
  }
  .settings-cta:hover {
    background: var(--w8);
    border-color: var(--w12);
  }
  .cta-inner {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .cta-icon {
    width: 34px; height: 34px;
    border-radius: 9px;
    background: var(--w8);
    border: 1px solid var(--w12);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--w60);
    flex-shrink: 0;
  }
  .cta-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--w);
    line-height: 1.2;
  }
  .cta-desc {
    font-size: 12px;
    color: var(--w30);
    margin-top: 2px;
  }
  :global(.cta-chevron) { color: var(--w30); flex-shrink: 0; }

  /* ── Error ── */
  .error-icon {
    width: 64px; height: 64px; border-radius: 50%;
    background: var(--w8);
    display: flex; align-items: center; justify-content: center;
    font-family: DrukWideCyr, sans-serif;
    font-size: 28px; color: var(--w30);
  }
  .error-text { font-size: 14px; color: var(--w60); }
</style>
