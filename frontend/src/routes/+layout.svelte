<script>
  import '../app.css';
  import { Header, Footer, MobileNav } from '$lib/components';
  import Background from '$lib/components/Background.svelte';
  import GlowingBackground from '../lib/components/GlowingBackground.svelte';
  import MusicPlayer from '$lib/components/MusicPlayer.svelte';
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth.js';
  import { api } from '$lib/api';
  let { children } = $props();

  onMount(() => {
    if ($auth.token) {
      api.auth.me().then(user => {
        auth.setUser({ ...$auth.user, ...user, avatar_thumb: user.avatar_thumb ?? $auth.user?.avatar_thumb, avatar_original: user.avatar_original ?? $auth.user?.avatar_original });
      }).catch(() => auth.logout());
    }
  });
</script>

<div class="min-h-screen flex flex-col relative overflow-hidden">
  <GlowingBackground />
  <Background />
  <Header />
  <main class="flex-1 relative z-10 pb-16 md:pb-0">
    {@render children()}
  </main>
  <Footer />
</div>

<!-- Fixed elements (outside main flow) -->
<MusicPlayer />
<MobileNav />
