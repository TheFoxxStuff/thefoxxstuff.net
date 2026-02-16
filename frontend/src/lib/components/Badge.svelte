<script>
  export let icon = null; 
  export let text = "28 April, 2024";
  export let iconSize = 16;
</script>

<div class="inline-flex items-center gap-[6px] px-[8px] py-[4px] bg-[rgba(255,255,255,0.05)] rounded-[5px] text-[rgba(255,255,255,0.6)] w-fit h-[26px]">
  {#if icon}
    <div class="flex-shrink-0 flex items-center justify-center">
      <svelte:component this={icon} size={iconSize} />
    </div>
  {/if}

  <span class="text-[14px] leading-none whitespace-nowrap">
    {text}
  </span>
</div>