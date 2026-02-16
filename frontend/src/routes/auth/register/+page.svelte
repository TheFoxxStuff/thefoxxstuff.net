<script>
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { auth } from '$lib/stores/auth.js';
  let username = $state('');
  let email = $state('');
  let password = $state('');
  let error = $state('');
  let loading = $state(false);
  const handleSubmit = async (e) => {
    e.preventDefault();
    error = ''; loading = true;
    try {
      const { access_token } = await api.auth.register({ username, email, password });
      auth.login(access_token, null);
      const [user, profile] = await Promise.all([api.auth.me(), api.profile.me().catch(() => null)]);
      auth.setUser({ ...user, avatar_thumb: profile?.avatar_thumb || null, avatar_original: profile?.avatar_original || null, display_name: profile?.display_name || "" });
      goto(user.role === 'admin' ? '/admin' : '/');
    } catch (err) { error = err.message; }
    finally { loading = false; }
  };
</script>
<svelte:head><title>Register | TheFoxxStuff</title></svelte:head>
<div class="max-w-md mx-auto px-4 py-16">
  <div class="card p-8">
    <h1 class="font-display text-3xl tracking-wide mb-6 text-center">Register</h1>
    <p class="text-sm text-dark-400 text-center mb-6">First user will automatically become admin!</p>
    {#if error}<div class="mb-4 p-3 bg-accent-red/10 border border-accent-red/50 rounded-lg text-accent-red text-sm">{error}</div>{/if}
    <form onsubmit={handleSubmit} class="space-y-4">
      <div><label for="username" class="label">Username</label><input type="text" id="username" bind:value={username} required class="input" /></div>
      <div><label for="email" class="label">Email</label><input type="email" id="email" bind:value={email} required class="input" /></div>
      <div><label for="password" class="label">Password</label><input type="password" id="password" bind:value={password} required minlength="6" class="input" /></div>
      <button type="submit" disabled={loading} class="btn btn-primary w-full">{loading ? 'Loading...' : 'Register'}</button>
    </form>
    <p class="mt-6 text-center text-sm text-dark-400">Already have an account? <a href="/auth/login" class="text-accent-green hover:underline">Login</a></p>
  </div>
</div>
