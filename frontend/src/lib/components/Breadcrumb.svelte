<script>
  import { Home, ChevronRight } from 'lucide-svelte'; 
  let { items = [] } = $props();
</script>

<nav class="flex items-center gap-[4px] text-sm text-[--w60]">
<a class="btn-breadcrumb hover:text-[--w]" href="/"><Home size={16} />Home</a>

  {#each items as item, i}
    <ChevronRight size={14}/>
    <!-- {#if i === items.length - 1}<span class="text-[--w]">{item.label}</span>{:else}<a href={item.href} class="hover:text-[--w]">{item.label}</a>{/if} -->
     {#if i === items.length - 1}<span class="btn-breadcrumb hover:bg-[--none]">{item.label}</span>{:else}<a class="btn-breadcrumb hover:text-[--w]" href={item.href}>{item.label}</a>{/if}
    
  {/each}
</nav>
