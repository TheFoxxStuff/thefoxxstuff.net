import { browser } from '$app/environment';
import { authedFetch } from '$lib/loadWithAuth.js';
const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';
export const prerender = false;
export async function load({ fetch }) {
  if (!browser) return { users: [] };
  const users = await authedFetch(fetch, `${BASE}/auth/users`);
  return { users: users ?? [] };
}
