const path = require("path"),
  fs = require("fs");
let playwright;
try {
  playwright = require("playwright");
} catch {
  playwright = require(
    process.env.PLAYWRIGHT_MODULE ||
      "/opt/codex/cua_node/lib/node_modules/playwright",
  );
}
(async () => {
  const browser = await playwright.chromium.launch({
    executablePath: process.env.CHROMIUM_BIN || "/usr/bin/chromium",
    args: [
      "--no-sandbox",
      "--use-gl=angle",
      "--use-angle=swiftshader",
      "--enable-unsafe-swiftshader",
    ],
  });
  try {
    const page = await browser.newPage({
        viewport: { width: 390, height: 844 },
        reducedMotion: "reduce",
      }),
      errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    page.on("console", (m) => {
      if (m.type() === "error") errors.push(m.text());
    });
    const out = path.resolve(__dirname, "../docs/screenshots");
    fs.mkdirSync(out, { recursive: true });
    await page.goto(process.env.BASE_URL || "http://127.0.0.1:8091");
    await page.waitForFunction(() => window.__DOKDO__);
    await page.screenshot({ path: path.join(out, "title-mobile.png") });
    await page.click("#startGame");
    await page.click('[data-act="close"]');
    await page.waitForTimeout(200);
    await page.screenshot({ path: path.join(out, "harbor-mobile.png") });
    await page.click("#depart");
    await page.mouse.move(170, 430);
    await page.mouse.down();
    await page.mouse.move(120, 490, { steps: 8 });
    await page.waitForTimeout(1000);
    await page.mouse.up();
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(out, "sailing-mobile.png") });
    await page.evaluate(() => {
      const g = window.__DOKDO__.game;
      g.state.levels.body = 10;
      g.state.levels.cannon = 50;
      g.state.flag = 1;
      g.state.hp = g.stats.hp;
      g.state.x = 110;
      g.state.z = 110;
      g.stop();
      window.__DOKDO__.view.initialized = false;
      g.maintainEnemies();
    });
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(out, "late-ship-mobile.png") });
    const desktop = await browser.newPage({
      viewport: { width: 1100, height: 850 },
    });
    desktop.on("pageerror", (e) => errors.push(e.message));
    await desktop.goto(process.env.BASE_URL || "http://127.0.0.1:8091");
    await desktop.waitForFunction(() => window.__DOKDO__);
    await desktop.click("#startGame");
    await desktop.click('[data-act="close"]');
    await desktop.screenshot({ path: path.join(out, "harbor-desktop.png") });
    const report = await page.evaluate(() => ({
      font: document.fonts.check(
        "450 16px DokdoKorean",
        "독도까지 똠방각하 힣",
      ),
      width: document.body.scrollWidth,
      reflectionCount: window.__DOKDO__.view.reflections.size,
      geometries: window.__DOKDO__.view.renderer.info.memory.geometries,
    }));
    console.log(JSON.stringify({ errors, ...report }, null, 2));
    if (errors.length) process.exitCode = 1;
  } finally {
    await browser.close();
  }
})();
