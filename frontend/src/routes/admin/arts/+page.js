import { browser } from '$app/environment';
import { authedFetch } from '$lib/loadWithAuth.js';
const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';
export const prerender = false;
export async function load({ fetch }) {
  if (!browser) return { artworks: [] };
  const data = await authedFetch(fetch, `${BASE}/arts?page=1&limit=100&sort=newest`);
  return { artworks: data?.items ?? [] };
}
