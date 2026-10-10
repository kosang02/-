const { chromium } = require("/opt/codex/cua_node/lib/node_modules/playwright");
(async () => {
  const browser = await chromium.launch({
    executablePath: "/usr/bin/chromium",
    headless: true,
    args: [
      "--no-sandbox",
      "--use-gl=angle",
      "--use-angle=swiftshader",
      "--enable-unsafe-swiftshader",
    ],
  });
  const page = await browser.newPage({
    viewport: { width: 1100, height: 850 },
  });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(m.text());
  });
  await page.goto("http://127.0.0.1:8091");
  await page.waitForFunction(() => window.__DOKDO__);
  await page.screenshot({ path: "/workspace/sites/dokdo-korean/title.png" });
  await page.click("#startGame");
  await page.click('[data-act="close"]');
  await page.waitForTimeout(500);
  await page.screenshot({
    path: "/workspace/sites/dokdo-korean/port-desktop.png",
  });
  await page.click('[data-tab="market"]');
  await page.click('[data-trade="2"][data-buy="1"]');
  await page.click('[data-trade="2"][data-buy="1"]');
  await page.click('[data-tab="upgrade"]');
  await page.click('[data-upgrade="cannon"]');
  const level = await page.evaluate(
    () => window.__DOKDO__.game.state.levels.cannon,
  );
  if (level !== 2) throw Error("Market + cannon upgrade failed");
  await page.click("#openMap");
  await page.screenshot({
    path: "/workspace/sites/dokdo-korean/map-desktop.png",
  });
  await page.click('[data-target="1"]');
  await page.waitForTimeout(2000);
  await page.screenshot({
    path: "/workspace/sites/dokdo-korean/sailing-desktop.png",
  });
  const before = await page.evaluate(() => ({
    x: window.__DOKDO__.game.state.x,
    z: window.__DOKDO__.game.state.z,
  }));
  await page.keyboard.down("ArrowRight");
  await page.waitForTimeout(1000);
  await page.keyboard.up("ArrowRight");
  const after = await page.evaluate(() => ({
    x: window.__DOKDO__.game.state.x,
    z: window.__DOKDO__.game.state.z,
  }));
  if (Math.hypot(before.x - after.x, before.z - after.z) < 1)
    throw Error("Keyboard did not navigate");
  await page.evaluate(() => window.__DOKDO__.save());
  await page.reload();
  await page.waitForFunction(() => window.__DOKDO__);
  await page.click("#startGame");
  if (
    (await page.evaluate(() => window.__DOKDO__.game.state.levels.cannon)) !== 2
  )
    throw Error("Save not restored");
  await page.evaluate(() => window.__DOKDO__.game.returnToPort());
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(500);
  await page.screenshot({
    path: "/workspace/sites/dokdo-korean/port-mobile.png",
  });
  await page.click("#openSettings");
  await page.screenshot({
    path: "/workspace/sites/dokdo-korean/settings-mobile.png",
  });
  console.log(
    JSON.stringify(
      {
        errors,
        font: await page.evaluate(() =>
          document.fonts.check(
            "450 16px DokdoKorean",
            "독도까지 선착장 낚시 강화",
          ),
        ),
        bodyWidth: await page.evaluate(() => document.body.scrollWidth),
      },
      null,
      2,
    ),
  );
  await browser.close();
  if (errors.length) process.exitCode = 1;
})();
