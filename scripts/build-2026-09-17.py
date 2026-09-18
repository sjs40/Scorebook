#!/usr/bin/env python3
"""Generate /workspace/2026-09-17/index.html and share race text files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-17"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-09-16" / "index.html"
ISSUE_DATE = "2026-09-17"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Kyle Tucker went 4-for-5 and the Dodgers clinched the NL West in an 8–2 win at Cincinnati. "
    "Tampa Bay scored six in the fourth in a 10–1 rout of Oakland. "
    "Aaron Nola shut out the Mets on three hits over seven in a 3–0 win. "
    "Wade Meckler's walk-off in the 10th lifted the Angels past Minnesota 5–4."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/17"

CLIPS = {
    "tucker_clinch": {
        "video": f"{MLB_CDN}/c5c274c7-b62b0b0f-e06edc46-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "kyle-tucker-leads-dodgers-win-division-clincher",
        "cap": (
            "Kyle Tucker went 4-for-5 with a homer and three RBIs — Los Angeles clinched its fifth straight NL West title. "
            "Dodgers 8, Reds 2."
        ),
    },
    "nola_shutout": {
        "video": f"{MLB_CDN}/573704e3-2124023b-1d863aea-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "aaron-nola-twirls-a-gem-in-shutuout-win",
        "cap": (
            "Aaron Nola: seven scoreless innings, three hits, and four strikeouts. "
            "Phillies 3, Mets 0."
        ),
    },
    "meckler_walkoff": {
        "video": f"{MLB_CDN}/3c07e3bf-da8cf04c-c004ef39-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "wade-meckler-s-walk-off-lifts-angels-over-twins-5-4",
        "cap": (
            "Wade Meckler singled with one out in the 10th — Minnesota and Los Angeles were tied 4–4. "
            "Angels 5, Twins 4 — Walbert Ureña fanned nine over seven scoreless innings."
        ),
    },
    "grichuk_throw": {
        "video": None,
        "slug": "bryan-hudson-in-play-out-s-to-spencer-torkelson",
        "cap": (
            "Detroit had a runner at third with one out in the seventh when Randal Grichuk threw out Spencer Torkelson at the plate — "
            "and the White Sox still won 3–1. That's baseball."
        ),
    },
    "rays_six_spot": {
        "video": f"{MLB_CDN}/46142c2e-d37f7dad-11f0c148-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "tampa-bay-puts-up-a-six-spot-in-the-4th-inning",
        "cap": (
            "Six runs in the fourth keyed a 10–1 rout — Chandler Simpson drove in two and stole twice. "
            "Rays 10, Athletics 1."
        ),
    },
    "padres_seven_run": {
        "video": f"{MLB_CDN}/3a9a20f3-42ca3083-194ad2f3-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "padres-offense-erupts-for-a-seven-run-2nd-inning",
        "cap": (
            "San Diego scored seven in the second — Xander Bogaerts homered and drove in two. "
            "Padres 9, Rockies 2."
        ),
    },
}

PITCHERS = [
    ("Walbert Ureña", "LAA", 79, "7.0", 4, 0, 0, 9, "MIN"),
    ("Aaron Nola", "PHI", 63, "7.0", 3, 0, 3, 4, "NYM"),
    ("Ethan Pecko", "HOU", 62, "5.2", 3, 1, 0, 4, "KCR"),
    ("Taj Bradley", "MIN", 61, "7.0", 5, 3, 1, 9, "LAA"),
]

HITTERS = [
    ("Kyle Tucker", "LAD", 9, 5, 4, 3, 1, 3, 0),
    ("Xander Bogaerts", "SDP", 9, 5, 3, 3, 1, 2, 0),
    ("Munetaka Murakami", "CWS", 7, 4, 2, 2, 1, 3, 0),
    ("Walker Jenkins", "MIN", 6, 4, 3, 1, 1, 2, 0),
    ("LaMonte Wade Jr.", "HOU", 6, 4, 2, 2, 1, 1, 0),
    ("Trevor Story", "BOS", 5, 4, 2, 1, 1, 3, 0),
    ("Jeremy Peña", "HOU", 5, 5, 2, 1, 1, 2, 0),
    ("Miguel Rojas", "LAD", 5, 5, 2, 1, 1, 1, 0),
]

GAMES = [
    ("MIL", "PIT", 4, 7, [0, 1, 0, 0, 0, 1, 0, 2, 0], [0, 5, 0, 0, 0, 0, 0, 2, 0], 9, 1, 7, 1, "W Khristian Curtis · L Kyle Harrison · S Mason Montgomery"),
    ("LAD", "CIN", 8, 2, [2, 2, 0, 3, 0, 0, 0, 0, 1], [0, 0, 0, 1, 0, 0, 0, 0, 1], 12, 0, 7, 0, "W Landon Knack · L Brady Singer"),
    ("ATH", "TBR", 1, 10, [0, 0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 6, 0, 2, 0, 2, 0], 5, 2, 7, 1, "W Drew Rasmussen · L Jeffrey Springs"),
    ("SDP", "COL", 9, 2, [0, 7, 0, 0, 2, 0, 0, 0, 0], [1, 0, 0, 0, 0, 1, 0, 0, 0], 15, 0, 9, 1, "W Michael King · L Tanner Gordon"),
    ("KCR", "HOU", 2, 6, [1, 0, 0, 0, 0, 0, 0, 1, 0], [1, 1, 0, 0, 2, 1, 0, 1, 0], 3, 0, 11, 0, "W Bryan King · L Seth Lugo"),
    ("PHI", "NYM", 3, 0, [0, 0, 0, 0, 1, 0, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], 8, 0, 4, 1, "W Aaron Nola · L Nolan McLean · S Jhoan Duran"),
    ("DET", "CWS", 1, 3, [0, 0, 1, 0, 0, 0, 0, 0, 0], [3, 0, 0, 0, 0, 0, 0, 0, 0], 8, 1, 5, 0, "W Bryan Hudson · L Framber Valdez · S Grant Taylor"),
    ("BOS", "TEX", 4, 3, [0, 0, 0, 0, 0, 0, 1, 3, 0], [1, 2, 0, 0, 0, 0, 0, 0, 0], 5, 0, 4, 1, "W Wyatt Olds · L Jacob Latz · S Garrett Whitlock"),
    ("MIN", "LAA", 4, 5, [0, 0, 0, 0, 0, 0, 0, 1, 2, 1], [3, 0, 0, 0, 0, 0, 0, 0, 0, 2], 10, 0, 8, 0, "W Blake Weiman · L Yoendrys Gómez"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 93, 59, "--", "--", "W6", "9-2", "+80"),
        ("NYY", 88, 64, "5.0", "+10.5", "L1", "7-3", "+136"),
        ("BOS", 83, 70, "10.5", "+5.0", "W1", "6-4", "+83"),
        ("TOR", 76, 77, "17.0", "2.0", "W1", "4-6", "-37"),
        ("BAL", 75, 78, "18.0", "3.0", "W3", "6-4", "-26"),
    ],
    "AL Central": [
        ("CLE", 78, 75, "--", "--", "W2", "6-4", "-7"),
        ("CWS", 78, 75, "--", "--", "W1", "4-6", "+36"),
        ("DET", 72, 81, "6.0", "6.0", "L2", "6-4", "+74"),
        ("MIN", 71, 82, "7.0", "7.0", "L1", "3-8", "-74"),
        ("KCR", 67, 86, "11.0", "11.0", "L1", "4-7", "-97"),
    ],
    "AL West": [
        ("HOU", 77, 76, "--", "--", "W1", "4-6", "-50"),
        ("TEX", 76, 77, "1.0", "2.0", "L1", "6-5", "-39"),
        ("SEA", 71, 82, "6.0", "7.0", "W1", "5-5", "-56"),
        ("ATH", 61, 92, "16.0", "17.0", "L3", "5-6", "-214"),
        ("LAA", 59, 94, "18.0", "19.0", "W1", "5-5", "-77"),
    ],
    "AL Wild Card": [
        ("NYY", 88, 64, "+10.5", "L1", "7-3", "+136", False),
        ("BOS", 83, 70, "+5.0", "W1", "6-4", "+83", False),
        ("CWS", 78, 75, "--", "W1", "4-6", "+36", True),
        ("TEX", 76, 77, "2.0", "L1", "6-5", "-39", False),
        ("TOR", 76, 77, "2.0", "W1", "4-6", "-37", False),
        ("BAL", 75, 78, "3.0", "W3", "6-4", "-26", False),
    ],
    "NL East": [
        ("ATL", 89, 64, "--", "--", "L1", "4-6", "+111"),
        ("PHI", 85, 68, "4.0", "+1.0", "W2", "5-5", "+34"),
        ("MIA", 76, 77, "13.0", "8.0", "W2", "5-5", "+8"),
        ("WSN", 71, 82, "18.0", "13.0", "L1", "4-6", "+3"),
        ("NYM", 69, 84, "20.0", "15.0", "L5", "5-6", "-46"),
    ],
    "NL Central": [
        ("MIL", 95, 58, "--", "--", "L1", "7-4", "+197"),
        ("CHC", 85, 68, "10.0", "+1.0", "W1", "4-6", "+143"),
        ("PIT", 76, 77, "19.0", "8.0", "W1", "6-4", "+24"),
        ("STL", 75, 78, "20.0", "9.0", "L2", "4-6", "-14"),
        ("CIN", 71, 82, "24.0", "13.0", "L1", "3-8", "-154"),
    ],
    "NL West": [
        ("LAD", 93, 60, "--", "--", "W1", "8-2", "+179"),
        ("SDP", 84, 69, "9.0", "--", "W2", "10-0", "+30"),
        ("ARI", 80, 73, "13.0", "4.0", "L2", "5-5", "0"),
        ("SFG", 64, 89, "29.0", "20.0", "W2", "5-5", "-70"),
        ("COL", 56, 97, "37.0", "28.0", "L2", "1-10", "-177"),
    ],
    "NL Wild Card": [
        ("CHC", 85, 68, "+1.0", "W1", "4-6", "+143", False),
        ("PHI", 85, 68, "+1.0", "W2", "5-5", "+34", False),
        ("SDP", 84, 69, "--", "W2", "10-0", "+30", True),
        ("ARI", 80, 73, "4.0", "L2", "5-5", "0", False),
        ("MIA", 76, 77, "8.0", "W2", "5-5", "+8", False),
        ("PIT", 76, 77, "8.0", "W1", "6-4", "+24", False),
    ],
}

UPCOMING = [
    ("CHC", "CIN", "Clay Holmes vs. Chase Burns", "6:40 PM ET", "2026-09-18T22:40:00Z", ""),
    ("KCR", "PIT", "Randy Dobnak vs. Paul Skenes", "6:40 PM ET", "2026-09-18T22:40:00Z", ""),
    ("MIL", "BAL", "Dustin May vs. TBD", "7:05 PM ET", "2026-09-18T23:05:00Z", ""),
    ("ATH", "CLE", "Mason Barnett vs. Daniel Espino", "7:10 PM ET", "2026-09-18T23:10:00Z", ""),
    ("BOS", "TBR", "Ranger Suarez vs. Ian Seymour", "7:10 PM ET", "2026-09-18T23:10:00Z", ""),
    ("PHI", "NYM", "TBD vs. Zac Thornton", "7:15 PM ET", "2026-09-18T23:15:00Z", ""),
    ("DET", "CWS", "Andrew Sears vs. David Sandlin", "7:40 PM ET", "2026-09-18T23:40:00Z", ""),
    ("TOR", "TEX", "Dylan Cease vs. Kumar Rocker", "8:05 PM ET", "2026-09-19T00:05:00Z", ""),
    ("SEA", "COL", "Bryan Woo vs. TBD", "8:10 PM ET", "2026-09-19T00:10:00Z", ""),
    ("ATL", "HOU", "Tyler Mahle vs. Peter Lambert", "8:10 PM ET", "2026-09-19T00:10:00Z", ""),
    ("WSN", "STL", "Cade Cavalli vs. Kyle Leahy", "8:15 PM ET", "2026-09-19T00:15:00Z", ""),
    ("MIN", "LAA", "Connor Prielipp vs. Grayson Rodriguez", "9:38 PM ET", "2026-09-19T01:38:00Z", ""),
    ("MIA", "SDP", "Tyler Phillips vs. Nick Pivetta", "9:40 PM ET", "2026-09-19T01:40:00Z", ""),
    ("NYY", "ARI", "Gerrit Cole vs. Eduardo Rodriguez", "9:40 PM ET", "2026-09-19T01:40:00Z", ""),
    ("SFG", "LAD", "Cesar Perdomo vs. Tyler Glasnow", "10:15 PM ET", "2026-09-19T02:15:00Z", ""),
]

OFF_TONIGHT = ["ATL", "BAL", "CHC", "CLE", "MIA", "NYY", "SEA", "SFG", "STL", "TOR", "WSN", "ARI"]

TEAM_SUMMARIES = {
    "CHC": "Your Cubs: Off today. At Cincinnati tonight.",
    "MIL": "Your Brewers: Lost 4–7 at Pittsburgh; Harrison took the loss. At Baltimore tonight.",
    "PIT": "Your Pirates: Won 7–4 over Milwaukee; Curtis earned the win. Host Kansas City tonight.",
    "LAD": "Your Dodgers: Won 8–2 at Cincinnati; Tucker went 4-for-5 and Los Angeles clinched the NL West. At San Francisco tonight.",
    "CIN": "Your Reds: Lost 2–8 to Los Angeles; Singer took the loss. Host Chicago tonight.",
    "ATH": "Your Athletics: Lost 1–10 at Tampa Bay; Springs took the loss. At Cleveland tonight.",
    "TBR": "Your Rays: Won 10–1 over Oakland; Rasmussen went five scoreless. Host Boston tonight.",
    "SDP": "Your Padres: Won 9–2 at Colorado; seven runs in the second keyed the win. At Miami tonight.",
    "COL": "Your Rockies: Lost 2–9 to San Diego; Gordon took the loss. Host Seattle tonight.",
    "KCR": "Your Royals: Lost 2–6 at Houston; Lugo took the loss. At Pittsburgh tonight.",
    "HOU": "Your Astros: Won 6–2 over Kansas City; five homers keyed the win. Host Atlanta tonight.",
    "PHI": "Your Phillies: Won 3–0 at New York; Nola shut them out for seven. At New York tonight.",
    "NYM": "Your Mets: Lost 0–3 to Philadelphia; McLean went six innings. Host Philadelphia tonight.",
    "DET": "Your Tigers: Lost 1–3 at Chicago; Valdez took the loss. At Chicago tonight.",
    "CWS": "Your White Sox: Won 3–1 over Detroit; Murakami's three-run homer in the first. Host Detroit tonight.",
    "BOS": "Your Red Sox: Won 4–3 at Texas; Story's three-run homer in the eighth. At Tampa Bay tonight.",
    "TEX": "Your Rangers: Lost 3–4 to Boston; Latz took the loss. Host Toronto tonight.",
    "MIN": "Your Twins: Lost 4–5 in 10 at Los Angeles; Meckler's walk-off ended it. At Los Angeles tonight.",
    "LAA": "Your Angels: Won 5–4 in 10 over Minnesota; Meckler walked it off. Host Minnesota tonight.",
    "ATL": "Your Braves: Off today. At Houston tonight.",
    "BAL": "Your Orioles: Off today. Host Milwaukee tonight.",
    "CLE": "Your Guardians: Off today. Host Athletics tonight.",
    "MIA": "Your Marlins: Off today. Host San Diego tonight.",
    "NYY": "Your Yankees: Off today. At Arizona tonight.",
    "SEA": "Your Mariners: Off today. At Colorado tonight.",
    "SFG": "Your Giants: Off today. Host Los Angeles tonight.",
    "STL": "Your Cardinals: Off today. Host Washington tonight.",
    "TOR": "Your Blue Jays: Off today. At Texas tonight.",
    "WSN": "Your Nationals: Off today. At St. Louis tonight.",
    "ARI": "Your Diamondbacks: Off today. Host New York tonight.",
}

RACE_AL_RECAP = (
    "Tampa Bay scored six in the fourth in a 10–1 rout of Oakland. "
    "Trevor Story's three-run homer in the eighth lifted Boston past Texas 4–3. "
    "Houston hit five homers in a 6–2 win over Kansas City."
)
RACE_AL_SINCE = "The Rays are 9–2 in their last ten."
RACE_NL_RECAP = (
    "Kyle Tucker went 4-for-5 and the Dodgers clinched the NL West in an 8–2 win at Cincinnati. "
    "San Diego scored seven in the second in a 9–2 win at Colorado. "
    "Aaron Nola shut out the Mets on three hits over seven in a 3–0 win."
)
RACE_NL_SINCE = "The Padres are 10–0 in their last ten."


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
    return m.group(1).replace("2026-09-16", ISSUE_DATE)


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
<title>Scorebook - Thursday, September 17</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Thursday, September 17" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Thursday, September 17" />
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
  <h1>Thursday, September 17</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("tucker_clinch")}
  <p class="cap">{CLIPS["tucker_clinch"]["cap"]}</p>
{clip_html("nola_shutout")}
  <p class="cap">{CLIPS["nola_shutout"]["cap"]}</p>
{clip_html("meckler_walkoff")}
  <p class="cap">{CLIPS["meckler_walkoff"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="tucker_clinch" required> Tucker's four-hit day and NL West clinch</label>
      <label><input type="radio" name="play" value="nola_shutout"> Nola's shutout</label>
      <label><input type="radio" name="play" value="meckler_walkoff"> Meckler's walk-off in the 10th</label>
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
{clip_html("grichuk_throw", video=False)}
  <p class="cap">{CLIPS["grichuk_throw"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Bottom of the fourth at Tropicana Field. Tampa Bay led 1–0 when the Rays put up six — Chandler Simpson drove in two and stole twice. Rays 10, Athletics 1.</p>
{clip_html("rays_six_spot")}
  <p class="cap">{CLIPS["rays_six_spot"]["cap"]}</p>

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
