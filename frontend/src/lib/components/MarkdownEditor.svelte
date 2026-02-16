<script>
  import { api } from '$lib/api';

  let { value = $bindable(''), placeholder = 'Write your content in Markdown...', rows = 10 } = $props();

  let fileInput;
  let uploading = $state(false);
  let mode = $state('write'); // 'write' | 'preview' | 'split'

  async function handleImageUpload() {
    const file = fileInput.files?.[0];
    if (!file) return;
    uploading = true;
    try {
      const result = await api.upload.markdown(file);
      const textarea = document.querySelector('.md-textarea');
      if (textarea) {
        const start = textarea.selectionStart, end = textarea.selectionEnd;
        value = value.substring(0, start) + result.markdown + value.substring(end);
      } else { value += '\n' + result.markdown; }
    } catch (err) { alert('Upload failed: ' + err.message); }
    finally { uploading = false; fileInput.value = ''; }
  }

  function insert(prefix, suffix = '') {
    const textarea = document.querySelector('.md-textarea');
    if (!textarea) return;
    const start = textarea.selectionStart, end = textarea.selectionEnd;
    const selected = value.substring(start, end);
    value = value.substring(0, start) + prefix + selected + suffix + value.substring(end);
    setTimeout(() => { textarea.focus(); textarea.setSelectionRange(start + prefix.length, start + prefix.length + selected.length); }, 0);
  }

  function parseMarkdown(md) {
    if (!md) return '<p class="text-dark-500 italic">Nothing to preview</p>';
    let html = md
      // Code blocks (fenced)
      .replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) =>
        `<pre class="bg-dark-950 rounded-lg p-4 my-3 overflow-x-auto"><code class="text-sm text-dark-300">${code.replace(/</g,'&lt;').replace(/>/g,'&gt;').trim()}</code></pre>`)
      // Tables
      .replace(/^\|(.+)\|\s*\n\|[-| :]+\|\s*\n((?:\|.+\|\s*\n?)*)/gm, (_, header, body) => {
        const ths = header.split('|').map(h => h.trim()).filter(Boolean).map(h => `<th class="px-3 py-2 text-left text-sm font-medium text-dark-300 border-b border-dark-700">${h}</th>`).join('');
        const rows = body.trim().split('\n').map(row => {
          const tds = row.split('|').map(c => c.trim()).filter(Boolean).map(c => `<td class="px-3 py-2 text-sm text-dark-400 border-b border-dark-800">${c}</td>`).join('');
          return `<tr>${tds}</tr>`;
        }).join('');
        return `<table class="w-full my-4 border-collapse"><thead><tr>${ths}</tr></thead><tbody>${rows}</tbody></table>`;
      })
      // Headings
      .replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>')
      .replace(/^## (.+)$/gm, '<h2 class="text-xl font-semibold mt-6 mb-3">$1</h2>')
      .replace(/^# (.+)$/gm, '<h1 class="text-2xl font-bold mt-8 mb-4">$1</h1>')
      // Inline
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/~~(.+?)~~/g, '<del class="text-dark-500">$1</del>')
      .replace(/`(.+?)`/g, '<code class="px-1 py-0.5 bg-dark-800 rounded text-sm">$1</code>')
      .replace(/!\[(.+?)\]\((.+?)\)/g, '<img src="$2" alt="$1" class="rounded-lg max-w-full my-4" />')
      .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" class="text-accent-green hover:underline">$1</a>')
      // Blockquote
      .replace(/^> (.+)$/gm, '<blockquote class="border-l-2 border-accent-green/50 pl-4 my-3 text-dark-400 italic">$1</blockquote>')
      // Lists
      .replace(/^- (.+)$/gm, '<li class="ml-4 list-disc">$1</li>')
      .replace(/^(\d+)\. (.+)$/gm, '<li class="ml-4 list-decimal">$2</li>')
      // Horizontal rule
      .replace(/^---$/gm, '<hr class="border-dark-700 my-6" />')
      // Paragraphs
      .replace(/\n\n/g, '</p><p class="my-3">')
      .replace(/\n/g, '<br>');
    return html;
  }
</script>

<div class="markdown-editor">
  <div class="flex items-center gap-1 mb-2 pb-2 border-b border-dark-700 flex-wrap">
    <button type="button" onclick={() => insert('**','**')} class="toolbar-btn" title="Bold"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 4h8a4 4 0 014 4 4 4 0 01-4 4H6z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 12h9a4 4 0 014 4 4 4 0 01-4 4H6z" /></svg></button>
    <button type="button" onclick={() => insert('*','*')} class="toolbar-btn" title="Italic"><span class="text-sm italic font-serif">I</span></button>
    <button type="button" onclick={() => insert('~~','~~')} class="toolbar-btn" title="Strikethrough"><span class="text-sm line-through">S</span></button>
    <button type="button" onclick={() => insert('# ')} class="toolbar-btn" title="Heading"><span class="font-bold text-sm">H</span></button>
    <button type="button" onclick={() => insert('[','](url)')} class="toolbar-btn" title="Link"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101" /></svg></button>
    <button type="button" onclick={() => insert('- ')} class="toolbar-btn" title="List"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg></button>
    <button type="button" onclick={() => insert('`','`')} class="toolbar-btn" title="Inline Code"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg></button>
    <button type="button" onclick={() => insert('```\n','\n```')} class="toolbar-btn" title="Code Block"><span class="text-[10px] font-mono">{'{}'}</span></button>
    <button type="button" onclick={() => insert('> ')} class="toolbar-btn" title="Quote"><span class="text-sm font-serif">"</span></button>
    <div class="w-px h-5 bg-dark-700 mx-1"></div>
    <button type="button" onclick={() => fileInput.click()} disabled={uploading} class="toolbar-btn" title="Upload Image">
      {#if uploading}<svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
      {:else}<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>{/if}
    </button>
    <input type="file" bind:this={fileInput} onchange={handleImageUpload} accept="image/*" class="hidden" />
    <div class="flex-1"></div>
    <div class="flex bg-dark-800 rounded-lg overflow-hidden">
      <button type="button" onclick={() => mode = 'write'} class="px-3 py-1 text-xs transition {mode === 'write' ? 'bg-dark-600 text-white' : 'text-dark-400 hover:text-white'}">Write</button>
      <button type="button" onclick={() => mode = 'split'} class="px-3 py-1 text-xs transition {mode === 'split' ? 'bg-dark-600 text-white' : 'text-dark-400 hover:text-white'}">Split</button>
      <button type="button" onclick={() => mode = 'preview'} class="px-3 py-1 text-xs transition {mode === 'preview' ? 'bg-dark-600 text-white' : 'text-dark-400 hover:text-white'}">Preview</button>
    </div>
  </div>

  {#if mode === 'split'}
    <div class="grid grid-cols-2 gap-3">
      <textarea bind:value {placeholder} {rows} class="md-textarea textarea font-mono text-sm"></textarea>
      <div class="prose prose-invert min-h-[200px] p-4 bg-dark-800 rounded-lg overflow-auto text-sm">{@html parseMarkdown(value)}</div>
    </div>
  {:else if mode === 'preview'}
    <div class="prose prose-invert min-h-[200px] p-4 bg-dark-800 rounded-lg overflow-auto">{@html parseMarkdown(value)}</div>
  {:else}
    <textarea bind:value {placeholder} {rows} class="md-textarea textarea font-mono text-sm"></textarea>
  {/if}
</div>

<style>
  .toolbar-btn { padding:0.5rem; border-radius:0.25rem; color:#818181; transition:all 0.2s; }
  .toolbar-btn:hover { background:#434343; color:white; }
  .prose { color:#a3a3a3; line-height:1.625; }
  .prose :global(img) { border-radius:0.5rem; max-width:100%; }
  .prose :global(a) { color:#4ade80; }
  .prose :global(a:hover) { text-decoration:underline; }
  .prose :global(code) { padding:0.125rem 0.25rem; background:#121212; border-radius:0.25rem; font-size:0.875rem; }
</style>
