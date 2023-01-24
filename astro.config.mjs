import { defineConfig } from 'astro/config';
import { useSanityClient } from 'astro-sanity';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import sanity from "astro-sanity";
import cloudflare from "@astrojs/cloudflare";

import netlify from "@astrojs/netlify/functions";

// https://astro.build/config
export default defineConfig({
  site: 'https://thefoxxstuff-net.pages.dev',
  integrations: [mdx(), sitemap(), sanity({
    projectId: 'ndh6wvwa',
    dataset: 'production',
    apiVersion: '2021-03-25',
    useCdn: true
  })],
  output: 'server' // adapter: cloudflare()
  ,
  adapter: netlify()
});