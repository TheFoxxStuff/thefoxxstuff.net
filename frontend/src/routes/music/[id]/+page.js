const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

export async function load({ fetch, params }) {
  try {
    const release = await fetch(`${BASE}/music/${params.id}`).then(r => r.ok ? r.json() : null);
    return { release };
  } catch {
    return { release: null };
  }
}
