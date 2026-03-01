<script>
  import '../app.css';
  import { Header, MobileHeader, Footer } from '$lib/components';
  import Background from '$lib/components/Background.svelte';
  import GlowingBackground from '../lib/components/GlowingBackground.svelte';
  import MusicPlayer from '$lib/components/MusicPlayer.svelte';
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth.js';
  import { presence } from '$lib/stores/presence.js';
  import { theme } from '$lib/stores/theme.js';
  import { api } from '$lib/api';
  let { children } = $props();

  onMount(() => {
    // FIX: обновляем профиль только при наличии токена
    // FIX: НЕ делаем logout при сетевой ошибке — только при явном 401
    if ($auth.token) {
      api.auth.me()
        .then(user => {
          auth.setUser({
            ...$auth.user,
            ...user,
            avatar_thumb:     user.avatar_thumb     ?? $auth.user?.avatar_thumb,
            avatar_original:  user.avatar_original   ?? $auth.user?.avatar_original,
          });
        })
        .catch(err => {
          // Логаутим только при явной ошибке аутентификации, не при сетевых проблемах
          if (err.message === 'Not authenticated') {
            auth.logout();
          }
          // При timeout / 500 / сети — просто продолжаем с закешированными данными
        });
    }

    // Presence запускается один раз на весь сеанс
    presence.startGlobal();

    // Подписываемся на тему — store уже применил класс при инициализации,
    // subscribe держит реактивность на случай системных изменений
    const unsubTheme = theme.subscribe(() => {});
    return unsubTheme;
  });
</script>

<div class="min-h-screen flex flex-col relative overflow-hidden">
  <GlowingBackground />
  <Background />
  <Header />
  <MobileHeader />
  <main class="flex-1 relative z-10">
    {@render children()}
  </main>
  <Footer />
</div>
<MusicPlayer />
