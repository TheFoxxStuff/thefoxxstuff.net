<script>
  let { 
    onclick, 
    href = null,
    target = null, // не забудьте добавить проп для blank
    children, 
    iconLeft: IconLeft = null, 
    iconRight: IconRight = null,
    class: className = "" 
  } = $props();

  const baseClass = "inline-flex items-center justify-center gap-[4px] px-[12px] py-[6px] bg-[--w5] hover:bg-[--w8] text-[#999] hover:text-[--w] rounded-[8px] transition-all duration-200 group no-underline";
</script>

{#if href}
  <a {href} {target} rel={target === '_blank' ? 'noreferrer' : null} class="{baseClass} {className}">
    {@render content()}
  </a>
{:else}
  <button type="button" onclick={onclick} class="{baseClass} {className}">
    {@render content()}
  </button>
{/if}

{#snippet content()}
  {#if IconLeft}
    <div class="flex items-center group-hover:opacity-80 transition-opacity">
      {#if typeof IconLeft === 'function'}
        {@render IconLeft()} 
      {:else}
        <IconLeft size={20} strokeWidth={2.5} />
      {/if}
    </div>
  {/if}

  <span class="text-[14px] font-medium tracking-wide">
    {@render children?.()}
  </span>

  {#if IconRight}
    <div class="flex items-center group-hover:text-[--w] transition-colors">
      <IconRight size={20} strokeWidth={2.5} />
    </div>
  {/if}
{/snippet}