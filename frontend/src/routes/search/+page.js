export const prerender = false;
export async function load({ fetch, url }) {
  const q = url.searchParams.get('q') || '';
  if (!q.trim()) return { query: '', results: null };
  const BASE_URL = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';
  try {
    const results = await fetch(`${BASE_URL}/stats/search?q=${encodeURIComponent(q)}`).then(r => r.ok ? r.json() : null);
    return { query: q, results };
  } catch { return { query: q, results: null }; }
}
