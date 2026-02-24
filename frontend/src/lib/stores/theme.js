import { writable } from 'svelte/store';
import { browser } from '$app/environment';

function getInitialTheme() {
  if (!browser) return 'dark';
  const stored = localStorage.getItem('theme');
  if (stored === 'dark' || stored === 'light') return stored;
  return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
}

// Применяем класс СРАЗУ при загрузке модуля — до первого рендера,
// чтобы не было вспышки неправильной темы (FOUC)
if (browser) {
  const initial = getInitialTheme();
  document.documentElement.classList.toggle('dark',  initial === 'dark');
  document.documentElement.classList.toggle('light', initial === 'light');
}

export const theme = writable(getInitialTheme());

theme.subscribe((value) => {
  if (browser) {
    localStorage.setItem('theme', value);
    document.documentElement.classList.toggle('dark',  value === 'dark');
    document.documentElement.classList.toggle('light', value === 'light');
    // Плавный переход всей страницы
    document.documentElement.style.transition = 'background-color 0.25s ease, color 0.25s ease';
  }
});

export const toggleTheme = () => theme.update((t) => (t === 'dark' ? 'light' : 'dark'));

// Следим за системными изменениями — применяем только если пользователь не выбрал вручную
if (browser) {
  window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
      theme.set(e.matches ? 'light' : 'dark');
    }
  });
}
