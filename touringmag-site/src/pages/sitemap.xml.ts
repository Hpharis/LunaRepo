import { getCollection } from 'astro:content';

export async function GET() {
  const posts = await getCollection('blog');
  const urls = posts.map((post) => `
    <url>
      <loc>https://touringmag.com/articles/${post.slug}</loc>
      <lastmod>${post.data.date}</lastmod>
    </url>
  `).join('');

  return new Response(
    `<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <url><loc>https://touringmag.com/</loc></url>
      ${urls}
    </urlset>`,
    { headers: { "Content-Type": "application/xml" } }
  );
}
