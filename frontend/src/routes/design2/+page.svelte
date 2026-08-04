<script>
  import { SEO } from '$lib/components';
  import {
    Music, FileText, Palette, Users, Image, Eye, ArrowUpRight,
    LayoutDashboard, Zap, Link as LinkIcon, Home, ChevronRight, ChevronLeft,
    Sun, Moon, Search, Shield, Send, Download, Copy, X, Check, Menu,
    ExternalLink, Camera, Heart, Star, Play, Trash2, Settings, User,
    Mail, MapPin, Calendar, Info, Maximize, ZoomIn, ZoomOut, Bell,
    AlertTriangle, Loader2, Plus, Edit3, LogOut, Volume2, Repeat,
    SkipBack, SkipForward, Pause, EyeOff, Lock, UserPlus, FileUp,
    Type, Bold, Italic, List, ListOrdered, Quote, Code, Hash, ImagePlus,
    Paperclip, GripVertical, MoreHorizontal, MessageSquare, TrendingUp,
    BarChart3, Globe, Sparkles, Layers
  } from 'lucide-svelte';
  import { theme } from '$lib/stores/theme.js';
  import { browser } from '$app/environment';

  const sections = [
    { id: 'foundations', label: 'Foundations', icon: Layers },
    { id: 'colors', label: 'Colors', icon: Palette },
    { id: 'typography', label: 'Typography', icon: Type },
    { id: 'spacing', label: 'Spacing', icon: RulersIcon },
    { id: 'buttons', label: 'Buttons', icon: Zap },
    { id: 'inputs', label: 'Inputs', icon: Edit3 },
    { id: 'cards', label: 'Cards', icon: Layers },
    { id: 'feedback', label: 'Feedback', icon: Bell },
    { id: 'navigation', label: 'Navigation', icon: CompassIcon },
    { id: 'media', label: 'Media', icon: Image },
    { id: 'overlays', label: 'Overlays', icon: Maximize },
    { id: 'tables', label: 'Data Lists', icon: List },
    { id: 'empty-states', label: 'Empty States', icon: EyeOff },
    { id: 'compositions', label: 'Patterns', icon: Sparkles },
    { id: 'icons', label: 'Icons', icon: Star },
    { id: 'principles', label: 'Principles', icon: Globe },
  ];

  // Small icon component workaround to avoid svelte:component issues in {#each}
  function RulersIcon(props) {
    return `<svg width="${props?.size||20}" height="${props?.size||20}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.3 15.3a2.4 2.4 0 0 1 0 3.4l-2.6 2.6a2.4 2.4 0 0 1-3.4 0L2.7 8.7a2.4 2.4 0 0 1 0-3.4l2.6-2.6a2.4 2.4 0 0 1 3.4 0Z"/><path d="m14.5 12.5 2-2"/><path d="m11.5 9.5 2-"/><path d="m8.5 6.5 2-2"/><path d="m17.5 15.5 2-2"/></svg>`;
  }
  function CompassIcon(props) {
    return `<svg width="${props?.size||20}" height="${props?.size||20}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>`;
  }

  const commonIcons = [
    { name: 'Home', icon: Home }, { name: 'Music', icon: Music },
    { name: 'FileText', icon: FileText }, { name: 'Palette', icon: Palette },
    { name: 'Users', icon: Users }, { name: 'Image', icon: Image },
    { name: 'Eye', icon: Eye }, { name: 'ArrowUpRight', icon: ArrowUpRight },
    { name: 'LayoutDashboard', icon: LayoutDashboard }, { name: 'Zap', icon: Zap },
    { name: 'Link', icon: LinkIcon }, { name: 'ChevronRight', icon: ChevronRight },
    { name: 'Search', icon: Search }, { name: 'Shield', icon: Shield },
    { name: 'Send', icon: Send }, { name: 'Heart', icon: Heart },
    { name: 'Star', icon: Star }, { name: 'Play', icon: Play },
    { name: 'Download', icon: Download }, { name: 'ExternalLink', icon: ExternalLink },
    { name: 'Calendar', icon: Calendar }, { name: 'Sun', icon: Sun },
    { name: 'Moon', icon: Moon }, { name: 'Settings', icon: Settings },
    { name: 'Trash2', icon: Trash2 }, { name: 'Check', icon: Check },
    { name: 'X', icon: X }, { name: 'Menu', icon: Menu },
    { name: 'User', icon: User }, { name: 'Camera', icon: Camera },
    { name: 'Mail', icon: Mail }, { name: 'MapPin', icon: MapPin },
    { name: 'Info', icon: Info }, { name: 'Bell', icon: Bell },
    { name: 'Plus', icon: Plus }, { name: 'Edit3', icon: Edit3 },
    { name: 'LogOut', icon: LogOut }, { name: 'Volume2', icon: Volume2 },
    { name: 'Repeat', icon: Repeat }, { name: 'SkipBack', icon: SkipBack },
    { name: 'SkipForward', icon: SkipForward }, { name: 'Lock', icon: Lock },
    { name: 'Upload', icon: FileUp }, { name: 'Copy', icon: Copy },
    { name: 'ZoomIn', icon: ZoomIn }, { name: 'MoreHorizontal', icon: MoreHorizontal },
    { name: 'MessageSquare', icon: MessageSquare },
    { name: 'BarChart3', icon: BarChart3 }, { name: 'Globe', icon: Globe },
    { name: 'Sparkles', icon: Sparkles }, { name: 'Layers', icon: Layers },
  ];

  const fontWeights = [100, 200, 300, 400, 500, 600, 700, 800, 900];

  // Markdown editor toolbar buttons
  const mdToolbarButtons = [
    { label: 'H1', icon: null }, { label: 'H2', icon: null }, { label: 'H3', icon: null },
    { label: 'B', bold: true }, { label: 'I', italic: true },
    { label: 'S', strike: true },
    { label: null, icon: Quote }, { label: null, icon: List }, { label: null, icon: ListOrdered },
    { label: null, icon: Code }, { label: null, icon: Hash },
    { label: null, icon: ImagePlus }, { label: null, icon: LinkIcon },
  ];

  function hue(name = '') {
    let h = 0;
    for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) % 360;
    return h;
  }

  // Interactive state
  let copiedCode = $state(null);
  function copyToClipboard(text, id) {
    if (browser && navigator.clipboard) {
      navigator.clipboard.writeText(text);
      copiedCode = id;
      setTimeout(() => { copiedCode = null }, 2000);
    }
  }

  // Live input demo
  let demoInput = $state('');
  let demoTextarea = $state('');
  let demoChecked = $state(false);
  let demoSelected = $state('split');

  if (browser) {
    $effect(() => {
      const handleHash = () => {
        const hash = window.location.hash.slice(1);
        if (hash) {
          const el = document.getElementById(hash);
          if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      };
      window.addEventListener('hashchange', handleHash);
      return () => window.removeEventListener('hashchange', handleHash);
    });
  }
</script>

<svelte:window />

<SEO
  title="Design System v2.0 | TheFoxxStuff"
  description="The complete visual design system, component library, and interaction patterns for TheFoxxStuff."
/>

<!-- ═══════════════════════════════════════════════════════ -->
<!-- PAGE WRAPPER                                          -->
<!-- ═══════════════════════════════════════════════════════ -->
<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-16 min-[829px]:max-w-[828px] min-[829px]:px-0">

  <!-- ════════════ HERO ════════════ -->
  <div class="mb-16 relative">
    <!-- Decorative accent glow -->
    <div class="absolute -top-20 -left-20 w-40 h-40 rounded-full blur-[80px] pointer-events-none" style="background: var(--green); opacity: 0.06;"></div>
    <div class="absolute -bottom-10 -right-10 w-32 h-32 rounded-full blur-[60px] pointer-events-none" style="background: var(--blue); opacity: 0.06;"></div>

    <div class="relative">
      <div class="flex items-center gap-2 mb-4">
        <span class="inline-block px-3 py-1 text-[11px] font-semibold tracking-wider uppercase rounded-full" style="background: rgba(115,238,7,0.08); color: var(--green); border: 1px solid rgba(115,238,7,0.15);">v2.0</span>
        <span class="text-xs" style="color: var(--w40);">Living reference</span>
      </div>
      <h1 class="font-display text-[32px] min-[829px]:text-[52px] tracking-wide text-[--w] leading-tight">
        Design System
      </h1>
      <p class="text-[--w60] text-[17px] mt-3 max-w-lg leading-relaxed">
        Complete visual reference for colors, typography, components, interaction patterns,
        and design principles of TheFoxxStuff.
      </p>
      <div class="flex items-center gap-4 mt-6">
        <a href="/design" class="inline-flex items-center gap-2 text-xs px-3 py-1.5 rounded-full transition-colors no-underline hover:text-[--w] hover:bg-[--w8]" style="color: var(--w40); background: var(--w5);">
          <span>Version 1.0</span>
          <ChevronRight size={12} />
        </a>
        <span class="text-xs" style="color: var(--w30);">
          {sections.length} sections &middot; 50+ components
        </span>
      </div>
    </div>
  </div>

  <!-- ════════════ STICKY SECTION NAV ════════════ -->
  <nav class="mb-12 sticky top-[60px] z-30 rounded-xl overflow-hidden" style="background: var(--header); border: 1px solid var(--w8);">
    <div class="p-3">
      <div class="flex flex-wrap gap-1.5">
        {#each sections as section}
          {@const Comp = section.icon}
          <a
            href="#{section.id}"
            class="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full transition-colors no-underline hover:text-[--w] hover:bg-[--w12]"
            style="color: var(--w40); background: var(--w5);"
          >
            {#if section.icon}
              <Comp size={12} />
            {/if}
            {section.label}
          </a>
        {/each}
      </div>
    </div>
  </nav>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- 1. FOUNDATIONS                                         -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section id="foundations" class="mb-24 scroll-mt-24">
    <div class="flex items-center gap-3 mb-8">
      <span class="text-xs font-mono px-2 py-1 rounded-md" style="background: var(--w5); color: var(--w30);">01</span>
      <h2 class="font-display text-[24px] tracking-wide">Foundations</h2>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <!-- Design Philosophy -->
      <div class="card p-6" style="background: linear-gradient(135deg, var(--w8), var(--w5));">
        <div class="w-10 h-10 rounded-xl flex items-center justify-center mb-4" style="background: rgba(115,238,7,0.1);">
          <Sparkles size={20} style="color: var(--green);" />
        </div>
        <h3 class="text-sm font-semibold text-[--w] mb-2">Design Philosophy</h3>
        <p class="text-xs leading-relaxed" style="color: var(--w60);">
          Dark-first interface with bold typography (DrukWideCyr) and warm neutral palette.
          Green accent guides attention. Surfaces built from white-with-opacity layers.
        </p>
      </div>

      <!-- CSS Architecture -->
      <div class="card p-6" style="background: linear-gradient(135deg, var(--w8), var(--w5));">
        <div class="w-10 h-10 rounded-xl flex items-center justify-center mb-4" style="background: rgba(71,173,255,0.1);">
          <Code size={20} style="color: var(--blue);" />
        </div>
        <h3 class="text-sm font-semibold text-[--w] mb-2">CSS Architecture</h3>
        <div class="space-y-1.5">
          <div class="flex items-center gap-2">
            <span class="text-xs px-1.5 py-0.5 rounded font-mono" style="background: var(--w5); color: var(--green);">@layer base</span>
            <span class="text-xs" style="color: var(--w40);">CSS variables, font-face, scrollbar</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs px-1.5 py-0.5 rounded font-mono" style="background: var(--w5); color: var(--blue);">@layer components</span>
            <span class="text-xs" style="color: var(--w40);">.btn, .card, .input, .badge, .tag</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs px-1.5 py-0.5 rounded font-mono" style="background: var(--w5); color: var(--purple);">@layer utilities</span>
            <span class="text-xs" style="color: var(--w40);">.text-gradient</span>
          </div>
        </div>
      </div>

      <!-- Theme System -->
      <div class="card p-6" style="background: linear-gradient(135deg, var(--w8), var(--w5));">
        <div class="w-10 h-10 rounded-xl flex items-center justify-center mb-4" style="background: rgba(109,7,238,0.1);">
          <Moon size={20} style="color: var(--purple);" />
        </div>
        <h3 class="text-sm font-semibold text-[--w] mb-2">Theme System</h3>
        <div class="space-y-1.5">
          <div class="flex items-center gap-2">
            <span class="w-4 h-4 rounded-full" style="background: var(--bg); border: 1px solid var(--w12);"></span>
            <span class="text-xs" style="color: var(--w60);">Dark &mdash; default, `rgb(17,17,17)`</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="w-4 h-4 rounded-full" style="background: #f0efeb; border: 1px solid var(--w12);"></span>
            <span class="text-xs" style="color: var(--w60);">Light &mdash; `#f0efeb`</span>
          </div>
          <div class="flex items-center gap-2">
            <button class="inline-flex items-center justify-center w-7 h-7 rounded-md transition-colors hover:bg-[--w12] hover:text-[--w]" style="background: var(--w8); color: var(--w60);" type="button" onclick={() => $theme = $theme === 'dark' ? 'light' : 'dark'}>
              {#if $theme === 'dark'}<Sun size={13} />{:else}<Moon size={13} />{/if}
            </button>
            <span class="text-xs" style="color: var(--w40);">Toggle here (live demo)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Transition specs -->
    <div class="card p-6">
      <h3 class="text-xs font-semibold text-[--w80] mb-4 uppercase tracking-wider">Global Transition Tokens</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        {#each [
          { token: '0.15s', usage: 'Card hover, quick micro', scope: 'ease' },
          { token: '0.16s', usage: 'Button transition-all', scope: 'duration-160' },
          { token: '0.2s', usage: 'Global bg/border/color', scope: 'ease' },
          { token: '0.25s', usage: 'Body theme, page-level', scope: 'ease' },
        ] as t}
          <div class="text-center">
            <div class="text-lg font-mono font-bold text-[--w]">{t.token}</div>
            <div class="text-[11px] mt-1" style="color: var(--w40);">{t.usage}</div>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- 2. COLORS                                              -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section id="colors" class="mb-24 scroll-mt-24">
    <div class="flex items-center gap-3 mb-8">
      <span class="text-xs font-mono px-2 py-1 rounded-md" style="background: var(--w5); color: var(--w30);">02</span>
      <h2 class="font-display text-[24px] tracking-wide">Colors</h2>
    </div>

    <!-- Brand Colors -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Brand Triad</h3>
    <div class="grid grid-cols-3 gap-3 mb-8">
      {#each [
        { var: '--green', dark: '#73EE07', light: '#4dbd00', label: 'Green', desc: 'Primary accent, CTAs, success' },
        { var: '--purple', dark: '#6D07EE', light: '#5b05c7', label: 'Purple', desc: 'Secondary accent, gradients' },
        { var: '--blue', dark: '#47ADFF', light: '#2563eb', label: 'Blue', desc: 'Active states, player, pagination' },
      ] as color}
        <div class="rounded-xl overflow-hidden card-hover cursor-pointer group" role="button" tabindex="0" onclick={() => copyToClipboard(color.dark, 'brand-'+color.var)} onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); copyToClipboard(color.dark, 'brand-'+color.var); } }}>
          <div class="h-28 relative transition-all group-hover:opacity-90" style="background: var({color.var});">
            <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              {#if copiedCode === 'brand-'+color.var}
                <Check size={20} style="color: var(--bg);" />
              {:else}
                <Copy size={20} style="color: var(--bg);" />
              {/if}
            </div>
          </div>
          <div class="p-4">
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm font-semibold text-[--w]">{color.label}</span>
              <span class="text-xs font-mono" style="color: var(--w40);">var({color.var})</span>
            </div>
            <div class="flex items-center gap-3 text-[11px]" style="color: var(--w40);">
              <span>Dark: {color.dark}</span>
              <span>Light: {color.light}</span>
            </div>
            <div class="text-[11px] mt-1" style="color: var(--w30);">{color.desc}</div>
          </div>
        </div>
      {/each}
    </div>

    <!-- Tailwind Accent Colors -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Tailwind Accent Colors</h3>
    <div class="grid grid-cols-3 gap-3 mb-8">
      {#each [
        { name: 'accent-green', hex: '#4ade80', usage: 'Admin badges, online indicators, success CTAs' },
        { name: 'accent-cyan', hex: '#22d3ee', usage: 'Gradient text, informational accents' },
        { name: 'accent-red', hex: '#ef4444', usage: 'Destructive actions, errors, danger states' },
      ] as color}
        <div class="rounded-xl overflow-hidden card" role="button" tabindex="0" onclick={() => copyToClipboard(color.hex, 'accent-'+color.name)} onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); copyToClipboard(color.hex, 'accent-'+color.name); } }}>
          <div class="h-20 relative" style="background: {color.hex};">
            <div class="absolute inset-0 flex items-center justify-center">
              <span class="text-[11px] font-bold" style="color: {color.hex === '#4ade80' ? '#0a0a0a' : 'white'};">{color.hex}</span>
            </div>
          </div>
          <div class="p-3">
            <div class="text-xs font-mono text-[--w]">{color.name}</div>
            <div class="text-[11px] mt-0.5" style="color: var(--w40);">{color.usage}</div>
          </div>
        </div>
      {/each}
    </div>

    <!-- Surface Hierarchy -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Surface Hierarchy</h3>
    <div class="card p-6 mb-8">
      <div class="space-y-3">
        {#each [
          { var: '--w5', pct: '5%', label: 'Base Surface', usage: 'Cards, panels, lightest layer' },
          { var: '--w8', pct: '8%', label: 'Raised Surface', usage: 'Inputs bg, card hover state, form controls' },
          { var: '--w12', pct: '12%', label: 'Border / Divider', usage: 'Input borders, tag-active, card borders' },
          { var: '--w18', pct: '18%', label: 'Hover / Active', usage: 'Hover borders, heavier overlays' },
        ] as item, i}
          <div class="flex items-center gap-4">
            <div class="w-24 shrink-0">
              <span class="text-sm font-medium text-[--w]">--{item.var.split('--')[1] || item.var}</span>
              <span class="text-[10px] block" style="color: var(--w30);">{item.pct}</span>
            </div>
            <div class="flex-1 h-10 rounded-lg overflow-hidden relative" style="background: var(--w8);">
              <div class="absolute inset-0 h-full" style="background: var({item.var}); width: {80 - i * 12}%;"></div>
            </div>
            <div class="w-40 shrink-0 hidden md:block">
              <span class="text-[11px]" style="color: var(--w40);">{item.usage}</span>
            </div>
          </div>
        {/each}
      </div>
    </div>

    <!-- Text Hierarchy -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Text Hierarchy</h3>
    <div class="card p-6 mb-8">
      <div class="space-y-4">
        {#each [
          { var: '--w', pct: '100%', role: 'Primary text — headings, important content' },
          { var: '--w80', pct: '80%', role: 'Secondary text — body copy, descriptions' },
          { var: '--w60', pct: '60%', role: 'Tertiary — labels, placeholders, metadata' },
          { var: '--w40', pct: '40%', role: 'Hints — helper text, disabled, captions' },
          { var: '--w30', pct: '30%', role: 'Muted — dividers, empty states, de-emphasized' },
        ] as t}
          <div class="flex items-baseline gap-4">
            <span class="text-xs font-mono w-14 shrink-0 tabular-nums" style="color: var(--w30);">{t.pct}</span>
            <div class="flex-1 min-w-0">
              <span class="text-[16px]" style="color: var({t.var});">
                The quick brown fox jumps over the lazy dog
              </span>
              <span class="text-[11px] block mt-0.5" style="color: var(--w30);">{t.role}</span>
            </div>
          </div>
        {/each}
      </div>
    </div>

    <!-- ::selection preview -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Selection</h3>
    <div class="card p-6">
      <p class="text-[15px] leading-relaxed" style="color: var(--w60);">
        Select this text to see the custom style &mdash; lime-green background with bright green text, no text shadow.
        Defined via <code class="text-xs px-1.5 py-0.5 rounded font-mono" style="background: var(--w8); color: var(--w60);">::selection</code> in <code class="text-xs px-1.5 py-0.5 rounded font-mono" style="background: var(--w8); color: var(--w60);">app.css</code>,
        using a dark transparent background with <code class="text-xs px-1.5 py-0.5 rounded font-mono" style="background: var(--w8); color: var(--green);">#88ff00</code> text.
      </p>
    </div>
  </section>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- 3. TYPOGRAPHY                                          -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section id="typography" class="mb-24 scroll-mt-24">
    <div class="flex items-center gap-3 mb-8">
      <span class="text-xs font-mono px-2 py-1 rounded-md" style="background: var(--w5); color: var(--w30);">03</span>
      <h2 class="font-display text-[24px] tracking-wide">Typography</h2>
    </div>

    <!-- Font Families Side by Side -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
      <div class="card p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <Type size={16} style="color: var(--green);" />
            <span class="text-sm font-semibold text-[--w]">Display</span>
          </div>
          <code class="text-xs px-2 py-1 rounded font-mono" style="background: var(--w5); color: var(--w40);">font-display</code>
        </div>
        <div class="font-display text-[22px] tracking-wide mb-2 leading-tight">
          Съешь ещё этих мягких французских булок
        </div>
        <div class="text-[11px]" style="color: var(--w40);">
          DrukWideCyr &middot; Medium weight &middot; /fonts/DrukWideCyrMedium.woff2 &middot; swap
        </div>
        <div class="mt-4 space-y-2">
          <div class="font-display text-[28px] tracking-wide text-[--w]">Hero Headline</div>
          <div class="font-display text-[24px] tracking-wide text-[--w]">Section Title</div>
          <div class="font-display text-[20px] tracking-wide text-[--w]">Card Heading</div>
          <div class="font-display text-[16px] tracking-wide text-[--w]">Small Label</div>
        </div>
      </div>
      <div class="card p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <Type size={16} style="color: var(--blue);" />
            <span class="text-sm font-semibold text-[--w]">Body</span>
          </div>
          <code class="text-xs px-2 py-1 rounded font-mono" style="background: var(--w5); color: var(--w40);">font-sans</code>
        </div>
        <div class="text-[16px] leading-relaxed mb-2">
          Съешь ещё этих мягких французских булок, да выпей чаю.
        </div>
        <div class="text-[11px]" style="color: var(--w40);">
          Golos-Text &middot; Variable weight 100&ndash;900 &middot; woff2-variations &middot; swap
        </div>
        <div class="mt-4 space-y-2 text-[15px] leading-relaxed text-[--w60]">
          <p>Body text uses Golos-Text Regular as a variable font, allowing smooth weight transitions from 100 to 900.</p>
          <p class="text-[13px]" style="color: var(--w40);">System fallback chain: 'Golos-Regular', system-ui, sans-serif</p>
        </div>
      </div>
    </div>

    <!-- Type Scale -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Type Scale</h3>
    <div class="card p-6 mb-8">
      <div class="space-y-6">
        {#each [
          { cls: 'font-display text-[42px] tracking-wide', label: 'Hero H1', spec: 'DrukWideCyr · 42px · desktop (32px mobile)' },
          { cls: 'font-display text-[24px] tracking-wide', label: 'Section H2', spec: 'DrukWideCyr · 24px' },
          { cls: 'font-display text-[20px] tracking-wide', label: 'Card H3', spec: 'DrukWideCyr · 20px' },
          { cls: 'text-[18px] text-[--w80]', label: 'Large Body', spec: 'Golos · 18px · lead paragraphs' },
          { cls: 'text-[16px] text-[--w60]', label: 'Body Text', spec: 'Golos · 16px · default paragraph' },
          { cls: 'text-[14px] text-[--w60]', label: 'Small Text', spec: 'Golos · 14px · captions, metadata' },
          { cls: 'text-[12px] text-[--w40]', label: 'Extra Small', spec: 'Golos · 12px · hints, labels, timestamps' },
          { cls: 'text-[10px] text-[--w40] tracking-wider uppercase', label: 'Micro Label', spec: 'Golos · 10px · badges, section numbers' },
        ] as t}
          <div class="border-b pb-4 last:border-0" style="border-color: var(--w8);">
            <div class="flex items-baseline gap-4 flex-col md:flex-row">
              <span class="{t.cls} text-[--w]">{t.label}</span>
              <span class="text-[11px] font-mono" style="color: var(--w30);">{t.spec}</span>
            </div>
          </div>
        {/each}
      </div>
    </div>

    <!-- Font Weight Scale -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Font Weight Scale (Golos Variable)</h3>
    <div class="card p-6 mb-8">
      <div class="space-y-3">
        {#each fontWeights as weight}
          <div class="flex items-center gap-4">
            <span class="text-[11px] font-mono w-10 shrink-0 tabular-nums" style="color: var(--w30);">{weight}</span>
            <span class="text-[18px] text-[--w80]" style="font-weight: {weight};">
              The quick brown fox
            </span>
          </div>
        {/each}
      </div>
    </div>

    <!-- Text Variants -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Text Variants</h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="card p-6">
        <div class="text-[11px] font-mono mb-2" style="color: var(--w30);">.text-gradient</div>
        <div class="text-[28px] font-bold text-gradient">Gradient from green to cyan</div>
        <div class="text-[11px] mt-2" style="color: var(--w40);">bg-gradient-to-r from-accent-green to-accent-cyan</div>
      </div>
      <div class="card p-6">
        <div class="text-[11px] font-mono mb-2" style="color: var(--w30);">Smart date colors (BlogCard)</div>
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full" style="background: #4ade80;"></span>
            <span class="text-sm text-[--w60]">Fresh (<span class="text-[11px] font-mono" style="color: var(--w40);">&lt;7d</span>) &mdash; green, sometimes gradient</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full" style="background: #22d3ee;"></span>
            <span class="text-sm text-[--w60]">Recent (<span class="text-[11px] font-mono" style="color: var(--w40);">&lt;30d</span>) &mdash; cyan</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full" style="background: var(--w40);"></span>
            <span class="text-sm text-[--w60]">Older &mdash; muted gray</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- 4. SPACING                                             -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section id="spacing" class="mb-24 scroll-mt-24">
    <div class="flex items-center gap-3 mb-8">
      <span class="text-xs font-mono px-2 py-1 rounded-md" style="background: var(--w5); color: var(--w30);">04</span>
      <h2 class="font-display text-[24px] tracking-wide">Spacing &amp; Layout</h2>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
      <!-- Tailwind Spacing Scale -->
      <div class="card p-6">
        <h3 class="text-xs font-semibold text-[--w80] mb-4 uppercase tracking-wider">Gap Scale</h3>
        <div class="space-y-2.5">
          {#each [
            { cls: 'gap-1', val: '4px' },
            { cls: 'gap-2', val: '8px' },
            { cls: 'gap-3', val: '12px' },
            { cls: 'gap-4', val: '16px' },
            { cls: 'gap-6', val: '24px' },
            { cls: 'gap-8', val: '32px' },
          ] as item}
            <div class="flex items-center gap-3">
              <span class="text-[11px] font-mono w-10 shrink-0" style="color: var(--w40);">{item.cls}</span>
              <div class="flex gap-[{item.val}] flex-1">
                <div class="h-6 rounded" style="background: var(--w12); flex: 1;"></div>
                <div class="h-6 rounded" style="background: var(--w12); flex: 1;"></div>
                <div class="h-6 rounded" style="background: var(--w12); flex: 1;"></div>
              </div>
              <span class="text-[11px] font-mono w-10 text-right" style="color: var(--w30);">{item.val}</span>
            </div>
          {/each}
        </div>
      </div>

      <!-- Border Radii -->
      <div class="card p-6">
        <h3 class="text-xs font-semibold text-[--w80] mb-4 uppercase tracking-wider">Border Radius</h3>
        <div class="grid grid-cols-3 gap-4">
          {#each [
            { val: '5px', label: 'badge' },
            { val: '6px', label: 'modal inner' },
            { val: '8px', label: 'buttons, inputs' },
            { val: '10px', label: 'player, md-editor' },
            { val: '0.75rem', label: 'cards' },
            { val: '20px', label: 'pill, circle' },
          ] as item}
            <div class="flex flex-col items-center gap-2">
              <div class="w-12 h-12 flex items-center justify-center text-[10px] font-mono"
                   style="background: var(--w8); border: 1px solid var(--w12); border-radius: {item.val}; color: var(--w30);">
                {item.val}
              </div>
              {#if item.label}
                <span class="text-[10px] text-center" style="color: var(--w30);">{item.label}</span>
              {/if}
            </div>
          {/each}
        </div>
      </div>
    </div>

    <!-- Breakpoints -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Breakpoints</h3>
    <div class="card p-6 mb-8">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        {#each [
          { name: 'Mobile', range: '< 600px', cls: 'default', desc: 'Phone' },
          { name: 'Mobile+', range: '≥ 768px', cls: 'md:', desc: 'Tablet' },
          { name: 'PC', range: '≥ 829px', cls: 'min-[829px]:', desc: 'Custom "pc"' },
          { name: 'Desktop', range: '≥ 829px', cls: 'pc:', desc: 'Full layout' },
        ] as bp}
          <div class="text-center">
            <div class="text-[14px] font-medium text-[--w] mb-1">{bp.name}</div>
            <div class="text-[11px] font-mono" style="color: var(--w40);">{bp.range}</div>
            <code class="inline-block mt-1.5 text-[10px] px-1.5 py-0.5 rounded font-mono" style="background: var(--w5); color: var(--w40);">{bp.cls}</code>
            <div class="text-[10px] mt-1" style="color: var(--w30);">{bp.desc}</div>
          </div>
        {/each}
      </div>
    </div>

    <!-- Max Widths -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Max Widths</h3>
    <div class="card p-6">
      <div class="space-y-3">
        {#each [
          { name: 'Main Content', cls: 'max-w-[828px]', usage: 'All pages, admin content, hero section' },
          { name: 'Admin Panels', cls: 'max-w-[480px]', usage: 'Admin create/edit form cards, side panels' },
          { name: 'Music Player', cls: 'w-[776px]', usage: 'Fixed bottom floating player' },
          { name: 'User Menu Dropdown', cls: 'w-[224px]', usage: 'Header dropdown, context menus' },
        ] as mw}
          <div class="flex items-center gap-3">
            <span class="text-sm text-[--w] min-w-[140px]">{mw.name}</span>
            <span class="text-[11px] font-mono px-2 py-0.5 rounded" style="background: var(--w5); color: var(--w40);">{mw.cls}</span>
            <span class="text-[11px]" style="color: var(--w30);">{mw.usage}</span>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- 5. BUTTONS                                             -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section id="buttons" class="mb-24 scroll-mt-24">
    <div class="flex items-center gap-3 mb-8">
      <span class="text-xs font-mono px-2 py-1 rounded-md" style="background: var(--w5); color: var(--w30);">05</span>
      <h2 class="font-display text-[24px] tracking-wide">Buttons</h2>
    </div>

    <!-- Primary action group -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Primary Actions (Tailwind @layer)</h3>
    <div class="card p-6 mb-8">
      <div class="flex flex-wrap gap-3 items-end mb-4">
        <button class="btn btn-primary">Primary Action</button>
        <button class="btn btn-primary" disabled>Disabled</button>
      </div>
      <div class="flex flex-wrap gap-2 text-[11px]" style="color: var(--w30);">
        <span>bg-accent-green (text-dark-950)</span>
        <span>hover:bg-accent-green/90</span>
        <span>disabled:opacity-50</span>
      </div>
    </div>

    <!-- Secondary & Danger -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
      <div class="card p-6">
        <div class="text-[11px] font-mono mb-3" style="color: var(--w30);">.btn-secondary</div>
        <div class="flex flex-wrap gap-3 mb-4">
          <button class="btn btn-secondary">Secondary</button>
          <button class="btn btn-secondary" disabled>Disabled</button>
        </div>
        <div class="text-[11px]" style="color: var(--w30);">bg: var(--w8) / border: var(--w12) / hover: var(--w12)</div>
      </div>
      <div class="card p-6">
        <div class="text-[11px] font-mono mb-3" style="color: var(--w30);">.btn-danger</div>
        <div class="flex flex-wrap gap-3 mb-4">
          <button class="btn btn-danger">Delete</button>
          <button class="btn btn-danger" disabled>Disabled</button>
        </div>
        <div class="text-[11px]" style="color: var(--w30);">bg-accent-red / text-white / hover:bg-accent-red/90</div>
      </div>
    </div>

    <!-- Button Component (with icons) -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Button Component (Svelte)</h3>
    <div class="card p-6 mb-8">
      <div class="text-[11px] font-mono mb-4" style="color: var(--w30);">
        &lt;Button iconRight={ChevronRight}&gt;Show more&lt;/Button&gt;
      </div>
      <div class="flex flex-wrap gap-3">
        <button class="group inline-flex items-center gap-[4px] px-[12px] py-[6px] bg-[--w5] hover:bg-[--w8] text-[#999] hover:text-[--w] rounded-[8px] transition-all duration-160 cursor-pointer">
          <span class="text-[14px] font-medium tracking-wide">Show More</span>
          <span class="flex items-center group-hover:text-[--w] transition-colors"><ChevronRight size={16} strokeWidth={2.5} /></span>
        </button>
        <button class="group inline-flex items-center gap-[4px] px-[12px] py-[6px] bg-[--w5] hover:bg-[--w8] text-[#999] hover:text-[--w] rounded-[8px] transition-all duration-160 cursor-pointer">
          <span class="flex items-center group-hover:opacity-80 transition-opacity"><Music size={16} strokeWidth={2.5} /></span>
          <span class="text-[14px] font-medium tracking-wide">Music</span>
        </button>
        <button class="group inline-flex items-center gap-[4px] px-[12px] py-[6px] bg-[--w5] hover:bg-[--w8] text-[#999] hover:text-[--w] rounded-[8px] transition-all duration-160 cursor-pointer">
          <span class="flex items-center group-hover:opacity-80 transition-opacity"><Download size={16} strokeWidth={2.5} /></span>
          <span class="text-[14px] font-medium tracking-wide">Download</span>
          <span class="flex items-center group-hover:text-[--w] transition-colors"><ArrowUpRight size={16} strokeWidth={2.5} /></span>
        </button>
        <button class="group inline-flex items-center gap-[4px] px-[12px] py-[6px] bg-[--w5] hover:bg-[--w8] text-[#999] hover:text-[--w] rounded-[8px] transition-all duration-160 cursor-pointer">
          <span class="flex items-center group-hover:opacity-80 transition-opacity"><Settings size={16} strokeWidth={2.5} /></span>
          <span class="text-[14px] font-medium tracking-wide">Settings</span>
          <span class="flex items-center group-hover:text-[--w] transition-colors"><ChevronRight size={16} strokeWidth={2.5} /></span>
        </button>
      </div>
    </div>

    <!-- Specialized variants -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
      <div class="card p-6">
        <div class="text-[11px] font-mono mb-3" style="color: var(--w30);">.btn-breadcrumb</div>
        <div class="flex flex-wrap gap-2 mb-4">
          <button class="btn-breadcrumb">Dashboard</button>
          <span style="color: var(--w30);">/</span>
          <button class="btn-breadcrumb">Blog</button>
          <span style="color: var(--w30);">/</span>
          <button class="btn-breadcrumb" disabled>Post</button>
        </div>
        <div class="text-[11px]" style="color: var(--w30);">Gap 6px / px 12 / py 6 / 14px font / disabled:opacity-5</div>
      </div>
      <div class="card p-6">
        <div class="text-[11px] font-mono mb-3" style="color: var(--w30);">.filter</div>
        <div class="flex flex-wrap gap-2 mb-4">
          <button class="filter">All</button>
          <button class="filter">Music</button>
          <button class="filter">Arts</button>
          <button class="filter">Blog</button>
          <button class="filter" disabled>Disabled</button>
        </div>
        <div class="text-[11px]" style="color: var(--w30);">bg w5 / text w60 / hover: text w + bg w8</div>
      </div>
    </div>

    <!-- CTA Hero Button -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Hero CTA Pattern</h3>
    <div class="card p-6">
      <button class="inline-flex items-center gap-2 px-5 py-2.5 bg-[--green] text-[--b] rounded-[8px] text-[14px] font-bold hover:opacity-90 transition-all hover:scale-[1.02] active:scale-[0.98]">
        <Play size={16} /> Play Latest Release
      </button>
      <span class="inline-flex items-center gap-2 px-5 py-2.5 bg-[--w8] text-[--w] rounded-[8px] text-[14px] font-medium hover:bg-[--w12] transition-all ml-3">
        About me &rarr;
      </span>
      <div class="text-[11px] mt-3" style="color: var(--w30);">hover:scale-[1.02] / active:scale-[0.98] / opacity-90 hover</div>
    </div>
  </section>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- 6. INPUTS                                              -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section id="inputs" class="mb-24 scroll-mt-24">
    <div class="flex items-center gap-3 mb-8">
      <span class="text-xs font-mono px-2 py-1 rounded-md" style="background: var(--w5); color: var(--w30);">06</span>
      <h2 class="font-display text-[24px] tracking-wide">Inputs &amp; Forms</h2>
    </div>

    <!-- Standard Form -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
      <div class="card p-6 space-y-5">
        <div>
          <div class="label">Text Input</div>
          <input bind:value={demoInput} type="text" class="input" placeholder="Enter text..." />
        </div>
        <div>
          <div class="label">Email</div>
          <input type="email" class="input" placeholder="you@example.com" />
        </div>
        <div>
          <div class="label">Textarea</div>
          <textarea bind:value={demoTextarea} class="textarea" rows="3" placeholder="Multi-line text..."></textarea>
        </div>
        <div>
          <div class="label">Disabled</div>
          <input type="text" class="input" value="Cannot edit" disabled />
        </div>
        <div class="flex items-center gap-2 pt-2">
          <input type="checkbox" bind:checked={demoChecked} id="demoCheck" class="accent-accent-green w-4 h-4" />
          <label for="demoCheck" class="text-sm text-[--w60] cursor-pointer">Checkbox label</label>
        </div>
        <div class="flex gap-2 pt-2">
          <button class="btn btn-primary">Submit</button>
          <button class="btn btn-secondary">Cancel</button>
        </div>
      </div>

      <!-- Focus & State Details -->
      <div class="space-y-4">
        <div class="card p-6">
          <h4 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">CSS Variables</h4>
          <div class="space-y-2 text-[12px]">
            <div class="flex justify-between items-center">
              <code class="font-mono text-[--w60]">.input</code>
              <span style="color: var(--w40);">bg w8 / border w12 / focus: green ring</span>
            </div>
            <div class="flex justify-between items-center">
              <code class="font-mono text-[--w60]">.textarea</code>
              <span style="color: var(--w40);">same + more padding, resize-none</span>
            </div>
            <div class="flex justify-between items-center">
              <code class="font-mono text-[--w60]">.label</code>
              <span style="color: var(--w40);">sm / medium / mb-1 / color w60</span>
            </div>
          </div>
        </div>
        <div class="card p-6">
          <h4 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Focus State</h4>
          <div class="flex items-center gap-3 mb-3">
            <span class="inline-block w-20 h-8 rounded-md" style="border: 2px solid rgba(74,222,128,0.5); box-shadow: 0 0 0 1px rgba(74,222,128,0.5);"></span>
            <div>
              <div class="text-sm text-[--w]">Green ring visible</div>
              <div class="text-[11px]" style="color: var(--w40);">ring-1 ring-accent-green/50</div>
            </div>
          </div>
          <div class="text-[11px] font-mono" style="color: var(--w30);">
            focus:outline-none · focus:ring-1 · focus:ring-accent-green/50
          </div>
        </div>
        <div class="card p-6">
          <h4 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Search Bar (Header)</h4>
          <div class="relative">
            <input type="text" class="filter search pr-9 h-[32px] w-full" placeholder="Search..." />
            <span class="absolute right-3 top-1/2 -translate-y-1/2" style="color: var(--w40);">
              <Search size={16} />
            </span>
          </div>
          <div class="text-[11px] mt-2" style="color: var(--w40);">
            .filter + .search · h-32px · animates open/closed in header
          </div>
        </div>
      </div>
    </div>

    <!-- Upload Zones -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Upload Zones</h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="card p-6">
        <h4 class="text-xs font-semibold text-[--w60] mb-3">ImageUpload (Single)</h4>
        <div class="upload-zone cursor-pointer p-8 flex flex-col items-center justify-center text-center" style="transition: all 0.2s;">
          <Image size={40} style="color: var(--w30);" />
          <div class="text-sm mt-3" style="color: var(--w40);">Drag &amp; drop or click to upload</div>
          <button class="btn btn-secondary text-sm mt-3">Choose File</button>
        </div>
      </div>
      <div class="card p-6">
        <h4 class="text-xs font-semibold text-[--w60] mb-3">MultiImageUpload</h4>
        <div class="upload-zone cursor-pointer p-8 flex flex-col items-center justify-center text-center" style="transition: all 0.2s;">
          <Plus size={28} style="color: var(--w30);" />
          <div class="text-sm mt-2" style="color: var(--w40);">Drag &amp; drop or click to add images</div>
        </div>
        <div class="grid grid-cols-4 gap-2 mt-4">
          {#each [1,2,3] as i}
            <div class="aspect-square rounded-lg overflow-hidden relative group" style="background: var(--w8);">
              <div class="w-full h-full flex items-center justify-center" style="color: var(--w30);">
                <Image size={20} />
              </div>
              <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-1">
                <button class="p-1 rounded hover:bg-[--w12] transition-colors" style="background: var(--w8); color: var(--w60);"><ChevronLeft size={12} /></button>
                <button class="p-1 rounded hover:bg-[--w12] transition-colors" style="background: var(--w8); color: var(--w60);"><ChevronRight size={12} /></button>
                <button class="p-1 rounded hover:bg-[rgba(239,68,68,0.4)] transition-colors" style="background: rgba(239,68,68,0.2); color: #ef4444;"><X size={12} /></button>
              </div>
            </div>
          {/each}
        </div>
      </div>
    </div>
  </section>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- 7. CARDS                                               -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section id="cards" class="mb-24 scroll-mt-24">
    <div class="flex items-center gap-3 mb-8">
      <span class="text-xs font-mono px-2 py-1 rounded-md" style="background: var(--w5); color: var(--w30);">07</span>
      <h2 class="font-display text-[24px] tracking-wide">Cards</h2>
    </div>

    <!-- Card Variants -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
      <div class="card p-6">
        <div class="text-[11px] font-mono mb-3" style="color: var(--w30);">Standard .card</div>
        <p class="text-sm text-[--w60]">bg: var(--w5) / border: var(--w8) / radius: 0.75rem / overflow: hidden</p>
      </div>
      <div class="card p-6 card-hover cursor-pointer">
        <div class="text-[11px] font-mono mb-3" style="color: var(--w30);">.card-hover</div>
        <p class="text-sm text-[--w60]">Interactive card &mdash; hover to see background transition to var(--w8)</p>
      </div>
    </div>

    <!-- MusicCard -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">MusicCard</h3>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div class="group rounded-[8px] px-[18px] py-[18px] bg-[--w5] hover:bg-[--w8] duration-100 block" style="cursor: pointer;">
        <div class="aspect-square rounded-[8px] overflow-hidden bg-[--w8] mb-[14px] relative">
          <div class="w-full h-full flex items-center justify-center text-dark-600">
            <Music size={48} style="color: var(--w30);" />
          </div>
          <span class="absolute top-2 right-2 px-2 py-1 text-xs font-medium bg-[--green] text-[--b] rounded">NEW RELEASE</span>
        </div>
        <span class="text-[18px] text-[--w] tracking-wide truncate block">New Album</span>
        <p class="text-[14px] text-[--w60]">April 28, 2024</p>
      </div>
      <div class="group rounded-[8px] px-[18px] py-[18px] bg-[--w5] hover:bg-[--w8] duration-100 block" style="cursor: pointer;">
        <div class="aspect-square rounded-[8px] overflow-hidden bg-[--w8] mb-[14px] relative">
          <div class="w-full h-full flex items-center justify-center text-dark-600">
            <Music size={48} style="color: var(--w30);" />
          </div>
        </div>
        <span class="text-[18px] text-[--w] tracking-wide truncate block">Single Title</span>
        <p class="text-[14px] text-[--w60]">March 12, 2024</p>
      </div>
    </div>

    <!-- BlogCard -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">BlogCard</h3>
    <div class="mb-8">
      <div class="group flex flex-col h-full bg-[--w5] hover:bg-[--w8] transition-all duration-300 rounded-[12px]" style="cursor: pointer;">
        <div class="px-[18px] pt-[18px]">
          <div class="aspect-[16/10] bg-[--w12] rounded-[8px] overflow-hidden">
            <div class="w-full h-full flex items-center justify-center text-[--w30] bg-[--w8]">
              <FileText size={40} style="color: var(--w30);" />
            </div>
          </div>
        </div>
        <div class="flex-1 flex flex-col px-[18px] pt-[12px] pb-[18px]">
          <h3 class="font-bold text-[18px] leading-tight text-[--w] mb-1 line-clamp-2">Post Title Goes Here</h3>
          <p class="text-[14px] leading-relaxed text-[--w60] mb-2 line-clamp-2">A short excerpt from the post content that gives context about what the article covers.</p>
          <div class="mt-auto flex items-center justify-between pt-[12px]">
            <div class="flex items-center gap-2">
              <span style="color: #4ade80; flex-shrink: 0; display: flex; align-items: center;"><Calendar size={14} /></span>
              <span class="text-[14px] font-medium" style="color: #4ade80;">April 28, 2024</span>
            </div>
            <div class="flex items-center gap-1 text-[--w60]">
              <Eye size={14} />
              <span class="text-[14px]">1.2k</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ArtCard -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">ArtCard (Square)</h3>
    <div class="grid grid-cols-4 gap-4 mb-8">
      {#each ['Art 1', 'Art 2', 'Art 3', 'Art 4'] as label, i}
        <div class="group" style="cursor: pointer;">
          <div class="aspect-square rounded-xl overflow-hidden bg-[--w8] group-hover:scale-105 transition-transform duration-500">
            <div class="w-full h-full flex items-center justify-center">
              <Palette size={32} style="color: var(--w30);" />
            </div>
          </div>
        </div>
      {/each}
    </div>

    <!-- Hero / FeaturedRelease -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Hero / FeaturedRelease</h3>
    <div class="relative rounded-[12px] overflow-hidden bg-[--w5] border border-[--w8] p-8 md:p-10">
      <div class="absolute inset-0 bg-gradient-to-br from-[rgba(115,238,7,0.05)] via-transparent to-[rgba(71,173,255,0.05)] pointer-events-none"></div>
      <div class="relative flex flex-col md:flex-row items-start md:items-center gap-6">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-3">
            <span class="inline-block w-2 h-2 rounded-full bg-[--green] animate-pulse"></span>
            <span class="text-[12px] text-[--green] font-medium tracking-widest uppercase">Musician &middot; Artist &middot; Blogger</span>
          </div>
          <div class="font-display text-[32px] md:text-[42px] tracking-wide text-[--w] leading-tight mb-3" style="font-family: 'DrukWideCyr';">
            THEF<span class="text-[--green]">O</span>XXSTUFF
          </div>
          <p class="text-[--w60] text-[15px] leading-relaxed max-w-md mb-6">
            Making music in the dark, painting strange worlds, writing about all of it.
            This is where it all lives.
          </p>
          <div class="flex flex-wrap gap-3">
            <button class="inline-flex items-center gap-2 px-5 py-2.5 bg-[--green] text-[--b] rounded-[8px] text-[14px] font-bold hover:opacity-90 transition-all hover:scale-[1.02] active:scale-[0.98]">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
              Play Latest Release
            </button>
            <a href="/about" class="inline-flex items-center gap-2 px-5 py-2.5 bg-[--w8] text-[--w] rounded-[8px] text-[14px] font-medium hover:bg-[--w12] transition-all no-underline">
              About me &rarr;
            </a>
          </div>
        </div>
        <div class="flex flex-row md:flex-col gap-3 flex-shrink-0">
          {#each [{ label: 'Music', href: '/music', icon: 'N' }, { label: 'Art', href: '/arts', icon: 'V' }, { label: 'Blog', href: '/blog', icon: 'V' }] as item}
            <a href={item.href} class="flex items-center gap-2 px-4 py-2 bg-[--w8] hover:bg-[--w12] rounded-[8px] text-[--w60] hover:text-[--w] transition-all text-[14px] no-underline">
              <span class="text-[--green] text-[16px]">{item.icon}</span>
              {item.label}
            </a>
          {/each}
        </div>
      </div>
    </div>
  </section>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- 8. FEEDBACK                                            -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section id="feedback" class="mb-24 scroll-mt-24">
    <div class="flex items-center gap-3 mb-8">
      <span class="text-xs font-mono px-2 py-1 rounded-md" style="background: var(--w5); color: var(--w30);">08</span>
      <h2 class="font-display text-[24px] tracking-wide">Feedback</h2>
    </div>

    <!-- Alerts -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Alert Messages</h3>
    <div class="space-y-3 mb-8">
      <!-- Error -->
      <div class="p-3 bg-accent-red/10 border border-accent-red/50 rounded-lg text-accent-red text-sm flex items-start gap-3">
        <AlertTriangle size={18} class="shrink-0 mt-0.5" />
        <div>
          <div class="font-medium">Error Alert</div>
          <div class="text-xs opacity-80 mt-0.5">Something went wrong. Please check your input and try again.</div>
        </div>
      </div>
      <!-- Success -->
      <div class="p-3 bg-accent-green/10 border border-accent-green/50 rounded-lg text-accent-green text-sm flex items-start gap-3">
        <Check size={18} class="shrink-0 mt-0.5" />
        <div>
          <div class="font-medium">Success Alert</div>
          <div class="text-xs opacity-80 mt-0.5">Changes saved successfully.</div>
        </div>
      </div>
    </div>

    <!-- Toast/Notification Pattern -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Loading States</h3>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div class="card p-6 flex items-center gap-3">
        <Loader2 size={20} class="animate-spin text-[--w40]" />
        <span class="text-sm text-[--w60]">Loading...</span>
      </div>
      <div class="card p-6 flex items-center gap-3">
        <div class="w-5 h-5 border-2 border-[--w30] border-t-[--green] rounded-full animate-spin"></div>
        <span class="text-sm text-[--w60]">Uploading...</span>
      </div>
      <div class="card p-6 flex items-center gap-3">
        <div class="flex gap-1">
          <span class="w-1.5 h-1.5 rounded-full bg-[--w40] animate-pulse"></span>
          <span class="w-1.5 h-1.5 rounded-full bg-[--w40] animate-pulse" style="animation-delay: 0.15s;"></span>
          <span class="w-1.5 h-1.5 rounded-full bg-[--w40] animate-pulse" style="animation-delay: 0.3s;"></span>
        </div>
        <span class="text-sm text-[--w60]">Processing</span>
      </div>
    </div>

    <!-- ViewingNow -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">ViewingNow Component</h3>
    <div class="card p-6 mb-8">
      <div class="inline-flex items-center gap-3 px-3 py-2 rounded-xl bg-[--w5] border border-[--w8] text-sm">
        <span class="relative flex-shrink-0 w-2 h-2">
          <span class="absolute inset-0 rounded-full bg-accent-green animate-ping opacity-50"></span>
          <span class="absolute inset-0.5 rounded-full bg-accent-green"></span>
        </span>
        <!-- Stacked avatars -->
        <div class="flex items-center">
          {#each ['Alice', 'Bob', 'Charlie'] as name, i}
            <div
              class="relative rounded-full ring-2 ring-[--ring] overflow-hidden"
              style="margin-left: {i === 0 ? 0 : -7}px; z-index: {3 - i}; width: 28px; height: 28px;"
            >
              <div class="w-full h-full flex items-center justify-center text-[9px] font-bold text-black" style="background: hsl({hue(name)}, 60%, 55%);">{name[0]}</div>
            </div>
          {/each}
          <div class="w-7 h-7 rounded-full bg-[--w8] ring-2 ring-[--ring] flex items-center justify-center text-[9px]" style="margin-left: -7px; color: var(--w50);">+4</div>
        </div>
        <span style="color: var(--w50);">
          <span class="text-[--w80] font-medium">7</span> viewing
        </span>
      </div>
      <div class="text-[11px] mt-3" style="color: var(--w30);">Ping + stacked avatars (max 6) + count text / shows only when count &gt; 0</div>
    </div>

    <!-- Live Pulse Indicators -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Status Indicators</h3>
    <div class="card p-6">
      <div class="flex flex-wrap items-center gap-6">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-[--green] animate-pulse inline-block"></span>
          <span class="text-sm text-[--w60]">Online (pulse)</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="relative flex-shrink-0 w-2 h-2">
            <span class="absolute inset-0 rounded-full bg-accent-green animate-ping opacity-50"></span>
            <span class="absolute inset-0.5 rounded-full bg-accent-green"></span>
          </span>
          <span class="text-sm text-[--w60]">Live (ping)</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-1.5 h-1.5 rounded-full bg-accent-green inline-block"></span>
          <span class="text-xs text-[--w30]">Static dot + count</span>
        </div>
      </div>
    </div>
  </section>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- 9. NAVIGATION                                          -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section id="navigation" class="mb-24 scroll-mt-24">
    <div class="flex items-center gap-3 mb-8">
      <span class="text-xs font-mono px-2 py-1 rounded-md" style="background: var(--w5); color: var(--w30);">09</span>
      <h2 class="font-display text-[24px] tracking-wide">Navigation</h2>
    </div>

    <!-- Admin top bar -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Admin Top Bar</h3>
    <div class="card mb-8 overflow-hidden" style="background: rgba(6,6,6,0.88);">
      <div class="flex items-center gap-3 px-4" style="height: 50px;">
        <a href="/" class="text-sm no-underline hover:text-[--w] flex items-center gap-2" style="color: var(--w60);">
          <span style="color: var(--w30);">&larr;</span>
          <span class="font-display text-[10px] tracking-wider" style="color: var(--green);">ADMIN</span>
        </a>
        <div class="flex gap-1 h-[30px] text-[13px] overflow-x-auto flex-1" style="scrollbar-width: none;">
          {#each [
            { href: '/admin', label: 'Dashboard', active: true },
            { href: '/admin/music', label: 'Music' },
            { href: '/admin/blog', label: 'Blog' },
            { href: '/admin/arts', label: 'Arts' },
            { href: '/admin/links', label: 'Links' },
            { href: '/admin/users', label: 'Users' },
            { href: '/admin/media', label: 'Media' },
            { href: '/admin/views-map', label: 'Views' },
          ] as item}
            <a href={item.href} class="flex items-center px-3 rounded-md no-underline shrink-0 h-full transition-colors hover:text-[--w]"
               style="color: var(--w60); {item.active ? 'background: var(--w8); color: var(--w);' : ''}">
              {item.label}
            </a>
          {/each}
        </div>
      </div>
    </div>

    <!-- Breadcrumb -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Breadcrumb</h3>
    <div class="card p-4 mb-8">
      <div class="flex items-center gap-[4px] text-sm" style="color: var(--w60);">
        <Home size={14} />
        <span style="color: var(--w40);">/</span>
        <a href="/blog" class="hover:text-[--w] transition-colors no-underline" style="color: var(--w60);">Blog</a>
        <ChevronRight size={14} />
        <span style="color: var(--w);">Article Title</span>
      </div>
    </div>

    <!-- Pagination -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Pagination</h3>
    <div class="card p-4 mb-8">
      <div class="flex items-center gap-2">
        <button class="w-[36px] h-[36px] rounded-[8px] flex items-center justify-center hover:bg-[--w8] hover:text-[--w] transition-colors" style="background: var(--w5); color: var(--w60);">
          <ChevronLeft size={16} />
        </button>
        {#each [1, 2, 3, '...', 12, 13, 14, 15, '...', 21] as page}
          {#if page === '...'}
            <span class="w-[36px] h-[36px] rounded-[8px] flex items-center justify-center text-sm" style="color: var(--w40);">&hellip;</span>
          {:else if page === 14}
            <button class="w-[36px] h-[36px] rounded-[8px] flex items-center justify-center text-sm font-bold" style="background: var(--blue); color: white;">{page}</button>
          {:else}
            <button class="w-[36px] h-[36px] rounded-[8px] flex items-center justify-center text-sm hover:bg-[--w8] hover:text-[--w] transition-colors" style="background: var(--w5); color: var(--w60);">{page}</button>
          {/if}
        {/each}
        <button class="w-[36px] h-[36px] rounded-[8px] flex items-center justify-center hover:bg-[--w8] hover:text-[--w] transition-colors" style="background: var(--w5); color: var(--w60);">
          <ChevronRight size={16} />
        </button>
      </div>
    </div>

    <!-- Header dropdown menu -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Dropdown / Context Menu</h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
      <!-- User menu dropdown -->
      <div class="card p-2" style="background: var(--select); border-color: var(--w12);">
        <div class="px-3 py-3 rounded-md transition hover:bg-[--w5]">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-[48px] h-[48px] rounded-full" style="background: hsl({hue('user')}, 60%, 55%);">
              <div class="w-full h-full flex items-center justify-center text-lg font-bold text-black">U</div>
            </div>
            <div>
              <div class="text-sm text-[--w] font-bold">Username</div>
              <div class="text-xs" style="color: var(--w60);">@user</div>
            </div>
          </div>
        </div>
        <div class="h-px bg-[--w8] my-1 mx-2"></div>
        <div class="px-2 pb-2 flex flex-col gap-0.5">
          <a href="/" class="flex items-center gap-[4px] px-3 py-1.5 text-[14px] text-[--w60] rounded-md transition hover:bg-[--w8] hover:text-[--w] no-underline" onclick={(e) => e.preventDefault()}>
            <Settings size={16} /> Profile settings
          </a>
          <div class="h-px bg-[--w8] my-0.5"></div>
          <a href="/" class="flex items-center gap-[4px] px-3 py-1.5 text-[14px] text-[--w60] rounded-md transition hover:bg-[--w8] hover:text-[--w] no-underline" onclick={(e) => e.preventDefault()}>
            <Shield size={16} /> Admin panel
          </a>
          <div class="h-px bg-[--w8] my-0.5"></div>
          <a href="/" class="flex items-center gap-[4px] px-3 py-1.5 text-[14px] text-accent-red rounded-md transition hover:bg-[--w8] no-underline" onclick={(e) => e.preventDefault()}>
            <LogOut size={16} /> Logout
          </a>
        </div>
      </div>

      <!-- Context menu -->
      <div>
        <div class="fixed z-[10001] min-w-[200px] backdrop-blur-xl border border-[--w12] rounded-xl p-1.5 shadow-2xl select-none"
             style="background: var(--select); position: relative; display: inline-block;">
          <button class="w-full flex items-center gap-2.5 px-2.5 py-2 text-sm text-[--w60] rounded-[8px] transition hover:bg-[--w8] hover:text-[--w]">
            <Copy size={16} /> Copy Action
          </button>
          <button class="w-full flex items-center gap-2.5 px-2.5 py-2 text-sm text-[--w60] rounded-[8px] transition hover:bg-[--w8] hover:text-[--w]">
            <Edit3 size={16} /> Edit
          </button>
          <div class="h-px bg-[--w8] my-0.5"></div>
          <button class="w-full flex items-center gap-2.5 px-2.5 py-2 text-sm text-accent-red rounded-[8px] transition hover:bg-[--w8]">
            <Trash2 size={16} /> Delete
          </button>
        </div>
        <div class="text-[11px] mt-16" style="color: var(--w30);">bg: var(--select) · backdrop-blur-xl · border: var(--w12) · radius: xl</div>
      </div>
    </div>

    <!-- Mobile navigation -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Mobile Navigation Preview</h3>
    <div class="card overflow-hidden">
      <div class="bg-[rgba(10,10,10,0.92)]" style="border-bottom: 1px solid rgba(255,255,255,0.06);">
        <div class="grid grid-cols-3 gap-0 p-2">
          {#each [
            { icon: Home, label: 'Home', active: false },
            { icon: Music, label: 'Music', active: false },
            { icon: Palette, label: 'Arts', active: false },
            { icon: FileText, label: 'Blog', active: false },
            { icon: LinkIcon, label: 'Links', active: false },
            { icon: Info, label: 'About', active: true },
          ] as item}
            {@const Comp = item.icon}
            <a href="/" class="flex flex-col items-center gap-1 py-2 rounded-lg transition-colors no-underline"
               style="color: {item.active ? 'var(--green)' : 'var(--w60)'};"
               onclick={(e) => e.preventDefault()}>
              <Comp size={20} />
              <span class="text-[11px]">{item.label}</span>
            </a>
          {/each}
        </div>
      </div>
    </div>
  </section>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- 10. MEDIA                                              -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section id="media" class="mb-24 scroll-mt-24">
    <div class="flex items-center gap-3 mb-8">
      <span class="text-xs font-mono px-2 py-1 rounded-md" style="background: var(--w5); color: var(--w30);">10</span>
      <h2 class="font-display text-[24px] tracking-wide">Media</h2>
    </div>

    <!-- Banner Component -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Banner Component</h3>
    <div class="relative h-48 md:h-64 rounded-2xl overflow-hidden bg-[--w5] mb-8">
      <!-- Gradient overlay -->
      <div class="absolute inset-0 bg-gradient-to-t from-dark-950/80 via-transparent to-dark-950/30" style="background: linear-gradient(to top, rgba(17,17,17,0.8), transparent 60%, rgba(17,17,17,0.3));"></div>
      <!-- Placeholder background -->
      <div class="absolute inset-0" style="background: linear-gradient(135deg, var(--w5), var(--w12));"></div>
      <!-- Title badge -->
      <div class="absolute left-4 bottom-4 z-10">
        <div class="inline-flex items-center justify-center gap-2 px-3 py-1.5 rounded-lg text-sm text-[--w60] bg-[--w8] backdrop-blur-[2px]">
          <Image size={18} />
          <span style="color: var(--w30);">Banner Slide Title</span>
        </div>
      </div>
      <!-- Dots -->
      <div class="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2 z-10">
        <span class="w-2 h-2 rounded-full" style="background: var(--w);"></span>
        <span class="w-2 h-2 rounded-full" style="background: var(--w30);"></span>
        <span class="w-2 h-2 rounded-full" style="background: var(--w30);"></span>
      </div>
      <!-- Arrows -->
      <div class="absolute right-4 bottom-4 flex gap-2 z-20">
        <button class="w-[36px] h-[36px] rounded-[10px] bg-[--w8] hover:bg-[--w12] flex items-center justify-center" style="color: var(--w60);">
          <ChevronLeft size={18} />
        </button>
        <button class="w-[36px] h-[36px] rounded-[10px] bg-[--w8] hover:bg-[--w12] flex items-center justify-center" style="color: var(--w60);">
          <ChevronRight size={18} />
        </button>
      </div>
    </div>

    <!-- Avatar Cropper -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Avatar Cropper</h3>
    <div class="card p-6 mb-8">
      <div class="flex items-center gap-6">
        <div class="relative w-32 h-32 rounded-full overflow-hidden flex items-center justify-center" style="background: var(--w8);">
          <Camera size={32} style="color: var(--w30);" />
          <div class="absolute inset-2 rounded-full border-2 border-dashed" style="border-color: var(--green); opacity: 0.4;"></div>
        </div>
        <div class="space-y-2 flex-1">
          <div class="text-sm text-[--w] font-medium">Crop Area Preview</div>
          <div class="text-xs" style="color: var(--w40);">Circle overlay with dashed green border indicating crop boundary</div>
          <div class="flex gap-2 mt-3">
            <button class="w-8 h-8 rounded-md flex items-center justify-center" style="background: var(--w5); color: var(--w60);"><ZoomIn size={16} /></button>
            <button class="w-8 h-8 rounded-md flex items-center justify-center" style="background: var(--w5); color: var(--w60);"><ZoomOut size={16} /></button>
            <button class="w-8 h-8 rounded-md flex items-center justify-center" style="background: var(--w5); color: var(--green)"><Check size={16} /></button>
            <button class="w-8 h-8 rounded-md flex items-center justify-center" style="background: var(--w5); color: var(--w60);"><X size={16} /></button>
          </div>
        </div>
      </div>
    </div>

    <!-- Image Lightbox (static preview) -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Image Lightbox</h3>
    <div class="card p-12 flex items-center justify-center relative" style="background: rgba(0,0,0,0.8);">
      <!-- Simulated lightbox stage -->
      <div class="relative">
        <div class="w-48 h-32 rounded-md flex items-center justify-center" style="background: var(--w8); box-shadow: 0 40px 100px rgba(0,0,0,0.7);">
          <Image size={32} style="color: var(--w30);" />
        </div>
        <div class="text-center mt-3">
          <div class="text-xs italic" style="color: rgba(255,255,255,0.4);">Image caption goes here</div>
        </div>
        <div class="absolute top-2 left-2 px-2 py-0.5 text-[10px] font-bold tracking-wider rounded-md" style="background: rgba(74,222,128,0.15); border: 1px solid rgba(74,222,128,0.3); color: #4ade80;">
          ORIGINAL
        </div>
      </div>
      <button class="absolute top-4 right-4 w-10 h-10 rounded-full flex items-center justify-center hover:bg-[rgba(255,255,255,0.15)]" style="background: rgba(255,255,255,0.07); color: rgba(255,255,255,0.65);">
        <X size={18} />
      </button>
      <div class="text-[11px] absolute bottom-3 left-1/2 -translate-x-1/2" style="color: var(--w30);">
        backdrop: 0.93 black + blur 14px / animation: 0.22s cubic-bezier pop
      </div>
    </div>
  </section>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- 11. OVERLAYS                                           -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section id="overlays" class="mb-24 scroll-mt-24">
    <div class="flex items-center gap-3 mb-8">
      <span class="text-xs font-mono px-2 py-1 rounded-md" style="background: var(--w5); color: var(--w30);">11</span>
      <h2 class="font-display text-[24px] tracking-wide">Overlays</h2>
    </div>

    <!-- MusicPlayer -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Music Player (Bottom Floating)</h3>
    <div class="card p-4 mb-8" style="background: rgba(10,10,10,0.92); border-color: rgba(255,255,255,0.06); box-shadow: 0 4px 24px rgba(0,0,0,0.5);">
      <div class="flex items-center gap-3">
        <!-- Drag handle -->
        <div class="flex items-center justify-center w-[30px] h-[30px] rounded-md cursor-grab" style="color: rgba(255,255,255,0.2);">
          <GripVertical size={16} />
        </div>
        <!-- Track info -->
        <div class="flex items-center gap-3" style="min-width: 190px;">
          <div class="w-[48px] h-[48px] rounded-[3px] flex items-center justify-center shrink-0" style="background: rgba(255,255,255,0.08);">
            <Music size={20} style="color: rgba(255,255,255,0.3);" />
          </div>
          <div>
            <div class="text-[14px] font-bold text-white">Track Title</div>
            <div class="text-[10px] text-white/40 uppercase tracking-[0.05em]">Album Name</div>
          </div>
        </div>
        <!-- Controls -->
        <div class="flex items-center gap-1 justify-center flex-1">
          <button class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/[0.06]" style="color: rgba(255,255,255,0.5);">
            <SkipBack size={16} />
          </button>
          <button class="w-10 h-10 flex items-center justify-center rounded-full hover:bg-white/[0.06]" style="background: rgba(255,255,255,0.1); color: white;">
            <Play size={18} />
          </button>
          <button class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/[0.06]" style="color: rgba(255,255,255,0.5);">
            <SkipForward size={16} />
          </button>
        </div>
        <!-- Time + Volume -->
        <div class="flex items-center gap-3" style="min-width: 190px; justify-content: flex-end;">
          <span class="text-[12px] text-white/50 font-mono tabular-nums">0:00 / 3:42</span>
          <div class="flex items-center gap-1.5">
            <Volume2 size={16} style="color: rgba(255,255,255,0.5);" />
            <div class="w-20 h-1 rounded-full overflow-hidden" style="background: rgba(255,255,255,0.1);">
              <div class="h-full rounded-full" style="width: 65%; background: linear-gradient(to right, #1e6fff, #0056d6);"></div>
            </div>
          </div>
          <button style="color: rgba(255,255,255,0.3);"><Repeat size={16} /></button>
        </div>
        <!-- Close -->
        <button class="w-[30px] h-[30px] flex items-center justify-center rounded-md hover:bg-[rgba(255,255,255,0.04)]" style="color: rgba(255,255,255,0.2);">
          <X size={14} />
        </button>
      </div>
      <!-- Progress bar -->
      <div class="relative w-full h-5 mt-1 cursor-pointer group">
        <div class="absolute bottom-0 left-0 right-0 h-[3px] group-hover:h-[5px] transition-all rounded-full" style="background: rgba(255,255,255,0.1);">
          <div class="h-full rounded-full" style="width: 35%; background: linear-gradient(to right, #1e6fff, #0056d6); position: relative;">
            <div class="absolute right-0 top-1/2 -translate-y-1/2 w-[13px] h-[13px] bg-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Markdown Editor -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Markdown Editor</h3>
    <div class="card mb-8" style="border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden; background: #121212;">
      <!-- Toolbar -->
      <div class="flex items-center px-3 py-2" style="background: #1a1a1a; border-bottom: 1px solid rgba(255,255,255,0.08);">
        <div class="flex items-center gap-0.5 flex-wrap">
          {#each [{l:'H1'},{l:'H2'},{l:'H3'}] as b}
            <button class="w-[30px] h-[30px] rounded-md flex items-center justify-center text-[13px] font-bold transition-colors hover:bg-[rgba(255,255,255,0.1)] hover:text-white"
                    style="color: rgba(255,255,255,0.55);">{b.l}</button>
          {/each}
          <div class="w-px h-5 mx-1" style="background: rgba(255,255,255,0.1);"></div>
          {#each [{l:'B', cls:'font-bold'},{l:'I', cls:'italic'}] as b}
            <button class="w-[30px] h-[30px] rounded-md flex items-center justify-center text-[13px] transition-colors hover:bg-[rgba(255,255,255,0.1)] hover:text-white {b.cls}"
                    style="color: rgba(255,255,255,0.55);">{b.l}</button>
          {/each}
          <div class="w-px h-5 mx-1" style="background: rgba(255,255,255,0.1);"></div>
          {#each [Quote, List, LinkIcon] as Icon}
            <button class="w-[30px] h-[30px] rounded-md flex items-center justify-center transition-colors hover:bg-[rgba(255,255,255,0.1)] hover:text-white"
                    style="color: rgba(255,255,255,0.55);">
              <Icon size={14} />
            </button>
          {/each}
        </div>
        <div class="flex-1"></div>
        <!-- Mode switcher -->
        <div class="flex rounded-md" style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);">
          {#each ['write', 'split', 'preview'] as mode}
            <button class="px-3 py-1 text-xs rounded-md transition-colors hover:text-white"
                    style="background: {demoSelected === mode ? 'rgba(255,255,255,0.1)' : 'transparent'}; color: {demoSelected === mode ? '#fff' : 'var(--w40)'};"
                    onclick={() => demoSelected = mode}>
              {mode}
            </button>
          {/each}
        </div>
      </div>
      <!-- Editor area -->
      <div class="flex" style="min-height: 160px;">
        <div class="flex-1 p-4" style="border-right: 1px solid rgba(255,255,255,0.08);">
          <textarea
            class="w-full h-full bg-transparent border-none text-[rgba(255,255,255,0.85)] font-mono text-sm leading-relaxed resize-none focus:outline-none"
            placeholder="Write markdown..."
            style="min-height: 140px;"
          ># Hello World

This is **bold** and *italic* text.</textarea>
        </div>
        <div class="flex-1 p-4 hidden md:block" style="background: #0f0f0f;">
          <div class="text-[18px] font-bold text-white mb-2">Hello World</div>
          <div class="text-sm text-[--w60]">This is <strong class="text-white">bold</strong> and <em>italic</em> text.</div>
        </div>
      </div>
      <!-- Footer -->
      <div class="px-3 py-1.5 text-[11px] flex justify-between items-center" style="background: #1a1a1a; color: rgba(255,255,255,0.25); border-top: 1px solid rgba(255,255,255,0.06);">
        <span>Markdown supported</span>
        <span>Ctrl+B · Ctrl+I · Ctrl+K</span>
      </div>
    </div>

    <!-- Volume popup -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Volume Popup (Player)</h3>
    <div class="card p-4 inline-block" style="background: rgba(12,12,12,0.96); backdrop-filter: blur(32px); border: 1px solid rgba(255,255,255,0.08);">
      <div class="w-8 h-32 relative flex flex-col items-center justify-center gap-2">
        <span class="text-[10px]" style="color: rgba(255,255,255,0.50);">100</span>
        <div class="flex-1 w-1.5 rounded-full overflow-hidden" style="background: rgba(255,255,255,0.1);">
          <div class="w-full rounded-full" style="height: 65%; background: linear-gradient(to top, #1e6fff, #0056d6);"></div>
        </div>
        <span class="text-[10px]" style="color: rgba(255,255,255,0.50);">0</span>
        <Volume2 size={14} style="color: rgba(255,255,255,0.50);" />
      </div>
    </div>
  </section>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- 12. DATA LISTS                                         -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section id="tables" class="mb-24 scroll-mt-24">
    <div class="flex items-center gap-3 mb-8">
      <span class="text-xs font-mono px-2 py-1 rounded-md" style="background: var(--w5); color: var(--w30);">12</span>
      <h2 class="font-display text-[24px] tracking-wide">Data Lists</h2>
    </div>

    <!-- Horizontal card list (blog/music) -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Horizontal List (Admin Pattern)</h3>
    <div class="space-y-2 mb-8">
      {#each [
        { title: 'Blog Post Title One', slug: '/blog/post-one', date: 'Apr 28, 2024', views: '1.2k' },
        { title: 'Another Post', slug: '/blog/another', date: 'Mar 12, 2024', views: '834' },
        { title: 'Featured Article', slug: '/blog/featured', date: 'Feb 5, 2024', views: '3.1k', featured: true },
      ] as item, i}
        <div class="card p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
          <div class="flex items-center gap-4">
            <div class="w-16 h-12 bg-[--w8] rounded-lg flex items-center justify-center shrink-0 overflow-hidden">
              <FileText size={18} style="color: var(--w30);" />
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h3 class="font-medium text-[--w]">{item.title}</h3>
                {#if item.featured}
                  <span class="px-2 py-0.5 text-[10px] font-bold bg-accent-green text-dark-950 rounded">FEATURED</span>
                {/if}
              </div>
              <p class="text-sm" style="color: var(--w60);">
                <span class="text-accent-green">{item.slug}</span>
                <span class="mx-1" style="color: var(--w30);">&middot;</span>
                {item.date}
                <span class="mx-1" style="color: var(--w30);">&middot;</span>
                <Eye size={12} class="inline" /> {item.views}
              </p>
            </div>
          </div>
          <div class="flex gap-2">
            <button class="btn btn-secondary text-xs px-3 py-1">Edit</button>
            <button class="btn btn-danger text-xs px-3 py-1">Delete</button>
          </div>
        </div>
      {/each}
    </div>

    <!-- Grid cards (arts pattern) -->
    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Grid Cards (Arts Admin)</h3>
    <div class="grid grid-cols-4 gap-3">
      {#each ['Artwork 1', 'Artwork 2', 'Artwork 3', 'Artwork 4'] as label, i}
        <div class="card p-2 group relative">
          <div class="aspect-square bg-[--w8] rounded-lg overflow-hidden mb-2 flex items-center justify-center">
            <Palette size={24} style="color: var(--w30);" />
          </div>
          <div class="text-sm truncate text-[--w]">{label}</div>
          <div class="text-xs" style="color: var(--w60);">2024</div>
          <div class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 flex flex-col gap-1 transition-opacity">
            <button class="p-1 bg-[--w8] rounded" style="color: var(--w60);"><Edit3 size={10} /></button>
            <button class="p-1 bg-accent-red/20 rounded" style="color: #ef4444;"><Trash2 size={10} /></button>
          </div>
        </div>
      {/each}
    </div>

    <!-- Admin form card -->
    <h3 class="text-xs font-semibold text-[--w80] mt-8 mb-3 uppercase tracking-wider">Admin Form Card</h3>
    <div class="card p-6">
      <h3 class="font-display text-lg mb-4">New Item</h3>
      <div class="space-y-5">
        <div>
          <div class="label">Title</div>
          <input type="text" class="input" placeholder="Enter title..." />
        </div>
        <div>
          <div class="label">Slug</div>
          <input type="text" class="input" placeholder="auto-generated-slug" />
          <span class="text-[11px] mt-1 block" style="color: var(--w30);">Auto-generated from title</span>
        </div>
        <div>
          <div class="label">Description</div>
          <textarea class="textarea" rows="3" placeholder="Enter description..."></textarea>
        </div>
        <div class="flex gap-2">
          <button class="btn btn-primary">Create</button>
          <button class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  </section>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- 13. EMPTY STATES                                       -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section id="empty-states" class="mb-24 scroll-mt-24">
    <div class="flex items-center gap-3 mb-8">
      <span class="text-xs font-mono px-2 py-1 rounded-md" style="background: var(--w5); color: var(--w30);">13</span>
      <h2 class="font-display text-[24px] tracking-wide">Empty States</h2>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <!-- Page-level -->
      <div class="card p-12 text-center flex flex-col items-center justify-center">
        <EyeOff size={48} class="mb-4" style="color: var(--w30);" />
        <div class="text-[--w] font-medium mb-1">Not Found</div>
        <div class="text-sm text-dark-400">Artwork not found</div>
      </div>
      <!-- Search -->
      <div class="card p-12 text-center flex flex-col items-center justify-center">
        <Search size={48} class="mb-4" style="color: var(--w30);" />
        <div class="text-[--w] font-medium mb-1">No Results</div>
        <div class="text-sm" style="color: var(--w40);">No results found for "query"</div>
      </div>
      <!-- Inline -->
      <div class="card p-12 text-center flex flex-col items-center justify-center">
        <MessageSquare size={48} class="mb-4" style="color: var(--w30);" />
        <div class="text-[--w] font-medium mb-1">No Data Yet</div>
        <div class="text-sm text-[--w30]">No users online right now</div>
      </div>
    </div>

    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Inline Empty States</h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
      <div class="card p-6">
        <div class="text-sm text-[--w30] italic text-center">Nothing to preview</div>
        <div class="text-[11px] mt-2 text-center" style="color: var(--w30);">MarkdownEditor empty preview</div>
      </div>
      <div class="card p-6">
        <div class="text-sm text-[--w30]">No tracks added yet.</div>
        <div class="text-[11px] mt-2" style="color: var(--w30);">Admin music track list (empty)</div>
      </div>
    </div>

    <div class="card p-6">
      <h4 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Empty State Pattern</h4>
      <div class="space-y-2 text-sm">
        <div class="flex items-start gap-3">
          <span class="text-[11px] font-mono w-32 shrink-0 mt-0.5" style="color: var(--w40);">Page-level</span>
          <div class="flex-1 space-y-1">
            <span class="text-[11px] px-1.5 py-0.5 rounded font-mono" style="background: var(--w5); color: var(--w40);">card</span>
            <span class="text-[11px] px-1.5 py-0.5 rounded font-mono" style="background: var(--w5); color: var(--w40);">p-12</span>
            <span class="text-[11px] px-1.5 py-0.5 rounded font-mono" style="background: var(--w5); color: var(--w40);">text-center</span>
            <span class="text-[11px] px-1.5 py-0.5 rounded font-mono" style="background: var(--w5); color: var(--w40);">text-dark-400</span>
          </div>
          <span class="text-xs" style="color: var(--w30);">Centered card with large icon and muted text</span>
        </div>
        <div class="flex items-start gap-3">
          <span class="text-[11px] font-mono w-32 shrink-0 mt-0.5" style="color: var(--w40);">Inline</span>
          <div class="flex-1 space-y-1">
            <span class="text-[11px] px-1.5 py-0.5 rounded font-mono" style="background: var(--w5); color: var(--w40);">text-sm</span>
            <span class="text-[11px] px-1.5 py-0.5 rounded font-mono" style="background: var(--w5); color: var(--w40);">text-[--w30]</span>
          </div>
          <span class="text-xs" style="color: var(--w30);">Simple muted text at 30% opacity</span>
        </div>
      </div>
    </div>
  </section>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- 14. COMPOSITION PATTERNS                               -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section id="compositions" class="mb-24 scroll-mt-24">
    <div class="flex items-center gap-3 mb-8">
      <span class="text-xs font-mono px-2 py-1 rounded-md" style="background: var(--w5); color: var(--w30);">14</span>
      <h2 class="font-display text-[24px] tracking-wide">Composition Patterns</h2>
    </div>

    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Page Layout Pattern</h3>
    <div class="card p-6 mb-8">
      <div class="flex flex-col md:flex-row gap-4">
        <!-- Simulated layout preview -->
        <div class="flex-1" style="background: var(--w5); border: 1px solid var(--w8); border-radius: 8px; padding: 16px;">
          <div style="height: 20px; width: 60%; background: var(--w12); border-radius: 4px; margin-bottom: 8px;"></div>
          <div style="height: 12px; width: 40%; background: var(--w5); border-radius: 3px; margin-bottom: 16px;"></div>
          <div class="grid grid-cols-2 gap-2">
            {#each [1,2,3,4] as _}
              <div style="height: 60px; background: var(--w8); border-radius: 6px;"></div>
            {/each}
          </div>
        </div>
        <div class="min-w-[180px] space-y-3">
          <div class="text-[11px] text-[--w80] font-medium mb-1">Anatomy</div>
          <div class="text-xs font-mono" style="color: var(--w40);">
            max-w-[828px] px-4 pc:px-0
          </div>
          <div class="text-xs font-mono" style="color: var(--w40);">
            mx-auto pt-[20px] pb-8
          </div>
          <div class="h-px my-3" style="background: var(--w8);"></div>
          <div class="text-[11px] text-[--w80] font-medium mb-1">Typical Flow</div>
          <div class="space-y-2 text-xs" style="color: var(--w60);">
            <div class="flex items-start gap-2">
              <span class="w-5 h-5 rounded bg-[--w8] flex items-center justify-center text-[10px] font-mono shrink-0">1</span>
              <span class="pt-0.5"><code class="text-[11px]" style="color: var(--w40);">font-display h1</code> page title</span>
            </div>
            <div class="flex items-start gap-2">
              <span class="w-5 h-5 rounded bg-[--w8] flex items-center justify-center text-[10px] font-mono shrink-0">2</span>
              <span class="pt-0.5"><code class="text-[11px]" style="color: var(--w40);">Breadcrumb</code> navigation</span>
            </div>
            <div class="flex items-start gap-2">
              <span class="w-5 h-5 rounded bg-[--w8] flex items-center justify-center text-[10px] font-mono shrink-0">3</span>
              <span class="pt-0.5"><code class="text-[11px]" style="color: var(--w40);">ViewingNow</code> if applicable</span>
            </div>
            <div class="flex items-start gap-2">
              <span class="w-5 h-5 rounded bg-[--w8] flex items-center justify-center text-[10px] font-mono shrink-0">4</span>
              <span class="pt-0.5"><code class="text-[11px]" style="color: var(--w40);">filter</code> chips / sort</span>
            </div>
            <div class="flex items-start gap-2">
              <span class="w-5 h-5 rounded bg-[--w8] flex items-center justify-center text-[10px] font-mono shrink-0">5</span>
              <span class="pt-0.5"><code class="text-[11px]" style="color: var(--w40);">grid</code> content cards</span>
            </div>
            <div class="flex items-start gap-2">
              <span class="w-5 h-5 rounded bg-[--w8] flex items-center justify-center text-[10px] font-mono shrink-0">6</span>
              <span class="pt-0.5"><code class="text-[11px]" style="color: var(--w40);">Pagination</code></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Card with Actions</h3>
    <div class="card p-4 mb-8">
      <div class="flex items-start justify-between gap-4 mb-3">
        <div>
          <h4 class="font-medium text-[--w]">Content Title</h4>
          <p class="text-sm" style="color: var(--w60);">Description text goes here</p>
        </div>
        <div class="flex gap-1 shrink-0">
          <button class="p-2 rounded-lg bg-[--w5] hover:bg-[--w8] text-[--w40] hover:text-[--w] transition-colors"><Eye size={16} /></button>
          <button class="p-2 rounded-lg bg-[--w5] hover:bg-[--w8] text-[--w40] hover:text-[--w] transition-colors"><Edit3 size={16} /></button>
          <button class="p-2 rounded-lg bg-[--w5] hover:bg-red-500/10 text-[--w40] hover:text-accent-red transition-colors"><Trash2 size={16} /></button>
        </div>
      </div>
      <div class="flex items-center gap-4 pt-3" style="border-top: 1px solid var(--w8);">
        <div class="flex items-center gap-1.5 text-xs" style="color: var(--w40);">
          <Calendar size={12} /> Apr 28, 2024
        </div>
        <div class="flex items-center gap-1.5 text-xs" style="color: var(--w40);">
          <Eye size={12} /> 1,234 views
        </div>
        <span class="text-[10px] font-medium px-2 py-0.5 rounded" style="background: rgba(115,238,7,0.08); color: var(--green); border: 1px solid rgba(115,238,7,0.15);">FEATURED</span>
      </div>
    </div>

    <h3 class="text-xs font-semibold text-[--w80] mb-3 uppercase tracking-wider">Admin Section Header + Action</h3>
    <div class="flex items-center justify-between mb-8">
      <div>
        <h3 class="font-display text-[20px] tracking-wide text-[--w]">Manage Posts</h3>
        <p class="text-sm" style="color: var(--w40);">3 items</p>
      </div>
      <button class="btn btn-primary flex items-center gap-1.5">
        <Plus size={16} /> Add New
      </button>
    </div>

    <h3 class="text-xs font-semibold text-[--w80] mt-8 mb-3 uppercase tracking-wider">Form with Upload</h3>
    <div class="card p-6">
      <div class="space-y-5">
        <div>
          <div class="label">Title</div>
          <input type="text" class="input" placeholder="Post title" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <div class="label">Category</div>
            <select class="input" style="cursor: pointer;">
              <option>Music</option>
              <option>Arts</option>
              <option>Blog</option>
            </select>
          </div>
          <div>
            <div class="label">Date</div>
            <input type="date" class="input" />
          </div>
        </div>
        <div>
          <div class="label">Cover Image</div>
          <div class="upload-zone cursor-pointer p-8 flex flex-col items-center justify-center text-center" style="border: 2px dashed #434343; border-radius: 0.5rem; transition: all 0.2s;">
            <Image size={32} style="color: var(--w30);" />
            <div class="text-sm mt-2" style="color: var(--w40);">Click or drag to upload</div>
          </div>
        </div>
        <div class="flex gap-2 pt-2">
          <button class="btn btn-primary">Save</button>
          <button class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  </section>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- 15. ICONS                                              -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section id="icons" class="mb-24 scroll-mt-24">
    <div class="flex items-center gap-3 mb-8">
      <span class="text-xs font-mono px-2 py-1 rounded-md" style="background: var(--w5); color: var(--w30);">15</span>
      <h2 class="font-display text-[24px] tracking-wide">Iconography</h2>
    </div>

    <div class="card p-6 mb-8">
      <p class="text-sm text-[--w60] mb-6">
        Project uses <code class="text-xs px-1.5 py-0.5 rounded font-mono" style="background: var(--w5); color: var(--w40);">lucide-svelte</code> for all icons. Stroke width varies per context: <code class="text-xs px-1.5 py-0.5 rounded font-mono" style="background: var(--w5); color: var(--w40);">1.5</code> for galleries, <code class="text-xs px-1.5 py-0.5 rounded font-mono" style="background: var(--w5); color: var(--w40);">2</code> default, <code class="text-xs px-1.5 py-0.5 rounded font-mono" style="background: var(--w5); color: var(--w40);">2.5</code> for compact buttons.
      </p>
      <div class="grid grid-cols-6 sm:grid-cols-8 md:grid-cols-10 gap-3">
        {#each commonIcons as iconItem}
          {@const Comp = iconItem.icon}
          <div class="flex flex-col items-center gap-2 group cursor-pointer">
            <div class="w-11 h-11 rounded-xl flex items-center justify-center transition-colors group-hover:bg-[--w8]" style="background: var(--w5);">
              <Comp size={20} strokeWidth={1.5} style="color: var(--w40);" class="group-hover:text-[--w] transition-colors" />
            </div>
            <span class="text-[9px] font-mono text-center leading-tight" style="color: var(--w30);">{iconItem.name}</span>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- 16. PRINCIPLES                                         -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section id="principles" class="mb-16 scroll-mt-24">
    <div class="flex items-center gap-3 mb-8">
      <span class="text-xs font-mono px-2 py-1 rounded-md" style="background: var(--w5); color: var(--w30);">16</span>
      <h2 class="font-display text-[24px] tracking-wide">Design Principles</h2>
    </div>

    <div class="space-y-4">
      {#each [
        {
          icon: Layers,
          color: 'var(--green)',
          title: '1. Dark-First Design',
          body: 'Every component is built for dark mode first. Light mode uses the same structure with inverted CSS variables. No separate component paths for themes -- one source of truth.',
        },
        {
          icon: Type,
          color: 'var(--purple)',
          title: '2. Bold Typography Hierarchy',
          body: 'DrukWideCyr dominates headers with tight letter-spacing. Golos body text carries readability at every weight. Size jumps are intentional -- 32/42px hero, 24px section, 20px card, 16px body.',
        },
        {
          icon: Palette,
          color: 'var(--blue)',
          title: '3. Surface Layering',
          body: 'All backgrounds derive from white-with-opacity (w5, w8, w12, w18). This creates natural visual hierarchy that adapts to both themes. Never use arbitrary colors where a surface token will do.',
        },
        {
          icon: Zap,
          color: 'var(--green)',
          title: '4. Green Guides the Eye',
          body: '--green / accent-green is the ONLY color used for primary CTAs and success states. It immediately draws attention. Purple and blue provide subtle secondary accents.',
        },
        {
          icon: Sparkles,
          color: 'var(--purple)',
          title: '5. Motion is Micro &amp; Purposeful',
          body: 'All transitions are 0.15s-0.25s ease. Hover scales are 1.02x (buttons) and 1.05x (images). Cards change background, not border. Active states press down (0.98x). Nothing moves without user input.',
        },
        {
          icon: Globe,
          color: 'var(--blue)',
          title: '6. Content-First Layout',
          body: 'Max-width 828px keeps lines readable. Cards fill the width. Grids are 2-4 columns with consistent gaps. Admin uses same container, different density. Mobile collapses gracefully with the bottom nav.',
        },
        {
          icon: Shield,
          color: 'var(--green)',
          title: '7. Consistent Component Contracts',
          body: 'Every component has one clear pattern: Button (href OR onclick), Card (bg+w5 + border+w8), Input (bg+w8 + border+w12 + focus ring), Badge (pill + w8 bg). No exceptions in the wild.',
        },
        {
          icon: Heart,
          color: 'var(--purple)',
          title: '8. Personality in the Details',
          body: 'Smart date colors (green for fresh, cyan for recent). HSL-based avatar colors from usernames. Gradient text. Pulse live indicators. The glow on THEF[O]XXSTUFF. These make the interface feel alive.',
        },
      ] as principle}
        {@const Comp = principle.icon}
        <div class="card p-6 flex gap-4 items-start" style="background: linear-gradient(135deg, var(--w8), var(--w5));">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0" style="background: rgba(115,238,7,0.06);">
            <Comp size={18} style="color: {principle.color};" />
          </div>
          <div>
            <h4 class="text-sm font-semibold text-[--w] mb-1">{principle.title}</h4>
            <p class="text-[14px] leading-relaxed" style="color: var(--w60);">{principle.body}</p>
          </div>
        </div>
      {/each}
    </div>

    <!-- File structure reference -->
    <h3 class="text-xs font-semibold text-[--w80] mt-12 mb-3 uppercase tracking-wider">File Structure Reference</h3>
    <div class="card p-6 overflow-x-auto">
      <pre class="text-xs leading-relaxed font-mono" style="color: var(--w60);"><code class="lang-text">frontend/
  src/
    app.css                  # @layer components, CSS vars, font-face
    app.html                 # &lt;!DOCTYPE html&gt;, Inter CDN
    lib/
      components/
        index.js             # Re-exports all components
        Button.svelte        # Icon-capable &lt;Button&gt; (href OR onclick)
        Badge.svelte         # Legacy date badge
        BlogCard.svelte      # 16:10 card with smart date colors
        ArtCard.svelte       # Square aspect ratio
        MusicCard.svelte     # Cover + title
        HeroSection.svelte   # Featured release hero
        OnlineUsers.svelte   # Avatar stack (compact/full modes)
        ViewingNow.svelte    # Ping + avatars + count
        ImageLightbox.svelte # Backdrop blur + zoom
        AvatarCropper.svelte # Circle crop with green border
        MarkdownEditor.svelte # Toolbar + write/split/preview modes
        ImageUpload.svelte   # Dashed-border single upload
        MultiImageUpload.svelte # Grid upload with reorder
        Header.svelte        # Desktop nav + search + user menu
        MobileHeader.svelte  # Bottom nav with slide-up panel
        Footer.svelte        # Copyright + Telegram + ThemeToggle
        MusicPlayer.svelte   # Fixed floating player
        Banner.svelte        # Carousel with gradient overlay
        Pagination.svelte    # Rounded page buttons + ellipsis
        Breadcrumb.svelte    # Home + ChevronRight chain
      stores/
        theme.js             # writable store + localStorage
        auth.js              # token + user with login/logout
        player.js            # music playback state
      api.js                 # API_BASE, getImageUrl, helpers
    routes/
      +layout.svelte         # Wraps Header/Footer/main
      /design/+page.svelte   # Design System v1.0
      /design2/+page.svelte  # Design System v2.0 (this page)</code></pre>
    </div>
  </section>

  <!-- ════════════ FOOTER ════════════ -->
  <footer class="py-12 border-t" style="border-color: var(--w8);">
    <div class="flex items-center justify-between flex-wrap gap-4">
      <div>
        <span class="text-sm font-medium text-[--w]">TheFoxxStuff</span>
        <span class="text-sm mx-2" style="color: var(--w30);">&middot;</span>
        <span class="text-sm" style="color: var(--w40);">Design System v2.0</span>
      </div>
      <div class="flex items-center gap-4">
        <a href="/design" class="text-xs no-underline px-3 py-1.5 rounded-full transition-colors hover:text-[--w] hover:bg-[--w8]" style="background: var(--w5); color: var(--w40);">
          Version 1.0
        </a>
        <button class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors hover:text-[--w] hover:bg-[--w12]" style="background: var(--w8); color: var(--w60);" type="button" onclick={() => $theme = $theme === 'dark' ? 'light' : 'dark'}>
          {#if $theme === 'dark'}<Sun size={14} />{:else}<Moon size={14} />{/if}
          <span class="text-xs">{ $theme === 'dark' ? 'Dark' : 'Light' }</span>
        </button>
      </div>
    </div>
  </footer>
</div>

<style>
  /* Upload zone styling */
  .upload-zone {
    border: 2px dashed #434343;
    border-radius: 0.5rem;
    transition: all 0.2s;
  }
  .upload-zone:hover,
  .upload-zone.drag-over {
    border-color: rgba(74, 222, 128, 0.5);
    background: rgba(56, 56, 56, 0.5);
  }

  ::selection {
    background-color: rgba(136, 255, 0, 0.12);
    color: #88ff00;
    text-shadow: none;
  }

  code {
    font-family: 'SF Mono', 'Fira Code', menlo, monospace;
    font-size: 0.85em;
  }

  [style*="scrollbar-width: none"] {
    -ms-overflow-style: none;
  }
  [style*="scrollbar-width: none"]::-webkit-scrollbar {
    display: none;
  }
</style>
