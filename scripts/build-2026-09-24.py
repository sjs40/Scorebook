#!/usr/bin/env python3
"""Generate /workspace/2026-09-24/index.html and share race text files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-24"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-09-23" / "index.html"
ISSUE_DATE = "2026-09-24"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Lucas Spence hit three homers in Houston's 7–5 win at Oakland. "
    "White Sox clinched a postseason berth with a 9–1 rout at Kansas City. "
    "George Lombard Jr.'s go-ahead homer lifted the Yankees to a 6–4 win over Tampa Bay. "
    "Arizona scored six in the first in a 12–8 slugfest at Colorado."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/24"

CLIPS = {
    "spence_three": {
        "video": f"{MLB_CDN}/17114bb6-fde8b515-1244eba3-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "lucas-spence-s-three-homer-game",
        "cap": (
            "Lucas Spence hit three homers — "
            "Houston beat Oakland 7–5."
        ),
    },
    "sox_clinch": {
        "video": f"{MLB_CDN}/e9d8287a-942b26c2-1afb0746-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "white-sox-clinch-postseason-berth-after-9-1-win",
        "cap": (
            "White Sox clinched a postseason berth — "
            "Chicago beat Kansas City 9–1."
        ),
    },
    "skenes_200": {
        "video": f"{MLB_CDN}/8da2e29a-43839ae7-0f8c955c-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "paul-skenes-fans-eight-logs-200th-k-vs-cardinals",
        "cap": (
            "Paul Skenes struck out eight and logged his 200th K — "
            "Pirates 2, Cardinals 1."
        ),
    },
    "lombard_deke": {
        "video": f"{MLB_CDN}/f91927d3-14861099-eade5452-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "brody-hopkins-ball-to-anthony-volpe-rd4qqe",
        "cap": (
            "George Lombard Jr. dekes out Liam Hicks on the way home — "
            "That's baseball."
        ),
    },
    "dbacks_first": {
        "video": f"{MLB_CDN}/898e0df2-7b5789fb-e1fce047-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "d-backs-plate-six-in-the-first-inning-vs-rockies",
        "cap": (
            "Arizona plated six in the first — "
            "part of a 12–8 win at Colorado."
        ),
    },
}

PITCHERS = [
    ("Ian Seymour", "TBR", 66, "5.0", 1, 0, 0, 3, "NYY"),
    ("Paul Skenes", "PIT", 65, "6.1", 3, 1, 2, 8, "STL"),
    ("Joey Cantillo", "CLE", 65, "5.0", 1, 0, 2, 4, "BOS"),
    ("David Sandlin", "CWS", 61, "6.0", 5, 1, 0, 7, "KCR"),
]

HITTERS = [
    ("Lucas Spence", "HOU", 12, 4, 3, 3, 3, 5, 0),
    ("Zack Gelof", "ATH", 8, 3, 2, 2, 2, 2, 0),
    ("Cole Carrigg", "COL", 7, 5, 4, 1, 1, 3, 0),
    ("Josh Jung", "TEX", 7, 3, 3, 2, 1, 2, 0),
    ("Nolan Arenado", "ARI", 6, 5, 3, 1, 1, 3, 0),
    ("George Lombard Jr.", "NYY", 6, 4, 2, 2, 1, 3, 0),
    ("Jeff McNeil", "ATH", 6, 4, 2, 2, 1, 3, 0),
    ("Héctor Rodríguez", "CIN", 6, 4, 2, 2, 1, 2, 0),
]

GAMES = [
    ("STL", "PIT", 1, 2, [1, 0, 0, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0, 1, 0], 5, 2, 7, 0, "W Luke Weaver · L Ryne Stanek · S Mason Montgomery"),
    ("CWS", "KCR", 9, 1, [3, 3, 0, 2, 1, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0], 12, 0, 7, 2, "W David Sandlin · L Randy Dobnak"),
    ("MIA", "CHC", 1, 2, [0, 0, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 1, 0, 0, 0], 5, 0, 6, 1, "W Matthew Boyd · L Jack Ralston · S Ryan Zeferjahn"),
    ("NYM", "TEX", 1, 3, [1, 0, 0, 0, 0, 0, 0, 0, 0], [2, 0, 0, 0, 0, 1, 0, 0, 0], 4, 0, 7, 0, "W Kumar Rocker · L Zac Thornton · S Jordan Montgomery"),
    ("ARI", "COL", 12, 8, [6, 2, 0, 2, 1, 1, 0, 0, 0], [0, 0, 0, 1, 0, 1, 4, 2, 0], 18, 0, 17, 0, "W Eduardo Rodriguez · L Tanner Gordon"),
    ("MIL", "PHI", 5, 1, [0, 1, 0, 0, 0, 0, 0, 3, 1], [0, 0, 1, 0, 0, 0, 0, 0, 0], 11, 1, 4, 0, "W JoJo Romero · L José Alvarado · S Antonio Senzatela"),
    ("CLE", "BOS", 1, 0, [0, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], 4, 1, 2, 1, "W Joey Cantillo · L Ranger Suarez · S Cade Smith"),
    ("TBR", "NYY", 4, 6, [0, 0, 2, 0, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 1, 3, 2, 0], 9, 1, 7, 2, "W Bradley Hanner · L Steven Matz"),
    ("CIN", "ATL", 7, 6, [1, 1, 3, 0, 0, 2, 0, 0, 0], [4, 0, 1, 0, 1, 0, 0, 0, 0], 7, 0, 12, 0, "W Connor Phillips · L AJ Smith-Shawver · S Emilio Pagán"),
    ("HOU", "ATH", 7, 5, [0, 3, 0, 0, 0, 1, 1, 1, 1], [0, 0, 4, 0, 0, 0, 0, 1, 0], 10, 0, 11, 0, "W Miguel Ullola · L Scott Blewett · S Bryan Abreu"),
    ("LAA", "SEA", 6, 4, [0, 1, 0, 0, 2, 2, 0, 1, 0], [0, 3, 0, 0, 1, 0, 0, 0, 0], 9, 0, 7, 1, "W Grayson Rodriguez · L Bryan Woo · S Ryan Watson"),
    ("SDP", "LAD", 4, 2, [0, 0, 0, 0, 0, 1, 3, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 1], 6, 0, 7, 0, "W Yuki Matsui · L Tyler Glasnow · S Mason Miller"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 96, 63, "--", "--", "L2", "6-4", "+77"),
        ("NYY", 92, 67, "4.0", "+10.0", "W2", "6-4", "+143"),
        ("BOS", 85, 74, "11.0", "+3.0", "L1", "4-6", "+79"),
        ("BAL", 78, 81, "18.0", "+4.0", "W3", "6-4", "-26"),
        ("TOR", 77, 82, "19.0", "+5.0", "L3", "3-7", "-47"),
    ],
    "AL Central": [
        ("CLE", 83, 76, "--", "--", "W1", "8-2", "+3"),
        ("CWS", 82, 77, "1.0", "--", "W1", "6-4", "+52"),
        ("MIN", 75, 84, "8.0", "+7.0", "W2", "5-5", "-64"),
        ("DET", 74, 85, "9.0", "+8.0", "L2", "4-6", "+71"),
        ("KCR", 68, 91, "15.0", "+14.0", "L1", "2-8", "-112"),
    ],
    "AL West": [
        ("HOU", 79, 80, "--", "--", "W1", "4-6", "-51"),
        ("TEX", 79, 80, "--", "+3.0", "W1", "6-4", "-40"),
        ("SEA", 74, 85, "5.0", "+8.0", "L1", "4-6", "-64"),
        ("ATH", 63, 96, "16.0", "+19.0", "L1", "3-7", "-219"),
        ("LAA", 61, 98, "18.0", "+21.0", "W1", "5-5", "-91"),
    ],
    "AL Wild Card": [
        ("NYY", 92, 67, "+10.0", "W2", "6-4", "+143", False),
        ("BOS", 85, 74, "+3.0", "L1", "4-6", "+79", False),
        ("CWS", 82, 77, "--", "W1", "6-4", "+52", True),
        ("TEX", 79, 80, "3.0", "W1", "6-4", "-40", False),
        ("BAL", 78, 81, "4.0", "W3", "6-4", "-26", False),
        ("TOR", 77, 82, "5.0", "L3", "3-7", "-47", False),
    ],
    "NL East": [
        ("ATL", 93, 66, "--", "--", "L1", "5-5", "+116"),
        ("PHI", 87, 72, "6.0", "--", "L2", "5-5", "+24"),
        ("MIA", 78, 81, "15.0", "+9.0", "L1", "5-5", "+3"),
        ("WSN", 75, 84, "18.0", "+12.0", "W2", "7-3", "+9"),
        ("NYM", 73, 86, "20.0", "+14.0", "L1", "4-6", "-35"),
    ],
    "NL Central": [
        ("MIL", 100, 59, "--", "--", "W2", "7-3", "+207"),
        ("CHC", 88, 71, "12.0", "+1.0", "W1", "5-5", "+146"),
        ("PIT", 81, 78, "19.0", "+6.0", "W1", "7-3", "+28"),
        ("STL", 77, 82, "23.0", "+10.0", "L1", "4-6", "-22"),
        ("CIN", 74, 85, "26.0", "+13.0", "W1", "4-6", "-159"),
    ],
    "NL West": [
        ("LAD", 97, 62, "--", "--", "L2", "7-3", "+194"),
        ("SDP", 89, 70, "8.0", "+2.0", "W2", "8-2", "+40"),
        ("ARI", 85, 74, "12.0", "+2.0", "W5", "6-4", "+10"),
        ("SFG", 65, 94, "32.0", "+22.0", "L2", "3-7", "-84"),
        ("COL", 57, 102, "40.0", "+30.0", "L4", "2-8", "-188"),
    ],
    "NL Wild Card": [
        ("SDP", 89, 70, "+2.0", "W2", "8-2", "+40", False),
        ("CHC", 88, 71, "+1.0", "W1", "5-5", "+146", False),
        ("PHI", 87, 72, "--", "L2", "5-5", "+24", True),
        ("ARI", 85, 74, "2.0", "W5", "6-4", "+10", False),
        ("PIT", 81, 78, "6.0", "W1", "7-3", "+28", False),
        ("MIA", 78, 81, "9.0", "L1", "5-5", "+3", False),
    ],
}

UPCOMING = [
    ("CHC", "BOS", "Clay Holmes vs. Alec Gamboa", "1:05 PM ET", "2026-09-25T17:05:00Z", "Game 1"),
    ("CHC", "BOS", "David Peterson vs. Brayan Bello", "6:05 PM ET", "2026-09-25T22:05:00Z", "Game 2"),
    ("BAL", "NYY", "Brandon Young vs. TBD", "4:05 PM ET", "2026-09-25T20:05:00Z", "Game 1"),
    ("BAL", "NYY", "Trevor Rogers vs. Brendan Beck", "4:10 PM ET", "2026-09-25T20:10:00Z", "Game 2"),
    ("PIT", "DET", "Bubba Chandler vs. Jackson Jobe", "6:40 PM ET", "2026-09-25T22:40:00Z", ""),
    ("TBR", "PHI", "Freddy Peralta vs. Cristopher Sánchez", "6:40 PM ET", "2026-09-25T22:40:00Z", ""),
    ("NYM", "WSN", "TBD vs. Andrew Alvarez", "6:45 PM ET", "2026-09-25T22:45:00Z", ""),
    ("CIN", "TOR", "Nick Lodolo vs. TBD", "7:07 PM ET", "2026-09-25T23:07:00Z", ""),
    ("ATL", "MIA", "TBD vs. Eury Pérez", "7:10 PM ET", "2026-09-25T23:10:00Z", ""),
    ("CLE", "KCR", "Gavin Williams vs. Noah Cameron", "7:40 PM ET", "2026-09-25T23:40:00Z", ""),
    ("COL", "CWS", "Tomoyuki Sugano vs. Sean Burke", "7:40 PM ET", "2026-09-25T23:40:00Z", ""),
    ("STL", "MIL", "Michael McGreevy vs. Robert Gasser", "7:40 PM ET", "2026-09-25T23:40:00Z", ""),
    ("TEX", "MIN", "Jacob deGrom vs. Joe Ryan", "8:10 PM ET", "2026-09-26T00:10:00Z", ""),
    ("HOU", "ATH", "Hunter Brown vs. Jacob Lopez", "9:40 PM ET", "2026-09-26T01:40:00Z", ""),
    ("ARI", "SDP", "Brandon Pfaadt vs. TBD", "9:40 PM ET", "2026-09-26T01:40:00Z", ""),
    ("LAA", "SEA", "Reid Detmers vs. Bryce Miller", "10:10 PM ET", "2026-09-26T02:10:00Z", ""),
    ("LAD", "SFG", "Tarik Skubal vs. Yunior Marte", "10:15 PM ET", "2026-09-26T02:15:00Z", ""),
]

OFF_TONIGHT: list[str] = []

TEAM_SUMMARIES = {
    "TBR": "Your Rays: Lost 4–6 at New York; Matz took the loss. At Philadelphia tonight.",
    "NYY": "Your Yankees: Won 6–4 over Tampa Bay; Hanner earned the win and George Lombard Jr. homered. Host Baltimore tonight.",
    "WSN": "Your Nationals: Off yesterday. Host New York tonight.",
    "DET": "Your Tigers: Off yesterday. Host Pittsburgh tonight.",
    "STL": "Your Cardinals: Lost 1–2 at Pittsburgh; Stanek took the loss. At Milwaukee tonight.",
    "PIT": "Your Pirates: Won 2–1 over St. Louis; Weaver earned the win and Paul Skenes struck out eight. At Detroit tonight.",
    "MIL": "Your Brewers: Won 5–1 at Philadelphia; Romero earned the win. Host St. Louis tonight.",
    "PHI": "Your Phillies: Lost 1–5 to Milwaukee; Alvarado took the loss. Host Tampa Bay tonight.",
    "CLE": "Your Guardians: Won 1–0 at Boston and clinched a postseason berth; Cantillo earned the win. At Kansas City tonight.",
    "BOS": "Your Red Sox: Lost 0–1 to Cleveland; Suarez took the loss. Host Chicago tonight.",
    "CIN": "Your Reds: Won 7–6 at Atlanta; Phillips earned the win and Elly De La Cruz hit his 30th homer. At Toronto tonight.",
    "ATL": "Your Braves: Lost 6–7 to Cincinnati; Smith-Shawver took the loss. At Miami tonight.",
    "CWS": "Your White Sox: Won 9–1 at Kansas City and clinched a postseason berth; Sandlin earned the win. Host Colorado tonight.",
    "KCR": "Your Royals: Lost 1–9 to Chicago; Dobnak took the loss. Host Cleveland tonight.",
    "MIA": "Your Marlins: Lost 1–2 at Chicago; Ralston took the loss. Host Atlanta tonight.",
    "CHC": "Your Cubs: Won 2–1 over Miami and clinched a Wild Card berth; Boyd tossed seven scoreless. At Boston tonight.",
    "NYM": "Your Mets: Lost 1–3 at Texas; Thornton took the loss. At Washington tonight.",
    "TEX": "Your Rangers: Won 3–1 over New York; Rocker earned the win. At Minnesota tonight.",
    "ARI": "Your Diamondbacks: Won 12–8 at Colorado; Rodriguez earned the win and Arenado homered. At San Diego tonight.",
    "COL": "Your Rockies: Lost 8–12 to Arizona; Gordon took the loss. At Chicago tonight.",
    "LAA": "Your Angels: Won 6–4 at Seattle; Rodriguez earned the win. At Seattle tonight.",
    "ATH": "Your Athletics: Lost 5–7 to Houston; Blewett took the loss. Host Houston tonight.",
    "HOU": "Your Astros: Won 7–5 at Oakland; Ullola earned the win and Lucas Spence hit three homers. At Oakland tonight.",
    "SEA": "Your Mariners: Lost 4–6 to the Angels; Woo took the loss. Host the Angels tonight.",
    "MIN": "Your Twins: Off yesterday. Host Texas tonight.",
    "SFG": "Your Giants: Off yesterday. Host the Dodgers tonight.",
    "SDP": "Your Padres: Won 4–2 at Los Angeles and clinched a postseason berth; Matsui earned the win. Host Arizona tonight.",
    "LAD": "Your Dodgers: Lost 2–4 to San Diego; Glasnow took the loss. At San Francisco tonight.",
    "TOR": "Your Blue Jays: Off yesterday. Host Cincinnati tonight.",
    "BAL": "Your Orioles: Off yesterday. At New York tonight.",
}

RACE_AL_RECAP = (
    "Lucas Spence hit three homers in Houston's 7–5 win at Oakland. "
    "White Sox clinched a postseason berth with a 9–1 rout at Kansas City. "
    "George Lombard Jr.'s go-ahead homer lifted the Yankees to a 6–4 win over Tampa Bay."
)
RACE_AL_SINCE = "The Guardians are 8–2 in their last ten."
RACE_NL_RECAP = (
    "Arizona scored six in the first in a 12–8 slugfest at Colorado. "
    "Cubs clinched a Wild Card behind Matthew Boyd's seven scoreless. "
    "Padres beat the Dodgers 4–2 and clinched a postseason berth."
)
RACE_NL_SINCE = "The Brewers are 7–3 in their last ten."


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
    return m.group(1).replace("2026-09-23", ISSUE_DATE)


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
<title>Scorebook - Thursday, September 24</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Thursday, September 24" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Thursday, September 24" />
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
  <h1>Thursday, September 24</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("spence_three")}
  <p class="cap">{CLIPS["spence_three"]["cap"]}</p>
{clip_html("sox_clinch")}
  <p class="cap">{CLIPS["sox_clinch"]["cap"]}</p>
{clip_html("skenes_200")}
  <p class="cap">{CLIPS["skenes_200"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="spence_three" required> Spence's three homers</label>
      <label><input type="radio" name="play" value="sox_clinch"> White Sox clinch</label>
      <label><input type="radio" name="play" value="skenes_200"> Skenes' 200th K</label>
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
{clip_html("lombard_deke")}
  <p class="cap">{CLIPS["lombard_deke"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Top of the first at Coors Field. Arizona put up six runs before Colorado came to bat — part of a 12–8 slugfest. Diamondbacks 12, Rockies 8.</p>
{clip_html("dbacks_first")}
  <p class="cap">{CLIPS["dbacks_first"]["cap"]}</p>

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
