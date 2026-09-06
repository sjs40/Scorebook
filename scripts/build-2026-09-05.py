#!/usr/bin/env python3
"""Generate /workspace/2026-09-05/index.html and share race text files."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-05"
REF_HTML = ROOT / "2026-09-04" / "index.html"
ISSUE_DATE = "2026-09-05"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Devers and Koss each go deep twice in SF's 9–5 win. "
    "Wheeler and Schwarber cut Atlanta's NL East lead to four. "
    "Aranda walks off Texas in the 10th. "
    "Gray's 17th win blanks Baltimore."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/05"

CLIPS = {
    "devers": {
        "video": f"{MLB_CDN}/54d480c7-564cf9c9-91b05433-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "devers-koss-each-homer-twice-in-9-5-win-over-mets",
        "cap": (
            "Rafael Devers and Christian Koss each homered twice. Devers drove in three. "
            "Giants 9, Mets 5 — six long balls total."
        ),
    },
    "wheeler": {
        "video": f"{MLB_CDN}/d3a11553-03dc9e33-a88adc6d-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "kyle-schwarber-zack-wheeler-fuel-phillies-4-2-win",
        "cap": (
            "Zack Wheeler: 6.0 IP, 3 H, 1 ER, 2 BB, 9 K. Kyle Schwarber's 41st homer. "
            "Phillies 4, Braves 2 — NL East gap to four."
        ),
    },
    "aranda": {
        "video": f"{MLB_CDN}/985b730a-92b30a6d-8da19b2a-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "jonathan-aranda-hits-the-go-ahead-in-rays-6-3-win",
        "cap": (
            "Jonathan Aranda: three-run homer in the 10th after an intentional walk to Yandy Díaz. "
            "Rays 6, Rangers 3."
        ),
    },
    "gray": {
        "video": f"{MLB_CDN}/779c899b-c0290d04-c899578b-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "sonny-gray-deals-seven-scoreless-in-red-sox-5-0-win",
        "cap": (
            "Sonny Gray: 7.0 IP, 3 H, 0 ER, 3 BB, 7 K — majors-leading 17th win. "
            "Red Sox 5, Orioles 0."
        ),
    },
    "rockies_fifth": {
        "video": f"{MLB_CDN}/548a6585-6087586b-b1e32df7-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "hunter-goodman-leads-rockies-past-cardinals-10-7",
        "cap": (
            "Six runs in the fifth — Hunter Goodman doubled among five Rockies hits in the frame. "
            "Colorado led 6–1 and won 10–7."
        ),
    },
}

PITCHERS = [
    ("Jeffrey Springs", "ATH", 77, "7.0", 2, 0, 2, 6, "SEA"),
    ("Drew Rasmussen", "TBR", 77, "7.0", 3, 1, 0, 7, "TEX"),
    ("Zack Wheeler", "PHI", 76, "6.0", 3, 1, 2, 9, "ATL"),
    ("Sonny Gray", "BOS", 76, "7.0", 3, 0, 3, 7, "BAL"),
]

HITTERS = [
    ("Riley Greene", "DET", 10, 5, 4, 2, 2, 4, 0),
    ("Rafael Devers", "SFG", 8, 4, 2, 2, 2, 3, 0),
    ("Christian Koss", "SFG", 8, 4, 2, 2, 2, 3, 0),
    ("Bryan Reynolds", "PIT", 6, 3, 3, 1, 1, 1, 0),
    ("Jonathan Aranda", "TBR", 5, 5, 2, 1, 1, 3, 0),
    ("Ivan Herrera", "STL", 5, 5, 2, 1, 1, 3, 0),
    ("Kyle Schwarber", "PHI", 5, 3, 2, 1, 1, 2, 0),
    ("Max Muncy", "ATH", 5, 4, 2, 1, 1, 2, 0),
]

# away, home, away_score, home_score, away_innings, home_innings, away_h, away_e, home_h, home_e, note
GAMES = [
    ("CHC", "MIA", 6, 5, [0, 0, 3, 1, 1, 1, 0, 0, 0], [0, 0, 0, 2, 2, 0, 1, 0, 0], 13, 0, 6, 0, "W Ryan Rolison · L Ryan Gusto · S Ryan Zeferjahn"),
    ("SFG", "NYM", 9, 5, [1, 0, 2, 0, 3, 0, 0, 2, 1], [0, 2, 0, 0, 0, 0, 1, 0, 2], 10, 1, 5, 0, "W Anthony Molina · L Zac Thornton"),
    ("ATL", "PHI", 2, 4, [0, 0, 1, 0, 0, 0, 1, 0, 0], [2, 1, 0, 1, 0, 0, 0, 0], 5, 0, 9, 0, "W Zack Wheeler · L Martin Perez · S Jhoan Duran"),
    ("DET", "CLE", 6, 0, [1, 0, 1, 0, 0, 1, 3, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], 11, 0, 3, 1, "W Framber Valdez · L Parker Messick"),
    ("LAA", "PIT", 6, 1, [0, 0, 0, 1, 2, 0, 3, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 0], 12, 0, 8, 0, "W Yusei Kikuchi · L Braxton Ashcraft"),
    ("MIL", "CIN", 3, 5, [1, 0, 1, 0, 0, 0, 1, 0, 0], [1, 0, 0, 1, 0, 1, 1, 1], 8, 0, 12, 1, "W Tony Santillan · L Aaron Ashby · S Emilio Pagan"),
    ("BOS", "BAL", 5, 0, [0, 0, 0, 0, 0, 3, 2, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], 9, 0, 5, 0, "W Sonny Gray · L Chris Bassitt"),
    ("TBR", "TEX", 6, 3, [1, 0, 0, 0, 1, 0, 0, 1, 0, 3], [0, 0, 0, 0, 0, 1, 0, 2, 0, 0], 10, 1, 6, 0, "W Tyler Wells · L Jacob Latz"),
    ("MIN", "CHW", 6, 4, [0, 0, 0, 2, 3, 0, 1, 0, 0], [3, 0, 0, 0, 1, 0, 0, 0, 0], 8, 0, 6, 1, "W Taj Bradley · L Anthony Kay · S Yoendrys Gomez"),
    ("TOR", "KCR", 4, 3, [2, 0, 1, 0, 0, 0, 1, 0, 0], [2, 0, 0, 1, 0, 0, 0, 0, 0], 13, 0, 7, 2, "W Mason Fluharty · L Craig Kimbrel · S Louis Varland"),
    ("ARI", "HOU", 4, 3, [0, 0, 0, 0, 1, 0, 1, 1, 0, 1], [0, 0, 2, 0, 1, 0, 0, 0, 0, 0], 8, 0, 9, 0, "W Jonathan Loaisiga · L Bryan King · S Brandyn Garcia"),
    ("NYY", "SDP", 5, 1, [0, 4, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0], 9, 1, 3, 1, "W Carlos Rodon · L Robbie Ray"),
    ("STL", "COL", 7, 10, [0, 1, 0, 0, 2, 2, 0, 0, 2], [0, 0, 0, 0, 6, 0, 4, 0], 13, 2, 11, 0, "W Brennan Bernardino · L Matthew Liberatore · S Jordan Romano"),
    ("WSN", "LAD", 5, 6, [0, 1, 0, 2, 0, 0, 1, 0, 1], [2, 0, 0, 0, 0, 0, 3, 1], 10, 0, 7, 0, "W Alex Vesia · L Clayton Beeter · S Tanner Scott"),
    ("ATH", "SEA", 6, 2, [0, 1, 1, 2, 0, 0, 0, 2, 0], [0, 0, 0, 0, 0, 0, 0, 1, 1], 9, 0, 6, 0, "W Jeffrey Springs · L George Kirby"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 85, 57, "--", "--", "W2", "7-3", "+49"),
        ("NYY", 81, 61, "4", "+9", "W1", "6-4", "+118"),
        ("BOS", 78, 65, "7", "+6", "W3", "5-5", "+84"),
        ("TOR", 72, 71, "13", "--", "W4", "8-2", "-33"),
        ("BAL", 69, 74, "16", "3", "L5", "4-6", "-27"),
    ],
    "AL Central": [
        ("CHW", 74, 68, "--", "--", "L1", "5-5", "+40"),
        ("CLE", 72, 71, "2", "--", "L1", "5-5", "-15"),
        ("MIN", 68, 74, "6", "4", "W1", "4-6", "-39"),
        ("DET", 65, 77, "9", "7", "W1", "3-7", "+51"),
        ("KCR", 63, 80, "11", "9", "L2", "4-6", "-93"),
    ],
    "AL West": [
        ("HOU", 73, 70, "--", "--", "L1", "7-3", "-37"),
        ("TEX", 70, 73, "3", "2", "L2", "4-6", "-46"),
        ("SEA", 66, 77, "7", "6", "L3", "2-8", "-73"),
        ("ATH", 57, 86, "16", "15", "W4", "5-5", "-186"),
        ("LAA", 54, 88, "19", "18", "W1", "2-8", "-76"),
    ],
    "AL Wild Card": [
        ("NYY", 81, 61, "+9", "W1", "6-4", "+118", False),
        ("BOS", 78, 65, "+6", "W3", "5-5", "+84", False),
        ("TOR", 72, 71, "--", "W4", "8-2", "-33", True),
        ("CLE", 72, 71, "0", "L1", "5-5", "-15", False),
        ("TEX", 70, 73, "2", "L2", "4-6", "-46", False),
        ("BAL", 69, 74, "3", "L5", "4-6", "-27", False),
    ],
    "NL East": [
        ("ATL", 84, 58, "--", "--", "L1", "7-3", "+119"),
        ("PHI", 80, 62, "4", "+5", "W1", "7-3", "+35"),
        ("MIA", 71, 72, "13", "4", "L3", "4-6", "+8"),
        ("WSN", 67, 77, "17", "8", "L3", "5-5", "+11"),
        ("NYM", 64, 78, "20", "11", "L1", "4-6", "-50"),
    ],
    "NL Central": [
        ("MIL", 88, 55, "--", "--", "L1", "6-4", "+172"),
        ("CHC", 81, 62, "7", "+6", "W3", "5-5", "+139"),
        ("STL", 71, 72, "17", "4", "L1", "5-5", "-11"),
        ("PIT", 70, 73, "18", "5", "L1", "6-4", "+25"),
        ("CIN", 68, 74, "20", "7", "W1", "6-4", "-109"),
    ],
    "NL West": [
        ("LAD", 85, 57, "--", "--", "W3", "5-5", "+150"),
        ("ARI", 75, 68, "10", "--", "W1", "5-5", "-2"),
        ("SDP", 74, 68, "11", "1", "L1", "3-7", "+7"),
        ("SFG", 59, 84, "26", "16", "W1", "5-5", "-73"),
        ("COL", 55, 87, "30", "20", "W1", "4-6", "-138"),
    ],
    "NL Wild Card": [
        ("CHC", 81, 62, "+6", "W3", "5-5", "+139", False),
        ("PHI", 80, 62, "+5", "W1", "7-3", "+35", False),
        ("ARI", 75, 68, "--", "W1", "5-5", "-2", True),
        ("SDP", 74, 68, "1", "L1", "3-7", "+7", False),
        ("MIA", 71, 72, "4", "L3", "4-6", "+8", False),
        ("STL", 71, 72, "4", "L1", "5-5", "-11", False),
    ],
}

UPCOMING = [
    ("MIL", "CIN", "Kyle Harrison vs. Brady Singer", "12:10 PM ET", "2026-09-06T16:10:00Z", ""),
    ("ATL", "PHI", "Tyler Mahle vs. Aaron Nola", "1:10 PM ET", "2026-09-06T17:10:00Z", ""),
    ("LAA", "PIT", "Walbert Urena vs. Paul Skenes", "1:35 PM ET", "2026-09-06T17:35:00Z", ""),
    ("BOS", "BAL", "Payton Tolle vs. Kyle Bradish", "1:35 PM ET", "2026-09-06T17:35:00Z", ""),
    ("CHC", "MIA", "Clay Holmes vs. Tyler Phillips", "1:40 PM ET", "2026-09-06T17:40:00Z", ""),
    ("DET", "CLE", "Jackson Jobe vs. Gavin Williams", "1:40 PM ET", "2026-09-06T17:40:00Z", ""),
    ("SFG", "NYM", "Cesar Perdomo vs. Christian Scott", "1:40 PM ET", "2026-09-06T17:40:00Z", ""),
    ("ARI", "HOU", "Eduardo Rodriguez vs. Peter Lambert", "2:10 PM ET", "2026-09-06T18:10:00Z", ""),
    ("TOR", "KCR", "Spencer Arrighetti vs. Randy Dobnak", "2:10 PM ET", "2026-09-06T18:10:00Z", ""),
    ("TBR", "TEX", "Ian Seymour vs. MacKenzie Gore", "2:35 PM ET", "2026-09-06T18:35:00Z", ""),
    ("STL", "COL", "Kyle Leahy vs. Tanner Gordon", "3:10 PM ET", "2026-09-06T19:10:00Z", ""),
    ("ATH", "SEA", "Gage Jump vs. Bryan Woo", "4:10 PM ET", "2026-09-06T20:10:00Z", ""),
    ("NYY", "SDP", "Gerrit Cole vs. Michael King", "4:10 PM ET", "2026-09-06T20:10:00Z", ""),
    ("MIN", "CHW", "Bailey Ober vs. Bryan Hudson", "6:20 PM ET", "2026-09-06T22:20:00Z", ""),
    ("WSN", "LAD", "Andrew Alvarez vs. Justin Wrobleski", "10:10 PM ET", "2026-09-07T02:10:00Z", ""),
]

OFF_TONIGHT: list[str] = []

TEAM_SUMMARIES = {
    "CHC": "Your Cubs: Conforto homered, Hoerner had three hits, 6-5 win at Miami. At Miami today.",
    "MIA": "Your Marlins: Lost 5-6 to Chicago. Host the Cubs today.",
    "SFG": "Your Giants: Devers and Koss each homered twice in a 9-5 win at Citi Field. At the Mets today.",
    "NYM": "Your Mets: Lost 5-9 to San Francisco. Host the Giants today.",
    "ATL": "Your Braves: Lost 2-4 in Philadelphia. NL East lead cut to four. At Philadelphia today.",
    "PHI": "Your Phillies: Wheeler six with nine Ks, Schwarber's 41st homer, 4-2 win. Host Atlanta today.",
    "DET": "Your Tigers: Greene two homers and four RBIs, Valdez seven scoreless in 6-0 shutout at Cleveland. At Cleveland today.",
    "CLE": "Your Guardians: Shut out 0-6 by Detroit. Host the Tigers today.",
    "LAA": "Your Angels: Kikuchi six scoreless, 6-1 win in Pittsburgh. At Pittsburgh today.",
    "PIT": "Your Pirates: Lost 1-6 to Los Angeles. Host the Angels today.",
    "MIL": "Your Brewers: Lost 3-5 in Cincinnati. At Cincinnati today.",
    "CIN": "Your Reds: Three homers in a 5-3 win over Milwaukee. Host the Brewers today.",
    "BOS": "Your Red Sox: Gray seven scoreless for his 17th win, 5-0 at Baltimore. At Baltimore today.",
    "BAL": "Your Orioles: Shut out 0-5 by Boston. Host the Red Sox today.",
    "TBR": "Your Rays: Aranda's three-run homer in the 10th, 6-3 win at Texas. At Texas today.",
    "TEX": "Your Rangers: Lost 3-6 in 10 to Tampa Bay. Host the Rays today.",
    "MIN": "Your Twins: Jeffers' three-run homer in a 6-4 win at Chicago. At the White Sox tonight.",
    "CHW": "Your White Sox: Lost 4-6 to Minnesota. Host the Twins tonight.",
    "TOR": "Your Blue Jays: Okamoto led a 4-3 win in Kansas City — tied for last AL wild-card spot. At Kansas City today.",
    "KCR": "Your Royals: Lost 3-4 to Toronto. Host the Blue Jays today.",
    "ARI": "Your Diamondbacks: Moreno's go-ahead single in the 10th, 4-3 win in Houston. At Houston today.",
    "HOU": "Your Astros: Lost 3-4 in 10 to Arizona. Host the Diamondbacks today.",
    "NYY": "Your Yankees: Spencer Jones sparked a four-run second in a 5-1 win at San Diego. At San Diego today.",
    "SDP": "Your Padres: Lost 1-5 to New York. Host the Yankees today.",
    "STL": "Your Cardinals: Lost 7-10 in Colorado despite Herrera's three RBIs. At Colorado today.",
    "COL": "Your Rockies: Six-run fifth inning in a 10-7 win over St. Louis. Host the Cardinals today.",
    "WSN": "Your Nationals: Lost 5-6 in Los Angeles. At Dodger Stadium tonight.",
    "LAD": "Your Dodgers: Edman and Hernández led a 6-5 win without Ohtani. Host Washington tonight.",
    "ATH": "Your Athletics: Springs seven shutout innings, Muncy homered, 6-2 at Seattle. At Seattle today.",
    "SEA": "Your Mariners: Lost 2-6 to Oakland. Host the Athletics today.",
}

RACE_AL_RECAP = (
    "Sonny Gray's seven scoreless innings earned his majors-leading 17th win. "
    "Jonathan Aranda's three-run homer in the 10th lifted Tampa Bay at Texas. "
    "Blue Jays edged Kansas City 4-3 to pull even in the wild-card race."
)
RACE_AL_SINCE = "Tampa Bay is 7-3 in its last ten."
RACE_NL_RECAP = (
    "Rafael Devers and Christian Koss each homered twice in San Francisco's 9-5 win. "
    "Zack Wheeler and Kyle Schwarber pulled Philadelphia within four in the NL East. "
    "Colorado scored six in the fifth and beat St. Louis 10-7."
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
    return m.group(1).replace("2026-09-04", ISSUE_DATE)


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
<title>Scorebook - Saturday, September 5</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Saturday, September 5" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Saturday, September 5" />
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
  <h1>Saturday, September 5</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("devers")}
  <p class="cap">{CLIPS["devers"]["cap"]}</p>
{clip_html("wheeler")}
  <p class="cap">{CLIPS["wheeler"]["cap"]}</p>
{clip_html("aranda")}
  <p class="cap">{CLIPS["aranda"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="devers" required> Devers and Koss each homer twice</label>
      <label><input type="radio" name="play" value="wheeler"> Wheeler and Schwarber cut NL East lead</label>
      <label><input type="radio" name="play" value="aranda"> Aranda walk-off in the 10th</label>
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
{clip_html("gray")}
  <p class="cap">{CLIPS["gray"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Bottom of the fifth at Coors Field. The Rockies sent ten batters to the plate and scored six runs on five hits — Hunter Goodman doubled among the damage. Colorado led 6–1 and won 10–7.</p>
{clip_html("rockies_fifth")}
  <p class="cap">{CLIPS["rockies_fifth"]["cap"]}</p>

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
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    html_path = OUT_DIR / "index.html"
    html_path.write_text(build_html(), encoding="utf-8")
    write_race_share_files()
    print(f"Wrote {html_path}")
    print(f"Wrote {OUT_DIR / 'share' / 'race-al.txt'}")
    print(f"Wrote {OUT_DIR / 'share' / 'race-nl.txt'}")


if __name__ == "__main__":
    main()
