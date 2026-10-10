const { chromium } = require("/opt/codex/cua_node/lib/node_modules/playwright");
(async () => {
  const b = await chromium.launch({
    executablePath: "/usr/bin/chromium",
    args: [
      "--no-sandbox",
      "--use-gl=angle",
      "--use-angle=swiftshader",
      "--enable-unsafe-swiftshader",
    ],
  });
  try {
    const p = await b.newPage({ viewport: { width: 390, height: 844 } }),
      errors = [],
      requests = [];
    p.on("pageerror", (e) => errors.push(e.message));
    p.on("request", (r) => {
      if (/^https?:/.test(r.url())) requests.push(r.url());
    });
    await p.context().setOffline(true);
    await p.setContent(
      require("fs").readFileSync(
        "/workspace/library-files/dokdo-korean.html",
        "utf8",
      ),
    );
    await p.waitForFunction(() => window.__DOKDO__);
    await p.click("#startGame");
    await p.click('[data-act="close"]');
    await p.screenshot({
      path: "/workspace/sites/dokdo-korean/offline-mobile.png",
    });
    await p.click("#depart");
    const before = await p.evaluate(() => ({ ...window.__DOKDO__.game.state }));
    await p.mouse.move(195, 350);
    await p.mouse.down();
    await p.mouse.move(250, 310, { steps: 6 });
    await p.waitForTimeout(800);
    await p.mouse.up();
    const moved = await p.evaluate(
      (s) =>
        Math.hypot(
          window.__DOKDO__.game.state.x - s.x,
          window.__DOKDO__.game.state.z - s.z,
        ),
      before,
    );
    if (moved < 0.5) throw Error("Drag failed");
    await p.evaluate(() => {
      const g = window.__DOKDO__.game;
      g.returnToPort();
      g.changeWorld();
      window.__DOKDO__.view.initialized = false;
      window.__DOKDO__.paint();
    });
    await p.waitForTimeout(300);
    await p.screenshot({
      path: "/workspace/sites/dokdo-korean/pisa-mobile.png",
    });
    console.log(
      JSON.stringify(
        {
          errors,
          networkRequests: requests,
          fontReady: await p.evaluate(() =>
            document.fonts.check("450 16px DokdoKorean", "갃똠힣 독도까지"),
          ),
          dragDistance: moved,
          world: await p.evaluate(() => window.__DOKDO__.game.state.world),
        },
        null,
        2,
      ),
    );
    if (errors.length || requests.length) process.exitCode = 1;
  } finally {
    await b.close();
  }
})();
