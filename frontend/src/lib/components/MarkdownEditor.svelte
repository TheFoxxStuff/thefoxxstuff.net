<script>
  import { api } from '$lib/api';
  import MarkdownRenderer from './MarkdownRenderer.svelte';

  let { value = $bindable(''), placeholder = 'Write your content in Markdown...', rows = 16 } = $props();

  let fileInput;
  let uploading = $state(false);
  let mode = $state('write'); // 'write' | 'preview' | 'split'
  let textarea;
  let dragOver = $state(false);

  async function handleImageUpload(file) {
    if (!file) return;
    uploading = true;
    try {
      const result = await api.upload.markdown(file);
      insertText(result.markdown + '\n');
    } catch (err) {
      alert('Upload failed: ' + err.message);
    } finally {
      uploading = false;
      if (fileInput) fileInput.value = '';
    }
  }

  function handleFileInput() {
    handleImageUpload(fileInput?.files?.[0]);
  }

  function handleDrop(e) {
    e.preventDefault();
    dragOver = false;
    const file = e.dataTransfer?.files?.[0];
    if (file && file.type.startsWith('image/')) handleImageUpload(file);
  }

  function insertText(text, wrap = false) {
    if (!textarea) return;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selected = value.substring(start, end);
    if (wrap && selected) {
      value = value.substring(0, start) + text + selected + text + value.substring(end);
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(start + text.length, start + text.length + selected.length);
      }, 0);
    } else if (wrap) {
      const placeholder_text = 'text';
      value = value.substring(0, start) + text + placeholder_text + text + value.substring(end);
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(start + text.length, start + text.length + placeholder_text.length);
      }, 0);
    } else {
      value = value.substring(0, start) + text + value.substring(end);
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(start + text.length, start + text.length);
      }, 0);
    }
  }

  function insertBlock(prefix, defaultText = 'text') {
    if (!textarea) return;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selected = value.substring(start, end);
    const ins = prefix + (selected || defaultText);
    value = value.substring(0, start) + ins + value.substring(end);
    setTimeout(() => {
      textarea.focus();
      const s = start + prefix.length;
      textarea.setSelectionRange(s, s + (selected || defaultText).length);
    }, 0);
  }

  function insertLink() {
    if (!textarea) return;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selected = value.substring(start, end);
    const ins = selected ? `[${selected}](url)` : '[link text](url)';
    value = value.substring(0, start) + ins + value.substring(end);
    setTimeout(() => {
      textarea.focus();
      const urlStart = start + (selected || 'link text').length + 3;
      textarea.setSelectionRange(urlStart, urlStart + 3);
    }, 0);
  }

  function insertHeading(level) {
    const prefix = '#'.repeat(level) + ' ';
    insertBlock(prefix, 'Heading');
  }

  function handleKeyDown(e) {
    if (e.key === 'Tab') {
      e.preventDefault();
      insertText('  ');
    }
    // Ctrl+B bold
    if ((e.ctrlKey || e.metaKey) && e.key === 'b') { e.preventDefault(); insertText('**', true); }
    // Ctrl+I italic
    if ((e.ctrlKey || e.metaKey) && e.key === 'i') { e.preventDefault(); insertText('*', true); }
    // Ctrl+K link
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); insertLink(); }
  }
</script>

<div class="md-editor">
  <!-- Toolbar -->
  <div class="toolbar">
    <!-- Headings -->
    <div class="toolbar-group">
      {#each [1,2,3] as h}
        <button type="button" onclick={() => insertHeading(h)} class="tb-btn" title="H{h}">
          <span class="tb-text">H{h}</span>
        </button>
      {/each}
    </div>
    <div class="toolbar-sep"></div>
    <!-- Formatting -->
    <div class="toolbar-group">
      <button type="button" onclick={() => insertText('**', true)} class="tb-btn" title="Bold (Ctrl+B)">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 4h8a4 4 0 014 4 4 4 0 01-4 4H6z"/><path d="M6 12h9a4 4 0 014 4 4 4 0 01-4 4H6z"/></svg>
      </button>
      <button type="button" onclick={() => insertText('*', true)} class="tb-btn" title="Italic (Ctrl+I)">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="19" y1="4" x2="10" y2="4"/><line x1="14" y1="20" x2="5" y2="20"/><line x1="15" y1="4" x2="9" y2="20"/></svg>
      </button>
      <button type="button" onclick={() => insertText('~~', true)} class="tb-btn" title="Strikethrough">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4H9a4 4 0 000 8h6a4 4 0 010 8H6"/><line x1="4" y1="12" x2="20" y2="12"/></svg>
      </button>
    </div>
    <div class="toolbar-sep"></div>
    <!-- Blocks -->
    <div class="toolbar-group">
      <button type="button" onclick={() => insertBlock('> ', 'quote')} class="tb-btn" title="Quote">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z"/></svg>
      </button>
      <button type="button" onclick={() => insertBlock('- ', 'item')} class="tb-btn" title="Unordered list">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="9" y1="6" x2="20" y2="6"/><line x1="9" y1="12" x2="20" y2="12"/><line x1="9" y1="18" x2="20" y2="18"/><circle cx="4" cy="6" r="1" fill="currentColor"/><circle cx="4" cy="12" r="1" fill="currentColor"/><circle cx="4" cy="18" r="1" fill="currentColor"/></svg>
      </button>
      <button type="button" onclick={() => insertBlock('1. ', 'item')} class="tb-btn" title="Ordered list">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="10" y1="6" x2="21" y2="6"/><line x1="10" y1="12" x2="21" y2="12"/><line x1="10" y1="18" x2="21" y2="18"/><path d="M4 6h1v4" stroke-width="1.5"/><path d="M4 10h2"/><path d="M6 18H4c0-1 2-2 2-3s-1-1.5-2-1"/></svg>
      </button>
      <button type="button" onclick={() => insertText('\n---\n')} class="tb-btn" title="Horizontal rule">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/></svg>
      </button>
    </div>
    <div class="toolbar-sep"></div>
    <!-- Code -->
    <div class="toolbar-group">
      <button type="button" onclick={() => insertText('`', true)} class="tb-btn" title="Inline code">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
      </button>
      <button type="button" onclick={() => insertText('```\n', false) || insertText('\n```')} class="tb-btn tb-code-block" title="Code block"
        onclick={() => {
          if (!textarea) return;
          const start = textarea.selectionStart;
          const end = textarea.selectionEnd;
          const selected = value.substring(start, end);
          const ins = '```\n' + (selected || 'code') + '\n```';
          value = value.substring(0, start) + ins + value.substring(end);
          setTimeout(() => { textarea.focus(); textarea.setSelectionRange(start + 4, start + 4 + (selected || 'code').length); }, 0);
        }}
      >
        <span class="tb-text text-[10px] font-mono">{'{}'}</span>
      </button>
    </div>
    <div class="toolbar-sep"></div>
    <!-- Media -->
    <div class="toolbar-group">
      <button type="button" onclick={insertLink} class="tb-btn" title="Link (Ctrl+K)">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>
      </button>
      <button type="button" onclick={() => fileInput.click()} disabled={uploading} class="tb-btn" title="Upload image">
        {#if uploading}
          <svg class="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-dashoffset="8"/></svg>
        {:else}
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
        {/if}
      </button>
    </div>
    <input type="file" bind:this={fileInput} onchange={handleFileInput} accept="image/*" class="hidden" />

    <div class="flex-1"></div>

    <!-- Mode switcher -->
    <div class="mode-switch">
      <button type="button" onclick={() => mode = 'write'} class:active={mode === 'write'}>Write</button>
      <button type="button" onclick={() => mode = 'split'} class:active={mode === 'split'}>Split</button>
      <button type="button" onclick={() => mode = 'preview'} class:active={mode === 'preview'}>Preview</button>
    </div>
  </div>

  <!-- Editor area -->
  <div class="editor-area" class:split={mode === 'split'}>
    {#if mode !== 'preview'}
      <div
        class="write-pane"
        class:drag-over={dragOver}
        ondragover={(e) => { e.preventDefault(); dragOver = true; }}
        ondragleave={() => dragOver = false}
        ondrop={handleDrop}
        role="presentation"
      >
        <textarea
          bind:this={textarea}
          bind:value
          {placeholder}
          {rows}
          class="md-textarea"
          onkeydown={handleKeyDown}
          spellcheck="false"
        ></textarea>
        {#if dragOver}
          <div class="drop-overlay">Drop image to upload</div>
        {/if}
      </div>
    {/if}

    {#if mode !== 'write'}
      <div class="preview-pane">
        {#if value}
          <MarkdownRenderer content={value} />
        {:else}
          <p class="empty-preview">Nothing to preview</p>
        {/if}
      </div>
    {/if}
  </div>

  <div class="editor-footer">
    <span>Markdown supported · Drag & drop images · Ctrl+B Bold · Ctrl+I Italic · Ctrl+K Link</span>
  </div>
</div>

<style>
  .md-editor {
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    overflow: hidden;
    background: #121212;
  }

  /* Toolbar */
  .toolbar {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 8px 12px;
    background: #1a1a1a;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    flex-wrap: wrap;
  }
  .toolbar-group { display: flex; align-items: center; gap: 2px; }
  .toolbar-sep { width: 1px; height: 20px; background: rgba(255,255,255,0.1); margin: 0 4px; }

  .tb-btn {
    width: 30px; height: 30px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 6px;
    color: rgba(255,255,255,0.55);
    transition: all 0.15s;
    cursor: pointer;
    flex-shrink: 0;
  }
  .tb-btn:hover { background: rgba(255,255,255,0.1); color: #fff; }
  .tb-btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .tb-text { font-size: 12px; font-weight: 600; font-family: inherit; }

  /* Mode switch */
  .mode-switch {
    display: flex;
    background: rgba(255,255,255,0.05);
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.08);
  }
  .mode-switch button {
    padding: 4px 12px;
    font-size: 12px;
    color: rgba(255,255,255,0.5);
    transition: all 0.15s;
  }
  .mode-switch button:hover { color: #fff; }
  .mode-switch button.active { background: rgba(255,255,255,0.1); color: #fff; }

  /* Editor area */
  .editor-area {
    display: flex;
    min-height: 300px;
  }
  .editor-area.split .write-pane,
  .editor-area.split .preview-pane {
    flex: 1;
    border-right: 1px solid rgba(255,255,255,0.08);
  }

  .write-pane {
    position: relative;
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  .write-pane.drag-over { background: rgba(74,222,128,0.05); }

  .md-textarea {
    flex: 1;
    width: 100%;
    background: transparent;
    border: none;
    outline: none;
    padding: 16px;
    color: rgba(255,255,255,0.85);
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    font-size: 14px;
    line-height: 1.7;
    resize: vertical;
    min-height: 280px;
  }
  .md-textarea::placeholder { color: rgba(255,255,255,0.25); }

  .drop-overlay {
    position: absolute; inset: 0;
    display: flex; align-items: center; justify-content: center;
    background: rgba(74,222,128,0.1);
    border: 2px dashed #4ade80;
    color: #4ade80;
    font-size: 15px;
    font-weight: 600;
    pointer-events: none;
    border-radius: 4px;
    margin: 4px;
  }

  .preview-pane {
    flex: 1;
    padding: 16px 20px;
    overflow-y: auto;
    background: #0f0f0f;
  }
  .empty-preview { color: rgba(255,255,255,0.25); font-style: italic; }

  /* Footer */
  .editor-footer {
    padding: 6px 14px;
    background: #1a1a1a;
    border-top: 1px solid rgba(255,255,255,0.06);
    font-size: 11px;
    color: rgba(255,255,255,0.25);
  }
</style>
