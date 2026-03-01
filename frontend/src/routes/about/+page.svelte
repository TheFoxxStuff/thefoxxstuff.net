<script>
  import { Breadcrumb, SEO } from '$lib/components';
  import { SITE, canonicalUrl } from '$lib/seo.js';
  import { Mail, Send, ExternalLink, MapPin, Calendar, Music } from 'lucide-svelte';

  const about = {
    name: 'TheFoxxStuff',
    realName: 'Айтал Попов (Aital Popov)',
    birthDate: '25.06.2002',
    location: 'Republic of Sakha (Yakutia)',
    locationUrl: 'https://en.wikipedia.org/wiki/Sakha_Republic',
    city: 'Yakutsk',
    genres: ['Hardcore', 'Breakcore', "Drum'n'Bass", 'IDM'],
    bio: `Привет! Я TheFoxxStuff — музыкальный продюсер из холодной Якутии. Родился 25 июня 2002 года в Якутске, и с тех пор музыка стала неотъемлемой частью моей жизни.

Моё творчество — это отражение контрастов: суровая северная природа и внутренняя энергия, тишина бескрайних просторов и взрывная динамика breakcore. Я создаю музыку, которая сочетает в себе агрессивные ритмы hardcore, сложные брейки и атмосферные текстуры, вдохновлённые культурой и природой Якутии.

Каждый трек — это попытка передать ощущение жизни на краю света, где -50°C зимой и белые ночи летом формируют особое мировосприятие. Моя музыка — это мост между традициями Севера и современной электронной культурой.`,

    websiteInfo: `Этот сайт — моё цифровое пространство, где я делюсь своей музыкой, мыслями и творчеством. Здесь вы найдёте все мои релизы, блог о процессе создания музыки, арты и многое другое. Сайт разработан с нуля и постоянно развивается, добавляются новые функции и возможности.`,

    email: 'mail@thefoxxstuff.net',
    telegram: 'https://t.me/thefoxxstuff',

    social_links: {
      bandcamp: 'https://thefoxxstuff.bandcamp.com',
      soundcloud: 'https://soundcloud.com/thefoxxstuff',
      telegram: 'https://t.me/thefoxxstuff',
    }
  };

  const aboutJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Person',
    name: about.name,
    url: SITE.url,
    description: about.bio,
    email: about.email,
    birthDate: '2002-06-25',
    jobTitle: 'Music Producer',
    knowsAbout: about.genres,
    address: {
      '@type': 'PostalAddress',
      addressLocality: about.city,
      addressCountry: 'RU'
    },
    sameAs: Object.values(about.social_links).filter(Boolean)
  };
</script>

<SEO
  title="About"
  description={`TheFoxxStuff (${about.realName}) — music producer from ${about.city}, ${about.location}. Creates ${about.genres.join(', ')} music.`}
  keywords={`${about.name}, about, musician, ${about.genres.join(', ')}, yakutia, yakutsk, aital popov`}
  type="profile"
  url={canonicalUrl('/about')}
  profile={{ username: 'thefoxxstuff' }}
  jsonLd={aboutJsonLd}
/>

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0 mb-20 md:mb-8">
  <h1 class="font-display text-[24px] tracking-wide mb-[8px]">About</h1>
  <Breadcrumb items={[{ href: '/about', label: 'About' }]} />

  <!-- Hero Section -->
  <div class="mt-8 bg-[--w5] rounded-xl p-8 border border-[--w8]">
    <div class="flex flex-col md:flex-row gap-8 items-start">
      <!-- Avatar -->
      <div class="w-full md:w-48 aspect-square bg-gradient-to-br from-[#4ade80] to-[#22d3ee] rounded-xl overflow-hidden flex-shrink-0 flex items-center justify-center">
        <div class="w-full h-full flex items-center justify-center text-[--w] text-6xl font-bold">
          TFS
        </div>
      </div>

      <!-- Main Info -->
      <div class="flex-1">
        <h2 class="font-display text-4xl tracking-wide mb-2 text-[--w]">{about.name}</h2>
        <p class="text-[--w60] text-lg mb-4">{about.realName}</p>

        <div class="flex flex-col gap-2 mb-6">
          <div class="flex items-center gap-2 text-[--w60]">
            <Calendar size={18} />
            <span>{about.birthDate}</span>
          </div>

          <div class="flex items-center gap-2 text-[--w60]">
            <MapPin size={18} />
            <a
              href={about.locationUrl}
              target="_blank"
              rel="noopener noreferrer"
              class="text-[#22d3ee] hover:underline flex items-center gap-1"
            >
              {about.city}, {about.location}
              <ExternalLink size={14} />
            </a>
          </div>

          <div class="flex items-center gap-2 text-[--w60] flex-wrap">
            <Music size={18} />
            {#each about.genres as genre, i}
              <span class="px-2 py-1 bg-[--w8] rounded-md text-sm text-[#4ade80]">{genre}</span>
            {/each}
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Bio Section -->
  <div class="mt-8 bg-[--w5] rounded-xl p-8 border border-[--w8]">
    <h3 class="font-display text-2xl tracking-wide mb-4 text-[--w]">О себе</h3>
    <div class="text-[--w80] leading-relaxed space-y-4 whitespace-pre-line">
      {about.bio}
    </div>
  </div>

  <!-- Website Info -->
  <div class="mt-8 bg-[--w5] rounded-xl p-8 border border-[--w8]">
    <h3 class="font-display text-2xl tracking-wide mb-4 text-[--w]">Об этом сайте</h3>
    <p class="text-[--w80] leading-relaxed">
      {about.websiteInfo}
    </p>
  </div>

  <!-- Contact Section -->
  <div class="mt-8 grid md:grid-cols-2 gap-4">
    <!-- Email -->
    <a
      href={`mailto:${about.email}`}
      class="bg-[--w5] rounded-xl p-6 border border-[--w8] hover:border-[#4ade80] transition-all group"
    >
      <div class="flex items-center gap-3 mb-2">
        <div class="w-10 h-10 rounded-lg bg-[--w8] flex items-center justify-center group-hover:bg-[#4ade80]/20 transition-colors">
          <Mail size={20} class="text-[#4ade80]" />
        </div>
        <div>
          <h4 class="font-semibold text-[--w]">Email</h4>
          <p class="text-sm text-[--w60]">Напишите мне</p>
        </div>
      </div>
      <p class="text-[#4ade80] text-sm">{about.email}</p>
    </a>

    <!-- Telegram -->
    <a
      href={about.telegram}
      target="_blank"
      rel="noopener noreferrer"
      class="bg-[--w5] rounded-xl p-6 border border-[--w8] hover:border-[#22d3ee] transition-all group"
    >
      <div class="flex items-center gap-3 mb-2">
        <div class="w-10 h-10 rounded-lg bg-[--w8] flex items-center justify-center group-hover:bg-[#22d3ee]/20 transition-colors">
          <Send size={20} class="text-[#22d3ee]" />
        </div>
        <div>
          <h4 class="font-semibold text-[--w]">Telegram</h4>
          <p class="text-sm text-[--w60]">Самый быстрый способ связи</p>
        </div>
      </div>
      <p class="text-[#22d3ee] text-sm flex items-center gap-1">
        @thefoxxstuff
        <ExternalLink size={14} />
      </p>
    </a>
  </div>

  <!-- Social Links -->
  <div class="mt-8 bg-[--w5] rounded-xl p-8 border border-[--w8]">
    <h3 class="font-display text-2xl tracking-wide mb-4 text-[--w]">Где меня найти</h3>
    <div class="grid md:grid-cols-3 gap-4">
      {#each Object.entries(about.social_links) as [key, value]}
        {#if value}
          <a
            href={value}
            target="_blank"
            rel="noopener noreferrer"
            class="flex items-center gap-2 px-4 py-3 bg-[--w8] rounded-lg hover:bg-[--w12] transition-colors text-[--w80] hover:text-[--w] group"
          >
            <span class="capitalize font-medium">{key}</span>
            <ExternalLink size={14} class="opacity-0 group-hover:opacity-100 transition-opacity" />
          </a>
        {/if}
      {/each}
    </div>
  </div>
</div>