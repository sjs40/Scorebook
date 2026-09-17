#!/usr/bin/env python3
"""Generate /workspace/2026-09-16/index.html and share race text files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-16"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-09-15" / "index.html"
ISSUE_DATE = "2026-09-16"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Victor Caratini's walk-off single in the 13th lifted Minnesota past New York 5–4. "
    "Ethan Salas homered twice as San Diego beat Colorado 9–3. "
    "Zack Wheeler shut out Washington on four hits over seven in a 3–0 win. "
    "Chris Bassitt and Baltimore rolled at New York 7–1."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/16"

CLIPS = {
    "caratini_walkoff": {
        "video": f"{MLB_CDN}/ae9c4641-cdc7d181-2dec0d1a-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "john-schreiber-in-play-run-s-to-victor-caratini",
        "cap": (
            "Victor Caratini singled with one out in the 13th — Minnesota and New York were tied 4–4. "
            "Twins 5, Yankees 4 — Zebby Matthews fanned eight over six scoreless innings."
        ),
    },
    "salas_two_homers": {
        "video": f"{MLB_CDN}/d9088dd9-a4efc73f-023a316e-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "ethan-salas-two-homer-game-fuels-padres-win",
        "cap": (
            "Ethan Salas homered twice in his first multi-homer game. "
            "Padres 9, Rockies 3 — San Diego scored four in the fifth."
        ),
    },
    "wheeler_shutout": {
        "video": f"{MLB_CDN}/8d3e24ab-57a0bed3-596adcac-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "arraez-wheeler-lead-phillies-to-a-3-0-win",
        "cap": (
            "Zack Wheeler: seven scoreless innings, four hits, and five strikeouts. "
            "Phillies 3, Nationals 0 — Luis Arraez doubled in the go-ahead run."
        ),
    },
    "walker_errant": {
        "video": None,
        "slug": "carson-seymour-in-play-run-s-to-nathan-church",
        "cap": (
            "San Francisco led 6–5 in the 10th when Jordan Walker scored on an errant throw — "
            "and the Cardinals still lost when Drew Gilbert homered in the 10th. "
            "That's baseball — Giants 6, Cardinals 5."
        ),
    },
    "orioles_third": {
        "video": f"{MLB_CDN}/c60ae2a1-a0aae523-f332ca07-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "the-orioles-go-back-to-back-in-the-3rd-inning",
        "cap": (
            "Jeremiah Jackson and Samuel Basallo went back-to-back — three runs keyed a 7–1 rout. "
            "Orioles 7, Mets 1."
        ),
    },
    "crow_armstrong": {
        "video": f"{MLB_CDN}/03790a28-42052086-8029b954-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "pete-crow-armstrong-lifts-two-homers-in-cubs-win",
        "cap": (
            "Pete Crow-Armstrong homered twice and Alex Bregman drove in four. "
            "Cubs 8, Braves 4 — Shota Imanaga fanned eight over six."
        ),
    },
}

PITCHERS = [
    ("Zebby Matthews", "MIN", 70, "6.0", 2, 0, 2, 8, "NYY"),
    ("Anthony Molina", "SFG", 68, "5.2", 2, 0, 1, 6, "STL"),
    ("Zack Wheeler", "PHI", 67, "7.0", 4, 0, 1, 5, "WSN"),
    ("Shota Imanaga", "CHC", 64, "6.0", 4, 1, 0, 8, "ATL"),
]

HITTERS = [
    ("Pete Crow-Armstrong", "CHC", 11, 4, 3, 3, 2, 3, 0),
    ("Alex Bregman", "CHC", 9, 4, 3, 3, 1, 4, 0),
    ("Ethan Salas", "SDP", 8, 4, 2, 2, 2, 3, 0),
    ("Christian Encarnacion-Strand", "BAL", 8, 4, 3, 3, 1, 2, 0),
    ("Gabriel Moreno", "ARI", 7, 4, 3, 2, 1, 1, 0),
    ("Jakob Marsee", "MIA", 6, 3, 2, 2, 1, 2, 1),
    ("Tommy White", "ATH", 6, 4, 3, 1, 1, 1, 0),
    ("Michael Massey", "KCR", 6, 5, 3, 1, 1, 1, 0),
]

GAMES = [
    ("CWS", "CLE", 3, 6, [0, 0, 0, 0, 3, 0, 0, 0, 0], [0, 0, 2, 0, 0, 4, 0, 0, 0], 8, 1, 5, 0, "W Parker Messick · L Hagen Smith · S Cade Smith"),
    ("SFG", "STL", 6, 5, [0, 0, 1, 0, 0, 0, 2, 1, 0, 2], [0, 0, 0, 0, 0, 0, 2, 0, 2, 1], 13, 2, 5, 2, "W Reiver Sanmartin · L Riley O'Brien · S Joel Kuhnel"),
    ("NYY", "MIN", 4, 5, [0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 0, 0], [1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1], 9, 1, 10, 0, "W Tommy Nance · L John Schreiber"),
    ("DET", "TOR", 1, 5, [1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 2, 1, 2, 0, 0, 0], 7, 3, 9, 0, "W Max Scherzer · L Keider Montero · S Louis Varland"),
    ("LAD", "CIN", 2, 6, [0, 0, 1, 0, 0, 1, 0, 0, 0], [0, 0, 2, 0, 1, 1, 2, 0, 0], 7, 0, 13, 0, "W Tejay Antone · L Seth Halvorsen"),
    ("ATH", "TBR", 3, 4, [0, 0, 2, 0, 0, 1, 0, 0, 0], [2, 2, 0, 0, 0, 0, 0, 0, 0], 8, 1, 9, 0, "W Nick Martinez · L Brady Basso · S Cole Sulser"),
    ("MIL", "PIT", 5, 4, [0, 2, 0, 0, 1, 0, 2, 0, 0], [0, 0, 0, 1, 2, 1, 0, 0, 0], 10, 0, 12, 0, "W Antonio Senzatela · L Carmen Mlodzinski · S Trevor Megill"),
    ("PHI", "WSN", 3, 0, [2, 0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], 5, 0, 4, 0, "W Zack Wheeler · L Jared Simpson · S Jhoan Duran"),
    ("BAL", "NYM", 7, 1, [1, 2, 3, 0, 0, 0, 0, 0, 1], [0, 0, 0, 1, 0, 0, 0, 0, 0], 9, 1, 7, 0, "W Chris Bassitt · L Xzavion Curry"),
    ("ATL", "CHC", 4, 8, [0, 0, 0, 0, 0, 1, 1, 0, 2], [1, 0, 1, 1, 3, 0, 1, 1, 0], 8, 0, 12, 0, "W Shota Imanaga · L JR Ritchie"),
    ("BOS", "TEX", 3, 7, [2, 0, 0, 0, 1, 0, 0, 0, 0], [1, 0, 0, 1, 1, 0, 3, 1, 0], 3, 1, 13, 0, "W Nathan Eovaldi · L Erik Miller"),
    ("KCR", "HOU", 5, 2, [0, 0, 0, 2, 0, 0, 0, 3, 0], [0, 0, 0, 0, 0, 0, 0, 1, 1], 8, 0, 8, 1, "W Daniel Lynch IV · L Cristian Javier"),
    ("SDP", "COL", 9, 3, [2, 1, 0, 1, 4, 1, 0, 0, 0], [1, 0, 0, 0, 0, 2, 0, 0, 0], 13, 0, 4, 0, "W Robbie Ray · L Mason Adams"),
    ("SEA", "LAA", 7, 2, [2, 0, 0, 0, 3, 2, 0, 0, 0], [1, 1, 0, 0, 0, 0, 0, 0, 0], 9, 1, 10, 2, "W Carlos Vargas · L Yusei Kikuchi"),
    ("MIA", "ARI", 4, 3, [0, 2, 2, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 1, 0, 0, 1, 0], 10, 0, 10, 1, "W Cade Gibson · L Merrill Kelly · S Sandy Alcantara"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 92, 59, "--", "--", "W5", "8-2", "+71"),
        ("NYY", 88, 64, "4.5", "+11.0", "L1", "7-3", "+136"),
        ("BOS", 82, 70, "10.5", "+5.0", "L2", "5-5", "+82"),
        ("TOR", 76, 77, "17.0", "1.5", "W1", "4-6", "-37"),
        ("BAL", 75, 78, "18.0", "2.5", "W3", "6-4", "-26"),
    ],
    "AL Central": [
        ("CLE", 78, 75, "--", "--", "W2", "6-4", "-7"),
        ("CWS", 77, 75, "0.5", "--", "L2", "3-7", "+34"),
        ("DET", 72, 80, "5.5", "5.0", "L1", "7-3", "+76"),
        ("MIN", 71, 81, "6.5", "6.0", "W1", "3-7", "-73"),
        ("KCR", 67, 85, "10.5", "10.0", "W1", "4-6", "-93"),
    ],
    "AL West": [
        ("HOU", 76, 76, "--", "--", "L1", "3-7", "-54"),
        ("TEX", 76, 76, "--", "1.0", "W4", "6-4", "-38"),
        ("SEA", 71, 82, "5.5", "6.5", "W1", "5-5", "-56"),
        ("ATH", 61, 91, "15.0", "16.0", "L2", "5-5", "-205"),
        ("LAA", 58, 94, "18.0", "19.0", "L1", "4-6", "-78"),
    ],
    "AL Wild Card": [
        ("NYY", 88, 64, "+11.0", "L1", "7-3", "+136", False),
        ("BOS", 82, 70, "+5.0", "L2", "5-5", "+82", False),
        ("CWS", 77, 75, "--", "L2", "3-7", "+34", True),
        ("TEX", 76, 76, "1.0", "W4", "6-4", "-38", False),
        ("TOR", 76, 77, "1.5", "W1", "4-6", "-37", False),
        ("BAL", 75, 78, "2.5", "W3", "6-4", "-26", False),
    ],
    "NL East": [
        ("ATL", 89, 64, "--", "--", "L1", "4-6", "+111"),
        ("PHI", 84, 68, "4.5", "+1.0", "W1", "4-6", "+31"),
        ("MIA", 76, 77, "13.0", "7.5", "W2", "5-5", "+8"),
        ("WSN", 71, 82, "18.0", "12.5", "L1", "4-6", "+3"),
        ("NYM", 69, 83, "19.5", "14.0", "L4", "5-5", "-43"),
    ],
    "NL Central": [
        ("MIL", 95, 57, "--", "--", "W2", "7-3", "+200"),
        ("CHC", 85, 68, "10.5", "+1.5", "W1", "4-6", "+143"),
        ("PIT", 75, 77, "19.0", "8.0", "L2", "5-5", "+21"),
        ("STL", 75, 78, "19.5", "8.5", "L2", "4-6", "-14"),
        ("CIN", 71, 81, "24.0", "12.0", "W1", "3-7", "-148"),
    ],
    "NL West": [
        ("LAD", 92, 60, "--", "--", "L1", "7-3", "+173"),
        ("SDP", 83, 69, "9.0", "--", "W1", "9-1", "+23"),
        ("ARI", 80, 73, "12.5", "3.5", "L2", "5-5", "+0"),
        ("SFG", 64, 89, "28.5", "19.5", "W2", "5-5", "-70"),
        ("COL", 56, 96, "36.0", "27.0", "L1", "1-9", "-170"),
    ],
    "NL Wild Card": [
        ("CHC", 85, 68, "+1.5", "W1", "4-6", "+143", False),
        ("PHI", 84, 68, "+1.0", "W1", "4-6", "+31", False),
        ("SDP", 83, 69, "--", "W1", "9-1", "+23", True),
        ("ARI", 80, 73, "3.5", "L2", "5-5", "+0", False),
        ("MIA", 76, 77, "7.5", "W2", "5-5", "+8", False),
        ("PIT", 75, 77, "8.0", "L2", "5-5", "+21", False),
    ],
}

UPCOMING = [
    ("MIL", "PIT", "Kyle Harrison vs. Wilber Dotel", "12:35 PM ET", "2026-09-17T16:35:00Z", ""),
    ("LAD", "CIN", "Justin Wrobleski vs. Brady Singer", "12:40 PM ET", "2026-09-17T16:40:00Z", ""),
    ("ATH", "TBR", "Jeffrey Springs vs. Drew Rasmussen", "1:10 PM ET", "2026-09-17T17:10:00Z", ""),
    ("SDP", "COL", "Michael King vs. Tanner Gordon", "3:10 PM ET", "2026-09-17T19:10:00Z", ""),
    ("KCR", "HOU", "Seth Lugo vs. TBD", "7:15 PM ET", "2026-09-17T23:15:00Z", ""),
    ("PHI", "NYM", "Aaron Nola vs. Nolan McLean", "7:15 PM ET", "2026-09-17T23:15:00Z", ""),
    ("DET", "CWS", "Framber Valdez vs. Erick Fedde", "7:40 PM ET", "2026-09-17T23:40:00Z", ""),
    ("BOS", "TEX", "Sonny Gray vs. Tyler Alexander", "8:05 PM ET", "2026-09-18T00:05:00Z", ""),
    ("MIN", "LAA", "Taj Bradley vs. Walbert Ureña", "9:38 PM ET", "2026-09-18T01:38:00Z", ""),
]

OFF_TONIGHT = ["ATL", "BAL", "CHC", "CLE", "MIA", "NYM", "SEA", "SFG", "STL", "TOR", "WSN", "ARI"]

TEAM_SUMMARIES = {
    "CHC": "Your Cubs: Won 8–4 over Atlanta; Crow-Armstrong homered twice and Bregman drove in four. Off tonight.",
    "MIA": "Your Marlins: Won 4–3 at Arizona; Marsee homered and stole a base. Off tonight.",
    "SFG": "Your Giants: Won 6–5 in 10 at St. Louis; Drew Gilbert's go-ahead homer in the 10th. Off tonight.",
    "NYM": "Your Mets: Lost 1–7 to Baltimore; Bassitt went 6 2/3 of one-run ball. Off tonight.",
    "ATL": "Your Braves: Lost 4–8 at Chicago; Imanaga fanned eight. Off tonight.",
    "PHI": "Your Phillies: Won 3–0 at Washington; Wheeler shut them out for seven. At New York tonight.",
    "DET": "Your Tigers: Lost 1–5 at Toronto; Scherzer earned the win for Toronto. At Chicago tonight.",
    "CLE": "Your Guardians: Won 6–3 over Chicago; four runs in the sixth keyed the win. Off tonight.",
    "LAA": "Your Angels: Lost 2–7 to Seattle; Vargas earned the win. Host Minnesota tonight.",
    "PIT": "Your Pirates: Lost 4–5 to Milwaukee; Jones fanned nine over five. Host Milwaukee tonight.",
    "MIL": "Your Brewers: Won 5–4 at Pittsburgh; Senzatela earned the win. At Pittsburgh tonight.",
    "CIN": "Your Reds: Won 6–2 over Los Angeles; Antone earned the win. Host Dodgers tonight.",
    "BOS": "Your Red Sox: Lost 3–7 at Texas; Eovaldi struck out six over six. At Texas tonight.",
    "BAL": "Your Orioles: Won 7–1 at New York; Bassitt and back-to-back homers in the third. Off tonight.",
    "TBR": "Your Rays: Won 4–3 over Oakland; Martinez earned the win. Host Athletics tonight.",
    "TEX": "Your Rangers: Won 7–3 over Boston; Eovaldi struck out six. Host Boston tonight.",
    "MIN": "Your Twins: Won 5–4 in 13 over New York; Caratini's walk-off and Matthews' eight Ks. At Los Angeles tonight.",
    "CWS": "Your White Sox: Lost 3–6 at Cleveland despite a three-run fifth. Host Detroit tonight.",
    "TOR": "Your Blue Jays: Won 5–1 over Detroit; Scherzer went five innings. Off tonight.",
    "KCR": "Your Royals: Won 5–2 at Houston; Lynch earned the win. At Houston tonight.",
    "ARI": "Your Diamondbacks: Lost 3–4 to Miami; Kelly took the loss. Off tonight.",
    "HOU": "Your Astros: Lost 2–5 to Kansas City; Javier went 5 1/3. Host Kansas City tonight.",
    "NYY": "Your Yankees: Lost 4–5 in 13 at Minnesota; Rodón went six innings. Off tonight.",
    "SDP": "Your Padres: Won 9–3 at Colorado; Salas homered twice. At Colorado tonight.",
    "STL": "Your Cardinals: Lost 5–6 to San Francisco in 10; Gilbert's walk-off homer. Off tonight.",
    "COL": "Your Rockies: Lost 3–9 to San Diego; Adams took the loss. Host San Diego tonight.",
    "WSN": "Your Nationals: Lost 0–3 to Philadelphia; Wheeler shut them out. Off tonight.",
    "LAD": "Your Dodgers: Lost 2–6 at Cincinnati; Halvorsen took the loss. At Cincinnati tonight.",
    "ATH": "Your Athletics: Lost 3–4 at Tampa Bay; Basso took the loss. At Tampa Bay tonight.",
    "SEA": "Your Mariners: Won 7–2 at Los Angeles; Vargas earned the win. Off tonight.",
}

RACE_AL_RECAP = (
    "Victor Caratini's walk-off single in the 13th lifted Minnesota past New York 5–4. "
    "Chris Bassitt and Baltimore rolled at New York 7–1. "
    "Cleveland scored four in the sixth to beat Chicago 6–3."
)
RACE_AL_SINCE = "The Rays are 8–2 in their last ten."
RACE_NL_RECAP = (
    "Ethan Salas homered twice as San Diego beat Colorado 9–3. "
    "Zack Wheeler shut out Washington on four hits over seven. "
    "Drew Gilbert's go-ahead homer in the 10th lifted San Francisco past St. Louis 6–5."
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
    return m.group(1).replace("2026-09-15", ISSUE_DATE)


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
<title>Scorebook - Wednesday, September 16</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Wednesday, September 16" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Wednesday, September 16" />
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
  <h1>Wednesday, September 16</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("caratini_walkoff")}
  <p class="cap">{CLIPS["caratini_walkoff"]["cap"]}</p>
{clip_html("salas_two_homers")}
  <p class="cap">{CLIPS["salas_two_homers"]["cap"]}</p>
{clip_html("wheeler_shutout")}
  <p class="cap">{CLIPS["wheeler_shutout"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="caratini_walkoff" required> Caratini's walk-off in the 13th</label>
      <label><input type="radio" name="play" value="salas_two_homers"> Salas' two-homer game</label>
      <label><input type="radio" name="play" value="wheeler_shutout"> Wheeler's shutout</label>
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
{clip_html("walker_errant", video=False)}
  <p class="cap">{CLIPS["walker_errant"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Top of the third at Citi Field. Baltimore trailed 1–0 when Jeremiah Jackson and Samuel Basallo went back-to-back — three runs keyed a 7–1 win. Orioles 7, Mets 1.</p>
{clip_html("orioles_third")}
  <p class="cap">{CLIPS["orioles_third"]["cap"]}</p>

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
