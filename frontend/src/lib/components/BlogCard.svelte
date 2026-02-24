<script>
  import { getImageUrl } from '$lib/api';
  import { Calendar, Eye } from 'lucide-svelte';
  import { getDateColorInfo } from '$lib/utils/dateColor';

  let { post } = $props();

  // cover_image_info отдаётся бэкендом — убран api.upload.getInfo() внутри компонента.
  // Это был N+1 на фронтенде: при 2 постах на главной = 2 лишних запроса.
  const coverUrl = $derived.by(() => {
    if (post.cover_image_info) return getImageUrl(post.cover_image_info, 'medium');
    return null;
  });

  const formatDate = (d) =>
    new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

  // 🎨 Smart date color indication
  const dateColor = $derived(getDateColorInfo(post.created_at));

  const gradientTextStyle = $derived(
    dateColor.gradient
      ? `background: ${dateColor.gradient}; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;`
      : `color: ${dateColor.iconColor};`
  );
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
    <h3 class="font-bold text-[18px] leading-tight text-[--w] mb-[4px] transition-colors line-clamp-2">
      {post.title}
    </h3>

    {#if post.excerpt}
      <p class="text-[14px] leading-relaxed text-[--w60] mb-[8px] line-clamp-2">
        {post.excerpt}
      </p>
    {/if}

    <div class="mt-auto flex items-center justify-between pt-[12px]">
      <!-- 🎨 Smart date indicator with gradient -->
        <!-- Icon gets the first gradient color -->
        <span style="color: {dateColor.iconColor}; flex-shrink: 0; display: flex; align-items: center;">
        </span>
        <!-- Date text gets the full gradient -->
        <span class="text-[14px] font-medium" style={gradientTextStyle}>
          {formatDate(post.created_at)}
        </span>
      </div>
        <span class="text-[14px]">{post.views} views</span>
      </div>
    </div>
  </div>
</a>
