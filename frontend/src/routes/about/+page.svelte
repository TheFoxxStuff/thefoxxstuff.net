<script>
  import { Breadcrumb, SEO } from '$lib/components';
  import { SITE, canonicalUrl } from '$lib/seo.js';

  const about = {
    name: 'TheFoxxStuff',
    location: 'Republic of Sakha (Yakutia)',
    city: 'Yakutsk',
    genres: ['Hardcore', 'Breakcore', "Drum'n'Bass"],
    bio: 'He has his own distinctive sound shaped by the atmosphere of the North. Growing up in Yakutia and being immersed in its culture gives his music a specific emotional depth, combining cold пространства с внутренней энергией и динамикой.',
    avatar: null, // например: '/about.jpg'
    email: 'mail@thefoxxstuff.net',
    social_links: {
      bandcamp: 'https://thefoxxstuff.bandcamp.com',
      soundcloud: 'https://soundcloud.com/thefoxxstuff',
      twitter: 'https://twitter.com/thefoxxstuff',
      vk: 'https://vk.com/thefoxxstuff',
      telegram: 'https://t.me/thefoxxstuff'
    },
    liner_notes:
      "So I spent a few hours in this world, until I felt it was time to return to reality. I opened my eyes and felt that my mind was cleansed and filled with new knowledge. I was ready for new challenges in life, knowing that the world where summer reigns will always be with me."
  };

  const aboutJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Person',
    name: about.name,
    url: SITE.url,
    description: about.bio,
    email: about.email,
    ...(about.avatar && { image: `${SITE.url}${about.avatar}` }),
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
  description={`TheFoxxStuff — music producer from ${about.city}, ${about.location}. Creates ${about.genres.join(', ')} music.`}
  keywords={`${about.name}, about, musician, ${about.genres.join(', ')}, yakutia, yakutsk`}
  image={about.avatar ? `${SITE.url}${about.avatar}` : undefined}
  imageAlt="TheFoxxStuff"
  type="profile"
  url={canonicalUrl('/about')}
  profile={{ username: 'thefoxxstuff' }}
  jsonLd={aboutJsonLd}
/>

<div class="mx-auto max-w-6xl px-4 pt-[20px] pb-8 min-[829px]:max-w-[828px] min-[829px]:px-0">
  <h1 class="font-display text-[24px] tracking-wide mb-[8px]">About</h1>
  <Breadcrumb items={[{ href: '/about', label: 'About' }]} />

  <div class="mt-8 flex flex-col md:flex-row gap-8">
    <div class="w-full md:w-80 aspect-square bg-dark-800 rounded-xl overflow-hidden flex-shrink-0">
      {#if about.avatar}
        <img src={about.avatar} alt={about.name} class="w-full h-full object-cover" />
      {:else}
        <div class="w-full h-full flex items-center justify-center text-dark-600">
          <svg class="w-24 h-24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
      {/if}
    </div>

    <div class="flex-1">
      <h2 class="font-display text-4xl tracking-wide mb-4">{about.name}</h2>

      <p class="text-dark-300 mb-6">
        Musician from
        <a
          href="https://en.wikipedia.org/wiki/Yakutsk"
          target="_blank"
          rel="noopener noreferrer"
          class="text-accent-green hover:underline"
        >
          {about.city}
        </a>
        who creates music in the genres of
        {#each about.genres as genre, i}
          <span class="text-accent-green">{genre}</span>{#if i < about.genres.length - 1}{i === about.genres.length - 2 ? ' and ' : ', '}{/if}
        {/each}.
        {about.bio}
      </p>

      <p class="text-dark-400 flex items-center gap-2">
        <span class="w-6 h-4 inline-flex items-center justify-center text-xs">🇷🇺</span>
        <a
          href="https://en.wikipedia.org/wiki/Sakha_(Republic)"
          target="_blank"
          rel="noopener noreferrer"
          class="text-accent-cyan hover:underline"
        >
          {about.location}
        </a>
      </p>
    </div>
  </div>

  <div class="mt-12 grid md:grid-cols-2 gap-8">
    <section>
      <h3 class="font-display text-2xl tracking-wide mb-4">Contacts</h3>
      <p class="text-dark-400">
        Email:
        <a
          href={`mailto:${about.email}`}
          class="text-accent-green hover:underline"
        >
          {about.email}
        </a>
      </p>
    </section>

    <section>
      <h3 class="font-display text-2xl tracking-wide mb-4">Liner Notes</h3>
      <p class="text-dark-300 italic">{about.liner_notes}</p>
    </section>
  </div>

  <section class="mt-8">
    <h4 class="text-sm text-dark-500 mb-3">Follow me:</h4>
    <div class="space-y-2 text-sm">
      {#each Object.entries(about.social_links) as [key, value]}
        {#if value}
          <p>
            ►{key.toUpperCase()}:
            <a
              href={value}
              target="_blank"
              rel="noopener noreferrer"
              class="text-accent-green hover:underline"
            >
              {value.replace('https://', '')}
            </a>
          </p>
        {/if}
      {/each}
    </div>
  </section>
</div>