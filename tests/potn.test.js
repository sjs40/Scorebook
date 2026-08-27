import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  normalizeCounts,
  pickWinner,
  parseVoteBody,
  totalVotes,
  ISSUE_RE,
} from "../functions/_lib/potn.js";

describe("potn vote helpers", () => {
  it("validates issue dates", () => {
    assert.equal(ISSUE_RE.test("2026-08-26"), true);
    assert.equal(ISSUE_RE.test("2026-8-26"), false);
  });

  it("normalizes counts", () => {
    assert.deepEqual(normalizeCounts({ suarez: 3, kim: "2", bad: -1 }), {
      suarez: 3,
      kim: 2,
    });
  });

  it("picks winner by count then order", () => {
    const counts = { suarez: 10, kim: 10, luzardo: 2, other: 1 };
    const winner = pickWinner(counts, ["suarez", "kim", "luzardo", "other"]);
    assert.equal(winner.choice, "suarez");
    assert.equal(winner.count, 10);
    assert.equal(totalVotes(counts), 23);
  });

  it("parses vote body", () => {
    assert.equal(parseVoteBody({ choice: "kim" }), "kim");
    assert.equal(parseVoteBody({ choice: "../etc" }), null);
  });
});
