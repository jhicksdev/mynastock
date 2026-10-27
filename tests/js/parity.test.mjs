// Cross-target parity: every case here must also exist in the Python suites.
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  concat,
  is_digits,
  parse_cents,
  format_cents,
  blend,
  stock_status,
  suggested_qty,
  lookup,
  fingerprint,
  plan_receive,
  plan_issue,
  plan_transfer,
  StockLevel,
  NewProduct,
  NewLocation,
  MoveCmd,
  create_product,
  create_location,
  post_movement,
  stock_rows,
  reorder_rows,
  valuation,
  new_memory_repo,
} from "../../build/js/portable.mjs";

test("concat", () => {
  assert.equal(concat([]), "");
  assert.equal(concat(["a"]), "a");
  assert.equal(concat(["a", "b"]), "ab");
  assert.equal(concat(["a", "b"], ","), "a,b");
});

test("is_digits", () => {
  assert.equal(is_digits("0"), true);
  assert.equal(is_digits("1234567890"), true);
  assert.equal(is_digits(""), false);
  assert.equal(is_digits("12a"), false);
  assert.equal(is_digits(" 1"), false);
});

test("parse_cents", () => {
  assert.equal(parse_cents("12"), 1200);
  assert.equal(parse_cents("12.3"), 1230);
  assert.equal(parse_cents("12.34"), 1234);
  assert.equal(parse_cents("0.05"), 5);
  assert.equal(parse_cents("00012"), 1200);
  assert.equal(parse_cents("1."), null);
  assert.equal(parse_cents(".5"), null);
  assert.equal(parse_cents("12.345"), null);
  assert.equal(parse_cents("-1"), null);
  assert.equal(parse_cents(""), null);
  assert.equal(parse_cents("1,000"), null);
  assert.equal(parse_cents("1.2.3"), null);
});

test("format_cents", () => {
  assert.equal(format_cents(1234), "12.34");
  assert.equal(format_cents(5), "0.05");
  assert.equal(format_cents(0), "0.00");
  assert.equal(format_cents(-5), "-0.05");
  assert.equal(format_cents(100), "1.00");
});

test("blend and stock helpers", () => {
  assert.equal(blend(0, 0, 10, 250), 250);
  assert.equal(blend(10, 250, 10, 350), 300);
  assert.equal(blend(10, 250, 0, 0), 250);
  assert.equal(stock_status(0, 5), "out");
  assert.equal(stock_status(5, 5), "low");
  assert.equal(stock_status(6, 5), "ok");
  assert.equal(suggested_qty(2, 5, 20), 18);
  assert.equal(suggested_qty(9, 5, 20), 0);
});

test("lookup uses dynamic keys", () => {
  assert.equal(lookup({ a: 1 }, "a"), 1);
  assert.equal(lookup({ a: 1 }, "b"), null);
  assert.equal(fingerprint(["receive", "A|B", "1", ""]) !== fingerprint(["receive", "A", "B|1", ""]), true);
});

test("ledger plans match Python", () => {
  const receive = plan_receive(null, "p1", "l1", 10, 250, "t1");
  assert.equal(receive.ok, true);
  assert.equal(receive.value.levels[0].on_hand, 10);
  assert.equal(receive.value.levels[0].avg_cost_cents, 250);

  const issue = plan_issue(new StockLevel("p1", "l1", 10, 250, 1, "t0"), "p1", "l1", 4, "t1");
  assert.equal(issue.ok, true);
  assert.equal(issue.value.levels[0].on_hand, 6);
  assert.equal(issue.value.legs[0].qty_delta, -4);

  const denied = plan_issue(new StockLevel("p1", "l1", 3, 250, 1, "t0"), "p1", "l1", 4, "t1");
  assert.equal(denied.ok, false);
  assert.equal(denied.error.code, "stock.insufficient");
  assert.equal(denied.error.meta.available, 3);

  const transfer = plan_transfer(
    new StockLevel("p1", "l1", 10, 250, 1, "t0"),
    new StockLevel("p1", "l2", 4, 300, 1, "t0"),
    "p1",
    "l1",
    "l2",
    5,
    "t1",
  );
  assert.equal(transfer.ok, true);
  assert.equal(transfer.value.legs[0].qty_delta + transfer.value.legs[1].qty_delta, 0);
  assert.equal(transfer.value.levels[1].on_hand, 9);
  assert.equal(transfer.value.levels[1].avg_cost_cents, 272);
});

test("service scenario matches Python", () => {
  const repo = new_memory_repo();
  const now = "2026-01-01T00:00:00Z";

  const product = create_product(new NewProduct("WID-001", "Widget", 250, 5, 20), repo, now, "p1");
  assert.equal(product.ok, true);
  assert.equal(create_location(new NewLocation("WH1", "Main", "warehouse"), repo, "l1").ok, true);
  assert.equal(create_location(new NewLocation("BIN-A", "Bin A"), repo, "l2").ok, true);

  const receive = post_movement(
    new MoveCmd("receive", "WID-001", "WH1", "", 10, 250, null, null, "tester", "k1"),
    repo,
    "t1",
    ["o1", "m1", "m2"],
  );
  assert.equal(receive.ok, true);
  assert.equal(receive.value.levels[0].on_hand, 10);

  const replay = post_movement(
    new MoveCmd("receive", "WID-001", "WH1", "", 10, 250, null, null, "tester", "k1"),
    repo,
    "t2",
    ["o9", "m8", "m7"],
  );
  assert.deepEqual(replay.value, receive.value);

  const conflict = post_movement(
    new MoveCmd("receive", "WID-001", "WH1", "", 11, 250, null, null, "tester", "k1"),
    repo,
    "t2",
    ["oa", "mb", "mc"],
  );
  assert.equal(conflict.ok, false);
  assert.equal(conflict.error.code, "movement.idempotency_conflict");

  const transfer = post_movement(
    new MoveCmd("transfer", "WID-001", "WH1", "BIN-A", 4, null, null, null, "tester", "k2"),
    repo,
    "t3",
    ["o2", "m3", "m4"],
  );
  assert.equal(transfer.ok, true);
  assert.equal(transfer.value.movements[0].type, "transfer_out");
  assert.equal(transfer.value.movements[1].type, "transfer_in");

  const rows = stock_rows(repo).value;
  assert.equal(rows.length, 2);
  const binA = rows.find((row) => row.location === "BIN-A");
  assert.equal(binA.on_hand, 4);
  assert.equal(binA.status, "low");

  const reorder = reorder_rows(repo).value;
  assert.equal(reorder.length, 1);
  assert.equal(reorder[0].suggested_qty, 16);

  const value = valuation(repo, "location").value;
  assert.equal(value.total_cents, 2500);

  const denied = post_movement(
    new MoveCmd("issue", "WID-001", "BIN-A", "", 99, null, null, null, "tester", "k3"),
    repo,
    "t4",
    ["o3", "m5", "m6"],
  );
  assert.equal(denied.ok, false);
  assert.equal(denied.error.code, "stock.insufficient");
  assert.equal(repo.list_movements().length, 3);
});
