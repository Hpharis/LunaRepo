import { getCollection } from "astro:content";
import rss from "@astrojs/rss";
import { SITE_DESCRIPTION, SITE_TITLE } from "../consts";

export async function GET(context) {
  const collections = ["blog", "gear", "guides", "upgrades"];

  // Gather all posts from all collections
  const posts = (
    await Promise.all(collections.map((c) => getCollection(c)))
  ).flat();

  // Sort newest first
  posts.sort(
    (a, b) => new Date(b.data.pubDate).getTime() - new Date(a.data.pubDate).getTime()
  );

  return rss({
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
    site: context.site,
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.summary,
      pubDate: post.data.pubDate,
      link: `/${post.collection}/${post.slug}/`, // ✅ dynamic link
    })),
  });
}


