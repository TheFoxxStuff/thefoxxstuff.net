<script>
  import { API_BASE } from '$lib/api';

  let { content = '', class: className = '' } = $props();

  function escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function parseMarkdown(md) {
    if (!md) return '';

    // Protect code blocks first
    const codeBlocks = [];
    const inlineCodes = [];

    // Fenced code blocks
    md = md.replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) => {
      const idx = codeBlocks.length;
      const langLabel = lang ? `<span class="md-code-lang">${escapeHtml(lang)}</span>` : '';
      codeBlocks.push(
        `<div class="md-code-block">${langLabel}<pre><code class="language-${lang || 'text'}">${escapeHtml(code.trim())}</code></pre></div>`
      );
      return `\x00CODE${idx}\x00`;
    });

    // Inline code
    md = md.replace(/`([^`\n]+)`/g, (_, code) => {
      const idx = inlineCodes.length;
      inlineCodes.push(`<code class="md-inline-code">${escapeHtml(code)}</code>`);
      return `\x00INLINE${idx}\x00`;
    });

    // Tables
    md = md.replace(/^(\|.+\|\s*\n\|[-| :]+\|\s*\n(?:\|.+\|\s*\n?)*)/gm, (tableBlock) => {
      const lines = tableBlock.trim().split('\n');
      if (lines.length < 2) return tableBlock;
      const headers = lines[0].split('|').map(h => h.trim()).filter(Boolean);
      const alignRow = lines[1].split('|').map(c => c.trim()).filter(Boolean);
      const aligns = alignRow.map(c => {
        if (c.startsWith(':') && c.endsWith(':')) return 'center';
        if (c.endsWith(':')) return 'right';
        return 'left';
      });
      const ths = headers.map((h, i) => `<th style="text-align:${aligns[i] || 'left'}">${h}</th>`).join('');
      const bodyRows = lines.slice(2).map(row => {
        const cells = row.split('|').map(c => c.trim()).filter(Boolean);
        const tds = cells.map((c, i) => `<td style="text-align:${aligns[i] || 'left'}">${inlineFormat(c)}</td>`).join('');
        return `<tr>${tds}</tr>`;
      }).join('');
      return `<table class="md-table"><thead><tr>${ths}</tr></thead><tbody>${bodyRows}</tbody></table>`;
    });

    // Headings
    md = md.replace(/^###### (.+)$/gm, '<h6 class="md-h6">$1</h6>');
    md = md.replace(/^##### (.+)$/gm, '<h5 class="md-h5">$1</h5>');
    md = md.replace(/^#### (.+)$/gm, '<h4 class="md-h4">$1</h4>');
    md = md.replace(/^### (.+)$/gm, '<h3 class="md-h3">$1</h3>');
    md = md.replace(/^## (.+)$/gm, '<h2 class="md-h2">$1</h2>');
    md = md.replace(/^# (.+)$/gm, '<h1 class="md-h1">$1</h1>');

    // Horizontal rule
    md = md.replace(/^[-*_]{3,}\s*$/gm, '<hr class="md-hr" />');

    // Blockquote
    md = md.replace(/^> (.+)$/gm, '<blockquote class="md-blockquote">$1</blockquote>');
    // Merge consecutive blockquotes
    md = md.replace(/<\/blockquote>\n<blockquote class="md-blockquote">/g, '\n');

    // Unordered lists
    md = md.replace(/((?:^[-*+] .+$\n?)+)/gm, (block) => {
      const items = block.trim().split('\n').map(line => {
        const text = line.replace(/^[-*+] /, '');
        return `<li>${inlineFormat(text)}</li>`;
      }).join('');
      return `<ul class="md-ul">${items}</ul>`;
    });

    // Ordered lists
    md = md.replace(/((?:^\d+\. .+$\n?)+)/gm, (block) => {
      const items = block.trim().split('\n').map(line => {
        const text = line.replace(/^\d+\. /, '');
        return `<li>${inlineFormat(text)}</li>`;
      }).join('');
      return `<ol class="md-ol">${items}</ol>`;
    });

    // Paragraphs (split by double newline, skip already-block elements)
    const blockTags = ['<h1', '<h2', '<h3', '<h4', '<h5', '<h6', '<ul', '<ol', '<blockquote', '<table', '<hr', '<div', '<pre'];
    md = md.split(/\n\n+/).map(block => {
      const trimmed = block.trim();
      if (!trimmed) return '';
      if (blockTags.some(t => trimmed.startsWith(t)) || trimmed.startsWith('\x00CODE')) return trimmed;
      return `<p class="md-p">${inlineFormat(trimmed.replace(/\n/g, '<br>'))}</p>`;
    }).join('\n');

    // Restore code blocks
    md = md.replace(/\x00CODE(\d+)\x00/g, (_, i) => codeBlocks[+i]);
    md = md.replace(/\x00INLINE(\d+)\x00/g, (_, i) => inlineCodes[+i]);

    return md;
  }

  function inlineFormat(text) {
    return text
      // Bold italic
      .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
      // Bold
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/__(.+?)__/g, '<strong>$1</strong>')
      // Italic
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/_(.+?)_/g, '<em>$1</em>')
      // Strikethrough
      .replace(/~~(.+?)~~/g, '<del>$1</del>')
      // Images (handle relative API paths)
      .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (_, alt, src) => {
        const fullSrc = src.startsWith('http') ? src
          : src.startsWith('/api/') ? `${API_BASE.replace('/api', '')}${src}`
          : src;
        return `<img src="${fullSrc}" alt="${escapeHtml(alt)}" class="md-img" loading="lazy" />`;
      })
      // Links
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="md-link" target="_blank" rel="noopener">$1</a>');
  }

  let rendered = $derived(parseMarkdown(content));
</script>

<div class="md-body {className}">
  {@html rendered}
</div>

<style>
  .md-body {
    color: var(--md-text, rgba(255,255,255,0.75));
    font-size: 16px;
    line-height: 1.75;
    word-break: break-word;
  }

  /* Headings */
  .md-body :global(.md-h1),
  .md-body :global(.md-h2),
  .md-body :global(.md-h3),
  .md-body :global(.md-h4),
  .md-body :global(.md-h5),
  .md-body :global(.md-h6) {
    color: #fff;
    font-weight: 700;
    line-height: 1.3;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    padding-bottom: 0.2em;
  }
  .md-body :global(.md-h1) { font-size: 2em; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 0.3em; }
  .md-body :global(.md-h2) { font-size: 1.5em; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 0.3em; }
  .md-body :global(.md-h3) { font-size: 1.25em; }
  .md-body :global(.md-h4) { font-size: 1em; }
  .md-body :global(.md-h5) { font-size: 0.875em; }
  .md-body :global(.md-h6) { font-size: 0.85em; color: rgba(255,255,255,0.5); }

  /* Paragraph */
  .md-body :global(.md-p) {
    margin: 0.85em 0;
  }

  /* Links */
  .md-body :global(.md-link) {
    color: #4ade80;
    text-decoration: none;
  }
  .md-body :global(.md-link:hover) {
    text-decoration: underline;
  }

  /* HR */
  .md-body :global(.md-hr) {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.1);
    margin: 1.5em 0;
  }

  /* Blockquote */
  .md-body :global(.md-blockquote) {
    margin: 1em 0;
    padding: 0.5em 1em;
    border-left: 3px solid #4ade80;
    background: rgba(74,222,128,0.05);
    color: rgba(255,255,255,0.6);
    font-style: italic;
    border-radius: 0 4px 4px 0;
  }

  /* Lists */
  .md-body :global(.md-ul),
  .md-body :global(.md-ol) {
    margin: 0.75em 0;
    padding-left: 1.75em;
  }
  .md-body :global(.md-ul) { list-style: disc; }
  .md-body :global(.md-ol) { list-style: decimal; }
  .md-body :global(.md-ul li),
  .md-body :global(.md-ol li) {
    margin: 0.25em 0;
    color: rgba(255,255,255,0.75);
  }

  /* Inline code */
  .md-body :global(.md-inline-code) {
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    font-size: 0.875em;
    padding: 0.15em 0.4em;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 4px;
    color: #f0883e;
  }

  /* Code block */
  .md-body :global(.md-code-block) {
    position: relative;
    margin: 1.25em 0;
    border-radius: 8px;
    overflow: hidden;
    background: #0d1117;
    border: 1px solid rgba(255,255,255,0.08);
  }
  .md-body :global(.md-code-block .md-code-lang) {
    display: block;
    padding: 0.4em 1em;
    font-size: 0.75em;
    color: rgba(255,255,255,0.4);
    background: rgba(255,255,255,0.04);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    font-family: monospace;
    text-transform: lowercase;
  }
  .md-body :global(.md-code-block pre) {
    margin: 0;
    padding: 1em 1.25em;
    overflow-x: auto;
  }
  .md-body :global(.md-code-block code) {
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    font-size: 0.875em;
    line-height: 1.6;
    color: #e6edf3;
    white-space: pre;
  }

  /* Table */
  .md-body :global(.md-table) {
    width: 100%;
    border-collapse: collapse;
    margin: 1.25em 0;
    font-size: 0.9em;
    overflow-x: auto;
    display: block;
  }
  .md-body :global(.md-table th) {
    padding: 0.5em 0.9em;
    background: rgba(255,255,255,0.05);
    color: rgba(255,255,255,0.9);
    font-weight: 600;
    border: 1px solid rgba(255,255,255,0.1);
    white-space: nowrap;
  }
  .md-body :global(.md-table td) {
    padding: 0.5em 0.9em;
    border: 1px solid rgba(255,255,255,0.07);
    color: rgba(255,255,255,0.65);
  }
  .md-body :global(.md-table tr:nth-child(even) td) {
    background: rgba(255,255,255,0.02);
  }

  /* Images */
  .md-body :global(.md-img) {
    max-width: 100%;
    border-radius: 8px;
    display: block;
    margin: 1.25em 0;
  }

  /* Strong / em / del */
  .md-body :global(strong) { color: #fff; font-weight: 700; }
  .md-body :global(em) { font-style: italic; }
  .md-body :global(del) { color: rgba(255,255,255,0.4); text-decoration: line-through; }
</style>
