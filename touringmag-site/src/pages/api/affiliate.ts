export const prerender = false;

import type { APIRoute } from "astro";
import fs from "fs";
import path from "path";

// Load affiliate link map from CSV (Keyword, URL)
function loadAffiliateLinks() {
  const csvPath = path.join(process.cwd(), "..", "goldloop", "data", "affiliate_links.csv");
  const text = fs.readFileSync(csvPath, "utf-8");
  const lines = text.split("\n").slice(1); // skip header
  const map: [string, string][] = [];
  for (const line of lines) {
    const [keyword, url] = line.split(",");
    if (keyword && url) map.push([keyword.trim(), url.trim()]);
  }
  return map;
}

function injectLinks(html: string, linkMap: [string, string][]) {
  let result = html;
  for (const [keyword, url] of linkMap) {
    const pattern = new RegExp(
      `\\b(${keyword})(s|es)?\\b`,
      "gi"
    );
    result = result.replace(
      pattern,
      `<a href="${url}" target="_blank" rel="noopener noreferrer">$1$2</a>`
    );
  }
  return result;
}

export const POST: APIRoute = async ({ request }) => {
  const body = await request.json();
  const html = body.html || "";
  const linkMap = loadAffiliateLinks();
  const enhanced = injectLinks(html, linkMap);
  return new Response(enhanced, {
    headers: { "Content-Type": "text/html" },
  });
};
