import { browser } from '$app/environment';
import { authedFetch } from '$lib/loadWithAuth.js';
const BASE_URL = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';
export const prerender = false;
export async function load({ fetch }) {
  if (!browser) return { profile: null };
  const profile = await authedFetch(fetch, `${BASE_URL}/profile/me`);
  return { profile };
}
