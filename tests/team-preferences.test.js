#!/usr/bin/env node
"use strict";

const { test, describe } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const logic = require("../js/team-preferences-logic.js");
const teams = JSON.parse(fs.readFileSync(path.join(__dirname, "../data/teams.json"), "utf8"));

const issueData = JSON.parse(
  fs.readFileSync(path.join(__dirname, "../2026-08-26/index.html"), "utf8")
    .match(/<script type="application\/json" id="scorebook-issue-data">\s*([\s\S]*?)<\/script>/)[1]
);

describe("teams.json", () => {
  test("contains exactly 30 teams", () => {
    assert.equal(Object.keys(teams).length, 30);
  });

  test("each team has required metadata fields", () => {
    for (const [abbr, team] of Object.entries(teams)) {
      assert.equal(team.abbreviation, abbr);
      assert.ok(team.id);
      assert.ok(team.name);
      assert.ok(team.shortName);
      assert.ok(team.city);
      assert.match(team.league, /^AL|NL$/);
      assert.match(team.division, /^(AL|NL) (East|Central|West)$/);
    }
  });
});

describe("preference precedence", () => {
  test("query param beats stored favorite", () => {
    assert.equal(logic.resolveEffectiveTeam("ATL", "CHC", teams), "ATL");
  });

  test("stored favorite used when no query param", () => {
    assert.equal(logic.resolveEffectiveTeam(null, "CHC", teams), "CHC");
  });

  test("invalid values resolve to no team", () => {
    assert.equal(logic.resolveEffectiveTeam("ZZZ", "CHC", teams), "CHC");
    assert.equal(logic.resolveEffectiveTeam(null, "ZZZ", teams), null);
    assert.equal(logic.resolveEffectiveTeam(null, null, teams), null);
  });
});

describe("game prioritization", () => {
  const games = issueData.allGames.map((g) => ({ away: g.away, home: g.home }));

  test("favorite game moves to front", () => {
    const ordered = logic.reorderGames(games, "CHC");
    assert.equal(ordered[0].away, "CHC");
    assert.equal(ordered.length, games.length);
  });

  test("repeated reordering preserves card count", () => {
    let ordered = games;
    ordered = logic.reorderGames(ordered, "CHC");
    ordered = logic.reorderGames(ordered, "ATL");
    assert.equal(ordered[0].home, "ATL");
    assert.equal(ordered.length, games.length);
  });

  test("duplicate prevention for compact insert", () => {
    const keys = games.map((g) => g.away + "@" + g.home);
    assert.equal(logic.wouldDuplicateExisting(keys, { away: "CHC", home: "ARI" }), true);
    assert.equal(logic.wouldDuplicateExisting(keys, { away: "NYY", home: "HOU" }), false);
  });
});

describe("team summaries", () => {
  test("uses prewritten teamSummaries when available", () => {
    assert.match(logic.pickTeamSummary("CHC", issueData, teams), /two hits/);
    assert.match(logic.pickTeamSummary("ATL", issueData, teams), /walk-off/);
  });

  test("off tonight teams get off copy when no game summary", () => {
    const data = { ...issueData, teamSummaries: {}, offTonight: ["CHC"] };
    assert.match(logic.pickTeamSummary("CHC", data, teams), /off Wednesday/);
  });

  test("unknown team returns empty summary", () => {
    assert.equal(logic.pickTeamSummary("NYY", { allGames: [], teamSummaries: {} }, teams), "");
  });
});

describe("reset behavior contract", () => {
  test("storage key is versioned", () => {
    assert.equal(logic.STORAGE_KEY, "scorebook.favoriteTeam.v1");
  });
});

console.log("All team-preferences tests passed.");
