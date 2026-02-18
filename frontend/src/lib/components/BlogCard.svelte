<script>
  import { getImageUrl } from '$lib/api';
  import { Calendar, Eye, ArrowUpRight } from 'lucide-svelte';

  let { post } = $props();

  const coverUrl = $derived.by(() => {
    if (post.cover_image_info) return getImageUrl(post.cover_image_info, 'medium');
    return null;
  });

  const formatDate = (d) =>
    new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
</script>

<a href="/blog/{post.slug || post._id}" class="group flex flex-col h-full rounded-[14px] overflow-hidden bg-[--w5] hover:bg-[--w8] transition-all duration-250 card-lift relative">

  <!-- Cover image -->
  <div class="relative overflow-hidden" style="height: 180px;">
    {#if coverUrl}
      <img
        loading="lazy"
        src={coverUrl}
        alt={post.title}
        class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-[1.05]"
      />
      <div class="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent"></div>
    {:else}
      <div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-dark-900 to-dark-800">
        <svg class="w-10 h-10 text-dark-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
    {/if}
  </div>

  <!-- Content -->
  <div class="flex flex-col flex-1 p-4 gap-2">
    <h3 class="font-bold text-[17px] leading-snug text-[--w] line-clamp-2 group-hover:text-[--green] transition-colors duration-200">
      {post.title}
    </h3>

    {#if post.excerpt}
      <p class="text-[13px] leading-relaxed text-[--w60] line-clamp-2 flex-1">
        {post.excerpt}
      </p>
    {/if}

    <div class="flex items-center justify-between pt-2 border-t border-[--w8] mt-auto">
      <div class="flex items-center gap-1.5 text-[--w40]">
        <Calendar size={12} />
        <span class="text-[12px]">{formatDate(post.created_at)}</span>
      </div>
      <div class="flex items-center gap-[5px] text-[--w40]">
        <Eye size={12} />
        <span class="text-[12px]">{post.views ?? 0}</span>
      </div>
    </div>
  </div>

  <!-- Arrow icon on hover -->
  <div class="absolute top-3 right-3 w-7 h-7 rounded-full bg-black/50 backdrop-blur-sm flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-200 translate-y-1 group-hover:translate-y-0">
    <ArrowUpRight size={14} class="text-white" />
  </div>
</a>
