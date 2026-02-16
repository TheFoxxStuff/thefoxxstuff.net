import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const getInitialTheme = () => {
  if (browser) {
    const stored = localStorage.getItem('theme');
    if (stored) return stored;
  }
  return 'dark';
};

export const theme = writable(getInitialTheme());

theme.subscribe((value) => {
  if (browser) {
    localStorage.setItem('theme', value);
    document.documentElement.classList.toggle('dark', value === 'dark');
  }
});

export const toggleTheme = () => theme.update((t) => (t === 'dark' ? 'light' : 'dark'));
