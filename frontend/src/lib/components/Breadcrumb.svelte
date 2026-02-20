<script>
  import { Home, ChevronRight } from 'lucide-svelte';
  // items: { href, label }[]
  // loading: если true — последний элемент показывается как скелетон
  let { items = [], loading = false } = $props();
</script>

<nav class="flex items-center gap-[4px] text-sm text-[--w60]">
  <a class="btn-breadcrumb hover:text-[--w]" href="/"><Home size={20} />Home</a>

  {#each items as item, i}
    <ChevronRight size={14} class="shrink-0 text-[--w30]" />

    {#if i === items.length - 1}
      <!-- Последний элемент: скелетон при загрузке, иначе просто текст -->
      {#if loading}
        <span class="inline-block h-[14px] w-[80px] rounded bg-[--w12] animate-pulse"></span>
      {:else}
        <span class="btn-breadcrumb hover:bg-[--none] text-[--w]">{item.label}</span>
      {/if}
    {:else}
      <a class="btn-breadcrumb hover:text-[--w]" href={item.href}>{item.label}</a>
    {/if}
  {/each}
</nav>
