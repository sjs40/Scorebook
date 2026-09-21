#!/usr/bin/env python3
"""Generate /workspace/2026-09-20/index.html and share race text files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-20"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-09-19" / "index.html"
ISSUE_DATE = "2026-09-20"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "The Braves clinched the NL East in a 4–2 win at Houston. "
    "Jake Cronenworth homered twice and drove in five in the Padres' 7–3 win over Miami. "
    "Nolan Arenado's grand slam lifted Arizona to an 8–4 win over New York. "
    "The Cubs scored nine at Cincinnati behind Peterson and Crow-Armstrong."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/20"

CLIPS = {
    "braves_clinch": {
        "video": f"{MLB_CDN}/6a4ac287-27ae9d88-9ebfdc69-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "braves-clinch-2026-nl-east-title-in-4-2-win",
        "cap": (
            "Mike Yastrzemski's three-run homer in the sixth keyed Atlanta's division clincher — "
            "Braves 4, Astros 2."
        ),
    },
    "cronenworth_five_rbi": {
        "video": f"{MLB_CDN}/488630df-31a49dfb-de0bb759-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "jake-cronenworth-s-five-rbi-game-vs-marlins",
        "cap": (
            "Jake Cronenworth went deep twice and drove in five — "
            "San Diego's fifth straight win. Padres 7, Marlins 3."
        ),
    },
    "arenado_grand_slam": {
        "video": f"{MLB_CDN}/38872a69-2543ad19-a302c9cf-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "nolan-arenado-s-grand-slam-27",
        "cap": (
            "Nolan Arenado cleared the bases with a grand slam in the fifth — "
            "Arizona scored five in the frame. D-backs 8, Yankees 4."
        ),
    },
    "red_sox_clinch": {
        "video": f"{MLB_CDN}/93c15bf0-139c388e-c356d914-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "red-sox-discuss-clinching-playoff-berth",
        "cap": (
            "Boston lost 1–5 at Tampa Bay — and still clinched a playoff berth. "
            "That's baseball."
        ),
    },
    "cubs_four_run_third": {
        "video": f"{MLB_CDN}/ef6889c0-5580a5cd-69728491-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "cubs-score-four-runs-in-the-top-of-the-3rd-inning",
        "cap": (
            "Chicago put up four in the third — part of a 9-run afternoon at Cincinnati. "
            "Cubs 9, Reds 1."
        ),
    },
}

PITCHERS = [
    ("Emmet Sheehan", "LAD", 69, "5.1", 1, 0, 1, 9, "SFG"),
    ("Gavin Williams", "CLE", 66, "7.0", 3, 0, 1, 9, "ATH"),
    ("Kade Anderson", "SEA", 66, "7.0", 3, 0, 0, 7, "COL"),
    ("Dean Kremer", "MIN", 66, "6.0", 1, 0, 3, 8, "LAA"),
]

HITTERS = [
    ("Jake Cronenworth", "SDP", 10, 4, 3, 3, 2, 5, 0),
    ("Iván Herrera", "STL", 8, 4, 2, 2, 2, 2, 0),
    ("Pete Crow-Armstrong", "CHC", 7, 5, 3, 2, 1, 2, 1),
    ("Alan Roden", "MIN", 6, 5, 3, 1, 1, 4, 0),
    ("Rafael Flores Jr.", "PIT", 6, 3, 2, 2, 1, 2, 0),
    ("Mike Yastrzemski", "ATL", 5, 4, 2, 1, 1, 3, 0),
    ("George Lombard Jr.", "NYY", 5, 4, 2, 1, 1, 2, 0),
    ("Nolan Arenado", "ARI", 4, 4, 1, 1, 1, 4, 0),
]

GAMES = [
    ("PHI", "NYM", 7, 2, [2, 0, 2, 0, 0, 0, 0, 3, 0], [0, 0, 0, 0, 0, 1, 1, 0, 0], 7, 0, 10, 0, "W Cristopher Sánchez · L Jonah Tong"),
    ("KCR", "PIT", 3, 4, [1, 0, 0, 0, 0, 0, 2, 0, 0], [0, 0, 0, 1, 0, 1, 0, 2, 0], 9, 1, 8, 1, "W Carmen Mlodzinski · L Nate Pearson · S Mason Montgomery"),
    ("CHC", "CIN", 9, 1, [1, 0, 4, 0, 3, 0, 0, 1, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0], 13, 1, 4, 0, "W David Peterson · L Rhett Lowder"),
    ("ATH", "CLE", 0, 1, [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0], 6, 0, 7, 0, "W Gavin Williams · L Jack Perkins · S Cade Smith"),
    ("BOS", "TBR", 1, 5, [0, 0, 0, 0, 0, 0, 0, 0, 1], [4, 0, 0, 1, 0, 0, 0, 0, 0], 6, 0, 4, 0, "W Griffin Jax · L Patrick Sandoval"),
    ("ATL", "HOU", 4, 2, [0, 0, 0, 0, 0, 4, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 1, 0], 6, 0, 8, 1, "W Victor Mederos · L Bryan King · S Dylan Dodd"),
    ("DET", "CWS", 1, 8, [0, 0, 0, 0, 0, 0, 0, 1, 0], [0, 1, 0, 3, 2, 0, 0, 2, 0], 6, 1, 10, 0, "W Huascar Brazobán · L Troy Melton"),
    ("WSN", "STL", 3, 5, [0, 1, 0, 0, 0, 2, 0, 0, 0], [1, 0, 1, 0, 0, 0, 0, 3, 0], 7, 1, 6, 0, "W Luis Gastelum · L Yovanny Cruz · S Riley O'Brien"),
    ("TOR", "TEX", 7, 2, [1, 0, 1, 0, 1, 0, 4, 0, 0], [0, 0, 0, 2, 0, 0, 0, 0, 0], 11, 0, 8, 0, "W Spencer Arrighetti · L Jacob deGrom"),
    ("SEA", "COL", 2, 1, [0, 0, 0, 1, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1], 4, 0, 5, 0, "W Kade Anderson · L Tomoyuki Sugano · S Eduard Bazardo"),
    ("MIN", "LAA", 8, 0, [0, 0, 2, 0, 1, 2, 3, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], 13, 0, 2, 1, "W Dean Kremer · L Ryan Johnson · S Bailey Ober"),
    ("SFG", "LAD", 1, 3, [1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 1, 1, 0], 2, 0, 11, 2, "W Kris Bubic · L Sam Hentges · S Tanner Scott"),
    ("MIA", "SDP", 3, 7, [0, 0, 0, 0, 0, 0, 3, 0, 0], [0, 2, 0, 2, 0, 0, 1, 2, 0], 4, 1, 10, 0, "W Walker Buehler · L Sandy Alcantara"),
    ("NYY", "ARI", 4, 8, [0, 0, 4, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 5, 0, 2, 0, 0], 8, 1, 11, 0, "W Justin Martinez · L Brent Headrick"),
    ("MIL", "BAL", 3, 0, [0, 1, 0, 1, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], 6, 0, 4, 0, "W DL Hall · L Brandon Young · S Trevor Megill"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 95, 60, "--", "--", "W2", "8-2", "+83"),
        ("NYY", 89, 66, "6.0", "+9.5", "L2", "6-4", "+137"),
        ("BOS", 84, 72, "11.5", "+4.0", "L2", "4-6", "+80"),
        ("TOR", 77, 79, "18.5", "3.0", "W1", "4-6", "-42"),
        ("BAL", 75, 81, "20.5", "5.0", "L3", "5-5", "-31"),
    ],
    "AL Central": [
        ("CLE", 81, 75, "--", "--", "W5", "7-3", "+2"),
        ("CWS", 80, 76, "1.0", "--", "W2", "5-5", "+42"),
        ("MIN", 73, 83, "8.0", "7.0", "W1", "4-6", "-64"),
        ("DET", 73, 83, "8.0", "7.0", "L2", "6-4", "+68"),
        ("KCR", 67, 89, "14.0", "13.0", "L4", "3-7", "-102"),
    ],
    "AL West": [
        ("TEX", 78, 78, "--", "--", "L1", "6-4", "-34"),
        ("HOU", 77, 79, "1.0", "3.0", "L3", "3-7", "-59"),
        ("SEA", 73, 83, "5.0", "7.0", "W1", "5-5", "-56"),
        ("ATH", 61, 95, "17.0", "19.0", "L6", "3-7", "-223"),
        ("LAA", 60, 96, "18.0", "20.0", "L1", "4-6", "-87"),
    ],
    "AL Wild Card": [
        ("NYY", 89, 66, "+9.5", "L2", "6-4", "+137", False),
        ("BOS", 84, 72, "+4.0", "L2", "4-6", "+80", False),
        ("CWS", 80, 76, "--", "W2", "5-5", "+42", True),
        ("TOR", 77, 79, "3.0", "W1", "4-6", "-42", False),
        ("HOU", 77, 79, "3.0", "L3", "3-7", "-59", False),
        ("BAL", 75, 81, "5.0", "L3", "5-5", "-31", False),
    ],
    "NL East": [
        ("ATL", 92, 64, "--", "--", "W3", "7-3", "+120"),
        ("PHI", 86, 70, "6.0", "--", "W1", "4-6", "+29"),
        ("MIA", 76, 80, "16.0", "10.0", "L3", "4-6", "-3"),
        ("WSN", 73, 83, "19.0", "13.0", "L1", "6-4", "+12"),
        ("NYM", 71, 85, "21.0", "15.0", "L1", "3-7", "-41"),
    ],
    "NL Central": [
        ("MIL", 98, 58, "--", "--", "W3", "8-2", "+202"),
        ("CHC", 87, 69, "11.0", "+1.0", "W2", "6-4", "+152"),
        ("PIT", 79, 77, "19.0", "7.0", "W4", "6-4", "+29"),
        ("STL", 76, 80, "22.0", "10.0", "W1", "4-6", "-23"),
        ("CIN", 72, 84, "26.0", "14.0", "L2", "3-7", "-163"),
    ],
    "NL West": [
        ("LAD", 96, 60, "--", "--", "W4", "7-3", "+193"),
        ("SDP", 87, 69, "9.0", "+1.0", "W5", "9-1", "+41"),
        ("ARI", 82, 74, "14.0", "4.0", "W2", "4-6", "-1"),
        ("SFG", 64, 92, "32.0", "22.0", "L3", "3-7", "-84"),
        ("COL", 57, 99, "39.0", "29.0", "L1", "2-8", "-177"),
    ],
    "NL Wild Card": [
        ("CHC", 87, 69, "+1.0", "W2", "6-4", "+152", False),
        ("SDP", 87, 69, "+1.0", "W5", "9-1", "+41", False),
        ("PHI", 86, 70, "--", "W1", "4-6", "+29", True),
        ("ARI", 82, 74, "4.0", "W2", "4-6", "-1", False),
        ("PIT", 79, 77, "7.0", "W4", "6-4", "+29", False),
        ("MIA", 76, 80, "10.0", "L3", "4-6", "-3", False),
    ],
}

UPCOMING = [
    ("TOR", "BAL", "Trey Yesavage vs. Shane Baz", "6:35 PM ET", "2026-09-21T22:35:00Z", ""),
    ("WSN", "DET", "DJ Herz vs. River Ryan", "6:40 PM ET", "2026-09-21T22:40:00Z", ""),
    ("MIN", "SFG", "Zebby Matthews vs. Blade Tidwell", "9:45 PM ET", "2026-09-22T01:45:00Z", ""),
]

OFF_TONIGHT = sorted([
    "ARI", "ATH", "ATL", "BOS", "CHC", "CIN", "CLE", "COL", "CWS", "HOU",
    "KCR", "LAA", "LAD", "MIA", "MIL", "NYM", "NYY", "PHI", "PIT", "SDP", "SEA",
    "STL", "TBR", "TEX",
])

TEAM_SUMMARIES = {
    "CHC": "Your Cubs: Won 9–1 at Cincinnati; Peterson earned the win. Off tonight.",
    "CIN": "Your Reds: Lost 1–9 to Chicago; Lowder took the loss. Off tonight.",
    "KCR": "Your Royals: Lost 3–4 at Pittsburgh; Pearson took the loss. Off tonight.",
    "PIT": "Your Pirates: Won 4–3 over Kansas City; Mlodzinski got the win. Off tonight.",
    "MIL": "Your Brewers: Won 3–0 at Baltimore — franchise-record 98th win. Off tonight.",
    "BAL": "Your Orioles: Lost 0–3 to Milwaukee; Young took the loss. Host Toronto tonight.",
    "ATH": "Your Athletics: Lost 0–1 at Cleveland; Perkins took the loss. Off tonight.",
    "CLE": "Your Guardians: Won 1–0 over Oakland; Williams struck out nine. Off tonight.",
    "BOS": "Your Red Sox: Lost 1–5 at Tampa Bay but clinched a playoff berth. Off tonight.",
    "TBR": "Your Rays: Won 5–1 over Boston; four in the first keyed it. Off tonight.",
    "PHI": "Your Phillies: Won 7–2 at New York; Sánchez earned the win. Off tonight.",
    "NYM": "Your Mets: Lost 2–7 to Philadelphia; Tong took the loss. Off tonight.",
    "DET": "Your Tigers: Lost 1–8 at Chicago; Melton took the loss. Host Washington tonight.",
    "CWS": "Your White Sox: Won 8–1 over Detroit; Brazobán earned the win. Off tonight.",
    "TOR": "Your Blue Jays: Won 7–2 at Texas; Arrighetti earned the win. At Baltimore tonight.",
    "TEX": "Your Rangers: Lost 2–7 to Toronto; deGrom took the loss. Off tonight.",
    "SEA": "Your Mariners: Won 2–1 at Colorado; Anderson went seven scoreless. Off tonight.",
    "COL": "Your Rockies: Lost 1–2 to Seattle; Sugano took the loss. Off tonight.",
    "ATL": "Your Braves: Won 4–2 at Houston and clinched the NL East. Off tonight.",
    "HOU": "Your Astros: Lost 2–4 to Atlanta; King took the loss. Off tonight.",
    "WSN": "Your Nationals: Lost 3–5 at St. Louis; Cruz took the loss. At Detroit tonight.",
    "STL": "Your Cardinals: Won 5–3 over Washington; Herrera homered twice. Off tonight.",
    "MIN": "Your Twins: Won 8–0 at Los Angeles; Kremer and Roden's three-run homer. At San Francisco tonight.",
    "LAA": "Your Angels: Lost 0–8 to Minnesota; Johnson took the loss. Off tonight.",
    "MIA": "Your Marlins: Lost 3–7 at San Diego; Alcantara took the loss. Off tonight.",
    "SDP": "Your Padres: Won 7–3 over Miami; Cronenworth homered twice. Off tonight.",
    "NYY": "Your Yankees: Lost 4–8 at Arizona; Headrick took the loss. Off tonight.",
    "ARI": "Your Diamondbacks: Won 8–4 over New York; Arenado's grand slam in the fifth. Off tonight.",
    "SFG": "Your Giants: Lost 1–3 at Los Angeles; Hentges took the loss. Host Minnesota tonight.",
    "LAD": "Your Dodgers: Won 3–1 over San Francisco; Sheehan struck out nine in relief. Off tonight.",
}

RACE_AL_RECAP = (
    "Gavin Williams struck out nine in Cleveland's 1–0 shutout of Oakland. "
    "The White Sox scored eight in an 8–1 win over Detroit. "
    "The Brewers set a franchise record with their 98th win in a 3–0 shutout at Baltimore."
)
RACE_AL_SINCE = "The Rays are 8–2 in their last ten."
RACE_NL_RECAP = (
    "The Braves clinched the NL East behind Mike Yastrzemski's three-run homer in a 4–2 win at Houston. "
    "Jake Cronenworth homered twice in the Padres' 7–3 win over Miami. "
    "Nolan Arenado's grand slam keyed Arizona's 8–4 win over New York."
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
    return m.group(1).replace("2026-09-19", ISSUE_DATE)


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
<title>Scorebook - Sunday, September 20</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Sunday, September 20" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Sunday, September 20" />
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
  <h1>Sunday, September 20</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("braves_clinch")}
  <p class="cap">{CLIPS["braves_clinch"]["cap"]}</p>
{clip_html("cronenworth_five_rbi")}
  <p class="cap">{CLIPS["cronenworth_five_rbi"]["cap"]}</p>
{clip_html("arenado_grand_slam")}
  <p class="cap">{CLIPS["arenado_grand_slam"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="braves_clinch" required> Braves clinch NL East</label>
      <label><input type="radio" name="play" value="cronenworth_five_rbi"> Cronenworth's five-RBI game</label>
      <label><input type="radio" name="play" value="arenado_grand_slam"> Arenado's grand slam</label>
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
{clip_html("red_sox_clinch")}
  <p class="cap">{CLIPS["red_sox_clinch"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Top of the third at Great American Ball Park. Chicago had already scored in the first when the Cubs put up four more — part of a 9-run afternoon. Cubs 9, Reds 1.</p>
{clip_html("cubs_four_run_third")}
  <p class="cap">{CLIPS["cubs_four_run_third"]["cap"]}</p>

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
