#!/usr/bin/env python3
"""Generate /workspace/2026-09-23/index.html and share race text files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-23"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-09-22" / "index.html"
ISSUE_DATE = "2026-09-23"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Ben Rice hit two of the Yankees' four homers in a 9–2 rout of Tampa Bay. "
    "Brett Baty crushed a 455-foot pinch-hit grand slam in the Mets' 7–2 win at Texas. "
    "Sonny Gray tossed six scoreless as Boston beat Cleveland 1–0. "
    "Orioles swept a doubleheader over Toronto, winning both 4–2."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/23"

CLIPS = {
    "yankees_homers": {
        "video": f"{MLB_CDN}/5643a92a-69a48650-cf4120fb-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "ben-rice-hits-two-of-yankees-four-homers-in-9-2-win",
        "cap": (
            "Ben Rice hit two of four Yankees homers — "
            "New York routed Tampa Bay. Yankees 9, Rays 2."
        ),
    },
    "baty_slam": {
        "video": f"{MLB_CDN}/ec9451fb-5b52b010-113cd7b8-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "brett-baty-crushes-455-foot-grand-slam",
        "cap": (
            "Brett Baty crushed a 455-foot pinch-hit grand slam — "
            "Mets 7, Rangers 2."
        ),
    },
    "gray_shutout": {
        "video": f"{MLB_CDN}/15067480-c932dd5e-1136df94-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "sonny-gray-s-six-scoreless-innings-vs-guardians",
        "cap": (
            "Sonny Gray allowed four hits over six scoreless — "
            "Red Sox 1, Guardians 0."
        ),
    },
    "dubon_walkoff": {
        "video": f"{MLB_CDN}/ebe9fc0f-b5bee51a-101d3220-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "mauricio-dubon-singles-on-a-ground-ball-to-pitcher-luis-mey-dashawn-keirs",
        "cap": (
            "Mauricio Dubón's walk-off single in the 10th — after a 2–2 tie through nine. "
            "That's baseball."
        ),
    },
    "yankees_third": {
        "video": f"{MLB_CDN}/54157832-ad976847-d47b94cc-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "mason-englert-in-play-run-s-to-ryan-mcmahon-2m0qr3",
        "cap": (
            "Ryan McMahon's grand slam capped a five-run third — "
            "part of a four-homer night in the Bronx. Yankees 9, Rays 2."
        ),
    },
}

PITCHERS = [
    ("Trey Gibson", "BAL", 69, "6.2", 3, 0, 2, 7, "TOR"),
    ("Mason Adams", "COL", 66, "6.0", 5, 0, 0, 8, "ARI"),
    ("Chris Sale", "ATL", 65, "5.2", 4, 1, 0, 10, "CIN"),
    ("Sonny Gray", "BOS", 62, "6.0", 4, 0, 1, 3, "CLE"),
]

HITTERS = [
    ("Ben Rice", "NYY", 9, 4, 3, 2, 2, 2, 0),
    ("Yainer Diaz", "HOU", 7, 5, 2, 2, 1, 3, 0),
    ("Matt Olson", "ATL", 6, 4, 2, 2, 1, 1, 0),
    ("Brice Turang", "MIL", 6, 4, 2, 2, 1, 1, 0),
    ("Henry Bolte", "ATH", 6, 5, 4, 2, 0, 1, 0),
    ("Ryan McMahon", "NYY", 5, 4, 2, 1, 1, 5, 0),
    ("Christian Encarnacion-Strand", "BAL", 5, 3, 2, 1, 1, 3, 0),
    ("Vaughn Grissom", "LAA", 5, 4, 2, 1, 1, 2, 0),
]

GAMES = [
    ("WSN", "DET", 4, 2, [0, 0, 0, 0, 0, 3, 1, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0, 1], 6, 0, 8, 0, "W Will Dion · L Framber Valdez · S Yovanny Cruz"),
    ("TOR", "BAL", 2, 4, [0, 0, 0, 0, 0, 2, 0, 0, 0], [0, 2, 0, 0, 2, 0, 0, 0, 0], 10, 1, 5, 1, "W Chris Bassitt · L Max Scherzer · S Andrew Kittredge"),
    ("TOR", "BAL", 2, 4, [0, 0, 0, 0, 0, 0, 0, 0, 2], [3, 0, 0, 1, 0, 0, 0, 0, 0], 6, 0, 4, 1, "W Trey Gibson · L CJ Van Eyk"),
    ("MIN", "SFG", 4, 2, [0, 0, 1, 0, 1, 0, 2, 0, 0], [0, 0, 0, 2, 0, 0, 0, 0, 0], 9, 0, 5, 1, "W Yoendrys Gómez · L Dylan Smith · S Andrew Morris"),
    ("STL", "PIT", 5, 1, [0, 0, 3, 2, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 0], 10, 0, 6, 0, "W Matthew Liberatore · L Brandon Eisert"),
    ("MIL", "PHI", 4, 1, [1, 1, 2, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 0], 6, 0, 6, 1, "W Logan Henderson · L Aaron Nola · S Trevor Megill"),
    ("TBR", "NYY", 2, 9, [0, 0, 0, 1, 1, 0, 0, 0, 0], [1, 1, 5, 1, 0, 0, 0, 1, 0], 6, 1, 12, 1, "W Gerrit Cole · L Mason Englert"),
    ("CLE", "BOS", 0, 1, [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0, 0], 5, 1, 12, 0, "W Sonny Gray · L Foster Griffin · S Aroldis Chapman"),
    ("CIN", "ATL", 2, 3, [1, 0, 0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 1, 1, 0, 0, 1], 5, 1, 7, 0, "W Brent Suter · L Luis Mey"),
    ("CWS", "KCR", 4, 5, [0, 0, 4, 0, 0, 0, 0, 0, 0], [4, 0, 0, 0, 0, 0, 1, 0, 0], 9, 1, 12, 0, "W Connor Thomas · L Hagen Smith · S Steven Cruz"),
    ("MIA", "CHC", 3, 2, [0, 0, 0, 0, 0, 2, 1, 0, 0], [0, 0, 0, 0, 0, 2, 0, 0, 0], 10, 0, 8, 0, "W Cade Gibson · L Ryan Rolison · S Sandy Alcantara"),
    ("NYM", "TEX", 7, 2, [0, 0, 2, 0, 0, 0, 0, 1, 4], [0, 0, 0, 0, 2, 0, 0, 0, 0], 8, 0, 4, 1, "W Nolan McLean · L Jacob Latz"),
    ("ARI", "COL", 5, 3, [4, 0, 0, 0, 0, 0, 0, 1, 0], [0, 1, 1, 0, 0, 0, 0, 1, 0], 8, 0, 7, 1, "W Merrill Kelly · L Mason Adams · S Jonathan Loáisiga"),
    ("LAA", "ATH", 3, 7, [0, 0, 0, 2, 1, 0, 0, 0, 0], [4, 1, 0, 0, 0, 2, 0, 0, 0], 8, 1, 13, 0, "W Geoff Hartlieb · L Walbert Ureña"),
    ("SDP", "LAD", 5, 1, [0, 0, 0, 2, 2, 0, 0, 0, 1], [0, 0, 0, 1, 0, 0, 0, 0, 0], 8, 0, 10, 1, "W Bradgley Rodriguez · L Yoshinobu Yamamoto"),
    ("HOU", "SEA", 5, 6, [0, 0, 4, 0, 0, 0, 0, 0, 0, 1], [0, 0, 3, 0, 1, 0, 0, 0, 0, 2], 10, 0, 9, 0, "W Cooper Criswell · L Josh Hader"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 96, 62, "--", "--", "L1", "7-3", "+79"),
        ("NYY", 91, 67, "5.0", "+10.0", "W1", "6-4", "+141"),
        ("BOS", 85, 73, "11.0", "+4.0", "W1", "5-5", "+80"),
        ("BAL", 78, 81, "18.5", "3.5", "W3", "6-4", "-26"),
        ("TOR", 77, 82, "19.5", "4.5", "L3", "3-7", "-47"),
    ],
    "AL Central": [
        ("CLE", 82, 76, "--", "--", "L1", "7-3", "+2"),
        ("CWS", 81, 77, "1.0", "--", "L1", "5-5", "+44"),
        ("MIN", 75, 84, "7.5", "6.5", "W2", "5-5", "-64"),
        ("DET", 74, 85, "8.5", "7.5", "L2", "4-6", "+71"),
        ("KCR", 68, 90, "14.0", "13.0", "W1", "2-8", "-104"),
    ],
    "AL West": [
        ("HOU", 78, 80, "--", "--", "L1", "3-7", "-53"),
        ("TEX", 78, 80, "--", "3.0", "L3", "6-4", "-42"),
        ("SEA", 74, 84, "4.0", "7.0", "W1", "5-5", "-62"),
        ("ATH", 63, 95, "15.0", "18.0", "W2", "3-7", "-217"),
        ("LAA", 60, 98, "18.0", "21.0", "L3", "4-6", "-93"),
    ],
    "AL Wild Card": [
        ("NYY", 91, 67, "+10.0", "W1", "6-4", "+141", False),
        ("BOS", 85, 73, "+4.0", "W1", "5-5", "+80", False),
        ("CWS", 81, 77, "--", "L1", "5-5", "+44", True),
        ("TEX", 78, 80, "3.0", "L3", "6-4", "-42", False),
        ("BAL", 78, 81, "3.5", "W3", "6-4", "-26", False),
        ("TOR", 77, 82, "4.5", "L3", "3-7", "-47", False),
    ],
    "NL East": [
        ("ATL", 93, 65, "--", "--", "W1", "6-4", "+117"),
        ("PHI", 87, 71, "6.0", "--", "L1", "5-5", "+28"),
        ("MIA", 78, 80, "15.0", "9.0", "W2", "6-4", "+4"),
        ("WSN", 75, 84, "18.5", "12.5", "W2", "7-3", "+9"),
        ("NYM", 73, 85, "20.0", "14.0", "W2", "4-6", "-33"),
    ],
    "NL Central": [
        ("MIL", 99, 59, "--", "--", "W1", "7-3", "+203"),
        ("CHC", 87, 71, "12.0", "--", "L2", "5-5", "+145"),
        ("PIT", 80, 78, "19.0", "7.0", "L1", "6-4", "+27"),
        ("STL", 77, 81, "22.0", "10.0", "W1", "4-6", "-21"),
        ("CIN", 73, 85, "26.0", "14.0", "L1", "4-6", "-160"),
    ],
    "NL West": [
        ("LAD", 97, 61, "--", "--", "L1", "7-3", "+196"),
        ("SDP", 88, 70, "9.0", "+1.0", "W1", "8-2", "+38"),
        ("ARI", 84, 74, "13.0", "3.0", "W4", "5-5", "+6"),
        ("SFG", 65, 94, "32.5", "22.5", "L2", "3-7", "-84"),
        ("COL", 57, 101, "40.0", "30.0", "L3", "2-8", "-184"),
    ],
    "NL Wild Card": [
        ("SDP", 88, 70, "+1.0", "W1", "8-2", "+38", False),
        ("CHC", 87, 71, "--", "L2", "5-5", "+145", False),
        ("PHI", 87, 71, "--", "L1", "5-5", "+28", True),
        ("ARI", 84, 74, "3.0", "W4", "5-5", "+6", False),
        ("PIT", 80, 78, "7.0", "L1", "6-4", "+27", False),
        ("MIA", 78, 80, "9.0", "W2", "6-4", "+4", False),
    ],
}

UPCOMING = [
    ("STL", "PIT", "Kyle Leahy vs. Paul Skenes", "12:35 PM ET", "2026-09-24T16:35:00Z", ""),
    ("CWS", "KCR", "David Sandlin vs. Randy Dobnak", "2:10 PM ET", "2026-09-24T18:10:00Z", ""),
    ("MIA", "CHC", "Tyler Phillips vs. Matthew Boyd", "2:20 PM ET", "2026-09-24T18:20:00Z", ""),
    ("NYM", "TEX", "Zac Thornton vs. Kumar Rocker", "2:35 PM ET", "2026-09-24T18:35:00Z", ""),
    ("ARI", "COL", "Eduardo Rodriguez vs. Tanner Gordon", "3:10 PM ET", "2026-09-24T19:10:00Z", ""),
    ("MIL", "PHI", "Bryse Wilson vs. Andrew Painter", "6:05 PM ET", "2026-09-24T22:05:00Z", ""),
    ("CLE", "BOS", "Daniel Espino vs. Ranger Suarez", "6:45 PM ET", "2026-09-24T22:45:00Z", ""),
    ("TBR", "NYY", "Ian Seymour vs. Cam Schlittler", "7:05 PM ET", "2026-09-24T23:05:00Z", ""),
    ("CIN", "ATL", "Brady Singer vs. Tyler Mahle", "7:15 PM ET", "2026-09-24T23:15:00Z", ""),
    ("HOU", "ATH", "Peter Lambert vs. Mason Barnett", "9:40 PM ET", "2026-09-25T01:40:00Z", ""),
    ("LAA", "SEA", "Grayson Rodriguez vs. Bryan Woo", "9:40 PM ET", "2026-09-25T01:40:00Z", ""),
    ("SDP", "LAD", "Nick Pivetta vs. Tyler Glasnow", "10:10 PM ET", "2026-09-25T02:10:00Z", ""),
]

OFF_TONIGHT = ["WSN", "DET", "TOR", "BAL", "MIN", "SFG"]

TEAM_SUMMARIES = {
    "TBR": "Your Rays: Lost 2–9 at New York; Englert took the loss. At New York tonight.",
    "NYY": "Your Yankees: Won 9–2 over Tampa Bay; Cole earned the win and Ben Rice homered twice. Host Tampa Bay tonight.",
    "WSN": "Your Nationals: Won 4–2 at Detroit; Dion earned the win. Off tonight.",
    "DET": "Your Tigers: Lost 2–4 to Washington; Valdez took the loss. Off tonight.",
    "STL": "Your Cardinals: Won 5–1 at Pittsburgh; Liberatore earned the win. At Pittsburgh tonight.",
    "PIT": "Your Pirates: Lost 1–5 to St. Louis; Eisert took the loss. Host St. Louis tonight.",
    "MIL": "Your Brewers: Won 4–1 at Philadelphia; Henderson earned the win. At Philadelphia tonight.",
    "PHI": "Your Phillies: Lost 1–4 to Milwaukee; Nola took the loss. Host Milwaukee tonight.",
    "CLE": "Your Guardians: Lost 0–1 at Boston; Griffin took the loss. At Boston tonight.",
    "BOS": "Your Red Sox: Won 1–0 over Cleveland; Gray tossed six scoreless. Host Cleveland tonight.",
    "CIN": "Your Reds: Lost 2–3 to Atlanta in 10; Mey took the loss. At Atlanta tonight.",
    "ATL": "Your Braves: Won 3–2 over Cincinnati in 10; Dubón's walk-off single. Host Cincinnati tonight.",
    "CWS": "Your White Sox: Lost 4–5 at Kansas City; Smith took the loss. At Kansas City tonight.",
    "KCR": "Your Royals: Won 5–4 over Chicago; Thomas earned the win. Host White Sox tonight.",
    "MIA": "Your Marlins: Won 3–2 at Chicago; Gibson earned the win. At Chicago tonight.",
    "CHC": "Your Cubs: Lost 2–3 to Miami; Rolison took the loss. Host Miami tonight.",
    "NYM": "Your Mets: Won 7–2 at Texas; McLean earned the win and Baty hit a pinch-hit grand slam. At Texas tonight.",
    "TEX": "Your Rangers: Lost 2–7 to New York; Latz took the loss. Host New York tonight.",
    "ARI": "Your Diamondbacks: Won 5–3 at Colorado; Kelly earned the win. At Colorado tonight.",
    "COL": "Your Rockies: Lost 3–5 to Arizona; Adams took the loss. Host Arizona tonight.",
    "LAA": "Your Angels: Lost 3–7 at Oakland; Ureña took the loss. At Seattle tonight.",
    "ATH": "Your Athletics: Won 7–3 over the Angels; Hartlieb earned the win. Host Houston tonight.",
    "HOU": "Your Astros: Lost 5–6 to Seattle in 10; Hader took the loss. At Oakland tonight.",
    "SEA": "Your Mariners: Won 6–5 over Houston in 10; Criswell earned the win. Host Angels tonight.",
    "MIN": "Your Twins: Won 4–2 at San Francisco; Gómez earned the win. Off tonight.",
    "SFG": "Your Giants: Lost 2–4 to Minnesota; Smith took the loss. Off tonight.",
    "SDP": "Your Padres: Won 5–1 at Los Angeles; Rodriguez earned the win and Machado homered. At Los Angeles tonight.",
    "LAD": "Your Dodgers: Lost 1–5 to San Diego; Yamamoto took the loss. Host San Diego tonight.",
    "TOR": "Your Blue Jays: Lost both games of a doubleheader at Baltimore, 2–4 each. Off tonight.",
    "BAL": "Your Orioles: Swept Toronto in a doubleheader, winning both 4–2. Off tonight.",
}

RACE_AL_RECAP = (
    "Ben Rice hit two of the Yankees' four homers in a 9–2 rout of Tampa Bay. "
    "Sonny Gray tossed six scoreless as Boston beat Cleveland 1–0. "
    "Baltimore swept Toronto in a doubleheader, winning both 4–2."
)
RACE_AL_SINCE = "The Yankees are 6–4 in their last ten."
RACE_NL_RECAP = (
    "Brett Baty crushed a 455-foot pinch-hit grand slam in the Mets' 7–2 win at Texas. "
    "San Diego beat Los Angeles 5–1 behind Manny Machado. "
    "Mauricio Dubón's walk-off single lifted Atlanta over Cincinnati 3–2 in 10."
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
    return m.group(1).replace("2026-09-22", ISSUE_DATE)


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
<title>Scorebook - Wednesday, September 23</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Wednesday, September 23" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Wednesday, September 23" />
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
  <h1>Wednesday, September 23</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("yankees_homers")}
  <p class="cap">{CLIPS["yankees_homers"]["cap"]}</p>
{clip_html("baty_slam")}
  <p class="cap">{CLIPS["baty_slam"]["cap"]}</p>
{clip_html("gray_shutout")}
  <p class="cap">{CLIPS["gray_shutout"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="yankees_homers" required> Yankees' four homers</label>
      <label><input type="radio" name="play" value="baty_slam"> Baty's grand slam</label>
      <label><input type="radio" name="play" value="gray_shutout"> Gray's shutout</label>
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
{clip_html("dubon_walkoff")}
  <p class="cap">{CLIPS["dubon_walkoff"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Bottom of the third at Yankee Stadium. New York had already scored twice when the Yankees put up five more — part of a four-homer night. Yankees 9, Rays 2.</p>
{clip_html("yankees_third")}
  <p class="cap">{CLIPS["yankees_third"]["cap"]}</p>

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
