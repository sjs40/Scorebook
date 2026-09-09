#!/usr/bin/env python3
"""Generate /workspace/2026-09-08/index.html and share race text files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-08"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-09-07" / "index.html"
ISSUE_DATE = "2026-09-08"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Detmers fans nine and Neto goes 4-for-5 in the Angels' 6–1 win. "
    "Ramos homers in the eighth as Yankees beat Colorado 5–3. "
    "Pirates score five in the first, Chandler beats Chicago 9–3. "
    "Guardians rally for nine at Baltimore."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/08"

CLIPS = {
    "detmers": {
        "video": f"{MLB_CDN}/c64fb778-2f56d003-a572d4b3-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "reid-detmers-fans-nine-against-the-red-sox",
        "cap": (
            "Reid Detmers: nine strikeouts, one hit over six innings. "
            "Angels 6, Red Sox 1 — Zach Neto went 4-for-5 with a two-run homer."
        ),
    },
    "ramos": {
        "video": f"{MLB_CDN}/e66d36c1-ef0ca201-8e1dbd8e-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "heliot-ramos-homers-11-on-a-fly-ball-to-center-field-ben-rice-scores-cody",
        "cap": (
            "Heliot Ramos: three-run homer in the eighth. "
            "Yankees 5, Rockies 3 — Cam Schlittler struck out 10 over seven."
        ),
    },
    "pirates": {
        "video": f"{MLB_CDN}/fe32e78f-5aa2d31e-97216d6d-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "five-run-inning-lifts-pirates-to-9-3-win",
        "cap": (
            "Bubba Chandler went six innings; Pittsburgh had 18 hits. "
            "Pirates 9, White Sox 3 — five runs in the first inning."
        ),
    },
    "siri": {
        "video": f"{MLB_CDN}/420e000c-d44537af-76fceb53-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "reid-detmers-in-play-out-s-to-wilyer-abreu-lhcuie",
        "cap": (
            "Jose Siri stumbled but held on for the catch in center at Fenway Park. "
            "That's baseball."
        ),
    },
    "pirates_first": {
        "video": f"{MLB_CDN}/5550ac78-6b6996ac-d0a86797-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "pirates-bat-around-for-five-run-1st-inning",
        "cap": (
            "Five runs in the first — Pittsburgh sent nine batters to the plate "
            "and had four hits in the frame."
        ),
    },
}

PITCHERS = [
    ("Reid Detmers", "LAA", 68, "6.0", 1, 0, 1, 9, "BOS"),
    ("Cam Schlittler", "NYY", 64, "7.0", 3, 1, 0, 10, "COL"),
    ("Bubba Chandler", "PIT", 53, "6.0", 4, 2, 0, 8, "CHW"),
    ("Jacob Misiorowski", "MIL", 53, "6.1", 4, 1, 2, 9, "CHC"),
]

HITTERS = [
    ("Zach Neto", "LAA", 7, 5, 4, 2, 1, 2, 0),
    ("Jackson Chourio", "MIL", 7, 5, 4, 2, 1, 2, 0),
    ("Tim Tawa", "ARI", 6, 5, 3, 1, 1, 2, 0),
    ("Daulton Varsho", "HOU", 6, 5, 3, 2, 1, 1, 0),
    ("Rafael Flores Jr.", "PIT", 6, 5, 3, 1, 1, 1, 0),
    ("Danny Jansen", "TEX", 5, 4, 2, 1, 1, 4, 0),
    ("Christian Walker", "HOU", 5, 3, 2, 1, 1, 3, 0),
    ("Juan Soto", "NYM", 5, 4, 2, 2, 1, 3, 0),
]

# away, home, away_score, home_score, away_innings, home_innings, away_h, away_e, home_h, home_e, note
GAMES = [
    ("CLE", "BAL", 9, 5, [1, 4, 1, 0, 0, 0, 3, 0, 0], [0, 0, 0, 1, 4, 0, 0, 0, 0], 12, 0, 6, 1, "W Tim Herrin · L Brandon Young"),
    ("MIN", "DET", 3, 2, [1, 0, 0, 0, 0, 2, 0, 0, 0], [0, 0, 0, 0, 2, 0, 0, 0, 0], 5, 1, 5, 0, "W Dean Kremer · L Drew Anderson · S Yoendrys Gómez"),
    ("HOU", "PHI", 6, 5, [0, 4, 0, 1, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 3, 1, 0, 1], 11, 0, 10, 0, "W Hayden Wesneski · L Andrew Painter · S Josh Hader"),
    ("NYM", "MIA", 7, 5, [2, 3, 1, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 4, 0, 0, 1], 8, 2, 10, 0, "W Sean Manaea · L Sandy Alcantara · S Kodai Senga"),
    ("LAA", "BOS", 6, 1, [0, 1, 2, 0, 1, 0, 0, 0, 2], [0, 0, 0, 0, 0, 0, 1, 0, 0], 15, 0, 4, 0, "W Reid Detmers · L Patrick Sandoval"),
    ("COL", "NYY", 3, 5, [0, 0, 1, 0, 0, 0, 0, 0, 2], [1, 0, 0, 0, 1, 0, 0, 3, 0], 4, 2, 8, 0, "W Cam Schlittler · L Gabriel Hughes · S David Bednar"),
    ("TBR", "ATL", 7, 1, [1, 0, 3, 0, 0, 1, 0, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0], 11, 0, 5, 2, "W Freddy Peralta · L AJ Smith-Shawver"),
    ("ARI", "KCR", 5, 3, [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 2], [0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0], 9, 1, 7, 0, "W Blake Walston · L Anthony Gose"),
    ("PIT", "CHW", 9, 3, [5, 2, 0, 0, 2, 0, 0, 0, 0], [0, 0, 0, 0, 1, 1, 1, 0, 0], 18, 0, 6, 0, "W Bubba Chandler · L Sean Burke"),
    ("CHC", "MIL", 3, 4, [1, 0, 0, 0, 0, 0, 0, 0, 2, 0], [1, 0, 0, 0, 0, 0, 0, 0, 2, 1], 7, 0, 12, 0, "W DL Hall · L Caleb Thielbar"),
    ("WSN", "SDP", 4, 5, [0, 1, 0, 0, 0, 2, 0, 1, 0], [0, 0, 0, 0, 0, 0, 1, 4, 0], 7, 0, 6, 0, "W David Morgan · L Erik Tolman · S Adrian Morejon"),
    ("TEX", "SEA", 10, 5, [1, 1, 0, 2, 5, 0, 1, 0, 0], [0, 0, 0, 3, 0, 0, 0, 1, 1], 11, 2, 9, 1, "W Cal Quantrill · L Bryce Miller"),
    ("TOR", "ATH", 4, 2, [0, 2, 0, 0, 0, 2, 0, 0, 0], [0, 0, 0, 1, 0, 0, 1, 0, 0], 11, 0, 6, 0, "W José Soriano · L Jack Perkins · S Spencer Miles"),
    ("STL", "SFG", 1, 2, [0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 1, 0, 0, 0, 0, 0, 0, 0], 5, 0, 6, 1, "W Landen Roupp · L Quinn Mathews · S Joel Kuhnel"),
    ("CIN", "LAD", 2, 3, [0, 0, 2, 0, 0, 0, 0, 0, 0], [1, 1, 0, 0, 1, 0, 0, 0, 0], 5, 0, 7, 1, "W Tarik Skubal · L Nick Lodolo · S Tanner Scott"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 86, 58, "--", "--", "W1", "6-4", "+53"),
        ("NYY", 82, 62, "4", "+9", "W1", "6-4", "+119"),
        ("BOS", 80, 66, "7", "+6", "L1", "6-4", "+84"),
        ("TOR", 73, 73, "14", "1", "W1", "7-3", "-37"),
        ("BAL", 70, 76, "17", "4", "L1", "3-7", "-31"),
    ],
    "AL Central": [
        ("CHW", 75, 69, "--", "--", "L1", "4-6", "+43"),
        ("CLE", 74, 72, "2", "--", "W1", "6-4", "-12"),
        ("MIN", 69, 76, "6.5", "4.5", "W1", "5-5", "-48"),
        ("DET", 66, 79, "9.5", "7.5", "L1", "3-7", "+50"),
        ("KCR", 64, 82, "12", "10", "L2", "3-7", "-91"),
    ],
    "AL West": [
        ("HOU", 74, 71, "--", "--", "W1", "6-4", "-37"),
        ("TEX", 72, 73, "2", "1.5", "W2", "6-4", "-39"),
        ("SEA", 67, 78, "7", "6.5", "L1", "3-7", "-76"),
        ("ATH", 58, 88, "16.5", "16", "L1", "5-5", "-189"),
        ("LAA", 55, 90, "19", "18.5", "W1", "3-7", "-75"),
    ],
    "AL Wild Card": [
        ("NYY", 82, 62, "+9", "W1", "6-4", "+119", False),
        ("BOS", 80, 66, "+6", "L1", "6-4", "+84", False),
        ("CLE", 74, 72, "--", "W1", "6-4", "-12", True),
        ("TOR", 73, 73, "1", "W1", "7-3", "-37", False),
        ("TEX", 72, 73, "1.5", "W2", "6-4", "-39", False),
        ("BAL", 70, 76, "4", "L1", "3-7", "-31", False),
    ],
    "NL East": [
        ("ATL", 85, 60, "--", "--", "L2", "5-5", "+113"),
        ("PHI", 81, 64, "4", "+3.5", "L1", "6-4", "+34"),
        ("MIA", 72, 74, "13.5", "6", "L2", "4-6", "+8"),
        ("NYM", 67, 78, "18", "10.5", "W3", "7-3", "-41"),
        ("WSN", 67, 80, "19", "11.5", "L6", "3-7", "+7"),
    ],
    "NL Central": [
        ("MIL", 90, 56, "--", "--", "W2", "5-5", "+170"),
        ("CHC", 81, 65, "9", "+3", "L3", "4-6", "+130"),
        ("PIT", 72, 73, "17.5", "5.5", "W2", "7-3", "+32"),
        ("STL", 72, 74, "18", "6", "L2", "4-6", "-11"),
        ("CIN", 69, 76, "20.5", "8.5", "L2", "5-5", "-109"),
    ],
    "NL West": [
        ("LAD", 88, 57, "--", "--", "W6", "7-3", "+156"),
        ("ARI", 78, 68, "10.5", "--", "W4", "6-4", "+2"),
        ("SDP", 77, 68, "11", "0.5", "W3", "5-5", "+10"),
        ("SFG", 61, 85, "27.5", "17", "W2", "6-4", "-73"),
        ("COL", 55, 89, "32.5", "22", "L2", "3-7", "-142"),
    ],
    "NL Wild Card": [
        ("PHI", 81, 64, "+3.5", "L1", "6-4", "+34", False),
        ("CHC", 81, 65, "+3", "L3", "4-6", "+130", False),
        ("ARI", 78, 68, "--", "W4", "6-4", "+2", True),
        ("SDP", 77, 68, "0.5", "W3", "5-5", "+10", False),
        ("PIT", 72, 73, "5.5", "W2", "7-3", "+32", False),
        ("MIA", 72, 74, "6", "L2", "4-6", "+8", False),
    ],
}

UPCOMING = [
    ("MIN", "DET", "Zebby Matthews vs. Keider Montero", "1:10 PM ET", "2026-09-09T17:10:00Z", ""),
    ("TOR", "ATH", "Braydon Fisher vs. Brady Basso", "3:05 PM ET", "2026-09-09T19:05:00Z", ""),
    ("STL", "SFG", "Andre Pallante vs. Blade Tidwell", "3:45 PM ET", "2026-09-09T19:45:00Z", ""),
    ("WSN", "SDP", "Jackson Kent vs. Walker Buehler", "4:10 PM ET", "2026-09-09T20:10:00Z", ""),
    ("TEX", "SEA", "Cody Bradford vs. Kade Anderson", "4:10 PM ET", "2026-09-09T20:10:00Z", ""),
    ("CLE", "BAL", "Foster Griffin vs. Shane Baz", "6:35 PM ET", "2026-09-09T22:35:00Z", ""),
    ("HOU", "PHI", "Hunter Brown vs. Cristopher Sánchez", "6:40 PM ET", "2026-09-09T22:40:00Z", ""),
    ("NYM", "MIA", "Robert Stock vs. Janson Junk", "6:40 PM ET", "2026-09-09T22:40:00Z", ""),
    ("LAA", "BOS", "Ryan Johnson vs. Jake Bennett", "6:45 PM ET", "2026-09-09T22:45:00Z", ""),
    ("COL", "NYY", "Tomoyuki Sugano vs. Will Warren", "7:05 PM ET", "2026-09-09T23:05:00Z", ""),
    ("TBR", "ATL", "Griffin Jax vs. TBD", "7:15 PM ET", "2026-09-09T23:15:00Z", ""),
    ("ARI", "KCR", "Zac Gallen vs. Daniel Lynch IV", "7:40 PM ET", "2026-09-09T23:40:00Z", ""),
    ("PIT", "CHW", "Lake Bachar vs. Davis Martin", "7:40 PM ET", "2026-09-09T23:40:00Z", ""),
    ("CHC", "MIL", "Kevin Gausman vs. Logan Henderson", "7:40 PM ET", "2026-09-09T23:40:00Z", ""),
    ("CIN", "LAD", "Rhett Lowder vs. Yoshinobu Yamamoto", "10:10 PM ET", "2026-09-10T02:10:00Z", ""),
]

OFF_TONIGHT: list[str] = []

TEAM_SUMMARIES = {
    "CHC": "Your Cubs: Lost 3-4 in 10 at Milwaukee; Chourio went 4-for-5. At Milwaukee tonight.",
    "MIA": "Your Marlins: Lost 7-5 to the Mets; Senga saved it. Host New York tonight.",
    "SFG": "Your Giants: Roupp and Eldridge beat St. Louis 2-1. Host the Cardinals tonight.",
    "NYM": "Your Mets: Soto homered in a 7-5 win at Miami. At Miami tonight.",
    "ATL": "Your Braves: Lost 1-7 to Tampa Bay. Host the Rays tonight.",
    "PHI": "Your Phillies: Lost 5-6 to Houston despite a Walker three-run homer. Host the Astros tonight.",
    "DET": "Your Tigers: Lost 2-3 to Minnesota. Host the Twins tonight.",
    "CLE": "Your Guardians: Bazzana homered; beat Baltimore 9-5. At Baltimore tonight.",
    "LAA": "Your Angels: Detmers fanned nine; Neto went 4-for-5 in a 6-1 win at Boston. At Boston tonight.",
    "PIT": "Your Pirates: Chandler and an 18-hit attack beat Chicago 9-3. At Chicago tonight.",
    "MIL": "Your Brewers: Walk-off in the 10th over Chicago 4-3. Host the Cubs tonight.",
    "CIN": "Your Reds: Lost 2-3 at Dodger Stadium. At Los Angeles tonight.",
    "BOS": "Your Red Sox: Lost 1-6 to the Angels. Host the Angels tonight.",
    "BAL": "Your Orioles: Lost 5-9 to Cleveland. Host the Guardians tonight.",
    "TBR": "Your Rays: Four homers in a 7-1 win at Atlanta. At Atlanta tonight.",
    "TEX": "Your Rangers: Jansen drove in four in a 10-5 win at Seattle. At Seattle tonight.",
    "MIN": "Your Twins: Kremer won 3-2 at Detroit. At Detroit tonight.",
    "CHW": "Your White Sox: Lost 3-9 to Pittsburgh. Host the Pirates tonight.",
    "TOR": "Your Blue Jays: Soriano won 4-2 at Oakland. At Oakland tonight.",
    "KCR": "Your Royals: Lost 3-5 in 11 to Arizona. Host the D-backs tonight.",
    "ARI": "Your Diamondbacks: Beat Kansas City 5-3 in 11. At Kansas City tonight.",
    "HOU": "Your Astros: Walker homered in a 6-5 win at Philadelphia. At Philadelphia tonight.",
    "NYY": "Your Yankees: Ramos's three-run eighth beat Colorado 5-3. Host the Rockies tonight.",
    "SDP": "Your Padres: Four-run eighth beat Washington 5-4. Host the Nationals tonight.",
    "STL": "Your Cardinals: Lost 1-2 at San Francisco. At San Francisco tonight.",
    "COL": "Your Rockies: Lost 3-5 at New York. At New York tonight.",
    "WSN": "Your Nationals: Lost 4-5 at San Diego. At San Diego tonight.",
    "LAD": "Your Dodgers: Skubal won 3-2 over Cincinnati. Host the Reds tonight.",
    "ATH": "Your Athletics: Lost 2-4 to Toronto. Host the Blue Jays tonight.",
    "SEA": "Your Mariners: Lost 5-10 to Texas. Host the Rangers tonight.",
}

RACE_AL_RECAP = (
    "Travis Bazzana homered as Cleveland beat Baltimore 9-5. "
    "Reid Detmers fanned nine in the Angels' 6-1 win at Boston. "
    "Danny Jansen drove in four as Texas beat Seattle 10-5."
)
RACE_AL_SINCE = "Cleveland is 6-4 in its last ten."
RACE_NL_RECAP = (
    "Tampa Bay hit four homers in a 7-1 win at Atlanta. "
    "Pittsburgh scored five in the first and beat Chicago 9-3 on 18 hits. "
    "Arizona beat Kansas City 5-3 in 11."
)
RACE_NL_SINCE = "Arizona is 6-4 in its last ten."


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
    return m.group(1).replace("2026-09-07", ISSUE_DATE)


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
<title>Scorebook - Tuesday, September 8</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Tuesday, September 8" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Tuesday, September 8" />
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
  <h1>Tuesday, September 8</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("detmers")}
  <p class="cap">{CLIPS["detmers"]["cap"]}</p>
{clip_html("ramos")}
  <p class="cap">{CLIPS["ramos"]["cap"]}</p>
{clip_html("pirates")}
  <p class="cap">{CLIPS["pirates"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="detmers" required> Detmers' nine Ks</label>
      <label><input type="radio" name="play" value="ramos"> Ramos's three-run homer</label>
      <label><input type="radio" name="play" value="pirates"> Pirates' five-run first</label>
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
{clip_html("siri")}
  <p class="cap">{CLIPS["siri"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Top of the first at Rate Field. Pittsburgh sent nine batters to the plate and scored five runs on four hits — a two-run homer, an RBI single, and a two-run double among the damage. Chicago answered with one in the fifth but fell 9-3.</p>
{clip_html("pirates_first")}
  <p class="cap">{CLIPS["pirates_first"]["cap"]}</p>

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
      <p class="subn">Standings through Tuesday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
{al_tables}
    </div>

    <div class="panel-nl" id="nl-panel">
      <div class="recap" data-share-card="race-nl.png" data-share-text-src="share/race-nl.txt">
        <p class="subn">Last night</p>
        <p>{RACE_NL_RECAP}</p>
        <p class="subn">Since August 13</p>
        <p>{RACE_NL_SINCE}</p>
      </div>
      <p class="subn">Standings through Tuesday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
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
