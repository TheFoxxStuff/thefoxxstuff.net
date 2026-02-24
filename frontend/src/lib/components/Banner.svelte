<script>
  import { browser } from '$app/environment';
  import { Image } from 'lucide-svelte';

  let {
    banner = { slides: [] },
    currentSlide = 0,
    getImageUrl,
    nextSlide,
    prevSlide,
    goToSlide
  } = $props();

  /**
   * Адаптивная загрузка: mobile → large, desktop → original.
   * Это экономит 2–5 МБ на мобильных слайдах.
   */
  function slideImageUrl(slide) {
    if (!slide.image_info) return null;
    if (!browser) return getImageUrl(slide.image_info, 'large');
    const variant = window.innerWidth <= 768 ? 'large' : 'medium';
    return getImageUrl(slide.image_info, variant);
  }
</script>

<section class="relative h-72 md:h-96 rounded-2xl overflow-hidden bg-[--w5]">
  {#if banner.slides.length > 0}
    {#each banner.slides as slide, i}
      <div
        class="absolute inset-0 transition-opacity duration-500 {i === currentSlide ? 'opacity-100' : 'opacity-0 pointer-events-none'}"
      >
        {#if slideImageUrl(slide)}
          <img
            loading={i === 0 ? 'eager' : 'lazy'}
            src={slideImageUrl(slide)}
            alt={slide.title}
            class="w-full h-full object-cover"
          />
        {:else}
          <div class="w-full h-full bg-gradient-to-r from-accent-green/10 to-accent-cyan/10"></div>
        {/if}

        <div class="absolute inset-0 bg-gradient-to-t from-dark-950/80 via-transparent to-dark-950/30"></div>

        <div class="absolute left-[19px] bottom-[14px] z-10">
          <div class="inline-flex items-center justify-center gap-2 px-3 py-1.5 rounded-lg text-sm text-[--w60] bg-[--w8] backdrop-blur-[2px]">
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
          aria-label="Previous slide"
          class="w-[36px] h-[36px] flex items-center justify-center rounded-[10px] text-[--w60] bg-[--w8] hover:bg-[--w12] transition-colors backdrop-blur-[2px]"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </button>
        <button
          onclick={nextSlide}
          aria-label="Next slide"
          class="w-[36px] h-[36px] flex items-center justify-center rounded-[10px] text-[--w60] bg-[--w8] hover:bg-[--w12] transition-colors backdrop-blur-[2px]"
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
            class="w-2 h-2 rounded-full transition-colors {i === currentSlide ? 'bg-[--w]' : 'bg-[--w30] hover:bg-[--w50]'}"
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
