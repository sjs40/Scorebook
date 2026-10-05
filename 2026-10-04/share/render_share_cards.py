#!/usr/bin/env python3
"""Reusable Twitter-ready Scorebook table / recap cards.

Future tables: one function call.

    from render_share_cards import table_card, recap_card, heat_abs

    table_card("al-east.png", "AL East", headers, rows)
    table_card("al-east-odds.png", "AL East · Division winner %",
               headers, rows, heat_fn=heat_abs(col=2, threshold=5))
    recap_card("race-al.png", "American League", [
        ("Last night", "…"),
        ("Since August 13", "…"),
    ])

Every card foots with: powered by getscorebook.com
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable, Optional, Sequence

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent

COVER = (30, 63, 115)       # #1E3F73
INK = (42, 90, 154)         # #2A5A9A
PAPER = (243, 238, 227)     # #F3EEE3
SHADE = (228, 235, 245)     # #E4EBF5
GRAPHITE = (26, 39, 68)     # #1A2744
GRID = (122, 154, 192)      # #7A9AC0
CREAM = PAPER
MUTED = (92, 107, 128)

SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"

W = 1080
PAD = 40
FOOT = "powered by getscorebook.com"
KICKER_DEFAULT = "Wednesday, August 26"
ISSUE_URL = "https://getscorebook.com/2026-08-26"
RACE_HASH = ISSUE_URL + "/#the-race"

HeatFn = Callable[[int, int, str], bool]


def fnt(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def text_size(d: ImageDraw.ImageDraw, t: str, font) -> tuple[int, int]:
    b = d.textbbox((0, 0), t, font=font)
    return b[2] - b[0], b[3] - b[1]


def draw_center(d, x, y, w, h, text, font, fill):
    tw_, th_ = text_size(d, text, font)
    d.text((x + (w - tw_) / 2, y + (h - th_) / 2 - 1), text, font=font, fill=fill)


def draw_right(d, x, y, w, h, text, font, fill, pad=10):
    tw_, th_ = text_size(d, text, font)
    d.text((x + w - pad - tw_, y + (h - th_) / 2 - 1), text, font=font, fill=fill)


def draw_left(d, x, y, w, h, text, font, fill, pad=10):
    tw_, th_ = text_size(d, text, font)
    d.text((x + pad, y + (h - th_) / 2 - 1), text, font=font, fill=fill)


def draw_sb_cell(d: ImageDraw.ImageDraw, x: int, y: int, size: int = 28,
                 stroke=CREAM, letter=CREAM) -> None:
    d.rectangle((x, y, x + size, y + size), outline=stroke, width=2)
    inset = 3
    d.rectangle((x + inset, y + inset, x + size - inset, y + size - inset),
                outline=stroke, width=1)
    font = fnt(SANS_B, 11 if size >= 28 else 9)
    draw_center(d, x, y, size, size, "SB", font, letter)


def wrap_text(d, text: str, font, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_size(d, trial, font)[0] <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def parse_move(val: str) -> float:
    s = str(val).replace("+", "").replace("%", "").strip()
    try:
        return abs(float(s))
    except ValueError:
        return 0.0


def heat_abs(col: int, threshold: float = 5) -> HeatFn:
    """Heat a cell when abs(numeric value in that column) >= threshold."""
    def _fn(r: int, c: int, val: str) -> bool:
        return c == col and parse_move(val) >= threshold
    return _fn


def heat_first_row(col: int) -> HeatFn:
    def _fn(r: int, c: int, val: str) -> bool:
        return r == 0 and c == col
    return _fn


def _measure_dummy() -> ImageDraw.ImageDraw:
    return ImageDraw.Draw(Image.new("RGB", (10, 10), PAPER))


def auto_widths(headers: Sequence[str], rows: Sequence[Sequence[str]],
                left_cols: int, usable: int) -> list[int]:
    d = _measure_dummy()
    fh = fnt(SANS_B, 13)
    fb = fnt(SANS_B, 18)
    n = len(headers)
    mins = []
    for i, h in enumerate(headers):
        font = fh
        w, _ = text_size(d, str(h), font)
        for row in rows:
            cell = str(row[i]) if i < len(row) else ""
            use = fb if i < left_cols else fnt(SANS, 18)
            cw, _ = text_size(d, cell, use)
            w = max(w, cw)
        pad = 28 if i == 0 else 22
        mins.append(w + pad)
    extra = usable - sum(mins)
    if extra < 0:
        scale = usable / sum(mins)
        widths = [max(36, int(m * scale)) for m in mins]
        widths[-1] += usable - sum(widths)
        return widths
    # dump leftover into the name-ish column (0, or 1 if a rank column)
    grow = 1 if n > 2 and headers[0] in ("#", "RK") else 0
    widths = list(mins)
    widths[grow] += extra
    return widths


def _mast_h() -> int:
    return 72


def _foot_h() -> int:
    return 44


def _draw_masthead(d: ImageDraw.ImageDraw, w: int, kicker: str, show_sb: bool) -> None:
    d.rectangle((0, 0, w, _mast_h()), fill=COVER)
    x = PAD
    if show_sb:
        draw_sb_cell(d, x, 22, 28)
        x += 40
    brand = fnt(SANS_B, 20)
    d.text((x, 26), "SCOREBOOK", font=brand, fill=CREAM)
    fk = fnt(SANS, 14)
    tw, th = text_size(d, kicker, fk)
    d.text((w - PAD - tw, 28), kicker, font=fk, fill=(197, 212, 230))


def _draw_footer(d: ImageDraw.ImageDraw, y: int, w: int) -> None:
    fi = fnt(SERIF_I, 15)
    tw, th = text_size(d, FOOT, fi)
    d.text(((w - tw) / 2, y + 12), FOOT, font=fi, fill=MUTED)


def table_card(
    filename: str,
    title: str,
    headers: Sequence[str],
    rows: Sequence[Sequence[str]],
    *,
    heat_fn: Optional[HeatFn] = None,
    heat_cells: Optional[Iterable[tuple[int, int]]] = None,
    cut_after: Optional[int] = None,
    left_cols: int = 1,
    kicker: str = KICKER_DEFAULT,
    out_dir: Path = OUT,
    show_sb: bool = True,
    widths: Optional[Sequence[int]] = None,
    width: int = W,
) -> Path:
    """Render one standalone table card. Heat = filled Cover cell."""
    pad_x = PAD
    usable = width - 2 * pad_x
    if widths is None:
        widths = auto_widths(headers, rows, left_cols, usable)
    else:
        widths = list(widths)
        if sum(widths) != usable:
            widths[-1] += usable - sum(widths)

    heat_set = set(heat_cells or [])
    title_h = 46
    head_h = 36
    row_h = 40
    mast = _mast_h()
    foot = _foot_h()
    H = mast + title_h + head_h + row_h * len(rows) + foot + 18

    im = Image.new("RGB", (width, H), PAPER)
    d = ImageDraw.Draw(im)
    _draw_masthead(d, width, kicker, show_sb)

    ft = fnt(SANS_B, 16)
    fh = fnt(SANS_B, 12)
    fb = fnt(SANS, 17)
    fb_b = fnt(SANS_B, 17)

    y = mast + 14
    d.text((pad_x, y), title.upper(), font=ft, fill=INK)
    y = mast + title_h

    x0 = pad_x
    table_w = sum(widths)
    d.rectangle((x0, y, x0 + table_w, y + head_h), fill=SHADE)
    d.line((x0, y, x0 + table_w, y), fill=INK, width=2)
    d.line((x0, y + head_h - 1, x0 + table_w, y + head_h - 1), fill=INK, width=2)
    x = x0
    for i, h in enumerate(headers):
        if i < left_cols:
            draw_left(d, x, y, widths[i], head_h, str(h), fh, INK)
        else:
            draw_right(d, x, y, widths[i], head_h, str(h), fh, INK)
        x += widths[i]
    y += head_h

    for r_i, row in enumerate(rows):
        bg = SHADE if r_i % 2 == 1 else PAPER
        d.rectangle((x0, y, x0 + table_w, y + row_h), fill=bg)
        x = x0
        for i, cell in enumerate(row):
            cell = str(cell)
            hot = (r_i, i) in heat_set
            if heat_fn and heat_fn(r_i, i, cell):
                hot = True
            if hot:
                d.rectangle((x + 2, y + 2, x + widths[i] - 2, y + row_h - 2), fill=COVER)
                fill = CREAM
                font = fb_b
                if i < left_cols:
                    draw_left(d, x, y, widths[i], row_h, cell, font, fill)
                else:
                    draw_right(d, x, y, widths[i], row_h, cell, font, fill)
            elif i == 0:
                draw_left(d, x, y, widths[i], row_h, cell, fb_b, INK)
            elif i < left_cols:
                draw_left(d, x, y, widths[i], row_h, cell, fb_b, INK)
            else:
                draw_right(d, x, y, widths[i], row_h, cell, fb, GRAPHITE)
            x += widths[i]
        if cut_after is not None and r_i == cut_after:
            d.line((x0, y + row_h - 1, x0 + table_w, y + row_h - 1), fill=COVER, width=3)
        else:
            d.line((x0, y + row_h - 1, x0 + table_w, y + row_h - 1), fill=GRID, width=1)
        y += row_h

    _draw_footer(d, y + 4, width)
    dest = out_dir / filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "PNG", optimize=True)
    print("wrote", dest.name, im.size)
    return dest


def recap_card(
    filename: str,
    league: str,
    blocks: Sequence[tuple[str, str]],
    *,
    kicker: str = KICKER_DEFAULT,
    out_dir: Path = OUT,
    show_sb: bool = True,
    width: int = W,
) -> Path:
    """Cream recap card: Scorebook header, grafs, powered-by foot."""
    mast = _mast_h()
    dummy = _measure_dummy()
    f_league = fnt(SANS_B, 22)
    f_lab = fnt(SANS_B, 12)
    f_body = fnt(SERIF, 22)
    max_w = width - 2 * PAD

    wrapped: list[tuple[str, list[str]]] = []
    body_h = 28
    for label, graf in blocks:
        lines = wrap_text(dummy, graf, f_body, max_w)
        wrapped.append((label, lines))
        body_h += 28 + 8 + len(lines) * 32 + 18

    H = mast + 56 + body_h + _foot_h()
    im = Image.new("RGB", (width, H), PAPER)
    d = ImageDraw.Draw(im)
    _draw_masthead(d, width, kicker, show_sb)

    y = mast + 22
    d.text((PAD, y), league.upper(), font=f_league, fill=INK)
    y += 40
    d.line((PAD, y, width - PAD, y), fill=INK, width=2)
    y += 18

    for label, lines in wrapped:
        d.text((PAD, y), label.upper(), font=f_lab, fill=INK)
        y += 26
        for line in lines:
            d.text((PAD, y), line, font=f_body, fill=GRAPHITE)
            y += 32
        y += 16

    _draw_footer(d, y + 4, width)
    dest = out_dir / filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "PNG", optimize=True)
    print("wrote", dest.name, im.size)
    return dest


def twitter_len(text: str) -> int:
    """Approx Twitter length: URLs count as 23."""
    import re
    return len(re.sub(r"https://\\S+", "x" * 23, text))


def write_tweet(filename: str, tweets: Sequence[str], out_dir: Path = OUT) -> Path:
    dest = out_dir / filename
    body = "\n\n".join(t.strip() for t in tweets)
    dest.write_text(body + "\n", encoding="utf-8")
    for i, t in enumerate(tweets, 1):
        print(f"  {filename} tweet {i}/{len(tweets)} chars={twitter_len(t)}")
    return dest


def _performers():
    table_card(
        "pitchers.png",
        "Pitchers  ·  Bill James game score, 5+ IP",
        ["#", "NAME", "TM", "GS", "IP", "H", "ER", "BB", "K", "OPP"],
        [
            ["1", "Jesús Luzardo", "PHI", "81", "7.0", "1", "0", "3", "9", "SEA"],
            ["2", "Eduardo Rodriguez", "ARI", "79", "7.0", "2", "0", "3", "9", "CHC"],
            ["3", "Freddy Peralta", "TBR", "72", "6.0", "2", "0", "0", "4", "DET"],
            ["4", "Tanner Gordon", "COL", "66", "7.0", "6", "1", "0", "5", "WSN"],
        ],
        left_cols=3,
        heat_fn=heat_first_row(3),
    )
    table_card(
        "hitters.png",
        "Hitters  ·  ranked by total bases",
        ["#", "NAME", "TM", "TB", "AB", "H", "XBH", "HR", "RBI", "SB"],
        [
            ["1", "Héctor Rodríguez", "CIN", "9", "6", "3", "2", "2", "2", "0"],
            ["2", "Tristan Peters", "CHW", "7", "4", "3", "2", "1", "2", "0"],
            ["3", "Andrés Chaparro", "WSN", "7", "4", "3", "2", "1", "1", "0"],
            ["4", "Sean Murphy", "ATL", "7", "4", "3", "2", "1", "1", "0"],
            ["5", "Kyle Schwarber", "PHI", "6", "5", "2", "2", "1", "3", "0"],
            ["6", "Tommy Edman", "LAD", "6", "4", "2", "2", "1", "3", "0"],
            ["7", "Luis García Jr.", "NYY", "6", "5", "3", "1", "1", "2", "0"],
            ["8", "Bryce Harper", "PHI", "6", "4", "2", "2", "1", "2", "0"],
        ],
        left_cols=3,
        heat_fn=heat_first_row(3),
    )


def _standings():
    al_east = [
        ["TBR", "79", "54", "--", "--", "W1", "5-5", "+47"],
        ["NYY", "75", "57", "3.5", "+8.0", "W1", "7-3", "+104"],
        ["BOS", "73", "60", "6.0", "+5.5", "L1", "7-3", "+101"],
        ["BAL", "65", "68", "14.0", "2.5", "W2", "5-5", "-22"],
        ["TOR", "65", "69", "14.5", "3.0", "W1", "5-5", "-54"],
    ]
    al_central = [
        ["CHW", "70", "63", "--", "--", "W2", "5-5", "+44"],
        ["CLE", "68", "66", "2.5", "--", "W7", "8-2", "-4"],
        ["MIN", "64", "70", "6.5", "4.0", "L2", "4-6", "-56"],
        ["DET", "62", "71", "8.0", "5.5", "L1", "2-8", "+70"],
        ["KCR", "59", "75", "11.5", "9.0", "L1", "9-1", "-92"],
    ]
    al_west = [
        ["HOU", "66", "67", "--", "--", "L1", "3-7", "-48"],
        ["TEX", "66", "68", "0.5", "2.0", "L2", "5-5", "-47"],
        ["SEA", "64", "70", "2.5", "4.0", "L1", "6-4", "-57"],
        ["ATH", "53", "81", "13.5", "15.0", "W2", "4-6", "-185"],
        ["LAA", "52", "82", "14.5", "16.0", "L4", "3-7", "-75"],
    ]
    al_wc = [
        ["NYY", "75", "57", "+8.0", "W1", "7-3", "+104"],
        ["BOS", "73", "60", "+5.5", "L1", "7-3", "+101"],
        ["CLE", "68", "66", "--", "W7", "8-2", "-4"],
        ["TEX", "66", "68", "2.0", "L2", "5-5", "-47"],
        ["BAL", "65", "68", "2.5", "W2", "5-5", "-22"],
        ["TOR", "65", "69", "3.0", "W1", "5-5", "-54"],
    ]
    div_h = ["TM", "W", "L", "GB", "WCGB", "STRK", "L10", "RD"]
    wc_h = ["TM", "W", "L", "WCGB", "STRK", "L10", "RD"]
    table_card("al-east.png", "AL East", div_h, al_east)
    table_card("al-central.png", "AL Central", div_h, al_central)
    table_card("al-west.png", "AL West", div_h, al_west)
    table_card("al-wc.png", "AL Wild Card", wc_h, al_wc, cut_after=2)

    nl_east = [
        ["ATL", "78", "55", "--", "--", "W3", "5-5", "+112"],
        ["PHI", "74", "60", "4.5", "+2.0", "W1", "8-2", "+23"],
        ["MIA", "68", "66", "10.5", "4.0", "W1", "5-5", "+19"],
        ["WSN", "62", "73", "17.0", "10.5", "L2", "2-8", "+6"],
        ["NYM", "60", "73", "18.0", "11.5", "L1", "6-4", "-46"],
    ]
    nl_central = [
        ["MIL", "82", "51", "--", "--", "W1", "7-3", "+167"],
        ["CHC", "76", "58", "6.5", "+4.0", "L2", "4-6", "+119"],
        ["STL", "66", "68", "16.5", "6.0", "L5", "3-7", "-15"],
        ["PIT", "65", "70", "18.0", "7.5", "L1", "5-5", "+24"],
        ["CIN", "63", "71", "19.5", "9.0", "W1", "4-6", "-100"],
    ]
    nl_west = [
        ["LAD", "80", "53", "--", "--", "L2", "6-4", "+149"],
        ["SDP", "72", "62", "8.5", "--", "W1", "6-4", "+17"],
        ["ARI", "71", "63", "9.5", "1.0", "W2", "5-5", "+5"],
        ["SFG", "54", "79", "26.0", "17.5", "L1", "3-7", "-74"],
        ["COL", "52", "81", "28.0", "19.5", "W2", "3-7", "-132"],
    ]
    nl_wc = [
        ["CHC", "76", "58", "+4.0", "L2", "4-6", "+119"],
        ["PHI", "74", "60", "+2.0", "W1", "8-2", "+23"],
        ["SDP", "72", "62", "--", "W1", "6-4", "+17"],
        ["ARI", "71", "63", "1.0", "W2", "5-5", "+5"],
        ["MIA", "68", "66", "4.0", "W1", "5-5", "+19"],
        ["STL", "66", "68", "6.0", "L5", "3-7", "-15"],
    ]
    table_card("nl-east.png", "NL East", div_h, nl_east)
    table_card("nl-central.png", "NL Central", div_h, nl_central)
    table_card("nl-west.png", "NL West", div_h, nl_west)
    table_card("nl-wc.png", "NL Wild Card", wc_h, nl_wc, cut_after=2)


def _odds():
    heat7 = heat_abs(2, 5)
    oh = ["TM", "DIV%", "7D"]
    table_card("al-east-odds.png", "AL East · Division winner %", oh, [
        ["TBR", "61.2", "-14"],
        ["NYY", "24.0", "+10"],
        ["BOS", "10.7", "+7"],
    ], heat_fn=heat7)
    table_card("al-central-odds.png", "AL Central · Division winner %", oh, [
        ["CHW", "60.6", "+4"],
        ["CLE", "26.0", "+15"],
    ], heat_fn=heat7)
    table_card("al-west-odds.png", "AL West · Division winner %", oh, [
        ["HOU", "37.0", "-11"],
        ["SEA", "36.5", "+14"],
        ["TEX", "28.0", "+0"],
    ], heat_fn=heat7)
    table_card("al-wc-odds.png", "AL Wild Card · Playoff %", ["TM", "PLAYOFF%"], [
        ["NYY", "99.4"],
        ["BOS", "97.2"],
        ["CLE", "62.0"],
        ["TEX", "46.5"],
        ["BAL", "21.0"],
        ["TOR", "14.5"],
    ], cut_after=2)

    table_card("nl-east-odds.png", "NL East · Division winner %", oh, [
        ["ATL", "76.0", "-4"],
        ["PHI", "24.0", "+8"],
    ], heat_fn=heat7)
    table_card("nl-central-odds.png", "NL Central · Division winner %", oh, [
        ["MIL", "92.0", "+4"],
        ["CHC", "6.5", "-6"],
    ], heat_fn=heat7)
    table_card("nl-west-odds.png", "NL West · Division winner %", oh, [
        ["LAD", "98.5", "0"],
        ["SDP", "1.0", "0"],
    ], heat_fn=heat7)
    table_card("nl-wc-odds.png", "NL Wild Card · Playoff %", ["TM", "PLAYOFF%"], [
        ["CHC", "96.2"],
        ["PHI", "89.5"],
        ["SDP", "69.5"],
        ["ARI", "39.0"],
        ["MIA", "6.0"],
        ["STL", "5.5"],
    ], cut_after=2)


def _recaps():
    recap_card("race-al.png", "American League", [
        ("Last night",
         "Cleveland wins a seventh straight and holds the last American League wild card. "
         "Boston loses; Tampa Bay’s lead in the East is six. The Yankees stay eight games "
         "up on the last wild-card spot."),
        ("Since August 13", "Cleveland is 9-3. Detroit is 2-10."),
    ])
    recap_card("race-nl.png", "National League", [
        ("Last night",
         "San Diego and Arizona both win. The Padres keep the last wild card. Arizona is "
         "one game out. The Cubs lose again, 6.5 back of Milwaukee. Philadelphia blanks Seattle."),
        ("Since August 13",
         "Philadelphia is 9-2. The Cubs are 5-7. St. Louis has lost five in a row."),
    ])

    al1 = (
        "Cleveland wins a 7th straight and holds the last AL wild card. "
        "Boston loses; Tampa Bay’s East lead is six. Yankees stay 8 up on the last WC.\n\n"
        "Since Aug 13: CLE 9-3. DET 2-10.\n\n"
        f"{FOOT}\n{RACE_HASH}"
    )
    nl_night = (
        "Last night: San Diego and Arizona both win. The Padres keep the last wild card. "
        "Arizona is one game out. The Cubs lose again, 6.5 back of Milwaukee. "
        "Philadelphia blanks Seattle."
    )
    nl_since = (
        f"Since Aug 13: Philadelphia 9-2. Cubs 5-7. St. Louis has lost five in a row.\n\n"
        f"{FOOT}\n{RACE_HASH}"
    )
    # Fit AL in one tweet if possible; NL as a two-tweet thread if needed.
    al_tweets = [al1]
    if twitter_len(al1) > 280:
        al_tweets = [
            "Cleveland wins a 7th straight and holds the last AL wild card. "
            "Boston loses; TB’s East lead is six. Yankees stay 8 up on the last WC. (1/2)",
            f"Since Aug 13: CLE 9-3. DET 2-10.\n\n{FOOT}\n{RACE_HASH}",
        ]
    nl_one = nl_night + "\n\n" + nl_since
    if twitter_len(nl_one) <= 280:
        nl_tweets = [nl_one]
    else:
        nl_tweets = [nl_night + " (1/2)", nl_since]
    write_tweet("race-al.txt", al_tweets)
    write_tweet("race-nl.txt", nl_tweets)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    _performers()
    _standings()
    _odds()
    _recaps()


if __name__ == "__main__":
    main()
