import { browser } from '$app/environment';
import { auth } from '$lib/stores/auth.js';

export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

// ─── In-memory cache ────────────────────────────────────────────────
const CACHE_TTL = 30_000; // 30 секунд
const cache = new Map(); // key → { data, ts }
const inflight = new Map(); // key → Promise (дедупликация параллельных запросов)

export function invalidateCache(prefix = null) {
  if (prefix === null) {
    cache.clear();
  } else {
    for (const k of cache.keys()) {
      if (k.startsWith(prefix)) cache.delete(k);
    }
  }
}

// ─── Token ──────────────────────────────────────────────────────────
const getToken = () => {
  if (!browser) return null;
  try {
    const stored = localStorage.getItem('auth');
    if (stored) return JSON.parse(stored).token;
  } catch {}
  return null;
};

// ─── Fetch с таймаутом ───────────────────────────────────────────────
const DEFAULT_TIMEOUT = 15_000;

async function fetchWithTimeout(url, options = {}, timeoutMs = DEFAULT_TIMEOUT) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

// ─── Базовый request ─────────────────────────────────────────────────
async function request(endpoint, options = {}, { cacheable = false, ttl = CACHE_TTL } = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const isGET = !options.method || options.method === 'GET';
  const key = endpoint;

  if (cacheable && isGET) {
    const hit = cache.get(key);
    if (hit && Date.now() - hit.ts < ttl) return hit.data;
    if (inflight.has(key)) return inflight.get(key);
  }

  const run = async () => {
    try {
      const response = await fetchWithTimeout(`${API_BASE}${endpoint}`, { ...options, headers });

      if (response.status === 401) {
        if (browser) { auth.logout(); window.location.href = '/auth/login'; }
        throw new Error('Not authenticated');
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `Error: ${response.status}`);
      }

      const data = await response.json();
      if (cacheable && isGET) cache.set(key, { data, ts: Date.now() });
      return data;
    } finally {
      inflight.delete(key);
    }
  };

  if (cacheable && isGET) {
    const promise = run();
    inflight.set(key, promise);
    return promise;
  }

  return run();
}

// ─── Upload helpers ──────────────────────────────────────────────────
async function uploadFile(endpoint, file, params = {}) {
  const token = getToken();
  const formData = new FormData();
  formData.append('file', file);
  const url = new URL(`${API_BASE}${endpoint}`);
  Object.entries(params).forEach(([k, v]) => {
    if (v !== null && v !== undefined) url.searchParams.append(k, v);
  });
  const headers = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const response = await fetchWithTimeout(url.toString(), { method: 'POST', headers, body: formData }, 60_000);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(error.detail || `Error: ${response.status}`);
  }
  return response.json();
}

async function uploadFiles(endpoint, files, params = {}) {
  const token = getToken();
  const formData = new FormData();
  for (const file of files) formData.append('files', file);
  const url = new URL(`${API_BASE}${endpoint}`);
  Object.entries(params).forEach(([k, v]) => {
    if (v !== null && v !== undefined) url.searchParams.append(k, v);
  });
  const headers = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const response = await fetchWithTimeout(url.toString(), { method: 'POST', headers, body: formData }, 60_000);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(error.detail || `Error: ${response.status}`);
  }
  return response.json();
}

// ─── API ──────────────────────────────────────────────────────────────
export const api = {
  auth: {
    register: (data) => request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
    login: (data) => request('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
    me: () => request('/auth/me'),
    users: () => request('/auth/users'),
    updateRole: (userId, role) => request(`/auth/users/${userId}/role?role=${role}`, { method: 'PUT' }),
    deleteUser: (userId) => request(`/auth/users/${userId}`, { method: 'DELETE' })
  },
  music: {
    list: (page = 1, limit = 10) => request(`/music?page=${page}&limit=${limit}`, {}, { cacheable: true }),
    featured: () => request('/music/featured', {}, { cacheable: true }),
    get: (id) => request(`/music/${id}`, {}, { cacheable: true }),
    getBySlug: (slug) => request(`/music/by-slug/${slug}`, {}, { cacheable: true }),
    create: (data) => { invalidateCache('/music'); return request('/music', { method: 'POST', body: JSON.stringify(data) }); },
    update: (id, data) => { invalidateCache('/music'); return request(`/music/${id}`, { method: 'PUT', body: JSON.stringify(data) }); },
    delete: (id) => { invalidateCache('/music'); return request(`/music/${id}`, { method: 'DELETE' }); }
  },
  blog: {
    list: (page = 1, limit = 10, search = '', sort = 'newest') => {
      let url = `/blog?page=${page}&limit=${limit}&sort=${sort}`;
      if (search && search.trim()) url += `&search=${encodeURIComponent(search)}`;
      return request(url, {}, { cacheable: !search });
    },
    get: (id) => request(`/blog/${id}`, {}, { cacheable: true }),
    getBySlug: (slug) => request(`/blog/by-slug/${slug}`, {}, { cacheable: true }),
    create: (data) => { invalidateCache('/blog'); return request('/blog', { method: 'POST', body: JSON.stringify(data) }); },
    update: (id, data) => { invalidateCache('/blog'); return request(`/blog/${id}`, { method: 'PUT', body: JSON.stringify(data) }); },
    delete: (id) => { invalidateCache('/blog'); return request(`/blog/${id}`, { method: 'DELETE' }); }
  },
  arts: {
    list: (page = 1, limit = 12, year = null, sort = 'newest') => {
      let url = `/arts?page=${page}&limit=${limit}&sort=${sort}`;
      if (year) url += `&year=${year}`;
      return request(url, {}, { cacheable: true });
    },
    grouped: (limit = 7) => request(`/arts/grouped?limit_per_year=${limit}`, {}, { cacheable: true }),
    years: () => request('/arts/years', {}, { cacheable: true }),
    get: (id) => request(`/arts/${id}`, {}, { cacheable: true }),
    getBySlug: (slug) => request(`/arts/by-slug/${slug}`, {}, { cacheable: true }),
    create: (data) => { invalidateCache('/arts'); return request('/arts', { method: 'POST', body: JSON.stringify(data) }); },
    update: (id, data) => { invalidateCache('/arts'); return request(`/arts/${id}`, { method: 'PUT', body: JSON.stringify(data) }); },
    delete: (id) => { invalidateCache('/arts'); return request(`/arts/${id}`, { method: 'DELETE' }); }
  },
  links: {
    list: () => request('/links', {}, { cacheable: true }),
    create: (data) => { invalidateCache('/links'); return request('/links', { method: 'POST', body: JSON.stringify(data) }); },
    update: (id, data) => { invalidateCache('/links'); return request(`/links/${id}`, { method: 'PUT', body: JSON.stringify(data) }); },
    delete: (id) => { invalidateCache('/links'); return request(`/links/${id}`, { method: 'DELETE' }); }
  },
  banner: {
    get: () => request('/banner', {}, { cacheable: true }),
    update: (data) => { invalidateCache('/banner'); return request('/banner', { method: 'PUT', body: JSON.stringify(data) }); },
    addSlide: (title, image, link = null) => { invalidateCache('/banner'); return request(`/banner/slide?title=${encodeURIComponent(title)}&image=${image}${link ? `&link=${encodeURIComponent(link)}` : ''}`, { method: 'POST' }); },
    removeSlide: (slideId) => { invalidateCache('/banner'); return request(`/banner/slide/${slideId}`, { method: 'DELETE' }); }
  },
  upload: {
    image: (file, category = 'markdown', customName = null, parentId = null, isGallery = false) =>
      uploadFile('/upload', file, { category, custom_name: customName, parent_id: parentId, is_gallery: isGallery }),
    images: (files, category = 'markdown', parentId = null, isGallery = false) =>
      uploadFiles('/upload/multiple', files, { category, parent_id: parentId, is_gallery: isGallery }),
    markdown: (file) => uploadFile('/upload/markdown', file),
    getInfo: (id) => request(`/upload/${id}`),
    delete: (id) => request(`/upload/${id}`, { method: 'DELETE' }),
    list: (page = 1, limit = 20, category = null, unusedOnly = false) => {
      let url = `/upload?page=${page}&limit=${limit}`;
      if (category) url += `&category=${category}`;
      if (unusedOnly) url += `&unused_only=true`;
      return request(url);
    },
    cleanup: () => request('/upload/cleanup', { method: 'POST' }),
    getUrl: (path) => `${API_BASE}/upload/file/${path}`,
    audio: (file, customName = null, generateMp3128 = false) =>
      uploadFile('/upload/audio', file, { custom_name: customName, generate_mp3_128: generateMp3128 }),
    audioInfo: (id) => request(`/upload/audio/${id}`),
    audioDelete: (id) => request(`/upload/audio/${id}`, { method: 'DELETE' }),
    audioToggleMp3128: (id, enable) => request(`/upload/audio/${id}/toggle-mp3-128?enable=${enable}`, { method: 'PUT' }),
    audioFileUrl: (path) => `${API_BASE}/upload/file/${path}`,
    writeMetadata: (data) => request('/upload/audio/write-metadata', { method: 'POST', body: JSON.stringify(data) })
  },
  stats: {
    get: () => request('/stats'),
    viewsChart: (days = 30) => request(`/stats/views/chart?days=${days}`),
    top: (limit = 5) => request(`/stats/top?limit=${limit}`),
    recentViews: (days = 7) => request(`/stats/recent-views?days=${days}`),
    search: (q) => request(`/stats/search?q=${encodeURIComponent(q)}`)
  },
  views: {
    record: (entityType, entityId) => {
      // Deduplicate per session: don't record if already done this session
      if (browser) {
        const key = `view_recorded_${entityType}_${entityId}`;
        if (sessionStorage.getItem(key)) return;
        sessionStorage.setItem(key, '1');
      }
      // Use fetch directly to avoid cache and ensure POST is sent
      const token = getToken();
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;
      fetch(`${API_BASE}/views/record?entity_type=${entityType}&entity_id=${entityId}`, {
        method: 'POST',
        headers,
      }).catch(() => {});
    },
    map: (days = 30) => request(`/views/map?days=${days}`),
    recent: (page = 1, limit = 50) => request(`/views/recent?page=${page}&limit=${limit}`)
  },
  about: {
    get: () => request('/about', {}, { cacheable: true }),
    update: (data) => { invalidateCache('/about'); return request('/about', { method: 'PUT', body: JSON.stringify(data) }); }
  },
  profile: {
    me: () => request('/profile/me'),
    get: (username) => request(`/profile/${username}`, {}, { cacheable: true }),
    update: (data) => { invalidateCache('/profile'); return request('/profile/me', { method: 'PUT', body: JSON.stringify(data) }); },
    uploadAvatar: (file, cropX = 0, cropY = 0, cropSize = 0) =>
      uploadFile('/profile/me/avatar', file, { crop_x: cropX, crop_y: cropY, crop_size: cropSize }),
    deleteAvatar: () => request('/profile/me/avatar', { method: 'DELETE' })
  },
  chat: {
    messages: (limit = 50) => request(`/chat/messages?limit=${limit}`)
  },
  presence: {
    online: () => fetch(`${API_BASE}/presence/online`).then(r => r.ok ? r.json() : { users: [], count: 0 }),
    viewing: (entityType, entityId) =>
      fetch(`${API_BASE}/presence/viewing/${entityType}/${entityId}`)
        .then(r => r.ok ? r.json() : { users: [], count: 0 }),
  },
};

// ─── Image URL helpers ────────────────────────────────────────────────
export function getImageUrl(imageInfo, variant = 'medium') {
  if (!imageInfo) return null;
  if (typeof imageInfo === 'string') return imageInfo;
  const path = imageInfo[variant] || imageInfo.medium || imageInfo.thumb;
  if (!path) return null;
  return `${API_BASE}/upload/file/${path}`;
}

/**
 * Адаптивный вариант: выбирает размер под ширину экрана.
 * mobile(≤640) → medium, tablet(≤1280) → large, desktop → original
 */
export function getResponsiveImageUrl(imageInfo) {
  if (!imageInfo || typeof imageInfo === 'string') return imageInfo ?? null;
  if (!browser) return getImageUrl(imageInfo, 'medium');
  const w = window.innerWidth;
  const variant = w <= 640 ? 'medium' : w <= 1280 ? 'large' : 'original';
  return getImageUrl(imageInfo, variant);
}

// ─── Slug helper ──────────────────────────────────────────────────────
export function generateSlug(title) {
  return title
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '');
}
