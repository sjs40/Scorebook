#!/usr/bin/env python3
"""Generate /workspace/2026-09-21/index.html and share race text files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "2026-09-21"
TEMPLATE_DIR = ROOT / "templates" / "default"
REF_HTML = ROOT / "2026-09-20" / "index.html"
ISSUE_DATE = "2026-09-21"
ISSUE_URL = f"https://getscorebook.com/{ISSUE_DATE}"
BEEHIIV_FORM = "9c7dfc79-2b79-46fd-ae61-3320bbbebe82"

DEK = (
    "Pete Alonso homered twice and drove in three in Baltimore's 4–3 win over Toronto. "
    "Detroit scored nine, keyed by a five-run fifth, in a rout of Washington. "
    "Drew Gilbert homered and drove in three as San Francisco beat Minnesota 5–2."
)

MLB_CDN = "https://mlb-cuts-diamond.mlb.com/FORGE/2026/2026-09/21"

CLIPS = {
    "alonso_two_homers": {
        "video": f"{MLB_CDN}/517ccb90-badc7778-c86bb765-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "pete-alonso-s-two-homer-game-powers-orioles-to-win",
        "cap": (
            "Pete Alonso homered twice and drove in three — "
            "Baltimore rallied past Toronto. Orioles 4, Blue Jays 3."
        ),
    },
    "tigers_five_run_fifth": {
        "video": f"{MLB_CDN}/00b1d0fb-2fa3419d-71aeb5d3-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "tigers-score-five-runs-in-the-5th-inning",
        "cap": (
            "Detroit put up five in the fifth — part of a nine-run night at Comerica Park. "
            "Tigers 9, Nationals 2."
        ),
    },
    "gilbert_homer": {
        "video": f"{MLB_CDN}/39c6c622-810e93bc-9a03e5cf-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "drew-gilbert-homers-in-giants-5-2-win",
        "cap": (
            "Drew Gilbert went deep and drove in three — "
            "San Francisco scored four in the first two innings. Giants 5, Twins 2."
        ),
    },
    "jays_early_lead": {
        "video": f"{MLB_CDN}/5222b528-9a051c7b-5a47e99e-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "tyler-rogers-in-play-run-s-to-pete-alonso",
        "cap": (
            "Toronto put up three in the first — and still lost when Pete Alonso "
            "homered twice. That's baseball."
        ),
    },
    "tigers_five_run_fifth_inning": {
        "video": f"{MLB_CDN}/00b1d0fb-2fa3419d-71aeb5d3-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
        "slug": "tigers-score-five-runs-in-the-5th-inning",
        "cap": (
            "Detroit put up five in the fifth — part of a nine-run rout. "
            "Tigers 9, Nationals 2."
        ),
    },
}

PITCHERS = [
    ("Shane Baz", "BAL", 86, "6.2", 5, 3, 3, 2, "TOR"),
    ("Zebby Matthews", "MIN", 77, "5.0", 8, 5, 0, 9, "SFG"),
]

HITTERS = [
    ("Pete Alonso", "BAL", 8, 4, 2, 2, 2, 3, 0),
    ("Gunnar Henderson", "BAL", 8, 4, 3, 2, 1, 1, 0),
    ("Drew Gilbert", "SFG", 6, 4, 3, 1, 1, 3, 0),
    ("Ben Malgeri", "DET", 6, 4, 2, 2, 1, 3, 0),
    ("Hao-Yu Lee", "DET", 5, 5, 3, 2, 0, 1, 0),
    ("Eduardo Valencia", "DET", 5, 4, 3, 2, 0, 0, 0),
    ("Yohandy Morales", "WSN", 4, 1, 1, 1, 1, 2, 0),
    ("Javier Báez", "DET", 4, 2, 1, 1, 1, 2, 0),
]

GAMES = [
    ("TOR", "BAL", 3, 4, [3, 0, 0, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 1, 0, 2, 0], 6, 0, 6, 0, "W Yennier Cano · L Tyler Rogers · S Rico Garcia"),
    ("WSN", "DET", 2, 9, [0, 0, 0, 0, 0, 0, 0, 2, 0], [2, 0, 0, 2, 5, 0, 0, 0, 0], 5, 1, 12, 1, "W Keider Montero · L DJ Herz"),
    ("MIN", "SFG", 2, 5, [0, 0, 0, 1, 0, 0, 0, 1, 0], [2, 2, 0, 0, 1, 0, 0, 0, 0], 4, 0, 10, 0, "W Tristan Beck · L Zebby Matthews · S Trent Harris"),
]

STANDINGS = {
    "AL East": [
        ("TBR", 95, 60, "--", "--", "W2", "8-2", "+83"),
        ("NYY", 89, 66, "6.0", "+9.5", "L2", "6-4", "+137"),
        ("BOS", 84, 72, "11.5", "+4.0", "L2", "4-6", "+80"),
        ("TOR", 77, 80, "19.0", "3.5", "L1", "4-6", "-43"),
        ("BAL", 76, 81, "20.0", "4.5", "W1", "5-5", "-30"),
    ],
    "AL Central": [
        ("CLE", 81, 75, "--", "--", "W5", "7-3", "+2"),
        ("CWS", 80, 76, "1.0", "--", "W2", "5-5", "+42"),
        ("DET", 74, 83, "7.5", "6.5", "W1", "6-4", "+75"),
        ("MIN", 73, 84, "8.5", "7.5", "L1", "4-6", "-67"),
        ("KCR", 67, 89, "14.0", "13.0", "L4", "3-7", "-102"),
    ],
    "AL West": [
        ("TEX", 78, 78, "--", "--", "L1", "6-4", "-34"),
        ("HOU", 77, 79, "1.0", "3.0", "L3", "3-7", "-59"),
        ("SEA", 73, 83, "5.0", "7.0", "W1", "5-5", "-56"),
        ("ATH", 61, 95, "17.0", "19.0", "L6", "3-7", "-223"),
        ("LAA", 60, 96, "18.0", "20.0", "L1", "4-6", "-87"),
    ],
    "AL Wild Card": [
        ("NYY", 89, 66, "+9.5", "L2", "6-4", "+137", False),
        ("BOS", 84, 72, "+4.0", "L2", "4-6", "+80", False),
        ("CWS", 80, 76, "--", "W2", "5-5", "+42", True),
        ("HOU", 77, 79, "3.0", "L3", "3-7", "-59", False),
        ("TOR", 77, 80, "3.5", "L1", "4-6", "-43", False),
        ("BAL", 76, 81, "4.5", "W1", "5-5", "-30", False),
    ],
    "NL East": [
        ("ATL", 92, 64, "--", "--", "W3", "7-3", "+120"),
        ("PHI", 86, 70, "6.0", "--", "W1", "4-6", "+29"),
        ("MIA", 76, 80, "16.0", "10.0", "L3", "4-6", "-3"),
        ("WSN", 73, 84, "19.5", "13.5", "L2", "6-4", "+5"),
        ("NYM", 71, 85, "21.0", "15.0", "L1", "3-7", "-41"),
    ],
    "NL Central": [
        ("MIL", 98, 58, "--", "--", "W3", "8-2", "+202"),
        ("CHC", 87, 69, "11.0", "+1.0", "W2", "6-4", "+152"),
        ("PIT", 79, 77, "19.0", "7.0", "W4", "6-4", "+29"),
        ("STL", 76, 80, "22.0", "10.0", "W1", "4-6", "-23"),
        ("CIN", 72, 84, "26.0", "14.0", "L2", "3-7", "-163"),
    ],
    "NL West": [
        ("LAD", 96, 60, "--", "--", "W4", "7-3", "+193"),
        ("SDP", 87, 69, "9.0", "+1.0", "W5", "9-1", "+41"),
        ("ARI", 82, 74, "14.0", "4.0", "W2", "4-6", "-1"),
        ("SFG", 65, 92, "31.5", "21.5", "W1", "3-7", "-81"),
        ("COL", 57, 99, "39.0", "29.0", "L1", "2-8", "-177"),
    ],
    "NL Wild Card": [
        ("CHC", 87, 69, "+1.0", "W2", "6-4", "+152", False),
        ("SDP", 87, 69, "+1.0", "W5", "9-1", "+41", False),
        ("PHI", 86, 70, "--", "W1", "4-6", "+29", True),
        ("ARI", 82, 74, "4.0", "W2", "4-6", "-1", False),
        ("PIT", 79, 77, "7.0", "W4", "6-4", "+29", False),
        ("MIA", 76, 80, "10.0", "L3", "4-6", "-3", False),
    ],
}

UPCOMING = [
    ("TBR", "NYY", "Nick Martinez vs. Carlos Rodón", "1:05 PM ET", "2026-09-22T17:05:00Z", "Game 1 of doubleheader"),
    ("TBR", "NYY", "Drew Rasmussen vs. Max Fried", "7:05 PM ET", "2026-09-22T23:05:00Z", "Game 2 of doubleheader"),
    ("TOR", "BAL", "Max Scherzer vs. Chris Bassitt", "6:35 PM ET", "2026-09-22T22:35:00Z", ""),
    ("WSN", "DET", "Jackson Kent vs. Drew Anderson", "6:40 PM ET", "2026-09-22T22:40:00Z", ""),
    ("STL", "PIT", "Andre Pallante vs. Jared Jones", "6:40 PM ET", "2026-09-22T22:40:00Z", ""),
    ("MIL", "PHI", "Dustin May vs. Zack Wheeler", "6:40 PM ET", "2026-09-22T22:40:00Z", ""),
    ("CLE", "BOS", "Parker Messick vs. Payton Tolle", "6:45 PM ET", "2026-09-22T22:45:00Z", ""),
    ("CIN", "ATL", "Brandon Williamson vs. JR Ritchie", "7:15 PM ET", "2026-09-22T23:15:00Z", ""),
    ("CWS", "KCR", "Anthony Kay vs. Daniel Lynch IV", "7:40 PM ET", "2026-09-22T23:40:00Z", ""),
    ("MIA", "CHC", "Janson Junk vs. TBD", "7:40 PM ET", "2026-09-22T23:40:00Z", ""),
    ("NYM", "TEX", "Sean Manaea vs. MacKenzie Gore", "8:05 PM ET", "2026-09-23T00:05:00Z", ""),
    ("ARI", "COL", "Michael Soroka vs. Kyle Freeland", "8:40 PM ET", "2026-09-23T00:40:00Z", ""),
    ("LAA", "ATH", "Yusei Kikuchi vs. Brady Basso", "9:40 PM ET", "2026-09-23T01:40:00Z", ""),
    ("HOU", "SEA", "Cristian Javier vs. Logan Gilbert", "9:40 PM ET", "2026-09-23T01:40:00Z", ""),
    ("MIN", "SFG", "Taj Bradley vs. Anthony Molina", "9:45 PM ET", "2026-09-23T01:45:00Z", ""),
    ("SDP", "LAD", "Michael King vs. TBD", "10:10 PM ET", "2026-09-23T02:10:00Z", ""),
]

OFF_TONIGHT: list[str] = []

TEAM_SUMMARIES = {
    "TOR": "Your Blue Jays: Lost 3–4 at Baltimore; Rogers took the loss. At Baltimore tonight.",
    "BAL": "Your Orioles: Beat Toronto 4–3; Alonso homered twice. Host Toronto tonight.",
    "WSN": "Your Nationals: Lost 2–9 at Detroit; Herz took the loss. At Detroit tonight.",
    "DET": "Your Tigers: Won 9–2 over Washington; Montero earned the win. Host Washington tonight.",
    "MIN": "Your Twins: Lost 2–5 at San Francisco; Matthews took the loss. At San Francisco tonight.",
    "SFG": "Your Giants: Won 5–2 over Minnesota; Gilbert homered. Host Minnesota tonight.",
    "CHC": "Your Cubs: Off last night. Host Miami tonight.",
    "CIN": "Your Reds: Off last night. At Atlanta tonight.",
    "KCR": "Your Royals: Off last night. Host White Sox tonight.",
    "PIT": "Your Pirates: Off last night. Host St. Louis tonight.",
    "MIL": "Your Brewers: Off last night. At Philadelphia tonight.",
    "ATH": "Your Athletics: Off last night. Host Angels tonight.",
    "CLE": "Your Guardians: Off last night. At Boston tonight.",
    "BOS": "Your Red Sox: Off last night. Host Cleveland tonight.",
    "TBR": "Your Rays: Off last night. At New York tonight (doubleheader).",
    "PHI": "Your Phillies: Off last night. Host Milwaukee tonight.",
    "NYM": "Your Mets: Off last night. At Texas tonight.",
    "CWS": "Your White Sox: Off last night. At Kansas City tonight.",
    "TEX": "Your Rangers: Off last night. Host New York tonight.",
    "SEA": "Your Mariners: Off last night. Host Houston tonight.",
    "COL": "Your Rockies: Off last night. Host Arizona tonight.",
    "ATL": "Your Braves: Off last night. Host Cincinnati tonight.",
    "HOU": "Your Astros: Off last night. At Seattle tonight.",
    "LAA": "Your Angels: Off last night. At Oakland tonight.",
    "STL": "Your Cardinals: Off last night. At Pittsburgh tonight.",
    "NYY": "Your Yankees: Off last night. Host Tampa Bay tonight (doubleheader).",
    "ARI": "Your Diamondbacks: Off last night. At Colorado tonight.",
    "MIA": "Your Marlins: Off last night. At Chicago tonight.",
    "SDP": "Your Padres: Off last night. At Los Angeles tonight.",
    "LAD": "Your Dodgers: Off last night. Host San Diego tonight.",
}

RACE_AL_RECAP = (
    "Pete Alonso homered twice in Baltimore's 4–3 win over Toronto. "
    "Detroit scored nine in a rout of Washington, keyed by a five-run fifth. "
    "Shane Baz went 6.2 innings in the Orioles' win."
)
RACE_AL_SINCE = "The Guardians are 7–3 in their last ten."
RACE_NL_RECAP = (
    "Drew Gilbert homered and drove in three in San Francisco's 5–2 win over Minnesota. "
    "The Giants scored four in the first two innings."
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
    return m.group(1).replace("2026-09-20", ISSUE_DATE)


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
<title>Scorebook - Monday, September 21</title>
<link rel="canonical" href="{ISSUE_URL}/" />
<meta name="description" content="{DEK}" />
<meta property="og:title" content="Scorebook - Monday, September 21" />
<meta property="og:description" content="{DEK}" />
<meta property="og:url" content="{ISSUE_URL}/" />
<meta property="og:image" content="{ISSUE_URL}/og.png" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Scorebook - Monday, September 21" />
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
  <p class="kicker">Monday night</p>
  <h1>Monday, September 21</h1>
  <p class="dek">{DEK}</p>
  <p class="sb-team-summary" id="sb-team-summary" aria-live="polite"></p>
  <p class="by">Scorebook · a daily recap of the games you didn't watch</p>

  <section class="shareable" id="must-watch">
  <h2>Must watch</h2>
{clip_html("alonso_two_homers")}
  <p class="cap">{CLIPS["alonso_two_homers"]["cap"]}</p>
{clip_html("tigers_five_run_fifth")}
  <p class="cap">{CLIPS["tigers_five_run_fifth"]["cap"]}</p>
{clip_html("gilbert_homer")}
  <p class="cap">{CLIPS["gilbert_homer"]["cap"]}</p>

  </section>

  <section class="shareable" id="play-of-the-night">
  <h2>Play of the night</h2>
  <p class="subn">The three Must watch clips, or something else.</p>
  <div class="poll" id="potn" data-potn-issue="{ISSUE_DATE}">
    <form id="potn-form">
      <label><input type="radio" name="play" value="alonso_two_homers" required> Alonso's two-homer game</label>
      <label><input type="radio" name="play" value="tigers_five_run_fifth"> Tigers' five-run fifth</label>
      <label><input type="radio" name="play" value="gilbert_homer"> Gilbert's three-RBI night</label>
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
{clip_html("jays_early_lead")}
  <p class="cap">{CLIPS["jays_early_lead"]["cap"]}</p>

  </section>

  <section class="shareable" id="one-inning">
  <h2>One inning</h2>
  <p>Bottom of the fifth at Comerica Park. Detroit had already scored four when the Tigers put up five more — part of a nine-run rout. Tigers 9, Nationals 2.</p>
{clip_html("tigers_five_run_fifth_inning")}
  <p class="cap">{CLIPS["tigers_five_run_fifth_inning"]["cap"]}</p>

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
      <p class="subn">Standings through Monday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
{al_tables}
    </div>

    <div class="panel-nl" id="nl-panel">
      <div class="recap" data-share-card="race-nl.png" data-share-text-src="share/race-nl.txt">
        <p class="subn">Last night</p>
        <p>{RACE_NL_RECAP}</p>
        <p class="subn">Since August 13</p>
        <p>{RACE_NL_SINCE}</p>
      </div>
      <p class="subn">Standings through Monday. L10 is the last ten games. RD is run differential. The heavy rule is the wild-card cut.</p>
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
