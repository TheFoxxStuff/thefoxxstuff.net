<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { api, API_BASE } from '$lib/api';
  import { User, Calendar, Shield } from 'lucide-svelte';

  let profile = $state(null);
  let loading = $state(true);
  let error = $state('');

  function getAvatarUrl(path) {
    if (!path) return null;
    return `${API_BASE}/upload/file/${path}`;
  }

  function formatDate(date) {
    if (!date) return '';
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric', month: 'long', day: 'numeric'
    });
  }

  onMount(async () => {
    const username = $page.params.username;
    try {
      profile = await api.profile.get(username);
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  });
</script>

<svelte:head>
  <title>{profile ? `@${profile.username}` : 'Profile'} | TheFoxxStuff</title>
</svelte:head>

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0">
  {#if loading}
    <div class="card p-8">
      <div class="animate-pulse space-y-4">
        <div class="w-28 h-28 rounded-full bg-dark-800 mx-auto"></div>
        <div class="h-5 bg-dark-800 rounded w-1/3 mx-auto"></div>
        <div class="h-16 bg-dark-800 rounded w-2/3 mx-auto"></div>
      </div>
    </div>
  {:else if error}
    <div class="card p-8 text-center">
      <User size={48} class="mx-auto text-dark-500 mb-4" />
      <div class="text-[--w60]">User not found</div>
    </div>
  {:else if profile}
    <div class="card p-8 flex flex-col items-center text-center space-y-4">
      <!-- Avatar -->
      {#if profile.avatar_original}
        <img
          src={getAvatarUrl(profile.avatar_original)}
          alt={profile.username}
          class="w-28 h-28 rounded-full object-cover ring-2 ring-[--w12]"
        />
      {:else}
        <div class="w-28 h-28 rounded-full bg-dark-800 flex items-center justify-center ring-2 ring-[--w12]">
          <User size={40} class="text-[--w60]" />
        </div>
      {/if}

      <!-- Name & Username -->
      <div>
        {#if profile.display_name}
          <h1 class="font-display text-xl tracking-wide">{profile.display_name}</h1>
        {/if}
        <div class="text-[--w60] text-sm mt-1">@{profile.username}</div>
      </div>

      <!-- Role badge -->
      {#if profile.role === 'admin'}
        <div class="inline-flex items-center gap-1.5 px-3 py-1 text-xs rounded-full bg-accent-green/10 text-accent-green border border-accent-green/20">
          <Shield size={12} />
          Admin
        </div>
      {/if}

      <!-- Bio -->
      {#if profile.bio}
        <p class="text-[--w60] text-sm leading-relaxed max-w-md">{profile.bio}</p>
      {/if}

      <!-- Member since -->
      {#if profile.created_at}
        <div class="flex items-center gap-2 text-xs text-dark-500">
          <Calendar size={12} />
          Joined {formatDate(profile.created_at)}
        </div>
      {/if}
    </div>
  {/if}
</div>
