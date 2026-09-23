#!/usr/bin/env python3
"""Generate /workspace/2026-09-22/index.html and share race text files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-22"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-09-21" / "index.html"
ISSUE_DATE = "2026-09-22"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Rays clinched the AL East with a 6–1 win in the nightcap — Drew Rasmussen struck out 11. "
    "Jared Jones spun seven one-hit innings in Pittsburgh's 2–0 shutout of St. Louis. "
    "White Sox and Royals combined for 25 runs in a 14–11 slugfest. "
    "CJ Abrams homered twice in Washington's 3–1 win at Detroit."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/22"

CLIPS = {
    "rays_clinch": {
        "video": f"{MLB_CDN}/ffb54a12-482a5efe-65f07282-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "rays-clinch-2026-al-east-title-with-6-1-win",
        "cap": (
            "Tampa Bay clinched the AL East — Drew Rasmussen struck out 11 in the nightcap. "
            "Rays 6, Yankees 1."
        ),
    },
    "jones_one_hitter": {
        "video": f"{MLB_CDN}/c3de80ed-9038700a-8933aa16-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "jared-jones-spins-seven-one-hit-innings-vs-cardinals",
        "cap": (
            "Jared Jones allowed one hit over seven — "
            "Pittsburgh's fifth straight win. Pirates 2, Cardinals 0."
        ),
    },
    "sox_slugfest": {
        "video": f"{MLB_CDN}/7b655295-c6cfdd6d-20a78d7b-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "randal-grichuck-goes-4-for-5-in-white-sox-win",
        "cap": (
            "Randal Grichuk went 4-for-5 with a homer — "
            "part of a 14–11 slugfest in Kansas City. White Sox 14, Royals 11."
        ),
    },
    "marlins_twelfth": {
        "video": f"{MLB_CDN}/99470df4-e0ef84ef-a9b44c70-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "griffin-conine-hits-go-ahead-single-in-marlins-win",
        "cap": (
            "Miami scored six in the 12th — after a 2–2 tie through 11. "
            "That's baseball."
        ),
    },
    "sox_seventh_inning": {
        "video": f"{MLB_CDN}/860b31d2-2b87f7bf-6ce7692e-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "whit-sox-rally-five-runs-in-the-7th-inning",
        "cap": (
            "Chicago put up five in the seventh — part of a 14-run night at Kauffman. "
            "White Sox 14, Royals 11."
        ),
    },
}

PITCHERS = [
    ("Jared Jones", "PIT", 85, "7.0", 1, 0, 0, 9, "STL"),
    ("Carlos Rodón", "NYY", 78, "8.0", 3, 0, 0, 8, "TBR"),
    ("Drew Rasmussen", "TBR", 76, "6.2", 1, 1, 3, 11, "NYY"),
    ("Michael Soroka", "ARI", 73, "7.0", 2, 1, 1, 9, "COL"),
]

HITTERS = [
    ("Randal Grichuk", "CWS", 9, 5, 4, 3, 1, 3, 0),
    ("CJ Abrams", "WSN", 8, 4, 2, 2, 2, 3, 0),
    ("Vinnie Pasquantino", "KCR", 7, 5, 3, 2, 1, 5, 0),
    ("Carlos Cortes", "ATH", 7, 2, 2, 2, 1, 3, 0),
    ("Nolan Arenado", "ARI", 7, 5, 3, 2, 1, 1, 0),
    ("Chase Meidroth", "CWS", 6, 4, 3, 1, 1, 5, 0),
    ("Brandon Marsh", "PHI", 6, 4, 2, 2, 1, 3, 0),
    ("Kyle Stowers", "MIA", 6, 4, 2, 2, 1, 2, 0),
]

GAMES = [
    ("TBR", "NYY", 0, 2, [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 2, 0, 0, 0, 0, 0], 3, 0, 5, 0, "W Carlos Rodón · L Nick Martinez · S David Bednar"),
    ("WSN", "DET", 3, 1, [0, 1, 0, 0, 0, 0, 2, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0, 0], 7, 0, 7, 0, "W Jackson Kent · L Drew Anderson · S Erik Tolman"),
    ("STL", "PIT", 0, 2, [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 1, 0, 0], 1, 1, 5, 0, "W Jared Jones · L Andre Pallante · S Gregory Soto"),
    ("MIL", "PHI", 4, 6, [0, 0, 0, 1, 0, 2, 0, 0, 1], [0, 2, 1, 0, 0, 0, 0, 3, 0], 6, 2, 8, 0, "W José Alvarado · L Colton Gordon · S Jhoan Duran"),
    ("CLE", "BOS", 3, 2, [0, 2, 0, 0, 0, 0, 0, 0, 1], [0, 1, 0, 0, 0, 0, 0, 1, 0], 12, 0, 8, 1, "W Hunter Gaddis · L Erik Miller · S Cade Smith"),
    ("TBR", "NYY", 6, 1, [0, 0, 1, 0, 0, 0, 3, 0, 2], [0, 0, 0, 0, 0, 0, 1, 0, 0], 11, 0, 3, 0, "W Drew Rasmussen · L Max Fried"),
    ("CIN", "ATL", 4, 0, [0, 0, 1, 0, 0, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], 10, 0, 7, 0, "W Brandon Williamson · L JR Ritchie"),
    ("CWS", "KCR", 14, 11, [2, 1, 3, 3, 0, 0, 5, 0, 0], [0, 0, 1, 2, 1, 0, 0, 3, 4], 13, 0, 13, 0, "W Noah Schultz · L Daniel Lynch IV"),
    ("MIA", "CHC", 8, 2, [0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 6], [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0], 11, 1, 7, 0, "W Josh Ekness · L Caleb Thielbar"),
    ("NYM", "TEX", 6, 3, [0, 0, 1, 1, 0, 3, 1, 0, 0], [0, 0, 1, 2, 0, 0, 0, 0, 0], 10, 1, 3, 1, "W Sean Manaea · L Nathan Eovaldi · S Kodai Senga"),
    ("ARI", "COL", 7, 2, [3, 0, 1, 1, 1, 0, 1, 0, 0], [0, 0, 2, 0, 0, 0, 0, 0, 0], 13, 2, 3, 1, "W Michael Soroka · L Kyle Freeland"),
    ("LAA", "ATH", 7, 9, [1, 0, 4, 0, 0, 1, 0, 0, 1], [0, 0, 0, 0, 0, 2, 3, 4, 0], 15, 1, 14, 0, "W Luis Medina · L Sam Bachman · S Hogan Harris"),
    ("HOU", "SEA", 7, 0, [1, 0, 3, 0, 0, 1, 0, 2, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], 12, 0, 4, 1, "W Miguel Ullola · L Logan Gilbert"),
    ("MIN", "SFG", 3, 2, [0, 0, 0, 0, 0, 2, 1, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 1], 6, 1, 6, 1, "W Taj Bradley · L Anthony Molina · S Jeff Hoffman"),
    ("SDP", "LAD", 0, 7, [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 4, 0, 1, 0, 1, 1, 0, 0], 5, 0, 9, 1, "W Justin Wrobleski · L Michael King"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 96, 61, "--", "--", "W1", "8-2", "+86"),
        ("NYY", 90, 67, "6.0", "+9.0", "L1", "5-5", "+134"),
        ("BOS", 84, 73, "12.0", "+3.0", "L3", "4-6", "+79"),
        ("TOR", 77, 80, "19.0", "4.0", "L1", "4-6", "-43"),
        ("BAL", 76, 81, "20.0", "5.0", "W1", "5-5", "-30"),
    ],
    "AL Central": [
        ("CLE", 82, 75, "--", "--", "W6", "8-2", "+3"),
        ("CWS", 81, 76, "1.0", "--", "W3", "6-4", "+45"),
        ("MIN", 74, 84, "8.5", "7.5", "W1", "4-6", "-66"),
        ("DET", 74, 84, "8.5", "7.5", "L1", "5-5", "+73"),
        ("KCR", 67, 90, "15.0", "14.0", "L5", "2-8", "-105"),
    ],
    "AL West": [
        ("HOU", 78, 79, "--", "--", "W1", "3-7", "-52"),
        ("TEX", 78, 79, "--", "3.0", "L2", "6-4", "-37"),
        ("SEA", 73, 84, "5.0", "8.0", "L1", "4-6", "-63"),
        ("ATH", 62, 95, "16.0", "19.0", "W1", "3-7", "-221"),
        ("LAA", 60, 97, "18.0", "21.0", "L2", "4-6", "-89"),
    ],
    "AL Wild Card": [
        ("NYY", 90, 67, "+9.0", "L1", "5-5", "+134", False),
        ("BOS", 84, 73, "+3.0", "L3", "4-6", "+79", False),
        ("CWS", 81, 76, "--", "W3", "6-4", "+45", True),
        ("TEX", 78, 79, "3.0", "L2", "6-4", "-37", False),
        ("TOR", 77, 80, "4.0", "L1", "4-6", "-43", False),
        ("BAL", 76, 81, "5.0", "W1", "5-5", "-30", False),
    ],
    "NL East": [
        ("ATL", 92, 65, "--", "--", "L1", "6-4", "+116"),
        ("PHI", 87, 70, "5.0", "--", "W2", "5-5", "+31"),
        ("MIA", 77, 80, "15.0", "10.0", "W1", "5-5", "+3"),
        ("WSN", 74, 84, "18.5", "13.5", "W1", "7-3", "+7"),
        ("NYM", 72, 85, "20.0", "15.0", "W1", "4-6", "-38"),
    ],
    "NL Central": [
        ("MIL", 98, 59, "--", "--", "L1", "7-3", "+200"),
        ("CHC", 87, 70, "11.0", "--", "L1", "6-4", "+146"),
        ("PIT", 80, 77, "18.0", "7.0", "W5", "6-4", "+31"),
        ("STL", 76, 81, "22.0", "11.0", "L1", "4-6", "-25"),
        ("CIN", 73, 84, "25.0", "14.0", "W1", "4-6", "-159"),
    ],
    "NL West": [
        ("LAD", 97, 60, "--", "--", "W5", "7-3", "+200"),
        ("SDP", 87, 70, "10.0", "--", "L1", "8-2", "+34"),
        ("ARI", 83, 74, "14.0", "4.0", "W3", "5-5", "+4"),
        ("SFG", 65, 93, "32.5", "22.5", "L1", "3-7", "-82"),
        ("COL", 57, 100, "40.0", "30.0", "L2", "2-8", "-182"),
    ],
    "NL Wild Card": [
        ("CHC", 87, 70, "--", "L1", "6-4", "+146", False),
        ("SDP", 87, 70, "--", "L1", "8-2", "+34", False),
        ("PHI", 87, 70, "--", "W2", "5-5", "+31", True),
        ("ARI", 83, 74, "4.0", "W3", "5-5", "+4", False),
        ("PIT", 80, 77, "7.0", "W5", "6-4", "+31", False),
        ("MIA", 77, 80, "10.0", "W1", "5-5", "+3", False),
    ],
}

UPCOMING = [
    ("WSN", "DET", "Richard Lovelady vs. Framber Valdez", "1:10 PM ET", "2026-09-23T17:10:00Z", ""),
    ("TOR", "BAL", "Max Scherzer vs. TBD", "1:35 PM ET", "2026-09-23T17:35:00Z", ""),
    ("TOR", "BAL", "TBD vs. TBD", "6:35 PM ET", "2026-09-23T22:35:00Z", "Game 2"),
    ("MIN", "SFG", "Connor Prielipp vs. Cesar Perdomo", "3:45 PM ET", "2026-09-23T19:45:00Z", ""),
    ("STL", "PIT", "Matthew Liberatore vs. Lake Bachar", "6:40 PM ET", "2026-09-23T22:40:00Z", ""),
    ("MIL", "PHI", "Logan Henderson vs. Aaron Nola", "6:40 PM ET", "2026-09-23T22:40:00Z", ""),
    ("TBR", "NYY", "Ian Seymour vs. Gerrit Cole", "7:05 PM ET", "2026-09-23T23:05:00Z", ""),
    ("CLE", "BOS", "Foster Griffin vs. Sonny Gray", "7:10 PM ET", "2026-09-23T23:10:00Z", ""),
    ("CIN", "ATL", "Andrew Abbott vs. Chris Sale", "7:15 PM ET", "2026-09-23T23:15:00Z", ""),
    ("CWS", "KCR", "Bryan Hudson vs. Seth Lugo", "7:40 PM ET", "2026-09-23T23:40:00Z", ""),
    ("MIA", "CHC", "Ryan Gusto vs. Kevin Gausman", "7:40 PM ET", "2026-09-23T23:40:00Z", ""),
    ("NYM", "TEX", "Nolan McLean vs. TBD", "8:05 PM ET", "2026-09-24T00:05:00Z", ""),
    ("ARI", "COL", "Merrill Kelly vs. Mason Adams", "8:40 PM ET", "2026-09-24T00:40:00Z", ""),
    ("LAA", "ATH", "Walbert Ureña vs. Jeffrey Springs", "9:40 PM ET", "2026-09-24T01:40:00Z", ""),
    ("SDP", "LAD", "Robbie Ray vs. Yoshinobu Yamamoto", "10:10 PM ET", "2026-09-24T02:10:00Z", ""),
    ("HOU", "SEA", "Ethan Pecko vs. George Kirby", "10:10 PM ET", "2026-09-24T02:10:00Z", ""),
]

OFF_TONIGHT: list[str] = []

TEAM_SUMMARIES = {
    "TBR": "Your Rays: Split the doubleheader at New York — lost 0–2, then clinched the AL East with a 6–1 win. At New York tonight.",
    "NYY": "Your Yankees: Split the doubleheader with Tampa Bay — Rodón shut out the Rays in Game 1, then lost 6–1 in the nightcap. Host Tampa Bay tonight.",
    "WSN": "Your Nationals: Won 3–1 at Detroit; Abrams homered twice. At Detroit tonight.",
    "DET": "Your Tigers: Lost 3–1 to Washington; Anderson took the loss. Host Washington tonight.",
    "STL": "Your Cardinals: Lost 0–2 at Pittsburgh; Pallante took the loss. At Pittsburgh tonight.",
    "PIT": "Your Pirates: Won 2–0 over St. Louis; Jones spun seven one-hit innings. Host St. Louis tonight.",
    "MIL": "Your Brewers: Lost 4–6 at Philadelphia; Gordon took the loss. At Philadelphia tonight.",
    "PHI": "Your Phillies: Won 6–4 over Milwaukee; Marsh homered. Host Milwaukee tonight.",
    "CLE": "Your Guardians: Won 3–2 at Boston; Gaddis earned the win. At Boston tonight.",
    "BOS": "Your Red Sox: Lost 3–2 to Cleveland; Miller took the loss. Host Cleveland tonight.",
    "CIN": "Your Reds: Won 4–0 at Atlanta; Williamson earned the win. At Atlanta tonight.",
    "ATL": "Your Braves: Lost 0–4 to Cincinnati; Ritchie took the loss. Host Cincinnati tonight.",
    "CWS": "Your White Sox: Won 14–11 at Kansas City; Grichuk went 4-for-5. At Kansas City tonight.",
    "KCR": "Your Royals: Lost 14–11 to Chicago; Lynch took the loss. Host White Sox tonight.",
    "MIA": "Your Marlins: Won 8–2 at Chicago in 12; scored six in the 12th. At Chicago tonight.",
    "CHC": "Your Cubs: Lost 2–8 to Miami in 12; Thielbar took the loss. Host Miami tonight.",
    "NYM": "Your Mets: Won 6–3 at Texas; Manaea earned the win. At Texas tonight.",
    "TEX": "Your Rangers: Lost 3–6 to New York; Eovaldi took the loss. Host New York tonight.",
    "ARI": "Your Diamondbacks: Won 7–2 at Colorado; Soroka earned the win. At Colorado tonight.",
    "COL": "Your Rockies: Lost 2–7 to Arizona; Freeland took the loss. Host Arizona tonight.",
    "LAA": "Your Angels: Lost 7–9 at Oakland; Bachman took the loss. At Oakland tonight.",
    "ATH": "Your Athletics: Won 9–7 over the Angels; Cortes homered. Host Angels tonight.",
    "HOU": "Your Astros: Won 7–0 at Seattle; Ullola earned the win. At Seattle tonight.",
    "SEA": "Your Mariners: Lost 0–7 to Houston; Gilbert took the loss. Host Houston tonight.",
    "MIN": "Your Twins: Won 3–2 at San Francisco; Bradley earned the win. At San Francisco tonight.",
    "SFG": "Your Giants: Lost 2–3 to Minnesota; Molina took the loss. Host Minnesota tonight.",
    "SDP": "Your Padres: Lost 0–7 at Los Angeles; King took the loss. At Los Angeles tonight.",
    "LAD": "Your Dodgers: Won 7–0 over San Diego; Wrobleski earned the win. Host San Diego tonight.",
    "TOR": "Your Blue Jays: Game at Baltimore postponed. At Baltimore tonight (doubleheader).",
    "BAL": "Your Orioles: Game against Toronto postponed. Host Toronto tonight (doubleheader).",
}

RACE_AL_RECAP = (
    "Tampa Bay clinched the AL East with a 6–1 win in the nightcap — Drew Rasmussen struck out 11. "
    "Carlos Rodón tossed eight scoreless in the opener. "
    "Chicago beat Kansas City 14–11; Randal Grichuk went 4-for-5."
)
RACE_AL_SINCE = "The Rays are 8–2 in their last ten."
RACE_NL_RECAP = (
    "Jared Jones spun seven one-hit innings in Pittsburgh's 2–0 shutout of St. Louis. "
    "CJ Abrams homered twice in Washington's 3–1 win at Detroit. "
    "Los Angeles shut out San Diego 7–0."
)
RACE_NL_SINCE = "The Dodgers are 7–3 in their last ten."


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
    return m.group(1).replace("2026-09-21", ISSUE_DATE)


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
<title>Scorebook - Tuesday, September 22</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Tuesday, September 22" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Tuesday, September 22" />
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
  <p class="kicker">Tuesday night</p>
  <h1>Tuesday, September 22</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("rays_clinch")}
  <p class="cap">{CLIPS["rays_clinch"]["cap"]}</p>
{clip_html("jones_one_hitter")}
  <p class="cap">{CLIPS["jones_one_hitter"]["cap"]}</p>
{clip_html("sox_slugfest")}
  <p class="cap">{CLIPS["sox_slugfest"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="rays_clinch" required> Rays clinch AL East</label>
      <label><input type="radio" name="play" value="jones_one_hitter"> Jones' one-hitter</label>
      <label><input type="radio" name="play" value="sox_slugfest"> White Sox slugfest</label>
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
{clip_html("marlins_twelfth")}
  <p class="cap">{CLIPS["marlins_twelfth"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Top of the seventh at Kauffman Stadium. Chicago had already scored nine when the White Sox put up five more — part of a 14-run night. White Sox 14, Royals 11.</p>
{clip_html("sox_seventh_inning")}
  <p class="cap">{CLIPS["sox_seventh_inning"]["cap"]}</p>

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
      <p class="subn">Standings through Tuesday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
{al_tables}
    </div>

    <div class="panel-nl" id="nl-panel">
      <div class="recap" data-share-card="race-nl.png" data-share-text-src="share/race-nl.txt">
        <p class="subn">Last night</p>
        <p>{RACE_NL_RECAP}</p>
        <p class="subn">Since August 13</p>
        <p>{RACE_NL_SINCE}</p>
      </div>
      <p class="subn">Standings through Tuesday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
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
