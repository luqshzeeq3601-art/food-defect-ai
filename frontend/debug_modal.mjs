import { chromium } from 'playwright-core';

async function main() {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 950 } });
  page.on('console', msg => console.log('BROWSER CONSOLE:', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('BROWSER ERROR:', err.message));
  page.on('request', req => console.log('REQ:', req.method(), req.url()));
  page.on('response', res => console.log('RES:', res.status(), res.url()));

  await page.goto('http://localhost:5173');
  await page.waitForTimeout(2000);

  const sampleBtn = page.locator('button:has-text("preset sample library"), button:has-text("Sample Library"), button:has-text("Samples")').first();
  console.log('Sample button visible:', await sampleBtn.isVisible());
  await sampleBtn.click();
  await page.waitForTimeout(1000);

  const images = page.locator('.fixed img');
  const count = await images.count();
  console.log('Modal images count:', count);
  for (let i = 0; i < count; i++) {
    console.log('Image', i, 'alt:', await images.nth(i).getAttribute('alt'));
  }

  // Click the first one
  console.log('Clicking first image...');
  await images.first().click();
  await page.waitForTimeout(4000);

  await page.screenshot({ path: '../screenshots/debug_after_click.png' });
  await browser.close();
}

main().catch(console.error);
