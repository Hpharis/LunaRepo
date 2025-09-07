// astro.config.mjs
// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import vercel from '@astrojs/vercel'; // ✅ correct import (no "/serverless")

export default defineConfig({
  site: 'https://touringmag.com',
  integrations: [mdx(), sitemap()],
  adapter: vercel(),
  // output: 'server', // optional; 'server' is the default
});
