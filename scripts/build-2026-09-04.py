#!/usr/bin/env python3
"""Generate /workspace/2026-09-04/index.html and share race text files."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-04"
REF_HTML = ROOT / "2026-09-03" / "index.html"
ISSUE_DATE = "2026-09-04"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Rocchio walks off Game 1, then the Guardians sweep Detroit. "
    "Sale extends Atlanta's NL East lead to five. "
    "Campusano lifts the Padres in the 10th. "
    "Herrera's ninth-inning blast saves St. Louis."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/04"

CLIPS = {
    "rocchio": {
        "video": f"{MLB_CDN}/e443c558-dca0a24f-33b7423b-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "brayan-rocchio-s-grand-slam-and-walk-off-home-run",
        "cap": (
            "Brayan Rocchio: grand slam in the fourth, walk-off homer in the ninth — "
            "five RBIs, the sixth player ever with both in one game. "
            "Guardians 7, Tigers 6 (Game 1)."
        ),
    },
    "sale": {
        "video": f"{MLB_CDN}/01a775e6-dfb1424a-ce08806f-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "dubon-sale-lead-braves-to-5-2-win",
        "cap": (
            "Chris Sale: 6.0 IP, 6 H, 2 ER, 1 BB, 7 K. Mauricio Dubón homered twice. "
            "Braves 5, Phillies 2 — NL East lead to five."
        ),
    },
    "campusano": {
        "video": f"{MLB_CDN}/8aa5965e-ed1814dd-ba313552-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "paul-blackburn-in-play-run-s-to-luis-campusano",
        "cap": (
            "Luis Campusano: two-run walk-off homer in the 10th. "
            "Padres 3, Yankees 2."
        ),
    },
    "benches": {
        "video": f"{MLB_CDN}/a66d35b0-04e08b9d-4c9c8a11-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "benches-clear-between-the-red-sox-and-orioles",
        "cap": (
            "Benches cleared in the eighth at Camden Yards. "
            "Ranger Suárez threw seven scoreless. Red Sox 1, Orioles 0."
        ),
    },
    "mets_second": {
        "video": f"{MLB_CDN}/4e5910de-c2e1d964-ab4d8be7-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "francisco-alvarez-swats-two-home-runs-in-mets-win",
        "cap": (
            "Four runs in the second — Francisco Alvarez and Mark Vientos homered among five Mets long balls. "
            "Mets led 7–2 and won 10–6."
        ),
    },
}

PITCHERS = [
    ("Jared Jones", "PIT", 63, "6.0", 3, 0, 1, 9, "LAA"),
    ("Cristian Javier", "HOU", 53, "5.0", 1, 1, 3, 8, "ARI"),
    ("Ranger Suarez", "BOS", 52, "7.0", 5, 0, 1, 3, "BAL"),
    ("Erick Fedde", "CHW", 51, "5.0", 3, 0, 2, 2, "MIN"),
]

HITTERS = [
    ("Brayan Rocchio", "CLE", 8, 4, 2, 2, 2, 5, 0),
    ("Francisco Alvarez", "NYM", 8, 4, 2, 2, 2, 2, 0),
    ("Rafael Devers", "SFG", 6, 4, 3, 1, 1, 5, 0),
    ("TJ Rumfield", "COL", 6, 4, 3, 1, 1, 1, 0),
    ("Ben Rice", "NYY", 6, 4, 3, 1, 1, 1, 0),
    ("Max Muncy", "ATH", 6, 4, 3, 1, 1, 1, 0),
    ("Mark Vientos", "NYM", 5, 4, 2, 1, 1, 3, 0),
    ("Travis Bazzana", "CLE", 5, 3, 2, 1, 1, 3, 0),
]

# away, home, away_score, home_score, away_innings, home_innings, away_h, away_e, home_h, home_e, note
GAMES = [
    ("DET", "CLE", 6, 7, [4, 1, 1, 0, 0, 0, 0, 0, 0], [1, 0, 0, 5, 0, 0, 0, 0, 1], 11, 0, 11, 0, "W Cade Smith · L Drew Sommers"),
    ("MIL", "CIN", 10, 7, [0, 2, 2, 0, 5, 1, 0, 0, 0], [1, 2, 3, 0, 0, 0, 1, 0, 0], 12, 0, 8, 1, "W Chad Patrick · L Rhett Lowder · S Trevor Megill"),
    ("LAA", "PIT", 0, 1, [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0], 4, 0, 5, 0, "W Jared Jones · L Ryan Johnson · S Mason Montgomery"),
    ("ATL", "PHI", 5, 2, [0, 3, 0, 0, 0, 0, 0, 2, 0], [0, 1, 0, 1, 0, 0, 0, 0, 0], 8, 0, 6, 1, "W Chris Sale · L Cristopher Sánchez · S Raisel Iglesias"),
    ("BOS", "BAL", 1, 0, [1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], 5, 0, 6, 2, "W Ranger Suarez · L Shane Baz · S Aroldis Chapman"),
    ("CHC", "MIA", 6, 1, [0, 1, 0, 0, 0, 3, 1, 0, 1], [0, 0, 0, 0, 0, 0, 1, 0, 0], 9, 0, 4, 0, "W Shota Imanaga · L Janson Junk · S Aaron Civale"),
    ("SFG", "NYM", 6, 10, [0, 0, 2, 0, 0, 0, 1, 3, 0], [3, 4, 0, 0, 0, 2, 0, 1], 12, 1, 9, 0, "W Nolan McLean · L Matt Wilkinson"),
    ("MIN", "CHW", 1, 4, [0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 1, 0, 2, 0, 0, 0, 0], 8, 0, 6, 1, "W Erick Fedde · L Zebby Matthews"),
    ("DET", "CLE", 3, 4, [0, 0, 2, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 2, 0, 1], 9, 0, 6, 0, "W Hunter Gaddis · L Kenley Jansen"),
    ("TBR", "TEX", 7, 6, [0, 0, 1, 1, 4, 0, 0, 0, 1], [0, 1, 0, 0, 0, 0, 4, 0, 1], 12, 0, 7, 1, "W Nick Martinez · L Kumar Rocker · S Tyler Wells"),
    ("ARI", "HOU", 1, 3, [0, 0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 3, 0, 0, 0, 0, 0], 3, 0, 7, 0, "W Cristian Javier · L Merrill Kelly · S Josh Hader"),
    ("TOR", "KCR", 9, 2, [4, 1, 0, 0, 0, 3, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 1], 13, 0, 6, 0, "W Joe Mantiply · L Daniel Lynch IV · S Michael Lorenzen"),
    ("STL", "COL", 7, 6, [0, 2, 0, 0, 2, 0, 0, 0, 3], [1, 0, 0, 0, 0, 4, 1, 0, 0], 9, 1, 10, 1, "W Cade Winquest · L Jordan Romano · S Riley O'Brien"),
    ("NYY", "SDP", 2, 3, [0, 0, 1, 0, 0, 0, 0, 0, 0, 1], [0, 1, 0, 0, 0, 0, 0, 0, 0, 2], 5, 0, 6, 0, "W Mason Miller · L Paul Blackburn"),
    ("ATH", "SEA", 7, 6, [0, 0, 5, 0, 2, 0, 0, 0, 0], [0, 2, 3, 0, 0, 0, 0, 1, 0], 11, 1, 10, 1, "W Brady Basso · L Logan Gilbert · S Hogan Harris"),
    ("WSN", "LAD", 3, 5, [0, 0, 0, 0, 0, 0, 0, 0, 3], [0, 0, 3, 1, 0, 1, 0, 0], 10, 1, 5, 1, "W Blake Snell · L Jackson Kent · S Jack Dreyer"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 84, 57, "--", "--", "W1", "6-4", "+46"),
        ("NYY", 80, 61, "4", "+8.5", "L1", "6-4", "+114"),
        ("BOS", 77, 65, "7.5", "+5", "W2", "4-6", "+79"),
        ("TOR", 71, 71, "13.5", "1", "W3", "7-3", "-34"),
        ("BAL", 69, 73, "15.5", "3", "L4", "5-5", "-22"),
    ],
    "AL Central": [
        ("CHW", 74, 67, "--", "--", "W1", "6-4", "+42"),
        ("CLE", 72, 70, "2.5", "--", "W2", "6-4", "-9"),
        ("MIN", 67, 74, "7", "4.5", "L2", "4-6", "-41"),
        ("DET", 64, 77, "10", "7.5", "L2", "3-7", "+45"),
        ("KCR", 63, 79, "11.5", "9", "L1", "5-5", "-92"),
    ],
    "AL West": [
        ("HOU", 73, 69, "--", "--", "W3", "7-3", "-36"),
        ("TEX", 70, 72, "3", "2", "L1", "4-6", "-43"),
        ("SEA", 66, 76, "7", "6", "L2", "3-7", "-69"),
        ("ATH", 56, 86, "17", "16", "W3", "5-5", "-190"),
        ("LAA", 53, 88, "19.5", "18.5", "L3", "1-9", "-81"),
    ],
    "AL Wild Card": [
        ("NYY", 80, 61, "+8.5", "L1", "6-4", "+114", False),
        ("BOS", 77, 65, "+5", "W2", "4-6", "+79", False),
        ("CLE", 72, 70, "--", "W2", "6-4", "-9", True),
        ("TOR", 71, 71, "1", "W3", "7-3", "-34", False),
        ("TEX", 70, 72, "2", "L1", "4-6", "-43", False),
        ("BAL", 69, 73, "3", "L4", "5-5", "-22", False),
    ],
    "NL East": [
        ("ATL", 84, 57, "--", "--", "W2", "8-2", "+121"),
        ("PHI", 79, 62, "5", "+5", "L2", "6-4", "+33"),
        ("MIA", 71, 71, "13.5", "3.5", "L2", "4-6", "+9"),
        ("WSN", 67, 76, "18", "8", "L2", "5-5", "+12"),
        ("NYM", 64, 77, "20", "10", "W2", "5-5", "-46"),
    ],
    "NL Central": [
        ("MIL", 88, 54, "--", "--", "W1", "7-3", "+174"),
        ("CHC", 80, 62, "8", "+5.5", "W2", "4-6", "+138"),
        ("STL", 71, 71, "17", "3.5", "W1", "5-5", "-8"),
        ("PIT", 70, 72, "18", "4.5", "W2", "7-3", "+30"),
        ("CIN", 67, 74, "20.5", "7", "L1", "5-5", "-111"),
    ],
    "NL West": [
        ("LAD", 84, 57, "--", "--", "W2", "4-6", "+149"),
        ("SDP", 74, 67, "10", "--", "W1", "3-7", "+11"),
        ("ARI", 74, 68, "10.5", "0.5", "L1", "5-5", "-3"),
        ("SFG", 58, 84, "26.5", "16.5", "L2", "4-6", "-77"),
        ("COL", 54, 87, "30", "20", "L1", "4-6", "-141"),
    ],
    "NL Wild Card": [
        ("CHC", 80, 62, "+5.5", "W2", "4-6", "+138", False),
        ("PHI", 79, 62, "+5", "L2", "6-4", "+33", False),
        ("SDP", 74, 67, "--", "W1", "3-7", "+11", True),
        ("ARI", 74, 68, "0.5", "L1", "5-5", "-3", False),
        ("MIA", 71, 71, "3.5", "L2", "4-6", "+9", False),
        ("STL", 71, 71, "3.5", "W1", "5-5", "-8", False),
    ],
}

UPCOMING = [
    ("CHC", "MIA", "Javier Assad vs. Yulián Gusto", "4:10 PM ET", "2026-09-05T20:10:00Z", ""),
    ("SFG", "NYM", "Luis Morales vs. Mason Thornton", "4:10 PM ET", "2026-09-05T20:10:00Z", ""),
    ("ATL", "PHI", "Nacho Perez vs. Zack Wheeler", "6:05 PM ET", "2026-09-05T22:05:00Z", ""),
    ("DET", "CLE", "Carlos Valdez vs. Chase Messick", "6:10 PM ET", "2026-09-05T22:10:00Z", ""),
    ("LAA", "PIT", "Yusei Kikuchi vs. Bryce Ashcraft", "6:40 PM ET", "2026-09-05T22:40:00Z", ""),
    ("MIL", "CIN", "Trevor May vs. Andrew Abbott", "6:40 PM ET", "2026-09-05T22:40:00Z", ""),
    ("BOS", "BAL", "Jacob Gray vs. Chris Bassitt", "7:05 PM ET", "2026-09-05T23:05:00Z", ""),
    ("TBR", "TEX", "Drew Rasmussen vs. Jacob deGrom", "7:05 PM ET", "2026-09-05T23:05:00Z", ""),
    ("MIN", "CHW", "Ty Bradley vs. Stephen Kay", "7:10 PM ET", "2026-09-05T23:10:00Z", ""),
    ("TOR", "KCR", "Max Scherzer vs. Seth Lugo", "7:10 PM ET", "2026-09-05T23:10:00Z", ""),
    ("ARI", "HOU", "Brandon Pfaadt vs. C.J. Pecko", "7:15 PM ET", "2026-09-05T23:15:00Z", ""),
    ("NYY", "SDP", "Carlos Rodón vs. Robbie Ray", "7:15 PM ET", "2026-09-05T23:15:00Z", ""),
    ("STL", "COL", "Matthew Liberatore vs. Grant Adams", "8:10 PM ET", "2026-09-06T00:10:00Z", ""),
    ("WSN", "LAD", "Cade Cavalli vs. Tyler Glasnow", "9:10 PM ET", "2026-09-06T01:10:00Z", ""),
    ("ATH", "SEA", "Jeffrey Springs vs. George Kirby", "9:40 PM ET", "2026-09-06T01:40:00Z", ""),
]

OFF_TONIGHT: list[str] = []

TEAM_SUMMARIES = {
    "CLE": "Your Guardians: Rocchio's grand slam and walk-off homer in Game 1, Bazzana's walk-off single in Game 2. Swept Detroit.",
    "DET": "Your Tigers: Lost both ends of the doubleheader in Cleveland. At Cleveland tonight.",
    "MIL": "Your Brewers: Cooper Pratt's bases-loaded triple, 10-7 win in Cincinnati. At Cincinnati tonight.",
    "CIN": "Your Reds: Lost 7-10 to Milwaukee. Host the Brewers tonight.",
    "PIT": "Your Pirates: Jared Jones six scoreless, 1-0 shutout of the Angels. Host Los Angeles tonight.",
    "LAA": "Your Angels: Shut out 0-1 in Pittsburgh. At Pittsburgh tonight.",
    "ATL": "Your Braves: Chris Sale and Mauricio Dubón led a 5-2 win in Philadelphia. NL East lead to five. At Philadelphia tonight.",
    "PHI": "Your Phillies: Lost 2-5 to Atlanta. Host the Braves tonight.",
    "BOS": "Your Red Sox: Mickey Gasper's first-inning homer, Suárez seven scoreless in a 1-0 win at Baltimore. At Baltimore tonight.",
    "BAL": "Your Orioles: Shut out 0-1 by Boston. Benches cleared in the eighth. Host Boston tonight.",
    "CHC": "Your Cubs: Imanaga six strong, Busch homered, 6-1 at Miami. At Miami tonight.",
    "MIA": "Your Marlins: Lost 1-6 to Chicago. Host the Cubs tonight.",
    "NYM": "Your Mets: Five homers in a 10-6 win over San Francisco. Host the Giants tonight.",
    "SFG": "Your Giants: Devers 3-for-4 with a homer and five RBIs, but lost 6-10 at Citi Field. At the Mets tonight.",
    "CHW": "Your White Sox: Colson Montgomery's two-run homer in a 4-1 win over Minnesota. Host the Twins tonight.",
    "MIN": "Your Twins: Lost 1-4 in Chicago. At the White Sox tonight.",
    "TBR": "Your Rays: Aranda and Palacios homered in a 7-6 win at Texas. At Texas tonight.",
    "TEX": "Your Rangers: Díaz's grand slam wasn't enough in a 6-7 loss to Tampa Bay. Host the Rays tonight.",
    "HOU": "Your Astros: Yainer Díaz homered in a 3-1 win over Arizona. Host the Diamondbacks tonight.",
    "ARI": "Your Diamondbacks: Lost 1-3 in Houston. At Houston tonight.",
    "TOR": "Your Blue Jays: Four-run first, 9-2 win in Kansas City — back to .500. At Kansas City tonight.",
    "KCR": "Your Royals: Lost 2-9 to Toronto. Host the Blue Jays tonight.",
    "STL": "Your Cardinals: Iván Herrera's three-run homer in the ninth for a 7-6 win in Colorado. At Colorado tonight.",
    "COL": "Your Rockies: Lost 6-7 to St. Louis. Host the Cardinals tonight.",
    "SDP": "Your Padres: Campusano's two-run walk-off in the 10th beat the Yankees 3-2. Host New York tonight.",
    "NYY": "Your Yankees: Lost 2-3 in 10 at San Diego. At San Diego tonight.",
    "ATH": "Your Athletics: Four homers in the third inning in a 7-6 win at Seattle. At Seattle tonight.",
    "SEA": "Your Mariners: Lost 6-7 to Oakland. Host the Athletics tonight.",
    "LAD": "Your Dodgers: Snell six shutout innings, 5-3 over Washington. Host the Nationals tonight.",
    "WSN": "Your Nationals: Kyle Tucker homered but lost 3-5 in Los Angeles. At Dodger Stadium tonight.",
}

RACE_AL_RECAP = (
    "Brayan Rocchio's grand slam and walk-off homer opened Cleveland's sweep of Detroit. "
    "Ranger Suárez shut out Baltimore over seven. "
    "Blue Jays scored four in the first and won 9-2 in Kansas City."
)
RACE_AL_SINCE = "Houston is 7-3 in its last ten."
RACE_NL_RECAP = (
    "Chris Sale and the Braves extended their NL East lead to five. "
    "Mets hit five homers in a 10-6 win. "
    "Iván Herrera's three-run homer in the ninth lifted St. Louis."
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
    return m.group(1).replace("2026-09-03", ISSUE_DATE)


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
<title>Scorebook - Friday, September 4</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Friday, September 4" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Friday, September 4" />
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
  <p class="kicker">Friday night</p>
  <h1>Friday, September 4</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("rocchio")}
  <p class="cap">{CLIPS["rocchio"]["cap"]}</p>
{clip_html("sale")}
  <p class="cap">{CLIPS["sale"]["cap"]}</p>
{clip_html("campusano")}
  <p class="cap">{CLIPS["campusano"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="rocchio" required> Rocchio grand slam and walk-off homer</label>
      <label><input type="radio" name="play" value="sale"> Sale outduels Sánchez</label>
      <label><input type="radio" name="play" value="campusano"> Campusano walk-off in the 10th</label>
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
{clip_html("benches")}
  <p class="cap">{CLIPS["benches"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Bottom of the second at Citi Field. The Mets sent eight batters to the plate and scored four runs on five hits — including home runs from Francisco Alvarez and Mark Vientos. New York led 7–2. The Mets hit five homers total and won 10–6.</p>
{clip_html("mets_second")}
  <p class="cap">{CLIPS["mets_second"]["cap"]}</p>

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
      <p class="subn">Standings through Friday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
{al_tables}
    </div>

    <div class="panel-nl" id="nl-panel">
      <div class="recap" data-share-card="race-nl.png" data-share-text-src="share/race-nl.txt">
        <p class="subn">Last night</p>
        <p>{RACE_NL_RECAP}</p>
        <p class="subn">Since August 13</p>
        <p>{RACE_NL_SINCE}</p>
      </div>
      <p class="subn">Standings through Friday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
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
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    html_path = OUT_DIR / "index.html"
    html_path.write_text(build_html(), encoding="utf-8")
    write_race_share_files()
    print(f"Wrote {html_path}")
    print(f"Wrote {OUT_DIR / 'share' / 'race-al.txt'}")
    print(f"Wrote {OUT_DIR / 'share' / 'race-nl.txt'}")


if __name__ == "__main__":
    main()
