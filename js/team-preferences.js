/**
 * Scorebook favorite-team personalization (localStorage, no accounts).
 * Shared across archive homepage and daily issues.
 */
(function (global) {
  "use strict";

  var STORAGE_KEY = "scorebook.favoriteTeam.v1";
  var DIVISION_ORDER = [
    "AL East", "AL Central", "AL West",
    "NL East", "NL Central", "NL West"
  ];

  var teamsCache = null;
  var initialLeagueSet = false;

  function safeStorage(op, value) {
    try {
      if (op === "get") return localStorage.getItem(STORAGE_KEY);
      if (op === "set") {
        if (value) localStorage.setItem(STORAGE_KEY, value);
        else localStorage.removeItem(STORAGE_KEY);
      }
    } catch (e) {}
    return null;
  }

  function loadTeams() {
    if (teamsCache) return Promise.resolve(teamsCache);
    return fetch("/data/teams.json")
      .then(function (res) {
        if (!res.ok) throw new Error("teams.json unavailable");
        return res.json();
      })
      .then(function (data) {
        teamsCache = data;
        return data;
      })
      .catch(function () {
        teamsCache = {};
        return teamsCache;
      });
  }

  function isValidTeam(abbr, teams) {
    return !!(abbr && teams && teams[abbr]);
  }

  function getStoredFavoriteTeam() {
    var val = safeStorage("get");
    if (!val) return null;
    if (teamsCache && !isValidTeam(val, teamsCache)) return null;
    return val;
  }

  function setStoredFavoriteTeam(abbr) {
    safeStorage("set", abbr || null);
  }

  function getQueryTeam() {
    var q = new URLSearchParams(global.location.search).get("team");
    if (!q) return null;
    q = q.toUpperCase();
    return isValidTeam(q, teamsCache) ? q : null;
  }

  function getEffectiveTeam() {
    return getQueryTeam() || getStoredFavoriteTeam() || null;
  }

  function parseIssueData() {
    var el = document.getElementById("scorebook-issue-data");
    if (!el) return null;
    try {
      return JSON.parse(el.textContent);
    } catch (e) {
      return null;
    }
  }

  function buildSelector(teams, stored, onChange) {
    var wrap = document.createElement("div");
    wrap.className = "sb-team-pick";

    var label = document.createElement("label");
    label.setAttribute("for", "sb-favorite-team");
    label.textContent = "My team";

    var select = document.createElement("select");
    select.id = "sb-favorite-team";
    select.name = "favorite-team";
    select.setAttribute("aria-label", "Choose your favorite MLB team");

    var empty = document.createElement("option");
    empty.value = "";
    empty.textContent = "No favorite team";
    select.appendChild(empty);

    DIVISION_ORDER.forEach(function (divName) {
      var group = document.createElement("optgroup");
      group.label = divName;
      Object.keys(teams)
        .filter(function (k) { return teams[k].division === divName; })
        .sort(function (a, b) { return teams[a].name.localeCompare(teams[b].name); })
        .forEach(function (abbr) {
          var opt = document.createElement("option");
          opt.value = abbr;
          opt.textContent = teams[abbr].name;
          group.appendChild(opt);
        });
      select.appendChild(group);
    });

    select.value = stored || "";
    select.addEventListener("change", function () {
      var val = select.value || null;
      setStoredFavoriteTeam(val);
      if (onChange) onChange(val);
    });

    wrap.appendChild(label);
    wrap.appendChild(select);
    return { wrap: wrap, select: select };
  }

  function mountSelector(container, onChange) {
    if (!container || container.querySelector(".sb-team-pick")) return;
    return loadTeams().then(function (teams) {
      var stored = getStoredFavoriteTeam();
      var preview = getQueryTeam();
      var ui = buildSelector(teams, preview || stored, onChange);
      if (preview && preview !== stored) {
        ui.select.value = preview;
      }
      container.appendChild(ui.wrap);
      return ui.select;
    });
  }

  function resetTeamPersonalization() {
    document.querySelectorAll("tr.sb-my-team").forEach(function (tr) {
      tr.classList.remove("sb-my-team");
    });
    document.querySelectorAll("details.game.sb-my-team, details.game.sb-compact").forEach(function (g) {
      g.classList.remove("sb-my-team");
    });
    document.querySelectorAll("article.upcoming-game.sb-my-team").forEach(function (a) {
      a.classList.remove("sb-my-team");
    });
    document.querySelectorAll(".sb-team-off").forEach(function (el) { el.remove(); });
    document.querySelectorAll("details.game[data-sb-inserted]").forEach(function (g) { g.remove(); });

    var gamesSection = document.getElementById("the-games");
    if (gamesSection && gamesSection._sbOriginalGameOrder) {
      var frag = document.createDocumentFragment();
      gamesSection._sbOriginalGameOrder.forEach(function (node) {
        frag.appendChild(node);
      });
      var subn = gamesSection.querySelector(".subn");
      if (subn) {
        gamesSection.insertBefore(frag, subn.nextSibling);
      } else {
        gamesSection.appendChild(frag);
      }
    }

    var tonight = document.getElementById("tonight-games");
    if (tonight && tonight._sbOriginalUpcomingOrder) {
      var tfrag = document.createDocumentFragment();
      tonight._sbOriginalUpcomingOrder.forEach(function (node) {
        tfrag.appendChild(node);
      });
      tonight.appendChild(tfrag);
    }

    var summary = document.getElementById("sb-team-summary");
    if (summary) summary.textContent = "";

    initialLeagueSet = false;
    var al = document.getElementById("tab-al");
    if (al) al.checked = true;
  }

  function highlightStandings(team) {
    if (!team) return;
    document.querySelectorAll('table.st tr[data-team="' + team + '"]').forEach(function (tr) {
      tr.classList.add("sb-my-team");
    });
  }

  function selectInitialLeague(team, teams) {
    if (initialLeagueSet || !team || !teams[team]) return;
    var league = teams[team].league;
    var tabId = league === "NL" ? "tab-nl" : "tab-al";
    var tab = document.getElementById(tabId);
    if (tab) tab.checked = true;
    initialLeagueSet = true;
  }

  function captureGameOrder(section) {
    if (!section || section._sbOriginalGameOrder) return;
    var games = Array.prototype.slice.call(section.querySelectorAll("details.game:not([data-sb-inserted])"));
    section._sbOriginalGameOrder = games.slice();
  }

  function captureUpcomingOrder(container) {
    if (!container || container._sbOriginalUpcomingOrder) return;
    var items = Array.prototype.slice.call(container.querySelectorAll("article.upcoming-game"));
    container._sbOriginalUpcomingOrder = items.slice();
  }

  function gameMatchesTeam(gameEl, team) {
    return gameEl.getAttribute("data-away-team") === team ||
      gameEl.getAttribute("data-home-team") === team;
  }

  function findGameInAllGames(team, issueData) {
    if (!issueData || !issueData.allGames) return null;
    for (var i = 0; i < issueData.allGames.length; i++) {
      var g = issueData.allGames[i];
      if (g.away === team || g.home === team) return g;
    }
    return null;
  }

  function findUpcomingForTeam(team, issueData) {
    if (!issueData || !issueData.upcomingGames) return null;
    for (var i = 0; i < issueData.upcomingGames.length; i++) {
      var g = issueData.upcomingGames[i];
      if (g.away === team || g.home === team) return g;
    }
    return null;
  }

  function renderCompactGameCard(game, teams) {
    var away = teams[game.away];
    var home = teams[game.home];
    if (!away || !home) return null;

    var awayName = away.shortName || away.name;
    var homeName = home.shortName || home.name;
    var winner = game.awayScore > game.homeScore ? awayName : homeName;
    var loser = game.awayScore > game.homeScore ? homeName : awayName;
    var winScore = Math.max(game.awayScore, game.homeScore);
    var loseScore = Math.min(game.awayScore, game.homeScore);

    var details = document.createElement("details");
    details.className = "game sb-compact";
    details.setAttribute("data-away-team", game.away);
    details.setAttribute("data-home-team", game.home);
    details.setAttribute("data-sb-inserted", "1");

    var summary = document.createElement("summary");
    summary.innerHTML = '<span class="hint"></span><h3>' + winner + " " + winScore + ", " + loser + " " + loseScore + "</h3>";
    if (game.note) {
      var note = document.createElement("p");
      note.className = "wl";
      note.textContent = game.note;
      summary.appendChild(note);
    }
    details.appendChild(summary);
    return details;
  }

  function renderUpcomingArticle(game, teams) {
    var away = teams[game.away];
    var home = teams[game.home];
    if (!away || !home) return null;

    var article = document.createElement("article");
    article.className = "upcoming-game";
    article.setAttribute("data-away-team", game.away);
    article.setAttribute("data-home-team", game.home);

    var p = document.createElement("p");
    var html = "";
    if (game.pitchers) {
      html += "<strong>" + game.pitchers + "</strong> — ";
    }
    html += away.shortName + " at " + home.shortName;
    if (game.startTime) {
      html += ", <time datetime=\"" + (game.startIso || "") + "\">" + game.startTime + "</time>";
    }
    if (game.note) {
      html += ". " + game.note;
    }
    p.innerHTML = html;
    article.appendChild(p);
    return article;
  }

  function prioritizePreviousGame(team, issueData, teams) {
    var section = document.getElementById("the-games");
    if (!section || !team) return;

    captureGameOrder(section);
    var games = Array.prototype.slice.call(section.querySelectorAll("details.game:not([data-sb-inserted])"));
    var match = games.find(function (g) { return gameMatchesTeam(g, team); });
    var firstGame = section.querySelector("details.game");

    if (!match) {
      var fromData = findGameInAllGames(team, issueData);
      if (fromData) {
        match = renderCompactGameCard(fromData, teams);
        if (match) {
          match.classList.add("sb-my-team");
          if (firstGame) section.insertBefore(match, firstGame);
          else section.appendChild(match);
        }
      }
      return;
    }

    match.classList.add("sb-my-team");
    if (firstGame) section.insertBefore(match, firstGame);
  }

  function prioritizeUpcomingGame(team, issueData, teams) {
    var container = document.getElementById("tonight-games");
    if (!container || !team) return;

    captureUpcomingOrder(container);

    if (issueData && issueData.offTonight && issueData.offTonight.indexOf(team) !== -1) {
      var off = document.createElement("p");
      off.className = "sb-team-off";
      var t = teams[team];
      off.textContent = "Your " + (t ? t.shortName : team) + " are off tonight.";
      container.insertBefore(off, container.firstChild);
    }

    var items = Array.prototype.slice.call(container.querySelectorAll("article.upcoming-game"));
    var match = items.find(function (a) { return gameMatchesTeam(a, team); });

    if (!match) {
      var fromData = findUpcomingForTeam(team, issueData);
      if (fromData && !(issueData.offTonight && issueData.offTonight.indexOf(team) !== -1)) {
        match = renderUpcomingArticle(fromData, teams);
        if (match) container.insertBefore(match, container.firstChild);
      }
      return;
    }

    match.classList.add("sb-my-team");
    var offEl = container.querySelector(".sb-team-off");
    if (offEl && offEl.nextSibling) {
      container.insertBefore(match, offEl.nextSibling);
    } else {
      container.insertBefore(match, container.firstChild);
    }
  }

  function renderTeamSummary(team, issueData, teams) {
    var el = document.getElementById("sb-team-summary");
    if (!el || !team) {
      if (el) el.textContent = "";
      return;
    }

    var t = teams[team];
    if (!t) {
      el.textContent = "";
      return;
    }

    var text = "";
    if (issueData && issueData.teamSummaries && issueData.teamSummaries[team]) {
      text = issueData.teamSummaries[team];
    } else if (issueData && issueData.offTonight && issueData.offTonight.indexOf(team) !== -1) {
      text = "Your " + t.shortName + ": " + t.city + " was off Wednesday.";
    } else {
      var game = findGameInAllGames(team, issueData);
      if (game) {
        var isHome = game.home === team;
        var opp = teams[isHome ? game.away : game.home];
        var teamScore = isHome ? game.homeScore : game.awayScore;
        var oppScore = isHome ? game.awayScore : game.homeScore;
        var won = teamScore > oppScore;
        text = "Your " + t.shortName + ": " + t.city + " " +
          (won ? "beat" : "lost to") + " " + (opp ? opp.city : "opponent") +
          " " + teamScore + "–" + oppScore + ".";
      }
    }

    el.textContent = text;
  }

  function applyTeamPreference(team, issueData, teams) {
    resetTeamPersonalization();
    if (!team) return;

    selectInitialLeague(team, teams);
    highlightStandings(team);
    renderTeamSummary(team, issueData, teams);
    prioritizePreviousGame(team, issueData, teams);
    prioritizeUpcomingGame(team, issueData, teams);
  }

  function initIssuePage() {
    var issueData = parseIssueData();
    if (!issueData) return;

    var header = document.querySelector("header.site");
    var tools = document.createElement("div");
    tools.className = "site-header-tools";
    if (header) header.appendChild(tools);

    loadTeams().then(function (teams) {
      mountSelector(tools, function (selected) {
        applyTeamPreference(selected, issueData, teams);
        var sel = document.getElementById("sb-favorite-team");
        if (sel) sel.value = selected || "";
      }).then(function () {
        applyTeamPreference(getEffectiveTeam(), issueData, teams);
      });
    });
  }

  function initHomepage() {
    var header = document.querySelector("header.site");
    var tools = document.createElement("div");
    tools.className = "site-header-tools";
    if (header) header.appendChild(tools);
    mountSelector(tools, function () {});
  }

  function init() {
    if (document.getElementById("scorebook-issue-data")) {
      initIssuePage();
    } else {
      initHomepage();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  var api = {
    STORAGE_KEY: STORAGE_KEY,
    loadTeams: loadTeams,
    getStoredFavoriteTeam: getStoredFavoriteTeam,
    setStoredFavoriteTeam: setStoredFavoriteTeam,
    getQueryTeam: getQueryTeam,
    getEffectiveTeam: getEffectiveTeam,
    parseIssueData: parseIssueData,
    isValidTeam: isValidTeam,
    resetTeamPersonalization: resetTeamPersonalization,
    highlightStandings: highlightStandings,
    prioritizePreviousGame: prioritizePreviousGame,
    prioritizeUpcomingGame: prioritizeUpcomingGame,
    renderTeamSummary: renderTeamSummary,
    applyTeamPreference: applyTeamPreference,
    findGameInAllGames: findGameInAllGames,
    gameMatchesTeam: gameMatchesTeam,
    _setTeamsCache: function (t) { teamsCache = t; }
  };

  global.ScorebookTeams = api;
})(typeof window !== "undefined" ? window : global);
