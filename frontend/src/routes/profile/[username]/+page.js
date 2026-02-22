import { browser } from '$app/environment';
const BASE_URL = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';
export const prerender = false;
export async function load({ fetch, params }) {
  try {
    const profile = await fetch(`${BASE_URL}/profile/${params.username}`).then(r => r.ok ? r.json() : null);
    return { profile };
  } catch { return { profile: null }; }
}
