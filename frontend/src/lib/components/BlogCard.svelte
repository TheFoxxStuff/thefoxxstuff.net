<script>
  import { api, getImageUrl } from '$lib/api';
  import { Calendar, Eye } from 'lucide-svelte';

  let { post } = $props();

  const formatDate = (d) => 
    new Date(d).toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
</script>

<a href="/blog/{post._id}" class="group flex flex-col h-full bg-[--w5] rounded-[12px] overflow-hidden transition-all duration-300 hover:bg-[--w8]">
  
  <div class="px-[18px] pt-[18px]">
    <div class="aspect-[16/10] bg-[--w12] rounded-[8px] overflow-hidden">
      {#if post.cover_image}
        {#await api.upload.getInfo(post.cover_image) then imgInfo}
          <img
            loading="lazy" 
            src={getImageUrl(imgInfo, 'medium')} 
            alt={post.title} 
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" 
          />
        {:catch}
          <div class="w-full h-full flex items-center justify-center text-[--w60] bg-[--w60]">
           <Calendar size={14} />
           </div>
        {/await}
      {:else}
        <div class="w-full h-full flex items-center justify-center text-[--w60] bg-[--w60]">
           <Eye size={14} />
        </div>
      {/if}
    </div>
  </div>

  <div class="flex-1 flex flex-col px-[18px] pt-[12px] pb-[18px]">
    <h3 class="font-bold text-[18px] leading-tight text-[--w] mb-[4px] transition-colors line-clamp-2">
      {post.title}
    </h3>
    
    {#if post.excerpt}
      <p class="text-[14px] leading-relaxed text-[--w60] mb-[8px] line-clamp-2">
        {post.excerpt}
      </p>
    {/if}

    <div class="mt-auto flex items-center justify-between pt-[12px]">
      <div class="flex items-center gap-2 text-[--green]">
        <Calendar size={14} />
        <span class="text-[14px] font-medium">{formatDate(post.created_at)}</span>
      </div>
      
      <div class="flex items-center gap-[6px] text-[--w60]">
        <Eye size={14} />
        <span class="text-[14px]">{post.views} views</span>
      </div>
    </div>
  </div>
</a>