<script>
  import { Breadcrumb } from '$lib/components';
  import { ExternalLink, Mail, MapPin } from 'lucide-svelte';

  const about = {
    name: 'TheFoxxStuff',
    location: 'Republic of Sakha (Yakutia)',
    city: 'Yakutsk',
    genres: ['Hardcore', 'Breakcore', "Drum'n'Bass"],
    bio: 'He has his own unique style and is able to convey his character in each composition. His music is characterized by its lightness and atmosphere, a quality that is influenced by his unique place of residence. His roots in Yakutia and his understanding of local culture and traditions give him a special source of strength that he uses to create music with a sound and atmosphere that is extremely unique to his region.',
    avatar: '/about.jpg',
    email: 'mail@thefoxxstuff.net',
    social_links: {
      bandcamp: 'https://thefoxxstuff.bandcamp.com',
      soundcloud: 'https://soundcloud.com/thefoxxstuff',
      twitter: 'https://twitter.com/thefoxxstuff',
      vk: 'https://vk.com/thefoxxstuff',
      telegram: 'https://t.me/thefoxxstuff'
    },
    liner_notes: "So I spent a few hours in this world, until I felt it was time to return to reality. I opened my eyes and felt that my mind was cleansed and filled with new knowledge. I was ready for new challenges in life, knowing that the world where summer reigns will always be with me."
  };

  const socialIcons = {
    bandcamp: '🎵',
    soundcloud: '☁️',
    twitter: '𝕏',
    vk: '🅥',
    telegram: '✈️',
  };
</script>

<svelte:head><title>About | TheFoxxStuff</title></svelte:head>

<div class="mx-auto max-w-6xl px-4 pt-5 pb-12 min-[829px]:max-w-[828px] min-[829px]:px-0">
  <h1 class="font-display text-3xl tracking-wide mb-2 text-[--w]">About</h1>
  <Breadcrumb items={[{ href: '/about', label: 'About' }]} />

  <!-- Main hero section -->
  <div class="mt-8 rounded-[16px] overflow-hidden relative" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);">
    <!-- Top gradient accent -->
    <div class="absolute inset-x-0 top-0 h-px" style="background: linear-gradient(90deg, transparent, rgba(115,238,7,0.3), transparent);"></div>

    <div class="p-6 md:p-8 flex flex-col md:flex-row gap-8 items-start">
      <!-- Avatar -->
      <div class="flex-shrink-0">
        <div class="w-40 h-40 md:w-48 md:h-48 rounded-[14px] overflow-hidden bg-dark-800 relative">
          {#if about.avatar}
            <img src={about.avatar} alt={about.name} class="w-full h-full object-cover" />
          {:else}
            <div class="w-full h-full flex items-center justify-center" style="background: linear-gradient(135deg, #1a1a1a, #222);">
              <svg class="w-16 h-16 text-dark-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          {/if}
        </div>
      </div>

      <!-- Info -->
      <div class="flex-1">
        <h2 class="font-display text-4xl md:text-5xl tracking-wide text-[--w] mb-3">{about.name}</h2>

        <!-- Genres -->
        <div class="flex flex-wrap gap-2 mb-4">
          {#each about.genres as genre}
            <span class="px-3 py-1 text-[12px] font-medium rounded-full" style="background: rgba(115,238,7,0.1); color: #73EE07; border: 1px solid rgba(115,238,7,0.2);">
              {genre}
            </span>
          {/each}
        </div>

        <p class="text-[14px] leading-relaxed mb-4" style="color: rgba(255,255,255,0.6);">
          Musician from
          <a href="https://en.wikipedia.org/wiki/Yakutsk" target="_blank" rel="noopener" class="text-[--green] hover:underline">{about.city}</a>.
          {about.bio}
        </p>

        <!-- Location -->
        <div class="flex items-center gap-1.5 text-[13px]" style="color: rgba(255,255,255,0.35);">
          <MapPin size={13} />
          <a href="https://en.wikipedia.org/wiki/Sakha_(Republic)" target="_blank" rel="noopener" class="hover:text-[--blue] transition-colors">
            {about.location} 🇷🇺
          </a>
        </div>
      </div>
    </div>
  </div>

  <!-- Grid: contacts + liner notes -->
  <div class="mt-5 grid md:grid-cols-2 gap-4">
    <!-- Contacts -->
    <div class="rounded-[14px] p-5" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);">
      <h3 class="font-display text-lg tracking-wide text-[--w] mb-4">Contact</h3>
      <a
        href="mailto:{about.email}"
        class="flex items-center gap-2.5 text-[13px] hover:text-[--green] transition-colors group"
        style="color: rgba(255,255,255,0.5);"
      >
        <div class="w-7 h-7 rounded-[7px] flex items-center justify-center group-hover:bg-[rgba(115,238,7,0.1)] transition-colors" style="background: rgba(255,255,255,0.05);">
          <Mail size={13} />
        </div>
        {about.email}
      </a>
    </div>

    <!-- Liner notes -->
    <div class="rounded-[14px] p-5" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);">
      <h3 class="font-display text-lg tracking-wide text-[--w] mb-3">Liner Notes</h3>
      <p class="text-[13px] leading-relaxed italic" style="color: rgba(255,255,255,0.45);">"{about.liner_notes}"</p>
    </div>
  </div>

  <!-- Social links -->
  <div class="mt-5 rounded-[14px] p-5" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);">
    <h3 class="font-display text-lg tracking-wide text-[--w] mb-4">Find me on</h3>
    <div class="flex flex-wrap gap-2">
      {#each Object.entries(about.social_links) as [platform, url]}
        {#if url}
          <a
            href={url}
            target="_blank"
            rel="noopener"
            class="flex items-center gap-2 px-4 py-2 rounded-[10px] text-[13px] font-medium transition-all hover:scale-105 hover:-translate-y-0.5"
            style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); color: rgba(255,255,255,0.7);"
          >
            <span>{socialIcons[platform] || '🔗'}</span>
            <span class="capitalize">{platform}</span>
            <ExternalLink size={11} style="color: rgba(255,255,255,0.3);" />
          </a>
        {/if}
      {/each}
    </div>
  </div>
</div>
