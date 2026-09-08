#!/usr/bin/env python3
"""Generate /workspace/2026-09-07/index.html and share race text files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-07"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-09-06" / "index.html"
ISSUE_DATE = "2026-09-07"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Luzardo shuts out Atlanta on two hits with 12 strikeouts. "
    "Mayo goes deep twice as Baltimore beats Cleveland 6–4. "
    "D-backs score five in the 10th at Kansas City. "
    "Mets beat Miami 9–4 behind Tong."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/07"

CLIPS = {
    "luzardo": {
        "video": f"{MLB_CDN}/9a125cbc-0fc54c32-1bebc03d-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "jesus-luzardo-gets-the-complete-game-shutout-in-win",
        "cap": (
            "Jesús Luzardo: complete-game shutout, two hits, 12 strikeouts. "
            "Phillies 1, Braves 0 — Schwarber's eighth-inning homer was the difference."
        ),
    },
    "mayo": {
        "video": f"{MLB_CDN}/2fdb26eb-26abc801-90dfd879-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "coby-mayo-mashes-two-home-runs-vs-guardians",
        "cap": (
            "Coby Mayo homered twice and drove in three. "
            "Orioles 6, Guardians 4 — Trevor Rogers went 7.1 scoreless innings."
        ),
    },
    "dbacks": {
        "video": f"{MLB_CDN}/fc2d9cc6-bb1e6501-ad2a3869-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "d-backs-rally-to-score-five-runs-in-the-10th",
        "cap": (
            "Arizona scored five in the top of the 10th — Perdomo's two-run single "
            "and Nootbaar's sac fly among the damage. D-backs 5, Royals 4."
        ),
    },
    "elly": {
        "video": f"{MLB_CDN}/702677ac-05339047-e1e4a0e7-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "brandon-williamson-in-play-out-s-to-kyle-tucker-ws72hj",
        "cap": (
            "Elly De La Cruz made a slick play at short in the sixth at Dodger Stadium. "
            "That's baseball."
        ),
    },
    "dbacks_tenth": {
        "video": f"{MLB_CDN}/fc2d9cc6-bb1e6501-ad2a3869-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "d-backs-rally-to-score-five-runs-in-the-10th",
        "cap": (
            "Five runs in the top of the 10th — Perdomo's two-run single "
            "and Nootbaar's sac fly among four D-backs hits in the frame."
        ),
    },
}

PITCHERS = [
    ("Jesús Luzardo", "PHI", 92, "9.0", 2, 0, 1, 12, "ATL"),
    ("Emmet Sheehan", "LAD", 70, "5.2", 3, 1, 1, 10, "CIN"),
    ("Noah Cameron", "KCR", 68, "6.0", 3, 0, 2, 7, "ARI"),
    ("Grant Holmes", "ATL", 66, "6.0", 3, 0, 2, 6, "PHI"),
]

HITTERS = [
    ("Coby Mayo", "BAL", 6, 5, 2, 2, 2, 3, 0),
    ("Riley Greene", "DET", 5, 4, 3, 1, 1, 2, 0),
    ("Moisés Ballesteros", "LAA", 5, 4, 3, 2, 1, 1, 0),
    ("Teoscar Hernández", "LAD", 4, 3, 2, 1, 1, 3, 1),
    ("Dylan Crews", "WSN", 4, 4, 2, 1, 1, 2, 0),
    ("Andrés Giménez", "TOR", 4, 4, 2, 2, 1, 2, 0),
    ("Pete Crow-Armstrong", "CHC", 4, 4, 2, 1, 1, 1, 2),
    ("Elly De La Cruz", "CIN", 4, 4, 2, 1, 1, 1, 1),
]

# away, home, away_score, home_score, away_innings, home_innings, away_h, away_e, home_h, home_e, note
GAMES = [
    ("ATL", "PHI", 0, 1, [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 0], 2, 0, 4, 0, "W Jesús Luzardo · L Didier Fuentes"),
    ("NYM", "MIA", 9, 4, [2, 1, 1, 3, 0, 2, 0, 0, 0], [0, 4, 0, 0, 0, 0, 0, 0, 0], 16, 0, 6, 2, "W Jonah Tong · L Eury Pérez"),
    ("LAA", "BOS", 2, 5, [0, 0, 0, 0, 0, 1, 0, 1, 0], [0, 4, 1, 0, 0, 0, 0, 0, 0], 6, 0, 9, 0, "W Brayan Bello · L Grayson Rodriguez · S Garrett Whitlock"),
    ("CLE", "BAL", 4, 6, [0, 0, 0, 0, 0, 1, 0, 0, 3], [0, 1, 3, 0, 0, 2, 0, 0, 0], 9, 0, 9, 0, "W Trevor Rogers · L Joey Cantillo · S Josh Walker"),
    ("ARI", "KCR", 5, 4, [0, 0, 0, 0, 0, 0, 0, 0, 0, 5], [0, 0, 0, 0, 0, 0, 0, 0, 0, 4], 10, 1, 8, 1, "W Justin Martinez · L Craig Kimbrel · S Dennis Santana"),
    ("CHC", "MIL", 3, 4, [0, 0, 0, 0, 1, 0, 1, 0, 1], [0, 0, 0, 0, 1, 0, 0, 3, 0], 6, 0, 6, 0, "W Abner Uribe · L Matthew Boyd · S Trevor Megill"),
    ("MIN", "DET", 4, 5, [1, 0, 0, 1, 0, 2, 0, 0, 0], [1, 2, 0, 0, 2, 0, 0, 0, 0], 8, 1, 8, 0, "W Troy Melton · L Joe Ryan · S Kenley Jansen"),
    ("WSN", "SDP", 2, 3, [0, 0, 0, 0, 0, 2, 0, 0, 0], [1, 0, 2, 0, 0, 0, 0, 0, 0], 5, 0, 9, 0, "W Nick Pivetta · L Jake Irvin · S Mason Miller"),
    ("STL", "SFG", 4, 5, [0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0], [1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1], 9, 1, 10, 0, "W Jason Foley · L George Soriano"),
    ("CIN", "LAD", 3, 6, [1, 0, 0, 0, 0, 0, 1, 1, 0], [0, 0, 0, 0, 2, 3, 0, 1, 0], 7, 2, 3, 0, "W Emmet Sheehan · L Brandon Williamson · S Evan Phillips"),
    ("TOR", "ATH", 5, 6, [0, 1, 0, 0, 0, 0, 3, 0, 1], [2, 0, 2, 0, 1, 0, 0, 0, 1], 9, 3, 6, 0, "W Hogan Harris · L Louis Varland"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 85, 58, "--", "--", "L1", "6-4", "+47"),
        ("NYY", 81, 62, "4", "+9", "L1", "6-4", "+117"),
        ("BOS", 80, 65, "6", "+7", "W5", "6-4", "+89"),
        ("TOR", 72, 73, "14", "1", "L2", "7-3", "-39"),
        ("BAL", 70, 75, "16", "3", "W1", "4-6", "-27"),
    ],
    "AL Central": [
        ("CHW", 75, 68, "--", "--", "W1", "5-5", "+49"),
        ("CLE", 73, 72, "3", "--", "L1", "5-5", "-16"),
        ("MIN", 68, 76, "7.5", "4.5", "L2", "4-6", "-49"),
        ("DET", 66, 78, "9.5", "6.5", "W1", "4-6", "+51"),
        ("KCR", 64, 81, "12", "9", "L1", "4-6", "-89"),
    ],
    "AL West": [
        ("HOU", 73, 71, "--", "--", "L2", "6-4", "-38"),
        ("TEX", 71, 73, "2", "1.5", "W1", "5-5", "-44"),
        ("SEA", 67, 77, "6", "5.5", "W1", "3-7", "-71"),
        ("ATH", 58, 87, "15.5", "15", "W1", "5-5", "-187"),
        ("LAA", 54, 90, "19", "18.5", "L2", "2-8", "-80"),
    ],
    "AL Wild Card": [
        ("NYY", 81, 62, "+9", "L1", "6-4", "+117", False),
        ("BOS", 80, 65, "+7", "W5", "6-4", "+89", False),
        ("CLE", 73, 72, "--", "L1", "5-5", "-16", True),
        ("TOR", 72, 73, "1", "L2", "7-3", "-39", False),
        ("TEX", 71, 73, "1.5", "W1", "5-5", "-44", False),
        ("BAL", 70, 75, "3", "W1", "4-6", "-27", False),
    ],
    "NL East": [
        ("ATL", 85, 59, "--", "--", "L1", "6-4", "+119"),
        ("PHI", 81, 63, "4", "+4.5", "W1", "7-3", "+35"),
        ("MIA", 72, 73, "13.5", "5", "L1", "4-6", "+10"),
        ("WSN", 67, 79, "19", "10.5", "L5", "4-6", "+8"),
        ("NYM", 66, 78, "19", "10.5", "W2", "6-4", "-43"),
    ],
    "NL Central": [
        ("MIL", 89, 56, "--", "--", "W1", "5-5", "+169"),
        ("CHC", 81, 64, "8", "+4", "L2", "5-5", "+131"),
        ("STL", 72, 73, "17", "5", "L1", "5-5", "-10"),
        ("PIT", 71, 73, "17.5", "5.5", "W1", "6-4", "+26"),
        ("CIN", 69, 75, "19.5", "7.5", "L1", "6-4", "-108"),
    ],
    "NL West": [
        ("LAD", 87, 57, "--", "--", "W5", "7-3", "+155"),
        ("ARI", 77, 68, "10.5", "--", "W3", "6-4", "0"),
        ("SDP", 76, 68, "11", "0.5", "W2", "4-6", "+9"),
        ("SFG", 60, 85, "27.5", "17", "W1", "5-5", "-74"),
        ("COL", 55, 88, "31.5", "21", "L1", "3-7", "-140"),
    ],
    "NL Wild Card": [
        ("PHI", 81, 63, "+4.5", "W1", "7-3", "+35", False),
        ("CHC", 81, 64, "+4", "L2", "5-5", "+131", False),
        ("ARI", 77, 68, "--", "W3", "6-4", "0", True),
        ("SDP", 76, 68, "0.5", "W2", "4-6", "+9", False),
        ("MIA", 72, 73, "5", "L1", "4-6", "+10", False),
        ("STL", 72, 73, "5", "L1", "5-5", "-10", False),
    ],
}

UPCOMING = [
    ("CLE", "BAL", "Tanner Bibee vs. Brandon Young", "6:35 PM ET", "2026-09-08T22:35:00Z", ""),
    ("MIN", "DET", "Dean Kremer vs. Drew Anderson", "6:40 PM ET", "2026-09-08T22:40:00Z", ""),
    ("HOU", "PHI", "Hayden Wesneski vs. Andrew Painter", "6:40 PM ET", "2026-09-08T22:40:00Z", ""),
    ("NYM", "MIA", "Sean Manaea vs. Sandy Alcantara", "6:40 PM ET", "2026-09-08T22:40:00Z", ""),
    ("LAA", "BOS", "Reid Detmers vs. Patrick Sandoval", "6:45 PM ET", "2026-09-08T22:45:00Z", ""),
    ("COL", "NYY", "Gabriel Hughes vs. Cam Schlittler", "7:05 PM ET", "2026-09-08T23:05:00Z", ""),
    ("TBR", "ATL", "Freddy Peralta vs. AJ Smith-Shawver", "7:15 PM ET", "2026-09-08T23:15:00Z", ""),
    ("ARI", "KCR", "Corbin Burnes vs. Michael Wacha", "7:40 PM ET", "2026-09-08T23:40:00Z", ""),
    ("PIT", "CHW", "Bubba Chandler vs. Sean Burke", "7:40 PM ET", "2026-09-08T23:40:00Z", ""),
    ("CHC", "MIL", "David Peterson vs. Jacob Misiorowski", "7:40 PM ET", "2026-09-08T23:40:00Z", ""),
    ("WSN", "SDP", "Riley Cornelio vs. Casey Mize", "9:40 PM ET", "2026-09-09T01:40:00Z", ""),
    ("TEX", "SEA", "TBD vs. TBD", "9:40 PM ET", "2026-09-09T01:40:00Z", ""),
    ("TOR", "ATH", "José Soriano vs. Jack Perkins", "9:40 PM ET", "2026-09-09T01:40:00Z", ""),
    ("STL", "SFG", "Quinn Mathews vs. Landen Roupp", "9:45 PM ET", "2026-09-09T01:45:00Z", ""),
    ("CIN", "LAD", "Nick Lodolo vs. Tarik Skubal", "10:10 PM ET", "2026-09-09T02:10:00Z", ""),
]

OFF_TONIGHT: list[str] = []

TEAM_SUMMARIES = {
    "CHC": "Your Cubs: Lost 3-4 at Milwaukee; Boyd went seven. At Milwaukee tonight.",
    "MIA": "Your Marlins: Lost 9-4 to the Mets. Host New York tonight.",
    "SFG": "Your Giants: Walk-off in the 11th over St. Louis; Whitcomb singled home the winner. Host the Cardinals tonight.",
    "NYM": "Your Mets: Tong struck out seven in a 9-4 win at Miami. At Miami tonight.",
    "ATL": "Your Braves: Shut out 0-1 by Luzardo and Philadelphia. Host Tampa Bay tonight.",
    "PHI": "Your Phillies: Luzardo's shutout and Schwarber's homer beat Atlanta 1-0. Host Houston tonight.",
    "DET": "Your Tigers: Greene homered; beat Minnesota 5-4. Host the Twins tonight.",
    "CLE": "Your Guardians: Lost 4-6 at Baltimore despite a three-run ninth. At Baltimore tonight.",
    "LAA": "Your Angels: Ballesteros homered but lost 2-5 at Boston. At Boston tonight.",
    "PIT": "Your Pirates: Off Monday. At Chicago tonight.",
    "MIL": "Your Brewers: Chourio's three-run eighth beat Chicago 4-3. Host the Cubs tonight.",
    "CIN": "Your Reds: Lost 3-6 at Dodger Stadium. At Los Angeles tonight.",
    "BOS": "Your Red Sox: Rutschman and Duran homered in a 5-2 win over the Angels. Host the Angels tonight.",
    "BAL": "Your Orioles: Mayo homered twice; Rogers went 7.1 in a 6-4 win over Cleveland. Host the Guardians tonight.",
    "TBR": "Your Rays: Off Monday. At Atlanta tonight.",
    "TEX": "Your Rangers: Off Monday. At Seattle tonight.",
    "MIN": "Your Twins: Lost 4-5 at Detroit. At Detroit tonight.",
    "CHW": "Your White Sox: Off Monday. Host Pittsburgh tonight.",
    "TOR": "Your Blue Jays: Lost 5-6 at Oakland on a walk-off. At Oakland tonight.",
    "KCR": "Your Royals: Lost 4-5 in 10 to Arizona. Host the D-backs tonight.",
    "ARI": "Your Diamondbacks: Five runs in the 10th beat Kansas City 5-4. At Kansas City tonight.",
    "HOU": "Your Astros: Off Monday. At Philadelphia tonight.",
    "NYY": "Your Yankees: Off Monday. Host Colorado tonight.",
    "SDP": "Your Padres: Pivetta won in his return; beat Washington 3-2. Host the Nationals tonight.",
    "STL": "Your Cardinals: Lost 4-5 in 11 at San Francisco. At San Francisco tonight.",
    "COL": "Your Rockies: Off Monday. At New York tonight.",
    "WSN": "Your Nationals: Crews homered but lost 2-3 at San Diego. At San Diego tonight.",
    "LAD": "Your Dodgers: Sheehan fanned 10; Hernández's three-run homer in a 6-3 win over Cincinnati. Host the Reds tonight.",
    "ATH": "Your Athletics: McNeil's walk-off beat Toronto 6-5. Host the Blue Jays tonight.",
    "SEA": "Your Mariners: Off Monday. Host Texas tonight.",
}

RACE_AL_RECAP = (
    "Coby Mayo homered twice in Baltimore's 6-4 win over Cleveland. "
    "Adley Rutschman and Jarren Duran homered in Boston's 5-2 win over the Angels. "
    "Jeff McNeil's walk-off lifted Oakland past Toronto 6-5."
)
RACE_AL_SINCE = "Boston is 6-4 in its last ten."
RACE_NL_RECAP = (
    "Jesús Luzardo shut out Atlanta on two hits; Philadelphia won 1-0. "
    "Jonah Tong and the Mets beat Miami 9-4. "
    "Arizona scored five in the 10th to beat Kansas City 5-4."
)
RACE_NL_SINCE = "Philadelphia is 7-3 in its last ten."


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
    return m.group(1).replace("2026-09-06", ISSUE_DATE)


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
<title>Scorebook - Monday, September 7</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Monday, September 7" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Monday, September 7" />
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
  <h1>Monday, September 7</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("luzardo")}
  <p class="cap">{CLIPS["luzardo"]["cap"]}</p>
{clip_html("mayo")}
  <p class="cap">{CLIPS["mayo"]["cap"]}</p>
{clip_html("dbacks")}
  <p class="cap">{CLIPS["dbacks"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="luzardo" required> Luzardo's shutout</label>
      <label><input type="radio" name="play" value="mayo"> Mayo's two homers</label>
      <label><input type="radio" name="play" value="dbacks"> D-backs' five-run 10th</label>
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
{clip_html("elly")}
  <p class="cap">{CLIPS["elly"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Top of the 10th at Kauffman Stadium. Arizona had been held scoreless through nine but sent nine batters to the plate and scored five runs on four hits — Perdomo's two-run single and Nootbaar's sac fly among the damage. Kansas City answered with four in the bottom half but fell 5-4.</p>
{clip_html("dbacks_tenth")}
  <p class="cap">{CLIPS["dbacks_tenth"]["cap"]}</p>

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
