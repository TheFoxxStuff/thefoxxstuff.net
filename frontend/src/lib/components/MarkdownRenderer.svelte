<script>
  import { API_BASE } from '$lib/api';
  import ImageLightbox from './ImageLightbox.svelte';

  let { content = '', class: className = '' } = $props();

  // API_BASE = "https://api.thefoxxstuff.net/api"  →  origin = "https://api.thefoxxstuff.net"
  const API_ORIGIN = API_BASE.replace(/\/api$/, '');

  function resolveImageSrc(src) {
    if (!src) return '';
    if (src.startsWith('http://') || src.startsWith('https://')) return src;
    if (src.startsWith('/api/')) return `${API_ORIGIN}${src}`;
    if (src.startsWith('api/'))  return `${API_ORIGIN}/${src}`;
    return src;
  }

  function escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // ── Image click state ───────────────────────────────────────────
  let lbOpen = $state(false);
  let lbSrc  = $state('');
  let lbAlt  = $state('');

  // Unique ID so multiple MarkdownRenderer instances don't clash
  const uid = Math.random().toString(36).slice(2, 8);

  function parseMarkdown(md) {
    if (!md) return '';

    const codeBlocks  = [];
    const inlineCodes = [];
    const imageBlocks = [];

    // ── Fenced code blocks ──────────────────────────────────────
    md = md.replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) => {
      const idx = codeBlocks.length;
      const langLabel = lang ? `<span class="md-code-lang">${escapeHtml(lang)}</span>` : '';
      codeBlocks.push(
        `<div class="md-code-block">${langLabel}<pre><code>${escapeHtml(code.trim())}</code></pre></div>`
      );
      return `\x00CODE${idx}\x00`;
    });

    // ── Inline code ─────────────────────────────────────────────
    md = md.replace(/`([^`\n]+)`/g, (_, code) => {
      const idx = inlineCodes.length;
      inlineCodes.push(`<code class="md-inline-code">${escapeHtml(code)}</code>`);
      return `\x00INLINE${idx}\x00`;
    });

    // ── Block images (own line) → Sanity-style figure ───────────
    md = md.replace(/^!\[([^\]]*)\]\(([^)]+)\)\s*$/gm, (_, alt, src) => {
      const idx     = imageBlocks.length;
      const fullSrc = resolveImageSrc(src.trim());
      const altText = escapeHtml(alt || '');
      imageBlocks.push(
        `<figure class="md-figure" data-md-img="${uid}-${idx}">` +
          `<div class="md-img-wrapper" role="button" tabindex="0" aria-label="View image" data-md-img="${uid}-${idx}">` +
            `<img src="${fullSrc}" alt="${altText}" class="md-img" loading="lazy" />` +
            `<div class="md-img-overlay"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg></div>` +
          `</div>` +
          (alt ? `<figcaption class="md-figcaption">${altText}</figcaption>` : '') +
        `</figure>`
      );
      return `\x00IMG${idx}\x00`;
    });

    // ── Tables ───────────────────────────────────────────────────
    md = md.replace(/^(\|.+\|\s*\n\|[-| :]+\|\s*\n(?:\|.+\|\s*\n?)*)/gm, (tableBlock) => {
      const lines = tableBlock.trim().split('\n');
      if (lines.length < 2) return tableBlock;
      const headers  = lines[0].split('|').map(h => h.trim()).filter(Boolean);
      const alignRow = lines[1].split('|').map(c => c.trim()).filter(Boolean);
      const aligns   = alignRow.map(c =>
        c.startsWith(':') && c.endsWith(':') ? 'center' : c.endsWith(':') ? 'right' : 'left'
      );
      const ths = headers.map((h, i) => `<th style="text-align:${aligns[i]||'left'}">${h}</th>`).join('');
      const bodyRows = lines.slice(2).map(row => {
        const cells = row.split('|').map(c => c.trim()).filter(Boolean);
        const tds = cells.map((c, i) => `<td style="text-align:${aligns[i]||'left'}">${inlineFormat(c)}</td>`).join('');
        return `<tr>${tds}</tr>`;
      }).join('');
      return `<table class="md-table"><thead><tr>${ths}</tr></thead><tbody>${bodyRows}</tbody></table>`;
    });

    // ── Headings ─────────────────────────────────────────────────
    md = md.replace(/^###### (.+)$/gm, '<h6 class="md-h6">$1</h6>');
    md = md.replace(/^##### (.+)$/gm,  '<h5 class="md-h5">$1</h5>');
    md = md.replace(/^#### (.+)$/gm,   '<h4 class="md-h4">$1</h4>');
    md = md.replace(/^### (.+)$/gm,    '<h3 class="md-h3">$1</h3>');
    md = md.replace(/^## (.+)$/gm,     '<h2 class="md-h2">$1</h2>');
    md = md.replace(/^# (.+)$/gm,      '<h1 class="md-h1">$1</h1>');

    // ── HR ───────────────────────────────────────────────────────
    md = md.replace(/^[-*_]{3,}\s*$/gm, '<hr class="md-hr" />');

    // ── Blockquote ───────────────────────────────────────────────
    md = md.replace(/^> (.+)$/gm, '<blockquote class="md-blockquote">$1</blockquote>');
    md = md.replace(/<\/blockquote>\n<blockquote class="md-blockquote">/g, '\n');

    // ── Lists ────────────────────────────────────────────────────
    md = md.replace(/((?:^[-*+] .+$\n?)+)/gm, (block) => {
      const items = block.trim().split('\n')
        .map(l => `<li>${inlineFormat(l.replace(/^[-*+] /, ''))}</li>`).join('');
      return `<ul class="md-ul">${items}</ul>`;
    });
    md = md.replace(/((?:^\d+\. .+$\n?)+)/gm, (block) => {
      const items = block.trim().split('\n')
        .map(l => `<li>${inlineFormat(l.replace(/^\d+\. /, ''))}</li>`).join('');
      return `<ol class="md-ol">${items}</ol>`;
    });

    // ── Paragraphs ───────────────────────────────────────────────
    const blockTags = ['<h1','<h2','<h3','<h4','<h5','<h6','<ul','<ol','<blockquote','<table','<hr','<div','<pre','<figure'];
    md = md.split(/\n\n+/).map(block => {
      const t = block.trim();
      if (!t) return '';
      if (blockTags.some(b => t.startsWith(b)) || t.startsWith('\x00CODE') || t.startsWith('\x00IMG')) return t;
      return `<p class="md-p">${inlineFormat(t.replace(/\n/g, '<br>'))}</p>`;
    }).join('\n');

    // ── Restore ──────────────────────────────────────────────────
    md = md.replace(/\x00CODE(\d+)\x00/g,   (_, i) => codeBlocks[+i]);
    md = md.replace(/\x00INLINE(\d+)\x00/g, (_, i) => inlineCodes[+i]);
    md = md.replace(/\x00IMG(\d+)\x00/g,    (_, i) => imageBlocks[+i]);

    return md;
  }

  function inlineFormat(text) {
    return text
      .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
      .replace(/\*\*(.+?)\*\*/g,     '<strong>$1</strong>')
      .replace(/__(.+?)__/g,         '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g,         '<em>$1</em>')
      .replace(/_(.+?)_/g,           '<em>$1</em>')
      .replace(/~~(.+?)~~/g,         '<del>$1</del>')
      // Inline images (inside paragraph — just render, no lightbox wrapper)
      .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (_, alt, src) =>
        `<img src="${resolveImageSrc(src.trim())}" alt="${escapeHtml(alt)}" class="md-img-inline" loading="lazy" />`
      )
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g,
        '<a href="$2" class="md-link" target="_blank" rel="noopener">$1</a>'
      );
  }

  let rendered = $derived(parseMarkdown(content));

  // Handle clicks on rendered images via event delegation
  function handleBodyClick(e) {
    const wrapper = e.target.closest('[data-md-img]');
    if (!wrapper) return;
    const img = wrapper.querySelector('img');
    if (!img) return;
    lbSrc  = img.src;
    lbAlt  = img.alt;
    lbOpen = true;
  }

  function handleBodyKeydown(e) {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    const wrapper = e.target.closest('[data-md-img]');
    if (!wrapper) return;
    const img = wrapper.querySelector('img');
    if (!img) return;
    lbSrc  = img.src;
    lbAlt  = img.alt;
    lbOpen = true;
  }
</script>

<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
<div
  class="md-body {className}"
  onclick={handleBodyClick}
  onkeydown={handleBodyKeydown}
  role="presentation"
>
  {@html rendered}
</div>

<!-- ImageLightbox — shows original URL same as src (markdown images don't have separate originals) -->
<ImageLightbox bind:open={lbOpen} src={lbSrc} originalSrc={lbSrc} alt={lbAlt} />

<style>
  .md-body { color: var(--md-text, rgba(255,255,255,0.75)); font-size:16px; line-height:1.75; word-break:break-word; }

  /* Headings */
  .md-body :global(.md-h1),.md-body :global(.md-h2),.md-body :global(.md-h3),
  .md-body :global(.md-h4),.md-body :global(.md-h5),.md-body :global(.md-h6)
    { color:#fff; font-weight:700; line-height:1.3; margin-top:1.5em; margin-bottom:0.5em; }
  .md-body :global(.md-h1) { font-size:2em;     border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:0.3em; }
  .md-body :global(.md-h2) { font-size:1.5em;   border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:0.3em; }
  .md-body :global(.md-h3) { font-size:1.25em; }
  .md-body :global(.md-h4) { font-size:1em; }
  .md-body :global(.md-h5) { font-size:0.875em; }
  .md-body :global(.md-h6) { font-size:0.85em; color:rgba(255,255,255,0.5); }

  .md-body :global(.md-p)  { margin:0.85em 0; }

  .md-body :global(.md-link)        { color:#4ade80; text-decoration:none; }
  .md-body :global(.md-link:hover)  { text-decoration:underline; }

  .md-body :global(.md-hr) { border:none; border-top:1px solid rgba(255,255,255,0.1); margin:1.5em 0; }

  .md-body :global(.md-blockquote) {
    margin:1em 0; padding:0.5em 1em;
    border-left:3px solid #4ade80;
    background:rgba(74,222,128,0.05);
    color:rgba(255,255,255,0.6);
    font-style:italic;
    border-radius:0 4px 4px 0;
  }

  .md-body :global(.md-ul),.md-body :global(.md-ol) { margin:0.75em 0; padding-left:1.75em; }
  .md-body :global(.md-ul) { list-style:disc; }
  .md-body :global(.md-ol) { list-style:decimal; }
  .md-body :global(.md-ul li),.md-body :global(.md-ol li) { margin:0.25em 0; color:rgba(255,255,255,0.75); }

  .md-body :global(.md-inline-code) {
    font-family:monospace; font-size:0.875em;
    padding:0.15em 0.4em;
    background:rgba(255,255,255,0.08);
    border:1px solid rgba(255,255,255,0.1);
    border-radius:4px; color:#f0883e;
  }

  .md-body :global(.md-code-block) {
    position:relative; margin:1.25em 0; border-radius:8px;
    overflow:hidden; background:#0d1117;
    border:1px solid rgba(255,255,255,0.08);
  }
  .md-body :global(.md-code-lang) {
    display:block; padding:0.4em 1em; font-size:0.75em;
    color:rgba(255,255,255,0.4); background:rgba(255,255,255,0.04);
    border-bottom:1px solid rgba(255,255,255,0.06); font-family:monospace;
  }
  .md-body :global(.md-code-block pre)  { margin:0; padding:1em 1.25em; overflow-x:auto; }
  .md-body :global(.md-code-block code) { font-family:monospace; font-size:0.875em; line-height:1.6; color:#e6edf3; white-space:pre; }

  .md-body :global(.md-table) { width:100%; border-collapse:collapse; margin:1.25em 0; font-size:0.9em; overflow-x:auto; display:block; }
  .md-body :global(.md-table th) { padding:0.5em 0.9em; background:rgba(255,255,255,0.05); color:rgba(255,255,255,0.9); font-weight:600; border:1px solid rgba(255,255,255,0.1); white-space:nowrap; }
  .md-body :global(.md-table td) { padding:0.5em 0.9em; border:1px solid rgba(255,255,255,0.07); color:rgba(255,255,255,0.65); }
  .md-body :global(.md-table tr:nth-child(even) td) { background:rgba(255,255,255,0.02); }

  /* ── Sanity-style image figure ──────────────────────────────── */
  .md-body :global(.md-figure) {
    margin:1.75em 0; border-radius:10px; overflow:hidden;
    background:#111; border:1px solid rgba(255,255,255,0.07);
  }
  .md-body :global(.md-img-wrapper) {
    position:relative; cursor:zoom-in; overflow:hidden;
    display:block; background:#0a0a0a; max-height:600px;
  }
  .md-body :global(.md-img) {
    display:block; width:100%; max-width:100%; height:auto;
    max-height:600px; object-fit:contain;
    transition:transform 0.3s ease;
  }
  .md-body :global(.md-img-wrapper:hover .md-img) { transform:scale(1.015); }
  .md-body :global(.md-img-overlay) {
    position:absolute; bottom:10px; right:10px;
    width:34px; height:34px;
    display:flex; align-items:center; justify-content:center;
    background:rgba(0,0,0,0.55); backdrop-filter:blur(6px);
    border-radius:8px; color:rgba(255,255,255,0.85);
    opacity:0; transform:scale(0.85);
    transition:opacity 0.2s, transform 0.2s;
    pointer-events:none;
  }
  .md-body :global(.md-img-wrapper:hover .md-img-overlay) { opacity:1; transform:scale(1); }
  .md-body :global(.md-figcaption) {
    padding:8px 14px; font-size:0.8em; color:rgba(255,255,255,0.4);
    text-align:center; background:rgba(255,255,255,0.03);
    border-top:1px solid rgba(255,255,255,0.05);
    font-style:italic;
  }
  .md-body :global(.md-img-inline) { max-width:100%; border-radius:6px; vertical-align:middle; margin:0 2px; }

  .md-body :global(strong) { color:#fff; font-weight:700; }
  .md-body :global(em)     { font-style:italic; }
  .md-body :global(del)    { color:rgba(255,255,255,0.4); text-decoration:line-through; }
</style>
