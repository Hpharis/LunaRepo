import { defineCollection, z } from "astro:content";

const baseFields = {
  title: z.string(),
  summary: z.string().optional(),
  pubDate: z.coerce.date(),
  updatedDate: z.coerce.date().optional(),
  heroImage: z.string().optional(),
  thumbnail: z.string().optional(),       // added
  affiliateLink: z.string().optional(),   // added
  tags: z.array(z.string()).optional(),   // shared
  author: z.string().optional(),
  role: z.string().optional(),
  editorComment: z.string().optional(),   // persona comments
};

const blog = defineCollection({
  type: "content",
  dir: "blog", // 
  schema: z.object(baseFields),
});

const gear = defineCollection({
  type: "content",
  dir: "gear",
  schema: z.object({
    ...baseFields,
    rating: z.number().min(1).max(5).optional(), // ⭐ reviews
  }),
});

const upgrades = defineCollection({
  type: "content",
  dir: "upgrades",
  schema: z.object(baseFields),
});

const guides = defineCollection({
  type: "content",
  dir: "guides",
  schema: z.object({
    ...baseFields,
    difficulty: z.enum(["Beginner", "Intermediate", "Advanced"]).optional(),
  }),
});

export const collections = { blog, gear, upgrades, guides };
