import { browser } from '$app/environment';
import { authedFetch } from '$lib/loadWithAuth.js';
import { redirect } from '@sveltejs/kit';

const BASE_URL = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';
export const prerender = false;
// Auth token живёт в localStorage — загружаем данные только на клиенте
export const ssr = false;

export async function load({ fetch }) {
  if (!browser) return { profile: null };

  // FIX: проверяем наличие токена до запроса
  let token = null;
  try { token = JSON.parse(localStorage.getItem('auth'))?.token ?? null; } catch {}

  if (!token) {
    // Нет токена — редиректим сразу, не ждём 401 от сервера
    throw redirect(302, '/auth/login');
  }

  const profile = await authedFetch(fetch, `${BASE_URL}/profile/me`);

  // FIX: если profile null (токен протух) — редиректим вместо краша
  if (!profile) {
    throw redirect(302, '/auth/login');
  }

  return { profile };
}
