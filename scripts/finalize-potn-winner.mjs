#!/usr/bin/env node
/**
 * Read Play of the night totals from the deployed API, pick a winner,
 * and write data/potn-winners.json for the nightly operator.
 *
 * Usage:
 *   node scripts/finalize-potn-winner.mjs 2026-08-26
 *   POTN_API_BASE=https://preview.example.pages.dev/api/potn/ node scripts/finalize-potn-winner.mjs 2026-08-26
 *
 * After finalizing, copy winners[issue].label into tomorrow's issues.json
 * playOfTheNight field (calendar prepends it to the dek automatically).
 */

import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { pickWinner, ISSUE_RE } from "../functions/_lib/potn.js";
const apiBase = process.env.POTN_API_BASE || "https://getscorebook.com/api/potn/";
const issue = process.argv[2];

if (!issue || !ISSUE_RE.test(issue)) {
  console.error("Usage: node scripts/finalize-potn-winner.mjs YYYY-MM-DD");
  process.exit(1);
}

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const winnersPath = join(root, "data", "potn-winners.json");

const res = await fetch(apiBase + encodeURIComponent(issue), {
  headers: { Accept: "application/json" },
});

if (!res.ok) {
  console.error("API error", res.status, await res.text());
  process.exit(1);
}

const labels = {
  suarez: "Eugenio Suárez, grand slam",
  kim: "Ha-Seong Kim walk-off",
  luzardo: "Jesús Luzardo, 9 Ks",
  cubs: "Cubs homer barrage",
  cowser: "Cowser catch",
  story: "Story walk-off",
  other: "Something else",
};

const nomineeOrder = {
  "2026-08-26": ["suarez", "kim", "luzardo", "other"],
  "2026-08-31": ["cubs", "cowser", "story", "other"],
};

const payload = await res.json();
const order = nomineeOrder[issue] || Object.keys(payload.counts || {});
const winner = pickWinner(payload.counts || {}, order);

if (!winner || !winner.choice) {
  console.error("No votes recorded for", issue);
  process.exit(1);
}

/** @type {{ issues: Record<string, unknown> }} */
let store;
try {
  store = JSON.parse(readFileSync(winnersPath, "utf8"));
} catch {
  store = { issues: {} };
}
if (!store.issues || typeof store.issues !== "object") {
  store.issues = {};
}

store.issues[issue] = {
  winner: winner.choice,
  label: labels[winner.choice] || winner.choice,
  counts: payload.counts || {},
  total: payload.total || 0,
  finalizedAt: new Date().toISOString(),
};

writeFileSync(winnersPath, JSON.stringify(store, null, 2) + "\n");

console.log("Finalized", issue, "→", store.issues[issue].label);
console.log("Counts:", store.issues[issue].counts);
console.log("");
console.log("Next: add to tomorrow's issues.json row:");
console.log('  "playOfTheNight": "' + store.issues[issue].label + '"');
