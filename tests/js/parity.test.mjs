// Cross-target parity: every case here must also exist in tests/test_money.myna.
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
} from "../../build/js/core.mjs";

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

test("blend", () => {
  assert.equal(blend(0, 0, 10, 250), 250);
  assert.equal(blend(10, 250, 10, 350), 300);
  assert.equal(blend(10, 250, 0, 0), 250);
  assert.equal(blend(0, 999, 0, 0), 0);
});

test("stock_status", () => {
  assert.equal(stock_status(0, 5), "out");
  assert.equal(stock_status(3, 5), "low");
  assert.equal(stock_status(5, 5), "low");
  assert.equal(stock_status(6, 5), "ok");
});

test("suggested_qty", () => {
  assert.equal(suggested_qty(2, 5, 20), 18);
  assert.equal(suggested_qty(5, 5, 20), 15);
  assert.equal(suggested_qty(9, 5, 20), 0);
});
