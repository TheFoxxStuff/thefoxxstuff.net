const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

export async function load({ fetch }) {
  try {
    const [featured, releases] = await Promise.all([
      fetch(`${BASE}/music/featured`).then(r => r.ok ? r.json() : null),
      fetch(`${BASE}/music?page=1&limit=12`).then(r => r.ok ? r.json() : { items: [], page: 1, pages: 1 }),
    ]);
    return { featured, releases };
  } catch {
    return { featured: null, releases: { items: [], page: 1, pages: 1 } };
  }
}
