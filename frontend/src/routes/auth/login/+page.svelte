<script>
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { auth } from '$lib/stores/auth.js';
  let username = $state('');
  let password = $state('');
  let error = $state('');
  let loading = $state(false);
  const handleSubmit = async (e) => {
    e.preventDefault();
    error = ''; loading = true;
    try {
      const { access_token } = await api.auth.login({ username, password });
      auth.login(access_token, null);
      const [user, profile] = await Promise.all([api.auth.me(), api.profile.me().catch(() => null)]);
      auth.setUser({ ...user, avatar_thumb: profile?.avatar_thumb || null, avatar_original: profile?.avatar_original || null, display_name: profile?.display_name || user.display_name || "" });
      goto(user.role === 'admin' ? '/admin' : '/');
    } catch (err) { error = err.message; }
    finally { loading = false; }
  };
</script>
<SEO
  title="Login"
  description="Sign in to TheFoxxStuff"
  url={canonicalUrl("/auth/login")}
  noindex={true}
/>|<SEO
  title="Login"
  description="Sign in to TheFoxxStuff"
  url={canonicalUrl("/auth/login")}
  noindex={true}
/>
<div class="max-w-md mx-auto px-4 py-16">
  <div class="card p-8">
    <h1 class="font-display text-[24px] tracking-wide mb-6 text-center">Login</h1>
    {#if error}<div class="mb-4 p-3 bg-accent-red/10 border border-accent-red/50 rounded-lg text-accent-red text-sm">{error}</div>{/if}
    <form onsubmit={handleSubmit} class="space-y-4">
      <div><label for="username" class="label">Username</label><input type="text" id="username" bind:value={username} required class="input" /></div>
      <div><label for="password" class="label">Password</label><input type="password" id="password" bind:value={password} required class="input" /></div>
      <button type="submit" disabled={loading} class="btn btn-primary w-full">{loading ? 'Loading...' : 'Login'}</button>
    </form>
    <p class="mt-6 text-center text-sm text-dark-400">Don't have an account? <a href="/auth/register" class="text-accent-green hover:underline">Register</a></p>
  </div>
</div>
