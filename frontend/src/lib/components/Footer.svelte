<script>
  import Button from '$lib/components/Button.svelte';
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';
  import { ExternalLink } from 'lucide-svelte';
  const currentYear = new Date().getFullYear();
</script>

<footer class="mx-auto w-full max-w-[828px] mb-[60px] my-[24px]">
  <div class="flex items-center justify-between px-5 py-3.5 rounded-[12px]" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);">
    <div class="flex items-center gap-3">
      <span class="text-[13px]" style="color: rgba(255,255,255,0.35);">© {currentYear} TheFoxxStuff</span>
      <div class="w-px h-3" style="background: rgba(255,255,255,0.1);"></div>
      <span class="text-[11px]" style="color: rgba(255,255,255,0.2);">All rights reserved</span>
    </div>

    <div class="flex items-center gap-2">
      <Button
        href="https://t.me/thefoxxstuff"
        target="_blank"
        iconRight={ExternalLink}
      >
        {#snippet iconLeft()}
          <img src="/icons/telegram-icon.svg" alt="" class="w-4 h-4" />
        {/snippet}
        <span class="text-[13px]">@thefoxxstuff</span>
      </Button>

      <ThemeToggle />
    </div>
  </div>
</footer>
