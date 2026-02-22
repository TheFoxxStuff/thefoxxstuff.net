/**
 * Central SEO configuration for TheFoxxStuff.net
 * Edit this file to update site-wide SEO defaults.
 */

export const SITE = {
  name: 'TheFoxxStuff',
  tagline: 'Hardcore · Breakcore · Drum\'n\'Bass',
  url: 'https://thefoxxstuff.net',
  description: 'TheFoxxStuff — musician from Yakutia, Russia. Hardcore, Breakcore and Drum\'n\'Bass producer. Listen to music, read the blog, browse artworks.',
  keywords: 'TheFoxxStuff, hardcore, breakcore, drum and bass, dnb, yakutia, yakutsk, electronic music, producer, music producer',
  author: 'TheFoxxStuff',
  email: 'mail@thefoxxstuff.net',
  locale: 'en_US',
  localeAlt: 'ru_RU',
  themeColor: '#00FF88',

  // Default OG image (place a 1200×630 image in /static/)
  defaultImage: 'https://thefoxxstuff.net/og-default.jpg',
  defaultImageWidth: 1200,
  defaultImageHeight: 630,

  // Favicon / Apple touch icon
  favicon: '/favicon.svg',
  appleTouchIcon: '/apple-touch-icon.png', // place 180x180 in /static/

  // Social handles
  twitter: '@thefoxxstuff',
  twitterUrl: 'https://twitter.com/thefoxxstuff',
  vk: 'thefoxxstuff',
  vkUrl: 'https://vk.com/thefoxxstuff',
  telegram: 'thefoxxstuff',
  telegramUrl: 'https://t.me/thefoxxstuff',
  bandcamp: 'https://thefoxxstuff.bandcamp.com',
  soundcloud: 'https://soundcloud.com/thefoxxstuff',

  // Verification tokens (fill in after adding site to webmaster tools)
  yandexVerification: '',   // Яндекс.Вебмастер → Добавить сайт → HTML-мета
  googleVerification: '',   // Google Search Console → HTML-тег
};

/**
 * Build a full canonical URL from a path.
 * @param {string} path - e.g. '/blog/my-post'
 */
export function canonicalUrl(path = '') {
  return `${SITE.url}${path.startsWith('/') ? path : '/' + path}`;
}

/**
 * Truncate a string to maxLen characters, preserving word boundaries.
 */
export function truncate(str = '', maxLen = 160) {
  if (!str || str.length <= maxLen) return str;
  return str.slice(0, maxLen).replace(/\s+\S*$/, '') + '…';
}
