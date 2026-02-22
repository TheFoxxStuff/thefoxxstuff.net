const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

export async function load({ fetch, params }) {
  try {
    const artwork = await fetch(`${BASE}/arts/${params.id}`).then(r => r.ok ? r.json() : null);
    return { artwork };
  } catch {
    return { artwork: null };
  }
}
