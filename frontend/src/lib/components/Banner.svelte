<script>
  import { Image, ChevronLeft, ChevronRight } from 'lucide-svelte';

  let {
    banner = { slides: [] },
    currentSlide = 0,
    getImageUrl,
    nextSlide,
    prevSlide,
    goToSlide
  } = $props();

  function slideImageUrl(slide) {
    if (slide.image_info) return getImageUrl(slide.image_info, 'original');
    return null;
  }
</script>

<section class="relative rounded-[16px] overflow-hidden bg-dark-900" style="height: clamp(200px, 38vw, 340px);">
  {#if banner.slides.length > 0}
    {#each banner.slides as slide, i}
      <div
        class="absolute inset-0 transition-all duration-600 ease-in-out"
        style="opacity: {i === currentSlide ? 1 : 0}; pointer-events: {i === currentSlide ? 'auto' : 'none'};"
      >
        {#if slideImageUrl(slide)}
          <img
            loading={i === 0 ? 'eager' : 'lazy'}
            src={slideImageUrl(slide)}
            alt={slide.title}
            class="w-full h-full object-cover"
          />
        {:else}
          <div class="w-full h-full" style="background: linear-gradient(135deg, rgba(35,130,120,0.2) 0%, rgba(70,40,120,0.2) 100%)"></div>
        {/if}

        <!-- Gradient overlays -->
        <div class="absolute inset-0" style="background: linear-gradient(to top, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.1) 40%, rgba(0,0,0,0.25) 100%)"></div>

        <!-- Title label -->
        {#if slide.title}
          <div class="absolute left-4 bottom-4 z-10">
            <div class="flex items-center gap-2 px-3 py-1.5 rounded-[8px] backdrop-blur-md" style="background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1);">
              <Image size={14} class="text-[--w60] shrink-0" />
              <span class="text-[13px] text-[--w60]">{slide.title}</span>
            </div>
          </div>
        {/if}
      </div>
    {/each}

    {#if banner.slides.length > 1}
      <!-- Prev/Next buttons -->
      <button
        onclick={prevSlide}
        class="absolute left-3 top-1/2 -translate-y-1/2 z-20 w-9 h-9 rounded-full flex items-center justify-center backdrop-blur-md transition-all duration-150 hover:scale-105"
        style="background: rgba(0,0,0,0.55); border: 1px solid rgba(255,255,255,0.12);"
        aria-label="Previous slide"
      >
        <ChevronLeft size={18} class="text-white" />
      </button>
      <button
        onclick={nextSlide}
        class="absolute right-3 top-1/2 -translate-y-1/2 z-20 w-9 h-9 rounded-full flex items-center justify-center backdrop-blur-md transition-all duration-150 hover:scale-105"
        style="background: rgba(0,0,0,0.55); border: 1px solid rgba(255,255,255,0.12);"
        aria-label="Next slide"
      >
        <ChevronRight size={18} class="text-white" />
      </button>

      <!-- Dots -->
      <div class="absolute bottom-4 right-4 flex gap-1.5 z-20">
        {#each banner.slides as _, i}
          <button
            onclick={() => goToSlide(i)}
            class="h-[3px] rounded-full transition-all duration-300 {i === currentSlide ? 'w-6 bg-white' : 'w-2 bg-white/35 hover:bg-white/55'}"
            aria-label="Slide {i + 1}"
          ></button>
        {/each}
      </div>
    {/if}
  {:else}
    <!-- Empty state -->
    <div class="absolute inset-0 flex items-center justify-center" style="background: linear-gradient(135deg, rgba(35,130,120,0.12) 0%, rgba(70,40,120,0.12) 100%)">
      <p class="text-[13px] text-[--w40]">No banner slides</p>
    </div>
  {/if}
</section>

<style>
  .duration-600 { transition-duration: 600ms; }
</style>
