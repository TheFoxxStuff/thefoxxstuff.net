<script>
  import { SEO } from '$lib/components';
  import {
    Music,
    FileText,
    Palette,
    Users,
    Image,
    Eye,
    ArrowUpRight,
    LayoutDashboard,
    Zap,
    Link as LinkIcon,
    Home,
    ChevronRight,
    ChevronLeft,
    Sun,
    Moon,
    Search,
    Shield,
    Send,
    Download,
    Copy,
    X,
    Check,
    Menu,
    ExternalLink,
    Camera,
    Heart,
    Star,
    Play,
    Trash2,
    Settings,
    User,
    Mail,
    MapPin,
    Calendar,
    Info,
  } from 'lucide-svelte';
  import { theme } from '$lib/stores/theme.js';
  import { browser } from '$app/environment';

  const sections = [
    { id: 'colors', label: 'Colors' },
    { id: 'typography', label: 'Typography' },
    { id: 'buttons', label: 'Buttons' },
    { id: 'cards', label: 'Cards' },
    { id: 'forms', label: 'Forms' },
    { id: 'badges', label: 'Badges & Tags' },
    { id: 'navigation', label: 'Navigation' },
    { id: 'avatars', label: 'Avatars' },
    { id: 'spacing', label: 'Spacing' },
    { id: 'animations', label: 'Animations' },
    { id: 'icons', label: 'Icons' },
  ];

  const commonIcons = [
    { name: 'Home', icon: Home },
    { name: 'Music', icon: Music },
    { name: 'FileText', icon: FileText },
    { name: 'Palette', icon: Palette },
    { name: 'Users', icon: Users },
    { name: 'Image', icon: Image },
    { name: 'Eye', icon: Eye },
    { name: 'ArrowUpRight', icon: ArrowUpRight },
    { name: 'LayoutDashboard', icon: LayoutDashboard },
    { name: 'Zap', icon: Zap },
    { name: 'Link', icon: LinkIcon },
    { name: 'ChevronRight', icon: ChevronRight },
    { name: 'Search', icon: Search },
    { name: 'Shield', icon: Shield },
    { name: 'Send', icon: Send },
    { name: 'Heart', icon: Heart },
    { name: 'Star', icon: Star },
    { name: 'Play', icon: Play },
    { name: 'Download', icon: Download },
    { name: 'ExternalLink', icon: ExternalLink },
    { name: 'Calendar', icon: Calendar },
    { name: 'Sun', icon: Sun },
    { name: 'Moon', icon: Moon },
    { name: 'Settings', icon: Settings },
    { name: 'Trash2', icon: Trash2 },
    { name: 'Check', icon: Check },
    { name: 'X', icon: X },
    { name: 'Menu', icon: Menu },
    { name: 'User', icon: User },
    { name: 'Camera', icon: Camera },
    { name: 'Mail', icon: Mail },
    { name: 'MapPin', icon: MapPin },
    { name: 'Info', icon: Info },
  ];

  const fontWeights = [100, 200, 300, 400, 500, 600, 700, 800, 900];

  function hue(name = '') {
    let h = 0;
    for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) % 360;
    return h;
  }

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
  title="Design System | TheFoxxStuff"
  description="Visual design system and component library for TheFoxxStuff."
/>

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0">
  <!-- ════════════ HERO ════════════ -->
  <div class="mb-16">
    <h1 class="font-display text-[32px] min-[829px]:text-[42px] tracking-wide text-[--w]">
      Design System
    </h1>
    <p class="text-[--w60] text-[17px] mt-2 max-w-xl">
      TheFoxxStuff &mdash; visual design system and component library.
      A living reference for developers and designers.
    </p>
  </div>

  <!-- ════════════ SECTION NAV ════════════ -->
  <nav class="card p-4 mb-12 sticky top-[60px] z-30" style="background: var(--header);">
    <div class="flex flex-wrap gap-2">
      {#each sections as section}
        <a
          href="#{section.id}"
          class="text-xs font-medium px-3 py-1.5 rounded-full transition-colors no-underline hover:text-[--w] hover:bg-[--w12]"
          style="color: var(--w60); background: var(--w8);"
        >
          {section.label}
        </a>
      {/each}
    </div>
  </nav>

  <!-- ════════════════════════════════════════════ -->
  <!-- 1. COLORS                                    -->
  <!-- ════════════════════════════════════════════ -->
  <section id="colors" class="mb-20">
    <h2 class="font-display text-[24px] tracking-wide mb-6">1. Colors</h2>

    <!-- Brand -->
    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Brand</h3>
    <div class="grid grid-cols-3 gap-4 mb-8">
      {#each [
        { var: '--green', hex: '#73EE07', hexLight: '#4dbd00' },
        { var: '--purple', hex: '#6D07EE', hexLight: '#5b05c7' },
        { var: '--blue', hex: '#47ADFF', hexLight: '#2563eb' },
      ] as color}
        <div class="rounded-xl overflow-hidden card">
          <div class="h-32" style="background: var({color.var});">
          </div>
          <div class="p-3">
            <div class="text-sm font-mono text-[--w]">{color.var}</div>
            <div class="text-xs mt-1" style="color: var(--w40);">
              Dark: {color.hex}
            </div>
            <div class="text-xs" style="color: var(--w40);">
              Light: {color.hexLight}
            </div>
          </div>
        </div>
      {/each}
    </div>

    <!-- Accent -->
    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Accent</h3>
    <div class="grid grid-cols-3 gap-4 mb-8">
      {#each [
        { name: 'accent-green', hex: '#4ade80' },
        { name: 'accent-cyan', hex: '#22d3ee' },
        { name: 'accent-red', hex: '#ef4444' },
      ] as color}
        <div class="rounded-xl overflow-hidden card">
          <div class="h-24" style="background: {color.hex};"></div>
          <div class="p-3">
            <div class="text-sm font-mono text-[--w]">{color.name}</div>
            <div class="text-xs mt-1" style="color: var(--w40);">{color.hex}</div>
          </div>
        </div>
      {/each}
    </div>

    <!-- Text Hierarchy -->
    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Text Hierarchy</h3>
    <div class="card p-6 space-y-4 mb-8">
      {#each [
        { var: '--w', pct: '100%', label: 'Primary' },
        { var: '--w80', pct: '80%', label: 'Secondary' },
        { var: '--w60', pct: '60%', label: 'Tertiary' },
        { var: '--w40', pct: '40%', label: 'Placeholder' },
        { var: '--w30', pct: '30%', label: 'Disabled / Hint' },
      ] as t}
        <div class="flex items-center justify-between">
          <span class="text-[16px]" style="color: var({t.var});">{t.label} &mdash; The quick brown fox ({t.pct})</span>
          <span class="text-xs font-mono shrink-0 ml-4" style="color: var(--w40);">var({t.var})</span>
        </div>
      {/each}
    </div>

    <!-- Surface Hierarchy -->
    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Surface</h3>
    <div class="grid grid-cols-4 gap-4 mb-8">
      {#each [
        { var: '--w5', label: 'w5' },
        { var: '--w8', label: 'w8' },
        { var: '--w12', label: 'w12' },
        { var: '--w18', label: 'w18' },
      ] as s}
        <div class="rounded-xl overflow-hidden card p-4">
          <div class="h-12 rounded-lg mb-3" style="background: var({s.var}); border: 1px solid var(--w8);"></div>
          <div class="text-xs font-mono" style="color: var(--w60);">var({s.var})</div>
        </div>
      {/each}
    </div>

    <!-- Selection Preview -->
    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Selection</h3>
    <div class="card p-6">
      <p class="text-[15px]" style="color: var(--w60);">
        Select this text to see the custom selection style: lime-green background with bright green text.
        Defined via <code class="text-xs bg-[--w8] px-1.5 py-0.5 rounded">::selection</code> in <code class="text-xs bg-[--w8] px-1.5 py-0.5 rounded">app.css</code>.
      </p>
    </div>
  </section>

  <!-- ════════════════════════════════════════════ -->
  <!-- 2. TYPOGRAPHY                                -->
  <!-- ════════════════════════════════════════════ -->
  <section id="typography" class="mb-20">
    <h2 class="font-display text-[24px] tracking-wide mb-6">2. Typography</h2>

    <!-- Font Families -->
    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Font Families</h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
      <div class="card p-6">
        <div class="text-xs font-mono mb-3" style="color: var(--w40);">font-display: 'DrukWideCyr', sans-serif</div>
        <div class="font-display text-[24px] tracking-wide">Съешь ещё этих мягких французских булок</div>
        <div class="text-xs mt-3" style="color: var(--w40);">Display font &mdash; headings, hero sections</div>
      </div>
      <div class="card p-6">
        <div class="text-xs font-mono mb-3" style="color: var(--w40);">body: 'Golos-Regular', system-ui, sans-serif</div>
        <div class="text-[16px] leading-relaxed">Съешь ещё этих мягких французских булок, да выпей чаю.</div>
        <div class="text-xs mt-3" style="color: var(--w40);">Body font &mdash; all regular text, variable weight 100&ndash;900</div>
      </div>
    </div>

    <!-- Type Scale -->
    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Type Scale</h3>
    <div class="card p-6 space-y-5 mb-8">
      <div>
        <div class="text-xs font-mono mb-1" style="color: var(--w40);">h1 &mdash; 32px / 42px (desktop) &middot; font-display</div>
        <h1 class="font-display text-[32px] min-[829px]:text-[42px] tracking-wide text-[--w]">Page Heading</h1>
      </div>
      <div>
        <div class="text-xs font-mono mb-1" style="color: var(--w40);">h2 &mdash; 24px &middot; font-display</div>
        <h2 class="font-display text-[24px] tracking-wide text-[--w]">Section Title</h2>
      </div>
      <div>
        <div class="text-xs font-mono mb-1" style="color: var(--w40);">text-lg &mdash; 18px</div>
        <p class="text-[18px] text-[--w80]">Large body text for emphasis</p>
      </div>
      <div>
        <div class="text-xs font-mono mb-1" style="color: var(--w40);">text-base &mdash; 16px</div>
        <p class="text-[16px] text-[--w60]">Default body text, standard paragraph size</p>
      </div>
      <div>
        <div class="text-xs font-mono mb-1" style="color: var(--w40);">text-sm &mdash; 14px</div>
        <p class="text-[14px] text-[--w60]">Small text for captions and metadata</p>
      </div>
      <div>
        <div class="text-xs font-mono mb-1" style="color: var(--w40);">text-xs &mdash; 12px</div>
        <p class="text-[12px] text-[--w40]">Extra small text for hints and labels</p>
      </div>
    </div>

    <!-- Font Weight -->
    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Font Weight (Golos Variable)</h3>
    <div class="card p-6 space-y-2 mb-8">
      {#each fontWeights as weight}
        <div class="flex items-baseline gap-4">
          <span class="text-xs font-mono w-12 shrink-0" style="color: var(--w30);">{weight}</span>
          <span style="font-weight: {weight};">The quick brown fox &mdash; Weight {weight}</span>
        </div>
      {/each}
    </div>

    <!-- Text Gradient -->
    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Text Variants</h3>
    <div class="card p-6 space-y-4">
      <div>
        <div class="text-xs font-mono mb-1" style="color: var(--w40);">.text-gradient</div>
        <p class="text-[24px] font-bold text-gradient">Gradient Text from green to cyan</p>
      </div>
    </div>
  </section>

  <!-- ════════════════════════════════════════════ -->
  <!-- 3. BUTTONS                                   -->
  <!-- ════════════════════════════════════════════ -->
  <section id="buttons" class="mb-20">
    <h2 class="font-display text-[24px] tracking-wide mb-6">3. Buttons</h2>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Tailwind Component Classes</h3>
    <div class="card p-6 space-y-6 mb-8">
      <div>
        <div class="text-xs font-mono mb-2" style="color: var(--w40);">.btn-primary</div>
        <div class="flex flex-wrap gap-3 items-center">
          <button class="btn btn-primary">Primary Button</button>
          <button class="btn btn-primary" disabled>Disabled</button>
        </div>
      </div>
      <div>
        <div class="text-xs font-mono mb-2" style="color: var(--w40);">.btn-secondary</div>
        <div class="flex flex-wrap gap-3 items-center">
          <button class="btn btn-secondary">Secondary Button</button>
          <button class="btn btn-secondary" disabled>Disabled</button>
        </div>
      </div>
      <div>
        <div class="text-xs font-mono mb-2" style="color: var(--w40);">.btn-danger</div>
        <div class="flex flex-wrap gap-3 items-center">
          <button class="btn btn-danger">Delete</button>
          <button class="btn btn-danger" disabled>Disabled</button>
        </div>
      </div>
      <div>
        <div class="text-xs font-mono mb-2" style="color: var(--w40);">.btn-breadcrumb</div>
        <div class="flex flex-wrap gap-2 items-center">
          <button class="btn-breadcrumb">Breadcrumb Item</button>
          <button class="btn-breadcrumb" disabled>Disabled</button>
        </div>
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Button Component (with icons)</h3>
    <div class="card p-6 space-y-6 mb-8">
      <div>
        <div class="text-xs font-mono mb-2" style="color: var(--w40);">&lt;Button iconRight={ChevronRight}&gt;</div>
        <div class="flex flex-wrap gap-3">
          <button class="inline-flex items-center justify-center gap-[4px] px-[12px] py-[6px] bg-[--w5] hover:bg-[--w8] text-[#999] hover:text-[--w] rounded-[8px] transition-all duration-160 group no-underline">
            <span class="text-[14px] font-medium tracking-wide">Show More</span>
            <span class="flex items-center group-hover:text-[--w] transition-colors"><ChevronRight size={16} strokeWidth={2.5} /></span>
          </button>
          <button class="inline-flex items-center justify-center gap-[4px] px-[12px] py-[6px] bg-[--w5] hover:bg-[--w8] text-[#999] hover:text-[--w] rounded-[8px] transition-all duration-160 group no-underline">
            <span class="flex items-center group-hover:opacity-80 transition-opacity"><Music size={16} strokeWidth={2.5} /></span>
            <span class="text-[14px] font-medium tracking-wide">Music</span>
          </button>
          <button class="inline-flex items-center justify-center gap-[4px] px-[12px] py-[6px] bg-[--w5] hover:bg-[--w8] text-[#999] hover:text-[--w] rounded-[8px] transition-all duration-160 group no-underline">
            <span class="flex items-center group-hover:opacity-80 transition-opacity"><Download size={16} strokeWidth={2.5} /></span>
            <span class="text-[14px] font-medium tracking-wide">Download</span>
            <span class="flex items-center group-hover:text-[--w] transition-colors"><ArrowUpRight size={16} strokeWidth={2.5} /></span>
          </button>
        </div>
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">.filter variant</h3>
    <div class="card p-6">
      <div class="flex flex-wrap gap-2">
        <button class="filter">All</button>
        <button class="filter">Music</button>
        <button class="filter">Arts</button>
        <button class="filter">Blog</button>
        <button class="filter" disabled>Disabled</button>
      </div>
    </div>
  </section>

  <!-- ════════════════════════════════════════════ -->
  <!-- 4. CARDS                                     -->
  <!-- ════════════════════════════════════════════ -->
  <section id="cards" class="mb-20">
    <h2 class="font-display text-[24px] tracking-wide mb-6">4. Cards</h2>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Standard Card</h3>
    <div class="grid grid-cols-2 gap-4 mb-8">
      <div class="card p-6">
        <div class="text-sm font-semibold text-[--w] mb-1">.card</div>
        <p class="text-xs" style="color: var(--w60);">background: var(--w5); border: 1px solid var(--w8); border-radius: 0.75rem; overflow: hidden</p>
      </div>
      <div class="card p-6 card-hover cursor-pointer">
        <div class="text-sm font-semibold text-[--w] mb-1">.card-hover</div>
        <p class="text-xs" style="color: var(--w60);">Interactive card &mdash; hover to see background change</p>
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Image Cards</h3>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <!-- BlogCard 16:10 -->
      <div class="col-span-2">
        <div class="card rounded-[12px] overflow-hidden card-hover cursor-pointer" style="aspect-ratio: 16 / 10;">
          <div class="w-full h-full flex items-end p-4" style="background: linear-gradient(135deg, var(--w8), var(--w12));">
            <div>
              <div class="text-[13px] text-[--w30] flex items-center gap-2 mb-1">
                <Calendar size={14} /> Apr 28, 2024
              </div>
              <div class="text-[15px] text-[--w] font-medium">Blog Card &mdash; 16:10 aspect</div>
            </div>
          </div>
        </div>
      </div>
      <!-- ArtCard square -->
      <div class="card rounded-xl overflow-hidden card-hover cursor-pointer" style="aspect-ratio: 1;">
        <div class="w-full h-full flex items-center justify-center" style="background: var(--w8);">
          <div class="text-center">
            <Palette size={28} style="color: var(--w30);" />
            <div class="text-xs mt-2" style="color: var(--w30);">Art Card &mdash; 1:1</div>
          </div>
        </div>
      </div>
      <!-- MusicCard pattern -->
      <div class="card rounded-[8px] p-[18px] card-hover cursor-pointer">
        <div class="w-full h-16 rounded-[8px] mb-3 flex items-center justify-center" style="background: var(--w8);">
          <Music size={24} style="color: var(--w30);" />
        </div>
        <div class="text-[14px] text-[--w] font-medium truncate">Music Card</div>
        <div class="text-[12px] mt-0.5" style="color: var(--w30);">Artist Name</div>
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Featured Release Pattern</h3>
    <div class="relative rounded-[12px] overflow-hidden bg-[--w5] border border-[--w8] p-6 md:p-10">
      <div class="absolute inset-0 bg-gradient-to-br from-[rgba(115,238,7,0.05)] via-transparent to-[rgba(71,173,255,0.05)] pointer-events-none"></div>
      <div class="relative">
        <div class="flex items-center gap-2 mb-3">
          <span class="inline-block w-2 h-2 rounded-full bg-[--green] animate-pulse"></span>
          <span class="text-[12px] text-[--green] font-medium tracking-widest uppercase">Musician &middot; Artist &middot; Blogger</span>
        </div>
        <div class="font-display text-[24px] md:text-[36px] tracking-wide text-[--w] leading-tight mb-3">
          THEF<span class="text-[--green]">O</span>XXSTUFF
        </div>
        <p class="text-[--w60] text-[15px] leading-relaxed max-w-md mb-4">
          Making music in the dark, painting strange worlds, writing about all of it.
        </p>
        <div class="flex flex-wrap gap-3">
          <button class="inline-flex items-center gap-2 px-5 py-2.5 bg-[--green] text-[--b] rounded-[8px] text-[14px] font-bold hover:opacity-90 transition-all hover:scale-[1.02] active:scale-[0.98]">
            <Play size={16} /> Play Latest Release
          </button>
          <a href="/about" class="inline-flex items-center gap-2 px-5 py-2.5 bg-[--w8] text-[--w] rounded-[8px] text-[14px] font-medium hover:bg-[--w12] transition-all no-underline">
            About me &rarr;
          </a>
        </div>
      </div>
    </div>
  </section>

  <!-- ════════════════════════════════════════════ -->
  <!-- 5. FORM CONTROLS                             -->
  <!-- ════════════════════════════════════════════ -->
  <section id="forms" class="mb-20">
    <h2 class="font-display text-[24px] tracking-wide mb-6">5. Form Controls</h2>

    <div class="card p-6 space-y-6 mb-8">
      <div>
        <label class="label">Email Address</label>
        <input type="email" class="input" placeholder="you@example.com" />
      </div>
      <div>
        <label class="label">Focus State</label>
        <input type="text" class="input" placeholder="Click to see green ring" />
        <p class="text-xs mt-1" style="color: var(--w40);">
          focus: ring-1, ring-accent-green/50
        </p>
      </div>
      <div>
        <label class="label">Message</label>
        <textarea class="textarea" rows="3" placeholder="Write something..."></textarea>
      </div>
      <div>
        <label class="label">Disabled</label>
        <input type="text" class="input" value="Cannot edit this" disabled />
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">CSS Variables</h3>
    <div class="card p-6 grid grid-cols-2 gap-x-8 gap-y-2">
      {#each [
        { var: '.input', props: 'background: var(--w8), border: 1px solid var(--w12), focus: green ring' },
        { var: '.textarea', props: 'same as input + resize-none, more padding' },
        { var: '.label', props: 'color: var(--w60), text-sm, font-medium, mb-1' },
      ] as item}
        <div class="text-xs font-mono mb-0.5" style="color: var(--w60);">{item.var}</div>
        <div class="text-xs" style="color: var(--w40);">{item.props}</div>
      {/each}
    </div>
  </section>

  <!-- ════════════════════════════════════════════ -->
  <!-- 6. BADGES, TAGS & PILLS                     -->
  <!-- ════════════════════════════════════════════ -->
  <section id="badges" class="mb-20">
    <h2 class="font-display text-[24px] tracking-wide mb-6">6. Badges, Tags & Pills</h2>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">.badge (pill badge)</h3>
    <div class="card p-6 space-y-4 mb-8">
      <div class="flex flex-wrap gap-3">
        <span class="badge">Default Badge</span>
        <span class="badge">With Icon &middot; 2024</span>
        <span class="badge"><Eye size={12} /> 1.2k views</span>
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">.tag & .tag-active</h3>
    <div class="card p-6 space-y-4 mb-8">
      <div class="flex flex-wrap gap-2">
        <span class="tag">All</span>
        <span class="tag-active tag">Music</span>
        <span class="tag">Arts</span>
        <span class="tag">Blog</span>
        <span class="tag">Links</span>
        <span class="tag">Hover me</span>
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Role &amp; Status</h3>
    <div class="card p-6 space-y-4 mb-8">
      <div class="flex flex-wrap items-center gap-3">
        <!-- Admin badge -->
        <span class="text-[10px] font-medium tracking-wide px-2 py-0.5 rounded" style="color: hsla(142, 76%, 36%, 0.6); background: hsla(142, 76%, 36%, 0.08); border: 1px solid hsla(142, 76%, 36%, 0.18);">
          ADMIN
        </span>
        <!-- Online dot -->
        <span class="flex items-center gap-2 text-sm" style="color: var(--w40);">
          <span class="w-2 h-2 rounded-full bg-accent-green animate-pulse inline-block"></span>
          Online
        </span>
        <!-- Ping style -->
        <span class="flex items-center gap-2 text-xs" style="color: var(--w30);">
          <span class="w-1.5 h-1.5 rounded-full bg-accent-green inline-block"></span>
          12 online
        </span>
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Number Badge</h3>
    <div class="card p-6">
      <div class="flex flex-wrap gap-3 items-center">
        <span class="inline-flex items-center justify-center w-[36px] h-[36px] rounded-[8px] text-sm font-medium" style="background: var(--w5); color: var(--w60);">1</span>
        <span class="inline-flex items-center justify-center w-[36px] h-[36px] rounded-[8px] text-sm font-medium" style="background: var(--w8); color: var(--w);">2</span>
        <span class="inline-flex items-center justify-center w-[36px] h-[36px] rounded-[8px] text-sm font-medium" style="background: var(--w12); color: var(--w);">3</span>
        <span class="inline-flex items-center justify-center w-[36px] h-[36px] rounded-[8px] text-sm font-bold" style="background: var(--w18); color: var(--w);">28</span>
        <span class="inline-flex items-center justify-center min-w-[36px] h-[36px] px-3 rounded-[8px] text-xs font-bold" style="background: var(--blue); color: white;">99+</span>
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Legacy Badge Component</h3>
    <div class="card p-6">
      <div class="flex items-center gap-[6px] px-[8px] py-[4px] bg-[rgba(255,255,255,0.05)] rounded-[5px] text-[rgba(255,255,255,0.6)] w-fit h-[26px]">
        <span class="text-[14px] leading-none whitespace-nowrap">28 April, 2024</span>
      </div>
    </div>
  </section>

  <!-- ════════════════════════════════════════════ -->
  <!-- 7. NAVIGATION & LAYOUT                      -->
  <!-- ════════════════════════════════════════════ -->
  <section id="navigation" class="mb-20">
    <h2 class="font-display text-[24px] tracking-wide mb-6">7. Navigation & Layout</h2>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Admin Navigation Pattern</h3>
    <div class="card mb-8 overflow-hidden" style="background: rgba(6,6,6,0.88); backdrop-filter: blur(14px);">
      <div class="flex items-center gap-3 px-4 py-2" style="height: 50px;">
        <a href="/" class="text-sm no-underline hover:text-[--w]" style="color: var(--w60);"><span class="font-display text-[10px] tracking-wider" style="color: var(--green);">ADMIN</span></a>
        <div class="flex gap-1 h-[30px] text-[13px] overflow-x-auto flex-1 scrollbar-hide">
          {#each [
            { href: '/admin', label: 'Dashboard' },
            { href: '/admin/banner', label: 'Banner' },
            { href: '/admin/music', label: 'Music' },
            { href: '/admin/blog', label: 'Blog' },
            { href: '/admin/arts', label: 'Arts' },
            { href: '/admin/links', label: 'Links' },
            { href: '/admin/users', label: 'Users' },
            { href: '/admin/media', label: 'Media' },
          ] as item, i}
            <a
              href={item.href}
              class="flex items-center gap-2 px-3 rounded-md no-underline shrink-0 h-full transition-colors hover:text-[--w]"
              style="color: var(--w60); {i === 0 ? 'background: var(--w8); color: var(--w);' : ''}"
            >
              {item.label}
            </a>
          {/each}
        </div>
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Breadcrumb</h3>
    <div class="card p-4 mb-8">
      <div class="flex items-center gap-[4px] text-sm" style="color: var(--w60);">
        <Home size={14} />
        <span>/</span>
        <span>Blog</span>
        <ChevronRight size={14} />
        <span style="color: var(--w);">Article Title</span>
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Pagination</h3>
    <div class="card p-4 mb-8">
      <div class="flex items-center gap-2">
        <button class="w-[36px] h-[36px] rounded-[8px] flex items-center justify-center hover:bg-[--w8] hover:text-[--w] transition-colors" style="background: var(--w5); color: var(--w60);">
          <ChevronLeft size={16} />
        </button>
        {#each [1, 2, 3, '...', 12, 13, 14, 15, '...', 21] as page}
          {#if page === '...'}
            <span class="w-[36px] h-[36px] rounded-[8px] flex items-center justify-center text-sm" style="color: var(--w40);">&hellip;</span>
          {:else if page === 3}
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

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Tab / Filter Chips</h3>
    <div class="card p-4">
      <div class="flex flex-wrap gap-2">
        <button class="btn-primary btn text-xs px-3 py-1.5 rounded-full">All</button>
        <button class="text-xs px-3 py-1.5 rounded-full font-medium transition-colors hover:text-[--w] hover:border-[--w18]" style="background: var(--w8); color: var(--w60); border: 1px solid var(--w12);">Music</button>
        <button class="text-xs px-3 py-1.5 rounded-full font-medium transition-colors hover:text-[--w] hover:border-[--w18]" style="background: var(--w8); color: var(--w60); border: 1px solid var(--w12);">Arts</button>
        <button class="text-xs px-3 py-1.5 rounded-full font-medium transition-colors hover:text-[--w] hover:border-[--w18]" style="background: var(--w8); color: var(--w60); border: 1px solid var(--w12);">Blog</button>
        <button class="text-xs px-3 py-1.5 rounded-full font-medium transition-colors hover:text-[--w] hover:border-[--w18]" style="background: var(--w8); color: var(--w60); border: 1px solid var(--w12);">Links</button>
      </div>
    </div>
  </section>

  <!-- ════════════════════════════════════════════ -->
  <!-- 8. AVATARS                                   -->
  <!-- ════════════════════════════════════════════ -->
  <section id="avatars" class="mb-20">
    <h2 class="font-display text-[24px] tracking-wide mb-6">8. Avatars</h2>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Size Variations</h3>
    <div class="card p-6 space-y-6 mb-8">
      <div class="flex items-center gap-6">
        {#each [
          { size: 20, label: '20px' },
          { size: 24, label: '24px' },
          { size: 28, label: '28px' },
          { size: 36, label: '36px' },
          { size: 56, label: '56px' },
        ] as variant}
          <div class="flex flex-col items-center gap-1">
            <div
              class="rounded-full object-cover flex items-center justify-center text-black font-bold"
              style="width: {variant.size}px; height: {variant.size}px; font-size: {Math.max(8, variant.size / 3)}px; background: hsl({hue('user')}, 60%, 55%);"
            >
              U
            </div>
            <span class="text-[10px]" style="color: var(--w40);">{variant.label}</span>
          </div>
        {/each}
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">With Ring (OnlineUsers pattern)</h3>
    <div class="card p-6 mb-8">
      <div class="flex items-center gap-4">
        {#each ['Alice', 'Bob', 'Charlie'] as name}
          <img
            src="/Logo.svg"
            alt={name}
            class="rounded-full ring-2 ring-[--ring] object-cover"
            style="width: 28px; height: 28px;"
          />
        {/each}
        <!-- fallback avatar -->
        <div
          class="rounded-full ring-2 ring-[--ring] flex items-center justify-center text-[10px] font-bold text-black"
          style="width: 28px; height: 28px; background: hsl({hue('Dave')}, 60%, 55%);"
        >
          D
        </div>
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Overlapping Avatar Stack</h3>
    <div class="card p-6 mb-8">
      <div class="flex items-center">
        {#each ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve'] as name, i}
          <div
            class="relative rounded-full ring-2 ring-[--ring] hover:z-10 transition-transform hover:scale-110 cursor-pointer"
            style="margin-left: {i === 0 ? 0 : -8}px; z-index: {5 - i};"
          >
            <div
              class="flex items-center justify-center font-bold text-black"
              style="width: 28px; height: 28px; border-radius: 50%; font-size: 10px; background: hsl({hue(name)}, 60%, 55%);"
            >
              {name[0]}
            </div>
          </div>
        {/each}
        <div
          class="rounded-full bg-[--w8] ring-2 ring-[--ring] flex items-center justify-center text-[10px] font-medium shrink-0"
          style="width: 28px; height: 28px; margin-left: -8px; color: var(--w60);"
        >
          +7
        </div>
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Avatar Cropper Preview Style</h3>
    <div class="card p-6">
      <div class="flex items-center gap-6">
        <div class="relative w-24 h-24 rounded-full overflow-hidden flex items-center justify-center" style="background: var(--w8);">
          <Camera size={32} style="color: var(--w30);" />
          <div class="absolute inset-0 rounded-full border-2" style="border-color: var(--green);"></div>
        </div>
        <div>
          <div class="text-sm text-[--w]">Crop Area</div>
          <div class="text-xs mt-1" style="color: var(--w40);">Circle overlay with green border indicating crop boundary</div>
        </div>
      </div>
    </div>
  </section>

  <!-- ════════════════════════════════════════════ -->
  <!-- 9. SPACING & LAYOUT                         -->
  <!-- ════════════════════════════════════════════ -->
  <section id="spacing" class="mb-20">
    <h2 class="font-display text-[24px] tracking-wide mb-6">9. Spacing & Layout</h2>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Surface Spacing Scale</h3>
    <div class="card p-6 mb-8">
      <div class="space-y-4">
        {#each [
          { var: '--w5', label: 'w5', desc: 'Lightest surface' },
          { var: '--w8', label: 'w8', desc: 'Input bg, card hover' },
          { var: '--w12', label: 'w12', desc: 'Border, tag-active' },
          { var: '--w18', label: 'w18', desc: 'Heavier overlays' },
        ] as item}
          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm text-[--w]">var(--{item.label})</span>
              <span class="text-xs font-mono" style="color: var(--w40);">{item.desc}</span>
            </div>
            <div class="h-8 rounded-lg" style="background: var(--w8); border: 1px solid var(--w8);">
              <div class="h-full rounded-lg" style="background: var(--{item.var}); width: 100%;"></div>
            </div>
          </div>
        {/each}
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Tailwind Spacing</h3>
    <div class="card p-6 mb-8">
      <div class="space-y-3">
        {#each [
          { cls: 'gap-1', px: '4px' },
          { cls: 'gap-2', px: '8px' },
          { cls: 'gap-3', px: '12px' },
          { cls: 'gap-4', px: '16px' },
          { cls: 'gap-6', px: '24px' },
          { cls: 'gap-8', px: '32px' },
        ] as item}
          <div class="flex items-center gap-4">
            <span class="text-xs font-mono w-12 shrink-0" style="color: var(--w40);">{item.cls}</span>
            <div class="flex gap-[{item.px}] flex-1">
              <div class="h-8 rounded shrink-0" style="background: var(--w12); flex: 1;"></div>
              <div class="h-8 rounded shrink-0" style="background: var(--w12); flex: 1;"></div>
              <div class="h-8 rounded shrink-0" style="background: var(--w12); flex: 1;"></div>
            </div>
            <span class="text-xs font-mono w-12 shrink-0 text-right" style="color: var(--w30);">{item.px}</span>
          </div>
        {/each}
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Border Radius</h3>
    <div class="card p-6 mb-8">
      <div class="flex flex-wrap items-end gap-6">
        {#each [
          { px: '5px', label: '5px', desc: 'badge' },
          { px: '6px', label: '6px', desc: '' },
          { px: '8px', label: '8px', desc: 'button' },
          { px: '10px', label: '10px', desc: '' },
          { px: '12px', label: '0.75rem', desc: 'card' },
          { px: '20px', label: 'full', desc: 'circle' },
        ] as item}
          <div class="flex flex-col items-center gap-1">
            <div
              class="flex items-center justify-center text-[10px] font-mono"
              style="width: 48px; height: 48px; background: var(--w8); border: 1px solid var(--w12); border-radius: {item.px}; color: var(--w40);"
            >
              {item.px}
            </div>
            {#if item.desc}
              <span class="text-[10px]" style="color: var(--w30);">{item.desc}</span>
            {/if}
          </div>
        {/each}
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Breakpoints</h3>
    <div class="card p-6">
      <div class="space-y-2">
        {#each [
          { name: 'mobile', width: '<600px', cls: 'default' },
          { name: 'mobile (md)', width: '<768px', cls: 'md:' },
          { name: 'pc', width: '829px', cls: 'min-[829px]:' },
          { name: 'desktop', width: '768px+', cls: 'min-[829px]:' },
        ] as bp}
          <div class="flex items-center gap-4">
            <span class="text-sm font-medium text-[--w] w-24">{bp.name}</span>
            <span class="text-xs font-mono" style="color: var(--w40);">{bp.width}</span>
            <span class="text-xs font-mono px-2 py-0.5 rounded" style="background: var(--w8); color: var(--w60);">{bp.cls}</span>
          </div>
        {/each}
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mt-6 mb-3 uppercase tracking-wider">Max Widths</h3>
    <div class="card p-6">
      <div class="space-y-2">
        <div class="flex items-center gap-4">
          <span class="text-sm text-[--w]">Main content</span>
          <span class="text-xs font-mono px-2 py-0.5 rounded" style="background: var(--w8); color: var(--w60);">max-w-[828px]</span>
        </div>
        <div class="flex items-center gap-4">
          <span class="text-sm text-[--w]">Admin panels</span>
          <span class="text-xs font-mono px-2 py-0.5 rounded" style="background: var(--w8); color: var(--w60);">max-w-[480px]</span>
        </div>
      </div>
    </div>
  </section>

  <!-- ════════════════════════════════════════════ -->
  <!-- 10. ANIMATIONS & TRANSITIONS                -->
  <!-- ════════════════════════════════════════════ -->
  <section id="animations" class="mb-20">
    <h2 class="font-display text-[24px] tracking-wide mb-6">10. Animations & Transitions</h2>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Transition Tokens</h3>
    <div class="card p-6 mb-8">
      <div class="space-y-2">
        {#each [
          { duration: '0.15s', desc: 'card hover, quick interactions' },
          { duration: '0.16s', desc: 'Button component transition-all duration-160' },
          { duration: '0.2s', desc: 'global bg, border, color transition (default)' },
          { duration: '0.25s', desc: 'body theme transition' },
        ] as t}
          <div class="flex items-center gap-4">
            <span class="text-xs font-mono w-14 shrink-0" style="color: var(--w40);">{t.duration}</span>
            <span class="text-sm text-[--w80]">{t.desc}</span>
          </div>
        {/each}
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Hover Scale (Card Images)</h3>
    <div class="grid grid-cols-3 gap-4 mb-8">
      <div class="card rounded-xl overflow-hidden group cursor-pointer">
        <div class="w-full aspect-square flex items-center justify-center transition-transform group-hover:scale-105" style="background: var(--w8);">
          <Image size={32} style="color: var(--w30);" />
        </div>
        <div class="p-3">
          <div class="text-xs font-mono" style="color: var(--w40);">group-hover:scale-105</div>
        </div>
      </div>
      <div class="card rounded-xl overflow-hidden card-hover cursor-pointer">
        <div class="p-6 flex items-center justify-center">
          <span class="text-sm text-[--w60]">Card Hover BG</span>
        </div>
        <div class="px-4 pb-3">
          <div class="text-xs font-mono" style="color: var(--w40);">transition: bg 0.15s</div>
        </div>
      </div>
      <div class="card rounded-xl overflow-hidden cursor-pointer">
        <div class="p-6 flex items-center justify-center">
          <button class="inline-flex items-center gap-2 px-4 py-2 bg-[--green] text-[--b] rounded-[8px] text-[13px] font-bold transition-all hover:scale-[1.02] active:scale-[0.98]">
            CTA Button
          </button>
        </div>
        <div class="px-4 pb-3">
          <div class="text-xs font-mono" style="color: var(--w40);">hover:scale-[1.02]</div>
        </div>
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Pulse (Online Indicator)</h3>
    <div class="card p-6 mb-8">
      <div class="flex items-center gap-4">
        <span class="w-2 h-2 rounded-full bg-[--green] animate-pulse inline-block"></span>
        <span class="w-3 h-3 rounded-full bg-accent-green animate-pulse inline-block"></span>
        <span class="w-4 h-4 rounded-full bg-[--blue] animate-pulse inline-block"></span>
        <span class="text-xs" style="color: var(--w40); margin-left: 8px;">pulse animation &mdash; online status, loading</span>
      </div>
    </div>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Theme Transition</h3>
    <div class="card p-6">
      <p class="text-sm" style="color: var(--w60);">
        All elements transition smoothly between dark and light themes.
        Toggle the theme with the
        <button class="inline-flex items-center justify-center w-8 h-8 rounded-lg hover:bg-[--w8] text-[--w60] hover:text-[--w] transition-colors" type="button" onclick={() => $theme = $theme === 'dark' ? 'light' : 'dark'}>
          {#if $theme === 'dark'}<Sun size={16} />{:else}<Moon size={16} />{/if}
        </button>
        button in the header. Duration: <code class="text-xs bg-[--w8] px-1.5 py-0.5 rounded">0.2s ease</code> for most elements, <code class="text-xs bg-[--w8] px-1.5 py-0.5 rounded">0.25s</code> for body.
      </p>
    </div>
  </section>

  <!-- ════════════════════════════════════════════ -->
  <!-- 11. ICONOGRAPHY                             -->
  <!-- ════════════════════════════════════════════ -->
  <section id="icons" class="mb-20">
    <h2 class="font-display text-[24px] tracking-wide mb-6">11. Iconography</h2>

    <h3 class="text-[--w80] text-sm font-semibold mb-3 uppercase tracking-wider">Lucide Svelte &mdash; Common Icons</h3>
    <div class="card p-6">
      <div class="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-4">
        {#each commonIcons as iconItem}
          <div class="flex flex-col items-center gap-2 cursor-pointer group">
            <div
              class="w-12 h-12 rounded-xl flex items-center justify-center transition-colors group-hover:bg-[--w8]"
              style="background: var(--w5);"
            >
              <svelte:component this={iconItem.icon} size={22} strokeWidth={1.5} style="color: var(--w60);" class="group-hover:text-[--w]" />
            </div>
            <span class="text-[10px] font-mono text-center leading-tight" style="color: var(--w30);">{iconItem.name}</span>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- ════════════════════════════════════════════ -->
  <!-- FOOTER                                      -->
  <!-- ════════════════════════════════════════════ -->
  <footer class="py-12 border-t" style="border-color: var(--w8);">
    <div class="flex items-center justify-between">
      <span class="text-sm" style="color: var(--w40);">Design System &mdash; TheFoxxStuff</span>
      <span class="text-xs font-mono" style="color: var(--w30);">Last updated: 2026</span>
    </div>
  </footer>
</div>

<style>
  /* Smooth scroll for anchor links */
  html {
    scroll-behavior: smooth;
  }

  /* Hide scrollbar for admin nav */
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }

  /* Hover color transition helper for inline classes */
  [class]:hover {
    /* handled by Tailwind / component classes */
  }

  /* Ensure code snippets look right */
  code {
    font-family: 'SF Mono', 'Fira Code', monospace;
    font-size: 0.8em;
  }
</style>
