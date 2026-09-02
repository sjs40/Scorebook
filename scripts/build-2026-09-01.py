#!/usr/bin/env python3
"""Generate /workspace/2026-09-01/index.html and share race text files."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-01"
REF_HTML = ROOT / "2026-08-31" / "index.html"
ISSUE_DATE = "2026-09-01"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Gavin Williams fans 13 in Cleveland. Pirates outlast the Giants 13–12. "
    "Morales homers in his debut. Phillies win their sixth straight. Twins rout Detroit 15–2."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/01"

CLIPS = {
    "williams": {
        "video": f"{MLB_CDN}/a0d902ac-1fd5e3ba-17c9db19-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "gavin-williams-13-strikeouts",
        "cap": "Gavin Williams: 7.0 IP, 2 H, 0 ER, 13 K. Guardians 6, Blue Jays 1.",
    },
    "slugfest": {
        "video": f"{MLB_CDN}/ab6f486a-8f41d6d6-78f9d063-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "pirates-outlast-giants-walk-off-in-slugfest-win",
        "cap": "Pirates 13, Giants 12. Lowe scores on a ninth-inning error.",
    },
    "morales": {
        "video": f"{MLB_CDN}/94bbccfb-f3323c3c-ee64aca0-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "yohandy-morales-knocks-three-hits-in-his-mlb-debut",
        "cap": "Yohandy Morales homers for his first big league hit. Nationals 9, Braves 5.",
    },
    "blooper": {
        "video": f"{MLB_CDN}/83309260-e55b3c26-58f16e10-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "three-brewers-collide-on-blooper-in-shallow-left",
        "cap": "Three Brewers collide on a pop-up at Wrigley. The ball drops for a double. Brewers still win 9–4.",
    },
    "pirates_third": {
        "video": f"{MLB_CDN}/13b981b9-f07be93e-9d0bb822-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "pirates-score-nine-runs-in-the-3rd",
        "cap": "Nine runs, eight singles, two walks. No extra-base hits.",
    },
}

PITCHERS = [
    ("Gavin Williams", "CLE", 85, "7.0", 2, 0, 1, 13, "TOR"),
    ("Sean Burke", "CWS", 69, "5.2", 1, 0, 4, 6, "HOU"),
    ("Freddy Peralta", "TBR", 69, "6.0", 3, 1, 0, 7, "NYM"),
    ("Tyler Phillips", "MIA", 67, "5.0", 1, 0, 2, 4, "KCR"),
]

HITTERS = [
    ("Thomas Saggese", "STL", 8, 3, 2, 0, 3, 0, 0),
    ("Fernando Tatis Jr.", "SDP", 8, 5, 4, 0, 2, 0, 0),
    ("Jacob Pauley", "MIA", 7, 4, 1, 4, 0, 2, 0),
    ("Royce Lewis", "MIN", 7, 4, 1, 3, 0, 3, 0),
    ("Ryan Jeffers", "MIN", 7, 4, 1, 3, 0, 2, 0),
    ("Jordan Walker", "STL", 7, 5, 1, 2, 0, 3, 0),
    ("Brandon Lowe", "PIT", 7, 6, 0, 1, 1, 0, 0),
    ("Yohandy Morales", "WSN", 7, 5, 1, 3, 0, 1, 0),
]

# away, home, away_score, home_score, away_innings, home_innings, away_h, away_e, home_h, home_e, note
GAMES = [
    ("SDP", "CIN", 3, 4, [1, 0, 0, 0, 1, 0, 0, 0, 1], [1, 0, 0, 0, 1, 0, 0, 2, 0], 7, 0, 8, 1, "W Burke · L Morejón · S Pagán"),
    ("SFG", "PIT", 12, 13, [0, 5, 0, 0, 0, 2, 0, 5, 0], [2, 0, 9, 0, 0, 0, 1, 0, 1], 16, 1, 19, 0, "W Montgomery · L Seymour"),
    ("NYM", "TBR", 2, 6, [1, 0, 0, 0, 0, 0, 1, 0, 0], [1, 0, 1, 0, 0, 3, 0, 1, 0], 3, 1, 13, 0, "W Peralta · L Manaea"),
    ("TOR", "CLE", 1, 6, [0, 0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 2, 0, 2, 2, 0], 3, 0, 8, 1, "W Williams · L Arrighetti"),
    ("SEA", "BOS", 9, 6, [1, 5, 1, 1, 1, 0, 0, 0, 0], [1, 0, 0, 0, 0, 1, 2, 0, 2], 14, 1, 11, 0, "W Woo · L Paez"),
    ("ATL", "WSN", 5, 9, [0, 1, 1, 0, 0, 0, 0, 3, 0], [0, 4, 1, 0, 0, 1, 2, 1, 0], 8, 1, 12, 0, "W Simpson · L Smith-Shawver"),
    ("MIL", "CHC", 9, 4, [0, 0, 0, 0, 1, 4, 2, 2, 0], [0, 0, 0, 3, 0, 1, 0, 0, 0], 13, 2, 6, 0, "W Senzatela · L Palencia"),
    ("MIA", "KCR", 6, 3, [0, 2, 0, 0, 1, 0, 3, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 1], 8, 1, 6, 0, "W Phillips · L Dobnak"),
    ("DET", "MIN", 2, 15, [1, 0, 0, 0, 0, 0, 0, 1, 0], [1, 0, 0, 0, 3, 10, 0, 1, 0], 8, 1, 13, 1, "W Prielipp · L Melton"),
    ("ATH", "TEX", 5, 8, [0, 0, 1, 0, 0, 0, 1, 1, 2], [1, 0, 1, 0, 3, 3, 0, 0, 0], 11, 0, 12, 1, "W Gore · L Basso · S Latz"),
    ("CWS", "HOU", 5, 1, [0, 0, 0, 0, 3, 0, 2, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 0], 8, 0, 3, 0, "W Burke · L Teng"),
    ("BAL", "COL", 2, 4, [0, 0, 1, 0, 0, 0, 1, 0, 0], [0, 2, 0, 0, 0, 0, 2, 0, 0], 7, 1, 10, 1, "W Hill · L De León · S Romano"),
    ("NYY", "LAA", 7, 3, [3, 0, 1, 0, 0, 0, 0, 2, 1], [0, 0, 1, 0, 0, 2, 0, 0, 0], 14, 0, 9, 0, "W Cole · L Rodriguez"),
    ("PHI", "ARI", 7, 1, [2, 0, 0, 0, 1, 0, 0, 3, 1], [0, 0, 0, 0, 1, 0, 0, 0, 0], 13, 0, 6, 0, "W Luzardo · L Rodríguez"),
    ("STL", "LAD", 13, 8, [0, 2, 5, 2, 1, 0, 1, 2, 0], [0, 0, 3, 0, 1, 0, 1, 0, 3], 13, 1, 9, 1, "W McGreevy · L Lauer"),
]

FEATURED_KEYS = [
    ("TOR", "CLE"),
    ("SFG", "PIT"),
    ("ATL", "WSN"),
    ("DET", "MIN"),
    ("MIL", "CHC"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 83, 55, "--", "--", "W1", "7-3", "+57"),
        ("NYY", 79, 60, "4.5", "+8.5", "W1", "6-4", "+112"),
        ("BOS", 75, 64, "8.5", "+4.5", "L1", "5-5", "+82"),
        ("BAL", 69, 70, "14.5", "1.5", "L1", "7-3", "-19"),
        ("TOR", 68, 71, "15.5", "2.5", "L1", "5-5", "-55"),
    ],
    "AL Central": [
        ("CHW", 73, 65, "--", "--", "W1", "6-4", "+45"),
        ("CLE", 70, 68, "3.0", "--", "W2", "8-2", "+3"),
        ("MIN", 67, 72, "6.5", "3.5", "W3", "4-6", "-33"),
        ("DET", 63, 75, "10.0", "6.0", "L3", "2-8", "+42"),
        ("KCR", 62, 77, "11.5", "7.5", "L2", "7-3", "-86"),
    ],
    "AL West": [
        ("HOU", 70, 69, "--", "--", "L1", "5-5", "-44"),
        ("TEX", 69, 70, "1.0", "1.5", "W3", "5-5", "-41"),
        ("SEA", 65, 74, "5.0", "5.5", "W1", "4-6", "-70"),
        ("LAA", 53, 86, "17.0", "16.5", "L1", "2-8", "-77"),
        ("ATH", 53, 86, "17.0", "16.5", "L5", "4-6", "-201"),
    ],
    "AL Wild Card": [
        ("NYY", 79, 60, "+8.5", "W1", "6-4", "+112", False),
        ("BOS", 75, 64, "+4.5", "L1", "5-5", "+82", False),
        ("CLE", 70, 68, "--", "W2", "8-2", "+3", True),
        ("BAL", 69, 70, "1.5", "L1", "7-3", "-19", False),
        ("TOR", 68, 71, "2.5", "L1", "5-5", "-55", False),
        ("TEX", 69, 70, "1.5", "W3", "5-5", "-41", False),
    ],
    "NL East": [
        ("ATL", 82, 57, "--", "--", "L2", "7-3", "+109"),
        ("PHI", 79, 60, "3.0", "+6.0", "W6", "8-2", "+37"),
        ("MIA", 70, 69, "12.0", "3.0", "W1", "5-5", "+15"),
        ("WSN", 67, 74, "16.0", "8.0", "W2", "6-4", "+23"),
        ("NYM", 62, 77, "20.0", "11.0", "L1", "4-6", "-56"),
    ],
    "NL Central": [
        ("MIL", 86, 53, "--", "--", "W1", "6-4", "+168"),
        ("CHC", 78, 61, "8.0", "+5.0", "L1", "4-6", "+136"),
        ("STL", 69, 70, "17.0", "4.0", "W1", "3-7", "-10"),
        ("PIT", 68, 71, "18.0", "5.0", "W3", "5-5", "+27"),
        ("CIN", 66, 73, "20.0", "7.0", "W1", "5-5", "-112"),
    ],
    "NL West": [
        ("LAD", 82, 56, "--", "--", "L1", "5-5", "+148"),
        ("SDP", 73, 66, "9.5", "--", "L1", "4-6", "+14"),
        ("ARI", 73, 67, "10.0", "0.5", "L3", "5-5", "-2"),
        ("SFG", 57, 82, "25.5", "16.0", "L1", "5-5", "-71"),
        ("COL", 53, 86, "29.5", "20.0", "W1", "3-7", "-141"),
    ],
    "NL Wild Card": [
        ("CHC", 78, 61, "+5.0", "L1", "4-6", "+136", False),
        ("PHI", 79, 60, "+6.0", "W6", "8-2", "+37", False),
        ("SDP", 73, 66, "--", "L1", "4-6", "+14", True),
        ("ARI", 73, 67, "0.5", "L3", "5-5", "-2", False),
        ("MIA", 70, 69, "3.0", "W1", "5-5", "+15", False),
        ("STL", 69, 70, "4.0", "W1", "3-7", "-10", False),
    ],
}

UPCOMING = [
    ("SDP", "CIN", "Randy Vásquez vs. Nick Lodolo", "12:40 ET", "2026-09-02T16:40:00Z", ""),
    ("ATL", "WSN", "Clay Holmes vs. Chase Lord", "1:05 ET", "2026-09-02T17:05:00Z", ""),
    ("ATH", "TEX", "Jacob Lopez vs. Zack Bradford", "2:35 ET", "2026-09-02T18:35:00Z", ""),
    ("BAL", "COL", "Tyler Rogers vs. Tomoyuki Sugano", "3:10 ET", "2026-09-02T19:10:00Z", ""),
    ("PHI", "ARI", "Tommy Painter vs. Travis Clarke", "3:40 ET", "2026-09-02T19:40:00Z", ""),
    ("SEA", "BOS", "Bryan Miller vs. Brayan Sandoval", "4:10 ET", "2026-09-02T20:10:00Z", ""),
    ("TOR", "CLE", "Dylan Cease vs. Joey Cantillo", "6:40 ET", "2026-09-02T22:40:00Z", ""),
    ("SFG", "PIT", "Randy Roupp vs. Chase Chandler", "6:40 ET", "2026-09-02T22:40:00Z", ""),
    ("NYM", "TBR", "Tyler Hagenman vs. Griffin Jax", "6:40 ET", "2026-09-02T22:40:00Z", ""),
    ("MIL", "CHC", "Robert Misiorowski vs. David Peterson", "7:40 ET", "2026-09-02T23:40:00Z", "MLBN"),
    ("MIA", "KCR", "Eury Pérez vs. Noah Cameron", "7:40 ET", "2026-09-02T23:40:00Z", ""),
    ("DET", "MIN", "Jackson Anderson vs. Dean Kremer", "7:40 ET", "2026-09-02T23:40:00Z", ""),
    ("CWS", "HOU", "Cooper Martin vs. Hayden Wesneski", "8:10 ET", "2026-09-03T00:10:00Z", ""),
    ("NYY", "LAA", "Ben Schlittler vs. Reid Detmers", "9:38 ET", "2026-09-03T01:38:00Z", ""),
    ("STL", "LAD", "TBD vs. Yoshinobu Yamamoto", "10:10 ET", "2026-09-03T02:10:00Z", ""),
]

TEAM_SUMMARIES = {
    "CLE": "Your Guardians: Gavin Williams struck out 13 in seven shutout innings. Beat Toronto 6-1.",
    "PIT": "Your Pirates: Thirteen runs on nineteen hits. Outlasted San Francisco 13-12 on a ninth-inning error.",
    "WSN": "Your Nationals: Yohandy Morales homered for his first big league hit. Beat Atlanta 9-5.",
    "MIN": "Your Twins: Fifteen runs. Royce Lewis and Ryan Jeffers had seven total bases apiece. Won 15-2 over Detroit.",
    "MIL": "Your Brewers: Nine runs at Wrigley. Three outfielders collided on a pop-up; the ball dropped for a double. Won 9-4 anyway.",
    "CHC": "Your Cubs: Lost 9-4 to Milwaukee. Three Brewers collided on a blooper; it fell for a double.",
    "PHI": "Your Phillies: Jesús Luzardo went the distance in a 7-1 win at Arizona. Sixth straight victory.",
    "STL": "Your Cardinals: Thirteen runs at Dodger Stadium. Thomas Saggese and Jordan Walker combined for fifteen total bases.",
    "TBR": "Your Rays: Freddy Peralta struck out seven over six. Beat the Mets 6-2.",
    "NYY": "Your Yankees: Gerrit Cole got the win in Anaheim. Seven runs, fourteen hits.",
    "CWS": "Your White Sox: Sean Burke held Houston to one run over 5.2 innings. Won 5-1.",
    "SEA": "Your Mariners: Bryan Woo outdueled Boston. Nine runs on fourteen hits in a 9-6 win at Fenway.",
    "MIA": "Your Marlins: Tyler Phillips and Jacob Pauley led a 6-3 win in Kansas City.",
    "TEX": "Your Rangers: MacKenzie Gore got the win. Beat Oakland 8-5.",
    "SFG": "Your Giants: Twelve runs weren't enough. Lost 13-12 in Pittsburgh.",
    "ATL": "Your Braves: Lost 9-5 in Washington. Yohandy Morales homered in his big league debut — for the Nationals.",
    "SDP": "Your Padres: Fernando Tatis Jr. had four hits and eight total bases. Lost 4-3 in Cincinnati.",
    "CIN": "Your Reds: Hunter Burke got the win. Beat San Diego 4-3 on Pagán's save.",
    "BOS": "Your Red Sox: Lost 9-6 to Seattle. Woo went the distance at Fenway.",
    "TOR": "Your Blue Jays: One run on three hits against Gavin Williams. Lost 6-1 in Cleveland.",
    "NYM": "Your Mets: Two runs on three hits. Lost 6-2 in Tampa.",
    "HOU": "Your Astros: One run, three hits. Lost 5-1 to the White Sox.",
    "DET": "Your Tigers: Two runs at Target Field. Lost 15-2 to Minnesota.",
    "KCR": "Your Royals: Three runs. Lost 6-3 to Miami.",
    "ATH": "Your Athletics: Five runs on eleven hits. Lost 8-5 in Texas.",
    "LAA": "Your Angels: Three runs. Lost 7-3 to the Yankees.",
    "BAL": "Your Orioles: Two runs at Coors Field. Lost 4-2 to Colorado.",
    "COL": "Your Rockies: Four runs beat Baltimore 4-2. Tyler Hill got the win.",
    "ARI": "Your Diamondbacks: One run on six hits. Lost 7-1 to Philadelphia.",
    "LAD": "Your Dodgers: Eight runs on nine hits. Lost 13-8 to St. Louis.",
}

RACE_AL_RECAP = (
    "Gavin Williams fans 13 and Cleveland wins. White Sox beat Houston. Texas beats Oakland."
)
RACE_AL_SINCE = "Cleveland is 8-2 in its last ten."
RACE_NL_RECAP = (
    "Pirates outlast Giants 13-12. Morales homers in his debut. "
    "Phillies win their sixth straight. Cubs lose 9-4 to Milwaukee."
)
RACE_NL_SINCE = "Philadelphia is 8-2 in its last ten."


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
    return m.group(1).replace("2026-08-31", ISSUE_DATE)


def clip_html(key: str) -> str:
    c = CLIPS[key]
    return f"""<figure class="clip">
  <video controls playsinline preload="metadata" src="{c['video']}"></video>
  <figcaption><a href="https://www.mlb.com/video/{c['slug']}">Film Room</a> · MLB Film Room stream</figcaption>
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


def find_game(away: str, home: str) -> tuple:
    for g in GAMES:
        if g[0] == away and g[1] == home:
            return g
    raise KeyError(f"Game {away}@{home} not found")


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
        note_bit = f". {note}." if note else "."
        parts.append(
            f'    <article class="upcoming-game" data-away-team="{away}" data-home-team="{home}">\n'
            f"      <p><strong>{pitchers}</strong> — {away} at {home}, "
            f'<time datetime="{start_iso}">{start_time}</time>{note_bit}</p>\n'
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
            "note": note.replace(" · ", " · "),
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
        "offTonight": [],
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
    featured = "\n".join(render_game(find_game(a, h)) for a, h in FEATURED_KEYS)

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
<title>Scorebook - Tuesday, September 1</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Tuesday, September 1" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Tuesday, September 1" />
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
  <h1>Tuesday, September 1</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("williams")}
  <p class="cap">{CLIPS["williams"]["cap"]}</p>
{clip_html("slugfest")}
  <p class="cap">{CLIPS["slugfest"]["cap"]}</p>
{clip_html("morales")}
  <p class="cap">{CLIPS["morales"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="williams" required> Gavin Williams 13 K</label>
      <label><input type="radio" name="play" value="slugfest"> Pirates slugfest</label>
      <label><input type="radio" name="play" value="morales"> Morales debut homer</label>
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
{clip_html("blooper")}
  <p class="cap">{CLIPS["blooper"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Top of the third at PNC Park. The Pirates sent twelve batters to the plate and scored nine runs over 34 minutes — eight singles, two walks, no extra-base hits. San Francisco led 5-2. Pittsburgh led 11-5.</p>
{clip_html("pirates_third")}
  <p class="cap">{CLIPS["pirates_third"]["cap"]}</p>

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
{featured}

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
    print(f"Wrote {html_path}")
    print(f"Wrote {OUT_DIR / 'share' / 'race-al.txt'}")
    print(f"Wrote {OUT_DIR / 'share' / 'race-nl.txt'}")


if __name__ == "__main__":
    main()
