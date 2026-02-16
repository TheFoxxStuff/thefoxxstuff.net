<script>
  import Button from '$lib/components/Button.svelte';
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';
  import { ExternalLink } from 'lucide-svelte';
  const currentYear = new Date().getFullYear();
</script>

<footer class="mx-auto w-full max-w-[828px] flex items-center justify-between mb-[60px] my-[20px] p-[14px_30px] bg-[--w5] rounded-[8px]">
  <div class="text-[--w60] text-[14px]">
    © TheFoxxStuff TEST 67sd {currentYear}
  </div>

  <div class="flex flex-row gap-2 items-center">
    <Button 
      href="https://t.me/thefoxxstuff" 
      target="_blank"
      iconRight={ExternalLink}
    >
      {#snippet iconLeft()}
        <img src="/icons/telegram-icon.svg" alt="" class="w-[20px] h-[20px]" />
      {/snippet}
      
      <span class="text-[--w]">@thefoxxstuff</span>
    </Button>
    
    <ThemeToggle />
  </div>
</footer>
