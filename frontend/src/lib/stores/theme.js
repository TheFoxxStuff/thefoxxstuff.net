import { writable } from 'svelte/store';
import { browser } from '$app/environment';

function getInitialTheme() {
  if (!browser) return 'dark';
  const stored = localStorage.getItem('theme');
  if (stored === 'dark' || stored === 'light') return stored;
  // Системные настройки
  return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
}

export const theme = writable(getInitialTheme());

theme.subscribe((value) => {
  if (browser) {
    localStorage.setItem('theme', value);
    document.documentElement.classList.toggle('dark', value === 'dark');
    document.documentElement.classList.toggle('light', value === 'light');
  }
});

export const toggleTheme = () => theme.update((t) => (t === 'dark' ? 'light' : 'dark'));

// Следим за системными изменениями и применяем, только если пользователь не выбрал вручную
if (browser) {
  window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', (e) => {
    const manualChoice = localStorage.getItem('theme');
    if (!manualChoice) {
      theme.set(e.matches ? 'light' : 'dark');
    }
  });
}
