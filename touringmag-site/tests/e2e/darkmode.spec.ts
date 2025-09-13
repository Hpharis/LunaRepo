import { test, expect } from '@playwright/test';

test('Dark mode toggle updates body class', async ({ page }) => {
  await page.goto('/');
  await page.click('button:has-text("🌙")');
  const hasDarkMode = await page.evaluate(() => document.body.classList.contains('dark'));
  expect(hasDarkMode).toBeTruthy();
});
