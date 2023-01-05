import { defineConfig } from 'astro/config';
import { useSanityClient } from 'astro-sanity';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
import sanity from "astro-sanity";

// https://astro.build/config
export default defineConfig({
  site: 'https://localhost:3000',
  integrations: [mdx(), sitemap(), sanity( {
    projectId: 'ndh6wvwa',
    dataset: 'production',
    apiVersion: '2021-03-25',
    useCdn: true,
})]
});