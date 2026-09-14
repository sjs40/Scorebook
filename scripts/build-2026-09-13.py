#!/usr/bin/env python3
"""Generate /workspace/2026-09-13/index.html and share race text files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-13"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-09-12" / "index.html"
ISSUE_DATE = "2026-09-13"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Rays scored 14 and completed a series sweep behind Aranda's two homers and Peralta's five hitless innings. "
    "Guardians routed Minnesota 9–2 behind Bibee and Kwan's leadoff homer. "
    "Phillies scored seven in the eighth at Atlanta. Butler's walk-off capped the Athletics' 8–7 win over Seattle."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/13"

CLIPS = {
    "rays_sweep": {
        "video": f"{MLB_CDN}/d5926b42-44f46fba-c529cf3a-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "mesa-jr-aranda-power-rays-to-series-sweep",
        "cap": (
            "Jonathan Aranda homered twice and Victor Mesa Jr. went 3-for-5. "
            "Rays 14, Astros 4 — Tampa Bay's 15th series sweep, most in the majors."
        ),
    },
    "phillies_eighth": {
        "video": f"{MLB_CDN}/eb61ee81-b7f185bb-d0bc3115-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "phillies-seven-run-8th-inning-fuels-9-4-win",
        "cap": (
            "Seven runs in the eighth — Realmuto homered and the Phillies scored nine total. "
            "Phillies 9, Braves 4 — Philadelphia has won two straight."
        ),
    },
    "butler_walkoff": {
        "video": f"{MLB_CDN}/27dc86a9-1910ff54-f88654fd-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "lawrence-butler-homers-twice-and-walks-it-off-in-win",
        "cap": (
            "Lawrence Butler homered twice including a walk-off in the ninth. "
            "Athletics 8, Mariners 7 — Oakland took two of three from Seattle."
        ),
    },
    "arozarena": {
        "video": f"{MLB_CDN}/dda1400f-0f2be99e-8574e13a-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "randy-arozarena-s-two-homer-game-x6444",
        "cap": (
            "Randy Arozarena went deep twice and drove in four — and the Mariners still lost. "
            "That's baseball — Seattle scored seven and Oakland scored eight."
        ),
    },
    "phillies_inning": {
        "video": f"{MLB_CDN}/05bf1158-3adcc6bc-85773462-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "phillies-take-the-lead-with-a-seven-run-8th-inning",
        "cap": (
            "Realmuto homered and the Phillies batted around in the eighth. "
            "Phillies 9, Braves 4."
        ),
    },
    "padres_sweep": {
        "video": f"{MLB_CDN}/9055c19b-504ca4ef-6b5e835c-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "fernando-tatis-jr-manny-machado-lift-padres-to-win",
        "cap": (
            "Tatis and Machado keyed a Padres sweep of San Francisco. "
            "Padres 6, Giants 4 — San Diego has won seven straight."
        ),
    },
}

PITCHERS = [
    ("Cam Schlittler", "NYY", 72, "6.0", 1, 0, 2, 8, "NYM"),
    ("Emmet Sheehan", "LAD", 68, "6.0", 2, 0, 1, 5, "MIA"),
    ("David Sandlin", "CWS", 67, "5.2", 2, 0, 0, 5, "STL"),
    ("Freddy Peralta", "TBR", 66, "5.0", 0, 0, 3, 4, "HOU"),
]

HITTERS = [
    ("Randy Arozarena", "SEA", 9, 5, 3, 2, 2, 4, 0),
    ("Lawrence Butler", "ATH", 8, 4, 2, 2, 2, 4, 0),
    ("Jonathan Aranda", "TBR", 8, 4, 2, 2, 2, 3, 0),
    ("Vladimir Guerrero Jr.", "TOR", 8, 5, 4, 2, 1, 1, 0),
    ("J.T. Realmuto", "PHI", 7, 5, 3, 2, 1, 3, 0),
    ("Steven Kwan", "CLE", 7, 4, 3, 2, 1, 2, 0),
    ("George Springer", "TOR", 6, 5, 2, 2, 1, 4, 0),
    ("Matt Olson", "ATL", 6, 5, 3, 1, 1, 3, 0),
]

GAMES = [
    ("COL", "DET", 1, 8, [1, 0, 0, 0, 0, 0, 0, 0, 0], [2, 3, 0, 2, 1, 0, 0, 0], 5, 0, 8, 0, "W Jackson Jobe · L Gabriel Hughes"),
    ("LAA", "WSN", 5, 6, [0, 0, 0, 1, 1, 0, 0, 2, 1], [0, 0, 0, 0, 0, 2, 0, 4], 4, 0, 13, 1, "W Erik Tolman · L Luke Murphy · S Jack Sinclair"),
    ("NYM", "NYY", 0, 2, [0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 0, 1, 0, 0, 0, 0, 0], 3, 0, 3, 0, "W Cam Schlittler · L Christian Scott · S David Bednar"),
    ("PHI", "ATL", 9, 4, [0, 2, 0, 0, 0, 0, 0, 7, 0], [1, 0, 0, 0, 0, 0, 1, 0, 2], 16, 0, 12, 0, "W José Alvarado · L Dylan Lee"),
    ("BAL", "TOR", 1, 8, [0, 0, 0, 0, 1, 0, 0, 0, 0], [0, 1, 0, 0, 3, 0, 0, 4], 9, 0, 10, 0, "W Dylan Cease · L Trevor Rogers"),
    ("HOU", "TBR", 4, 14, [0, 0, 0, 0, 0, 2, 0, 2, 0], [3, 0, 4, 2, 2, 0, 3, 0], 4, 1, 15, 0, "W Freddy Peralta · L Hayden Wesneski"),
    ("LAD", "MIA", 4, 6, [0, 0, 0, 3, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 2, 4], 9, 0, 9, 0, "W Dax Fulton · L Tanner Scott"),
    ("CIN", "MIL", 4, 3, [0, 0, 0, 0, 0, 3, 0, 1, 0], [0, 2, 0, 0, 0, 0, 1, 0, 0], 8, 1, 6, 0, "W Brandon Williamson · L Abner Uribe · S Emilio Pagán"),
    ("CLE", "MIN", 9, 2, [1, 0, 1, 2, 0, 2, 0, 0, 3], [0, 0, 1, 0, 0, 0, 1, 0, 0], 14, 1, 6, 1, "W Tanner Bibee · L Joe Ryan"),
    ("CWS", "STL", 1, 3, [0, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 0, 0], 4, 1, 4, 0, "W Michael McGreevy · L David Sandlin · S George Soriano"),
    ("PIT", "CHC", 4, 3, [1, 0, 0, 0, 0, 3, 0, 0, 0], [0, 0, 0, 0, 2, 1, 0, 0, 0], 9, 0, 5, 0, "W Bubba Chandler · L Matthew Boyd · S Mason Montgomery"),
    ("KCR", "BOS", 1, 4, [0, 0, 0, 0, 0, 0, 1, 0, 0], [0, 1, 0, 0, 0, 0, 1, 2], 5, 2, 8, 0, "W Garrett Whitlock · L Craig Kimbrel · S Aroldis Chapman"),
    ("SEA", "ATH", 7, 8, [0, 0, 2, 3, 1, 0, 0, 1, 0], [2, 0, 0, 0, 0, 0, 4, 0, 2], 12, 1, 9, 0, "W Elvis Alvarado · L Andrés Muñoz"),
    ("TEX", "ARI", 7, 6, [2, 0, 0, 0, 3, 2, 0, 0, 0], [0, 0, 0, 1, 0, 0, 3, 0, 2], 10, 0, 12, 2, "W Cal Quantrill · L Eduardo Rodriguez · S Jacob Latz"),
    ("SDP", "SFG", 6, 4, [2, 3, 0, 1, 0, 0, 0, 0, 0], [0, 2, 0, 0, 1, 1, 0, 0, 0], 9, 2, 9, 0, "W Wandy Peralta · L Logan Webb · S Yuki Matsui"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 90, 59, "--", "--", "W3", "7-3", "+69"),
        ("NYY", 86, 63, "4", "+10.5", "W1", "7-3", "+125"),
        ("BOS", 82, 68, "8.5", "+6", "W2", "7-3", "+88"),
        ("TOR", 75, 75, "15.5", "1", "W2", "6-4", "-31"),
        ("BAL", 72, 78, "18.5", "4", "L2", "3-7", "-35"),
    ],
    "AL Central": [
        ("CWS", 76, 73, "--", "--", "L1", "3-7", "+34"),
        ("CLE", 76, 74, "0.5", "--", "W1", "6-4", "-7"),
        ("MIN", 70, 79, "6", "5.5", "L1", "3-7", "-62"),
        ("DET", 70, 79, "6", "5.5", "W4", "6-4", "+70"),
        ("KCR", 66, 84, "10.5", "10", "L2", "4-6", "-94"),
    ],
    "AL West": [
        ("HOU", 75, 75, "--", "--", "L3", "4-6", "-53"),
        ("TEX", 74, 76, "1", "2", "W2", "5-5", "-44"),
        ("SEA", 70, 80, "5", "6", "L1", "4-6", "-58"),
        ("ATH", 61, 89, "14", "15", "W1", "7-3", "-203"),
        ("LAA", 56, 93, "18.5", "19.5", "L3", "3-7", "-76"),
    ],
    "AL Wild Card": [
        ("NYY", 86, 63, "+10.5", "W1", "7-3", "+125", False),
        ("BOS", 82, 68, "+6", "W2", "7-3", "+88", False),
        ("CLE", 76, 74, "--", "W1", "6-4", "-7", True),
        ("TOR", 75, 75, "1", "W2", "6-4", "-31", False),
        ("TEX", 74, 76, "2", "W2", "5-5", "-44", False),
        ("BAL", 72, 78, "4", "L2", "3-7", "-35", False),
    ],
    "NL East": [
        ("ATL", 88, 62, "--", "--", "L1", "5-5", "+116"),
        ("PHI", 83, 67, "5", "+1.5", "W1", "4-6", "+31"),
        ("MIA", 74, 76, "14", "7.5", "W2", "3-7", "+6"),
        ("WSN", 70, 81, "18.5", "12", "W3", "3-7", "+3"),
        ("NYM", 69, 80, "18.5", "12", "L1", "7-3", "-34"),
    ],
    "NL Central": [
        ("MIL", 93, 57, "--", "--", "L1", "6-4", "+195"),
        ("CHC", 83, 67, "10", "+1.5", "L1", "5-5", "+138"),
        ("PIT", 75, 75, "18", "6.5", "W1", "7-3", "+26"),
        ("STL", 74, 76, "19", "7.5", "W1", "4-6", "-7"),
        ("CIN", 70, 79, "22.5", "11", "W1", "4-6", "-145"),
    ],
    "NL West": [
        ("LAD", 90, 59, "--", "--", "L2", "8-2", "+170"),
        ("SDP", 81, 68, "9", "--", "W7", "8-2", "+22"),
        ("ARI", 79, 71, "11.5", "2.5", "L2", "6-4", "+2"),
        ("SFG", 62, 88, "28.5", "19.5", "L3", "4-6", "-77"),
        ("COL", 55, 94, "35", "26", "L7", "2-8", "-169"),
    ],
    "NL Wild Card": [
        ("CHC", 83, 67, "+1.5", "L1", "5-5", "+138", False),
        ("PHI", 83, 67, "+1.5", "W1", "4-6", "+31", False),
        ("SDP", 81, 68, "--", "W7", "8-2", "+22", True),
        ("ARI", 79, 71, "2.5", "L2", "6-4", "+2", False),
        ("PIT", 75, 75, "6.5", "W1", "7-3", "+26", False),
        ("MIA", 74, 76, "7.5", "W2", "3-7", "+6", False),
    ],
}

UPCOMING = [
    ("CWS", "CLE", "Sean Newcomb vs. Gavin Williams", "6:40 PM ET", "2026-09-14T22:40:00Z", ""),
    ("LAD", "CIN", "Tarik Skubal vs. Nick Lodolo", "6:40 PM ET", "2026-09-14T22:40:00Z", ""),
    ("DET", "TOR", "Troy Melton vs. José Soriano", "7:07 PM ET", "2026-09-14T23:07:00Z", ""),
    ("BAL", "NYM", "Brandon Young vs. Jonah Tong", "7:10 PM ET", "2026-09-14T23:10:00Z", ""),
    ("ATL", "CHC", "Reynaldo López vs. David Peterson", "7:40 PM ET", "2026-09-14T23:40:00Z", ""),
    ("NYY", "MIN", "Will Warren vs. Dean Kremer", "7:40 PM ET", "2026-09-14T23:40:00Z", ""),
    ("SFG", "STL", "Landen Roupp vs. Quinn Mathews", "7:45 PM ET", "2026-09-14T23:45:00Z", ""),
    ("SDP", "COL", "Casey Mize vs. Tomoyuki Sugano", "8:40 PM ET", "2026-09-15T00:40:00Z", ""),
    ("SEA", "LAA", "Kade Anderson vs. Reid Detmers", "9:38 PM ET", "2026-09-15T01:38:00Z", ""),
    ("MIA", "ARI", "Sandy Alcantara vs. Corbin Burnes", "9:40 PM ET", "2026-09-15T01:40:00Z", ""),
]

OFF_TONIGHT = ["ATH", "BOS", "HOU", "KCR", "MIL", "PHI", "PIT", "TBR", "TEX", "WSN"]

TEAM_SUMMARIES = {
    "CHC": "Your Cubs: Lost 3–4 to Pittsburgh at Wrigley. Host Atlanta tonight.",
    "MIA": "Your Marlins: Fulton and a six-run rally beat the Dodgers 6–4. At Arizona tonight.",
    "SFG": "Your Giants: Lost 4–6 to San Diego; Webb took the loss. At St. Louis tonight.",
    "NYM": "Your Mets: Shut out 0–2 at Yankee Stadium; Scott took the loss. Host Baltimore tonight.",
    "ATL": "Your Braves: Olson homered but lost 4–9 to Philadelphia. At Chicago tonight.",
    "PHI": "Your Phillies: Scored seven in the eighth in a 9–4 win at Atlanta. Off tonight.",
    "DET": "Your Tigers: Jobe fanned eight in an 8–1 win over Colorado. At Toronto tonight.",
    "CLE": "Your Guardians: Bibee and Kwan keyed a 9–2 rout at Minnesota. Host Chicago tonight.",
    "LAA": "Your Angels: Lost 5–6 in 10 at Washington. Host Seattle tonight.",
    "PIT": "Your Pirates: Chandler earned the win in a 4–3 victory at Chicago. Off tonight.",
    "MIL": "Your Brewers: Lost 3–4 to Cincinnati at home. Off tonight.",
    "CIN": "Your Reds: Williamson earned the win in a 4–3 victory at Milwaukee. Host Los Angeles tonight.",
    "BOS": "Your Red Sox: Whitlock and Chapman beat Kansas City 4–1. Off tonight.",
    "BAL": "Your Orioles: Lost 1–8 at Toronto. At New York tonight.",
    "TBR": "Your Rays: Aranda homered twice in a 14–4 sweep of Houston. Off tonight.",
    "TEX": "Your Rangers: Seager homered and Quantrill earned the win in a 7–6 victory at Arizona. Off tonight.",
    "MIN": "Your Twins: Lost 2–9 to Cleveland. Host New York tonight.",
    "CWS": "Your White Sox: Lost 1–3 at St. Louis. At Cleveland tonight.",
    "TOR": "Your Blue Jays: Cease and eight runs beat Baltimore 8–1. Host Detroit tonight.",
    "KCR": "Your Royals: Lost 1–4 at Fenway. Off tonight.",
    "ARI": "Your Diamondbacks: Lost 6–7 to Texas. Host Miami tonight.",
    "HOU": "Your Astros: Lost 4–14 at Tampa Bay. Off tonight.",
    "NYY": "Your Yankees: Schlittler shut out the Mets 2–0. At Minnesota tonight.",
    "SDP": "Your Padres: Swept San Francisco 6–4; seven straight wins. At Colorado tonight.",
    "STL": "Your Cardinals: McGreevy earned the win in a 3–1 victory over Chicago. Host San Francisco tonight.",
    "COL": "Your Rockies: Lost 1–8 at Detroit. Host San Diego tonight.",
    "WSN": "Your Nationals: Tolman earned the win in a 6–5 victory over the Angels. Off tonight.",
    "LAD": "Your Dodgers: Lost 4–6 at Miami. At Cincinnati tonight.",
    "ATH": "Your Athletics: Butler's walk-off capped an 8–7 win over Seattle. Off tonight.",
    "SEA": "Your Mariners: Arozarena homered twice but lost 7–8 at Oakland. At Los Angeles tonight.",
}

RACE_AL_RECAP = (
    "Jonathan Aranda homered twice as the Rays scored 14 and completed their 15th series sweep. "
    "Tanner Bibee and Steven Kwan keyed a Guardians 9–2 rout at Minnesota. "
    "Lawrence Butler's walk-off capped the Athletics' 8–7 win over Seattle."
)
RACE_AL_SINCE = "The Rays are 7–3 in their last ten."
RACE_NL_RECAP = (
    "Phillies scored seven in the eighth in a 9–4 win at Atlanta. "
    "Padres completed a sweep of San Francisco with a 6–4 win — seven straight. "
    "Pirates edged the Cubs 4–3 at Wrigley."
)
RACE_NL_SINCE = "The Padres are 8–2 in their last ten."


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
    return m.group(1).replace("2026-09-12", ISSUE_DATE)


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
<title>Scorebook - Sunday, September 13</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Sunday, September 13" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Sunday, September 13" />
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
  <h1>Sunday, September 13</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("rays_sweep")}
  <p class="cap">{CLIPS["rays_sweep"]["cap"]}</p>
{clip_html("phillies_eighth")}
  <p class="cap">{CLIPS["phillies_eighth"]["cap"]}</p>
{clip_html("butler_walkoff")}
  <p class="cap">{CLIPS["butler_walkoff"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="rays_sweep" required> Rays' 14-run sweep</label>
      <label><input type="radio" name="play" value="phillies_eighth"> Phillies' seven-run eighth</label>
      <label><input type="radio" name="play" value="butler_walkoff"> Butler's walk-off</label>
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
{clip_html("arozarena")}
  <p class="cap">{CLIPS["arozarena"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Top of the eighth at Truist Park. Philadelphia trailed 4–2 when the Phillies scored seven — Realmuto homered and the rally keyed a 9–4 win. Phillies 9, Braves 4.</p>
{clip_html("phillies_inning")}
  <p class="cap">{CLIPS["phillies_inning"]["cap"]}</p>

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
