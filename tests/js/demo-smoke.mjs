// Boots the compiled browser demo against a minimal DOM/localStorage stub.
// This is not a rendering test; it proves the assembled bundle executes, every
// route renders, and a write goes through the real request pipeline.
import test from "node:test";
import assert from "node:assert/strict";

test("browser demo boots, routes, and writes", async () => {
  const store = new Map();
  const nodes = new Map();
  const node = (id) => {
    if (!nodes.has(id)) {
      nodes.set(id, {
        id,
        innerHTML: "",
        value: "",
        checked: false,
        addEventListener() {},
        getAttribute() {
          return null;
        },
      });
    }
    return nodes.get(id);
  };

  globalThis.window = {
    localStorage: {
      getItem: (key) => (store.has(key) ? store.get(key) : null),
      setItem: (key, value) => store.set(key, value),
      removeItem: (key) => store.delete(key),
    },
    location: { hash: "", reload() {} },
    addEventListener() {},
    setTimeout() {},
    scrollTo() {},
  };
  globalThis.document = { body: { addEventListener() {} }, getElementById: node };
  if (!globalThis.crypto) {
    globalThis.crypto = { randomUUID: () => `stub-${store.size}-${Date.now()}` };
  }

  const demo = await import("../../build/demo.mjs");

  assert.match(node("nav").innerHTML, /Stock/);
  assert.match(node("app").innerHTML, /On hand/);
  assert.match(node("app").innerHTML, /Recent movements/);
  assert.ok(store.has("mynastock:v1"), "demo should persist seeded state");

  const routes = [
    ["#/stock", /Post a movement/],
    ["#/movements", /Append-only ledger/],
    ["#/products", /Add a product/],
    ["#/reorder", /Suggested quantity/],
    ["#/behind", /Behind the demo/],
    ["#/nope", /Page not found/],
  ];
  for (const [hash, expected] of routes) {
    globalThis.window.location.hash = hash;
    demo.render();
    assert.match(node("app").innerHTML, expected, `route ${hash}`);
  }

  const before = JSON.parse(demo.api_get("/api/v1/stock", {}).body).items
    .reduce((sum, row) => sum + row.on_hand, 0);

  const response = demo.post_move("receive", "WID-001", "WH1", "", 5, null, "");
  assert.equal(response.status, 201);

  const after = JSON.parse(demo.api_get("/api/v1/stock", {}).body).items
    .reduce((sum, row) => sum + row.on_hand, 0);
  assert.equal(after, before + 5);
  assert.ok(store.get("mynastock:v1").includes("WID-001"));
});
