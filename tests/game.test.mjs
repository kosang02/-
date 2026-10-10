import test from "node:test";
import assert from "node:assert/strict";
import { Game, R, WORLD, initialState, validateState } from "../dist/engine.js";
const game = () => {
  const g = new Game(null, { random: () => 0.5, now: () => 100000 });
  g.state.started = true;
  return g;
};
test("world and initial state match researched numerical data", () => {
  const g = game();
  assert.equal(WORLD.islands.length, 47);
  assert.equal(g.islands.length, 28);
  assert.deepEqual(g.state.resources, [500, 0, 0, 0, 0, 0, 0]);
  assert.equal(g.stats.hp, 40);
  assert.equal(R.maxUpgradeLevel("body", 10), 10);
  assert.equal(R.maxUpgradeLevel("sail", 10), 50);
  assert.deepEqual(R.upgradeCost("body", 1), [600, 0, 20, 0, 0, 0, 0]);
});
test("all upgrade levels have nonnegative finite costs", () => {
  for (const k of Object.keys(R.UPGRADE_KO))
    for (let l = 1; l < (k === "body" ? 10 : 50); l++) {
      const c = R.upgradeCost(k, l);
      assert.equal(c.length, 7);
      assert.ok(
        c.every((n) => Number.isFinite(n) && Number.isInteger(n) && n >= 0),
      );
      assert.ok(c.some((n) => n > 0));
    }
});
test("upgrade spends exact resources and enforces hull unlock", () => {
  const g = game();
  assert.equal(g.upgrade("body"), false);
  g.state.resources = Array(7).fill(1e8);
  assert.equal(g.upgrade("body"), true);
  assert.equal(g.state.resources[0], 1e8 - 600);
  assert.equal(g.state.resources[2], 1e8 - 20);
  g.state.levels.sail = 10;
  assert.equal(g.upgrade("sail"), false);
  g.upgrade("body");
  assert.equal(g.upgrade("sail"), true);
  g.depart();
  assert.equal(g.upgrade("sail"), false);
});
test("market never produces negative balance and resets stock", () => {
  const g = game();
  assert.equal(g.trade(2, true, 999999), 13);
  assert.equal(g.state.resources[0], 32);
  assert.equal(g.stock()[1], 87);
  assert.equal(g.trade(2, false, 999999), 13);
  assert.equal(g.state.resources[0], 448);
  assert.equal(g.state.resources[2], 0);
  g.now = () => 800001;
  assert.equal(g.stock()[1], 100);
});
test("guards are not respawned after out-of-order kills; island captures", () => {
  const g = game(),
    a = WORLD.islands[1];
  g.depart();
  g.state.x = a.port.x;
  g.state.z = a.port.z;
  g.maintainEnemies();
  const es = g.enemies.filter((e) => e.home === a.id);
  assert.equal(es.length, a.enemyCount);
  g.defeat(es.at(-1));
  g.enemies = g.enemies.filter((e) => !e.dead);
  g.maintainEnemies();
  assert.equal(
    g.enemies.filter((e) => e.home === a.id).length,
    a.enemyCount - 1,
  );
  for (const e of g.enemies.filter((e) => e.home === a.id)) g.defeat(e);
  g.enemies = g.enemies.filter((e) => !e.dead);
  g.undockTimer = 0;
  g.tick(0.01);
  assert.ok(g.owned.includes(a.id));
  assert.equal(g.state.docked, a.id);
});
test("leaving island radius resets remaining guard group", () => {
  const g = game(),
    a = WORLD.islands[1];
  g.depart();
  Object.assign(g.state, a.port);
  g.maintainEnemies();
  g.defeat(g.enemies.find((e) => e.home === a.id));
  g.state.x += 500;
  g.maintainEnemies();
  assert.equal(g.state.kills[a.id], 0);
  assert.ok(!g.enemies.some((e) => e.home === a.id));
});
test("fishing, docking, repair and save restoration", () => {
  const g = game();
  g.depart();
  g.undockTimer = 0;
  const p = WORLD.islands[0].port;
  g.state.x = p.x - 15;
  g.state.z = p.z - 15;
  for (let i = 0; i < 105; i++) g.tick(0.1);
  assert.ok(g.state.resources[1] > 0);
  g.state.x = p.x;
  g.state.z = p.z;
  assert.equal(g.dock(0), true);
  g.state.hp = 1;
  for (let i = 0; i < 21; i++) g.tick(0.1);
  assert.ok(g.state.hp > 1);
  const clone = new Game(g.snapshot());
  assert.deepEqual(clone.state.resources, g.state.resources);
  assert.equal(clone.state.docked, 0);
});
test("world transition preserves resources and has valid saves", () => {
  const g = game();
  g.changeWorld();
  assert.equal(g.state.world, 1);
  assert.equal(g.islands.length, 19);
  assert.equal(g.state.docked, 28);
  assert.doesNotThrow(() => validateState(g.snapshot()));
  g.depart();
  assert.equal(g.changeWorld(), false);
});
test("invalid imports rejected", () => {
  const s = initialState();
  s.resources[0] = -1;
  assert.throws(() => validateState(s));
  const t = initialState();
  t.levels.cannon = 51;
  assert.throws(() => validateState(t));
  const u = initialState();
  u.lastIsland = 900;
  assert.throws(() => validateState(u));
});
test("arena wave, reward and resurrection", () => {
  const g = game();
  g.startArena();
  for (let i = 0; i < 21; i++) g.tick(0.1);
  assert.equal(g.enemies.length, 7);
  for (const e of g.enemies) g.defeat(e);
  const before = g.state.resources[0];
  g.finishArena();
  assert.equal(g.state.resources[0], before + R.arenaReward(7));
  assert.equal(g.state.arenaBest, 7);
  g.dead = true;
  g.state.hp = 0;
  assert.equal(g.revive(true), true);
  assert.equal(g.state.revivals, 2);
  assert.equal(g.state.hp, g.stats.hp);
});
test("companions charge full price and obey cap", () => {
  const g = game();
  assert.equal(g.companion("assistant", 0), false);
  g.state.resources[0] = 1e7;
  g.companion("assistant", 0);
  assert.equal(g.state.assistants[0], 1);
  assert.equal(g.state.resources[0], 9900000);
  g.companion("assistant", 0);
  assert.equal(g.state.resources[0], 9880000);
  g.state.assistants[0] = 50;
  assert.equal(g.companion("assistant", 0), false);
});
