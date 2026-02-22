import { browser } from '$app/environment';
import { authedFetch } from '$lib/loadWithAuth.js';
const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';
export const prerender = false;
export async function load({ fetch }) {
  if (!browser) return { stats: null, chartData: null, topContent: null };
  const [stats, chartData, topContent] = await Promise.all([
    authedFetch(fetch, `${BASE}/stats`),
    authedFetch(fetch, `${BASE}/stats/views/chart?days=30`),
    authedFetch(fetch, `${BASE}/stats/top?limit=5`),
  ]);
  return { stats, chartData, topContent };
}
