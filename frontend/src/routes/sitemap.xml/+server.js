import { SITE } from '$lib/seo.js';

const BASE_API = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

/** @type {import('./$types').RequestHandler} */
export async function GET({ fetch }) {
  const now = new Date().toISOString();

  // Static pages with priorities
  const staticPages = [
    { path: '/',       changefreq: 'daily',   priority: '1.0' },
    { path: '/music',  changefreq: 'weekly',  priority: '0.9' },
    { path: '/blog',   changefreq: 'weekly',  priority: '0.9' },
    { path: '/arts',   changefreq: 'weekly',  priority: '0.8' },
    { path: '/about',  changefreq: 'monthly', priority: '0.7' },
  ];

  // Fetch dynamic content (best-effort — silently skip on error)
  let musicItems = [], blogItems = [], artsItems = [];

  try {
    const [music, blog, arts] = await Promise.all([
      fetch(`${BASE_API}/music?page=1&limit=200`).then(r => r.ok ? r.json() : { items: [] }),
      fetch(`${BASE_API}/blog?page=1&limit=200`).then(r => r.ok ? r.json() : { items: [] }),
      fetch(`${BASE_API}/arts?page=1&limit=200`).then(r => r.ok ? r.json() : { items: [] }),
    ]);
    musicItems = music.items || [];
    blogItems  = blog.items  || [];
    artsItems  = arts.items  || [];
  } catch {
    // API unavailable during static build — static pages only
  }

  const url = (path) => `${SITE.url}${path}`;
  const lastmod = (item) => item.updated_at || item.created_at || now;

  const entries = [
    // Static pages
    ...staticPages.map(p => `
  <url>
    <loc>${url(p.path)}</loc>
    <lastmod>${now}</lastmod>
    <changefreq>${p.changefreq}</changefreq>
    <priority>${p.priority}</priority>
  </url>`),

    // Music releases
    ...musicItems.map(item => `
  <url>
    <loc>${url(`/music/${item.slug || item._id}`)}</loc>
    <lastmod>${lastmod(item)}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
    ${item.cover_image ? `<image:image>
      <image:loc>${BASE_API}/upload/file/${item.cover_image}</image:loc>
      <image:title>${escapeXml(item.title)}</image:title>
    </image:image>` : ''}
  </url>`),

    // Blog posts
    ...blogItems.map(item => `
  <url>
    <loc>${url(`/blog/${item.slug || item._id}`)}</loc>
    <lastmod>${lastmod(item)}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
    ${item.cover_image ? `<image:image>
      <image:loc>${BASE_API}/upload/file/${item.cover_image}</image:loc>
      <image:title>${escapeXml(item.title)}</image:title>
    </image:image>` : ''}
  </url>`),

    // Artworks
    ...artsItems.map(item => `
  <url>
    <loc>${url(`/arts/${item.slug || item._id}`)}</loc>
    <lastmod>${lastmod(item)}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
    ${item.image ? `<image:image>
      <image:loc>${BASE_API}/upload/file/${item.image}</image:loc>
      <image:title>${escapeXml(item.title)}</image:title>
    </image:image>` : ''}
  </url>`),
  ];

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset
  xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
    http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
${entries.join('')}
</urlset>`;

  return new Response(xml.trim(), {
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'public, max-age=3600', // 1 hour cache
    },
  });
}

function escapeXml(str = '') {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}
