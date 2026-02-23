<script>
  import '../app.css';
  import { Header, Footer } from '$lib/components';
  import Background from '$lib/components/Background.svelte';
  import GlowingBackground from '../lib/components/GlowingBackground.svelte';
  import MusicPlayer from '$lib/components/MusicPlayer.svelte';
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth.js';
  import { presence } from '$lib/stores/presence.js';
  import { api } from '$lib/api';
  let { children } = $props();

  onMount(() => {
    if ($auth.token) {
      api.auth.me().then(user => {
        auth.setUser({ ...$auth.user, ...user, avatar_thumb: user.avatar_thumb ?? $auth.user?.avatar_thumb, avatar_original: user.avatar_original ?? $auth.user?.avatar_original });
      }).catch(() => auth.logout());
    }

    // Запускаем presence один раз для всего сайта.
    // Отдельные страницы вызывают presence.start(type, id) для is-here,
    // но само WebSocket-соединение живёт здесь — на любой странице сайта.
    presence.startGlobal();

    return () => {
      // presence.stop() НЕ вызываем — соединение переиспользуется между страницами.
      // Оно закроется только при закрытии вкладки.
    };
  });
</script>

<div class="min-h-screen flex flex-col relative overflow-hidden">
  <GlowingBackground />
  <Background />
  <Header />
  <main class="flex-1 relative z-10">
    {@render children()}
  </main>
  <Footer />
</div>
<MusicPlayer />
