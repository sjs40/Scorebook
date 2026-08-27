/**
 * Pure helpers for favorite-team personalization (testable without DOM).
 * Loaded before team-preferences.js in the browser; exported for Node tests.
 */
(function (global) {
  "use strict";

  var STORAGE_KEY = "scorebook.favoriteTeam.v1";

  function isValidTeam(abbr, teams) {
    return !!(abbr && teams && teams[abbr]);
  }

  function resolveEffectiveTeam(queryTeam, storedTeam, teams) {
    if (queryTeam && isValidTeam(queryTeam, teams)) return queryTeam;
    if (storedTeam && isValidTeam(storedTeam, teams)) return storedTeam;
    return null;
  }

  function gameMatchesTeam(game, team) {
    return game.away === team || game.home === team;
  }

  function findGameForTeam(team, allGames) {
    if (!allGames) return null;
    for (var i = 0; i < allGames.length; i++) {
      if (gameMatchesTeam(allGames[i], team)) return allGames[i];
    }
    return null;
  }

  function findUpcomingForTeam(team, upcomingGames) {
    if (!upcomingGames) return null;
    for (var i = 0; i < upcomingGames.length; i++) {
      if (gameMatchesTeam(upcomingGames[i], team)) return upcomingGames[i];
    }
    return null;
  }

  function pickTeamSummary(team, issueData, teams) {
    if (!team || !teams[team]) return "";
    var t = teams[team];
    if (issueData.teamSummaries && issueData.teamSummaries[team]) {
      return issueData.teamSummaries[team];
    }
    if (issueData.offTonight && issueData.offTonight.indexOf(team) !== -1) {
      return "Your " + t.shortName + ": " + t.city + " was off Wednesday.";
    }
    var game = findGameForTeam(team, issueData.allGames);
    if (!game) return "";
    var isHome = game.home === team;
    var opp = teams[isHome ? game.away : game.home];
    var teamScore = isHome ? game.homeScore : game.awayScore;
    var oppScore = isHome ? game.awayScore : game.homeScore;
    var won = teamScore > oppScore;
    return "Your " + t.shortName + ": " + t.city + " " +
      (won ? "beat" : "lost to") + " " + (opp ? opp.city : "opponent") +
      " " + teamScore + "–" + oppScore + ".";
  }

  function reorderGames(games, team) {
    var list = games.slice();
    var idx = list.findIndex(function (g) { return gameMatchesTeam(g, team); });
    if (idx <= 0) return list;
    var item = list.splice(idx, 1)[0];
    list.unshift(item);
    return list;
  }

  function wouldDuplicateExisting(existingKeys, game) {
    var key = game.away + "@" + game.home;
    return existingKeys.indexOf(key) !== -1;
  }

  var api = {
    STORAGE_KEY: STORAGE_KEY,
    isValidTeam: isValidTeam,
    resolveEffectiveTeam: resolveEffectiveTeam,
    gameMatchesTeam: gameMatchesTeam,
    findGameForTeam: findGameForTeam,
    findUpcomingForTeam: findUpcomingForTeam,
    pickTeamSummary: pickTeamSummary,
    reorderGames: reorderGames,
    wouldDuplicateExisting: wouldDuplicateExisting
  };

  global.ScorebookTeamLogic = api;

  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
})(typeof window !== "undefined" ? window : global);
