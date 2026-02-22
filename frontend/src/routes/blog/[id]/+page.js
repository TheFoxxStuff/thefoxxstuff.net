const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

export async function load({ fetch, params }) {
  try {
    const post = await fetch(`${BASE}/blog/${params.id}`).then(r => r.ok ? r.json() : null);
    return { post };
  } catch {
    return { post: null };
  }
}
