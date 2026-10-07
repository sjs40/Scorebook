#!/usr/bin/env python3
"""Fetch MLB Stats API data for 2026-10-06 ship JSON."""

from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "ship-2026-10-06.json"
ISSUE_DATE = "2026-10-06"
NEXT_DATE = "2026-10-07"
STANDINGS_DATE = "2026-09-27"

TEAMS = json.loads((ROOT / "data" / "teams.json").read_text(encoding="utf-8"))
ID_TO_ABBR = {meta["id"]: code for code, meta in TEAMS.items()}

ABBR_MAP = {
    "TB": "TBR",
    "KC": "KCR",
    "SF": "SFG",
    "AZ": "ARI",
    "SD": "SDP",
    "WSH": "WSN",
    "CHW": "CWS",
    "ATH": "ATH",
}


def get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read())


def issue_abbr(code: str) -> str:
    return ABBR_MAP.get(code, code)


def parse_innings(linescore: dict) -> list[dict]:
    innings = []
    for inn in linescore.get("innings", []):
        away = inn.get("away", {}).get("runs", 0)
        home = inn.get("home", {}).get("runs", 0)
        innings.append({"away": away if away != "" else 0, "home": home if home != "" else 0})
    return innings


def batter_stats(player: dict, team_abbr: str) -> dict | None:
    stats = player.get("stats", {}).get("batting", {})
    if not stats or stats.get("atBats", 0) <= 0:
        return None
    doubles = stats.get("doubles", 0)
    triples = stats.get("triples", 0)
    homers = stats.get("homeRuns", 0)
    return {
        "name": player["person"]["fullName"],
        "team": issue_abbr(team_abbr),
        "AB": stats.get("atBats", 0),
        "H": stats.get("hits", 0),
        "2B": doubles,
        "3B": triples,
        "HR": homers,
        "RBI": stats.get("rbi", 0),
        "SB": stats.get("stolenBases", 0),
        "TB": stats.get("totalBases", 0),
    }


def pitcher_stats(player: dict, side: str, team_abbr: str) -> dict | None:
    stats = player.get("stats", {}).get("pitching", {})
    if not stats or not stats.get("inningsPitched"):
        return None
    return {
        "name": player["person"]["fullName"],
        "team": issue_abbr(team_abbr),
        "side": side,
        "IP": stats.get("inningsPitched", "0"),
        "H": stats.get("hits", 0),
        "ER": stats.get("earnedRuns", 0),
        "BB": stats.get("baseOnBalls", 0),
        "K": stats.get("strikeOuts", 0),
    }


def fetch_box(game_pk: int) -> dict:
    box = get(f"https://statsapi.mlb.com/api/v1/game/{game_pk}/boxscore")
    batters = []
    pitchers = []
    for side in ("away", "home"):
        team = box["teams"][side]
        team_abbr = team["team"]["abbreviation"]
        players = team.get("players", {})
        for bid in team.get("batters", []):
            key = f"ID{bid}"
            if key in players:
                row = batter_stats(players[key], team_abbr)
                if row:
                    batters.append(row)
        for pid in team.get("pitchers", []):
            key = f"ID{pid}"
            if key in players:
                row = pitcher_stats(players[key], side, team_abbr)
                if row:
                    pitchers.append(row)
    return {"batters": batters, "pitchers": pitchers}


def fmt_gb(value: str) -> str:
    if value in ("-", "—", "+0.0", "0.0"):
        return "—"
    return value


def fmt_wcgb(value: str) -> str:
    if value in ("-", "—"):
        return "—"
    return value


def fetch_standings() -> list[dict]:
    url = (
        "https://statsapi.mlb.com/api/v1/standings"
        f"?leagueId=103,104&season=2026&standingsTypes=regularSeason&date={STANDINGS_DATE}"
    )
    payload = get(url)
    divisions = []
    for record in payload.get("records", []):
        div_id = record["division"]["id"]
        div_name = {
            201: "AL East",
            202: "AL Central",
            200: "AL West",
            204: "NL East",
            205: "NL Central",
            203: "NL West",
        }.get(div_id, f"Division {div_id}")
        teams = []
        for tr in record.get("teamRecords", []):
            name = tr["team"]["name"]
            if name == "Athletics":
                short = "Athletics"
            elif name.startswith("Arizona"):
                short = "D-backs"
            else:
                short = name.split()[-1] if " " in name else name
                for code, meta in TEAMS.items():
                    if meta["id"] == tr["team"]["id"]:
                        short = meta["shortName"]
                        break
            l10 = tr.get("records", {}).get("splitRecords", [])
            last10 = next((r for r in l10 if r.get("type") == "lastTen"), None)
            if last10:
                l10w, l10l = last10["wins"], last10["losses"]
            else:
                l10w, l10l = 0, 0
            teams.append(
                {
                    "team": short,
                    "w": tr["wins"],
                    "l": tr["losses"],
                    "gb": fmt_gb(tr.get("gamesBack", "-")),
                    "wcgb": fmt_wcgb(tr.get("wildCardGamesBack", "-")),
                    "l10": l10w,
                    "l10l": l10l,
                    "rd": tr.get("runDifferential", 0),
                }
            )
        divisions.append({"division": div_name, "teams": teams})
    order = ["AL East", "AL Central", "AL West", "NL East", "NL Central", "NL West"]
    divisions.sort(key=lambda d: order.index(d["division"]))
    return divisions


def et_time(iso: str) -> str:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    et = dt.astimezone(timezone(timedelta(hours=-4)))
    h = et.hour % 12 or 12
    suffix = "AM" if et.hour < 12 else "PM"
    return f"{h}:{et.minute:02d} {suffix} ET"


def fetch_tonight() -> list[dict]:
    url = (
        f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={NEXT_DATE}"
        "&hydrate=probablePitcher,team"
    )
    payload = get(url)
    if not payload.get("dates"):
        return []
    games = []
    for g in payload["dates"][0].get("games", []):
        away = g["teams"]["away"]["team"]["abbreviation"]
        home = g["teams"]["home"]["team"]["abbreviation"]
        away_prob = g["teams"]["away"].get("probablePitcher") or {}
        home_prob = g["teams"]["home"].get("probablePitcher") or {}
        games.append(
            {
                "awayAbbr": away,
                "homeAbbr": home,
                "awayProb": away_prob.get("fullName", "TBD") if away_prob else "TBD",
                "homeProb": home_prob.get("fullName", "TBD") if home_prob else "TBD",
                "et": et_time(g["gameDate"]),
            }
        )
    return games


def fetch_games() -> tuple[list[dict], dict[str, dict], list[dict]]:
    url = (
        f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={ISSUE_DATE}"
        "&hydrate=linescore,decisions,team"
    )
    payload = get(url)
    games = []
    box_by_pk: dict[str, dict] = {}
    cancelled = []
    for g in payload["dates"][0]["games"]:
        state = g["status"]["detailedState"]
        away_id = g["teams"]["away"]["team"]["id"]
        home_id = g["teams"]["home"]["team"]["id"]
        if state in ("Cancelled", "Postponed"):
            cancelled.append(
                {
                    "away": issue_abbr(g["teams"]["away"]["team"]["abbreviation"]),
                    "home": issue_abbr(g["teams"]["home"]["team"]["abbreviation"]),
                    "reason": g["status"].get("reason", state),
                }
            )
            continue
        if state != "Final":
            continue
        pk = g["gamePk"]
        ls = g.get("linescore", {})
        decisions = g.get("decisions", {})
        wp = decisions.get("winner", {}).get("fullName")
        lp = decisions.get("loser", {}).get("fullName")
        sv = decisions.get("save", {}).get("fullName") if decisions.get("save") else None
        games.append(
            {
                "gamePk": pk,
                "away": {"id": away_id, "score": g["teams"]["away"]["score"]},
                "home": {"id": home_id, "score": g["teams"]["home"]["score"]},
                "innings": parse_innings(ls),
                "rhe": {
                    "away": {
                        "hits": ls.get("teams", {}).get("away", {}).get("hits", 0),
                        "errors": ls.get("teams", {}).get("away", {}).get("errors", 0),
                    },
                    "home": {
                        "hits": ls.get("teams", {}).get("home", {}).get("hits", 0),
                        "errors": ls.get("teams", {}).get("home", {}).get("errors", 0),
                    },
                },
                "wp": wp,
                "lp": lp,
                "sv": sv,
            }
        )
        box_by_pk[str(pk)] = fetch_box(pk)
    return games, box_by_pk, cancelled


def off_tonight(cancelled: list[dict]) -> list[dict]:
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={NEXT_DATE}&hydrate=team"
    payload = get(url)
    playing: set[int] = set()
    if payload.get("dates"):
        for g in payload["dates"][0].get("games", []):
            playing.add(g["teams"]["away"]["team"]["id"])
            playing.add(g["teams"]["home"]["team"]["id"])
    off = []
    for code, meta in TEAMS.items():
        if meta["id"] not in playing:
            off.append({"id": meta["id"]})
    return off


def main() -> None:
    games, box_by_pk, cancelled = fetch_games()
    standings = fetch_standings()
    tonight = fetch_tonight()
    off = off_tonight(cancelled)

    data = {
        "games": games,
        "boxByPk": box_by_pk,
        "cancelled": cancelled,
        "standings": standings,
        "tonight": tonight,
        "tonightDate": NEXT_DATE,
        "offTonight": off,
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Final games: {len(games)}, cancelled: {len(cancelled)}, tonight: {len(tonight)}")


if __name__ == "__main__":
    main()
