#!/usr/bin/env python3
"""Generate /workspace/2026-09-11/index.html and share race text files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-11"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-09-10" / "index.html"
ISSUE_DATE = "2026-09-11"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Milwaukee scored 20 runs to clinch a playoff berth and shut out Cincinnati behind Dustin May and a "
    "Brice Turang three-run homer. Kyle Tucker's grand slam and five RBIs powered the Dodgers to a 6–2 win "
    "at Miami. Drake Baldwin's walk-off double in the 11th lifted Atlanta past Philadelphia 6–5. "
    "Donovan Walton's two-run shot in the 11th walked off Seattle for the Athletics, 6–5."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/11"

CLIPS = {
    "brewers20": {
        "video": f"{MLB_CDN}/8e607204-9e56147a-6b915e1e-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "brewers-score-20-runs-to-clinch-postseason-berth",
        "cap": (
            "Milwaukee scored 20 runs — six in the second, eight in the fifth — to clinch a postseason berth "
            "and shut out Cincinnati. Dustin May spun six scoreless on two hits."
        ),
    },
    "tucker": {
        "video": f"{MLB_CDN}/1a2f68b8-4b5a8d1c-478a2771-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "cade-gibson-in-play-run-s-to-kyle-tucker",
        "cap": (
            "Kyle Tucker: grand slam and five RBIs on a 3-for-3 night. "
            "Dodgers 6, Marlins 2 — Blake Snell struck out eight in 5⅔ innings."
        ),
    },
    "baldwin": {
        "video": f"{MLB_CDN}/87f1ceda-c7988859-79b5f340-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "brooks-raley-in-play-run-s-to-drake-baldwin",
        "cap": (
            "Drake Baldwin: walk-off double in the 11th after Ha-Seong Kim tied it with an RBI single. "
            "Braves 6, Phillies 5 — Atlanta won in extras for the second straight night."
        ),
    },
    "clinch": {
        "video": f"{MLB_CDN}/0c0f8d61-087b53b2-5622fa8a-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "brewers-clinch-playoff-berth-with-final-out",
        "cap": (
            "Final out: Milwaukee clinched a postseason berth with a 20–0 rout. "
            "That's baseball — the Brewers scored 20 and the Reds scored zero."
        ),
    },
    "brewers_fifth": {
        "video": f"{MLB_CDN}/70e006ad-a98fe52f-8b3b776a-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "brewers-eight-run-5th-inning",
        "cap": (
            "Eight runs in the fifth — Brice Turang's three-run homer and Garrett Mitchell's two-run shot "
            "highlighted the frame. Milwaukee led 17–0 and never looked back."
        ),
    },
    "walton": {
        "video": f"{MLB_CDN}/c54eefa5-a3d081ea-39e71b6e-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "donovan-walton-walks-it-off-in-extras-for-the-a-s",
        "cap": (
            "Donovan Walton: walk-off two-run homer in the 11th. "
            "Athletics 6, Mariners 5 — Lawrence Butler also homered in the extra-inning win."
        ),
    },
}

PITCHERS = [
    ("Dustin May", "MIL", 66, "6.0", 2, 0, 1, 6, "CIN"),
    ("Carlos Rodón", "NYY", 66, "6.1", 3, 1, 1, 8, "NYM"),
    ("Taj Bradley", "MIN", 64, "6.0", 1, 0, 4, 6, "CLE"),
    ("Cade Cavalli", "WSN", 64, "6.0", 3, 2, 2, 9, "LAA"),
]

HITTERS = [
    ("Chase Meidroth", "CWS", 8, 4, 2, 2, 2, 2, 0),
    ("Kyle Tucker", "LAD", 8, 3, 3, 2, 1, 5, 0),
    ("Brice Turang", "MIL", 7, 3, 3, 2, 1, 4, 0),
    ("Alex Bregman", "CHC", 7, 4, 3, 2, 1, 2, 0),
    ("Lawrence Butler", "ATH", 7, 5, 3, 2, 1, 2, 0),
    ("Garrett Mitchell", "MIL", 6, 5, 3, 1, 1, 4, 0),
    ("Brett Bateman", "TOR", 6, 5, 3, 1, 1, 2, 0),
    ("Donovan Walton", "ATH", 6, 5, 3, 1, 1, 2, 0),
]

# away, home, away_score, home_score, away_innings, home_innings, away_h, away_e, home_h, home_e, note
GAMES = [
    ("PIT", "CHC", 2, 12, [1, 0, 0, 0, 0, 1, 0, 0, 0], [0, 3, 2, 4, 0, 2, 1, 0, 0], 7, 1, 16, 0, "W Shota Imanaga · L Wilber Dotel"),
    ("COL", "DET", 2, 6, [0, 0, 0, 0, 1, 0, 0, 0, 1], [0, 0, 0, 0, 1, 4, 0, 1, 0], 10, 0, 5, 1, "W Framber Valdez · L Mark Manfredi · S Kenley Jansen"),
    ("LAA", "WSN", 3, 4, [1, 0, 0, 0, 0, 0, 1, 0, 1], [0, 0, 0, 1, 0, 0, 0, 3, 0], 4, 1, 6, 0, "W Clayton Beeter · L Samy Natera Jr. · S Erik Tolman"),
    ("NYM", "NYY", 4, 6, [0, 1, 0, 0, 0, 0, 1, 1, 1], [1, 3, 0, 0, 1, 0, 0, 1, 0], 7, 0, 13, 1, "W Carlos Rodón · L Nolan McLean · S David Bednar"),
    ("BAL", "TOR", 7, 4, [1, 5, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 1, 0, 1, 0, 0, 2], 11, 1, 10, 0, "W Chris Bassitt · L Max Scherzer · S Rico Garcia"),
    ("KCR", "BOS", 3, 2, [1, 0, 2, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 2, 0, 0, 0, 0], 10, 0, 8, 0, "W Seth Lugo · L Sonny Gray · S Steven Cruz"),
    ("HOU", "TBR", 1, 3, [0, 0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 2], 9, 0, 4, 0, "W Bryan Baker · L Bryan Abreu"),
    ("LAD", "MIA", 6, 2, [0, 0, 1, 0, 0, 1, 4, 0, 0], [0, 0, 0, 0, 0, 1, 0, 1, 0], 8, 0, 10, 0, "W Blake Snell · L Ryan Gusto"),
    ("PHI", "ATL", 5, 6, [0, 3, 0, 0, 0, 0, 0, 0, 0, 1, 1], [1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 2], 7, 1, 11, 0, "W Didier Fuentes · L Brooks Raley"),
    ("CIN", "MIL", 0, 20, [0, 0, 0, 0, 0, 0, 0, 0, 0], [2, 6, 0, 1, 8, 0, 0, 3, 0], 2, 1, 23, 1, "W Dustin May · L Andrew Abbott · S Garrett Stallings"),
    ("CLE", "MIN", 5, 2, [0, 0, 0, 0, 0, 0, 2, 0, 3], [0, 1, 0, 0, 0, 0, 1, 0, 0], 7, 0, 6, 0, "W Hunter Gaddis · L Yoendrys Gómez · S Cade Smith"),
    ("CWS", "STL", 3, 7, [1, 0, 1, 0, 0, 0, 0, 1, 0], [1, 1, 1, 0, 3, 0, 1, 0, 0], 9, 0, 13, 0, "W Gordon Graceffo · L Anthony Kay"),
    ("SEA", "ATH", 5, 6, [1, 1, 0, 0, 0, 2, 0, 0, 0, 1], [2, 0, 2, 0, 0, 0, 0, 0, 0, 2], 10, 1, 14, 1, "W Chris Roycroft · L Eduard Bazardo"),
    ("TEX", "ARI", 1, 9, [0, 0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 4, 5, 0, 0, 0], 5, 0, 11, 0, "W Kevin Ginkel · L MacKenzie Gore"),
    ("SDP", "SFG", 7, 5, [0, 2, 5, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 4, 0, 0, 0, 0], 12, 0, 6, 1, "W Robbie Ray · L Anthony Molina · S Mason Miller"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 88, 59, "--", "--", "W1", "6-4", "+58"),
        ("NYY", 85, 62, "3", "+10.5", "W4", "7-3", "+133"),
        ("BOS", 80, 68, "8.5", "+5", "L3", "5-5", "+81"),
        ("TOR", 73, 75, "15.5", "2", "L2", "5-5", "-42"),
        ("BAL", 72, 76, "16.5", "3", "W2", "3-7", "-24"),
    ],
    "AL Central": [
        ("CWS", 75, 72, "--", "--", "L4", "3-7", "+35"),
        ("CLE", 75, 73, "0.5", "--", "W1", "5-5", "-13"),
        ("MIN", 69, 78, "6", "5.5", "L2", "4-6", "-56"),
        ("DET", 68, 79, "7", "6.5", "W2", "5-5", "+59"),
        ("KCR", 66, 82, "9.5", "9", "W2", "4-6", "-87"),
    ],
    "AL West": [
        ("HOU", 75, 73, "--", "--", "L1", "5-5", "-42"),
        ("TEX", 72, 76, "3", "3", "L3", "4-6", "-49"),
        ("SEA", 69, 79, "6", "6", "L1", "5-5", "-75"),
        ("ATH", 60, 88, "15", "15", "W2", "7-3", "-186"),
        ("LAA", 56, 91, "18.5", "18.5", "L1", "4-6", "-74"),
    ],
    "AL Wild Card": [
        ("NYY", 85, 62, "+10.5", "W4", "7-3", "+133", False),
        ("BOS", 80, 68, "+5", "L3", "5-5", "+81", False),
        ("CLE", 75, 73, "--", "W1", "5-5", "-13", True),
        ("TOR", 73, 75, "2", "L2", "5-5", "-42", False),
        ("TEX", 72, 76, "3", "L3", "4-6", "-49", False),
        ("BAL", 72, 76, "3", "W2", "3-7", "-24", False),
    ],
    "NL East": [
        ("ATL", 87, 61, "--", "--", "W2", "5-5", "+111"),
        ("PHI", 82, 66, "5", "+2.5", "L2", "4-6", "+36"),
        ("MIA", 72, 76, "15", "7.5", "L4", "3-7", "+3"),
        ("NYM", 68, 79, "18.5", "11", "L1", "7-3", "-42"),
        ("WSN", 68, 81, "19.5", "12", "W1", "3-7", "+1"),
    ],
    "NL Central": [
        ("MIL", 92, 56, "--", "--", "W4", "7-3", "+192"),
        ("CHC", 82, 66, "10", "+2.5", "W1", "4-6", "+138"),
        ("PIT", 74, 74, "18", "5.5", "L1", "7-3", "+26"),
        ("STL", 73, 75, "19", "6.5", "W1", "5-5", "-8"),
        ("CIN", 69, 78, "22.5", "10", "L4", "4-6", "-142"),
    ],
    "NL West": [
        ("LAD", 90, 57, "--", "--", "W8", "8-2", "+173"),
        ("SDP", 79, 68, "11", "--", "W5", "7-3", "+19"),
        ("ARI", 79, 69, "11.5", "0.5", "W1", "6-4", "+7"),
        ("SFG", 62, 86, "28.5", "17.5", "L1", "5-5", "-74"),
        ("COL", 55, 92, "35", "24", "L5", "3-7", "-158"),
    ],
    "NL Wild Card": [
        ("PHI", 82, 66, "+2.5", "L2", "4-6", "+36", False),
        ("CHC", 82, 66, "+2.5", "W1", "4-6", "+138", False),
        ("SDP", 79, 68, "--", "W5", "7-3", "+19", True),
        ("ARI", 79, 69, "0.5", "W1", "6-4", "+7", False),
        ("PIT", 74, 74, "5.5", "L1", "7-3", "+26", False),
        ("MIA", 72, 76, "7.5", "L4", "3-7", "+3", False),
    ],
}

UPCOMING = [
    ("COL", "DET", "Tanner Gordon vs. Andrew Sears", "1:10 PM ET", "2026-09-12T17:10:00Z", ""),
    ("NYM", "NYY", "Zac Thornton vs. Gerrit Cole", "1:35 PM ET", "2026-09-12T17:35:00Z", ""),
    ("PIT", "CHC", "Paul Skenes vs. Clay Holmes", "2:20 PM ET", "2026-09-12T18:20:00Z", ""),
    ("BAL", "TOR", "Kyle Bradish vs. Spencer Miles", "3:07 PM ET", "2026-09-12T19:07:00Z", ""),
    ("LAA", "WSN", "Walbert Ureña vs. Andrew Alvarez", "4:05 PM ET", "2026-09-12T20:05:00Z", ""),
    ("SDP", "SFG", "Michael King vs. Cesar Perdomo", "4:05 PM ET", "2026-09-12T20:05:00Z", ""),
    ("KCR", "BOS", "Randy Dobnak vs. Ranger Suárez", "4:10 PM ET", "2026-09-12T20:10:00Z", ""),
    ("CLE", "MIN", "Daniel Espino vs. Connor Prielipp", "4:10 PM ET", "2026-09-12T20:10:00Z", ""),
    ("LAD", "MIA", "Tyler Glasnow vs. Tyler Phillips", "4:10 PM ET", "2026-09-12T20:10:00Z", ""),
    ("HOU", "TBR", "Peter Lambert vs. Ian Seymour", "6:10 PM ET", "2026-09-12T22:10:00Z", ""),
    ("CIN", "MIL", "Brady Singer vs. TBD", "7:10 PM ET", "2026-09-12T23:10:00Z", ""),
    ("PHI", "ATL", "TBD vs. Tyler Mahle", "7:15 PM ET", "2026-09-12T23:15:00Z", ""),
    ("CWS", "STL", "Sean Newcomb vs. Kyle Leahy", "7:15 PM ET", "2026-09-12T23:15:00Z", ""),
    ("TEX", "ARI", "Kumar Rocker vs. Brandon Pfaadt", "8:10 PM ET", "2026-09-13T00:10:00Z", ""),
    ("SEA", "ATH", "Bryan Woo vs. Gage Jump", "9:40 PM ET", "2026-09-13T01:40:00Z", ""),
]

OFF_TONIGHT: list[str] = []

TEAM_SUMMARIES = {
    "CHC": "Your Cubs: Imanaga earned the win and Bregman homered in a 12–2 rout of Pittsburgh. Host the Pirates tonight.",
    "MIA": "Your Marlins: Lost 2–6 to the Dodgers; Tucker hit a grand slam in the seventh. Host Los Angeles tonight.",
    "SFG": "Your Giants: Lost 5–7 to San Diego after a five-run third by the Padres. Host San Diego tonight.",
    "NYM": "Your Mets: Lost 4–6 at the Yankees; Rodón struck out eight. At New York tonight.",
    "ATL": "Your Braves: Baldwin's walk-off double in the 11th beat Philadelphia 6–5. Host the Phillies tonight.",
    "PHI": "Your Phillies: Lost 5–6 in 11 at Atlanta; five back in the NL East. At Atlanta tonight.",
    "DET": "Your Tigers: Valdez and a four-run sixth beat Colorado 6–2. Host the Rockies tonight.",
    "CLE": "Your Guardians: Scored five in the ninth to beat Minnesota 5–2. At Minnesota tonight.",
    "LAA": "Your Angels: Lost 3–4 at Washington. At Washington tonight.",
    "PIT": "Your Pirates: Lost 2–12 at Chicago. At the Cubs tonight.",
    "MIL": "Your Brewers: Scored 20 to clinch a playoff berth and shut out Cincinnati. Host the Reds tonight.",
    "CIN": "Your Reds: Shut out 0–20 at Milwaukee. At Milwaukee tonight.",
    "BOS": "Your Red Sox: Lost 2–3 to Kansas City; Lugo outdueled Gray. Host the Royals tonight.",
    "BAL": "Your Orioles: Bassitt and a six-run second beat Toronto 7–4. At Toronto tonight.",
    "TBR": "Your Rays: Baker earned the win in a 3–1 victory over Houston. Host the Astros tonight.",
    "TEX": "Your Rangers: Lost 1–9 at Arizona. At Arizona tonight.",
    "MIN": "Your Twins: Bradley spun six scoreless on one hit but lost 2–5 to Cleveland. Host the Guardians tonight.",
    "CWS": "Your White Sox: Meidroth homered twice in a 3–7 loss at St. Louis. At St. Louis tonight.",
    "TOR": "Your Blue Jays: Lost 4–7 to Baltimore. Host the Orioles tonight.",
    "KCR": "Your Royals: Lugo struck out seven in a 3–2 win at Fenway. At Boston tonight.",
    "ARI": "Your Diamondbacks: Scored nine runs in the fifth and sixth to beat Texas 9–1. Host Texas tonight.",
    "HOU": "Your Astros: Lost 1–3 at Tampa Bay. At Tampa Bay tonight.",
    "NYY": "Your Yankees: Rodón and a Ben Rice homer beat the Mets 6–4. Host New York tonight.",
    "SDP": "Your Padres: A five-run third keyed a 7–5 win at San Francisco. At San Francisco tonight.",
    "STL": "Your Cardinals: Graceffo earned the win in a 7–3 victory over Chicago. Host the White Sox tonight.",
    "COL": "Your Rockies: Lost 2–6 at Detroit. At Detroit tonight.",
    "WSN": "Your Nationals: Cavalli fanned nine in a 4–3 win over the Angels. Host Los Angeles tonight.",
    "LAD": "Your Dodgers: Tucker's grand slam and Snell's eight strikeouts beat Miami 6–2. At Miami tonight.",
    "ATH": "Your Athletics: Walton's walk-off homer in the 11th beat Seattle 6–5. Host the Mariners tonight.",
    "SEA": "Your Mariners: Lost 5–6 in 11 at Oakland. At Oakland tonight.",
}

RACE_AL_RECAP = (
    "Seth Lugo outdueled Sonny Gray in a 3–2 Royals win at Fenway. Carlos Rodón struck out eight "
    "as the Yankees beat the Mets 6–4. Donovan Walton's walk-off homer in the 11th lifted the Athletics "
    "past Seattle 6–5."
)
RACE_AL_SINCE = "The Yankees are 7–3 in their last ten."
RACE_NL_RECAP = (
    "Milwaukee scored 20 runs to clinch a postseason berth and shut out Cincinnati. Kyle Tucker's grand "
    "slam powered the Dodgers to a 6–2 win at Miami. Drake Baldwin's walk-off double in the 11th beat "
    "Philadelphia 6–5."
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
    return m.group(1).replace("2026-09-10", ISSUE_DATE)


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
<title>Scorebook - Friday, September 11</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Friday, September 11" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Friday, September 11" />
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
  <p class="kicker">Friday night</p>
  <h1>Friday, September 11</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("brewers20")}
  <p class="cap">{CLIPS["brewers20"]["cap"]}</p>
{clip_html("tucker")}
  <p class="cap">{CLIPS["tucker"]["cap"]}</p>
{clip_html("baldwin")}
  <p class="cap">{CLIPS["baldwin"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="brewers20" required> Brewers score 20 to clinch</label>
      <label><input type="radio" name="play" value="tucker"> Kyle Tucker's grand slam</label>
      <label><input type="radio" name="play" value="baldwin"> Baldwin's walk-off double in 11</label>
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
{clip_html("clinch")}
  <p class="cap">{CLIPS["clinch"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Top of the fifth at American Family Field. Milwaukee already led 9–0 when Brice Turang launched a three-run homer and Garrett Mitchell followed with a two-run shot. Eight runs crossed in the frame — part of a 20–0 rout that clinched a postseason berth.</p>
{clip_html("brewers_fifth")}
  <p class="cap">{CLIPS["brewers_fifth"]["cap"]}</p>

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
      <p class="subn">Standings through Friday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
{al_tables}
    </div>

    <div class="panel-nl" id="nl-panel">
      <div class="recap" data-share-card="race-nl.png" data-share-text-src="share/race-nl.txt">
        <p class="subn">Last night</p>
        <p>{RACE_NL_RECAP}</p>
        <p class="subn">Since August 13</p>
        <p>{RACE_NL_SINCE}</p>
      </div>
      <p class="subn">Standings through Friday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
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
