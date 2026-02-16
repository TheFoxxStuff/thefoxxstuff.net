import { browser } from '$app/environment';
import { auth } from '$lib/stores/auth.js';

export const API_BASE = 'http://localhost:8000/api';

const getToken = () => {
  if (!browser) return null;
  try {
    const stored = localStorage.getItem('auth');
    if (stored) return JSON.parse(stored).token;
  } catch {}
  return null;
};

async function request(endpoint, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  
  const response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
  
  if (response.status === 401) {
    if (browser) {
      auth.logout();
      window.location.href = '/auth/login';
    }
    throw new Error('Not authenticated');
  }
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `Error: ${response.status}`);
  }
  
  return response.json();
}

async function uploadFile(endpoint, file, params = {}) {
  const token = getToken();
  const formData = new FormData();
  formData.append('file', file);
  
  // Build URL with query params
  const url = new URL(`${API_BASE}${endpoint}`);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      url.searchParams.append(key, value);
    }
  });
  
  const headers = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  
  const response = await fetch(url.toString(), {
    method: 'POST',
    headers,
    body: formData
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(error.detail || `Error: ${response.status}`);
  }
  
  return response.json();
}

async function uploadFiles(endpoint, files, params = {}) {
  const token = getToken();
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }
  
  // Build URL with query params
  const url = new URL(`${API_BASE}${endpoint}`);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      url.searchParams.append(key, value);
    }
  });
  
  const headers = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  
  const response = await fetch(url.toString(), {
    method: 'POST',
    headers,
    body: formData
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(error.detail || `Error: ${response.status}`);
  }
  
  return response.json();
}

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
    list: (page = 1, limit = 10) => request(`/music?page=${page}&limit=${limit}`),
    featured: () => request('/music/featured'),
    get: (id) => request(`/music/${id}`),
    getBySlug: (slug) => request(`/music/by-slug/${slug}`),
    create: (data) => request('/music', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/music/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => request(`/music/${id}`, { method: 'DELETE' })
  },
  blog: {
    list: (page = 1, limit = 10, search = '', sort = 'newest') => {
      let url = `/blog?page=${page}&limit=${limit}&sort=${sort}`;
      if (search && search.trim()) url += `&search=${encodeURIComponent(search)}`;
      return request(url);
    },
    get: (id) => request(`/blog/${id}`),
    getBySlug: (slug) => request(`/blog/by-slug/${slug}`),
    create: (data) => request('/blog', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/blog/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => request(`/blog/${id}`, { method: 'DELETE' })
  },
  arts: {
    list: (page = 1, limit = 12, year = null, sort = 'newest') => {
      let url = `/arts?page=${page}&limit=${limit}&sort=${sort}`;
      if (year) url += `&year=${year}`;
      return request(url);
    },
    grouped: (limit = 7) => request(`/arts/grouped?limit_per_year=${limit}`),
    years: () => request('/arts/years'),
    get: (id) => request(`/arts/${id}`),
    getBySlug: (slug) => request(`/arts/by-slug/${slug}`),
    create: (data) => request('/arts', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/arts/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => request(`/arts/${id}`, { method: 'DELETE' })
  },
  links: {
    list: () => request('/links'),
    create: (data) => request('/links', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/links/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => request(`/links/${id}`, { method: 'DELETE' })
  },
  banner: {
    get: () => request('/banner'),
    update: (data) => request('/banner', { method: 'PUT', body: JSON.stringify(data) }),
    addSlide: (title, image, link = null) => request(`/banner/slide?title=${encodeURIComponent(title)}&image=${image}${link ? `&link=${encodeURIComponent(link)}` : ''}`, { method: 'POST' }),
    removeSlide: (slideId) => request(`/banner/slide/${slideId}`, { method: 'DELETE' })
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
    getUrl: (path, variant = 'medium') => `${API_BASE}/upload/file/${path}`,
    // Audio
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
    record: (entityType, entityId) => request(`/views/record?entity_type=${entityType}&entity_id=${entityId}`, { method: 'POST' }),
    map: (days = 30) => request(`/views/map?days=${days}`),
    recent: (page = 1, limit = 50) => request(`/views/recent?page=${page}&limit=${limit}`)
  },
  about: {
    get: () => request('/about'),
    update: (data) => request('/about', { method: 'PUT', body: JSON.stringify(data) })
  },
  profile: {
    me: () => request('/profile/me'),
    get: (username) => request(`/profile/${username}`),
    update: (data) => request('/profile/me', { method: 'PUT', body: JSON.stringify(data) }),
    uploadAvatar: (file, cropX = 0, cropY = 0, cropSize = 0) =>
      uploadFile('/profile/me/avatar', file, { crop_x: cropX, crop_y: cropY, crop_size: cropSize }),
    deleteAvatar: () => request('/profile/me/avatar', { method: 'DELETE' }),
  },
  chat: {
    messages: (limit = 50) => request(`/chat/messages?limit=${limit}`),
  }
};

// Helper to get image URL from image object or ID
export function getImageUrl(imageInfo, variant = 'medium') {
  if (!imageInfo) return null;
  if (typeof imageInfo === 'string') return imageInfo;
  const path = imageInfo[variant] || imageInfo.medium || imageInfo.thumb;
  if (!path) return null;
  return `${API_BASE}/upload/file/${path}`;
}

// Helper to generate SEO-friendly slug
export function generateSlug(title) {
  return title
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '');
}
