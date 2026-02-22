const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

export async function load({ fetch }) {
  try {
    const posts = await fetch(`${BASE}/blog?page=1&limit=6&sort=newest`).then(r => r.ok ? r.json() : { items: [], page: 1, pages: 1 });
    return { posts };
  } catch {
    return { posts: { items: [], page: 1, pages: 1 } };
  }
}
