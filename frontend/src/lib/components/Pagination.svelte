<script>
  import { ChevronLeft, ChevronRight } from 'lucide-svelte';

  let { currentPage = $bindable(1), totalPages = 21, onPageChange } = $props();

  let isEditing = $state(false);
  let inputValue = $state(String(currentPage));
  // Состояние валидации для real-time обратной связи
  let inputError = $state(false);

  $effect(() => {
    if (!isEditing) inputValue = String(currentPage);
  });

  /** Проверяем ввод в реальном времени */
  function handleInput(e) {
    inputValue = e.target.value;
    const val = parseInt(inputValue);
    inputError = isNaN(val) || val < 1 || val > totalPages;
  }

  const handleKeydown = (e) => {
    if (e.key === 'Enter') submit();
    else if (e.key === 'Escape') {
      isEditing = false;
      inputValue = String(currentPage);
      inputError = false;
    }
  };

  const submit = () => {
    const val = parseInt(inputValue);
    if (!isNaN(val) && val >= 1 && val <= totalPages) {
      onPageChange(val);
    } else {
      inputValue = String(currentPage);
    }
    isEditing = false;
    inputError = false;
  };

  const getPages = () => {
    const pages = [];
    if (totalPages <= 3) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
      return pages;
    }
    let start = currentPage - 1;
    if (start < 1) start = 1;
    if (start > totalPages - 3) start = totalPages - 3;
    for (let i = start; i < start + 3; i++) {
      if (i < totalPages) pages.push(i);
    }
    if (pages[pages.length - 1] < totalPages - 1) pages.push(null);
    if (!pages.includes(totalPages)) pages.push(totalPages);
    return pages;
  };

  function autofocus(node) {
    node.focus();
    node.select();
  }
</script>

<div class="flex items-center gap-3 w-full h-[36px] font-sans select-none">
  <div class="flex items-center gap-[5px] px-3 h-[36px] rounded-[8px] bg-[var(--w5)]">
    <span class="text-sm text-[var(--w60)] whitespace-nowrap">Page —</span>
    {#if isEditing}
      <input
        type="number"
        min="1"
        max={totalPages}
        bind:value={inputValue}
        oninput={handleInput}
        onkeydown={handleKeydown}
        onblur={submit}
        use:autofocus
        class="w-[32px] h-[22px] text-[var(--w)] text-xs font-medium text-center rounded-[4px] border-none outline-none focus:ring-1 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none transition-colors
          {inputError
            ? 'bg-accent-red/20 focus:ring-accent-red'
            : 'bg-[var(--w12)] focus:ring-[var(--blue)]'}"
      />
    {:else}
      <button
        onclick={() => { isEditing = true; inputValue = String(currentPage); }}
        class="flex items-center justify-center min-w-[22px] h-[22px] px-1.5 text-xs font-medium text-[var(--w)] bg-[var(--w12)] rounded-[4px] hover:bg-[var(--w18)] transition-colors"
        title="Click to enter page number"
      >
        {currentPage}
      </button>
    {/if}
  </div>

  <div class="flex gap-1.5">
    {#each getPages() as p}
      {#if p === null}
        <div class="w-[36px] h-[36px] flex items-center justify-center text-[var(--w60)]">
          <span class="mt-[-4px] text-lg">...</span>
        </div>
      {:else}
        <button
          onclick={() => onPageChange(p)}
          class="w-[36px] h-[36px] flex items-center justify-center rounded-[8px] text-sm font-medium transition-all
          {p === currentPage
            ? 'bg-[var(--w12)] text-[var(--w)]'
            : 'bg-[var(--w5)] text-[var(--w60)] hover:bg-[var(--w8)] hover:text-[var(--w)]'}"
        >
          {p}
        </button>
      {/if}
    {/each}
  </div>

  <div class="flex gap-1.5 ml-auto">
    <button
      onclick={() => onPageChange(Math.max(1, currentPage - 1))}
      disabled={currentPage === 1}
      class="w-[36px] h-[36px] flex items-center justify-center rounded-[8px] bg-[var(--w5)] text-[var(--w60)] transition-colors hover:enabled:bg-[var(--w12)] hover:enabled:text-[var(--w)] disabled:opacity-20 disabled:cursor-not-allowed"
    >
      <ChevronLeft size={20} />
    </button>

    <button
      onclick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
      disabled={currentPage === totalPages}
      class="w-[36px] h-[36px] flex items-center justify-center rounded-[8px] bg-[var(--w5)] text-[var(--w60)] transition-colors hover:enabled:bg-[var(--w12)] hover:enabled:text-[var(--w)] disabled:opacity-20 disabled:cursor-not-allowed"
    >
      <ChevronRight size={20} />
    </button>
  </div>
</div>

<style>
  input[type='number'] {
    -moz-appearance: textfield;
  }
</style>
