import { browser } from '$app/environment';
import { authedFetch } from '$lib/loadWithAuth.js';
const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';
export const prerender = false;
export async function load({ fetch }) {
  if (!browser) return { mapData: null };
  const mapData = await authedFetch(fetch, `${BASE}/views/map?days=30`);
  return { mapData };
}
