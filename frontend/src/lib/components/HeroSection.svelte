<script>
  import { player } from '$lib/stores/player.js';

  let { latestRelease = null } = $props();

  function playLatest() {
    if (latestRelease) player.playRelease(latestRelease, 0);
  }
</script>

<div class="relative rounded-[12px] overflow-hidden bg-[--w5] border border-[--w8] p-8 md:p-10">
  <!-- Subtle gradient accent -->
  <div class="absolute inset-0 bg-gradient-to-br from-[rgba(115,238,7,0.05)] via-transparent to-[rgba(71,173,255,0.05)] pointer-events-none"></div>

  <div class="relative flex flex-col md:flex-row items-start md:items-center gap-6">
    <!-- Text content -->
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-2 mb-3">
        <span class="inline-block w-2 h-2 rounded-full bg-[--green] animate-pulse"></span>
        <span class="text-[12px] text-[--green] font-medium tracking-widest uppercase">Musician · Artist · Blogger</span>
      </div>

      <h1 class="font-display text-[32px] md:text-[42px] tracking-wide text-[--w] leading-tight mb-3" style="font-family: 'DrukWideCyr';">
        THEF<span class="text-[--green]">O</span>XXSTUFF
      </h1>

      <p class="text-[--w60] text-[15px] leading-relaxed max-w-md mb-6">
        Making music in the dark, painting strange worlds, writing about all of it.
        This is where it all lives.
      </p>

      <div class="flex flex-wrap gap-3">
        {#if latestRelease}
          <button
            onclick={playLatest}
            class="inline-flex items-center gap-2 px-5 py-2.5 bg-[--green] text-[--b] rounded-[8px] text-[14px] font-bold hover:opacity-90 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <svg class="w-4 h-4 ml-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
            Play Latest Release
          </button>
        {/if}

        <a
          href="/about"
          class="inline-flex items-center gap-2 px-5 py-2.5 bg-[--w8] text-[--w] rounded-[8px] text-[14px] font-medium hover:bg-[--w12] transition-all"
        >
          About me →
        </a>
      </div>
    </div>

    <!-- Stats / quick links -->
    <div class="flex flex-row md:flex-col gap-3 flex-shrink-0">
      {#each [
        { label: 'Music', href: '/music', icon: '♫' },
        { label: 'Art', href: '/arts', icon: '◈' },
        { label: 'Blog', href: '/blog', icon: '✦' },
      ] as item}
        <a
          href={item.href}
          class="flex items-center gap-2 px-4 py-2 bg-[--w8] hover:bg-[--w12] rounded-[8px] text-[--w60] hover:text-[--w] transition-all text-[14px]"
        >
          <span class="text-[--green] text-[16px]">{item.icon}</span>
          {item.label}
        </a>
      {/each}
    </div>
  </div>
</div>
