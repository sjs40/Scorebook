#!/usr/bin/env python3
"""Generate /workspace/2026-09-12/index.html and share race text files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-12"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-09-11" / "index.html"
ISSUE_DATE = "2026-09-12"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Mariners pounded the Athletics 19–1 — franchise-largest margin — with five homers and 23 hits. "
    "Mets routed the Yankees 12–2 behind Lindor's two homers and five RBIs. "
    "Braves crushed the Phillies 12–2. Cubs edged the Pirates 4–3 at Wrigley."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/12"

CLIPS = {
    "mariners19": {
        "video": f"{MLB_CDN}/8dfd5e63-e2e7a3ba-c0bc0a1a-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "arroyo-wilson-shine-in-19-1-mariners-win",
        "cap": (
            "Michael Arroyo homered in his first big-league at-bat and Cole Young drove in five. "
            "Mariners 19, Athletics 1 — Seattle's largest margin of victory in franchise history."
        ),
    },
    "lindor": {
        "video": f"{MLB_CDN}/2238cf11-0ce2800c-e3b5d903-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "francisco-lindor-collects-two-home-runs",
        "cap": (
            "Francisco Lindor: two homers including a grand slam, five RBIs on a 3-for-5 night. "
            "Mets 12, Yankees 2 — New York scored five in the eighth alone."
        ),
    },
    "harris": {
        "video": f"{MLB_CDN}/443288c6-63060c87-90abe1c6-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "michael-harris-ii-s-three-run-home-run-25",
        "cap": (
            "Michael Harris II: four hits and a three-run homer in an eight-run fourth. "
            "Braves 12, Phillies 2 — Atlanta has won three straight."
        ),
    },
    "mariners_hrs": {
        "video": f"{MLB_CDN}/d135d4bf-49e63e53-ff624613-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "mariners-crush-five-home-runs-vs-athletics",
        "cap": (
            "Five Mariners homers — Arozarena, Young, Canzone, Crawford, and Arroyo. "
            "That's baseball — Seattle scored 19 and Oakland scored one."
        ),
    },
    "rangers_fifth": {
        "video": f"{MLB_CDN}/a7b702e3-ef5f3976-9a65c869-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "rangers-score-six-runs-in-the-5th-to-power-6-2-win",
        "cap": (
            "Six runs in the fifth — Langford homered and Duran's two-run single capped the frame. "
            "Rangers 6, Diamondbacks 2."
        ),
    },
    "cubs_win": {
        "video": f"{MLB_CDN}/6ddf293d-8c0797a8-8e5aab68-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "michael-busch-pedro-ramirez-power-cubs-to-4-3-win",
        "cap": (
            "Pedro Ramírez homered and Ryan Rolison earned the win. "
            "Cubs 4, Pirates 3 — Chicago took the series opener at Wrigley."
        ),
    },
}

PITCHERS = [
    ("Andrew Alvarez", "WSN", 69, "7.0", 1, 0, 4, 8, "LAA"),
    ("Ranger Suárez", "BOS", 65, "7.0", 5, 1, 0, 8, "KCR"),
    ("Bryan Woo", "SEA", 62, "6.0", 3, 0, 2, 5, "ATH"),
    ("Ian Seymour", "TBR", 60, "6.0", 4, 2, 1, 10, "HOU"),
]

HITTERS = [
    ("Francisco Lindor", "NYM", 9, 5, 3, 2, 2, 5, 0),
    ("Garrett Mitchell", "MIL", 8, 5, 4, 2, 1, 4, 1),
    ("Michael Harris II", "ATL", 7, 5, 4, 1, 1, 3, 1),
    ("Michael Arroyo", "SEA", 7, 4, 3, 2, 1, 3, 0),
    ("Hao-Yu Lee", "DET", 7, 5, 3, 3, 0, 3, 0),
    ("Cole Young", "SEA", 6, 6, 3, 1, 1, 5, 0),
    ("Juan Brito", "CIN", 6, 4, 3, 1, 1, 3, 0),
    ("Luis Torrens", "NYM", 6, 4, 2, 2, 1, 3, 0),
]

# away, home, away_score, home_score, away_innings, home_innings, away_h, away_e, home_h, home_e, note
GAMES = [
    ("COL", "DET", 7, 11, [0, 0, 3, 1, 0, 2, 0, 1, 0], [0, 0, 2, 2, 0, 0, 0, 7, 0], 12, 0, 18, 2, "W Beau Brieske · L Jaden Hill"),
    ("NYM", "NYY", 12, 2, [1, 2, 1, 0, 1, 0, 1, 5, 1], [0, 0, 0, 1, 0, 1, 0, 0, 0], 14, 0, 7, 0, "W Zac Thornton · L Gerrit Cole"),
    ("PIT", "CHC", 3, 4, [0, 0, 0, 0, 0, 3, 0, 0, 0], [1, 0, 1, 0, 0, 0, 0, 2, 0], 6, 0, 5, 1, "W Ryan Rolison · L Gregory Soto · S Ryan Zeferjahn"),
    ("BAL", "TOR", 3, 7, [0, 0, 0, 1, 0, 0, 2, 0, 0], [2, 0, 3, 0, 0, 1, 1, 0, 0], 6, 0, 11, 3, "W Spencer Arrighetti · L Kyle Bradish"),
    ("LAA", "WSN", 5, 6, [0, 0, 0, 0, 0, 0, 0, 3, 2, 0], [1, 3, 0, 0, 0, 0, 0, 0, 1, 1], 4, 2, 11, 1, "W Jack Sinclair · L José Fermin"),
    ("SDP", "SFG", 7, 6, [0, 2, 1, 1, 1, 1, 1, 0, 0], [2, 1, 0, 0, 0, 0, 0, 3, 0], 13, 0, 8, 1, "W Michael King · L Cesar Perdomo · S Mason Miller"),
    ("KCR", "BOS", 1, 5, [0, 0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 2, 1, 1, 0], 5, 0, 10, 1, "W Ranger Suárez · L Randy Dobnak"),
    ("CLE", "MIN", 3, 4, [0, 1, 0, 0, 2, 0, 0, 0, 0], [0, 0, 4, 0, 0, 0, 0, 0, 0], 5, 0, 7, 0, "W Connor Prielipp · L Franco Aleman · S A.J. Minter"),
    ("LAD", "MIA", 3, 4, [2, 0, 0, 0, 0, 0, 0, 0, 1], [0, 3, 0, 0, 1, 0, 0, 0, 0], 4, 1, 7, 0, "W Cade Gibson · L Tyler Glasnow · S Pete Fairbanks"),
    ("HOU", "TBR", 2, 3, [1, 0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 2, 0, 1, 0, 0], 5, 0, 7, 0, "W Tyler Wells · L Peter Lambert · S Bryan Baker"),
    ("CIN", "MIL", 9, 13, [0, 1, 1, 3, 0, 0, 0, 4, 0], [4, 0, 1, 3, 5, 0, 0, 0, 0], 14, 1, 14, 0, "W Chad Patrick · L Brady Singer"),
    ("PHI", "ATL", 2, 12, [1, 0, 0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 8, 0, 1, 0, 3, 0], 7, 2, 13, 0, "W Tyler Mahle · L Brooks Raley"),
    ("CWS", "STL", 6, 5, [0, 0, 0, 1, 3, 0, 0, 0, 2], [0, 3, 0, 1, 0, 0, 0, 1, 0], 6, 2, 8, 1, "W Jordan Hicks · L Riley O'Brien · S Bryan Hudson"),
    ("TEX", "ARI", 6, 2, [0, 0, 0, 0, 6, 0, 0, 0, 0], [0, 0, 1, 0, 0, 1, 0, 0, 0], 13, 0, 6, 0, "W Robert Garcia · L Brandon Pfaadt"),
    ("SEA", "ATH", 19, 1, [2, 3, 0, 2, 2, 0, 3, 4, 3], [0, 0, 1, 0, 0, 0, 0, 0, 0], 23, 1, 5, 1, "W Bryan Woo · L Gage Jump"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 89, 59, "--", "--", "W2", "6-4", "+59"),
        ("NYY", 85, 63, "4", "+10.5", "L1", "7-3", "+123"),
        ("BOS", 81, 68, "8.5", "+6", "W1", "6-4", "+85"),
        ("TOR", 74, 75, "15.5", "1", "W1", "6-4", "-38"),
        ("BAL", 72, 77, "17.5", "3", "L1", "3-7", "-28"),
    ],
    "AL Central": [
        ("CWS", 76, 72, "--", "--", "W1", "3-7", "+36"),
        ("CLE", 75, 74, "1.5", "--", "L1", "5-5", "-14"),
        ("MIN", 70, 78, "6", "4.5", "W1", "4-6", "-55"),
        ("DET", 69, 79, "7", "5.5", "W3", "6-4", "+63"),
        ("KCR", 66, 83, "10.5", "9", "L1", "4-6", "-91"),
    ],
    "AL West": [
        ("HOU", 75, 74, "--", "--", "L2", "5-5", "-43"),
        ("TEX", 73, 76, "2", "2", "W1", "4-6", "-45"),
        ("SEA", 70, 79, "5", "5", "W1", "5-5", "-57"),
        ("ATH", 60, 89, "15", "15", "L1", "7-3", "-204"),
        ("LAA", 56, 92, "18.5", "18.5", "L2", "3-7", "-75"),
    ],
    "AL Wild Card": [
        ("NYY", 85, 63, "+10.5", "L1", "7-3", "+123", False),
        ("BOS", 81, 68, "+6", "W1", "6-4", "+85", False),
        ("CLE", 75, 74, "--", "L1", "5-5", "-14", True),
        ("TOR", 74, 75, "1", "W1", "6-4", "-38", False),
        ("TEX", 73, 76, "2", "W1", "4-6", "-45", False),
        ("BAL", 72, 77, "3", "L1", "3-7", "-28", False),
    ],
    "NL East": [
        ("ATL", 88, 61, "--", "--", "W3", "6-4", "+121"),
        ("PHI", 82, 67, "6", "+1.5", "L3", "3-7", "+26"),
        ("MIA", 73, 76, "15", "7.5", "W1", "3-7", "+4"),
        ("NYM", 69, 79, "18.5", "11", "W1", "7-3", "-32"),
        ("WSN", 69, 81, "19.5", "12", "W2", "3-7", "+2"),
    ],
    "NL Central": [
        ("MIL", 93, 56, "--", "--", "W5", "7-3", "+196"),
        ("CHC", 83, 66, "10", "+2.5", "W2", "5-5", "+139"),
        ("PIT", 74, 75, "19", "6.5", "L2", "6-4", "+25"),
        ("STL", 73, 76, "20", "7.5", "L1", "4-6", "-9"),
        ("CIN", 69, 79, "23.5", "11", "L5", "4-6", "-146"),
    ],
    "NL West": [
        ("LAD", 90, 58, "--", "--", "L1", "8-2", "+172"),
        ("SDP", 80, 68, "10", "--", "W6", "7-3", "+20"),
        ("ARI", 79, 70, "11.5", "1.5", "L1", "6-4", "+3"),
        ("SFG", 62, 87, "28.5", "18.5", "L2", "5-5", "-75"),
        ("COL", 55, 93, "35", "25", "L6", "3-7", "-162"),
    ],
    "NL Wild Card": [
        ("CHC", 83, 66, "+2.5", "W2", "5-5", "+139", False),
        ("PHI", 82, 67, "+1.5", "L3", "3-7", "+26", False),
        ("SDP", 80, 68, "--", "W6", "7-3", "+20", True),
        ("ARI", 79, 70, "1.5", "L1", "6-4", "+3", False),
        ("PIT", 74, 75, "6.5", "L2", "6-4", "+25", False),
        ("MIA", 73, 76, "7.5", "W1", "3-7", "+4", False),
    ],
}

UPCOMING = [
    ("COL", "DET", "Gabriel Hughes vs. Jackson Jobe", "12:10 PM ET", "2026-09-13T16:10:00Z", ""),
    ("LAA", "WSN", "Grayson Rodriguez vs. Jake Irvin", "1:35 PM ET", "2026-09-13T17:35:00Z", ""),
    ("PHI", "ATL", "Andrew Painter vs. Grant Holmes", "1:35 PM ET", "2026-09-13T17:35:00Z", ""),
    ("NYM", "NYY", "Christian Scott vs. Cam Schlittler", "1:35 PM ET", "2026-09-13T17:35:00Z", ""),
    ("BAL", "TOR", "Trevor Rogers vs. Dylan Cease", "1:37 PM ET", "2026-09-13T17:37:00Z", ""),
    ("HOU", "TBR", "Hayden Wesneski vs. Freddy Peralta", "1:40 PM ET", "2026-09-13T17:40:00Z", ""),
    ("LAD", "MIA", "Emmet Sheehan vs. Eury Pérez", "1:40 PM ET", "2026-09-13T17:40:00Z", ""),
    ("CLE", "MIN", "Tanner Bibee vs. TBD", "2:10 PM ET", "2026-09-13T18:10:00Z", ""),
    ("CIN", "MIL", "Chase Burns vs. Robert Gasser", "2:10 PM ET", "2026-09-13T18:10:00Z", ""),
    ("CWS", "STL", "TBD vs. Michael McGreevy", "2:15 PM ET", "2026-09-13T18:15:00Z", ""),
    ("PIT", "CHC", "Bubba Chandler vs. Matthew Boyd", "2:20 PM ET", "2026-09-13T18:20:00Z", ""),
    ("KCR", "BOS", "Noah Cameron vs. Payton Tolle", "3:05 PM ET", "2026-09-13T19:05:00Z", ""),
    ("SEA", "ATH", "Bryce Miller vs. Jacob Lopez", "4:05 PM ET", "2026-09-13T20:05:00Z", ""),
    ("TEX", "ARI", "Cal Quantrill vs. Eduardo Rodriguez", "4:10 PM ET", "2026-09-13T20:10:00Z", ""),
    ("SDP", "SFG", "Nick Pivetta vs. Logan Webb", "7:20 PM ET", "2026-09-13T23:20:00Z", ""),
]

OFF_TONIGHT: list[str] = []

TEAM_SUMMARIES = {
    "CHC": "Your Cubs: Rolison earned the win in a 4–3 victory over Pittsburgh. Host the Pirates today.",
    "MIA": "Your Marlins: Gibson and Fairbanks beat the Dodgers 4–3. Host Los Angeles today.",
    "SFG": "Your Giants: Lost 6–7 to San Diego after a three-run eighth by the Padres. Host San Diego tonight.",
    "NYM": "Your Mets: Lindor homered twice and drove in five in a 12–2 rout at Yankee Stadium. At New York today.",
    "ATL": "Your Braves: Harris went 4-for-5 and Mahle earned the win in a 12–2 rout of Philadelphia. Host the Phillies today.",
    "PHI": "Your Phillies: Lost 2–12 at Atlanta; six back in the NL East. At Atlanta today.",
    "DET": "Your Tigers: An eight-run eighth keyed an 11–7 win over Colorado. Host the Rockies today.",
    "CLE": "Your Guardians: Lost 3–4 to Minnesota. At Minnesota today.",
    "LAA": "Your Angels: Lost 5–6 in 10 at Washington. At Washington today.",
    "PIT": "Your Pirates: Lost 3–4 at Chicago. At the Cubs today.",
    "MIL": "Your Brewers: Mitchell went 4-for-5 in a 13–9 win over Cincinnati. Host the Reds today.",
    "CIN": "Your Reds: Scored nine but lost 9–13 at Milwaukee. At Milwaukee today.",
    "BOS": "Your Red Sox: Suárez spun seven strong innings in a 5–1 win over Kansas City. Host the Royals today.",
    "BAL": "Your Orioles: Lost 3–7 at Toronto. At Toronto today.",
    "TBR": "Your Rays: Wells and Baker beat Houston 3–2. Host the Astros today.",
    "TEX": "Your Rangers: Scored six in the fifth in a 6–2 win at Arizona. At Arizona today.",
    "MIN": "Your Twins: Prielipp earned the win in a 4–3 victory over Cleveland. Host the Guardians today.",
    "CWS": "Your White Sox: Hicks earned the save in a 6–5 win at St. Louis. At St. Louis today.",
    "TOR": "Your Blue Jays: Arrighetti and seven runs beat Baltimore 7–3. Host the Orioles today.",
    "KCR": "Your Royals: Lost 1–5 at Fenway. At Boston today.",
    "ARI": "Your Diamondbacks: Lost 2–6 to Texas. Host Texas today.",
    "HOU": "Your Astros: Lost 2–3 at Tampa Bay. At Tampa Bay today.",
    "NYY": "Your Yankees: Lost 2–12 to the Mets; Cole took the loss. Host New York today.",
    "SDP": "Your Padres: King outdueled San Francisco 7–6. At San Francisco tonight.",
    "STL": "Your Cardinals: Lost 5–6 to Chicago. Host the White Sox today.",
    "COL": "Your Rockies: Lost 7–11 at Detroit. At Detroit today.",
    "WSN": "Your Nationals: Alvarez fanned eight in seven scoreless on one hit in a 6–5 win over the Angels. Host Los Angeles today.",
    "LAD": "Your Dodgers: Lost 3–4 at Miami. At Miami today.",
    "ATH": "Your Athletics: Lost 19–1 to Seattle; Woo spun six scoreless. Host the Mariners today.",
    "SEA": "Your Mariners: Pounded Oakland 19–1 with five homers and 23 hits. At Oakland today.",
}

RACE_AL_RECAP = (
    "The Mariners scored 19 runs in a franchise-record rout of the Athletics. "
    "Francisco Lindor homered twice as the Mets routed the Yankees 12–2. "
    "Tyler Wells and Bryan Baker edged Houston 3–2 as Tampa Bay won its second straight."
)
RACE_AL_SINCE = "The Mariners are 5–5 in their last ten."
RACE_NL_RECAP = (
    "Michael Harris II and Tyler Mahle keyed a 12–2 Braves rout of Philadelphia. "
    "Milwaukee outscored Cincinnati 13–9 behind Garrett Mitchell's four hits. "
    "The Cubs edged Pittsburgh 4–3 at Wrigley."
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
    return m.group(1).replace("2026-09-11", ISSUE_DATE)


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
<title>Scorebook - Saturday, September 12</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Saturday, September 12" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Saturday, September 12" />
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
  <p class="kicker">Saturday night</p>
  <h1>Saturday, September 12</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("mariners19")}
  <p class="cap">{CLIPS["mariners19"]["cap"]}</p>
{clip_html("lindor")}
  <p class="cap">{CLIPS["lindor"]["cap"]}</p>
{clip_html("harris")}
  <p class="cap">{CLIPS["harris"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="mariners19" required> Mariners' 19-run rout</label>
      <label><input type="radio" name="play" value="lindor"> Lindor's two-homer game</label>
      <label><input type="radio" name="play" value="harris"> Harris II's four-hit night</label>
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
{clip_html("mariners_hrs")}
  <p class="cap">{CLIPS["mariners_hrs"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Top of the fifth at Chase Field. Texas already trailed 1–0 when the Rangers scored six — Langford homered and Ezequiel Duran's two-run single capped the frame. Rangers 6, Diamondbacks 2.</p>
{clip_html("rangers_fifth")}
  <p class="cap">{CLIPS["rangers_fifth"]["cap"]}</p>

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
      <p class="subn">Standings through Saturday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
{al_tables}
    </div>

    <div class="panel-nl" id="nl-panel">
      <div class="recap" data-share-card="race-nl.png" data-share-text-src="share/race-nl.txt">
        <p class="subn">Last night</p>
        <p>{RACE_NL_RECAP}</p>
        <p class="subn">Since August 13</p>
        <p>{RACE_NL_SINCE}</p>
      </div>
      <p class="subn">Standings through Saturday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
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
