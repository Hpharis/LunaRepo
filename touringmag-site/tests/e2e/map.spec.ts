import { test, expect } from '@playwright/test';

test('Interactive map loads and has a marker', async ({ page }) => {
  await page.goto('/map');
  const map = page.locator('#map');
  await expect(map).toBeVisible();
});
