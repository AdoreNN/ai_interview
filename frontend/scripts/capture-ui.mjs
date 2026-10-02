import { chromium } from "playwright";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 960 }, deviceScaleFactor: 1 });

await page.goto("http://127.0.0.1:3000", { waitUntil: "networkidle" });
await page.screenshot({ path: "/tmp/grillo-auth-desktop.png", fullPage: true });

await page.getByRole("button", { name: "Посмотреть демо" }).click();
await page.screenshot({ path: "/tmp/grillo-interview-desktop.png", fullPage: true });

await page.getByRole("button", { name: "Новое интервью" }).click();
await page.screenshot({ path: "/tmp/grillo-setup-desktop.png", fullPage: true });

await page.setViewportSize({ width: 390, height: 844 });
await page.waitForTimeout(350);
await page.screenshot({ path: "/tmp/grillo-setup-mobile.png", fullPage: true });

await page.getByRole("button", { name: "Открыть меню" }).click();
await page.waitForTimeout(250);
await page.screenshot({ path: "/tmp/grillo-menu-mobile.png", fullPage: true });

await page.getByRole("button", { name: "Закрыть меню", exact: true }).last().click();
await page.waitForTimeout(250);

await page.reload({ waitUntil: "networkidle" });
await page.getByRole("button", { name: "Посмотреть демо" }).click();
await page.waitForTimeout(250);
await page.screenshot({ path: "/tmp/grillo-interview-mobile.png", fullPage: true });

await browser.close();
console.log("UI screenshots captured");
