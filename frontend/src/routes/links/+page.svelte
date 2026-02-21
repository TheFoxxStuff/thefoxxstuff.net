<!-- <script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { Breadcrumb } from '$lib/components';
  let links = $state([]);
  let loading = $state(true);
  onMount(async () => { try { links = await api.links.list(); } catch (e) { console.error(e); } finally { loading = false; } });
</script>
<svelte:head><title>Links | TheFoxxStuff</title></svelte:head>
<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0">
  <h1 class="font-display text-[24px] tracking-wide mb-2">Links</h1>
  <Breadcrumb items={[{ href: '/links', label: 'Links' }]} />
  <div class="mt-8 max-w-xl mx-auto space-y-4">
    {#if loading}{#each Array(4) as _}<div class="h-16 bg-dark-800 rounded-xl animate-pulse"></div>{/each}
    {:else}{#each links as link}
      <a href={link.url} target="_blank" rel="noopener noreferrer" class="card card-hover p-4 flex items-center gap-4 group">
        <div class="w-10 h-10 flex items-center justify-center text-dark-400 group-hover:text-accent-green">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101" /></svg>
        </div>
        <span class="font-medium group-hover:text-gradient">{link.title}</span>
      </a>
    {/each}{/if}
  </div>
</div> -->



<script>
  import { Breadcrumb } from '$lib/components';
</script>
<svelte:head><title>Links | TheFoxxStuff</title></svelte:head>
<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0">
  <h1 class="font-display text-[24px] tracking-wide mb-2">Links</h1>
  <Breadcrumb items={[{ href: '/links', label: 'Links' }]} />
  <div class="">
    <div class="mt-6">
  
  <section class="mb-12">
    <h2 class="text-4xl font-black mb-8 tracking-tight italic uppercase">Social networks</h2>
    
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-x-[16px] gap-y-[20px]">
      <div class="group cursor-pointer">
        <div class="bg-[#FF0000] aspect-video rounded-xl flex items-center justify-center mb-[12px] transition-transform hover:scale-[1.02]">
           <svg class="w-16 h-16" fill="currentColor" viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
        </div>
        <h3 class="text-xl font-bold">YouTube</h3>
        <p class="text-gray-400 text-sm">All video</p>
      </div>

      <div class="group cursor-pointer">
        <div class="bg-[#0077FF] aspect-video rounded-xl flex items-center justify-center mb-[12px] transition-transform hover:scale-[1.02]">
           <svg class="w-16 h-16" fill="currentColor" viewBox="0 0 24 24"><path d="M13.162 18.994c-6.098 0-9.57-4.172-9.715-11.106H6.52c.102 5.093 2.346 7.252 4.124 7.701V7.888h3.075v4.397c1.884-.204 3.73-2.196 4.398-4.397h2.957a7.22 7.22 0 0 1-4.04 5.564 7.421 7.421 0 0 1 4.704 5.542h-3.271a4.343 4.343 0 0 0-3.824-3.565v3.565h-1.481z"/></svg>
        </div>
        <h3 class="text-xl font-bold">Vk</h3>
        <p class="text-gray-400 text-sm">Vk Group for RU</p>
      </div>

      <div class="group cursor-pointer">
        <div class="bg-[#24A1DE] aspect-video rounded-xl flex items-center justify-center mb-[12px] transition-transform hover:scale-[1.02]">
           <svg class="w-14 h-14 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12.012 12.012 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>
        </div>
        <h3 class="text-xl font-bold">Telegram</h3>
        <p class="text-gray-400 text-sm">Be aware of everything</p>
      </div>

      <div class="group cursor-pointer">
        <div class="bg-black border border-gray-800 aspect-video rounded-xl flex items-center justify-center mb-[12px] transition-transform hover:scale-[1.02]">
           <svg class="w-12 h-12" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
        </div>
        <h3 class="text-xl font-bold">X</h3>
        <p class="text-gray-400 text-sm">Twitter for ENG</p>
      </div>
    </div>
  </section>

  <section>
    <h2 class="text-4xl font-black mb-8 tracking-tight italic uppercase">Streaming</h2>
    
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-x-[16px] gap-y-[20px]">
      <div class="group cursor-pointer">
        <div class="bg-[#191414] aspect-video rounded-xl flex items-center justify-center mb-[12px] transition-transform hover:scale-[1.02]">
           <div class="w-16 h-16 bg-[#1DB954] rounded-full flex items-center justify-center">
             <svg class="w-10 h-10 text-black" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.49 17.306c-.215.353-.674.463-1.027.248-2.85-1.742-6.437-2.136-10.662-1.17-.404.092-.81-.16-.902-.564-.092-.404.16-.81.564-.902 4.622-1.057 8.59-.606 11.78 1.343.353.215.463.674.247 1.027zm1.465-3.264c-.27.44-.846.58-1.287.31-3.262-2.004-8.234-2.586-12.093-1.414-.495.15-1.02-.128-1.17-.623-.15-.495.128-1.02.623-1.17 4.41-1.338 9.89-.684 13.618 1.604.44.27.58.847.31 1.287zm.127-3.41c-3.913-2.325-10.364-2.542-14.12-1.403-.6.182-1.242-.164-1.424-.764-.182-.6.164-1.242.764-1.424 4.307-1.306 11.44-1.05 15.93 1.614.54.32.716 1.015.396 1.555-.32.54-1.015.716-1.555.396z"/></svg>
           </div>
        </div>
        <h3 class="text-xl font-bold">Spotify</h3>
        <p class="text-gray-400 text-sm">Vk Group for RU</p>
      </div>

      <div class="group cursor-pointer">
        <div class="bg-black border border-gray-800 aspect-video rounded-xl flex items-center justify-center mb-[12px] transition-transform hover:scale-[1.02]">
           <div class="text-[#FFCC00]">
             <svg class="w-16 h-16" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0L14.59 8.41L23 11L14.59 13.59L12 22L9.41 13.59L1 11L9.41 8.41L12 0Z"/></svg>
           </div>
        </div>
        <h3 class="text-xl font-bold">Yandex Music</h3>
        <p class="text-gray-400 text-sm">Будь в курсе всего</p>
      </div>

      <div class="group cursor-pointer">
        <div class="bg-[#0077FF] aspect-video rounded-xl flex items-center justify-center mb-[12px] transition-transform hover:scale-[1.02]">
           <div class="bg-gradient-to-br from-pink-400 to-purple-600 p-3 rounded-lg">
             <svg class="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/></svg>
           </div>
        </div>
        <h3 class="text-xl font-bold">VK Music</h3>
        <p class="text-gray-400 text-sm">Twitter for ENG</p>
      </div>

      <div class="group cursor-pointer">
        <div class="bg-[#FF7700] aspect-video rounded-xl flex items-center justify-center mb-[12px] transition-transform hover:scale-[1.02]">
           </div>
        <h3 class="text-xl font-bold">SoundCloud</h3>
        <p class="text-gray-400 text-sm">Группа в Vk</p>
      </div>
    </div>
  </section>

</div>

  </div>
</div>


