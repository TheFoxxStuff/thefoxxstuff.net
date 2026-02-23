<script>
  /**
   * SEO.svelte — единый компонент для всех мета-тегов.
   *
   * Поддерживает: Google, Yandex, Bing, Twitter/X, VK, Telegram,
   * Discord, WhatsApp, iMessage, LinkedIn, Facebook, Slack, Signal.
   *
   * Props:
   *   title        — заголовок страницы (без суффикса сайта)
   *   description  — описание (до 160 символов)
   *   keywords     — ключевые слова через запятую
   *   image        — абсолютный URL OG-изображения (1200×630)
   *   imageWidth   — ширина OG-изображения (default: 1200)
   *   imageHeight  — высота OG-изображения (default: 630)
   *   imageAlt     — alt текст для OG-изображения
   *   type         — og:type: 'website' | 'article' | 'music.album' | 'profile' | 'music.song'
   *   url          — канонический URL страницы (абсолютный)
   *   noindex      — true для admin/приватных страниц
   *   nofollow     — true для nofollow
   *   article      — { publishedTime, modifiedTime, author, section, tags[] }
   *   profile      — { firstName, lastName, username }
   *   jsonLd       — JSON-LD объект (или массив объектов)
   *   titleFull    — если задан, используется как <title> без добавления siteName
   */
  import { SITE, truncate } from '$lib/seo.js';

  let {
    title = '',
    description = '',
    keywords = '',
    image = '',
    imageWidth = 1200,
    imageHeight = 630,
    imageAlt = '',
    type = 'website',
    url = '',
    noindex = false,
    nofollow = false,
    article = null,
    profile = null,
    jsonLd = null,
    titleFull = '',
  } = $props();

  // Computed values
  const finalTitle = $derived(titleFull || (title ? `${title} | ${SITE.name}` : `${SITE.name} — ${SITE.tagline}`));
  const finalDescription = $derived(truncate(description || SITE.description, 160));
  const finalImage = $derived(image || SITE.defaultImage);
  const finalImageAlt = $derived(imageAlt || title || SITE.name);
  const finalImageWidth = $derived(image ? imageWidth : SITE.defaultImageWidth);
  const finalImageHeight = $derived(image ? imageHeight : SITE.defaultImageHeight);
  const finalUrl = $derived(url || SITE.url);
  const finalKeywords = $derived(keywords || SITE.keywords);
  const robots = $derived([
    noindex ? 'noindex' : 'index',
    nofollow ? 'nofollow' : 'follow',
    'max-snippet:-1',
    'max-image-preview:large',
    'max-video-preview:-1',
  ].join(', '));

  // JSON-LD serialization
  const jsonLdStr = $derived(jsonLd ? JSON.stringify(Array.isArray(jsonLd) ? jsonLd : [jsonLd]) : null);
</script>

<svelte:head>
  <!-- ═══════════════════════════════════════════════════
       БАЗОВЫЕ ТЕГИ (Google, Yandex, Bing, все браузеры)
       ═══════════════════════════════════════════════════ -->
  <title>{finalTitle}</title>
  <meta name="description" content={finalDescription} />
  {#if finalKeywords}<meta name="keywords" content={finalKeywords} />{/if}
  <meta name="author" content={SITE.author} />
  <meta name="robots" content={robots} />
  <meta name="googlebot" content={robots} />
  <meta name="yandex" content="all" />
  <link rel="canonical" href={finalUrl} />

  <!-- Верификация поисковиков (заполни SITE.yandexVerification / googleVerification) -->
  {#if SITE.yandexVerification}
    <meta name="yandex-verification" content={SITE.yandexVerification} />
  {/if}
  {#if SITE.googleVerification}
    <meta name="google-site-verification" content={SITE.googleVerification} />
  {/if}

  <!-- ═══════════════════════════════════════════════════
       OPEN GRAPH
       Используют: VK, Telegram, Discord, WhatsApp,
       iMessage, Slack, Signal, LinkedIn, Facebook
       ═══════════════════════════════════════════════════ -->
  <meta property="og:site_name" content={SITE.name} />
  <meta property="og:type" content={type} />
  <meta property="og:title" content={finalTitle} />
  <meta property="og:description" content={finalDescription} />
  <meta property="og:url" content={finalUrl} />
  <meta property="og:locale" content={SITE.locale} />
  <meta property="og:locale:alternate" content={SITE.localeAlt} />
  <meta property="og:image" content={finalImage} />
  <meta property="og:image:secure_url" content={finalImage} />
  <meta property="og:image:type" content="image/jpeg" />
  <meta property="og:image:width" content={String(finalImageWidth)} />
  <meta property="og:image:height" content={String(finalImageHeight)} />
  <meta property="og:image:alt" content={finalImageAlt} />

  <!-- Article specific OG (Google News, VK article sharing) -->
  {#if article}
    {#if article.publishedTime}
      <meta property="article:published_time" content={article.publishedTime} />
    {/if}
    {#if article.modifiedTime}
      <meta property="article:modified_time" content={article.modifiedTime} />
    {/if}
    {#if article.author}
      <meta property="article:author" content={article.author} />
    {/if}
    {#if article.section}
      <meta property="article:section" content={article.section} />
    {/if}
    {#each (article.tags || []) as tag}
      <meta property="article:tag" content={tag} />
    {/each}
  {/if}

  <!-- Profile OG -->
  {#if profile}
    {#if profile.firstName}<meta property="profile:first_name" content={profile.firstName} />{/if}
    {#if profile.lastName}<meta property="profile:last_name" content={profile.lastName} />{/if}
    {#if profile.username}<meta property="profile:username" content={profile.username} />{/if}
  {/if}

  <!-- Music OG (Spotify, Apple Music embeds, VK Music) -->
  {#if type === 'music.album' || type === 'music.song'}
    <meta property="music:musician" content={SITE.url} />
  {/if}

  <!-- ═══════════════════════════════════════════════════
       TWITTER / X CARDS
       summary_large_image = большая карточка с изображением
       ═══════════════════════════════════════════════════ -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:site" content={SITE.twitter} />
  <meta name="twitter:creator" content={SITE.twitter} />
  <meta name="twitter:title" content={finalTitle} />
  <meta name="twitter:description" content={finalDescription} />
  <meta name="twitter:image" content={finalImage} />
  <meta name="twitter:image:alt" content={finalImageAlt} />
  <meta name="twitter:domain" content="thefoxxstuff.net" />
  <meta name="twitter:url" content={finalUrl} />

  <!-- ═══════════════════════════════════════════════════
       VK специфичные теги (дополнительно к OG)
       ═══════════════════════════════════════════════════ -->
  <meta property="vk:image" content={finalImage} />

  <!-- ═══════════════════════════════════════════════════
       ТЕХНИЧЕСКИЕ / PWA / МОБИЛЬНЫЕ
       ═══════════════════════════════════════════════════ -->
  <meta name="theme-color" content={SITE.themeColor} />
  <meta name="msapplication-TileColor" content={SITE.themeColor} />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  <meta name="apple-mobile-web-app-title" content={SITE.name} />
  <meta name="mobile-web-app-capable" content="yes" />
  <meta name="format-detection" content="telephone=no" />

  <!-- ═══════════════════════════════════════════════════
       JSON-LD STRUCTURED DATA (Google, Yandex Knowledge Graph)
       ═══════════════════════════════════════════════════ -->
  {#if jsonLdStr}
    {@html `<script type="application/ld+json">${jsonLdStr}</script>`}
  {/if}
</svelte:head>
