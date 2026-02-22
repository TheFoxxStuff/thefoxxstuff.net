<script>
  import { getImageUrl } from '$lib/api';
  import { Calendar, Eye, Clock } from 'lucide-svelte';

  let { post } = $props();

  const coverUrl = $derived.by(() => {
    if (post.cover_image_info) return getImageUrl(post.cover_image_info, 'medium');
    return null;
  });

  const formatDate = (d) =>
    new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

  // Estimate reading time from content or use pre-computed field
  const readingTime = $derived.by(() => {
    if (post.reading_time_min) return post.reading_time_min;
    if (post.content) return Math.max(1, Math.ceil(post.content.split(/\s+/).length / 200));
    return null;
  });
</script>

<a href="/blog/{post.slug || post._id}" class="group flex flex-col h-full bg-[--w5] rounded-[12px] overflow-hidden transition-all duration-300 hover:bg-[--w8]">

  <div class="px-[18px] pt-[18px]">
    <div class="aspect-[16/10] bg-[--w12] rounded-[8px] overflow-hidden">
      {#if coverUrl}
        <img
          loading="lazy"
          src={coverUrl}
          alt={post.title}
          class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        />
      {:else}
        <div class="w-full h-full flex items-center justify-center text-[--w30] bg-[--w8]">
          <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
      {/if}
    </div>
  </div>

  <div class="flex-1 flex flex-col px-[18px] pt-[12px] pb-[18px]">
    <!-- Tags -->
    {#if post.tags?.length}
      <div class="flex gap-1.5 mb-2 flex-wrap">
        {#each post.tags.slice(0, 3) as tag}
          <span class="text-[11px] px-2 py-0.5 bg-[--w8] text-[--w60] rounded">{tag}</span>
        {/each}
      </div>
    {/if}

    <h3 class="font-bold text-[20px] leading-tight text-[--w] mb-[6px] transition-colors line-clamp-2 group-hover:text-accent-green">
      {post.title}
    </h3>

    {#if post.excerpt}
      <p class="text-[14px] leading-relaxed text-[--w60] mb-[8px] line-clamp-2">
        {post.excerpt}
      </p>
    {/if}

    <div class="mt-auto flex items-center justify-between pt-[12px] border-t border-[--w5]">
      <div class="flex items-center gap-2 text-[--green]">
        <Calendar size={13} />
        <span class="text-[13px] font-medium">{formatDate(post.created_at)}</span>
      </div>
      <div class="flex items-center gap-3 text-[--w60]">
        {#if readingTime}
          <div class="flex items-center gap-1">
            <Clock size={13} />
            <span class="text-[13px]">{readingTime} min</span>
          </div>
        {/if}
        <div class="flex items-center gap-1">
          <Eye size={13} />
          <span class="text-[13px]">{post.views}</span>
        </div>
      </div>
    </div>
  </div>
</a>
