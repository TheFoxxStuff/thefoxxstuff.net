import { browser } from '$app/environment';
import { authedFetch } from '$lib/loadWithAuth.js';
const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';
export const prerender = false;
export async function load({ fetch }) {
  if (!browser) return { images: { items: [], total: 0, page: 1, pages: 1 } };
  const images = await authedFetch(fetch, `${BASE}/upload?page=1&limit=24`);
  return { images: images ?? { items: [], total: 0, page: 1, pages: 1 } };
}
