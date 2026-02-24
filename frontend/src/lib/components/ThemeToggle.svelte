<script>
  import { theme, toggleTheme } from '$lib/stores/theme.js';
  import { Sun, Moon } from 'lucide-svelte';
</script>

<button
  onclick={toggleTheme}
  class="flex items-center justify-center w-8 h-8 rounded-lg hover:bg-[--w8] text-[--w60] hover:text-[--w] transition-colors"
  aria-label="Toggle theme"
  title={$theme === 'dark' ? 'Switch to light' : 'Switch to dark'}
>
  {#if $theme === 'dark'}
    <Sun size={16} />
  {:else}
    <Moon size={16} />
  {/if}
</button>
