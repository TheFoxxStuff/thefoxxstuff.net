const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

export async function load({ fetch }) {
  try {
    const [grouped, years] = await Promise.all([
      fetch(`${BASE}/arts/grouped?limit_per_year=100`).then(r => r.ok ? r.json() : {}),
      fetch(`${BASE}/arts/years`).then(r => r.ok ? r.json() : []),
    ]);
    return { grouped, years };
  } catch {
    return { grouped: {}, years: [] };
  }
}
