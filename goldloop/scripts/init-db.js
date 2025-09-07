const Database = require("better-sqlite3");

const db = new Database("goldloop.db");

// Create posts table if it doesn't exist
db.exec(`
CREATE TABLE IF NOT EXISTS posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  summary TEXT,
  heroImage TEXT,
  content TEXT NOT NULL,
  createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
);
`);

// Insert a test post
db.prepare(`
INSERT OR IGNORE INTO posts (slug, title, summary, heroImage, content)
VALUES (@slug, @title, @summary, @heroImage, @content)
`).run({
  slug: "performance-upgrades-2025",
  title: "Top 5 Harley-Davidson Performance Upgrades for 2025",
  summary: "Explore the top 5 performance upgrades to enhance your Harley-Davidson ride in 2025.",
  heroImage: "/assets/motorcycle-459594_1280.jpg",
  content: "<p>This is the <strong>HTML content</strong> for the performance upgrades article.</p>"
});

console.log("✅ Database initialized and seeded: goldloop.db");


