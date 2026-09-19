#!/usr/bin/env python3
"""Generate /workspace/2026-09-18/index.html and share race text files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-18"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-09-17" / "index.html"
ISSUE_DATE = "2026-09-18"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Mookie Betts homered twice and the Dodgers scored four in the eighth in an 8–2 win at San Francisco. "
    "The Yankees scored five in the first in a 9–2 win at Arizona. "
    "Detroit rallied with five in the eighth for an 11–8 win at Chicago. "
    "Connor Prielipp shut out the Angels on two hits over seven in a 3–0 Twins win."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/18"

CLIPS = {
    "betts_two_homers": {
        "video": f"{MLB_CDN}/a71f8a13-218ac306-715aa82b-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "mookie-betts-two-homer-game-x2528",
        "cap": (
            "Mookie Betts went 3-for-4 with two homers and three RBIs — Los Angeles scored four in the eighth. "
            "Dodgers 8, Giants 2."
        ),
    },
    "yankees_five_run": {
        "video": f"{MLB_CDN}/0f6acc40-5f8974dc-31c41409-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "five-run-1st-inning-leads-yankees-to-9-2-win",
        "cap": (
            "Five runs in the first keyed a 9–2 rout — Ben Rice homered and George Lombard Jr. drove in two. "
            "Yankees 9, Diamondbacks 2."
        ),
    },
    "prielipp_shutout": {
        "video": f"{MLB_CDN}/d8099c6e-b9c77e8c-175c8990-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "connor-prielipp-s-strong-start-leads-twins-to-3-0-win",
        "cap": (
            "Connor Prielipp: seven scoreless innings, two hits, and eight strikeouts. "
            "Twins 3, Angels 0."
        ),
    },
    "white_sox_six_run_first": {
        "video": f"{MLB_CDN}/ed4be033-0e7ab98d-7c08c831-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "white-sox-offense-erupts-for-six-run-1st-inning",
        "cap": (
            "Chicago scored six in the first — and still lost 11–8 when Detroit put up five in the eighth. "
            "That's baseball."
        ),
    },
    "dodgers_four_homer_8th": {
        "video": f"{MLB_CDN}/1e8693c0-56ae0172-432f55d4-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "dodgers-hit-back-to-back-homers-twice-in-the-8th",
        "cap": (
            "Los Angeles hit back-to-back homers twice — Betts, Tucker, Smith, and Muncy all went deep. "
            "Dodgers 8, Giants 2."
        ),
    },
}

PITCHERS = [
    ("Connor Prielipp", "MIN", 69, "7.0", 2, 0, 2, 8, "LAA"),
    ("Joey Cantillo", "CLE", 64, "6.0", 2, 0, 1, 5, "ATH"),
    ("Tyler Glasnow", "LAD", 60, "6.0", 3, 2, 2, 10, "SFG"),
    ("Tyler Mahle", "ATL", 59, "6.0", 3, 1, 1, 6, "HOU"),
]

HITTERS = [
    ("Mookie Betts", "LAD", 9, 4, 3, 2, 2, 3, 0),
    ("Hao-Yu Lee", "DET", 8, 5, 4, 2, 1, 3, 0),
    ("Juan Soto", "NYM", 7, 5, 3, 2, 1, 3, 0),
    ("Ben Rice", "NYY", 7, 3, 2, 2, 1, 2, 0),
    ("Edmundo Sosa", "PHI", 7, 3, 3, 2, 1, 1, 0),
    ("Miguel Vargas", "CWS", 6, 5, 2, 2, 1, 3, 0),
    ("Michael Harris II", "ATL", 6, 5, 3, 1, 1, 2, 0),
    ("Matt Olson", "ATL", 6, 5, 3, 1, 1, 2, 0),
]

GAMES = [
    ("CHC", "CIN", 4, 6, [0, 1, 1, 2, 0, 0, 0, 0, 0], [2, 0, 1, 0, 0, 3, 0, 0], 9, 1, 8, 0, "W Julian Aguiar · L Clay Holmes · S Emilio Pagán"),
    ("KCR", "PIT", 5, 8, [1, 0, 3, 1, 0, 0, 0, 0, 0], [0, 0, 2, 2, 1, 0, 3, 0], 8, 2, 15, 0, "W Yohan Ramírez · L Nate Pearson · S Gregory Soto"),
    ("MIL", "BAL", 6, 5, [0, 3, 0, 0, 0, 0, 0, 0, 2, 1], [0, 0, 3, 0, 0, 0, 0, 0, 2, 0], 10, 0, 12, 0, "W Trevor Megill · L Grant Wolfram · S Chad Patrick"),
    ("ATH", "CLE", 3, 5, [3, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 3, 1, 1, 0, 0], 3, 0, 10, 0, "W Joey Cantillo · L Scott Blewett · S Cade Smith"),
    ("BOS", "TBR", 4, 2, [1, 2, 1, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0, 0, 1], 9, 0, 5, 1, "W Ranger Suarez · L Ian Seymour · S Erik Miller"),
    ("PHI", "NYM", 3, 6, [0, 1, 0, 0, 0, 1, 1, 0, 0], [3, 0, 0, 0, 0, 3, 0, 0], 6, 0, 13, 0, "W Zac Thornton · L Tim Mayza · S Dedniel Núñez"),
    ("DET", "CWS", 11, 8, [1, 0, 1, 0, 3, 1, 0, 5, 0], [6, 0, 2, 0, 0, 0, 0, 0, 0], 16, 2, 7, 0, "W Drew Sommers · L Sean Newcomb · S Kenley Jansen"),
    ("TOR", "TEX", 1, 7, [0, 0, 0, 0, 1, 0, 0, 0, 0], [0, 4, 0, 0, 1, 1, 0, 1], 5, 3, 8, 0, "W Trevor Williams · L Dylan Cease"),
    ("SEA", "COL", 5, 4, [3, 0, 0, 0, 0, 0, 1, 0, 1], [1, 0, 0, 1, 0, 2, 0, 0, 0], 9, 1, 15, 0, "W Carlos Vargas · L Jordan Romano · S Andrés Muñoz"),
    ("ATL", "HOU", 6, 2, [0, 0, 0, 2, 0, 0, 2, 0, 2], [0, 0, 0, 1, 0, 0, 0, 1, 0], 11, 0, 5, 1, "W Tyler Mahle · L Peter Lambert"),
    ("WSN", "STL", 9, 1, [3, 0, 4, 1, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 0], 7, 0, 7, 3, "W Cade Cavalli · L Kyle Leahy"),
    ("MIN", "LAA", 3, 0, [2, 0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], 9, 0, 4, 1, "W Connor Prielipp · L Grayson Rodriguez · S Travis Adams"),
    ("MIA", "SDP", 2, 8, [0, 0, 1, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 6, 0, 0, 2], 10, 1, 12, 0, "W Nick Pivetta · L Cade Gibson"),
    ("NYY", "ARI", 9, 2, [5, 0, 1, 0, 0, 1, 2, 0, 0], [0, 2, 0, 0, 0, 0, 0, 0, 0], 8, 0, 7, 2, "W Gerrit Cole · L Eduardo Rodriguez"),
    ("SFG", "LAD", 2, 8, [0, 1, 1, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 1, 1, 0, 5], 5, 0, 11, 0, "W Tyler Glasnow · L Jason Foley"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 93, 60, "--", "--", "L1", "8-2", "+78"),
        ("NYY", 89, 64, "4.0", "+11.5", "W1", "8-2", "+143"),
        ("BOS", 84, 70, "9.5", "+6.0", "W2", "5-5", "+85"),
        ("TOR", 76, 78, "17.5", "2.0", "L1", "4-6", "-43"),
        ("BAL", 75, 79, "18.5", "3.0", "L1", "6-4", "-27"),
    ],
    "AL Central": [
        ("CLE", 79, 75, "--", "--", "W3", "6-4", "-5"),
        ("CWS", 78, 76, "1.0", "--", "L1", "3-7", "+33"),
        ("DET", 73, 81, "6.0", "5.0", "W1", "7-3", "+77"),
        ("MIN", 72, 82, "7.0", "6.0", "W1", "4-6", "-71"),
        ("KCR", 67, 87, "12.0", "11.0", "L2", "3-7", "-100"),
    ],
    "AL West": [
        ("HOU", 77, 77, "--", "--", "L1", "4-6", "-54"),
        ("TEX", 77, 77, "--", "1.0", "W1", "6-4", "-33"),
        ("SEA", 72, 82, "5.0", "6.0", "W2", "5-5", "-55"),
        ("ATH", 61, 93, "16.0", "17.0", "L4", "4-6", "-216"),
        ("LAA", 59, 95, "18.0", "19.0", "L1", "5-5", "-80"),
    ],
    "AL Wild Card": [
        ("NYY", 89, 64, "+11.5", "W1", "8-2", "+143", False),
        ("BOS", 84, 70, "+6.0", "W2", "5-5", "+85", False),
        ("CWS", 78, 76, "--", "L1", "3-7", "+33", True),
        ("TEX", 77, 77, "1.0", "W1", "6-4", "-33", False),
        ("TOR", 76, 78, "2.0", "L1", "4-6", "-43", False),
        ("BAL", 75, 79, "3.0", "L1", "6-4", "-27", False),
    ],
    "NL East": [
        ("ATL", 90, 64, "--", "--", "W1", "5-5", "+115"),
        ("PHI", 85, 69, "5.0", "--", "L1", "4-6", "+31"),
        ("MIA", 76, 78, "14.0", "9.0", "L1", "4-6", "+2"),
        ("WSN", 72, 82, "18.0", "13.0", "W1", "5-5", "+11"),
        ("NYM", 70, 84, "20.0", "15.0", "W1", "4-6", "-43"),
    ],
    "NL Central": [
        ("MIL", 96, 58, "--", "--", "W1", "8-2", "+198"),
        ("CHC", 85, 69, "11.0", "--", "L1", "4-6", "+141"),
        ("PIT", 77, 77, "19.0", "8.0", "W2", "6-4", "+27"),
        ("STL", 75, 79, "21.0", "10.0", "L3", "3-7", "-22"),
        ("CIN", 72, 82, "24.0", "13.0", "W1", "3-7", "-152"),
    ],
    "NL West": [
        ("LAD", 94, 60, "--", "--", "W2", "7-3", "+185"),
        ("SDP", 85, 69, "9.0", "--", "W3", "9-1", "+36"),
        ("ARI", 80, 74, "14.0", "5.0", "L3", "4-6", "-7"),
        ("SFG", 64, 90, "30.0", "21.0", "L1", "5-5", "-76"),
        ("COL", 56, 98, "38.0", "29.0", "L3", "1-9", "-178"),
    ],
    "NL Wild Card": [
        ("CHC", 85, 69, "--", "L1", "4-6", "+141", False),
        ("PHI", 85, 69, "--", "L1", "4-6", "+31", False),
        ("SDP", 85, 69, "--", "W3", "9-1", "+36", True),
        ("ARI", 80, 74, "5.0", "L3", "4-6", "-7", False),
        ("PIT", 77, 77, "8.0", "W2", "6-4", "+27", False),
        ("MIA", 76, 78, "9.0", "L1", "4-6", "+2", False),
    ],
}

UPCOMING = [
    ("DET", "CWS", "Jackson Jobe vs. Sean Burke", "2:10 PM ET", "2026-09-19T18:10:00Z", ""),
    ("MIL", "BAL", "Robert Gasser vs. Trevor Rogers", "4:05 PM ET", "2026-09-19T20:05:00Z", ""),
    ("BOS", "TBR", "TBD vs. Freddy Peralta", "4:10 PM ET", "2026-09-19T20:10:00Z", ""),
    ("PHI", "NYM", "Andrew Painter vs. Christian Scott", "4:10 PM ET", "2026-09-19T20:10:00Z", ""),
    ("ATH", "CLE", "Jacob Lopez vs. Tanner Bibee", "6:10 PM ET", "2026-09-19T22:10:00Z", ""),
    ("CHC", "CIN", "Matthew Boyd vs. Nick Lodolo", "6:40 PM ET", "2026-09-19T22:40:00Z", ""),
    ("KCR", "PIT", "Noah Cameron vs. Bubba Chandler", "6:40 PM ET", "2026-09-19T22:40:00Z", ""),
    ("TOR", "TEX", "José Soriano vs. Cal Quantrill", "7:05 PM ET", "2026-09-19T23:05:00Z", ""),
    ("ATL", "HOU", "Grant Holmes vs. Hayden Wesneski", "7:10 PM ET", "2026-09-19T23:10:00Z", ""),
    ("WSN", "STL", "Andrew Alvarez vs. Michael McGreevy", "7:15 PM ET", "2026-09-19T23:15:00Z", ""),
    ("SEA", "COL", "Bryce Miller vs. Jose Quintana", "8:10 PM ET", "2026-09-20T00:10:00Z", ""),
    ("NYY", "ARI", "Cam Schlittler vs. Brandon Pfaadt", "8:10 PM ET", "2026-09-20T00:10:00Z", ""),
    ("MIA", "SDP", "Eury Pérez vs. Casey Mize", "8:40 PM ET", "2026-09-20T00:40:00Z", ""),
    ("SFG", "LAD", "TBD vs. Tarik Skubal", "9:10 PM ET", "2026-09-20T01:10:00Z", ""),
    ("MIN", "LAA", "Joe Ryan vs. Reid Detmers", "9:38 PM ET", "2026-09-20T01:38:00Z", ""),
]

OFF_TONIGHT: list[str] = []

TEAM_SUMMARIES = {
    "CHC": "Your Cubs: Lost 4–6 at Cincinnati; Holmes took the loss. At Cincinnati tonight.",
    "CIN": "Your Reds: Won 6–4 over Chicago; Aguiar earned the win. Host Chicago tonight.",
    "KCR": "Your Royals: Lost 5–8 at Pittsburgh; Pearson took the loss. At Pittsburgh tonight.",
    "PIT": "Your Pirates: Won 8–5 over Kansas City; Ramírez earned the win. Host Kansas City tonight.",
    "MIL": "Your Brewers: Won 6–5 in 10 at Baltimore; Megill got the win. At Baltimore tonight.",
    "BAL": "Your Orioles: Lost 5–6 in 10 to Milwaukee; Wolfram took the loss. Host Milwaukee tonight.",
    "ATH": "Your Athletics: Lost 3–5 at Cleveland; Blewett took the loss. At Cleveland tonight.",
    "CLE": "Your Guardians: Won 5–3 over Oakland; Cantillo went six scoreless. Host Athletics tonight.",
    "BOS": "Your Red Sox: Won 4–2 at Tampa Bay; Suarez earned the win. At Tampa Bay tonight.",
    "TBR": "Your Rays: Lost 2–4 to Boston; Seymour took the loss. Host Boston tonight.",
    "PHI": "Your Phillies: Lost 3–6 at New York; Mayza took the loss. At New York tonight.",
    "NYM": "Your Mets: Won 6–3 over Philadelphia; Thornton earned the win. Host Philadelphia tonight.",
    "DET": "Your Tigers: Won 11–8 at Chicago; five in the eighth keyed the comeback. At Chicago tonight.",
    "CWS": "Your White Sox: Lost 8–11 to Detroit; six in the first wasn't enough. Host Detroit tonight.",
    "TOR": "Your Blue Jays: Lost 1–7 at Texas; Cease took the loss. At Texas tonight.",
    "TEX": "Your Rangers: Won 7–1 over Toronto; Williams earned the win. Host Toronto tonight.",
    "SEA": "Your Mariners: Won 5–4 at Colorado; Muñoz saved it. At Colorado tonight.",
    "COL": "Your Rockies: Lost 4–5 to Seattle; Romano took the loss. Host Seattle tonight.",
    "ATL": "Your Braves: Won 6–2 at Houston; Mahle went six innings. At Houston tonight.",
    "HOU": "Your Astros: Lost 2–6 to Atlanta; Lambert took the loss. Host Atlanta tonight.",
    "WSN": "Your Nationals: Won 9–1 at St. Louis; Cavalli earned the win. At St. Louis tonight.",
    "STL": "Your Cardinals: Lost 1–9 to Washington; Leahy took the loss. Host Washington tonight.",
    "MIN": "Your Twins: Won 3–0 at Los Angeles; Prielipp shut them out for seven. At Los Angeles tonight.",
    "LAA": "Your Angels: Lost 0–3 to Minnesota; Rodriguez took the loss. Host Minnesota tonight.",
    "MIA": "Your Marlins: Lost 2–8 at San Diego; Gibson took the loss. At San Diego tonight.",
    "SDP": "Your Padres: Won 8–2 over Miami; six in the fifth keyed the win. Host Miami tonight.",
    "NYY": "Your Yankees: Won 9–2 at Arizona; five-run first keyed it. At Arizona tonight.",
    "ARI": "Your Diamondbacks: Lost 2–9 to New York; Rodriguez took the loss. Host New York tonight.",
    "SFG": "Your Giants: Lost 2–8 at Los Angeles; Foley took the loss. At Los Angeles tonight.",
    "LAD": "Your Dodgers: Won 8–2 over San Francisco; Betts homered twice. Host San Francisco tonight.",
}

RACE_AL_RECAP = (
    "The Yankees scored five in the first in a 9–2 win at Arizona. "
    "Texas scored four in the second in a 7–1 win over Toronto. "
    "Boston won 4–2 at Tampa Bay behind Roman Anthony's leadoff homer."
)
RACE_AL_SINCE = "The Rays are 8–2 in their last ten."
RACE_NL_RECAP = (
    "Mookie Betts homered twice and the Dodgers scored four in the eighth in an 8–2 win at San Francisco. "
    "San Diego scored six in the fifth in an 8–2 win over Miami. "
    "Washington won 9–1 at St. Louis behind Cade Cavalli."
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
    return m.group(1).replace("2026-09-17", ISSUE_DATE)


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
<title>Scorebook - Friday, September 18</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Friday, September 18" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Friday, September 18" />
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
  <h1>Friday, September 18</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("betts_two_homers")}
  <p class="cap">{CLIPS["betts_two_homers"]["cap"]}</p>
{clip_html("yankees_five_run")}
  <p class="cap">{CLIPS["yankees_five_run"]["cap"]}</p>
{clip_html("prielipp_shutout")}
  <p class="cap">{CLIPS["prielipp_shutout"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="betts_two_homers" required> Betts's two-homer game</label>
      <label><input type="radio" name="play" value="yankees_five_run"> Yankees' five-run first</label>
      <label><input type="radio" name="play" value="prielipp_shutout"> Prielipp's shutout</label>
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
{clip_html("white_sox_six_run_first")}
  <p class="cap">{CLIPS["white_sox_six_run_first"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Bottom of the eighth at Dodger Stadium. Los Angeles led 4–2 when the Dodgers put up four — back-to-back homers twice, with Betts, Tucker, Smith, and Muncy all going deep. Dodgers 8, Giants 2.</p>
{clip_html("dodgers_four_homer_8th")}
  <p class="cap">{CLIPS["dodgers_four_homer_8th"]["cap"]}</p>

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
