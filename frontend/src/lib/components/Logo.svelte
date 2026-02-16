<script>
  let { size = 'md' } = $props();
  const sizes = { sm: 'h-6', md: 'h-8', lg: 'h-10' };
</script>

<a href="/" class="flex items-center gap-2 group">
  <svg class="{sizes[size]} w-auto" viewBox="0 0 32 32" fill="none">
    <path d="M16 2L4 8v16l12 6 12-6V8L16 2z" fill="url(#logo-gradient)" />
    <path d="M10 12l6 3 6-3M16 15v9" stroke="#0a0a0a" stroke-width="2" stroke-linecap="round" />
    <defs>
      <linearGradient id="logo-gradient" x1="4" y1="2" x2="28" y2="30">
        <stop stop-color="#4ade80" />
        <stop offset="1" stop-color="#22d3ee" />
      </linearGradient>
    </defs>
  </svg>
  <span class="font-display text-xl tracking-wide group-hover:text-gradient transition-all">thefoxxstuff</span>
</a>
