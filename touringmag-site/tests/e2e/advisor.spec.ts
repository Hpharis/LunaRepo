import { test, expect } from '@playwright/test';

test('Gear Advisor responds with fallback message', async ({ page }) => {
  await page.goto('/advisor');
  await page.fill('input[name=query]', 'random');
  await page.click('button');
  await expect(page.locator('.advisor')).toContainText('No match found');
});
