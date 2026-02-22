const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

export async function load({ fetch }) {
  try {
    const [music, blog, arts, banner] = await Promise.all([
      fetch(`${BASE}/music?page=1&limit=4`).then(r => r.ok ? r.json() : { items: [], page: 1, pages: 1 }),
      fetch(`${BASE}/blog?page=1&limit=2&sort=newest`).then(r => r.ok ? r.json() : { items: [], page: 1, pages: 1 }),
      fetch(`${BASE}/arts?page=1&limit=6&sort=newest`).then(r => r.ok ? r.json() : { items: [] }),
      fetch(`${BASE}/banner`).then(r => r.ok ? r.json() : { slides: [] }),
    ]);
    return { music, blog, arts: arts.items ?? [], banner };
  } catch {
    return { music: { items: [], page: 1, pages: 1 }, blog: { items: [], page: 1, pages: 1 }, arts: [], banner: { slides: [] } };
  }
}
