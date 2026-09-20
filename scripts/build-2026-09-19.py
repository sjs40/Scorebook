#!/usr/bin/env python3
"""Generate /workspace/2026-09-19/index.html and share race text files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-19"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-09-18" / "index.html"
ISSUE_DATE = "2026-09-19"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Angel Martínez went 4-for-5 with two homers in Cleveland's 12–6 win over Oakland. "
    "Carson Benge set the Mets' rookie hit record in a 10–3 win over Philadelphia. "
    "Ronald Acuña Jr. hit a go-ahead grand slam in Atlanta's 6–3 win at Houston. "
    "Mookie Betts went 4-for-4 as the Dodgers beat San Francisco 10–4."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/19"

CLIPS = {
    "martinez_two_homers": {
        "video": f"{MLB_CDN}/5933a69c-0b469af1-0a344f69-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "angel-martinez-s-two-homer-game-x7869",
        "cap": (
            "Angel Martínez went 4-for-5 with two homers and four RBIs — Cleveland scored 12. "
            "Guardians 12, Athletics 6."
        ),
    },
    "benge_rookie_record": {
        "video": f"{MLB_CDN}/a5c8ec63-6bf373d7-75822697-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "carson-benge-s-historic-night-powers-mets-to-10-3-win",
        "cap": (
            "Carson Benge broke the Mets' all-time rookie hit record with his 156th — "
            "New York scored four in the eighth. Mets 10, Phillies 3."
        ),
    },
    "acuna_grand_slam": {
        "video": f"{MLB_CDN}/72f5be3f-1bf05be8-04eb3b29-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "acuna-jr-s-go-ahead-grand-slam-power-braves-to-win",
        "cap": (
            "Ronald Acuña Jr. cleared the bases with a go-ahead grand slam in the seventh — "
            "Atlanta scored four in the frame. Braves 6, Astros 3."
        ),
    },
    "moore_walkoff": {
        "video": f"{MLB_CDN}/cac54d5b-44f9d29a-7bc14600-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "christian-moore-singles-on-a-sharp-ground-ball-to-pitcher-taylor-rogers-z",
        "cap": (
            "Minnesota took the lead in the eighth — and still lost when Christian Moore "
            "singled it off in the 11th. That's baseball."
        ),
    },
    "guardians_five_run_third": {
        "video": f"{MLB_CDN}/fbcde337-ad957eb6-04fa474e-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "guardians-score-five-runs-in-the-3rd",
        "cap": (
            "Cleveland put up five in the third — part of a 12-run night at Progressive Field. "
            "Guardians 12, Athletics 6."
        ),
    },
}

PITCHERS = [
    ("Trevor Rogers", "BAL", 73, "8.0", 3, 1, 1, 10, "MIL"),
    ("Brayan Bello", "BOS", 71, "8.0", 5, 1, 0, 11, "TBR"),
    ("Andrew Alvarez", "WSN", 65, "6.0", 5, 0, 1, 8, "STL"),
    ("Robert Gasser", "MIL", 64, "7.0", 3, 0, 3, 2, "BAL"),
]

HITTERS = [
    ("Angel Martínez", "CLE", 11, 5, 4, 3, 2, 4, 0),
    ("Mookie Betts", "LAD", 7, 4, 4, 3, 0, 2, 0),
    ("Donovan Walton", "ATH", 6, 3, 3, 1, 1, 4, 1),
    ("Carson Benge", "NYM", 6, 4, 3, 1, 1, 2, 0),
    ("Will Smith", "LAD", 6, 5, 3, 1, 1, 2, 0),
    ("Cal Raleigh", "SEA", 6, 4, 2, 2, 1, 2, 0),
    ("Victor Bericoto", "SFG", 6, 4, 2, 2, 1, 2, 0),
    ("Ronald Acuña Jr.", "ATL", 5, 3, 2, 1, 1, 4, 0),
]

GAMES = [
    ("DET", "CWS", 1, 3, [0, 0, 0, 0, 1, 0, 0, 0, 0], [1, 0, 0, 0, 1, 1, 0, 0, 0], 8, 1, 4, 0, "W Sean Burke · L Jackson Jobe · S Grant Taylor"),
    ("MIL", "BAL", 1, 0, [0, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], 3, 0, 4, 0, "W Robert Gasser · L Trevor Rogers · S Aaron Ashby"),
    ("BOS", "TBR", 1, 2, [0, 0, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 1], 8, 2, 8, 0, "W Bryan Baker · L Garrett Whitlock"),
    ("PHI", "NYM", 3, 10, [0, 0, 0, 1, 2, 0, 0, 0, 0], [0, 1, 0, 0, 3, 2, 0, 4, 0], 9, 0, 11, 0, "W Jefry Yan · L Andrew Painter"),
    ("ATH", "CLE", 6, 12, [2, 0, 1, 1, 2, 0, 0, 0, 0], [5, 0, 5, 1, 0, 1, 0, 0, 0], 12, 1, 15, 1, "W Slade Cecconi · L Jacob Lopez · S Cade Smith"),
    ("CHC", "CIN", 5, 2, [0, 1, 0, 0, 1, 1, 0, 1, 1], [0, 0, 0, 0, 2, 0, 0, 0, 0], 8, 1, 4, 0, "W Matthew Boyd · L Nick Lodolo · S Ryan Rolison"),
    ("KCR", "PIT", 5, 6, [0, 0, 1, 0, 2, 0, 2, 0, 0], [0, 2, 0, 2, 0, 0, 0, 2, 0], 13, 1, 9, 1, "W Luke Weaver · L Steven Cruz · S Mason Montgomery"),
    ("TOR", "TEX", 2, 6, [0, 0, 0, 0, 0, 1, 1, 0, 0], [1, 2, 0, 0, 0, 3, 0, 0, 0], 6, 1, 5, 0, "W Jordan Montgomery · L José Soriano"),
    ("ATL", "HOU", 6, 3, [0, 0, 0, 0, 0, 1, 4, 1, 0], [1, 0, 1, 0, 0, 0, 0, 1, 0], 11, 0, 10, 0, "W Grant Holmes · L AJ Blubaugh · S Raisel Iglesias"),
    ("WSN", "STL", 8, 5, [2, 0, 0, 0, 0, 1, 0, 0, 0, 1, 4], [0, 0, 0, 0, 0, 0, 2, 0, 1, 1, 1], 12, 4, 14, 2, "W Riley Cornelio · L Gordon Graceffo · S Will Dion"),
    ("SEA", "COL", 3, 5, [2, 0, 1, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 4, 0, 0], 8, 3, 9, 0, "W Juan Mejia · L José A. Ferrer · S Brennan Bernardino"),
    ("NYY", "ARI", 3, 5, [0, 0, 0, 0, 1, 2, 0, 0, 0], [0, 0, 0, 0, 2, 1, 0, 0, 2], 6, 1, 7, 0, "W Juan Morillo · L Michael Fulmer"),
    ("MIA", "SDP", 6, 7, [0, 3, 2, 0, 0, 0, 0, 0, 1, 0], [0, 1, 3, 1, 0, 1, 0, 0, 0, 1], 10, 0, 11, 0, "W David Morgan · L Josh Ekness"),
    ("SFG", "LAD", 4, 10, [0, 0, 2, 1, 1, 0, 0, 0, 0], [1, 1, 1, 1, 3, 3, 0, 0, 0], 8, 2, 15, 0, "W Tarik Skubal · L Yunior Marte"),
    ("MIN", "LAA", 5, 6, [0, 0, 2, 1, 1, 0, 0, 1, 0, 0, 0], [0, 0, 0, 2, 0, 0, 0, 2, 1, 0, 1], 11, 1, 11, 0, "W Tayler Saucedo · L Taylor Rogers"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 94, 60, "--", "--", "W1", "8-2", "+79"),
        ("NYY", 89, 65, "5.0", "+10.5", "L1", "7-3", "+141"),
        ("BOS", 84, 71, "10.5", "+5.0", "L1", "4-6", "+84"),
        ("TOR", 76, 79, "18.5", "3.0", "L2", "4-6", "-47"),
        ("BAL", 75, 80, "19.5", "4.0", "L2", "5-5", "-28"),
    ],
    "AL Central": [
        ("CLE", 80, 75, "--", "--", "W4", "7-3", "+1"),
        ("CWS", 79, 76, "1.0", "--", "W1", "4-6", "+35"),
        ("DET", 73, 82, "7.0", "6.0", "L1", "7-3", "+75"),
        ("MIN", 72, 83, "8.0", "7.0", "L1", "3-7", "-72"),
        ("KCR", 67, 88, "13.0", "12.0", "L3", "3-7", "-101"),
    ],
    "AL West": [
        ("TEX", 78, 77, "--", "--", "W2", "6-4", "-29"),
        ("HOU", 77, 78, "1.0", "2.0", "L2", "3-7", "-57"),
        ("SEA", 72, 83, "6.0", "7.0", "L1", "5-5", "-57"),
        ("ATH", 61, 94, "17.0", "18.0", "L5", "3-7", "-222"),
        ("LAA", 60, 95, "18.0", "19.0", "W1", "5-5", "-79"),
    ],
    "AL Wild Card": [
        ("NYY", 89, 65, "+10.5", "L1", "7-3", "+141", False),
        ("BOS", 84, 71, "+5.0", "L1", "4-6", "+84", False),
        ("CWS", 79, 76, "--", "W1", "4-6", "+35", True),
        ("HOU", 77, 78, "2.0", "L2", "3-7", "-57", False),
        ("TOR", 76, 79, "3.0", "L2", "4-6", "-47", False),
        ("BAL", 75, 80, "4.0", "L2", "5-5", "-28", False),
    ],
    "NL East": [
        ("ATL", 91, 64, "--", "--", "W2", "6-4", "+118"),
        ("PHI", 85, 70, "6.0", "--", "L2", "4-6", "+24"),
        ("MIA", 76, 79, "15.0", "9.0", "L2", "4-6", "+1"),
        ("WSN", 73, 82, "18.0", "12.0", "W2", "6-4", "+14"),
        ("NYM", 71, 84, "20.0", "14.0", "W2", "4-6", "-36"),
    ],
    "NL Central": [
        ("MIL", 97, 58, "--", "--", "W2", "8-2", "+199"),
        ("CHC", 86, 69, "11.0", "+1.0", "W1", "5-5", "+144"),
        ("PIT", 78, 77, "19.0", "7.0", "W3", "6-4", "+28"),
        ("STL", 75, 80, "22.0", "10.0", "L4", "3-7", "-25"),
        ("CIN", 72, 83, "25.0", "13.0", "L1", "3-7", "-155"),
    ],
    "NL West": [
        ("LAD", 95, 60, "--", "--", "W3", "7-3", "+191"),
        ("SDP", 86, 69, "9.0", "+1.0", "W4", "9-1", "+37"),
        ("ARI", 81, 74, "14.0", "4.0", "W1", "4-6", "-5"),
        ("SFG", 64, 91, "31.0", "21.0", "L2", "4-6", "-82"),
        ("COL", 57, 98, "38.0", "28.0", "W1", "2-8", "-176"),
    ],
    "NL Wild Card": [
        ("CHC", 86, 69, "+1.0", "W1", "5-5", "+144", False),
        ("SDP", 86, 69, "+1.0", "W4", "9-1", "+37", False),
        ("PHI", 85, 70, "--", "L2", "4-6", "+24", True),
        ("ARI", 81, 74, "4.0", "W1", "4-6", "-5", False),
        ("PIT", 78, 77, "7.0", "W3", "6-4", "+28", False),
        ("MIA", 76, 79, "9.0", "L2", "4-6", "+1", False),
    ],
}

UPCOMING = [
    ("PHI", "NYM", "Cristopher Sánchez vs. Jonah Tong", "1:10 PM ET", "2026-09-20T17:10:00Z", ""),
    ("KCR", "PIT", "Michael Wacha vs. Lake Bachar", "1:35 PM ET", "2026-09-20T17:35:00Z", ""),
    ("CHC", "CIN", "TBD vs. Rhett Lowder", "1:40 PM ET", "2026-09-20T17:40:00Z", ""),
    ("ATH", "CLE", "Jack Perkins vs. Gavin Williams", "1:40 PM ET", "2026-09-20T17:40:00Z", ""),
    ("BOS", "TBR", "Patrick Sandoval vs. Griffin Jax", "1:40 PM ET", "2026-09-20T17:40:00Z", ""),
    ("ATL", "HOU", "Martín Pérez vs. Hunter Brown", "2:10 PM ET", "2026-09-20T18:10:00Z", ""),
    ("DET", "CWS", "Troy Melton vs. Davis Martin", "2:10 PM ET", "2026-09-20T18:10:00Z", ""),
    ("WSN", "STL", "Jake Irvin vs. Quinn Mathews", "2:15 PM ET", "2026-09-20T18:15:00Z", ""),
    ("TOR", "TEX", "Spencer Miles vs. Jacob deGrom", "2:35 PM ET", "2026-09-20T18:35:00Z", ""),
    ("SEA", "COL", "Kade Anderson vs. Tomoyuki Sugano", "3:10 PM ET", "2026-09-20T19:10:00Z", ""),
    ("MIN", "LAA", "Dean Kremer vs. Ryan Johnson", "4:07 PM ET", "2026-09-20T20:07:00Z", ""),
    ("SFG", "LAD", "Matt Wilkinson vs. TBD", "4:10 PM ET", "2026-09-20T20:10:00Z", ""),
    ("MIA", "SDP", "Sandy Alcantara vs. Walker Buehler", "4:10 PM ET", "2026-09-20T20:10:00Z", ""),
    ("NYY", "ARI", "Will Warren vs. Corbin Burnes", "4:10 PM ET", "2026-09-20T20:10:00Z", ""),
    ("MIL", "BAL", "Jacob Misiorowski vs. Brandon Young", "7:20 PM ET", "2026-09-20T23:20:00Z", ""),
]

OFF_TONIGHT: list[str] = []

TEAM_SUMMARIES = {
    "CHC": "Your Cubs: Won 5–2 at Cincinnati; Boyd earned the win. At Cincinnati today.",
    "CIN": "Your Reds: Lost 2–5 to Chicago; Lodolo took the loss. Host Chicago today.",
    "KCR": "Your Royals: Lost 5–6 at Pittsburgh; Cruz took the loss. At Pittsburgh today.",
    "PIT": "Your Pirates: Won 6–5 over Kansas City; Weaver earned the win. Host Kansas City today.",
    "MIL": "Your Brewers: Won 1–0 at Baltimore; Gasser went seven scoreless. At Baltimore tonight.",
    "BAL": "Your Orioles: Lost 0–1 to Milwaukee; Rogers took the loss despite 10 strikeouts. Host Milwaukee tonight.",
    "ATH": "Your Athletics: Lost 6–12 at Cleveland; Lopez took the loss. At Cleveland today.",
    "CLE": "Your Guardians: Won 12–6 over Oakland; Martínez homered twice. Host Athletics today.",
    "BOS": "Your Red Sox: Lost 1–2 at Tampa Bay; Bello struck out 11 over eight. At Tampa Bay today.",
    "TBR": "Your Rays: Won 2–1 over Boston; Palacios walked it off. Host Boston today.",
    "PHI": "Your Phillies: Lost 3–10 at New York; Painter took the loss. At New York today.",
    "NYM": "Your Mets: Won 10–3 over Philadelphia; Benge set the rookie hit record. Host Philadelphia today.",
    "DET": "Your Tigers: Lost 1–3 at Chicago; eight hits weren't enough. At Chicago today.",
    "CWS": "Your White Sox: Won 3–1 over Detroit; Burke earned the win. Host Detroit today.",
    "TOR": "Your Blue Jays: Lost 2–6 at Texas; Soriano took the loss. At Texas today.",
    "TEX": "Your Rangers: Won 6–2 over Toronto; Montgomery earned the win. Host Toronto today.",
    "SEA": "Your Mariners: Lost 3–5 at Colorado; Ferrer took the loss. At Colorado today.",
    "COL": "Your Rockies: Won 5–3 over Seattle; four in the seventh keyed it. Host Seattle today.",
    "ATL": "Your Braves: Won 6–3 at Houston; Acuña's grand slam in the seventh. At Houston today.",
    "HOU": "Your Astros: Lost 3–6 to Atlanta; Blubaugh took the loss. Host Atlanta today.",
    "WSN": "Your Nationals: Won 8–5 in 11 at St. Louis; four in the 11th keyed it. At St. Louis today.",
    "STL": "Your Cardinals: Lost 5–8 to Washington in 11; Graceffo took the loss. Host Washington today.",
    "MIN": "Your Twins: Lost 5–6 in 11 at Los Angeles; Moore walked it off for the Angels. At Los Angeles today.",
    "LAA": "Your Angels: Won 6–5 over Minnesota in 11; Moore's walk-off single. Host Minnesota today.",
    "MIA": "Your Marlins: Lost 6–7 in 10 at San Diego; Ekness took the loss. At San Diego today.",
    "SDP": "Your Padres: Won 7–6 over Miami in 10; Morgan got the win. Host Miami today.",
    "NYY": "Your Yankees: Lost 3–5 at Arizona; Smith's walk-off homer ended it. At Arizona today.",
    "ARI": "Your Diamondbacks: Won 5–3 over New York; Smith walked it off. Host New York today.",
    "SFG": "Your Giants: Lost 4–10 at Los Angeles; Marte took the loss. At Los Angeles today.",
    "LAD": "Your Dodgers: Won 10–4 over San Francisco; Betts went 4-for-4. Host San Francisco today.",
}

RACE_AL_RECAP = (
    "Robert Gasser shut out Baltimore over seven in a 1–0 Brewers win — "
    "Trevor Rogers struck out 10 in eight and still took the loss. "
    "Angel Martínez homered twice in Cleveland's 12–6 rout of Oakland. "
    "Pavin Smith's walk-off homer lifted Arizona to a 5–3 win over New York."
)
RACE_AL_SINCE = "The Rays are 8–2 in their last ten."
RACE_NL_RECAP = (
    "Carson Benge set the Mets' rookie hit record in a 10–3 win over Philadelphia. "
    "Ronald Acuña Jr.'s go-ahead grand slam keyed Atlanta's 6–3 win at Houston. "
    "Mookie Betts went 4-for-4 in the Dodgers' 10–4 win over San Francisco."
)
RACE_NL_SINCE = "The Padres are 9–1 in their last ten."


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
    return m.group(1).replace("2026-09-18", ISSUE_DATE)


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
<title>Scorebook - Saturday, September 19</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Saturday, September 19" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Saturday, September 19" />
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
  <p class="kicker">Saturday night</p>
  <h1>Saturday, September 19</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("martinez_two_homers")}
  <p class="cap">{CLIPS["martinez_two_homers"]["cap"]}</p>
{clip_html("benge_rookie_record")}
  <p class="cap">{CLIPS["benge_rookie_record"]["cap"]}</p>
{clip_html("acuna_grand_slam")}
  <p class="cap">{CLIPS["acuna_grand_slam"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="martinez_two_homers" required> Martínez's two-homer game</label>
      <label><input type="radio" name="play" value="benge_rookie_record"> Benge's rookie hit record</label>
      <label><input type="radio" name="play" value="acuna_grand_slam"> Acuña's go-ahead grand slam</label>
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
{clip_html("moore_walkoff")}
  <p class="cap">{CLIPS["moore_walkoff"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Bottom of the third at Progressive Field. Cleveland had already scored five in the first when the Guardians put up five more — part of a 12-run rout. Guardians 12, Athletics 6.</p>
{clip_html("guardians_five_run_third")}
  <p class="cap">{CLIPS["guardians_five_run_third"]["cap"]}</p>

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
      <p class="subn">Standings through Saturday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
{al_tables}
    </div>

    <div class="panel-nl" id="nl-panel">
      <div class="recap" data-share-card="race-nl.png" data-share-text-src="share/race-nl.txt">
        <p class="subn">Last night</p>
        <p>{RACE_NL_RECAP}</p>
        <p class="subn">Since August 13</p>
        <p>{RACE_NL_SINCE}</p>
      </div>
      <p class="subn">Standings through Saturday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
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
