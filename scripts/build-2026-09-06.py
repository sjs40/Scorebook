#!/usr/bin/env python3
"""Generate /workspace/2026-09-06/index.html and share race text files."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-06"
REF_HTML = ROOT / "2026-09-05" / "index.html"
ISSUE_DATE = "2026-09-06"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Burger goes deep twice in Texas' 8–6 win. "
    "Acuña's 1,000th hit ties it; Braves beat Philadelphia 5–4. "
    "Marlins score five in the fifth, beat Chicago 10–3. "
    "Chapman records his 400th save in Boston's 3–1 win."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/06"

CLIPS = {
    "burger": {
        "video": f"{MLB_CDN}/28b0f3bf-ad5ba72c-4c6f2df6-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "jake-burger-hammers-two-home-runs-against-rays",
        "cap": (
            "Jake Burger: two homers, three RBIs. "
            "Rangers 8, Rays 6 — four-run fourth and a two-run shot in the eighth."
        ),
    },
    "acuna": {
        "video": f"{MLB_CDN}/00b16cb8-397d4dd0-2e9ae710-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "acuna-jr-and-riley-lead-braves-in-comeback-win",
        "cap": (
            "Ronald Acuña Jr. tied it on his 1,000th career hit; Austin Riley's triple "
            "gave Atlanta the lead. Braves 5, Phillies 4."
        ),
    },
    "marlins": {
        "video": f"{MLB_CDN}/5da68847-a24469b3-1ae887aa-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "five-run-rally-pair-of-homers-lead-marlins-10-3-win",
        "cap": (
            "Miami scored five in the fifth — Sanoja and Hernández homered among the damage. "
            "Marlins 10, Cubs 3."
        ),
    },
    "pigeon": {
        "video": f"{MLB_CDN}/8003820d-52513dcc-0c6604a1-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "elly-de-la-cruz-saves-pigeon-on-field",
        "cap": (
            "Elly De La Cruz rescued a pigeon on the field at Great American Ball Park. "
            "That's baseball."
        ),
    },
    "marlins_fifth": {
        "video": f"{MLB_CDN}/79fdf914-d1b5d082-2c175ff6-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "marlins-take-the-lead-with-five-run-5th-inning",
        "cap": (
            "Five runs in the fifth — Sanoja's two-run homer and Hernández's solo shot "
            "among five Marlins hits in the frame."
        ),
    },
}

PITCHERS = [
    ("Bryan Woo", "SEA", 77, "8.0", 1, 0, 2, 9, "ATH"),
    ("Walbert Ureña", "LAA", 63, "8.0", 3, 1, 1, 4, "PIT"),
    ("Payton Tolle", "BOS", 62, "6.0", 4, 1, 0, 12, "BAL"),
    ("Cesar Perdomo", "SFG", 59, "6.0", 3, 0, 1, 4, "NYM"),
]

HITTERS = [
    ("Jake Burger", "TEX", 8, 4, 2, 2, 2, 3, 0),
    ("Elly De La Cruz", "CIN", 6, 4, 2, 2, 1, 4, 0),
    ("Ronald Acuña Jr.", "ATL", 6, 3, 2, 2, 1, 4, 0),
    ("Jake McCarthy", "COL", 6, 5, 3, 1, 1, 3, 0),
    ("Sam Antonacci", "CHW", 6, 4, 3, 3, 0, 2, 0),
    ("Mickey Moniak", "COL", 5, 4, 2, 1, 1, 4, 0),
    ("Eli White", "BOS", 5, 4, 2, 1, 1, 3, 0),
    ("Heriberto Hernández", "MIA", 5, 4, 2, 1, 1, 2, 1),
]

# away, home, away_score, home_score, away_innings, home_innings, away_h, away_e, home_h, home_e, note
GAMES = [
    ("MIL", "CIN", 8, 12, [0, 0, 0, 3, 3, 0, 0, 1, 1], [1, 2, 1, 2, 3, 0, 0, 3, 0], 7, 2, 14, 1, "W Brady Singer · L Antonio Senzatela · S Emilio Pagán"),
    ("ATL", "PHI", 5, 4, [0, 0, 0, 0, 0, 1, 0, 3, 1], [2, 0, 0, 0, 0, 0, 2, 0, 0], 10, 1, 7, 0, "W Dylan Lee · L Jhoan Duran · S Raisel Iglesias"),
    ("BOS", "BAL", 3, 1, [0, 3, 0, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0, 0, 0], 4, 0, 5, 1, "W Payton Tolle · L Kyle Bradish · S Aroldis Chapman"),
    ("LAA", "PIT", 0, 1, [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0, 0, 0], 5, 0, 3, 0, "W Paul Skenes · L Walbert Ureña · S Mason Montgomery"),
    ("DET", "CLE", 2, 3, [2, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 1, 0, 0, 0, 0, 1], 4, 0, 7, 0, "W Cade Smith · L Kyle Finnegan"),
    ("SFG", "NYM", 2, 4, [0, 0, 0, 2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 4, 0], 5, 0, 7, 1, "W Tobias Myers · L Carson Seymour · S Kodai Senga"),
    ("CHC", "MIA", 3, 10, [0, 0, 1, 1, 1, 0, 0, 0, 0], [0, 2, 0, 1, 5, 0, 2, 0, 0], 7, 0, 11, 0, "W Tyler Phillips · L Clay Holmes"),
    ("ARI", "HOU", 3, 2, [0, 1, 2, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0, 1, 0], 9, 0, 7, 0, "W Eduardo Rodriguez · L Peter Lambert · S Kevin Ginkel"),
    ("TOR", "KCR", 1, 6, [0, 0, 0, 0, 0, 1, 0, 0, 0], [3, 0, 2, 0, 1, 0, 0, 0, 0], 8, 1, 7, 0, "W Randy Dobnak · L Spencer Arrighetti"),
    ("TBR", "TEX", 6, 8, [0, 4, 0, 1, 0, 0, 1, 0, 0], [0, 1, 0, 4, 2, 0, 0, 1, 0], 10, 2, 12, 2, "W Trevor Williams · L Steven Matz · S Jakob Junis"),
    ("STL", "COL", 10, 8, [0, 1, 0, 0, 6, 0, 0, 3, 0], [2, 0, 3, 0, 0, 0, 0, 1, 2], 15, 1, 10, 1, "W Cooper Hjerpe · L Jimmy Herget · S George Soriano"),
    ("ATH", "SEA", 0, 2, [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 2, 0, 0, 0, 0, 0], 1, 0, 7, 0, "W Bryan Woo · L Gage Jump · S Andrés Muñoz"),
    ("NYY", "SDP", 3, 4, [0, 0, 0, 0, 0, 0, 0, 3, 0], [3, 0, 0, 0, 0, 0, 1, 0, 0], 7, 1, 6, 1, "W Michael King · L Gerrit Cole · S Mason Miller"),
    ("MIN", "CHW", 1, 10, [0, 0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 3, 1, 5, 0], 4, 0, 12, 0, "W Hagen Smith · L Bailey Ober"),
    ("WSN", "LAD", 5, 7, [0, 0, 0, 4, 0, 1, 0, 0, 0], [0, 0, 1, 0, 3, 0, 0, 3, 0], 9, 0, 10, 1, "W Bobby Miller · L Will Dion · S Edgardo Henriquez"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 85, 58, "--", "--", "L1", "6-4", "+47"),
        ("NYY", 81, 62, "4", "+9", "L1", "6-4", "+117"),
        ("BOS", 79, 65, "6.5", "+6", "W4", "6-4", "+86"),
        ("TOR", 72, 72, "13.5", "1", "L1", "7-3", "-38"),
        ("BAL", 69, 75, "16.5", "4", "L6", "4-6", "-29"),
    ],
    "AL Central": [
        ("CHW", 75, 68, "--", "--", "W1", "5-5", "+49"),
        ("CLE", 73, 71, "2.5", "--", "W1", "5-5", "-14"),
        ("MIN", 68, 75, "7", "4.5", "L1", "4-6", "-48"),
        ("DET", 65, 78, "10", "7.5", "L1", "3-7", "+50"),
        ("KCR", 64, 80, "11.5", "9", "W1", "5-5", "-88"),
    ],
    "AL West": [
        ("HOU", 73, 71, "--", "--", "L2", "6-4", "-38"),
        ("TEX", 71, 73, "2", "2", "W1", "5-5", "-44"),
        ("SEA", 67, 77, "6", "6", "W1", "3-7", "-71"),
        ("ATH", 57, 87, "16", "16", "L1", "4-6", "-188"),
        ("LAA", 54, 89, "18.5", "18.5", "L1", "2-8", "-77"),
    ],
    "AL Wild Card": [
        ("NYY", 81, 62, "+9", "L1", "6-4", "+117", False),
        ("BOS", 79, 65, "+6", "W4", "6-4", "+86", False),
        ("CLE", 73, 71, "--", "W1", "5-5", "-14", True),
        ("TOR", 72, 72, "1", "L1", "7-3", "-38", False),
        ("TEX", 71, 73, "2", "W1", "5-5", "-44", False),
        ("BAL", 69, 75, "4", "L6", "4-6", "-29", False),
    ],
    "NL East": [
        ("ATL", 85, 58, "--", "--", "W1", "7-3", "+120"),
        ("PHI", 80, 63, "5", "+5", "L1", "7-3", "+34"),
        ("MIA", 72, 72, "13.5", "4", "W1", "4-6", "+15"),
        ("WSN", 67, 78, "19", "9.5", "L4", "5-5", "+9"),
        ("NYM", 65, 78, "20", "10.5", "W1", "5-5", "-48"),
    ],
    "NL Central": [
        ("MIL", 88, 56, "--", "--", "L2", "5-5", "+168"),
        ("CHC", 81, 63, "7", "+5", "L1", "5-5", "+132"),
        ("STL", 72, 72, "16", "4", "W1", "6-4", "-9"),
        ("PIT", 71, 73, "17", "5", "W1", "6-4", "+26"),
        ("CIN", 69, 74, "18.5", "6.5", "W2", "7-3", "-105"),
    ],
    "NL West": [
        ("LAD", 86, 57, "--", "--", "W4", "6-4", "+152"),
        ("ARI", 76, 68, "10.5", "--", "W2", "5-5", "-1"),
        ("SDP", 75, 68, "11", "0.5", "W1", "4-6", "+8"),
        ("SFG", 59, 85, "27.5", "17", "L1", "4-6", "-75"),
        ("COL", 55, 88, "31", "20.5", "L1", "3-7", "-140"),
    ],
    "NL Wild Card": [
        ("CHC", 81, 63, "+5", "L1", "5-5", "+132", False),
        ("PHI", 80, 63, "+5", "L1", "7-3", "+34", False),
        ("ARI", 76, 68, "--", "W2", "5-5", "-1", True),
        ("SDP", 75, 68, "0.5", "W1", "4-6", "+8", False),
        ("MIA", 72, 72, "4", "W1", "4-6", "+15", False),
        ("STL", 72, 72, "4", "W1", "6-4", "-9", False),
    ],
}

UPCOMING = [
    ("ATL", "PHI", "Grant Holmes vs. Jesús Luzardo", "1:05 PM ET", "2026-09-07T17:05:00Z", ""),
    ("NYM", "MIA", "Jonah Tong vs. Eury Pérez", "1:10 PM ET", "2026-09-07T17:10:00Z", ""),
    ("LAA", "BOS", "Grayson Rodriguez vs. TBD", "1:35 PM ET", "2026-09-07T17:35:00Z", ""),
    ("CLE", "BAL", "Joey Cantillo vs. Trevor Rogers", "1:35 PM ET", "2026-09-07T17:35:00Z", ""),
    ("ARI", "KCR", "TBD vs. Noah Cameron", "2:10 PM ET", "2026-09-07T18:10:00Z", ""),
    ("CHC", "MIL", "Matthew Boyd vs. Robert Gasser", "2:10 PM ET", "2026-09-07T18:10:00Z", ""),
    ("MIN", "DET", "TBD vs. Troy Melton", "3:10 PM ET", "2026-09-07T19:10:00Z", ""),
    ("WSN", "SDP", "Jake Irvin vs. Nick Pivetta", "5:10 PM ET", "2026-09-07T21:10:00Z", ""),
    ("STL", "SFG", "Michael McGreevy vs. Logan Webb", "8:10 PM ET", "2026-09-08T00:10:00Z", ""),
    ("CIN", "LAD", "Chase Burns vs. TBD", "9:10 PM ET", "2026-09-08T01:10:00Z", ""),
    ("TOR", "ATH", "Dylan Cease vs. Jacob Lopez", "10:05 PM ET", "2026-09-08T02:05:00Z", ""),
]

OFF_TONIGHT = ["TBR", "NYY", "TEX", "HOU", "SEA", "COL", "PIT", "CHW"]

TEAM_SUMMARIES = {
    "CHC": "Your Cubs: Lost 3-10 at Miami. At Milwaukee today.",
    "MIA": "Your Marlins: Five-run fifth in a 10-3 win over Chicago. Host the Mets today.",
    "SFG": "Your Giants: Lost 2-4 at Citi Field. Off today.",
    "NYM": "Your Mets: Eight-run eighth in a 4-2 win over San Francisco. At Miami today.",
    "ATL": "Your Braves: Acuña tied it on his 1,000th hit; rallied to beat Philadelphia 5-4. At Philadelphia today.",
    "PHI": "Your Phillies: Lost 4-5 to Atlanta despite Nola's seven innings. Host Atlanta today.",
    "DET": "Your Tigers: Lost 2-3 in 10 at Cleveland. Host Minnesota today.",
    "CLE": "Your Guardians: Walk-off in the 10th over Detroit; Williams fanned 11. At Baltimore today.",
    "LAA": "Your Angels: Ureña went eight innings but lost 0-1 at Pittsburgh. At Boston today.",
    "PIT": "Your Pirates: Skenes beat the Angels 1-0. Off today.",
    "MIL": "Your Brewers: Lost 8-12 at Cincinnati. Host Chicago today.",
    "CIN": "Your Reds: De La Cruz drove in four in a 12-8 win over Milwaukee. At Dodger Stadium tonight.",
    "BOS": "Your Red Sox: Tolle struck out 12; Chapman earned his 400th save in a 3-1 win at Baltimore. Host the Angels today.",
    "BAL": "Your Orioles: Lost 1-3 to Boston. Host Cleveland today.",
    "TBR": "Your Rays: Lost 6-8 at Texas. Off today.",
    "TEX": "Your Rangers: Burger homered twice in an 8-6 win over Tampa Bay. Off today.",
    "MIN": "Your Twins: Lost 1-10 at Chicago. At Detroit today.",
    "CHW": "Your White Sox: Antonacci and Teel powered a 10-1 rout of Minnesota. Off today.",
    "TOR": "Your Blue Jays: Lost 1-6 at Kansas City. At Oakland tonight.",
    "KCR": "Your Royals: Dobnak went six in a 6-1 win over Toronto. Host Arizona today.",
    "ARI": "Your Diamondbacks: Rodriguez six strong in a 3-2 win at Houston. At Kansas City today.",
    "HOU": "Your Astros: Lost 2-3 to Arizona. Off today.",
    "NYY": "Your Yankees: Lost 3-4 at San Diego. Off today.",
    "SDP": "Your Padres: King beat Cole; Campusano homered in a 4-3 win over New York. Host Washington today.",
    "STL": "Your Cardinals: Six-run fifth at Coors; lost 10-8 despite 15 hits. At San Francisco tonight.",
    "COL": "Your Rockies: McCarthy and Moniak homered; lost 8-10 to St. Louis. Off today.",
    "WSN": "Your Nationals: Lost 5-7 at Dodger Stadium. At San Diego today.",
    "LAD": "Your Dodgers: Miller won; beat Washington 7-5. Host Cincinnati tonight.",
    "ATH": "Your Athletics: Woo held them to one hit over eight in a 2-0 win at Seattle. Host Toronto tonight.",
    "SEA": "Your Mariners: Shut out 0-2 by Oakland. Off today.",
}

RACE_AL_RECAP = (
    "Jake Burger homered twice in Texas' 8-6 win over Tampa Bay. "
    "Payton Tolle fanned 12 and Aroldis Chapman notched his 400th save in Boston's 3-1 win. "
    "Bryan Woo blanked Oakland on one hit over eight."
)
RACE_AL_SINCE = "Boston is 6-4 in its last ten."
RACE_NL_RECAP = (
    "Ronald Acuña Jr. tied it on his 1,000th hit and Atlanta rallied past Philadelphia 5-4. "
    "Elly De La Cruz drove in four in Cincinnati's 12-8 win. "
    "Miami scored five in the fifth to beat Chicago 10-3."
)
RACE_NL_SINCE = "Atlanta is 7-3 in its last ten."


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
    return m.group(1).replace("2026-09-05", ISSUE_DATE)


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
<title>Scorebook - Sunday, September 6</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Sunday, September 6" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Sunday, September 6" />
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
  <p class="kicker">Sunday night</p>
  <h1>Sunday, September 6</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("burger")}
  <p class="cap">{CLIPS["burger"]["cap"]}</p>
{clip_html("acuna")}
  <p class="cap">{CLIPS["acuna"]["cap"]}</p>
{clip_html("marlins")}
  <p class="cap">{CLIPS["marlins"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="burger" required> Burger's two homers</label>
      <label><input type="radio" name="play" value="acuna"> Acuña ties it on 1,000th hit</label>
      <label><input type="radio" name="play" value="marlins"> Marlins' five-run fifth</label>
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
{clip_html("pigeon")}
  <p class="cap">{CLIPS["pigeon"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Bottom of the fifth at loanDepot park. Miami sent nine batters to the plate and scored five runs on four hits — Javier Sanoja and Heriberto Hernández homered in the frame. The Marlins led 8-3 and won 10-3.</p>
{clip_html("marlins_fifth")}
  <p class="cap">{CLIPS["marlins_fifth"]["cap"]}</p>

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
      <p class="subn">Standings through Sunday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
{al_tables}
    </div>

    <div class="panel-nl" id="nl-panel">
      <div class="recap" data-share-card="race-nl.png" data-share-text-src="share/race-nl.txt">
        <p class="subn">Last night</p>
        <p>{RACE_NL_RECAP}</p>
        <p class="subn">Since August 13</p>
        <p>{RACE_NL_SINCE}</p>
      </div>
      <p class="subn">Standings through Sunday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
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
    share = OUT_DIR / "share"
    share.mkdir(parents=True, exist_ok=True)
    render_src = ROOT / "templates" / "default" / "share" / "render_share_cards.py"
    (share / "render_share_cards.py").write_text(
        render_src.read_text(encoding="utf-8"), encoding="utf-8"
    )
    print(f"Wrote {html_path}")
    print(f"Wrote {OUT_DIR / 'share' / 'race-al.txt'}")
    print(f"Wrote {OUT_DIR / 'share' / 'race-nl.txt'}")


if __name__ == "__main__":
    main()
