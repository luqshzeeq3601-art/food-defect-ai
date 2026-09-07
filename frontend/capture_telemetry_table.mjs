import { chromium } from 'playwright-core';
import path from 'path';

async function main() {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 950 }, deviceScaleFactor: 2 });
  await page.goto('http://localhost:5173');
  await page.waitForTimeout(1000);

  const samples = [
    'Active Rot & Decay (REJECT)',
    'Cosmetic Blemish (GRADE B)',
    'Pristine Produce (GRADE A)',
    'Empty Conveyor Belt (NO OBJECT)',
  ];

  for (const name of samples) {
    const btn = page.locator('button:has-text("preset sample library"), button:has-text("Sample Library")').first();
    await btn.click();
    await page.waitForTimeout(600);

    const inspectPromise = page.waitForResponse(
      (r) => r.url().includes('/api/v1/inspect') && r.status() === 200,
      { timeout: 15000 }
    );
    await page.locator(`img[alt="${name}"]`).click();
    await inspectPromise;
    await page.waitForTimeout(800);
  }

  const auditCard = page.locator('#audit-log-card');
  if (await auditCard.isVisible()) {
    await auditCard.scrollIntoViewIfNeeded();
    await page.waitForTimeout(600);
    await page.screenshot({ path: path.resolve('../screenshots/05_proof_session_telemetry_table.png') });
    console.log('Session telemetry table captured!');
  }

  await browser.close();
}

main().catch(console.error);
