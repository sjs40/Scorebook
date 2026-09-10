#!/usr/bin/env python3
"""Generate /workspace/2026-09-09/index.html and share race text files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-09"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-09-08" / "index.html"
ISSUE_DATE = "2026-09-09"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Mets and Marlins combine for 29 runs in a 15–14 slugfest — Lindor's 3-run homer keyed a six-run seventh. "
    "Schwarber's grand slam and Harper's bat fuel an 11–7 Phillies win over Houston. "
    "Brewers hit three homers to hold off the Cubs 8–6. "
    "Rays stay two clear in the AL East with a 7–2 win in Atlanta."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/09"

CLIPS = {
    "lindor": {
        "video": f"{MLB_CDN}/9b6e6cab-878591d6-5a175ab3-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "tyler-zuber-in-play-run-s-to-francisco-lindor",
        "cap": (
            "Francisco Lindor: three-run homer in a six-run seventh. "
            "Mets 15, Marlins 14 — New York led 8–0 and Miami nearly came back twice."
        ),
    },
    "brewers": {
        "video": f"{MLB_CDN}/35884a84-317b3be1-a2e848be-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "brewers-crush-three-homers-in-win-vs-cubs",
        "cap": (
            "Christian Yelich, William Contreras, and Jackson Chourio all homered. "
            "Brewers 8, Cubs 6 — Milwaukee's magic number is five."
        ),
    },
    "rays": {
        "video": f"{MLB_CDN}/8592d5c2-0b2b2fa1-023aaffd-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "victor-mesa-jr-jorge-mateo-lift-rays-in-7-2-win",
        "cap": (
            "Victor Mesa Jr. homered; Jorge Mateo drove in two. "
            "Rays 7, Braves 2 — Tampa Bay's lead in the AL East is four games."
        ),
    },
    "lombard": {
        "video": f"{MLB_CDN}/68411571-5b6a78d2-afe78a78-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "george-lombard-jr-hits-first-career-grand-slam",
        "cap": (
            "George Lombard Jr.: first career grand slam, a pinch-hit shot in the third. "
            "That's baseball."
        ),
    },
    "mets_seventh": {
        "video": f"{MLB_CDN}/32bcad92-6f3e66d6-e7ef6d7e-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "mets-rack-up-six-runs-in-the-7th-inning",
        "cap": (
            "Six runs in the top of the seventh — Lindor's three-run homer "
            "and Morel's two-run shot among the damage."
        ),
    },
}

PITCHERS = [
    ("Will Warren", "NYY", 72, "6.0", 4, 1, 2, 8, "COL"),
    ("Logan Henderson", "MIL", 72, "5.0", 2, 0, 1, 6, "CHC"),
    ("Kade Anderson", "SEA", 63, "6.0", 6, 1, 1, 5, "TEX"),
    ("Ryan Johnson", "LAA", 61, "6.0", 5, 3, 1, 5, "BOS"),
]

HITTERS = [
    ("Jackson Merrill", "SDP", 12, 5, 4, 3, 2, 6, 0),
    ("Christopher Morel", "NYM", 7, 4, 3, 2, 1, 3, 0),
    ("Jackson Chourio", "MIL", 6, 5, 3, 1, 1, 2, 1),
    ("Joe Mack", "MIA", 6, 5, 3, 1, 1, 3, 0),
    ("Denzer Guzman", "LAA", 6, 4, 3, 1, 1, 1, 0),
    ("Luis García Jr.", "NYY", 6, 4, 2, 2, 1, 1, 0),
    ("Isaac Paredes", "HOU", 5, 4, 2, 1, 1, 3, 0),
    ("Zach Neto", "LAA", 5, 3, 2, 1, 1, 3, 0),
]

# away, home, away_score, home_score, away_innings, home_innings, away_h, away_e, home_h, home_e, note
GAMES = [
    ("MIN", "DET", 2, 7, [0, 0, 0, 2, 0, 0, 0, 0, 0], [2, 0, 3, 0, 0, 0, 1, 1, 0], 5, 0, 7, 0, "W Tyler Holton · L Zebby Matthews"),
    ("TOR", "ATH", 0, 2, [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 0, 0, 0, 0, 0], 6, 0, 4, 0, "W Scott Blewett · L Michael Lorenzen · S Elvis Alvarado"),
    ("STL", "SFG", 6, 7, [0, 1, 3, 0, 1, 1, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0, 6, 0], 8, 0, 10, 3, "W Matt Wilkinson · L George Soriano · S Trent Harris"),
    ("WSN", "SDP", 2, 9, [0, 0, 2, 0, 0, 0, 0, 0, 0], [0, 0, 3, 2, 2, 0, 1, 1, 0], 4, 1, 16, 0, "W Kyle Hart · L Jackson Kent"),
    ("TEX", "SEA", 2, 3, [0, 1, 0, 0, 0, 0, 0, 1, 0], [0, 1, 0, 2, 0, 0, 0, 0, 0], 7, 0, 6, 0, "W Kade Anderson · L Cody Bradford · S Andrés Muñoz"),
    ("CLE", "BAL", 5, 9, [2, 0, 0, 0, 0, 3, 0, 0, 0], [0, 0, 8, 0, 0, 1, 0, 0, 0], 9, 2, 10, 1, "W Shane Baz · L Foster Griffin · S Rico Garcia"),
    ("HOU", "PHI", 7, 11, [0, 0, 4, 2, 0, 0, 1, 0, 0], [0, 0, 4, 0, 1, 6, 0, 0, 0], 12, 2, 12, 2, "W Cristopher Sánchez · L Bryan King"),
    ("NYM", "MIA", 15, 14, [0, 6, 2, 0, 0, 0, 6, 1, 0], [0, 0, 0, 3, 0, 5, 1, 2, 3], 15, 0, 20, 0, "W Daniel Duarte · L Josh Ekness · S Tobias Myers"),
    ("LAA", "BOS", 6, 4, [0, 0, 5, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 2, 1, 0, 0, 1], 12, 0, 8, 0, "W Ryan Johnson · L Jake Bennett · S Ben Joyce"),
    ("COL", "NYY", 1, 6, [0, 0, 0, 0, 1, 0, 0, 0, 0], [0, 1, 4, 0, 0, 0, 0, 1, 0], 5, 0, 7, 0, "W Will Warren · L Tomoyuki Sugano"),
    ("TBR", "ATL", 7, 2, [0, 3, 0, 3, 0, 0, 1, 0, 0], [0, 0, 0, 1, 0, 1, 0, 0, 0], 10, 0, 3, 0, "W Griffin Jax · L Reynaldo López"),
    ("ARI", "KCR", 2, 5, [0, 0, 0, 1, 1, 0, 0, 0, 0], [0, 1, 1, 0, 3, 0, 0, 0, 0], 9, 1, 7, 0, "W Daniel Lynch IV · L Michael Soroka · S Nate Pearson"),
    ("PIT", "CHW", 4, 2, [0, 0, 0, 0, 1, 0, 3, 0, 0], [0, 0, 0, 0, 0, 0, 1, 1, 0], 10, 0, 8, 0, "W Brandon Eisert · L Davis Martin · S Mason Montgomery"),
    ("CHC", "MIL", 6, 8, [0, 0, 0, 1, 0, 0, 0, 0, 5], [3, 3, 1, 0, 0, 1, 0, 0, 0], 5, 2, 9, 1, "W Logan Henderson · L Kevin Gausman"),
    ("CIN", "LAD", 1, 14, [0, 0, 0, 1, 0, 0, 0, 0, 0], [0, 1, 2, 6, 0, 2, 2, 1, 0], 6, 0, 14, 0, "W Yoshinobu Yamamoto · L Rhett Lowder"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 87, 58, "--", "--", "W2", "6-4", "+58"),
        ("NYY", 83, 62, "4", "+10", "W2", "7-3", "+124"),
        ("BOS", 80, 67, "8", "+6", "L2", "6-4", "+82"),
        ("TOR", 73, 74, "15", "1", "L1", "6-4", "-39"),
        ("BAL", 71, 76, "17", "3", "W1", "3-7", "-27"),
    ],
    "AL Central": [
        ("CHW", 75, 70, "--", "--", "L2", "3-7", "+41"),
        ("CLE", 74, 73, "2", "--", "L1", "5-5", "-16"),
        ("MIN", 69, 77, "6.5", "4.5", "L1", "5-5", "-53"),
        ("DET", 67, 79, "8.5", "6.5", "W1", "4-6", "+55"),
        ("KCR", 65, 82, "11", "9", "W1", "3-7", "-88"),
    ],
    "AL West": [
        ("HOU", 74, 72, "--", "--", "L1", "6-4", "-41"),
        ("TEX", 72, 74, "2", "1.5", "L1", "6-4", "-40"),
        ("SEA", 68, 78, "6", "5.5", "W1", "4-6", "-75"),
        ("ATH", 59, 88, "15.5", "15", "W1", "6-4", "-187"),
        ("LAA", 56, 90, "18", "17.5", "W2", "4-6", "-73"),
    ],
    "AL Wild Card": [
        ("NYY", 83, 62, "+10", "W2", "7-3", "+124", False),
        ("BOS", 80, 67, "+6", "L2", "6-4", "+82", False),
        ("CLE", 74, 73, "--", "L1", "5-5", "-16", True),
        ("TOR", 73, 74, "1", "L1", "6-4", "-39", False),
        ("TEX", 72, 74, "1.5", "L1", "6-4", "-40", False),
        ("BAL", 71, 76, "3", "W1", "3-7", "-27", False),
    ],
    "NL East": [
        ("ATL", 85, 61, "--", "--", "L3", "4-6", "+108"),
        ("PHI", 82, 64, "3", "+4", "W1", "6-4", "+38"),
        ("MIA", 72, 75, "13.5", "6.5", "L3", "3-7", "+7"),
        ("NYM", 68, 78, "17", "10", "W4", "7-3", "-40"),
        ("WSN", 67, 81, "19", "12", "L7", "2-8", "0"),
    ],
    "NL Central": [
        ("MIL", 91, 56, "--", "--", "W3", "6-4", "+172"),
        ("CHC", 81, 66, "10", "+2.5", "L4", "4-6", "+128"),
        ("PIT", 73, 73, "17.5", "5", "W3", "8-2", "+34"),
        ("STL", 72, 75, "19", "6.5", "L3", "4-6", "-12"),
        ("CIN", 69, 77, "21.5", "9", "L3", "5-5", "-122"),
    ],
    "NL West": [
        ("LAD", 89, 57, "--", "--", "W7", "8-2", "+169"),
        ("SDP", 78, 68, "11", "--", "W4", "6-4", "+17"),
        ("ARI", 78, 69, "11.5", "0.5", "L1", "5-5", "-1"),
        ("SFG", 62, 85, "27.5", "16.5", "W3", "6-4", "-72"),
        ("COL", 55, 90, "33.5", "22.5", "L3", "3-7", "-147"),
    ],
    "NL Wild Card": [
        ("PHI", 82, 64, "+4", "W1", "6-4", "+38", False),
        ("CHC", 81, 66, "+2.5", "L4", "4-6", "+128", False),
        ("SDP", 78, 68, "--", "W4", "6-4", "+17", True),
        ("ARI", 78, 69, "0.5", "L1", "5-5", "-1", False),
        ("PIT", 73, 73, "5", "W3", "8-2", "+34", False),
        ("MIA", 72, 75, "6.5", "L3", "3-7", "+7", False),
    ],
}

UPCOMING = [
    ("TBR", "ATL", "Nick Martinez vs. Martín Pérez", "12:15 PM ET", "2026-09-10T16:15:00Z", ""),
    ("HOU", "PHI", "Cristian Javier vs. Zack Wheeler", "1:05 PM ET", "2026-09-10T17:05:00Z", ""),
    ("TEX", "SEA", "Jacob deGrom vs. Logan Gilbert", "4:10 PM ET", "2026-09-10T20:10:00Z", ""),
    ("COL", "NYY", "Ryan Feltner vs. Max Fried", "7:05 PM ET", "2026-09-10T23:05:00Z", ""),
    ("PIT", "CHW", "Jared Jones vs. Hagen Smith", "7:40 PM ET", "2026-09-10T23:40:00Z", ""),
]

OFF_TONIGHT: list[str] = []

TEAM_SUMMARIES = {
    "CHC": "Your Cubs: Gausman took the loss as Milwaukee hit three homers in an 8–6 defeat. Off tonight.",
    "MIA": "Your Marlins: Joe Mack homered in a 14–15 loss to the Mets; Miami nearly came back twice. Off tonight.",
    "SFG": "Your Giants: Six runs in the eighth beat St. Louis 7–6. Off tonight.",
    "NYM": "Your Mets: Lindor's 3-run homer keyed a six-run seventh in a 15–14 win at Miami. Off tonight.",
    "ATL": "Your Braves: Lost 2–7 to Tampa Bay; third straight defeat. Host the Rays tonight.",
    "PHI": "Your Phillies: Schwarber's grand slam in a six-run sixth; beat Houston 11–7. Host the Astros tonight.",
    "DET": "Your Tigers: Keith and Dingler homered in a 7–2 win over Minnesota. Off tonight.",
    "CLE": "Your Guardians: Lost 5–9 at Baltimore after an eight-run Orioles third. Off tonight.",
    "LAA": "Your Angels: Johnson won at Fenway; Guzman and Neto homered in a 6–4 win. Off tonight.",
    "PIT": "Your Pirates: Eisert and Montgomery closed out a 4–2 win at Chicago. At Chicago tonight.",
    "MIL": "Your Brewers: Yelich, Contreras, and Chourio homered in an 8–6 win over the Cubs. Off tonight.",
    "CIN": "Your Reds: Lost 1–14 at Dodger Stadium. Off tonight.",
    "BOS": "Your Red Sox: Lost 4–6 to the Angels. Off tonight.",
    "BAL": "Your Orioles: Eight runs in the third beat Cleveland 9–5. Off tonight.",
    "TBR": "Your Rays: Mesa Jr. homered in a 7–2 win at Atlanta; AL East lead is four. At Atlanta tonight.",
    "TEX": "Your Rangers: Lost 2–3 at Seattle. At Seattle tonight.",
    "MIN": "Your Twins: Lost 2–7 at Detroit. Off tonight.",
    "CHW": "Your White Sox: Lost 2–4 to Pittsburgh. Host the Pirates tonight.",
    "TOR": "Your Blue Jays: Shut out 0–2 at Oakland. Off tonight.",
    "KCR": "Your Royals: Lynch won 5–2 over Arizona. Off tonight.",
    "ARI": "Your Diamondbacks: Lost 2–5 at Kansas City. Off tonight.",
    "HOU": "Your Astros: Paredes homered but lost 7–11 at Philadelphia. At Philadelphia tonight.",
    "NYY": "Your Yankees: Lombard Jr.'s first career grand slam in a 6–1 win over Colorado. Host the Rockies tonight.",
    "SDP": "Your Padres: Merrill went 4-for-5 with two homers and six RBIs in a 9–2 rout of Washington. Off tonight.",
    "STL": "Your Cardinals: Six runs in the eighth weren't enough in a 6–7 loss at San Francisco. Off tonight.",
    "COL": "Your Rockies: Lost 1–6 at New York. At New York tonight.",
    "WSN": "Your Nationals: Lost 2–9 at San Diego; seventh straight defeat. Off tonight.",
    "LAD": "Your Dodgers: Yamamoto fanned 10 in seven innings; beat Cincinnati 14–1. Off tonight.",
    "ATH": "Your Athletics: Blewett won 2–0 over Toronto. Off tonight.",
    "SEA": "Your Mariners: Anderson beat Texas 3–2. Host the Rangers tonight.",
}

RACE_AL_RECAP = (
    "Kyle Schwarber's grand slam led Philadelphia past Houston 11–7. "
    "The Rays beat Atlanta 7–2 to stay four clear in the AL East. "
    "Shane Baz and an eight-run third beat Cleveland 9–5 at Camden Yards."
)
RACE_AL_SINCE = "The Rays are 6–4 in their last ten."
RACE_NL_RECAP = (
    "The Mets outlasted Miami 15–14 — Lindor's 3-run homer keyed a six-run seventh. "
    "Milwaukee hit three homers to beat Chicago 8–6; the Brewers' magic number is five. "
    "Yoshinobu Yamamoto fanned 10 as the Dodgers beat Cincinnati 14–1."
)
RACE_NL_SINCE = "Milwaukee is 6–4 in its last ten."


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
    return m.group(1).replace("2026-09-08", ISSUE_DATE)


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
<title>Scorebook - Wednesday, September 9</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Wednesday, September 9" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Wednesday, September 9" />
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
  <h1>Wednesday, September 9</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("lindor")}
  <p class="cap">{CLIPS["lindor"]["cap"]}</p>
{clip_html("brewers")}
  <p class="cap">{CLIPS["brewers"]["cap"]}</p>
{clip_html("rays")}
  <p class="cap">{CLIPS["rays"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="lindor" required> Lindor's 3-run homer in the 7th</label>
      <label><input type="radio" name="play" value="brewers"> Brewers' three homers vs Cubs</label>
      <label><input type="radio" name="play" value="rays"> Rays rout Braves</label>
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
{clip_html("lombard")}
  <p class="cap">{CLIPS["lombard"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Top of the seventh at loanDepot park. The Mets had led 8–0 — then Francisco Lindor launched a three-run homer and Christopher Morel followed with a two-run shot as New York sent six across. Miami still nearly won 15–14.</p>
{clip_html("mets_seventh")}
  <p class="cap">{CLIPS["mets_seventh"]["cap"]}</p>

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
