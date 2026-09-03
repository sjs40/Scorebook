#!/usr/bin/env python3
"""Generate /workspace/2026-09-02/index.html and share race text files."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-02"
REF_HTML = ROOT / "2026-09-01" / "index.html"
ISSUE_DATE = "2026-09-02"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Ronald Acuña Jr. became the fastest to 200 homers and 200 steals. "
    "Dylan Cease and Toronto shut out Cleveland 11-0. "
    "Detroit scored five in the 12th. Athletics hit five home runs in Arlington."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/02"

CLIPS = {
    "acuna": {
        "video": f"{MLB_CDN}/38670fb6-7db498a7-a8d2413a-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "ronald-acuna-jr-hits-his-200th-career-homer-in-win",
        "cap": "Ronald Acuña Jr.: 200th career homer, 200th steal club. Fastest ever. Braves 9, Nationals 0.",
    },
    "cease": {
        "video": f"{MLB_CDN}/5944c3d6-13578d38-1896e60b-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "dylan-cease-throws-six-scoreless-innings",
        "cap": "Dylan Cease: 6.0 IP, 4 H, 0 ER, 4 K. Blue Jays 11, Guardians 0.",
    },
    "guerrero": {
        "video": f"{MLB_CDN}/a5bc853b-445d919c-b057744c-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "vladimir-guerrero-jr-homers-8-on-a-fly-ball-to-left-field-brett-bateman-s",
        "cap": "Vladimir Guerrero Jr. three-run homer, five RBIs. Blue Jays 11, Guardians 0.",
    },
    "genao": {
        "video": f"{MLB_CDN}/0d2775b9-4220a7a7-13fb5d20-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "joey-cantillo-in-play-run-s-to-george-springer",
        "cap": "Angel Genao's throw to second sailed into center. Two runs score. Blue Jays led 3-0 and never looked back.",
    },
    "det_twelfth": {
        "video": f"{MLB_CDN}/a3d71db1-1d28517c-3a983bc3-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "spencer-torkelson-s-12th-inning-homer-leads-to-win",
        "cap": "Five runs in the 12th. Spencer Torkelson homered. Tigers 11, Twins 6.",
    },
}

PITCHERS = [
    ("Cam Schlittler", "NYY", 130, "8.0", 2, 1, 0, 9, "LAA"),
    ("Andrew Painter", "PHI", 117, "7.0", 2, 0, 0, 6, "ARI"),
    ("Hayden Wesneski", "HOU", 117, "7.0", 1, 0, 2, 5, "CWS"),
    ("Trevor Rogers", "BAL", 104, "6.2", 6, 2, 0, 11, "COL"),
]

HITTERS = [
    ("Henry Bolte", "ATH", 9, 4, 3, 2, 2, 4, 1),
    ("Carter Jensen", "KCR", 8, 4, 2, 2, 2, 2, 0),
    ("Jackson Chourio", "MIL", 8, 6, 4, 2, 1, 1, 0),
    ("Vladimir Guerrero Jr.", "TOR", 7, 4, 3, 2, 1, 5, 0),
    ("JJ Bleday", "CIN", 7, 4, 3, 2, 1, 2, 0),
    ("Ronald Acuña Jr.", "ATL", 6, 5, 3, 1, 1, 3, 1),
    ("Alika Williams", "ATH", 6, 4, 2, 2, 1, 2, 0),
    ("Mookie Betts", "LAD", 6, 6, 3, 2, 1, 1, 0),
]

# away, home, away_score, home_score, away_innings, home_innings, away_h, away_e, home_h, home_e, note
GAMES = [
    ("SDP", "CIN", 3, 7, [2, 1, 0, 0, 0, 0, 0, 0, 0], [0, 4, 0, 0, 0, 1, 2, 0, 0], 7, 1, 10, 0, "W Williamson · L Mize"),
    ("ATL", "WSN", 9, 0, [0, 0, 0, 0, 0, 3, 3, 2, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0], 11, 0, 2, 1, "W Elieser Hernández · L Riley Cornelio"),
    ("ATH", "TEX", 9, 2, [0, 0, 3, 2, 3, 0, 1, 0, 0], [1, 1, 0, 0, 0, 0, 0, 0, 0], 14, 1, 8, 0, "W Jacob Lopez · L Cody Bradford"),
    ("BAL", "COL", 5, 6, [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 2], [0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 3], 10, 0, 12, 1, "W Blas Castaño · L Grant Wolfram"),
    ("PHI", "ARI", 0, 1, [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 0], 3, 1, 3, 0, "W Jonathan Loáisiga · L Jonathan Bowlan · S Juan Morillo"),
    ("SEA", "BOS", 8, 3, [0, 0, 4, 0, 0, 4, 0, 0, 0], [0, 0, 0, 1, 0, 0, 2, 0, 0], 12, 0, 12, 1, "W Cooper Criswell · L Patrick Sandoval"),
    ("TOR", "CLE", 11, 0, [1, 5, 1, 0, 0, 2, 0, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0], 15, 1, 6, 1, "W Dylan Cease · L Joey Cantillo"),
    ("SFG", "PIT", 5, 4, [1, 0, 0, 0, 2, 0, 0, 0, 0, 2], [0, 0, 0, 1, 0, 0, 1, 1, 0, 1], 7, 0, 8, 0, "W Jason Foley · L Camilo Doval · S Dylan Smith"),
    ("NYM", "TBR", 10, 4, [3, 0, 3, 0, 0, 0, 3, 1, 0], [0, 0, 1, 3, 0, 0, 0, 0, 0], 14, 1, 7, 2, "W Dedniel Núñez · L Griffin Jax"),
    ("MIL", "CHC", 9, 5, [2, 1, 0, 3, 0, 0, 1, 0, 2], [2, 3, 0, 0, 0, 0, 0, 0, 0], 14, 0, 6, 1, "W JoJo Romero · L David Peterson"),
    ("MIA", "KCR", 9, 6, [2, 0, 1, 0, 1, 3, 0, 0, 2], [5, 0, 0, 1, 0, 0, 0, 0, 0], 13, 0, 9, 0, "W Cade Gibson · L Jose Cuas · S Calvin Faucher"),
    ("DET", "MIN", 11, 6, [0, 2, 0, 0, 2, 1, 0, 0, 0, 0, 1, 5], [0, 0, 0, 1, 0, 1, 0, 3, 0, 0, 1, 0], 14, 2, 9, 1, "W Kyle Finnegan · L Tommy Nance"),
    ("CWS", "HOU", 0, 2, [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 0], 3, 0, 7, 1, "W AJ Blubaugh · L Sean Newcomb · S Josh Hader"),
    ("NYY", "LAA", 6, 3, [0, 0, 0, 1, 0, 0, 0, 0, 0, 5], [0, 0, 0, 0, 0, 0, 1, 0, 0, 2], 12, 0, 4, 0, "W David Bednar · L Luke Murphy"),
    ("STL", "LAD", 8, 6, [0, 0, 0, 0, 0, 2, 2, 1, 0, 3], [3, 0, 0, 0, 0, 2, 0, 0, 0, 1], 9, 0, 11, 0, "W Justin Bruihl · L Brock Stewart · S Riley O'Brien"),
]

FEATURED_KEYS = [
    ("ATL", "WSN"),
    ("TOR", "CLE"),
    ("DET", "MIN"),
    ("ATH", "TEX"),
    ("NYM", "TBR"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 83, 56, "--", "--", "L1", "7-3", "+51"),
        ("NYY", 80, 60, "3.5", "+9.5", "W2", "6-4", "+115"),
        ("BOS", 75, 65, "8.5", "+4.5", "L2", "4-6", "+77"),
        ("BAL", 69, 71, "14.5", "1.5", "L2", "6-4", "-20"),
        ("TOR", 69, 71, "14.5", "1.5", "W1", "6-4", "-44"),
    ],
    "AL Central": [
        ("CHW", 73, 66, "--", "--", "L1", "6-4", "+43"),
        ("CLE", 70, 69, "3.0", "--", "L1", "7-3", "-8"),
        ("MIN", 67, 73, "6.5", "3.5", "L1", "4-6", "-38"),
        ("DET", 64, 75, "9.0", "6.0", "W1", "3-7", "+47"),
        ("KCR", 62, 78, "11.5", "8.5", "L3", "6-4", "-89"),
    ],
    "AL West": [
        ("HOU", 71, 69, "--", "--", "W1", "6-4", "-42"),
        ("TEX", 69, 71, "2.0", "1.5", "L1", "5-5", "-48"),
        ("SEA", 66, 74, "5.0", "4.5", "W2", "4-6", "-65"),
        ("ATH", 54, 86, "17.0", "16.5", "W1", "4-6", "-194"),
        ("LAA", 53, 87, "18.0", "17.5", "L2", "1-9", "-80"),
    ],
    "AL Wild Card": [
        ("NYY", 80, 60, "+9.5", "W2", "6-4", "+115", False),
        ("BOS", 75, 65, "+4.5", "L2", "4-6", "+77", False),
        ("CLE", 70, 69, "--", "L1", "7-3", "-8", True),
        ("BAL", 69, 71, "1.5", "L2", "6-4", "-20", False),
        ("TOR", 69, 71, "1.5", "W1", "6-4", "-44", False),
        ("TEX", 69, 71, "1.5", "L1", "5-5", "-48", False),
    ],
    "NL East": [
        ("ATL", 83, 57, "--", "--", "W1", "8-2", "+118"),
        ("PHI", 79, 61, "4.0", "+5.5", "L1", "7-3", "+36"),
        ("MIA", 71, 69, "12.0", "2.5", "W2", "5-5", "+18"),
        ("WSN", 67, 75, "17.0", "7.5", "L1", "6-4", "+14"),
        ("NYM", 63, 77, "20.0", "10.5", "W1", "4-6", "-50"),
    ],
    "NL Central": [
        ("MIL", 87, 53, "--", "--", "W2", "6-4", "+172"),
        ("CHC", 78, 62, "9.0", "+4.5", "L2", "4-6", "+132"),
        ("STL", 70, 70, "17.0", "3.5", "W2", "4-6", "-8"),
        ("PIT", 68, 72, "19.0", "5.5", "L1", "5-5", "+26"),
        ("CIN", 67, 73, "20.0", "6.5", "W2", "5-5", "-108"),
    ],
    "NL West": [
        ("LAD", 82, 57, "--", "--", "L2", "4-6", "+146"),
        ("ARI", 74, 67, "9.0", "--", "W1", "5-5", "-1"),
        ("SDP", 73, 67, "9.5", "0.5", "L2", "3-7", "+10"),
        ("SFG", 58, 82, "24.5", "15.5", "W1", "6-4", "-70"),
        ("COL", 54, 86, "28.5", "19.5", "W2", "4-6", "-140"),
    ],
    "NL Wild Card": [
        ("PHI", 79, 61, "+5.5", "L1", "7-3", "+36", False),
        ("CHC", 78, 62, "+4.5", "L2", "4-6", "+132", False),
        ("ARI", 74, 67, "--", "W1", "5-5", "-1", True),
        ("SDP", 73, 67, "0.5", "L2", "3-7", "+10", False),
        ("MIA", 71, 69, "2.5", "W2", "5-5", "+18", False),
        ("STL", 70, 70, "3.5", "W2", "4-6", "-8", False),
    ],
}

UPCOMING = [
    ("SFG", "PIT", "Blade Tidwell vs. Lake Bachar", "12:35 PM ET", "2026-09-03T16:35:00Z", ""),
    ("TOR", "CLE", "José Soriano vs. Tanner Bibee", "1:10 PM ET", "2026-09-03T17:10:00Z", ""),
    ("CWS", "HOU", "Luis Castillo vs. Hunter Brown", "2:10 PM ET", "2026-09-03T18:10:00Z", ""),
    ("BOS", "BAL", "Jake Bennett vs. Brandon Young", "7:15 PM ET", "2026-09-03T23:15:00Z", "FOX"),
    ("MIL", "CHC", "Logan Henderson vs. Kevin Gausman", "7:15 PM ET", "2026-09-03T23:15:00Z", "FOX"),
    ("MIA", "KCR", "Sandy Alcantara vs. Michael Wacha", "7:40 PM ET", "2026-09-03T23:40:00Z", ""),
    ("TBR", "TEX", "Shane McClanahan vs. Cal Quantrill", "8:05 PM ET", "2026-09-04T00:05:00Z", ""),
    ("ATH", "SEA", "Jack Perkins vs. Kade Anderson", "9:40 PM ET", "2026-09-04T01:40:00Z", ""),
    ("STL", "LAD", "Quinn Mathews vs. Tarik Skubal", "10:10 PM ET", "2026-09-04T02:10:00Z", ""),
]

OFF_TONIGHT = ["SDP", "CIN", "ATL", "WSN", "COL", "PHI", "ARI", "NYM", "DET", "MIN", "NYY", "LAA"]

TEAM_SUMMARIES = {
    "ATL": "Your Braves: Ronald Acuña Jr. hit his 200th homer and joined the 200-200 club. Shut out Washington 9-0.",
    "TOR": "Your Blue Jays: Dylan Cease threw six scoreless innings. Vladimir Guerrero Jr. drove in five. Won 11-0 in Cleveland.",
    "DET": "Your Tigers: Five runs in the 12th at Target Field. Beat Minnesota 11-6 in 12 innings.",
    "ATH": "Your Athletics: Five home runs in a 9-2 win at Texas. Henry Bolte had two of them.",
    "NYM": "Your Mets: Ten runs on fourteen hits. Beat Tampa Bay 10-4.",
    "CIN": "Your Reds: Seven runs on ten hits. Beat San Diego 7-3.",
    "SEA": "Your Mariners: Two four-run innings at Fenway. Won 8-3 over Boston.",
    "MIL": "Your Brewers: Jackson Chourio had four hits. Beat the Cubs 9-5 at Wrigley.",
    "MIA": "Your Marlins: Nine runs in Kansas City. Won 9-6.",
    "COL": "Your Rockies: Walk-off in the 11th. Beat Baltimore 6-5.",
    "HOU": "Your Astros: Josh Hader saved a 2-0 shutout of the White Sox.",
    "NYY": "Your Yankees: Cam Schlittler struck out nine over eight innings. Won 6-3 in 10 at Anaheim.",
    "STL": "Your Cardinals: Won 8-6 in 10 at Dodger Stadium.",
    "ARI": "Your Diamondbacks: James McCann's eighth-inning homer beat Philadelphia 1-0.",
    "CLE": "Your Guardians: Shut out 11-0 by Toronto. Angel Genao's error opened a five-run second.",
    "WSN": "Your Nationals: Shut out 9-0 by Atlanta. Acuña homered for his 200th career round-tripper.",
    "TEX": "Your Rangers: Lost 9-2 to Oakland. Athletics hit five homers.",
    "BOS": "Your Red Sox: Lost 8-3 to Seattle at Fenway.",
    "CHC": "Your Cubs: Lost 9-5 to Milwaukee at Wrigley.",
    "KCR": "Your Royals: Scored six but lost 9-6 to Miami.",
    "MIN": "Your Twins: Lost 11-6 to Detroit in 12 innings.",
    "PIT": "Your Pirates: Lost 5-4 in 10 to San Francisco.",
    "SFG": "Your Giants: Won 5-4 in 10 at PNC Park.",
    "TBR": "Your Rays: Lost 10-4 to the Mets.",
    "PHI": "Your Phillies: Andrew Painter threw seven scoreless innings. Lost 1-0 at Arizona.",
    "SDP": "Your Padres: Three runs on seven hits. Lost 7-3 in Cincinnati.",
    "BAL": "Your Orioles: Lost 6-5 in 11 at Coors Field.",
    "CWS": "Your White Sox: Shut out 2-0 in Houston.",
    "LAA": "Your Angels: Lost 6-3 in 10 to the Yankees.",
    "LAD": "Your Dodgers: Lost 8-6 in 10 to St. Louis.",
}

RACE_AL_RECAP = (
    "Dylan Cease and Toronto shut out Cleveland. Detroit won in 12. "
    "Cam Schlittler struck out nine for the Yankees. Athletics hit five homers in Texas."
)
RACE_AL_SINCE = "Toronto is 6-4 in its last ten."
RACE_NL_RECAP = (
    "Ronald Acuña Jr. reached 200 homers and 200 steals. "
    "Mets scored ten in Tampa. Brewers beat the Cubs 9-5. Cardinals won in 10 at Dodger Stadium."
)
RACE_NL_SINCE = "Atlanta is 8-2 in its last ten."


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
    return m.group(1).replace("2026-09-01", ISSUE_DATE)


def clip_html(key: str) -> str:
    c = CLIPS[key]
    return f"""<figure class="clip">
  <video controls playsinline preload="metadata" src="{c['video']}"></video>
  <figcaption><a href="https://www.mlb.com/video/{c['slug']}">Film Room</a> · MLB Film Room stream</figcaption>
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


def find_game(away: str, home: str) -> tuple:
    for g in GAMES:
        if g[0] == away and g[1] == home:
            return g
    raise KeyError(f"Game {away}@{home} not found")


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
        note_bit = f". {note}." if note else "."
        parts.append(
            f'    <article class="upcoming-game" data-away-team="{away}" data-home-team="{home}">\n'
            f"      <p><strong>{pitchers}</strong> — {away} at {home}, "
            f'<time datetime="{start_iso}">{start_time}</time>{note_bit}</p>\n'
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
            "note": note.replace(" · ", " · "),
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


def build_html() -> str:
    style = extract_style_block()
    footer = extract_footer_scripts()
    featured = "\n".join(render_game(find_game(a, h)) for a, h in FEATURED_KEYS)

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
<title>Scorebook - Wednesday, September 2</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Wednesday, September 2" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Wednesday, September 2" />
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
  <p class="kicker">Wednesday night</p>
  <h1>Wednesday, September 2</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("acuna")}
  <p class="cap">{CLIPS["acuna"]["cap"]}</p>
{clip_html("cease")}
  <p class="cap">{CLIPS["cease"]["cap"]}</p>
{clip_html("guerrero")}
  <p class="cap">{CLIPS["guerrero"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="acuna" required> Acuña 200/200 milestone</label>
      <label><input type="radio" name="play" value="cease"> Dylan Cease shutout</label>
      <label><input type="radio" name="play" value="guerrero"> Guerrero five RBIs</label>
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
{clip_html("genao")}
  <p class="cap">{CLIPS["genao"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Bottom of the 12th at Target Field. Detroit sent nine batters to the plate and scored five runs — a single, three walks, a hit batsman, and Spencer Torkelson's two-run homer. The Twins had tied it in the 11th. The Tigers led 6-6. They won 11-6.</p>
{clip_html("det_twelfth")}
  <p class="cap">{CLIPS["det_twelfth"]["cap"]}</p>

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
      <p class="subn">Standings through Wednesday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
{al_tables}
    </div>

    <div class="panel-nl" id="nl-panel">
      <div class="recap" data-share-card="race-nl.png" data-share-text-src="share/race-nl.txt">
        <p class="subn">Last night</p>
        <p>{RACE_NL_RECAP}</p>
        <p class="subn">Since August 13</p>
        <p>{RACE_NL_SINCE}</p>
      </div>
      <p class="subn">Standings through Wednesday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
{nl_tables}
    </div>
  </div>

  </section>

  <section class="shareable" id="the-games">
  <h2>The games</h2>
  <p class="subn">Team, runs, hits, errors. Tap a box and the innings fill in.</p>
{featured}

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
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    html_path = OUT_DIR / "index.html"
    html_path.write_text(build_html(), encoding="utf-8")
    write_race_share_files()
    print(f"Wrote {html_path}")
    print(f"Wrote {OUT_DIR / 'share' / 'race-al.txt'}")
    print(f"Wrote {OUT_DIR / 'share' / 'race-nl.txt'}")


if __name__ == "__main__":
    main()
