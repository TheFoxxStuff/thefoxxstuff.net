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

<div class="flex items-center justify-center min-h-[70vh] px-4">
  <div class="w-full max-w-[380px] animate-fade-in-up">
    <div class="text-center mb-8">
      <h1 class="font-display text-3xl tracking-wide text-[--w] mb-1">Create account</h1>
      <p class="text-[13px]" style="color: rgba(255,255,255,0.4);">First user becomes admin automatically</p>
    </div>

    <div class="rounded-[18px] overflow-hidden" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);">
      <div class="h-px w-full" style="background: linear-gradient(90deg, transparent, rgba(115,238,7,0.4), transparent);"></div>

      <div class="p-7">
        {#if error}
          <div class="mb-5 px-4 py-3 rounded-[10px] text-[13px] text-red-400 animate-fade-in" style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.15);">
            {error}
          </div>
        {/if}

        <form onsubmit={handleSubmit} class="space-y-4">
          <div>
            <label for="username" class="block text-[12px] font-medium mb-1.5" style="color: rgba(255,255,255,0.5);">Username</label>
            <input type="text" id="username" bind:value={username} required
              class="w-full px-3.5 py-2.5 rounded-[10px] text-[14px] text-[--w] placeholder-[--w40] outline-none transition-all"
              style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);"
              placeholder="cool_username" />
          </div>

          <div>
            <label for="email" class="block text-[12px] font-medium mb-1.5" style="color: rgba(255,255,255,0.5);">Email</label>
            <input type="email" id="email" bind:value={email} required
              class="w-full px-3.5 py-2.5 rounded-[10px] text-[14px] text-[--w] placeholder-[--w40] outline-none transition-all"
              style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);"
              placeholder="you@example.com" />
          </div>

          <div>
            <label for="password" class="block text-[12px] font-medium mb-1.5" style="color: rgba(255,255,255,0.5);">Password</label>
            <input type="password" id="password" bind:value={password} required minlength="6"
              class="w-full px-3.5 py-2.5 rounded-[10px] text-[14px] text-[--w] placeholder-[--w40] outline-none transition-all"
              style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);"
              placeholder="••••••••" />
          </div>

          <button
            type="submit"
            disabled={loading}
            class="w-full py-2.5 mt-1 rounded-[10px] text-[14px] font-semibold transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50"
            style="background: #73EE07; color: #0a0a0a;"
          >
            {loading ? 'Creating...' : 'Create Account'}
          </button>
        </form>
      </div>
    </div>

    <p class="text-center text-[13px] mt-5" style="color: rgba(255,255,255,0.35);">
      Already have an account?
      <a href="/auth/login" class="text-[--green] hover:underline ml-1">Sign in</a>
    </p>
  </div>
</div>
