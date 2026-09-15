#!/usr/bin/env python3
"""Generate /workspace/2026-09-14/index.html and share race text files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-14"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-09-13" / "index.html"
ISSUE_DATE = "2026-09-14"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Dodgers clinched a playoff berth behind Tarik Skubal's seven scoreless innings. "
    "Corbin Carroll walked off Arizona's 8–7 win over Miami. "
    "Crow-Armstrong went 4-for-5 in the Cubs' 7–3 win over Atlanta. "
    "White Sox scored six in the sixth at Cleveland."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/14"

CLIPS = {
    "dodgers_clinch": {
        "video": f"{MLB_CDN}/bbe55632-7615670b-495a9e64-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "evan-phillips-in-play-out-s-to-tyler-stephenson",
        "cap": (
            "Tarik Skubal: seven scoreless innings and nine strikeouts. "
            "Dodgers 4, Reds 1 — Los Angeles clinched a playoff berth, tying the MLB record with 14 straight."
        ),
    },
    "carroll_walkoff": {
        "video": f"{MLB_CDN}/e0bdd45a-5f5d6e92-241a233d-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "corbin-carroll-homers-21-on-a-fly-ball-to-right-field-tommy-troy-scores",
        "cap": (
            "Corbin Carroll homered with one out in the ninth — Arizona trailed 7–5 entering the bottom of the ninth. "
            "Diamondbacks 8, Marlins 7 — Miami had scored seven and still lost."
        ),
    },
    "crow_armstrong": {
        "video": f"{MLB_CDN}/cbeec9ce-0b00c1a2-3b7a12a4-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "pete-crow-armstrong-s-four-hit-performance",
        "cap": (
            "Pete Crow-Armstrong: 4-for-5 with a homer, a double, and four RBIs. "
            "Cubs 7, Braves 3 — David Peterson struck out seven over six innings."
        ),
    },
    "marsee_sanoja": {
        "video": f"{MLB_CDN}/ee582a99-d81e65e2-d35abe0a-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "jakob-marsee-and-javier-sanoja-go-back-to-back",
        "cap": (
            "Jakob Marsee and Javier Sanoja went back-to-back — and the Marlins still lost on a walk-off. "
            "That's baseball — Miami scored seven and Arizona scored eight."
        ),
    },
    "cws_sixth": {
        "video": f"{MLB_CDN}/1acb727e-bbc095c2-e270dfe1-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "white-sox-plate-six-in-the-6th-vs-guardians",
        "cap": (
            "Six runs in the sixth — Vargas homered and the White Sox batted around. "
            "White Sox 7, Guardians 3."
        ),
    },
    "judge_hr": {
        "video": f"{MLB_CDN}/a23f0abb-35793c74-b0eb0474-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "a-j-minter-in-play-run-s-to-aaron-judge",
        "cap": (
            "Aaron Judge's three-run homer keyed a six-run eighth. "
            "Yankees 8, Twins 3 — New York had already clinched a postseason spot."
        ),
    },
}

PITCHERS = [
    ("Tarik Skubal", "LAD", 72, "7.0", 3, 0, 1, 9, "CIN"),
    ("Jonah Tong", "NYM", 64, "6.0", 4, 0, 1, 6, "BAL"),
    ("Quinn Mathews", "STL", 62, "6.2", 4, 1, 2, 8, "SFG"),
    ("Dean Kremer", "MIN", 60, "5.2", 2, 1, 1, 5, "NYY"),
]

HITTERS = [
    ("Pete Crow-Armstrong", "CHC", 8, 5, 4, 2, 1, 4, 1),
    ("Jakob Marsee", "MIA", 8, 4, 3, 2, 1, 1, 0),
    ("Javier Sanoja", "MIA", 7, 4, 2, 2, 1, 3, 1),
    ("Lars Nootbaar", "ARI", 6, 5, 3, 1, 1, 2, 0),
    ("Corbin Carroll", "ARI", 5, 5, 2, 1, 1, 3, 0),
    ("Miguel Vargas", "CWS", 5, 4, 2, 1, 1, 2, 1),
    ("José Caballero", "NYY", 5, 4, 2, 1, 1, 2, 1),
    ("Jordan Lawlar", "ARI", 5, 4, 2, 1, 1, 2, 1),
]

GAMES = [
    ("LAD", "CIN", 4, 1, [0, 1, 0, 2, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1], 3, 0, 4, 0, "W Tarik Skubal · L Nick Lodolo"),
    ("CWS", "CLE", 7, 3, [0, 0, 0, 0, 0, 6, 0, 0, 1], [0, 0, 0, 0, 0, 1, 0, 0, 2], 9, 2, 7, 1, "W Sean Burke · L Gavin Williams"),
    ("DET", "TOR", 6, 5, [0, 0, 0, 0, 0, 0, 4, 1, 1], [2, 0, 0, 0, 0, 0, 3, 0, 0], 9, 0, 8, 1, "W Tyler Kinley · L Louis Varland · S Kenley Jansen"),
    ("BAL", "NYM", 2, 1, [0, 1, 0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0], 9, 0, 6, 1, "W Yennier Cano · L Dedniel Núñez · S Rico Garcia"),
    ("ATL", "CHC", 3, 7, [0, 0, 0, 0, 0, 0, 3, 0, 0], [0, 3, 2, 0, 0, 2, 0, 0, 0], 8, 0, 10, 1, "W David Peterson · L Reynaldo López"),
    ("NYY", "MIN", 8, 3, [0, 0, 1, 0, 0, 0, 0, 6, 1], [0, 0, 0, 0, 0, 2, 0, 1, 0], 9, 3, 6, 0, "W Tim Hill · L Andrew Morris · S John Schreiber"),
    ("SFG", "STL", 1, 2, [0, 0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 2, 0, 0, 0, 0], 6, 0, 8, 0, "W Quinn Mathews · L Landen Roupp · S Riley O'Brien"),
    ("SDP", "COL", 8, 7, [1, 4, 1, 0, 0, 0, 1, 1, 0], [1, 0, 0, 0, 1, 3, 1, 1, 0], 13, 0, 14, 0, "W Casey Mize · L Tomoyuki Sugano · S Mason Miller"),
    ("SEA", "LAA", 4, 6, [0, 0, 0, 3, 0, 0, 1, 0, 0], [2, 0, 2, 0, 2, 0, 0, 0, 0], 8, 0, 9, 0, "W Reid Detmers · L Kade Anderson · S Ben Joyce"),
    ("MIA", "ARI", 7, 8, [0, 3, 0, 2, 0, 0, 2, 0, 0], [0, 0, 3, 0, 1, 0, 0, 2, 2], 12, 2, 11, 0, "W Juan Morillo · L Jack Ralston"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 90, 59, "--", "--", "W3", "7-3", "+69"),
        ("NYY", 87, 63, "3.5", "+11.5", "W2", "7-3", "+130"),
        ("BOS", 82, 68, "8.5", "+6.5", "W2", "7-3", "+88"),
        ("TOR", 75, 76, "16", "1", "L1", "5-5", "-32"),
        ("BAL", 73, 78, "18", "3", "W1", "4-6", "-34"),
    ],
    "AL Central": [
        ("CWS", 77, 73, "--", "--", "W1", "4-6", "+38"),
        ("CLE", 76, 75, "1.5", "--", "L1", "5-5", "-11"),
        ("DET", 71, 79, "6", "4.5", "W5", "7-3", "+71"),
        ("MIN", 70, 80, "7", "5.5", "L2", "3-7", "-67"),
        ("KCR", 66, 84, "11", "9.5", "L2", "4-6", "-94"),
    ],
    "AL West": [
        ("HOU", 75, 75, "--", "--", "L3", "4-6", "-53"),
        ("TEX", 74, 76, "1", "2", "W2", "5-5", "-44"),
        ("SEA", 70, 81, "5.5", "6", "L2", "4-6", "-60"),
        ("ATH", 61, 89, "14", "14.5", "W1", "7-3", "-203"),
        ("LAA", 57, 93, "18", "18.5", "W1", "4-6", "-74"),
    ],
    "AL Wild Card": [
        ("NYY", 87, 63, "+11.5", "W2", "7-3", "+130", False),
        ("BOS", 82, 68, "+6.5", "W2", "7-3", "+88", False),
        ("CLE", 76, 75, "--", "L1", "5-5", "-11", True),
        ("TOR", 75, 76, "1", "L1", "5-5", "-32", False),
        ("TEX", 74, 76, "2", "W2", "5-5", "-44", False),
        ("BAL", 73, 78, "3", "W1", "4-6", "-34", False),
    ],
    "NL East": [
        ("ATL", 88, 63, "--", "--", "L2", "4-6", "+112"),
        ("PHI", 83, 67, "4.5", "+1", "W1", "4-6", "+31"),
        ("MIA", 74, 77, "14", "8.5", "L1", "3-7", "+5"),
        ("WSN", 70, 81, "18", "12.5", "W3", "3-7", "+3"),
        ("NYM", 69, 81, "18.5", "13", "L2", "6-4", "-35"),
    ],
    "NL Central": [
        ("MIL", 93, 57, "--", "--", "L1", "6-4", "+195"),
        ("CHC", 84, 67, "9.5", "+1.5", "W1", "5-5", "+142"),
        ("PIT", 75, 75, "18", "7", "W1", "7-3", "+26"),
        ("STL", 75, 76, "18.5", "7.5", "W2", "5-5", "-6"),
        ("CIN", 70, 80, "23", "12", "L1", "3-7", "-148"),
    ],
    "NL West": [
        ("LAD", 91, 59, "--", "--", "W1", "8-2", "+173"),
        ("SDP", 82, 68, "9", "--", "W8", "9-1", "+23"),
        ("ARI", 80, 71, "11.5", "2.5", "W1", "6-4", "+3"),
        ("SFG", 62, 89, "29.5", "20.5", "L4", "4-6", "-78"),
        ("COL", 55, 95, "36", "27", "L8", "1-9", "-170"),
    ],
    "NL Wild Card": [
        ("CHC", 84, 67, "+1.5", "W1", "5-5", "+142", False),
        ("PHI", 83, 67, "+1", "W1", "4-6", "+31", False),
        ("SDP", 82, 68, "--", "W8", "9-1", "+23", True),
        ("ARI", 80, 71, "2.5", "W1", "6-4", "+3", False),
        ("PIT", 75, 75, "7", "W1", "7-3", "+26", False),
        ("MIA", 74, 77, "8.5", "L1", "3-7", "+5", False),
    ],
}

UPCOMING = [
    ("LAD", "CIN", "Yoshinobu Yamamoto vs. Rhett Lowder", "6:40 PM ET", "2026-09-15T22:40:00Z", ""),
    ("ATH", "TBR", "Jack Perkins vs. Griffin Jax", "6:40 PM ET", "2026-09-15T22:40:00Z", ""),
    ("CWS", "CLE", "Davis Martin vs. Foster Griffin", "6:40 PM ET", "2026-09-15T22:40:00Z", ""),
    ("MIL", "PIT", "Jacob Misiorowski vs. Lake Bachar", "6:40 PM ET", "2026-09-15T22:40:00Z", ""),
    ("PHI", "WSN", "Cristopher Sánchez vs. Jackson Kent", "6:45 PM ET", "2026-09-15T22:45:00Z", ""),
    ("DET", "TOR", "Drew Anderson vs. Braydon Fisher", "7:07 PM ET", "2026-09-15T23:07:00Z", ""),
    ("BAL", "NYM", "Shane Baz vs. Sean Manaea", "7:10 PM ET", "2026-09-15T23:10:00Z", ""),
    ("ATL", "CHC", "Martín Pérez vs. Kevin Gausman", "7:40 PM ET", "2026-09-15T23:40:00Z", ""),
    ("NYY", "MIN", "Max Fried vs. Bailey Ober", "7:40 PM ET", "2026-09-15T23:40:00Z", ""),
    ("SFG", "STL", "Blade Tidwell vs. Andre Pallante", "7:45 PM ET", "2026-09-15T23:45:00Z", ""),
    ("BOS", "TEX", "Patrick Sandoval vs. TBD", "8:05 PM ET", "2026-09-16T00:05:00Z", ""),
    ("KCR", "HOU", "Michael Wacha vs. Hunter Brown", "8:10 PM ET", "2026-09-16T00:10:00Z", ""),
    ("SDP", "COL", "Walker Buehler vs. Kyle Freeland", "8:40 PM ET", "2026-09-16T00:40:00Z", ""),
    ("SEA", "LAA", "Logan Gilbert vs. Ryan Johnson", "9:38 PM ET", "2026-09-16T01:38:00Z", ""),
    ("MIA", "ARI", "Janson Junk vs. Michael Soroka", "9:40 PM ET", "2026-09-16T01:40:00Z", ""),
]

OFF_TONIGHT: list[str] = []

TEAM_SUMMARIES = {
    "CHC": "Your Cubs: Crow-Armstrong went 4-for-5 in a 7–3 win over Atlanta. Host Atlanta tonight.",
    "MIA": "Your Marlins: Marsee and Sanoja homered but lost 7–8 on a walk-off at Arizona. At Arizona tonight.",
    "SFG": "Your Giants: Lost 1–2 at St. Louis; Roupp took the loss. At St. Louis tonight.",
    "NYM": "Your Mets: Lost 1–2 to Baltimore; Tong went six scoreless. Host Baltimore tonight.",
    "ATL": "Your Braves: Lost 3–7 at Chicago. At Chicago tonight.",
    "PHI": "Your Phillies: Off yesterday. At Washington tonight.",
    "DET": "Your Tigers: Won 6–5 at Toronto; scored four in the seventh. At Toronto tonight.",
    "CLE": "Your Guardians: Lost 3–7 to Chicago; Williams took the loss. Host White Sox tonight.",
    "LAA": "Your Angels: Won 6–4 over Seattle; Detmers fanned eight. Host Seattle tonight.",
    "PIT": "Your Pirates: Off yesterday. Host Milwaukee tonight.",
    "MIL": "Your Brewers: Off yesterday. At Pittsburgh tonight.",
    "CIN": "Your Reds: Lost 1–4 to Los Angeles; Lodolo took the loss. Host Dodgers tonight.",
    "BOS": "Your Red Sox: Off yesterday. At Texas tonight.",
    "BAL": "Your Orioles: Won 2–1 at New York; Henderson homered. At New York tonight.",
    "TBR": "Your Rays: Off yesterday. Host Athletics tonight.",
    "TEX": "Your Rangers: Off yesterday. Host Boston tonight.",
    "MIN": "Your Twins: Lost 3–8 to the Yankees; Judge homered. Host Yankees tonight.",
    "CWS": "Your White Sox: Won 7–3 at Cleveland; six-run sixth keyed the win. At Cleveland tonight.",
    "TOR": "Your Blue Jays: Lost 5–6 to Detroit. Host Detroit tonight.",
    "KCR": "Your Royals: Off yesterday. At Houston tonight.",
    "ARI": "Your Diamondbacks: Carroll's walk-off homer capped an 8–7 win over Miami. Host Miami tonight.",
    "HOU": "Your Astros: Off yesterday. Host Kansas City tonight.",
    "NYY": "Your Yankees: Won 8–3 at Minnesota; six-run eighth and Judge's three-run homer. At Minnesota tonight.",
    "SDP": "Your Padres: Tatis and Machado homered in an 8–7 win at Colorado. At Colorado tonight.",
    "STL": "Your Cardinals: Won 2–1 over San Francisco; Mathews fanned eight. Host San Francisco tonight.",
    "COL": "Your Rockies: Lost 7–8 to San Diego. Host San Diego tonight.",
    "WSN": "Your Nationals: Off yesterday. Host Philadelphia tonight.",
    "LAD": "Your Dodgers: Skubal shut out Cincinnati for seven and clinched a playoff berth. At Cincinnati tonight.",
    "ATH": "Your Athletics: Off yesterday. At Tampa Bay tonight.",
    "SEA": "Your Mariners: Lost 4–6 at Los Angeles. At Los Angeles tonight.",
}

RACE_AL_RECAP = (
    "Tarik Skubal shut out the Reds for seven as the Dodgers clinched a playoff berth. "
    "White Sox scored six in the sixth in a 7–3 win at Cleveland. "
    "Yankees scored six in the eighth and Judge homered in an 8–3 win at Minnesota."
)
RACE_AL_SINCE = "The Dodgers are 8–2 in their last ten."
RACE_NL_RECAP = (
    "Corbin Carroll's walk-off homer capped the Diamondbacks' 8–7 win over Miami. "
    "Crow-Armstrong went 4-for-5 as the Cubs beat Atlanta 7–3. "
    "Padres edged Colorado 8–7 behind Tatis and Machado homers."
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
    return m.group(1).replace("2026-09-13", ISSUE_DATE)


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
<title>Scorebook - Monday, September 14</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Monday, September 14" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Monday, September 14" />
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
  <h1>Monday, September 14</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("dodgers_clinch")}
  <p class="cap">{CLIPS["dodgers_clinch"]["cap"]}</p>
{clip_html("carroll_walkoff")}
  <p class="cap">{CLIPS["carroll_walkoff"]["cap"]}</p>
{clip_html("crow_armstrong")}
  <p class="cap">{CLIPS["crow_armstrong"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="dodgers_clinch" required> Dodgers clinch playoff berth</label>
      <label><input type="radio" name="play" value="carroll_walkoff"> Carroll's walk-off homer</label>
      <label><input type="radio" name="play" value="crow_armstrong"> Crow-Armstrong's four-hit night</label>
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
{clip_html("marsee_sanoja")}
  <p class="cap">{CLIPS["marsee_sanoja"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Bottom of the sixth at Progressive Field. Chicago trailed 1–0 when the White Sox scored six — Vargas homered and the rally keyed a 7–3 win. White Sox 7, Guardians 3.</p>
{clip_html("cws_sixth")}
  <p class="cap">{CLIPS["cws_sixth"]["cap"]}</p>

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
