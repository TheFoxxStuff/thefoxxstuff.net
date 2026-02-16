<script>
  import { Image } from 'lucide-svelte';
  
  // Принимаем данные баннера и функции управления как пропсы
  let { 
    banner = { slides: [] }, 
    currentSlide = 0,
    api,
    getImageUrl,
    nextSlide,
    prevSlide,
    goToSlide 
  } = $props(); // Используем Svelte 5 синтаксис ($props). Если у вас Svelte 4, используйте export let.
</script>

<section class="relative h-72 md:h-96 bg-dark-900 rounded-2xl overflow-hidden">
  {#if banner.slides.length > 0}
    {#each banner.slides as slide, i}
      <div 
        class="absolute inset-0 transition-opacity duration-500 {i === currentSlide ? 'opacity-100' : 'opacity-0 pointer-events-none'}"
      >
        {#await api.upload.getInfo(slide.image) then imgInfo}
          <img loading="lazy" src={getImageUrl(imgInfo, 'original')} alt={slide.title} class="w-full h-full object-cover" />
        {:catch}
          <div class="w-full h-full bg-gradient-to-r from-accent-green/10 to-accent-cyan/10"></div>
        {/await}

        <div class="absolute inset-0 bg-gradient-to-t from-dark-950/80 via-transparent to-dark-950/30"></div>

        <div class="absolute left-[19px] bottom-[14px] z-10">
          <div class="inline-flex items-center justify-center gap-2 px-3 py-1.5 bg-dark-900/60 rounded-lg text-sm text-white/60 backdrop-blur-[2px]">
            <Image size={20} class="shrink-0" />
            <span class="text-dark-300 leading-[20px] flex items-center">
              {slide.title ?? 'Banner'}
            </span>
          </div>
        </div>
      </div>
    {/each}
    
    {#if banner.slides.length > 1}
      <div class="absolute right-[19px] bottom-[14px] flex gap-2 z-20">
        <button 
          onclick={prevSlide} 
          class="w-[36px] h-[36px] flex items-center justify-center bg-dark-900/60 hover:bg-dark-800 rounded-[10px] text-white/60 transition-colors backdrop-blur-[2px]"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </button>

        <button 
          onclick={nextSlide} 
          class="w-[36px] h-[36px] flex items-center justify-center bg-dark-900/60 hover:bg-dark-800 rounded-[10px] text-white/60 transition-colors backdrop-blur-[2px]"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 18l6-6-6-6" />
          </svg>
        </button>
      </div>

      <div class="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2 z-10">
        {#each banner.slides as _, i}
          <button 
            onclick={() => goToSlide(i)} 
            class="w-2 h-2 rounded-full transition-colors {i === currentSlide ? 'bg-white' : 'bg-dark-500 hover:bg-dark-400'}"
            aria-label="Go to slide {i + 1}"
          ></button>
        {/each}
      </div>
    {/if}
  {:else}
    <div class="absolute inset-0 bg-gradient-to-r from-accent-green/10 to-accent-cyan/10"></div>
    <div class="absolute bottom-4 left-4 text-sm text-dark-400">No banner slides</div>
  {/if}
</section>