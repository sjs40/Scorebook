#!/usr/bin/env python3
"""Generate /workspace/2026-09-15/index.html and share race text files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-15"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-09-14" / "index.html"
ISSUE_DATE = "2026-09-15"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Yamamoto blanked Cincinnati on one hit over seven in a 4–0 Dodgers win. "
    "Junior Caminero and Brayan Rocchio delivered walk-off knocks in Tampa Bay and Cleveland. "
    "Pete Alonso hit his 300th homer as Baltimore won in 11 at New York. "
    "Cole Carrigg went 4-for-5 with two homers as Colorado beat San Diego 9–3."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/15"

CLIPS = {
    "yamamoto": {
        "video": f"{MLB_CDN}/67daa063-5102d934-924b0274-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "yoshinobu-yamamoto-fans-seven-against-the-reds",
        "cap": (
            "Yoshinobu Yamamoto: seven scoreless innings, one hit, and seven strikeouts. "
            "Dodgers 4, Reds 0 — Los Angeles allowed one hit on Roberto Clemente Day."
        ),
    },
    "caminero_walkoff": {
        "video": f"{MLB_CDN}/28f510ef-de411289-77b9b952-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "junior-caminero-s-walk-off-home-run-41",
        "cap": (
            "Junior Caminero homered with one out in the ninth — Tampa Bay trailed 1–0 entering the bottom of the ninth. "
            "Rays 2, Athletics 1."
        ),
    },
    "alonso_300": {
        "video": f"{MLB_CDN}/7fa75afd-29dfa603-a1aed3a2-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "kodai-senga-in-play-run-s-to-pete-alonso",
        "cap": (
            "Pete Alonso's 300th career homer keyed Baltimore's rally in the 11th. "
            "Orioles 7, Mets 5 — Alonso returned to Citi Field and Coby Mayo added an inside-the-park homer."
        ),
    },
    "cws_rocchio": {
        "video": f"{MLB_CDN}/dd83e007-f966cab1-accafb5a-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "brayan-rocchio-delivers-walk-off-hit-vs-white-sox",
        "cap": (
            "Chicago scored four in the sixth and still lost on a Brayan Rocchio walk-off. "
            "That's baseball — Travis Bazzana homered twice and the White Sox led 6–5 in the ninth."
        ),
    },
    "giants_third": {
        "video": f"{MLB_CDN}/46839f93-7aa8ca47-401bd1ad-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "giants-round-up-four-in-the-3rd-inning",
        "cap": (
            "Four runs in the third — Eldridge homered and San Francisco batted around. "
            "Giants 10, Cardinals 3."
        ),
    },
}

PITCHERS = [
    ("Yoshinobu Yamamoto", "LAD", 76, "7.0", 1, 0, 2, 7, "CIN"),
    ("Jack Perkins", "ATH", 74, "6.2", 4, 0, 1, 8, "TBR"),
    ("Griffin Jax", "TBR", 70, "5.0", 2, 0, 0, 7, "ATH"),
    ("Max Fried", "NYY", 68, "7.0", 6, 1, 0, 6, "MIN"),
]

HITTERS = [
    ("Cole Carrigg", "COL", 11, 5, 4, 3, 2, 5, 0),
    ("Jeremy Peña", "HOU", 9, 4, 3, 2, 2, 2, 0),
    ("Travis Bazzana", "CLE", 8, 4, 2, 2, 2, 2, 0),
    ("Spencer Torkelson", "DET", 6, 4, 2, 2, 1, 3, 1),
    ("Bryce Eldridge", "SFG", 6, 4, 2, 2, 1, 3, 0),
    ("Cody Bellinger", "NYY", 6, 4, 3, 1, 1, 2, 0),
    ("Alex Freeland", "LAD", 6, 4, 2, 2, 1, 1, 0),
    ("Andrés Chaparro", "WSN", 6, 3, 2, 2, 1, 1, 0),
]

GAMES = [
    ("LAD", "CIN", 4, 0, [0, 1, 2, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], 8, 0, 3, 0, "W Yoshinobu Yamamoto · L Rhett Lowder"),
    ("ATH", "TBR", 1, 2, [0, 0, 0, 0, 0, 1, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 1], 4, 0, 6, 0, "W Bryan Baker · L Elvis Alvarado"),
    ("CWS", "CLE", 6, 7, [0, 0, 0, 1, 1, 4, 0, 0, 0], [3, 0, 0, 0, 1, 1, 0, 0, 2], 8, 1, 8, 0, "W Cade Smith · L Grant Taylor"),
    ("MIL", "PIT", 5, 1, [0, 1, 0, 0, 0, 4, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 0], 8, 0, 10, 0, "W Jacob Misiorowski · L Lake Bachar"),
    ("PHI", "WSN", 3, 6, [1, 0, 1, 0, 1, 0, 0, 0, 0], [2, 0, 0, 0, 1, 0, 3, 0, 0], 5, 0, 9, 0, "W Richard Lovelady · L Cristopher Sánchez · S Erik Tolman"),
    ("DET", "TOR", 10, 1, [0, 0, 0, 4, 1, 1, 0, 2, 2], [0, 0, 0, 0, 0, 0, 0, 1, 0], 10, 1, 6, 2, "W Drew Anderson · L Michael Lorenzen"),
    ("BAL", "NYM", 7, 5, [0, 2, 0, 0, 0, 0, 0, 0, 1, 1, 3], [1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1], 8, 1, 12, 0, "W Alex Hoppe · L Jonathan Pintaro · S Andrew Kittredge"),
    ("ATL", "CHC", 6, 3, [0, 0, 0, 0, 0, 2, 2, 0, 2], [0, 1, 0, 2, 0, 0, 0, 0, 0], 9, 1, 5, 0, "W Martín Pérez · L Jacob Webb · S Raisel Iglesias"),
    ("NYY", "MIN", 8, 1, [2, 0, 1, 0, 0, 4, 0, 0, 1], [0, 1, 0, 0, 0, 0, 0, 0, 0], 14, 0, 7, 1, "W Max Fried · L Bailey Ober"),
    ("SFG", "STL", 10, 3, [3, 0, 4, 1, 0, 0, 0, 1, 1], [1, 0, 1, 0, 0, 0, 0, 1, 0], 12, 0, 5, 2, "W Blade Tidwell · L Andre Pallante"),
    ("BOS", "TEX", 2, 4, [0, 0, 2, 0, 0, 0, 0, 0, 0], [0, 4, 0, 0, 0, 0, 0, 0, 0], 6, 0, 7, 0, "W Jacob deGrom · L Patrick Sandoval · S Jacob Latz"),
    ("KCR", "HOU", 2, 4, [0, 0, 0, 0, 1, 1, 0, 0, 0], [1, 0, 1, 0, 2, 0, 0, 0, 0], 4, 0, 4, 0, "W Hunter Brown · L Michael Wacha · S Josh Hader"),
    ("SDP", "COL", 3, 9, [1, 1, 0, 0, 1, 0, 0, 0, 0], [0, 0, 2, 0, 0, 5, 2, 0, 0], 11, 0, 16, 0, "W Ryan Feltner · L Wandy Peralta"),
    ("SEA", "LAA", 1, 2, [0, 0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 1, 1, 0, 0, 0], 7, 0, 7, 0, "W Ryan Johnson · L Logan Gilbert · S Ryan Watson"),
    ("MIA", "ARI", 4, 2, [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 3], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 5, 1, 9, 1, "W Josh Ekness · L Taylor Clarke"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 91, 59, "--", "--", "W4", "8-2", "+70"),
        ("NYY", 88, 63, "3.5", "+11.5", "W3", "8-2", "+137"),
        ("BOS", 82, 69, "9.5", "+5.5", "L1", "6-4", "+86"),
        ("TOR", 75, 77, "17", "2", "L2", "4-6", "-41"),
        ("BAL", 74, 78, "18", "3", "W2", "5-5", "-32"),
    ],
    "AL Central": [
        ("CWS", 77, 74, "--", "--", "L1", "3-7", "+37"),
        ("CLE", 77, 75, "0.5", "--", "W1", "5-5", "-10"),
        ("DET", 72, 79, "5", "4.5", "W6", "8-2", "+80"),
        ("MIN", 70, 81, "7", "6.5", "L3", "3-7", "-74"),
        ("KCR", 66, 85, "11", "10.5", "L3", "3-7", "-96"),
    ],
    "AL West": [
        ("HOU", 76, 75, "--", "--", "W1", "4-6", "-51"),
        ("TEX", 75, 76, "1", "1.5", "W3", "5-5", "-42"),
        ("SEA", 70, 82, "6.5", "7", "L3", "4-6", "-61"),
        ("ATH", 61, 90, "15", "15.5", "L1", "6-4", "-204"),
        ("LAA", 58, 93, "18", "18.5", "W2", "5-5", "-73"),
    ],
    "AL Wild Card": [
        ("NYY", 88, 63, "+11.5", "W3", "8-2", "+137", False),
        ("BOS", 82, 69, "+5.5", "L1", "6-4", "+86", False),
        ("CLE", 77, 75, "--", "W1", "5-5", "-10", True),
        ("TEX", 75, 76, "1.5", "W3", "5-5", "-42", False),
        ("TOR", 75, 77, "2", "L2", "4-6", "-41", False),
        ("BAL", 74, 78, "3", "W2", "5-5", "-32", False),
    ],
    "NL East": [
        ("ATL", 89, 63, "--", "--", "W1", "5-5", "+115"),
        ("PHI", 83, 68, "5.5", "+1", "L1", "4-6", "+28"),
        ("MIA", 75, 77, "14", "7.5", "W1", "4-6", "+7"),
        ("WSN", 71, 81, "18", "11.5", "W4", "4-6", "+6"),
        ("NYM", 69, 82, "19.5", "13", "L3", "5-5", "-37"),
    ],
    "NL Central": [
        ("MIL", 94, 57, "--", "--", "W1", "7-3", "+199"),
        ("CHC", 84, 68, "10.5", "+1.5", "L1", "4-6", "+139"),
        ("PIT", 75, 76, "19", "7", "L1", "6-4", "+22"),
        ("STL", 75, 77, "19.5", "7.5", "L1", "4-6", "-13"),
        ("CIN", 70, 81, "24", "12", "L2", "3-7", "-152"),
    ],
    "NL West": [
        ("LAD", 92, 59, "--", "--", "W2", "8-2", "+177"),
        ("SDP", 82, 69, "10", "--", "L1", "8-2", "+17"),
        ("ARI", 80, 72, "12.5", "2.5", "L1", "6-4", "+1"),
        ("SFG", 63, 89, "29.5", "19.5", "W1", "5-5", "-71"),
        ("COL", 56, 95, "36", "26", "W1", "2-8", "-164"),
    ],
    "NL Wild Card": [
        ("CHC", 84, 68, "+1.5", "L1", "4-6", "+139", False),
        ("PHI", 83, 68, "+1", "L1", "4-6", "+28", False),
        ("SDP", 82, 69, "--", "L1", "8-2", "+17", True),
        ("ARI", 80, 72, "2.5", "L1", "6-4", "+1", False),
        ("PIT", 75, 76, "7", "L1", "6-4", "+22", False),
        ("MIA", 75, 77, "7.5", "W1", "4-6", "+7", False),
    ],
}

UPCOMING = [
    ("CWS", "CLE", "Anthony Kay vs. Parker Messick", "1:10 PM ET", "2026-09-16T17:10:00Z", ""),
    ("SFG", "STL", "Anthony Molina vs. Matthew Liberatore", "1:15 PM ET", "2026-09-16T17:15:00Z", ""),
    ("NYY", "MIN", "Carlos Rodón vs. Zebby Matthews", "1:40 PM ET", "2026-09-16T17:40:00Z", ""),
    ("DET", "TOR", "Keider Montero vs. Max Scherzer", "3:07 PM ET", "2026-09-16T19:07:00Z", ""),
    ("LAD", "CIN", "Blake Snell vs. Andrew Abbott", "6:40 PM ET", "2026-09-16T22:40:00Z", ""),
    ("ATH", "TBR", "Brady Basso vs. Nick Martinez", "6:40 PM ET", "2026-09-16T22:40:00Z", ""),
    ("MIL", "PIT", "Logan Henderson vs. Jared Jones", "6:40 PM ET", "2026-09-16T22:40:00Z", ""),
    ("PHI", "WSN", "Zack Wheeler vs. Jared Simpson", "6:45 PM ET", "2026-09-16T22:45:00Z", ""),
    ("BAL", "NYM", "Chris Bassitt vs. Robert Stock", "7:10 PM ET", "2026-09-16T23:10:00Z", ""),
    ("ATL", "CHC", "JR Ritchie vs. Shota Imanaga", "7:40 PM ET", "2026-09-16T23:40:00Z", ""),
    ("BOS", "TEX", "Jake Bennett vs. MacKenzie Gore", "8:05 PM ET", "2026-09-17T00:05:00Z", ""),
    ("KCR", "HOU", "Daniel Lynch IV vs. Cristian Javier", "8:10 PM ET", "2026-09-17T00:10:00Z", ""),
    ("SDP", "COL", "Robbie Ray vs. Mason Adams", "8:40 PM ET", "2026-09-17T00:40:00Z", ""),
    ("SEA", "LAA", "George Kirby vs. Yusei Kikuchi", "9:38 PM ET", "2026-09-17T01:38:00Z", ""),
    ("MIA", "ARI", "Ryan Gusto vs. Merrill Kelly", "9:40 PM ET", "2026-09-17T01:40:00Z", ""),
]

OFF_TONIGHT: list[str] = []

TEAM_SUMMARIES = {
    "CHC": "Your Cubs: Lost 3–6 to Atlanta at home. Host Atlanta tonight.",
    "MIA": "Your Marlins: Won 4–2 in 11 at Arizona; Ruiz's three-run double keyed the 11th. At Arizona tonight.",
    "SFG": "Your Giants: Won 10–3 at St. Louis; Eldridge and Hill homered. At St. Louis this afternoon.",
    "NYM": "Your Mets: Lost 5–7 to Baltimore in 11; Alonso hit his 300th homer. Host Baltimore tonight.",
    "ATL": "Your Braves: Won 6–3 at Chicago; Pérez earned the win. At Chicago tonight.",
    "PHI": "Your Phillies: Lost 3–6 at Washington; Lile's go-ahead homer decided it. At Washington tonight.",
    "DET": "Your Tigers: Won 10–1 at Toronto; Torkelson's three-run homer keyed a four-run fourth. At Toronto tonight.",
    "CLE": "Your Guardians: Rocchio's walk-off beat Chicago 7–6; Bazzana homered twice. Host White Sox this afternoon.",
    "LAA": "Your Angels: Won 2–1 over Seattle; Johnson fanned seven over six. Host Seattle tonight.",
    "PIT": "Your Pirates: Lost 1–5 to Milwaukee. Host Milwaukee tonight.",
    "MIL": "Your Brewers: Won 5–1 at Pittsburgh; Misiorowski fanned seven over five. At Pittsburgh tonight.",
    "CIN": "Your Reds: Lost 0–4 to Los Angeles; Yamamoto shut them out for seven. Host Dodgers tonight.",
    "BOS": "Your Red Sox: Lost 2–4 at Texas; deGrom struck out eight. At Texas tonight.",
    "BAL": "Your Orioles: Won 7–5 in 11 at New York; Alonso's 300th and Mayo's inside-the-park homer. At New York tonight.",
    "TBR": "Your Rays: Caminero's walk-off homer beat Oakland 2–1. Host Athletics tonight.",
    "TEX": "Your Rangers: Won 4–2 over Boston; deGrom struck out eight. Host Boston tonight.",
    "MIN": "Your Twins: Lost 1–8 to the Yankees; Fried went seven innings of one-run ball. Host Yankees this afternoon.",
    "CWS": "Your White Sox: Lost 6–7 on a Rocchio walk-off at Cleveland despite a four-run sixth. At Cleveland this afternoon.",
    "TOR": "Your Blue Jays: Lost 1–10 to Detroit. Host Detroit tonight.",
    "KCR": "Your Royals: Lost 2–4 at Houston. At Houston tonight.",
    "ARI": "Your Diamondbacks: Lost 2–4 in 11 to Miami. Host Miami tonight.",
    "HOU": "Your Astros: Won 4–2 over Kansas City; Brown struck out 10. Host Kansas City tonight.",
    "NYY": "Your Yankees: Won 8–1 at Minnesota; Fried and Bellinger keyed the rout. At Minnesota this afternoon.",
    "SDP": "Your Padres: Lost 3–9 at Colorado; Carrigg homered twice. At Colorado tonight.",
    "STL": "Your Cardinals: Lost 3–10 to San Francisco. Host San Francisco this afternoon.",
    "COL": "Your Rockies: Carrigg went 4-for-5 with two homers in a 9–3 win over San Diego. Host San Diego tonight.",
    "WSN": "Your Nationals: Won 6–3 over Philadelphia; Lile's go-ahead homer in the seventh. Host Philadelphia tonight.",
    "LAD": "Your Dodgers: Yamamoto shut out Cincinnati for seven in a 4–0 win. At Cincinnati tonight.",
    "ATH": "Your Athletics: Lost 1–2 at Tampa Bay; Perkins fanned eight over 6 2/3. At Tampa Bay tonight.",
    "SEA": "Your Mariners: Lost 1–2 at Los Angeles. At Los Angeles tonight.",
}

RACE_AL_RECAP = (
    "Yoshinobu Yamamoto blanked Cincinnati on one hit over seven. "
    "Brayan Rocchio's walk-off beat Chicago 7–6; Travis Bazzana homered twice. "
    "Pete Alonso's 300th homer keyed Baltimore's 7–5 win in 11 at New York."
)
RACE_AL_SINCE = "The Dodgers are 8–2 in their last ten."
RACE_NL_RECAP = (
    "Cole Carrigg went 4-for-5 with two homers as Colorado beat San Diego 9–3. "
    "San Francisco scored 10 at St. Louis behind Eldridge and Hill homers. "
    "Daylen Lile's go-ahead homer lifted Washington past Philadelphia 6–3."
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
    return m.group(1).replace("2026-09-14", ISSUE_DATE)


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
<title>Scorebook - Monday, September 15</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Monday, September 15" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Monday, September 15" />
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
  <p class="kicker">Monday night</p>
  <h1>Monday, September 15</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("yamamoto")}
  <p class="cap">{CLIPS["yamamoto"]["cap"]}</p>
{clip_html("caminero_walkoff")}
  <p class="cap">{CLIPS["caminero_walkoff"]["cap"]}</p>
{clip_html("alonso_300")}
  <p class="cap">{CLIPS["alonso_300"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="yamamoto" required> Yamamoto's shutout</label>
      <label><input type="radio" name="play" value="caminero_walkoff"> Caminero's walk-off homer</label>
      <label><input type="radio" name="play" value="alonso_300"> Alonso's 300th homer</label>
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
{clip_html("cws_rocchio")}
  <p class="cap">{CLIPS["cws_rocchio"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Top of the third at Busch Stadium. San Francisco led 3–1 when the Giants scored four — Eldridge homered and the rally keyed a 10–3 win. Giants 10, Cardinals 3.</p>
{clip_html("giants_third")}
  <p class="cap">{CLIPS["giants_third"]["cap"]}</p>

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
      <p class="subn">Standings through Monday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
{al_tables}
    </div>

    <div class="panel-nl" id="nl-panel">
      <div class="recap" data-share-card="race-nl.png" data-share-text-src="share/race-nl.txt">
        <p class="subn">Last night</p>
        <p>{RACE_NL_RECAP}</p>
        <p class="subn">Since August 13</p>
        <p>{RACE_NL_SINCE}</p>
      </div>
      <p class="subn">Standings through Monday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
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
