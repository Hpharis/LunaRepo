// scripts/generate-post.js
import Database from "better-sqlite3";
import OpenAI from "openai";
import "dotenv/config";

// ✅ Connect to SQLite DB (relative to project root)
const db = new Database("goldloop.db");

// ✅ Make sure posts table exists
db.exec(`
CREATE TABLE IF NOT EXISTS posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  summary TEXT,
  heroImage TEXT,
  content TEXT NOT NULL,
  createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
)
`);

// ✅ Setup OpenAI client
if (!process.env.OPENAI_API_KEY) {
  console.error("❌ Missing OPENAI_API_KEY environment variable.");
  process.exit(1);
}

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

async function generatePost() {
  const prompt = `
    Write a blog post about a Harley-Davidson touring upgrade for 2025.
    Include:
    Title: (catchy, max 12 words)
    Summary: (1-sentence overview)
    Body: (3–5 paragraphs, valid HTML using <h2>, <p>, <ul>, <li>)
  `;

  console.log("🤖 Requesting AI-generated post from OpenAI...");

  const response = await client.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: prompt }],
  });

  const content = response.choices[0].message.content;

  // ✅ Parse AI output
  const titleMatch = content.match(/Title:(.*)/i);
  const summaryMatch = content.match(/Summary:(.*)/i);

  const title = titleMatch ? titleMatch[1].trim() : "Harley-Davidson Touring Upgrade 2025";
  const summary = summaryMatch ? summaryMatch[1].trim() : "Discover the latest Harley-Davidson upgrade for 2025.";
  const body = content; // store full content, including <h2>, <p>, etc.

  const slug = title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");

  // ✅ Insert into DB
  const stmt = db.prepare(`
    INSERT OR IGNORE INTO posts (slug, title, summary, heroImage, content)
    VALUES (@slug, @title, @summary, @heroImage, @content)
  `);

  const result = stmt.run({
    slug,
    title,
    summary,
    heroImage: "/assets/blog-placeholder-1.jpg",
    content: body,
  });

  if (result.changes > 0) {
    console.log(`✅ Post inserted: ${slug} | ${title}`);
  } else {
    console.log(`⚠️ Skipped (already exists): ${slug}`);
  }
}

generatePost().catch((err) => {
  console.error("❌ Error generating post:", err);
  process.exit(1);
});
