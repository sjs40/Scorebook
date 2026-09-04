#!/usr/bin/env python3
"""Generate /workspace/2026-09-03/index.html and share race text files."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-03"
REF_HTML = ROOT / "2026-09-02" / "index.html"
ISSUE_DATE = "2026-09-03"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Rutschman homers twice in his Baltimore return. "
    "Quantrill and the Rangers shut out Tampa Bay. "
    "Jensen finishes a single shy of the cycle. "
    "Gausman and the Cubs edge Milwaukee 2–1."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/03"

CLIPS = {
    "rutschman": {
        "video": f"{MLB_CDN}/1cfb5f86-f5339216-0db849f6-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "adley-rutschman-collects-two-homers-in-stellar-return",
        "cap": (
            "Adley Rutschman: two solo homers in his return to Camden Yards — first-inning shot to right, "
            "sixth-inning drive to left. A month after Baltimore traded him to Boston. Red Sox 6, Orioles 5."
        ),
    },
    "quantrill": {
        "video": f"{MLB_CDN}/9ae36c60-b0a4baf0-c9b68ce7-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "cal-quantrill-twirls-seven-scoreless-innings",
        "cap": "Cal Quantrill: 7.0 IP, 2 H, 0 ER, 2 BB, 5 K. Corey Seager's two-run homer in the fifth. Rangers 6, Rays 0.",
    },
    "jensen": {
        "video": f"{MLB_CDN}/90005221-91bc31b8-5289d278-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "carter-jensen-seals-royals-win-with-homer-and-triple",
        "cap": (
            "Carter Jensen: home run, triple, and double — one single short of the cycle. "
            "Three RBIs. Royals 7, Marlins 3."
        ),
    },
    "pirates_pen": {
        "video": f"{MLB_CDN}/7e34ace5-22072552-d512e673-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "pirates-manufacture-runs-to-back-bullpen-in-5-2-win",
        "cap": (
            "Six Pittsburgh relievers combined on a two-hitter. "
            "Blade Tidwell lasted five. Khristian Curtis got the win. Pirates 5, Giants 2."
        ),
    },
    "jays_fifth": {
        "video": f"{MLB_CDN}/f5eba0dc-79ef1ad5-ecdaeea2-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "the-blue-jays-four-run-inning",
        "cap": "Four runs in the fifth. Nathan Lukes's two-run double with the bases loaded. Blue Jays led 5–1 and won 6–3.",
    },
}

PITCHERS = [
    ("Cal Quantrill", "TEX", 68, "7.0", 2, 0, 2, 5, "TBR"),
    ("Logan Henderson", "MIL", 64, "7.0", 3, 2, 0, 7, "CHC"),
    ("Kevin Gausman", "CHC", 64, "7.0", 5, 1, 1, 9, "MIL"),
    ("Jake Bennett", "BOS", 53, "6.0", 5, 3, 0, 7, "BAL"),
]

HITTERS = [
    ("Carter Jensen", "KCR", 9, 4, 3, 3, 1, 3, 0),
    ("Adley Rutschman", "BOS", 8, 4, 2, 2, 2, 2, 0),
    ("Christian Encarnacion-Strand", "BAL", 5, 3, 2, 1, 1, 2, 0),
    ("Zack Gelof", "ATH", 5, 5, 2, 1, 1, 1, 1),
    ("Tommy Edman", "LAD", 5, 5, 4, 1, 0, 0, 1),
    ("Jose Altuve", "HOU", 4, 4, 1, 1, 1, 2, 0),
    ("Nick Sogard", "BOS", 4, 3, 1, 1, 1, 2, 0),
    ("Pete Alonso", "BAL", 4, 3, 1, 1, 1, 2, 0),
]

# away, home, away_score, home_score, away_innings, home_innings, away_h, away_e, home_h, home_e, note
GAMES = [
    ("SFG", "PIT", 2, 5, [0, 0, 0, 0, 0, 0, 2, 0, 0], [2, 0, 0, 0, 0, 2, 0, 1, 0], 2, 1, 5, 0, "W Khristian Curtis · L Blade Tidwell · S Mason Montgomery"),
    ("TOR", "CLE", 6, 3, [0, 0, 0, 1, 4, 0, 0, 0, 1], [0, 0, 1, 0, 2, 0, 0, 0, 0], 9, 0, 8, 2, "W Spencer Miles · L Tanner Bibee · S Louis Varland"),
    ("CWS", "HOU", 2, 6, [0, 2, 0, 0, 0, 0, 0, 0, 0], [2, 0, 4, 0, 0, 0, 0, 0, 0], 7, 0, 8, 0, "W Hunter Brown · L Luis Castillo"),
    ("BOS", "BAL", 6, 5, [1, 0, 0, 0, 0, 1, 1, 2, 1], [1, 0, 0, 2, 0, 0, 0, 0, 2], 7, 0, 7, 1, "W Erik Miller · L Luis De León · S Aroldis Chapman"),
    ("MIL", "CHC", 1, 2, [0, 0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 2, 0, 0, 0, 0, 0, 0], 5, 0, 3, 0, "W Kevin Gausman · L Logan Henderson · S Ryan Rolison"),
    ("MIA", "KCR", 3, 7, [1, 1, 0, 1, 0, 0, 0, 0, 0], [0, 0, 2, 0, 2, 0, 0, 3, 0], 6, 0, 11, 0, "W Michael Wacha · L Sandy Alcantara"),
    ("TBR", "TEX", 0, 6, [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 3, 0, 0, 2, 0], 3, 0, 9, 0, "W Cal Quantrill · L Shane McClanahan"),
    ("ATH", "SEA", 7, 4, [1, 1, 0, 0, 2, 1, 0, 1, 1], [3, 0, 0, 0, 0, 1, 0, 0, 0], 14, 0, 9, 0, "W Scott Blewett · L Kade Anderson · S Hogan Harris"),
    ("STL", "LAD", 2, 3, [1, 0, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 2], 12, 0, 6, 0, "W Brock Stewart · L Riley O'Brien"),
]

FEATURED_KEYS = [
    ("BOS", "BAL"),
    ("TBR", "TEX"),
    ("MIA", "KCR"),
    ("MIL", "CHC"),
    ("TOR", "CLE"),
    ("SFG", "PIT"),
    ("CWS", "HOU"),
    ("ATH", "SEA"),
    ("STL", "LAD"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 83, 57, "--", "--", "L2", "6-4", "+45"),
        ("NYY", 80, 60, "3", "+10", "W2", "6-4", "+115"),
        ("BOS", 76, 65, "7.5", "+5.5", "W1", "4-6", "+78"),
        ("TOR", 70, 71, "13.5", "0.5", "W2", "6-4", "-41"),
        ("BAL", 69, 72, "14.5", "1.5", "L3", "6-4", "-21"),
    ],
    "AL Central": [
        ("CHW", 73, 67, "--", "--", "L2", "5-5", "+39"),
        ("CLE", 70, 70, "3", "--", "L2", "6-4", "-11"),
        ("MIN", 67, 73, "6", "3", "L1", "4-6", "-38"),
        ("DET", 64, 75, "8.5", "5.5", "W1", "3-7", "+47"),
        ("KCR", 63, 78, "10.5", "7.5", "W1", "6-4", "-85"),
    ],
    "AL West": [
        ("HOU", 72, 69, "--", "--", "W2", "7-3", "-38"),
        ("TEX", 70, 71, "2", "0.5", "W1", "5-5", "-42"),
        ("SEA", 66, 75, "6", "4", "L1", "4-6", "-68"),
        ("ATH", 55, 86, "17", "15", "W2", "4-6", "-191"),
        ("LAA", 53, 87, "18.5", "16.5", "L2", "1-9", "-80"),
    ],
    "AL Wild Card": [
        ("NYY", 80, 60, "+10", "W2", "6-4", "+115", False),
        ("BOS", 76, 65, "+5.5", "W1", "4-6", "+78", False),
        ("CLE", 70, 70, "--", "L2", "6-4", "-11", True),
        ("TOR", 70, 71, "0.5", "W2", "6-4", "-41", False),
        ("TEX", 70, 71, "0.5", "W1", "5-5", "-42", False),
        ("BAL", 69, 72, "1.5", "L3", "6-4", "-21", False),
    ],
    "NL East": [
        ("ATL", 83, 57, "--", "--", "W1", "8-2", "+118"),
        ("PHI", 79, 61, "4", "+5.5", "L1", "7-3", "+36"),
        ("MIA", 71, 70, "12.5", "3", "L1", "4-6", "+14"),
        ("WSN", 67, 75, "17", "7.5", "L1", "6-4", "+14"),
        ("NYM", 63, 77, "20", "10.5", "W1", "4-6", "-50"),
    ],
    "NL Central": [
        ("MIL", 87, 54, "--", "--", "L1", "6-4", "+171"),
        ("CHC", 79, 62, "8", "+5", "W1", "4-6", "+133"),
        ("STL", 70, 71, "17", "4", "L1", "4-6", "-9"),
        ("PIT", 69, 72, "18", "5", "W1", "6-4", "+29"),
        ("CIN", 67, 73, "19.5", "6.5", "W2", "5-5", "-108"),
    ],
    "NL West": [
        ("LAD", 83, 57, "--", "--", "W1", "4-6", "+147"),
        ("ARI", 74, 67, "9.5", "--", "W1", "5-5", "-1"),
        ("SDP", 73, 67, "10", "0.5", "L2", "3-7", "+10"),
        ("SFG", 58, 83, "25.5", "15.5", "L1", "5-5", "-73"),
        ("COL", 54, 86, "29", "19", "W2", "4-6", "-140"),
    ],
    "NL Wild Card": [
        ("PHI", 79, 61, "+5.5", "L1", "7-3", "+36", False),
        ("CHC", 79, 62, "+5", "W1", "4-6", "+133", False),
        ("ARI", 74, 67, "--", "W1", "5-5", "-1", True),
        ("SDP", 73, 67, "0.5", "L2", "3-7", "+10", False),
        ("MIA", 71, 70, "3", "L1", "4-6", "+14", False),
        ("STL", 70, 71, "4", "L1", "4-6", "-9", False),
    ],
}

UPCOMING = [
    ("DET", "CLE", "Keider Montero vs. Logan Allen", "2:10 PM ET", "2026-09-04T18:10:00Z", ""),
    ("MIL", "CIN", "Shane Drohan vs. Rhett Lowder", "6:10 PM ET", "2026-09-04T22:10:00Z", ""),
    ("ATL", "PHI", "Chris Sale vs. Cristopher Sánchez", "6:40 PM ET", "2026-09-04T22:40:00Z", ""),
    ("LAA", "PIT", "Ryan Johnson vs. Jared Jones", "6:45 PM ET", "2026-09-04T22:45:00Z", ""),
    ("BOS", "BAL", "Ranger Suarez vs. Shane Baz", "7:05 PM ET", "2026-09-04T23:05:00Z", ""),
    ("SFG", "NYM", "Matt Wilkinson vs. Nolan McLean", "7:10 PM ET", "2026-09-04T23:10:00Z", ""),
    ("CHC", "MIA", "Shota Imanaga vs. Janson Junk", "7:10 PM ET", "2026-09-04T23:10:00Z", ""),
    ("DET", "CLE", "Andrew Sears vs. Foster Griffin", "7:15 PM ET", "2026-09-04T23:15:00Z", "Game 2"),
    ("MIN", "CWS", "Zebby Matthews vs. Erick Fedde", "7:40 PM ET", "2026-09-04T23:40:00Z", ""),
    ("TBR", "TEX", "Nick Martinez vs. Trevor Williams", "8:05 PM ET", "2026-09-05T00:05:00Z", ""),
    ("ARI", "HOU", "Merrill Kelly vs. Cristian Javier", "8:10 PM ET", "2026-09-05T00:10:00Z", ""),
    ("TOR", "KCR", "Jameson Taillon vs. Daniel Lynch IV", "8:10 PM ET", "2026-09-05T00:10:00Z", ""),
    ("STL", "COL", "Andre Pallante vs. Ryan Feltner", "8:40 PM ET", "2026-09-05T00:40:00Z", ""),
    ("NYY", "SDP", "Max Fried vs. Walker Buehler", "9:40 PM ET", "2026-09-05T01:40:00Z", ""),
    ("WSN", "LAD", "Jackson Kent vs. Blake Snell", "10:10 PM ET", "2026-09-05T02:10:00Z", ""),
    ("ATH", "SEA", "Kade Morris vs. Logan Gilbert", "10:10 PM ET", "2026-09-05T02:10:00Z", ""),
]

OFF_TONIGHT: list[str] = []

TEAM_SUMMARIES = {
    "SFG": "Your Giants: Two hits against six Pirates relievers. Lost 2-5 at PNC Park. At the Mets tonight.",
    "PIT": "Your Pirates: Six relievers on a two-hitter. Won 5-2. Host the Angels tonight.",
    "TOR": "Your Blue Jays: Four-run fifth inning in a 6-3 win at Cleveland. Half a game out of the final wild-card spot. At Kansas City tonight.",
    "CLE": "Your Guardians: Lost 6-3 to Toronto. Host Detroit twice tonight.",
    "CWS": "Your White Sox: Lost 2-6 in Houston. Jose Altuve homered. Host Minnesota tonight.",
    "HOU": "Your Astros: Altuve homered, Varsho tripled in a 6-2 win over Chicago. Host Arizona tonight.",
    "BOS": "Your Red Sox: Rallied to beat Baltimore 6-5. Adley Rutschman homered twice in his return to Camden Yards. At Baltimore tonight.",
    "BAL": "Your Orioles: Rutschman hit two homers against his former club but lost 5-6. Host Boston tonight.",
    "MIL": "Your Brewers: Lost 1-2 at Wrigley. At Cincinnati tonight.",
    "CHC": "Your Cubs: Pete Crow-Armstrong homered, Kevin Gausman threw seven strong innings. Won 2-1. At Miami tonight.",
    "MIA": "Your Marlins: Lost 3-7 in Kansas City. Host the Cubs tonight.",
    "KCR": "Your Royals: Carter Jensen finished a single shy of the cycle in a 7-3 win. Host Toronto tonight.",
    "TBR": "Your Rays: Shut out 0-6 in Arlington. At Texas tonight.",
    "TEX": "Your Rangers: Cal Quantrill threw seven scoreless. Corey Seager homered. Won 6-0. Host Tampa Bay tonight.",
    "ATH": "Your Athletics: Won 7-4 in Seattle. Lawrence Butler drove in the go-ahead run. At Seattle tonight.",
    "SEA": "Your Mariners: Lost 4-7 to Oakland. Host the Athletics tonight.",
    "STL": "Your Cardinals: Lost 2-3 on a walk-off in Los Angeles. At Colorado tonight.",
    "LAD": "Your Dodgers: Teoscar Hernández doubled in two runs in the ninth. Won 3-2. Host Washington tonight.",
    "ATL": "Your Braves: Off Thursday. At Philadelphia tonight.",
    "PHI": "Your Phillies: Off Thursday. Host Atlanta tonight.",
    "WSN": "Your Nationals: Off Thursday. At Dodger Stadium tonight.",
    "NYM": "Your Mets: Off Thursday. Host San Francisco tonight.",
    "CIN": "Your Reds: Off Thursday. Host Milwaukee tonight.",
    "SDP": "Your Padres: Off Thursday. Host the Yankees tonight.",
    "ARI": "Your Diamondbacks: Off Thursday. At Houston tonight.",
    "COL": "Your Rockies: Off Thursday. Host St. Louis tonight.",
    "NYY": "Your Yankees: Off Thursday. At San Diego tonight.",
    "MIN": "Your Twins: Off Thursday. At the White Sox tonight.",
    "DET": "Your Tigers: Off Thursday. At Cleveland twice tonight.",
    "LAA": "Your Angels: Off Thursday. At Pittsburgh tonight.",
}

RACE_AL_RECAP = (
    "Adley Rutschman homered twice in his Baltimore return. "
    "Cal Quantrill shut out Tampa Bay over seven. Blue Jays won 6-3 in Cleveland. "
    "Royals beat Miami behind Carter Jensen's near-cycle."
)
RACE_AL_SINCE = "Houston is 7-3 in its last ten."
RACE_NL_RECAP = (
    "Pete Crow-Armstrong homered, Kevin Gausman dominated in the Cubs' 2-1 win. "
    "Teoscar Hernández walked off the Dodgers in the ninth. "
    "Six Pirates relievers two-hit the Giants."
)
RACE_NL_SINCE = "Atlanta is 8-2 in its last ten."


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
    return m.group(1).replace("2026-09-02", ISSUE_DATE)


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
<title>Scorebook - Thursday, September 3</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Thursday, September 3" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Thursday, September 3" />
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
  <p class="kicker">Thursday night</p>
  <h1>Thursday, September 3</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("rutschman")}
  <p class="cap">{CLIPS["rutschman"]["cap"]}</p>
{clip_html("quantrill")}
  <p class="cap">{CLIPS["quantrill"]["cap"]}</p>
{clip_html("jensen")}
  <p class="cap">{CLIPS["jensen"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="rutschman" required> Rutschman two homers in Baltimore return</label>
      <label><input type="radio" name="play" value="quantrill"> Quantrill seven scoreless</label>
      <label><input type="radio" name="play" value="jensen"> Jensen near-cycle</label>
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
{clip_html("pirates_pen")}
  <p class="cap">{CLIPS["pirates_pen"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Top of the fifth at Progressive Field. Toronto sent eight batters to the plate and scored four runs — a single, a walk, a two-run double from Nathan Lukes with the bases loaded, and an RBI single from Ernie Clement. The Blue Jays led 5–1. They won 6–3.</p>
{clip_html("jays_fifth")}
  <p class="cap">{CLIPS["jays_fifth"]["cap"]}</p>

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
      <p class="subn">Standings through Thursday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
{al_tables}
    </div>

    <div class="panel-nl" id="nl-panel">
      <div class="recap" data-share-card="race-nl.png" data-share-text-src="share/race-nl.txt">
        <p class="subn">Last night</p>
        <p>{RACE_NL_RECAP}</p>
        <p class="subn">Since August 13</p>
        <p>{RACE_NL_SINCE}</p>
      </div>
      <p class="subn">Standings through Thursday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
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
