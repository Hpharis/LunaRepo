import { test, expect } from '@playwright/test';

test('Route Builder returns recommended gear', async ({ page }) => {
  await page.goto('/routes');
  await page.fill('input[name="start"]', 'Halifax');
  await page.fill('input[name="end"]', 'Montreal');
  await page.click('button[type=submit]');
  await expect(page.getByRole('heading', { name: /Recommended Gear/i })).toBeVisible();
});
