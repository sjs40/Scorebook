#!/usr/bin/env python3
"""Generate /workspace/2026-10-06/index.html from shipped data JSON."""

from __future__ import annotations

import json
import re
import shutil
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "ship-2026-10-06.json"
OUT_DIR = ROOT / "2026-10-06"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-10-05" / "index.html"
ISSUE_DATE = "2026-10-06"
STANDINGS_DATE = "2026-09-27"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Enrique Hernández and Freddie Freeman homered in a three-run fourth as the Dodgers beat Atlanta 3–1 and took a 2–1 NLDS lead. "
    "Yoshinobu Yamamoto struck out 10 in seven innings. "
    "Jake Cronenworth homered and San Diego held on 4–3 to pull within 2–1 against Milwaukee; William Contreras went deep for the Brewers. "
    "ALDS Game 3 is tonight in Chicago and New York."
)

RACE_AL_RECAP = (
    "ALDS off Tuesday. Both series hold at 2–0 — Chicago leads Cleveland; Tampa Bay leads New York after Monday's Game 2s."
)
RACE_AL_SINCE = (
    "ALDS Game 3 Wednesday: Guardians at White Sox (4:00 PM ET); Rays at Yankees (8:00 PM ET). "
    "Best-of-five — winners need three."
)
RACE_NL_RECAP = (
    "NLDS Game 3: Dodgers scored three in the fourth at Truist Park and beat the Braves 3–1 on Yoshinobu Yamamoto's 10-strikeout start; "
    "Padres beat Milwaukee 4–3 as Jake Cronenworth homered and Michael King closed it out."
)
RACE_NL_SINCE = (
    "Los Angeles leads Atlanta 2–1; Milwaukee leads San Diego 2–1. "
    "NLDS Game 4 Wednesday: Dodgers at Braves (6:00 PM ET); Brewers at Padres (10:00 PM ET)."
)

CLIPS = {
    "kike_hr": {
        "video": "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-10/06/2dfd6a18-11d8a4f6-995cd24e-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "enrique-hernandez-homers-1-on-a-fly-ball-to-left-field-andy-pages-scores",
        "cap": "Enrique Hernández's two-run homer keyed the fourth — Dodgers 3, Braves 1.",
    },
    "yamamoto": {
        "video": "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-10/06/9f6d0071-f9054648-310ac631-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "yoshinobu-yamamoto-s-fans-10-in-dominant-outing",
        "cap": "Yoshinobu Yamamoto struck out 10 in seven innings — Dodgers 3, Braves 1.",
    },
    "cronenworth": {
        "video": "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-10/06/b92bbecd-4acc9300-88c87874-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "jojo-romero-in-play-run-s-to-jake-cronenworth",
        "cap": "Jake Cronenworth's solo homer — Padres 4, Brewers 3.",
    },
    "dubon_rob": {
        "video": "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-10/06/c1d3075e-38b5784c-5bf6586b-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "chris-sale-in-play-out-s-to-freddie-freeman-7nfloy",
        "cap": "Mauricio Dubón robbed Freddie Freeman at the wall — Braves still lost 3–1. That's baseball.",
    },
    "fourth_inning": {
        "video": "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-10/06/844f11ac-a3a6372a-a56b71c0-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "chris-sale-in-play-run-s-to-freddie-freeman",
        "cap": "Freddie Freeman's solo shot capped a three-run fourth — Dodgers 3, Braves 1.",
    },
}

ABBR_TO_ISSUE = {
    "TB": "TBR",
    "KC": "KCR",
    "SF": "SFG",
    "AZ": "ARI",
    "SD": "SDP",
    "WSH": "WSN",
    "CHW": "CWS",
}

TEAMS = json.loads((ROOT / "data" / "teams.json").read_text(encoding="utf-8"))
ID_TO_ABBR = {meta["id"]: code for code, meta in TEAMS.items()}
NAME_TO_ABBR = {meta["shortName"]: code for code, meta in TEAMS.items()}
NAME_TO_ABBR["Athletics"] = "ATH"
NAME_TO_ABBR["D-backs"] = "ARI"


def issue_abbr(code: str) -> str:
    return ABBR_TO_ISSUE.get(code, code)


ISSUE_TO_CODE = {issue_abbr(code): code for code in TEAMS}
for short, mapped in ABBR_TO_ISSUE.items():
    ISSUE_TO_CODE[short] = ISSUE_TO_CODE[mapped]


def norm_from_id(team_id: int) -> str:
    return issue_abbr(ID_TO_ABBR[team_id])


def team_meta(abbr: str) -> dict:
    return TEAMS[ISSUE_TO_CODE[abbr]]


def load_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def fetch_streaks() -> dict[int, str]:
    url = (
        "https://statsapi.mlb.com/api/v1/standings"
        f"?leagueId=103,104&season=2026&standingsTypes=regularSeason&date={STANDINGS_DATE}"
    )
    streaks: dict[int, str] = {}
    with urllib.request.urlopen(url, timeout=20) as resp:
        payload = json.loads(resp.read())
    for record in payload.get("records", []):
        for team in record.get("teamRecords", []):
            tid = team["team"]["id"]
            streak = team.get("streak", {})
            code = streak.get("streakCode") or "W0"
            streaks[tid] = code.upper()
    return streaks


def ip_to_outs(ip: str | float | int) -> int:
    if isinstance(ip, (int, float)):
        whole = int(ip)
        frac = round((ip - whole) * 10)
        return whole * 3 + frac
    s = str(ip)
    if "." in s:
        whole, frac = s.split(".", 1)
        return int(whole) * 3 + int(frac or 0)
    return int(s) * 3


def bill_james_gs(ip: str, h: int, er: int, bb: int, k: int) -> int:
    outs = ip_to_outs(ip)
    return round(40 + 2 * outs - 3 * h - 2 * er - bb + k)


def parse_innings(raw: list[dict]) -> tuple[list[int], list[int]]:
    away: list[int] = []
    home: list[int] = []
    for inn in raw:
        a = inn.get("away", 0)
        h = inn.get("home", 0)
        away.append(0 if a == "" else int(a))
        home.append(0 if h == "" else int(h))
    return away, home


def wl_note(game: dict) -> str:
    parts = [f"W {game['wp']}"]
    if game.get("lp"):
        parts.append(f"L {game['lp']}")
    if game.get("sv"):
        parts.append(f"S {game['sv']}")
    return " · ".join(parts)


def et_to_iso(et: str, date: str) -> str:
    m = re.match(r"(\d{1,2}):(\d{2})\s*(AM|PM)\s*ET", et.strip(), re.I)
    if not m:
        return f"{date}T12:00:00Z"
    hour = int(m.group(1)) % 12
    if m.group(3).upper() == "PM":
        hour += 12
    minute = int(m.group(2))
    dt = datetime.strptime(date, "%Y-%m-%d").replace(
        hour=hour, minute=minute, tzinfo=timezone(timedelta(hours=-4))
    )
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_games(data: dict) -> list[dict]:
    games = []
    for game in data["games"]:
        away = norm_from_id(game["away"]["id"])
        home = norm_from_id(game["home"]["id"])
        away_inn, home_inn = parse_innings(game["innings"])
        rhe = game["rhe"]
        games.append(
            {
                "away": away,
                "home": home,
                "awayScore": game["away"]["score"],
                "homeScore": game["home"]["score"],
                "awayInn": away_inn,
                "homeInn": home_inn,
                "awayH": rhe["away"]["hits"],
                "awayE": rhe["away"]["errors"],
                "homeH": rhe["home"]["hits"],
                "homeE": rhe["home"]["errors"],
                "note": wl_note(game),
            }
        )
    return games


def build_hitters(data: dict) -> list[tuple]:
    rows = []
    for box in data["boxByPk"].values():
        for batter in box.get("batters", []):
            if batter.get("AB", 0) <= 0:
                continue
            xbh = batter.get("2B", 0) + batter.get("3B", 0) + batter.get("HR", 0)
            rows.append(
                (
                    batter["TB"],
                    batter["HR"],
                    batter["RBI"],
                    batter["H"],
                    batter["SB"],
                    batter["name"],
                    issue_abbr(batter["team"]),
                    batter["AB"],
                    xbh,
                )
            )
    rows.sort(key=lambda r: (-r[0], -r[1], -r[2], -r[3], -r[4]))
    return rows[:8]


def build_pitchers(data: dict) -> list[tuple]:
    game_teams: dict[str, tuple[str, str]] = {}
    for game in data["games"]:
        pk = str(game["gamePk"])
        away = norm_from_id(game["away"]["id"])
        home = norm_from_id(game["home"]["id"])
        game_teams[pk] = (away, home)

    rows = []
    for pk, box in data["boxByPk"].items():
        away, home = game_teams.get(pk, ("?", "?"))
        for pitcher in box.get("pitchers", []):
            ip = pitcher.get("IP", "0")
            if ip_to_outs(ip) < 15:
                continue
            side = pitcher.get("side")
            opp = home if side == "away" else away
            gs = bill_james_gs(
                ip,
                pitcher.get("H", 0),
                pitcher.get("ER", 0),
                pitcher.get("BB", 0),
                pitcher.get("K", 0),
            )
            rows.append(
                (
                    gs,
                    pitcher["name"],
                    issue_abbr(pitcher["team"]),
                    ip,
                    pitcher.get("H", 0),
                    pitcher.get("ER", 0),
                    pitcher.get("BB", 0),
                    pitcher.get("K", 0),
                    opp,
                )
            )
    rows.sort(key=lambda r: -r[0])
    return rows[:4]


def fmt_gb(value: str) -> str:
    if value in ("-", "—"):
        return "--"
    return value


def fmt_wcgb(value: str) -> str:
    if value in ("-", "—"):
        return "--"
    if value.startswith("+"):
        return value
    if value.replace(".", "", 1).isdigit():
        return value
    return value


def fmt_rd(value: int) -> str:
    return f"{value:+d}"


def division_rows(division: dict, streaks: dict[int, str]) -> list[tuple]:
    rows = []
    for team in division["teams"]:
        code = NAME_TO_ABBR.get(team["team"], team["team"][:3].upper())
        abbr = issue_abbr(code)
        streak = streaks.get(TEAMS[code]["id"], "W0")
        rows.append(
            (
                abbr,
                team["w"],
                team["l"],
                fmt_gb(team["gb"]),
                fmt_wcgb(team["wcgb"]),
                streak,
                f"{team['l10']}-{team['l10l']}",
                fmt_rd(team["rd"]),
            )
        )
    return rows


def division_leaders(data: dict) -> set[str]:
    leaders: set[str] = set()
    for division in data["standings"]:
        for team in division["teams"]:
            if team["gb"] in ("-", "—"):
                code = NAME_TO_ABBR.get(team["team"], team["team"][:3].upper())
                leaders.add(issue_abbr(code))
    return leaders


def series_table(title: str, rows: list[tuple], card: str) -> str:
    body = ""
    for leader, trailer, w, l in rows:
        body += (
            f'<tr data-team="{leader}"><td class="tm">{leader}</td><td>{trailer}</td>'
            f"<td>{w}</td><td>{l}</td></tr>\n"
        )
    return f"""      <div class="table-block" data-share-card="{card}">
      <div class="div">{title}</div>
      <div class="scroll"><table class="st"><thead><tr><th>Tm</th><th>Opp</th><th>W</th><th>L</th></tr></thead><tbody>
{body}</tbody></table></div>
      </div>"""


AL_DS_SERIES = [("CWS", "CLE", 2, 0), ("TBR", "NYY", 2, 0)]
NL_DS_SERIES = [("LAD", "ATL", 2, 1), ("MIL", "SDP", 2, 1)]

TEAM_SUMMARY_OVERRIDES: dict[str, str] = {
    "CWS": "Your White Sox: Off yesterday. Lead Cleveland 2–0 in the ALDS. Host Guardians tonight.",
    "CLE": "Your Guardians: Off yesterday. Trail 0–2 in the ALDS. At White Sox tonight.",
    "TBR": "Your Rays: Off yesterday. Lead New York 2–0 in the ALDS. At Yankees tonight.",
    "NYY": "Your Yankees: Off yesterday. Trail 0–2 in the ALDS. Host Rays tonight.",
    "LAD": "Your Dodgers: Won 3–1 at Atlanta in NLDS Game 3; Yoshinobu Yamamoto earned the win. Lead the series 2–1. At Braves tonight.",
    "ATL": "Your Braves: Lost 1–3 to Los Angeles in NLDS Game 3; Chris Sale took the loss. Trail 1–2. Host Dodgers tonight.",
    "MIL": "Your Brewers: Lost 3–4 at San Diego in NLDS Game 3; JoJo Romero took the loss. Lead the series 2–1. At Padres tonight.",
    "SDP": "Your Padres: Won 4–3 over Milwaukee in NLDS Game 3; Yuki Matsui earned the win. Trail 2–1 in the NLDS. Host Brewers tonight.",
    "CHC": "Your Cubs: Season over. Off tonight.",
}


def wild_card_rows(data: dict, league: str, streaks: dict[int, str]) -> list[tuple]:
    leaders = division_leaders(data)
    candidates = []
    for division in data["standings"]:
        if not division["division"].startswith(league):
            continue
        for team in division["teams"]:
            code = NAME_TO_ABBR.get(team["team"], team["team"][:3].upper())
            abbr = issue_abbr(code)
            if abbr in leaders:
                continue
            candidates.append(
                (
                    -team["w"],
                    abbr,
                    team["w"],
                    team["l"],
                    fmt_wcgb(team["wcgb"]),
                    streaks.get(TEAMS[code]["id"], "W0"),
                    f"{team['l10']}-{team['l10l']}",
                    fmt_rd(team["rd"]),
                )
            )
    candidates.sort()
    rows = []
    for idx, (_, abbr, w, l, wcgb, streak, l10, rd) in enumerate(candidates[:6]):
        rows.append((abbr, w, l, wcgb, streak, l10, rd, idx == 2))
    return rows


def build_upcoming(data: dict) -> list[dict]:
    rows = []
    for game in data["tonight"]:
        away = issue_abbr(game["awayAbbr"])
        home = issue_abbr(game["homeAbbr"])
        away_prob = game.get("awayProb") or "TBD"
        home_prob = game.get("homeProb") or "TBD"
        rows.append(
            {
                "away": away,
                "home": home,
                "pitchers": f"{away_prob} vs. {home_prob}",
                "startTime": game["et"],
                "startIso": et_to_iso(game["et"], data["tonightDate"]),
                "note": "",
            }
        )
    return rows


def score_phrase(winner_score: int, loser_score: int) -> str:
    return f"{winner_score}–{loser_score}"


def cancelled_abbrs(data: dict) -> set[str]:
    abbrs: set[str] = set()
    for game in data.get("cancelled", []):
        abbrs.add(game["away"])
        abbrs.add(game["home"])
    return abbrs


def render_cancelled(data: dict) -> str:
    parts = []
    for game in data.get("cancelled", []):
        reason = game.get("reason", "Cancelled")
        label = reason if reason.lower() == "rain" else f"{reason} (rain)"
        parts.append(
            f'  <p class="subn">{game["away"]} at {game["home"]} — Cancelled ({label}).</p>'
        )
    return "\n".join(parts)


def build_team_summaries(data: dict, upcoming: list[dict]) -> dict[str, str]:
    off_abbrs = {norm_from_id(team["id"]) for team in data["offTonight"]}
    rainout_abbrs = cancelled_abbrs(data)

    results: dict[str, list[str]] = {issue_abbr(code): [] for code in TEAMS}
    for game in data["games"]:
        away = norm_from_id(game["away"]["id"])
        home = norm_from_id(game["home"]["id"])
        away_score = game["away"]["score"]
        home_score = game["home"]["score"]
        away_name = team_meta(away)["shortName"]
        home_name = team_meta(home)["shortName"]
        if away_score > home_score:
            results[away].append(
                f"Won {score_phrase(away_score, home_score)} at {home_name}; {game['wp']} earned the win"
            )
            results[home].append(
                f"Lost {score_phrase(home_score, away_score)} to {away_name}; {game['lp']} took the loss"
            )
        elif home_score > away_score:
            results[home].append(
                f"Won {score_phrase(home_score, away_score)} over {away_name}; {game['wp']} earned the win"
            )
            results[away].append(
                f"Lost {score_phrase(away_score, home_score)} to {home_name}; {game['lp']} took the loss"
            )

    tonight_away: dict[str, str] = {}
    tonight_home: dict[str, str] = {}
    for item in upcoming:
        away = item["away"]
        home = item["home"]
        tonight_away[away] = team_meta(home)["shortName"]
        tonight_home[home] = team_meta(away)["shortName"]

    summaries: dict[str, str] = {}
    for code, meta in TEAMS.items():
        abbr = issue_abbr(code)
        short = meta["shortName"]
        if results[abbr]:
            yesterday = (
                results[abbr][0]
                if len(results[abbr]) == 1
                else f"{results[abbr][0]}; {results[abbr][1]}"
            )
            body = f"Your {short}: {yesterday}."
        elif abbr in rainout_abbrs:
            body = f"Your {short}: Scheduled game cancelled (rain)."
        else:
            body = f"Your {short}: Off yesterday."
        if abbr in off_abbrs:
            body += " Off tonight."
        elif abbr in tonight_away:
            body += f" At {tonight_away[abbr]} tonight."
        elif abbr in tonight_home:
            body += f" Host {tonight_home[abbr]} tonight."
        else:
            body += " Off tonight."
        summaries[abbr] = body
    return summaries


def extract_style_block() -> str:
    text = REF_HTML.read_text(encoding="utf-8")
    match = re.search(r"<style>(.*?)</style>", text, re.DOTALL)
    if not match:
        raise RuntimeError("Could not extract <style> from reference HTML")
    return match.group(1)


def extract_footer_scripts() -> str:
    text = REF_HTML.read_text(encoding="utf-8")
    match = re.search(r"(<script>\nwindow\.SCOREBOOK_BEEHIIV.*?</html>)", text, re.DOTALL)
    if not match:
        raise RuntimeError("Could not extract footer scripts from reference HTML")
    return match.group(1).replace("2026-10-05", ISSUE_DATE)


def clip_html(key: str, *, video: bool = True) -> str:
    clip = CLIPS[key]
    if video and clip.get("video"):
        return f"""<figure class="clip">
  <video controls playsinline preload="metadata" src="{clip['video']}"></video>
  <figcaption><a href="https://www.mlb.com/video/{clip['slug']}">Film Room</a> · MLB Film Room stream</figcaption>
</figure>"""
    return f"""<figure class="clip">
  <figcaption><a href="https://www.mlb.com/video/{clip['slug']}">Film Room</a> · MLB Film Room</figcaption>
</figure>"""


def hot_innings(innings: list[int]) -> set[int]:
    if not innings:
        return set()
    mx = max(innings)
    if mx <= 0:
        return set()
    return {i for i, runs in enumerate(innings) if runs == mx}


def inn_cell(runs: int, idx: int, hot: set[int]) -> str:
    cls = ' class="inn hot"' if idx in hot else ' class="inn"'
    return f"<td{cls}>{runs}</td>"


def render_line_score(game: dict) -> str:
    away = game["away"]
    home = game["home"]
    away_inn = game["awayInn"]
    home_inn = game["homeInn"]
    n = max(len(away_inn), len(home_inn))
    away_hot = hot_innings(away_inn)
    home_hot = hot_innings(home_inn)
    headers = "".join(f'<th class="inn">{i + 1}</th>' for i in range(n))
    away_cells = "".join(
        inn_cell(away_inn[i] if i < len(away_inn) else 0, i, away_hot) for i in range(n)
    )
    home_cells = "".join(
        inn_cell(home_inn[i] if i < len(home_inn) else 0, i, home_hot) for i in range(n)
    )
    return (
        f'<table class="ls"><tr><th class="tm"></th>{headers}'
        f'<th class="tot rhe">R</th><th class="tot">H</th><th class="tot">E</th></tr>'
        f'<tr data-team="{away}"><td class="tm">{away}</td>{away_cells}'
        f'<td class="tot rhe">{game["awayScore"]}</td><td class="tot">{game["awayH"]}</td>'
        f'<td class="tot">{game["awayE"]}</td></tr>'
        f'<tr data-team="{home}"><td class="tm">{home}</td>{home_cells}'
        f'<td class="tot rhe">{game["homeScore"]}</td><td class="tot">{game["homeH"]}</td>'
        f'<td class="tot">{game["homeE"]}</td></tr></table>'
    )


def game_heading(game: dict) -> str:
    away = game["away"]
    home = game["home"]
    away_score = game["awayScore"]
    home_score = game["homeScore"]
    if home_score > away_score:
        return f"{home} {home_score}, {away} {away_score}"
    return f"{away} {away_score}, {home} {home_score}"


def render_game(game: dict) -> str:
    heading = game_heading(game)
    line_score = render_line_score(game)
    return (
        f'  <details class="game" data-away-team="{game["away"]}" data-home-team="{game["home"]}">'
        f'<summary><span class="hint"></span><h3>{heading}</h3><div class="scroll">{line_score}</div>'
        f'<p class="wl">{game["note"]}</p></summary></details>'
    )


def standings_row(cols: tuple, wc: bool = False) -> str:
    if wc:
        tm, w, l, wcgb, strk, l10, rd, cut = cols
        tr_cls = ' class="cut"' if cut else ""
        return (
            f'<tr{tr_cls} data-team="{tm}"><td class="tm">{tm}</td><td>{w}</td><td>{l}</td>'
            f"<td>{wcgb}</td><td>{strk}</td><td>{l10}</td><td>{rd}</td></tr>\n"
        )
    tm, w, l, gb, wcgb, strk, l10, rd = cols
    return (
        f'<tr data-team="{tm}"><td class="tm">{tm}</td><td>{w}</td><td>{l}</td><td>{gb}</td>'
        f"<td>{wcgb}</td><td>{strk}</td><td>{l10}</td><td>{rd}</td></tr>\n"
    )


def standings_table(title: str, rows: list, card: str, wc: bool = False) -> str:
    if wc:
        head = "<th>Tm</th><th>W</th><th>L</th><th>WCGB</th><th>Strk</th><th>L10</th><th>RD</th>"
    else:
        head = "<th>Tm</th><th>W</th><th>L</th><th>GB</th><th>WCGB</th><th>Strk</th><th>L10</th><th>RD</th>"
    body = "".join(standings_row(row, wc=wc) for row in rows)
    return f"""      <div class="table-block" data-share-card="{card}">
      <div class="div">{title}</div>
      <div class="scroll"><table class="st"><thead><tr>{head}</tr></thead><tbody>
{body}</tbody></table></div>
      </div>"""


def render_pitchers(rows: list[tuple]) -> str:
    html_rows = []
    for idx, (name, tm, gs, ip, h, er, bb, k, opp) in enumerate(rows, 1):
        hi = ' class="hi"' if idx == 1 else ""
        html_rows.append(
            f'<tr><td>{idx}</td><td class="name">{name}</td><td>{tm}</td><td{hi}>{gs}</td>'
            f"<td>{ip}</td><td>{h}</td><td>{er}</td><td>{bb}</td><td>{k}</td><td>{opp}</td></tr>"
        )
    return "\n".join(html_rows)


def render_hitters(rows: list[tuple]) -> str:
    html_rows = []
    for idx, (name, tm, tb, ab, h, xbh, hr, rbi, sb) in enumerate(rows, 1):
        hi = ' class="hi"' if idx == 1 else ""
        html_rows.append(
            f'<tr><td>{idx}</td><td class="name">{name}</td><td>{tm}</td><td{hi}>{tb}</td>'
            f"<td>{ab}</td><td>{h}</td><td>{xbh}</td><td>{hr}</td><td>{rbi}</td><td>{sb}</td></tr>"
        )
    return "\n".join(html_rows)


def render_upcoming(rows: list[dict]) -> str:
    parts = []
    for item in rows:
        note_bit = f" ({item['note']})" if item.get("note") else ""
        parts.append(
            f'    <article class="upcoming-game" data-away-team="{item["away"]}" data-home-team="{item["home"]}">\n'
            f"      <p><strong>{item['pitchers']}</strong> — {item['away']} at {item['home']}, "
            f'<time datetime="{item["startIso"]}">{item["startTime"]}</time>{note_bit}.</p>\n'
            f"    </article>"
        )
    return "\n".join(parts)


def issue_json(
    games: list[dict],
    upcoming: list[dict],
    off_tonight: list[str],
    team_summaries: dict[str, str],
) -> str:
    all_games = [
        {
            "away": g["away"],
            "home": g["home"],
            "awayScore": g["awayScore"],
            "homeScore": g["homeScore"],
            "note": g["note"],
        }
        for g in games
    ]
    payload = {
        "date": ISSUE_DATE,
        "allGames": all_games,
        "upcomingGames": upcoming,
        "offTonight": off_tonight,
        "teamSummaries": team_summaries,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def write_race_share_files() -> None:
    share = OUT_DIR / "share"
    share.mkdir(parents=True, exist_ok=True)
    (share / "race-al.txt").write_text(
        f"{RACE_AL_RECAP}\n\nSince Aug 13: {RACE_AL_SINCE}\n\n"
        f"powered by getscorebook.com\n{ISSUE_URL}/#the-race\n",
        encoding="utf-8",
    )
    (share / "race-nl.txt").write_text(
        f"Last night: {RACE_NL_RECAP}\n\nSince Aug 13: {RACE_NL_SINCE}\n\n"
        f"powered by getscorebook.com\n{ISSUE_URL}/#the-race\n",
        encoding="utf-8",
    )


def copy_assets() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("favicon.png", "favicon-32.png", "apple-touch.png", "og.png"):
        shutil.copy2(TEMPLATE_DIR / name, OUT_DIR / name)


def render_tonight(upcoming: list[dict]) -> str:
    if upcoming:
        return render_upcoming(upcoming)
    return (
        "    <p>No MLB games scheduled tonight — postseason off day.</p>\n"
        "    <p class=\"subn\">ALDS Game 3 Wednesday: Guardians at White Sox (4:00 PM ET); Rays at Yankees (8:00 PM ET).</p>"
    )


def build_html(
    games: list[dict],
    hitters: list[tuple],
    pitchers: list[tuple],
    upcoming: list[dict],
    off_tonight: list[str],
    team_summaries: dict[str, str],
    streaks: dict[int, str],
    data: dict,
) -> str:
    style = extract_style_block()
    footer = extract_footer_scripts()
    all_games_html = "\n".join(render_game(g) for g in games)
    cancelled_html = render_cancelled(data)
    if cancelled_html:
        all_games_html = f"{all_games_html}\n{cancelled_html}"

    hitter_rows = [
        (name, tm, tb, ab, h, xbh, hr, rbi, sb)
        for tb, hr, rbi, h, sb, name, tm, ab, xbh in hitters
    ]
    pitcher_rows = [
        (name, tm, gs, ip, h, er, bb, k, opp)
        for gs, name, tm, ip, h, er, bb, k, opp in pitchers
    ]

    al_divs = [d for d in data["standings"] if d["division"].startswith("AL")]
    nl_divs = [d for d in data["standings"] if d["division"].startswith("NL")]

    al_tables = ""
    for division in al_divs:
        slug = division["division"].lower().replace(" ", "-")
        al_tables += standings_table(
            division["division"],
            division_rows(division, streaks),
            f"{slug}.png",
        )
    al_tables += series_table(
        "AL Division Series",
        AL_DS_SERIES,
        "al-ds.png",
    )

    nl_tables = ""
    for division in nl_divs:
        slug = division["division"].lower().replace(" ", "-")
        nl_tables += standings_table(
            division["division"],
            division_rows(division, streaks),
            f"{slug}.png",
        )
    nl_tables += series_table(
        "NL Division Series",
        NL_DS_SERIES,
        "nl-ds.png",
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Scorebook - Tuesday, October 6</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Tuesday, October 6" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Tuesday, October 6" />
<meta name="twitter:description" content="{DEK}" />
<meta name="twitter:image" content="{ISSUE_URL}/og.png" />
<link rel="icon" href="favicon.png" type="image/png" />
<link rel="icon" href="favicon-32.png" type="image/png" sizes="32x32" />
<link rel="apple-touch-icon" href="apple-touch.png" />
<link rel="stylesheet" href="/css/team-preferences.css" />
<style>{style}
</style>
</head>
<body>
<header class="site">
  <div class="site-brand">
    <div class="cell"><span>SB</span></div>
    <div><span class="site-name">Scorebook</span>
      <span class="site-tag">The games you didn't watch.</span></div>
  </div>
</header>
<article class="page">
  <p class="kicker">Tuesday night</p>
  <h1>Tuesday, October 6</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("kike_hr")}
  <p class="cap">{CLIPS["kike_hr"]["cap"]}</p>
{clip_html("yamamoto")}
  <p class="cap">{CLIPS["yamamoto"]["cap"]}</p>
{clip_html("cronenworth")}
  <p class="cap">{CLIPS["cronenworth"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="kike_hr" required> Enrique Hernández two-run homer</label>
      <label><input type="radio" name="play" value="yamamoto"> Yoshinobu Yamamoto 10 strikeouts</label>
      <label><input type="radio" name="play" value="cronenworth"> Jake Cronenworth solo homer</label>
      <label><input type="radio" name="play" value="other"> Something else</label>
      <button type="submit">Vote</button>
    </form>
    <div id="potn-results" hidden></div>
  </div>

  </section>

  <aside class="sb-subscribe" id="subscribe">
  <p class="sb-sub-kicker">Subscribe</p>
  <p class="sb-sub-lead">The games you didn't watch, every morning.</p>
  <div class="sb-beehiiv">
    <script async src="https://subscribe-forms.beehiiv.com/v3/loader.js" data-beehiiv-form="{BEEHIIV_FORM}"></script>
  </div>
</aside>

  <section class="shareable" id="thats-baseball">
  <h2>That's baseball</h2>
{clip_html("dubon_rob")}
  <p class="cap">{CLIPS["dubon_rob"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Top of the fourth at Truist Park, still scoreless. Andy Pages singled, Enrique Hernández homered (two-run), and Freddie Freeman followed with a solo shot — three runs in the frame. Yoshinobu Yamamoto and Edwin Díaz made it stand up. Dodgers 3, Braves 1.</p>
{clip_html("fourth_inning")}
  <p class="cap">{CLIPS["fourth_inning"]["cap"]}</p>

  </section>

  <section class="shareable" id="top-performers">
  <h2>Top performers</h2>
  <p class="subn">Pitchers · Bill James game score, 5+ IP</p>
  <div class="scroll" data-share-card="pitchers.png">
  <table class="lb">
    <thead><tr><th>#</th><th>Name</th><th>Tm</th><th>GS</th><th>IP</th><th>H</th><th>ER</th><th>BB</th><th>K</th><th>Opp</th></tr></thead>
    <tbody>
{render_pitchers(pitcher_rows)}
    </tbody>
  </table>
  </div>
  <p class="subn">Hitters · ranked by total bases, then HR, RBI, H, SB</p>
  <div class="scroll" data-share-card="hitters.png">
  <table class="lb">
    <thead><tr><th>#</th><th>Name</th><th>Tm</th><th>TB</th><th>AB</th><th>H</th><th>XBH</th><th>HR</th><th>RBI</th><th>SB</th></tr></thead>
    <tbody>
{render_hitters(hitter_rows)}
    </tbody>
  </table>
  </div>
  <p class="cap">Pitchers by Bill James game score, 5+ IP. Hitters by total bases. XBH is 2B + 3B + HR.</p>

  </section>

  <section class="shareable" id="the-race">
  <h2 id="race">The race</h2>
  <div class="league-tabs">
    <input type="radio" name="league" id="tab-al" checked>
    <input type="radio" name="league" id="tab-nl">
    <div class="tab-bar" role="tablist">
      <label for="tab-al">AL</label>
      <label for="tab-nl">NL</label>
    </div>

    <div class="panel-al">
      <div class="recap" data-share-card="race-al.png" data-share-text-src="share/race-al.txt">
        <p class="subn">Last night</p>
        <p>{RACE_AL_RECAP}</p>
        <p class="subn">Postseason</p>
        <p>{RACE_AL_SINCE}</p>
      </div>
      <p class="subn">Final regular-season standings through Sunday, September 27. L10 is the last ten games. RD is run differential. Division Series table is best-of-five wins.</p>
{al_tables}
    </div>

    <div class="panel-nl" id="nl-panel">
      <div class="recap" data-share-card="race-nl.png" data-share-text-src="share/race-nl.txt">
        <p class="subn">Last night</p>
        <p>{RACE_NL_RECAP}</p>
        <p class="subn">Postseason</p>
        <p>{RACE_NL_SINCE}</p>
      </div>
      <p class="subn">Final regular-season standings through Sunday, September 27. L10 is the last ten games. RD is run differential. Division Series table is best-of-five wins.</p>
{nl_tables}
    </div>
  </div>

  </section>

  <section class="shareable" id="the-games">
  <h2>The games</h2>
  <p class="subn">Team, runs, hits, errors. Tap a box and the innings fill in.</p>
{all_games_html}

  </section>

  <section class="shareable" id="tonight">
  <h2>Tonight</h2>
  <div class="tonight" id="tonight-games">
{render_tonight(upcoming)}
  </div>

  </section>

  <aside class="sb-subscribe">
  <p class="sb-sub-kicker">Subscribe</p>
  <p class="sb-sub-lead">The games you didn't watch, every morning.</p>
  <div class="sb-beehiiv">
    <script async src="https://subscribe-forms.beehiiv.com/v3/loader.js" data-beehiiv-form="{BEEHIIV_FORM}"></script>
  </div>
</aside>

  <p class="foot">Clips stream from MLB Film Room. We do not rehost the files. Pitchers by game score (5+ IP). Hitters by total bases.</p>
<script type="application/json" id="scorebook-issue-data">
{issue_json(games, upcoming, off_tonight, team_summaries)}
</script>
</article>

{footer}
"""


def main() -> None:
    data = load_data()
    streaks = fetch_streaks()
    games = build_games(data)
    hitters = build_hitters(data)
    pitchers = build_pitchers(data)
    upcoming = build_upcoming(data)
    off_tonight = sorted(norm_from_id(team["id"]) for team in data["offTonight"])
    team_summaries = build_team_summaries(data, upcoming)
    for abbr, text in TEAM_SUMMARY_OVERRIDES.items():
        team_summaries[abbr] = text

    copy_assets()
    html_path = OUT_DIR / "index.html"
    html_path.write_text(
        build_html(
            games,
            hitters,
            pitchers,
            upcoming,
            off_tonight,
            team_summaries,
            streaks,
            data,
        ),
        encoding="utf-8",
    )
    write_race_share_files()
    share = OUT_DIR / "share"
    share.mkdir(parents=True, exist_ok=True)
    render_src = TEMPLATE_DIR / "share" / "render_share_cards.py"
    (share / "render_share_cards.py").write_text(
        render_src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    print(f"Wrote {html_path}")
    print(f"Games: {len(games)}")
    print(f"Hitters: {len(hitters)} Pitchers: {len(pitchers)}")
    print(f"Tonight: {len(upcoming)} Off tonight: {off_tonight}")


if __name__ == "__main__":
    main()
