<script>
  import { ChevronLeft, ChevronRight } from 'lucide-svelte';

  let { currentPage = $bindable(1), totalPages = 21, onPageChange } = $props();

  let isEditing = $state(false);
  let inputValue = $state(currentPage);

  $effect(() => {
    inputValue = currentPage;
  });

  const handleKeydown = (e) => {
    if (e.key === 'Enter') submit();
    else if (e.key === 'Escape') {
      isEditing = false;
      inputValue = currentPage;
    }
  };

  const submit = () => {
    let val = parseInt(inputValue);
    if (!isNaN(val) && val >= 1 && val <= totalPages) {
      onPageChange(val);
    } else {
      inputValue = currentPage;
    }
    isEditing = false;
  };

  // Логика формирования кнопок с многоточием
const getPages = () => {
    const pages = [];
    
    // Если страниц всего 3 или меньше, просто выводим их
    if (totalPages <= 3) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
      return pages;
    }

    // Определяем начало нашего "окна" из 3-х кнопок
    let start = currentPage - 1;

    // Сдвигаем окно, чтобы оно не выходило за границы
    if (start < 1) start = 1;
    if (start > totalPages - 3) start = totalPages - 3; 

    // Добавляем 3 последовательные страницы
    for (let i = start; i < start + 3; i++) {
      if (i < totalPages) {
        pages.push(i);
      }
    }

    // Если последняя страница из тройки — это не предпоследняя страница всего списка,
    // добавляем многоточие перед финальной страницей
    if (pages[pages.length - 1] < totalPages - 1) {
      pages.push(null);
    }

    // Всегда добавляем последнюю страницу, если её еще нет в списке
    if (!pages.includes(totalPages)) {
      pages.push(totalPages);
    }

    return pages;
  };
</script>



<div class="flex items-center gap-3 w-full h-[36px] font-sans select-none">
  <div class="flex items-center gap-[5px] px-3 h-[36px] rounded-[8px] bg-[var(--w5)]">
    <span class="text-sm text-[var(--w60)] whitespace-nowrap">Page —</span>
    {#if isEditing}
      <input
        type="number"
        bind:value={inputValue}
        onkeydown={handleKeydown}
        onblur={submit}
        use:autofocus
        class="w-[32px] h-[22px] bg-[var(--w12)] text-[var(--w)] text-xs font-medium text-center rounded-[4px] border-none outline-none focus:ring-1 focus:ring-[var(--blue)] [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
      />
    {:else}
      <button 
        onclick={() => isEditing = true}
        class="flex items-center justify-center min-w-[22px] h-[22px] px-1.5 text-xs font-medium text-[var(--w)] bg-[var(--w12)] rounded-[4px] hover:bg-[var(--w18)] transition-colors"
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