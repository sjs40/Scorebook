#!/usr/bin/env python3
"""Generate /workspace/2026-09-10/index.html and share race text files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-10"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-09-09" / "index.html"
ISSUE_DATE = "2026-09-10"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Anthony Volpe returned with a grand slam and five RBIs in a six-run seventh as the Yankees swept Colorado 10–3. "
    "Cam Smith's ninth-inning homer off Jhoan Duran lifted Houston past Philadelphia 2–1. "
    "Atlanta scored three in the eighth to deny Tampa Bay a playoff clinch, 3–1. "
    "Jared Jones flirted with a no-hitter and Julio Rodríguez's three-run shot lifted Seattle past Texas 4–3."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/10"

CLIPS = {
    "volpe": {
        "video": f"{MLB_CDN}/1e7df880-88098f98-89a477db-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "anthony-volpe-returns-with-a-grand-slam",
        "cap": (
            "Anthony Volpe: grand slam in his return, five RBIs on the night. "
            "Yankees 10, Rockies 3 — New York completed a three-game sweep."
        ),
    },
    "smith": {
        "video": f"{MLB_CDN}/331809f4-108128c6-51b8aa88-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "jhoan-duran-in-play-run-s-to-cam-smith-x0891",
        "cap": (
            "Cam Smith: tiebreaking solo homer in the ninth off Jhoan Duran. "
            "Astros 2, Phillies 1 — Houston took two of three in Philadelphia."
        ),
    },
    "jrod": {
        "video": f"{MLB_CDN}/fe5739e4-ceacd692-e29d7a07-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "julio-rodriguez-homers-21-on-a-line-drive-to-left-center-field-dominic-canzone-s",
        "cap": (
            "Julio Rodríguez: go-ahead three-run homer in the seventh. "
            "Mariners 4, Rangers 3 — Seattle scored four in the frame after trailing 3–0."
        ),
    },
    "jones": {
        "video": f"{MLB_CDN}/293cdee7-e372493a-a63a336e-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "jared-jones-flirts-with-no-hitter-fans-eight",
        "cap": (
            "Jared Jones: seven innings, one hit, eight strikeouts — no-hitter broken up in the seventh. "
            "That's baseball."
        ),
    },
    "yankees_seventh": {
        "video": f"{MLB_CDN}/82a3d660-3e5a5788-01370eea-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "anthony-volpe-hits-a-grand-slam-2-to-right-field-spencer-jones-scores-rya",
        "cap": (
            "Six runs in the bottom of the seventh — Volpe's grand slam capped the rally "
            "after McCarthy's RBI triple and Spencer Jones's two-run single."
        ),
    },
}

PITCHERS = [
    ("Jacob deGrom", "TEX", 76, "6.0", 1, 0, 0, 12, "SEA"),
    ("Jared Jones", "PIT", 73, "7.0", 1, 0, 2, 8, "CHW"),
    ("Logan Gilbert", "SEA", 62, "7.0", 3, 3, 2, 11, "TEX"),
    ("Martín Pérez", "ATL", 57, "7.0", 4, 0, 2, 4, "TBR"),
]

HITTERS = [
    ("Anthony Volpe", "NYY", 6, 4, 3, 1, 1, 5, 1),
    ("Oneil Cruz", "PIT", 6, 4, 3, 1, 1, 2, 0),
    ("Cam Smith", "HOU", 5, 3, 2, 1, 1, 1, 0),
    ("Julio Rodríguez", "SEA", 4, 3, 1, 1, 1, 3, 0),
    ("Joc Pederson", "TEX", 4, 3, 1, 1, 1, 2, 0),
    ("Luis García Jr.", "NYY", 4, 5, 1, 1, 1, 2, 0),
    ("Victor Mesa Jr.", "TBR", 4, 1, 1, 1, 1, 1, 0),
    ("Kyle Karros", "COL", 4, 4, 1, 1, 1, 1, 0),
]

# away, home, away_score, home_score, away_innings, home_innings, away_h, away_e, home_h, home_e, note
GAMES = [
    ("TBR", "ATL", 1, 3, [0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 3, 0], 5, 0, 7, 0, "W Didier Fuentes · L Kevin Kelly · S 32 Raisel Iglesias"),
    ("HOU", "PHI", 2, 1, [0, 1, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 1, 0, 0, 0, 0], 8, 0, 3, 1, "W Bryan Abreu · L Jhoan Duran · S 25 Josh Hader"),
    ("TEX", "SEA", 3, 4, [0, 0, 2, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 4, 0, 0], 4, 0, 4, 1, "W Logan Gilbert · L Jakob Junis · S 27 Andrés Muñoz"),
    ("COL", "NYY", 3, 10, [0, 1, 0, 0, 0, 0, 1, 1, 0], [2, 2, 0, 0, 0, 0, 6, 0, 0], 8, 0, 11, 2, "W John Schreiber · L Ryan Feltner"),
    ("PIT", "CHW", 2, 0, [0, 0, 0, 1, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], 7, 1, 2, 0, "W Jared Jones · L Erick Fedde · S 12 Mason Montgomery"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 87, 59, "--", "--", "L1", "5-5", "+56"),
        ("NYY", 84, 62, "3", "+10.5", "W3", "7-3", "+131"),
        ("BOS", 80, 67, "7.5", "+6", "L2", "6-4", "+82"),
        ("TOR", 73, 74, "14.5", "1", "L1", "6-4", "-39"),
        ("BAL", 71, 76, "16.5", "3", "W1", "3-7", "-27"),
    ],
    "AL Central": [
        ("CHW", 75, 71, "--", "--", "L3", "3-7", "+39"),
        ("CLE", 74, 73, "1.5", "--", "L1", "5-5", "-16"),
        ("MIN", 69, 77, "6", "4.5", "L1", "5-5", "-53"),
        ("DET", 67, 79, "8", "6.5", "W1", "4-6", "+55"),
        ("KCR", 65, 82, "10.5", "9", "W1", "3-7", "-88"),
    ],
    "AL West": [
        ("HOU", 75, 72, "--", "--", "W1", "6-4", "-40"),
        ("TEX", 72, 75, "3", "2", "L2", "5-5", "-41"),
        ("SEA", 69, 78, "6", "5", "W2", "5-5", "-74"),
        ("ATH", 59, 88, "16", "15", "W1", "6-4", "-187"),
        ("LAA", 56, 90, "18.5", "17.5", "W2", "4-6", "-73"),
    ],
    "AL Wild Card": [
        ("NYY", 84, 62, "+10.5", "W3", "7-3", "+131", False),
        ("BOS", 80, 67, "+6", "L2", "6-4", "+82", False),
        ("CLE", 74, 73, "--", "L1", "5-5", "-16", True),
        ("TOR", 73, 74, "1", "L1", "6-4", "-39", False),
        ("TEX", 72, 75, "2", "L2", "5-5", "-41", False),
        ("BAL", 71, 76, "3", "W1", "3-7", "-27", False),
    ],
    "NL East": [
        ("ATL", 86, 61, "--", "--", "W1", "4-6", "+110"),
        ("PHI", 82, 65, "4", "+3.5", "L1", "5-5", "+37"),
        ("MIA", 72, 75, "14", "6.5", "L3", "3-7", "+7"),
        ("NYM", 68, 78, "17.5", "10", "W4", "7-3", "-40"),
        ("WSN", 67, 81, "19.5", "12", "L7", "2-8", "0"),
    ],
    "NL Central": [
        ("MIL", 91, 56, "--", "--", "W3", "6-4", "+172"),
        ("CHC", 81, 66, "10", "+2.5", "L4", "4-6", "+128"),
        ("PIT", 74, 73, "17", "4.5", "W4", "8-2", "+36"),
        ("STL", 72, 75, "19", "6.5", "L3", "4-6", "-12"),
        ("CIN", 69, 77, "21.5", "9", "L3", "5-5", "-122"),
    ],
    "NL West": [
        ("LAD", 89, 57, "--", "--", "W7", "8-2", "+169"),
        ("SDP", 78, 68, "11", "--", "W4", "6-4", "+17"),
        ("ARI", 78, 69, "11.5", "0.5", "L1", "5-5", "-1"),
        ("SFG", 62, 85, "27.5", "16.5", "W3", "6-4", "-72"),
        ("COL", 55, 91, "34", "23", "L4", "3-7", "-154"),
    ],
    "NL Wild Card": [
        ("PHI", 82, 65, "+3.5", "L1", "5-5", "+37", False),
        ("CHC", 81, 66, "+2.5", "L4", "4-6", "+128", False),
        ("SDP", 78, 68, "--", "W4", "6-4", "+17", True),
        ("ARI", 78, 69, "0.5", "L1", "5-5", "-1", False),
        ("PIT", 74, 73, "4.5", "W4", "8-2", "+36", False),
        ("MIA", 72, 75, "6.5", "L3", "3-7", "+7", False),
    ],
}

UPCOMING = [
    ("PIT", "CHC", "Wilber Dotel vs. Shota Imanaga", "2:20 PM ET", "2026-09-11T18:20:00Z", ""),
    ("COL", "DET", "Mason Adams vs. Framber Valdez", "6:40 PM ET", "2026-09-11T22:40:00Z", ""),
    ("LAA", "WSN", "Yusei Kikuchi vs. Cade Cavalli", "6:45 PM ET", "2026-09-11T22:45:00Z", ""),
    ("NYM", "NYY", "Nolan McLean vs. Carlos Rodón", "7:05 PM ET", "2026-09-11T23:05:00Z", ""),
    ("BAL", "TOR", "Chris Bassitt vs. Max Scherzer", "7:07 PM ET", "2026-09-11T23:07:00Z", ""),
    ("KCR", "BOS", "Seth Lugo vs. Sonny Gray", "7:10 PM ET", "2026-09-11T23:10:00Z", ""),
    ("HOU", "TBR", "Miguel Ullola vs. Drew Rasmussen", "7:10 PM ET", "2026-09-11T23:10:00Z", ""),
    ("LAD", "MIA", "TBD vs. Ryan Gusto", "7:10 PM ET", "2026-09-11T23:10:00Z", ""),
    ("PHI", "ATL", "Aaron Nola vs. Chris Sale", "7:15 PM ET", "2026-09-11T23:15:00Z", ""),
    ("CIN", "MIL", "Andrew Abbott vs. Dustin May", "7:45 PM ET", "2026-09-11T23:45:00Z", ""),
    ("CLE", "MIN", "Parker Messick vs. Taj Bradley", "8:10 PM ET", "2026-09-12T00:10:00Z", ""),
    ("CHW", "STL", "Anthony Kay vs. Matthew Liberatore", "8:15 PM ET", "2026-09-12T00:15:00Z", ""),
    ("TEX", "ARI", "TBD vs. TBD", "9:40 PM ET", "2026-09-12T01:40:00Z", ""),
    ("SEA", "ATH", "George Kirby vs. Jeffrey Springs", "9:40 PM ET", "2026-09-12T01:40:00Z", ""),
    ("SDP", "SFG", "Robbie Ray vs. Anthony Molina", "10:15 PM ET", "2026-09-12T02:15:00Z", ""),
]

OFF_TONIGHT: list[str] = []

TEAM_SUMMARIES = {
    "CHC": "Your Cubs: Off yesterday. Host Pittsburgh tonight.",
    "MIA": "Your Marlins: Off yesterday. Host the Dodgers tonight.",
    "SFG": "Your Giants: Off yesterday. Host San Diego tonight.",
    "NYM": "Your Mets: Off yesterday. At the Yankees tonight.",
    "ATL": "Your Braves: Pérez spun seven scoreless and a three-run eighth beat Tampa Bay 3–1. Host Philadelphia tonight.",
    "PHI": "Your Phillies: Lost 1–2 to Houston on Cam Smith's ninth-inning homer; four back in the NL East. At Atlanta tonight.",
    "DET": "Your Tigers: Off yesterday. Host Colorado tonight.",
    "CLE": "Your Guardians: Off yesterday. At Minnesota tonight.",
    "LAA": "Your Angels: Off yesterday. At Washington tonight.",
    "PIT": "Your Pirates: Jones flirted with a no-hitter and Cruz homered in a 2–0 shutout at Chicago. At the Cubs tonight.",
    "MIL": "Your Brewers: Off yesterday. Host Cincinnati tonight.",
    "CIN": "Your Reds: Off yesterday. At Milwaukee tonight.",
    "BOS": "Your Red Sox: Off yesterday. Host Kansas City tonight.",
    "BAL": "Your Orioles: Off yesterday. At Toronto tonight.",
    "TBR": "Your Rays: Lost 1–3 at Atlanta; denied a chance to clinch a playoff berth. Host Houston tonight.",
    "TEX": "Your Rangers: deGrom fanned 12 through six but Julio Rodríguez's three-run homer beat Texas 4–3. At Arizona tonight.",
    "MIN": "Your Twins: Off yesterday. Host Cleveland tonight.",
    "CHW": "Your White Sox: Shut out 0–2 by Pittsburgh; Jared Jones took a no-hitter into the seventh. At St. Louis tonight.",
    "TOR": "Your Blue Jays: Off yesterday. Host Baltimore tonight.",
    "KCR": "Your Royals: Off yesterday. At Boston tonight.",
    "ARI": "Your Diamondbacks: Off yesterday. Host Texas tonight.",
    "HOU": "Your Astros: Smith homered in the ninth to beat Philadelphia 2–1. At Tampa Bay tonight.",
    "NYY": "Your Yankees: Volpe's grand slam keyed a six-run seventh in a 10–3 sweep of Colorado. Host the Mets tonight.",
    "SDP": "Your Padres: Off yesterday. At San Francisco tonight.",
    "STL": "Your Cardinals: Off yesterday. Host the White Sox tonight.",
    "COL": "Your Rockies: Lost 3–10 at New York; Volpe's grand slam in the seventh. At Detroit tonight.",
    "WSN": "Your Nationals: Off yesterday. Host the Angels tonight.",
    "LAD": "Your Dodgers: Off yesterday. At Miami tonight.",
    "ATH": "Your Athletics: Off yesterday. Host Seattle tonight.",
    "SEA": "Your Mariners: Gilbert fanned 11 and Rodríguez's three-run homer beat Texas 4–3. At Oakland tonight.",
}

RACE_AL_RECAP = (
    "Anthony Volpe's grand slam keyed a six-run seventh as the Yankees swept Colorado 10–3, "
    "moving within three games of Tampa Bay. Cam Smith's ninth-inning homer beat Philadelphia 2–1. "
    "Julio Rodríguez's three-run shot lifted Seattle past Texas 4–3."
)
RACE_AL_SINCE = "The Yankees are 7–3 in their last ten."
RACE_NL_RECAP = (
    "Martín Pérez spun seven scoreless and Atlanta scored three in the eighth to deny Tampa Bay a clinch, 3–1. "
    "Jared Jones flirted with a no-hitter and Oneil Cruz homered as Pittsburgh shut out Chicago 2–0."
)
RACE_NL_SINCE = "Pittsburgh is 8–2 in its last ten."


def extract_style_block() -> str:
    text = REF_HTML.read_text(encoding="utf-8")
    m = re.search(r"<style>(.*?)</style>", text, re.DOTALL)
    if not m:
        raise RuntimeError("Could not extract <style> from reference HTML")
    return m.group(1)


def extract_footer_scripts() -> str:
    text = REF_HTML.read_text(encoding="utf-8")
    m = re.search(r"(<script>\nwindow\.SCOREBOOK_BEEHIIV.*?</html>)", text, re.DOTALL)
    if not m:
        raise RuntimeError("Could not extract footer scripts from reference HTML")
    return m.group(1).replace("2026-09-09", ISSUE_DATE)


def clip_html(key: str, *, video: bool = True) -> str:
    c = CLIPS[key]
    if video and c.get("video"):
        return f"""<figure class="clip">
  <video controls playsinline preload="metadata" src="{c['video']}"></video>
  <figcaption><a href="https://www.mlb.com/video/{c['slug']}">Film Room</a> · MLB Film Room stream</figcaption>
</figure>"""
    return f"""<figure class="clip">
  <figcaption><a href="https://www.mlb.com/video/{c['slug']}">Film Room</a> · MLB Film Room</figcaption>
</figure>"""


def hot_innings(innings: list[int]) -> set[int]:
    if not innings:
        return set()
    mx = max(innings)
    if mx <= 0:
        return set()
    return {i for i, r in enumerate(innings) if r == mx}


def inn_cell(runs: int, idx: int, hot: set[int]) -> str:
    cls = ' class="inn hot"' if idx in hot else ' class="inn"'
    return f"<td{cls}>{runs}</td>"


def render_line_score(
    away: str,
    home: str,
    away_inn: list[int],
    home_inn: list[int],
    away_r: int,
    home_r: int,
    away_h: int,
    away_e: int,
    home_h: int,
    home_e: int,
) -> str:
    n = max(len(away_inn), len(home_inn))
    away_hot = hot_innings(away_inn)
    home_hot = hot_innings(home_inn)
    headers = "".join(f'<th class="inn">{i + 1}</th>' for i in range(n))
    away_cells = "".join(inn_cell(away_inn[i] if i < len(away_inn) else 0, i, away_hot) for i in range(n))
    home_cells = "".join(inn_cell(home_inn[i] if i < len(home_inn) else 0, i, home_hot) for i in range(n))
    return (
        f'<table class="ls"><tr><th class="tm"></th>{headers}'
        f'<th class="tot rhe">R</th><th class="tot">H</th><th class="tot">E</th></tr>'
        f'<tr data-team="{away}"><td class="tm">{away}</td>{away_cells}'
        f'<td class="tot rhe">{away_r}</td><td class="tot">{away_h}</td><td class="tot">{away_e}</td></tr>'
        f'<tr data-team="{home}"><td class="tm">{home}</td>{home_cells}'
        f'<td class="tot rhe">{home_r}</td><td class="tot">{home_h}</td><td class="tot">{home_e}</td></tr></table>'
    )


def game_heading(away: str, home: str, away_score: int, home_score: int) -> str:
    if home_score > away_score:
        return f"{home} {home_score}, {away} {away_score}"
    return f"{away} {away_score}, {home} {home_score}"


def render_game(g: tuple) -> str:
    away, home, as_, hs, ai, hi, ah, ae, hh, he, note = g
    h3 = game_heading(away, home, as_, hs)
    ls = render_line_score(away, home, ai, hi, as_, hs, ah, ae, hh, he)
    return (
        f'  <details class="game" data-away-team="{away}" data-home-team="{home}">'
        f'<summary><span class="hint"></span><h3>{h3}</h3><div class="scroll">{ls}</div>'
        f'<p class="wl">{note}</p></summary></details>'
    )


def standings_row(cols: tuple, wc: bool = False) -> str:
    if wc:
        tm, w, l, wcgb, strk, l10, rd, cut = cols
        tr_cls = ' class="cut"' if cut else ""
        return (
            f'<tr{tr_cls} data-team="{tm}"><td class="tm">{tm}</td><td>{w}</td><td>{l}</td>'
            f'<td>{wcgb}</td><td>{strk}</td><td>{l10}</td><td>{rd}</td></tr>\n'
        )
    tm, w, l, gb, wcgb, strk, l10, rd = cols
    return (
        f'<tr data-team="{tm}"><td class="tm">{tm}</td><td>{w}</td><td>{l}</td><td>{gb}</td>'
        f'<td>{wcgb}</td><td>{strk}</td><td>{l10}</td><td>{rd}</td></tr>\n'
    )


def standings_table(title: str, rows: list, card: str, wc: bool = False) -> str:
    if wc:
        head = "<th>Tm</th><th>W</th><th>L</th><th>WCGB</th><th>Strk</th><th>L10</th><th>RD</th>"
    else:
        head = "<th>Tm</th><th>W</th><th>L</th><th>GB</th><th>WCGB</th><th>Strk</th><th>L10</th><th>RD</th>"
    body = "".join(standings_row(r, wc=wc) for r in rows)
    return f"""      <div class="table-block" data-share-card="{card}">
      <div class="div">{title}</div>
      <div class="scroll"><table class="st"><thead><tr>{head}</tr></thead><tbody>
{body}</tbody></table></div>
      </div>"""


def render_pitchers() -> str:
    rows = []
    for i, (name, tm, gs, ip, h, er, bb, k, opp) in enumerate(PITCHERS, 1):
        hi = ' class="hi"' if i == 1 else ""
        rows.append(
            f'<tr><td>{i}</td><td class="name">{name}</td><td>{tm}</td><td{hi}>{gs}</td>'
            f"<td>{ip}</td><td>{h}</td><td>{er}</td><td>{bb}</td><td>{k}</td><td>{opp}</td></tr>"
        )
    return "\n".join(rows)


def render_hitters() -> str:
    rows = []
    for i, (name, tm, tb, ab, h, xbh, hr, rbi, sb) in enumerate(HITTERS, 1):
        hi = ' class="hi"' if i == 1 else ""
        rows.append(
            f'<tr><td>{i}</td><td class="name">{name}</td><td>{tm}</td><td{hi}>{tb}</td>'
            f"<td>{ab}</td><td>{h}</td><td>{xbh}</td><td>{hr}</td><td>{rbi}</td><td>{sb}</td></tr>"
        )
    return "\n".join(rows)


def render_upcoming() -> str:
    parts = []
    for away, home, pitchers, start_time, start_iso, note in UPCOMING:
        note_bit = f" ({note})" if note else ""
        parts.append(
            f'    <article class="upcoming-game" data-away-team="{away}" data-home-team="{home}">\n'
            f"      <p><strong>{pitchers}</strong> — {away} at {home}, "
            f'<time datetime="{start_iso}">{start_time}</time>{note_bit}.</p>\n'
            f"    </article>"
        )
    return "\n".join(parts)


def issue_json() -> str:
    all_games = []
    for away, home, as_, hs, *_rest, note in GAMES:
        all_games.append({
            "away": away,
            "home": home,
            "awayScore": as_,
            "homeScore": hs,
            "note": note,
        })
    upcoming = []
    for away, home, pitchers, start_time, start_iso, note in UPCOMING:
        upcoming.append({
            "away": away,
            "home": home,
            "pitchers": pitchers,
            "startTime": start_time,
            "startIso": start_iso,
            "note": note,
        })
    data = {
        "date": ISSUE_DATE,
        "allGames": all_games,
        "upcomingGames": upcoming,
        "offTonight": OFF_TONIGHT,
        "teamSummaries": TEAM_SUMMARIES,
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


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


def build_html() -> str:
    style = extract_style_block()
    footer = extract_footer_scripts()
    all_games_html = "\n".join(render_game(g) for g in GAMES)

    al_tables = (
        standings_table("AL East", STANDINGS["AL East"], "al-east.png")
        + standings_table("AL Central", STANDINGS["AL Central"], "al-central.png")
        + standings_table("AL West", STANDINGS["AL West"], "al-west.png")
        + standings_table("AL Wild Card", STANDINGS["AL Wild Card"], "al-wc.png", wc=True)
    )
    nl_tables = (
        standings_table("NL East", STANDINGS["NL East"], "nl-east.png")
        + standings_table("NL Central", STANDINGS["NL Central"], "nl-central.png")
        + standings_table("NL West", STANDINGS["NL West"], "nl-west.png")
        + standings_table("NL Wild Card", STANDINGS["NL Wild Card"], "nl-wc.png", wc=True)
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Scorebook - Thursday, September 10</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Thursday, September 10" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Thursday, September 10" />
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
  <p class="kicker">Thursday night</p>
  <h1>Thursday, September 10</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("volpe")}
  <p class="cap">{CLIPS["volpe"]["cap"]}</p>
{clip_html("smith")}
  <p class="cap">{CLIPS["smith"]["cap"]}</p>
{clip_html("jrod")}
  <p class="cap">{CLIPS["jrod"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="volpe" required> Volpe's grand slam in his return</label>
      <label><input type="radio" name="play" value="smith"> Cam Smith's 9th-inning homer</label>
      <label><input type="radio" name="play" value="jrod"> Julio Rodríguez's 3-run homer</label>
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
{clip_html("jones")}
  <p class="cap">{CLIPS["jones"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Bottom of the seventh at Yankee Stadium. Jake McCarthy's RBI triple cut the lead to 4–2, Spencer Jones singled home two, and Anthony Volpe — recalled earlier in the day — lined a grand slam over the short porch to make it 10–2. The Yankees had already led 4–2; six runs crossed in the frame.</p>
{clip_html("yankees_seventh")}
  <p class="cap">{CLIPS["yankees_seventh"]["cap"]}</p>

  </section>

  <section class="shareable" id="top-performers">
  <h2>Top performers</h2>
  <p class="subn">Pitchers · Bill James game score, 5+ IP</p>
  <div class="scroll" data-share-card="pitchers.png">
  <table class="lb">
    <thead><tr><th>#</th><th>Name</th><th>Tm</th><th>GS</th><th>IP</th><th>H</th><th>ER</th><th>BB</th><th>K</th><th>Opp</th></tr></thead>
    <tbody>
{render_pitchers()}
    </tbody>
  </table>
  </div>
  <p class="subn">Hitters · ranked by total bases, then HR, RBI, H, SB</p>
  <div class="scroll" data-share-card="hitters.png">
  <table class="lb">
    <thead><tr><th>#</th><th>Name</th><th>Tm</th><th>TB</th><th>AB</th><th>H</th><th>XBH</th><th>HR</th><th>RBI</th><th>SB</th></tr></thead>
    <tbody>
{render_hitters()}
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
        <p class="subn">Since August 13</p>
        <p>{RACE_AL_SINCE}</p>
      </div>
      <p class="subn">Standings through Thursday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
{al_tables}
    </div>

    <div class="panel-nl" id="nl-panel">
      <div class="recap" data-share-card="race-nl.png" data-share-text-src="share/race-nl.txt">
        <p class="subn">Last night</p>
        <p>{RACE_NL_RECAP}</p>
        <p class="subn">Since August 13</p>
        <p>{RACE_NL_SINCE}</p>
      </div>
      <p class="subn">Standings through Thursday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
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
{render_upcoming()}
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
{issue_json()}
</script>
</article>

{footer}
"""


def main() -> None:
    copy_assets()
    html_path = OUT_DIR / "index.html"
    html_path.write_text(build_html(), encoding="utf-8")
    write_race_share_files()
    share = OUT_DIR / "share"
    share.mkdir(parents=True, exist_ok=True)
    render_src = TEMPLATE_DIR / "share" / "render_share_cards.py"
    (share / "render_share_cards.py").write_text(
        render_src.read_text(encoding="utf-8"), encoding="utf-8"
    )
    print(f"Wrote {html_path}")
    print(f"Wrote {OUT_DIR / 'share' / 'race-al.txt'}")
    print(f"Wrote {OUT_DIR / 'share' / 'race-nl.txt'}")


if __name__ == "__main__":
    main()
