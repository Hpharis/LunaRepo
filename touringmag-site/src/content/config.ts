// const blog = defineCollection({
  // type: "content",
 //  schema: z.object({
  //   title: z.string(),
  //   summary: z.string().optional(),
 //    pubDate: z.coerce.date(),
  //   heroImage: z.string().optional(),
//  }),
//  });

import { defineCollection, z } from "astro:content";

const blog = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    summary: z.string().optional(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    heroImage: z.string().optional(),
	thumbnail: z.string().optional(),        // add this
    affiliateLink: z.string().optional(),    // allow injected links
    tags: z.array(z.string()).optional(),
  }),
});

const gear = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    summary: z.string().optional(),
    pubDate: z.coerce.date(),
    heroImage: z.string().optional(),
    rating: z.number().min(1).max(5).optional(), // ⭐ for reviews
	thumbnail: z.string().optional(),        // add this
    affiliateLink: z.string().optional(),
  }),
});

const upgrades = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    summary: z.string().optional(),
    pubDate: z.coerce.date(),
    heroImage: z.string().optional(),
	thumbnail: z.string().optional(),        // add this
    tags: z.array(z.string()).optional(),
	affiliateLink: z.string().optional(),    // allow injected links
  }),
});

const guides = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    summary: z.string().optional(),
    pubDate: z.coerce.date(),
    heroImage: z.string().optional(),
	thumbnail: z.string().optional(),        // add this
    difficulty: z.enum(["Beginner", "Intermediate", "Advanced"]).optional(),
  }),
});

export const collections = { blog, gear, upgrades, guides };
