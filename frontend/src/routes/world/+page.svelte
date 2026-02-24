<script>
  import { SEO } from '$lib/components';
  import { SITE, canonicalUrl } from '$lib/seo.js';
  import { onMount } from 'svelte';

  let visible = false;
  onMount(() => {
    requestAnimationFrame(() => { visible = true; });
  });

  const characters = [
    {
      id: 'max',
      name: 'макс',
      species: 'арктический лис',
      color: '#e8f0ff',
      accent: '#a8c4ff',
      glyph: '◈',
      lines: [
        'белый. почти сливается со снегом если стоит неподвижно.',
        'не молчит потому что нечего сказать. молчит потому что слова требуют причины а большинство причин недостаточно весомые.',
        'делает музыку ночью когда всё остальное останавливается.',
        'любимое время — полярная ночь. не потому что романтично. просто тихо.',
      ],
      tracks: ['Low', 'Permafrost'],
    },
    {
      id: 'darya',
      name: 'дарья',
      species: 'арктическая лисица',
      color: '#fff0e0',
      accent: '#ffb870',
      glyph: '◉',
      lines: [
        'рыжая. тёплая — в буквальном смысле, рядом с ней чуть теплее.',
        'чувствует всё что макс не говорит вслух. это не телепатия — она просто смотрит внимательнее.',
        'рисует всё что попадается под руку включая обложки.',
        'не пытается его разморозить. просто рядом. это важнее.',
      ],
      tracks: ['Night rain', 'Everybody Screaming at Each Other and Nobody Listening to Me.'],
    },
    {
      id: 'mira',
      name: 'мира',
      species: 'ящерица',
      color: '#e8ffe8',
      accent: '#6ee870',
      glyph: '◬',
      lines: [
        'зелёная. золотые глаза. ящерица в якутском холоде — это противоречие которое она давно перестала объяснять.',
        'наблюдает. замечает детали которые остальные пропускают — не потому что умнее, а потому что смотрит под другим углом.',
        'на стене у неё схемы и заметки которые никто кроме неё не понимает до конца.',
        'в углу стоит сервер макса и тихо гудит. она говорит что привыкла.',
      ],
      tracks: ['Through the clouds', 'To the end of the world'],
    },
    {
      id: 'isak',
      name: 'исак',
      species: 'опоссум',
      color: '#f0e8ff',
      accent: '#c4a0ff',
      glyph: '◎',
      lines: [
        'серый. появляется ниоткуда.',
        'никто не помнит точно когда он появился. кажется однажды просто был на кухне и пил чай как будто всегда так и было.',
        'говорит странные вещи которые звучат как бессмыслица. через неделю оказывается что был прав.',
        'официально нигде не живёт. или живёт везде понемногу.',
      ],
      tracks: ['Mystic Forest', 'The World Revolving'],
    },
  ];
</script>

<SEO
  title="World"
  description="TheFoxxStuff — место, персонажи, лор. Село в Якутии, вечная мерзлота, четыре существа."
  keywords="TheFoxxStuff world, lore, characters, Макс, Дарья, Мира, Исак, Якутск"
  url={canonicalUrl('/world')}
/>

<div class="world-page" class:visible>

  <!-- Фоновый шум / атмосфера -->
  <div class="noise" aria-hidden="true"></div>

  <div class="content">

    <!-- Заголовок -->
    <header class="site-header fade-item" style="--delay: 0ms">
      <span class="breadcrumb"><a href="/">thefoxxstuff.net</a> / world</span>
    </header>

    <!-- Место -->
    <section class="place-section fade-item" style="--delay: 80ms">
      <div class="place-label">где это</div>
      <div class="place-text">
        <p>село. где-то рядом с якутском но достаточно отдельно чтобы считаться своим местом.</p>
        <p>зимой дорогу заметает. летом белые ночи. в любое время года здесь тихо в том смысле что тишина звучит.</p>
        <p>под землёй — вечная мерзлота. она была здесь до всех и останется после.</p>
      </div>
      <div class="temp-indicator" aria-label="температура снаружи">
        <span class="temp-val">−40°</span>
        <span class="temp-label">снаружи</span>
      </div>
    </section>

    <div class="divider fade-item" style="--delay: 120ms" aria-hidden="true">——————</div>

    <!-- Персонажи -->
    <section class="characters-section">
      <div class="chars-label fade-item" style="--delay: 160ms">кто здесь живёт</div>

      <div class="chars-grid">
        {#each characters as char, i}
          <article
            class="char-card fade-item"
            style="--delay: {200 + i * 80}ms; --char-color: {char.color}; --char-accent: {char.accent}"
          >
            <div class="char-top">
              <span class="char-glyph" style="color: {char.accent}">{char.glyph}</span>
              <div class="char-identity">
                <h2 class="char-name">{char.name}</h2>
                <span class="char-species">{char.species}</span>
              </div>
            </div>

            <div class="char-lines">
              {#each char.lines as line}
                <p>{line}</p>
              {/each}
            </div>

            <div class="char-tracks">
              {#each char.tracks as track}
                <span class="track-ref">"{track}"</span>
              {/each}
            </div>
          </article>
        {/each}
      </div>
    </section>

    <div class="divider fade-item" style="--delay: 600ms" aria-hidden="true">——————</div>

    <!-- Дома -->
    <section class="places-section fade-item" style="--delay: 640ms">
      <div class="place-label">места</div>

      <div class="places-grid">
        <div class="place-card">
          <div class="place-icon">⌂</div>
          <div class="place-info">
            <strong>дом макса и дарьи</strong>
            <p>куплен на деньги родителей. снаружи обычный якутский дом. внутри — слои. дарьина половина это тепло и цвет. максова это тихая комната с оборудованием которую он называет работой.</p>
            <p class="place-note">здесь рождается музыка.</p>
          </div>
        </div>

        <div class="place-card">
          <div class="place-icon">⊡</div>
          <div class="place-info">
            <strong>дом миры</strong>
            <p>построила сама. маленький, немного кривой по одному углу. каждая вещь на своём месте. на стене схемы.</p>
            <p class="place-note">в углу стоит сервер макса и тихо гудит.</p>
          </div>
        </div>
      </div>
    </section>

    <div class="divider fade-item" style="--delay: 720ms" aria-hidden="true">——————</div>

    <!-- Манифест -->
    <section class="manifesto fade-item" style="--delay: 760ms">
      <p class="manifesto-text">TheFoxxStuff — это не лейбл и не студия.</p>
      <p class="manifesto-text">это конкретный дом в конкретном селе где снаружи −40 а внутри мерцает оборудование и иногда получается музыка.</p>
      <p class="manifesto-text manifesto-end">всё что здесь сделано — сделано здесь.</p>
    </section>

    <footer class="page-footer fade-item" style="--delay: 840ms">
      <span>обновляется когда есть что сказать</span>
    </footer>

  </div>
</div>

<style>
  /* ── Reset / Base ─────────────────────────────────────────── */
  .world-page {
    min-height: 100vh;
    background: var(--bg);
    color: var(--w);
    font-family: 'Golos-Regular', system-ui, sans-serif;
    position: relative;
    overflow-x: hidden;
  }

  /* ── Noise texture ────────────────────────────────────────── */
  .noise {
    pointer-events: none;
    position: fixed;
    inset: 0;
    z-index: 0;
    opacity: 0.025;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
    background-size: 128px 128px;
  }

  /* ── Layout ───────────────────────────────────────────────── */
  .content {
    position: relative;
    z-index: 1;
    max-width: 640px;
    margin: 0 auto;
    padding: 48px 24px 96px;
  }

  /* ── Fade-in animation ────────────────────────────────────── */
  .fade-item {
    opacity: 0;
    transform: translateY(12px);
    transition: opacity 0.6s ease, transform 0.6s ease;
    transition-delay: var(--delay, 0ms);
  }
  .visible .fade-item {
    opacity: 1;
    transform: translateY(0);
  }

  /* ── Header ───────────────────────────────────────────────── */
  .site-header {
    margin-bottom: 64px;
  }
  .breadcrumb {
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: lowercase;
    color: var(--w30);
  }
  .breadcrumb a {
    color: var(--w40);
    text-decoration: none;
    transition: color 0.2s;
  }
  .breadcrumb a:hover {
    color: var(--w60);
  }

  /* ── Place section ────────────────────────────────────────── */
  .place-section {
    margin-bottom: 48px;
    display: grid;
    grid-template-columns: 80px 1fr auto;
    gap: 0 24px;
    align-items: start;
  }
  .place-label {
    font-size: 10px;
    letter-spacing: 0.15em;
    text-transform: lowercase;
    color: var(--w30);
    padding-top: 4px;
    white-space: nowrap;
  }
  .place-text {
    grid-column: 2;
  }
  .place-text p {
    font-size: 14px;
    line-height: 1.8;
    color: var(--w60);
    margin: 0 0 10px;
  }
  .place-text p:last-child { margin: 0; }

  .temp-indicator {
    grid-column: 3;
    grid-row: 1;
    text-align: right;
    padding-top: 2px;
  }
  .temp-val {
    display: block;
    font-family: 'DrukWideCyr', sans-serif;
    font-size: 22px;
    color: var(--w40);
    letter-spacing: -0.02em;
  }
  .temp-label {
    font-size: 9px;
    letter-spacing: 0.12em;
    text-transform: lowercase;
    color: var(--w20);
  }

  /* ── Divider ──────────────────────────────────────────────── */
  .divider {
    font-size: 11px;
    color: var(--w12);
    letter-spacing: 0.1em;
    margin: 40px 0;
    user-select: none;
  }

  /* ── Characters label ─────────────────────────────────────── */
  .chars-label {
    font-size: 10px;
    letter-spacing: 0.15em;
    text-transform: lowercase;
    color: var(--w30);
    margin-bottom: 32px;
  }

  /* ── Characters grid ──────────────────────────────────────── */
  .chars-grid {
    display: grid;
    gap: 2px;
  }

  .char-card {
    padding: 24px;
    border: 1px solid var(--w8);
    background: var(--w5);
    transition: border-color 0.3s, background 0.3s;
    cursor: default;
  }
  .char-card:hover {
    border-color: var(--w18);
    background: var(--w8);
  }

  .char-top {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    margin-bottom: 20px;
  }

  .char-glyph {
    font-size: 28px;
    line-height: 1;
    flex-shrink: 0;
    margin-top: 2px;
    opacity: 0.8;
  }

  .char-identity {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .char-name {
    font-family: 'DrukWideCyr', sans-serif;
    font-size: 20px;
    letter-spacing: 0.06em;
    text-transform: lowercase;
    color: var(--w);
    margin: 0;
    line-height: 1;
  }

  .char-species {
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: lowercase;
    color: var(--w30);
  }

  .char-lines {
    margin-bottom: 16px;
    padding-left: 44px;
  }
  .char-lines p {
    font-size: 13px;
    line-height: 1.75;
    color: var(--w50);
    margin: 0 0 8px;
  }
  .char-lines p:last-child { margin: 0; }

  .char-tracks {
    padding-left: 44px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .track-ref {
    font-size: 10px;
    letter-spacing: 0.08em;
    color: var(--w25);
    font-style: italic;
  }

  /* ── Places ───────────────────────────────────────────────── */
  .places-section {
    display: grid;
    grid-template-columns: 80px 1fr;
    gap: 0 24px;
    margin-bottom: 0;
  }

  .places-grid {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .place-card {
    display: flex;
    gap: 16px;
    align-items: flex-start;
  }
  .place-icon {
    font-size: 16px;
    color: var(--w30);
    flex-shrink: 0;
    margin-top: 2px;
    width: 20px;
    text-align: center;
  }
  .place-info strong {
    display: block;
    font-size: 12px;
    letter-spacing: 0.1em;
    text-transform: lowercase;
    color: var(--w60);
    margin-bottom: 6px;
    font-weight: 600;
  }
  .place-info p {
    font-size: 13px;
    line-height: 1.75;
    color: var(--w40);
    margin: 0 0 6px;
  }
  .place-note {
    color: var(--w25) !important;
    font-style: italic;
  }

  /* ── Manifesto ────────────────────────────────────────────── */
  .manifesto {
    padding: 32px 0;
  }
  .manifesto-text {
    font-size: 15px;
    line-height: 1.9;
    color: var(--w50);
    margin: 0 0 12px;
  }
  .manifesto-end {
    color: var(--w30);
    margin-top: 24px;
  }

  /* ── Footer ───────────────────────────────────────────────── */
  .page-footer {
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: lowercase;
    color: var(--w18);
    padding-top: 8px;
  }

  /* ── Mobile ───────────────────────────────────────────────── */
  @media (max-width: 500px) {
    .content { padding: 32px 16px 64px; }
    .place-section { grid-template-columns: 60px 1fr; }
    .temp-indicator { display: none; }
    .places-section { grid-template-columns: 60px 1fr; }
    .char-lines, .char-tracks { padding-left: 0; }
    .char-top { gap: 12px; }
    .char-glyph { font-size: 22px; }
  }

  /* ── w20/w25 helper (не в глобальном css) ─────────────────── */
  :global(html) { --w20: rgba(255,255,255,0.20); --w25: rgba(255,255,255,0.25); }
  :global(html.light) { --w20: rgba(0,0,0,0.15); --w25: rgba(0,0,0,0.20); }
</style>