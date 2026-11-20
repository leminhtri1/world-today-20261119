"""Draw entry.png: a one-page world news front page for Thursday 19 November 2026.

Everything is drawn with Pillow: shapes, icons and flags. Text uses fonts that
ship with Windows (Georgia, Arial); they are read from the system font folder
at build time and are not part of this repository.

    python build.py        -> writes entry.png next to this file
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 36

PAPER = (247, 244, 236)
INK = (22, 22, 24)
GREY = (78, 78, 82)
DETAIL = (34, 34, 38)
RULE = (150, 146, 138)
RED = (190, 30, 36)
WHITE = (255, 255, 255)

FONT_DIRS = [
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
    "/usr/share/fonts/truetype/msttcorefonts",
    "/Library/Fonts",
]


def font_path(name):
    for d in FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    sys.exit(f"font not found: {name}")


SERIF_BOLD = font_path("georgiab.ttf")
SERIF = font_path("georgia.ttf")
SANS = font_path("arial.ttf")
SANS_BOLD = font_path("arialbd.ttf")
SERIF_ITALIC = font_path("georgiai.ttf")

_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def text_w(d, s, font):
    return d.textlength(s, font=font)


def wrap(d, text, font, width):
    """Greedy word wrap; returns lines or None if a single word is too wide."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if text_w(d, trial, font) <= width:
            cur = trial
        else:
            if not cur or text_w(d, word, font) > width:
                return None
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(d, text, path, width, max_lines, start, smallest):
    """Largest font size (start..smallest) at which text wraps into max_lines."""
    for size in range(start, smallest - 1, -1):
        f = F(path, size)
        lines = wrap(d, text, f, width)
        if lines is not None and len(lines) <= max_lines:
            return f, lines
    raise SystemExit(f"text does not fit: {text!r}")


def line_h(font, lead=1.2):
    return round(font.size * lead)


def draw_lines(d, x, y, lines, font, fill, lead=1.2, center_w=None):
    for ln in lines:
        if center_w is not None:
            d.text((x + (center_w - text_w(d, ln, font)) / 2, y), ln, font=font, fill=fill)
        else:
            d.text((x, y), ln, font=font, fill=fill)
        y += line_h(font, lead)
    return y


def star(cx, cy, r_out, r_in, rot=-90):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ---------------------------------------------------------------- flags

def flag_us(d, x, y, w, h):
    stripe = h / 13
    for i in range(13):
        d.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe],
                    fill=(178, 34, 52) if i % 2 == 0 else WHITE)
    cw, ch = w * 0.4, stripe * 7
    d.rectangle([x, y, x + cw, y + ch], fill=(60, 59, 110))
    for r in range(4):
        for c in range(5):
            sx = x + cw * (c + 0.5) / 5
            sy = y + ch * (r + 0.5) / 4
            d.polygon(star(sx, sy, 3.2, 1.3), fill=WHITE)
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    yel = (255, 222, 0)
    u = h / 20
    d.polygon(star(x + 5 * u, y + 5 * u, 3 * u, 1.15 * u), fill=yel)
    for (sx, sy) in [(10, 2), (12, 4), (12, 7), (10, 9)]:
        cx, cy = x + sx * u, y + sy * u
        rot = math.degrees(math.atan2((y + 5 * u) - cy, (x + 5 * u) - cx))
        d.polygon(star(cx, cy, u, 0.4 * u, rot), fill=yel)
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def flag_ru(d, x, y, w, h):
    t = h / 3
    d.rectangle([x, y, x + w, y + t], fill=WHITE)
    d.rectangle([x, y + t, x + w, y + 2 * t], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * t, x + w, y + h], fill=(213, 43, 30))
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)


# ---------------------------------------------------------------- icons (s x s box)

def icon_scales(d, x, y, s):
    cx = x + s / 2
    d.line([cx, y + 8, cx, y + s - 8], fill=INK, width=3)
    d.polygon([(cx - 14, y + s - 4), (cx + 14, y + s - 4), (cx, y + s - 12)], fill=INK)
    d.line([x + 6, y + 14, x + s - 6, y + 14], fill=INK, width=3)
    d.ellipse([cx - 4, y + 4, cx + 4, y + 12], fill=RED)
    for px in (x + 10, x + s - 10):
        d.line([px, y + 14, px - 8, y + 32], fill=INK, width=1)
        d.line([px, y + 14, px + 8, y + 32], fill=INK, width=1)
        d.chord([px - 11, y + 24, px + 11, y + 40], 0, 180, fill=INK)


def icon_chart(d, x, y, s):
    d.line([x + 6, y + 4, x + 6, y + s - 6, x + s - 4, y + s - 6], fill=INK, width=3)
    for i, bh in enumerate([10, 16, 13, 24]):
        bx = x + 12 + i * 9
        d.rectangle([bx, y + s - 7 - bh, bx + 5, y + s - 7], fill=GREY)
    pts = [(x + 10, y + s - 16), (x + 22, y + s - 24), (x + 32, y + s - 20), (x + s - 8, y + 12)]
    d.line(pts, fill=RED, width=4, joint="curve")
    tip = (x + s - 4, y + 7)
    d.polygon([tip, (x + s - 18, y + 10), (x + s - 7, y + 21)], fill=RED)


def icon_bridge(d, x, y, s):
    deck = y + s * 0.45
    d.rectangle([x + 2, deck, x + s - 2, deck + 5], fill=INK)
    for i in range(3):
        ax = x + 2 + i * (s - 4) / 3
        aw = (s - 4) / 3
        d.arc([ax, deck + 3, ax + aw, deck + 3 + aw * 0.9], 180, 360, fill=INK, width=3)
        d.line([ax, deck + 5, ax, y + s - 6], fill=INK, width=3)
    d.line([x + s - 2, deck + 5, x + s - 2, y + s - 6], fill=INK, width=3)
    for i in range(4):
        wy = y + s - 6 + (i % 2)
        d.arc([x + i * s / 4, wy - 3, x + (i + 1) * s / 4, wy + 3], 0, 180, fill=GREY, width=2)
    d.polygon(star(x + s * 0.62, deck - 2, 14, 6), fill=RED)


def icon_tower(d, x, y, s):
    cx = x + s / 2
    d.polygon([(cx - 10, y + s - 4), (cx + 10, y + s - 4), (cx + 6, y + 14), (cx - 6, y + 14)], fill=INK)
    d.line([cx, y + 2, cx, y + 14], fill=INK, width=2)
    for wy in range(int(y + 20), int(y + s - 8), 6):
        d.line([cx - 4, wy, cx + 4, wy], fill=PAPER, width=1)
    d.polygon(star(cx + 9, y + 20, 11, 5), fill=RED)
    d.line([x + 2, y + s - 4, x + s - 2, y + s - 4], fill=INK, width=2)
    d.rectangle([x + 4, y + s - 18, x + 12, y + s - 4], fill=GREY)
    d.rectangle([x + s - 13, y + s - 24, x + s - 5, y + s - 4], fill=GREY)


def icon_arctic(d, x, y, s):
    cx = x + s / 2
    shield = [(x + 6, y + 4), (x + s - 6, y + 4), (x + s - 6, y + s * 0.5),
              (cx, y + s - 2), (x + 6, y + s * 0.5)]
    d.polygon(shield, outline=INK, fill=PAPER, width=3)
    cy = y + s * 0.45
    r = s * 0.27
    for k in range(3):
        a = math.radians(90 + k * 60)
        dx, dy = r * math.cos(a), r * math.sin(a)
        d.line([cx - dx, cy - dy, cx + dx, cy + dy], fill=RED, width=3)
        for sgn in (1, -1):
            ex, ey = cx + sgn * dx * 0.6, cy + sgn * dy * 0.6
            for t in (-35, 35):
                b = a + math.radians(t) + (0 if sgn > 0 else math.pi)
                d.line([ex, ey, ex + 5 * math.cos(b), ey + 5 * math.sin(b)], fill=RED, width=2)


def icon_protest(d, x, y, s):
    d.rectangle([x + 22, y + 2, x + s - 4, y + 18], fill=RED)
    d.line([x + 32, y + 18, x + 32, y + 34], fill=INK, width=3)
    for i, hx in enumerate([x + 10, x + 26, x + 42]):
        top = y + 30 + (4 if i != 1 else 0)
        d.ellipse([hx - 6, top, hx + 6, top + 12], fill=INK)
        d.pieslice([hx - 10, top + 13, hx + 10, top + 33], 180, 360, fill=INK)
    d.rectangle([x + 2, y + s - 6, x + s - 2, y + s - 3], fill=INK)


# ---------------------------------------------------------------- world map
# Coarse hand-made coastlines (lon, lat), Mercator projection, cropped to
# lon -105..135 and lat -20..72 so every story location fits.

MAP_W, MAP_H = 320, 166
LON0, LON1, LAT0, LAT1 = -105.0, 135.0, -20.0, 72.0
SEA = (234, 236, 236)
LAND = (203, 200, 193)


def _merc(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def proj(lon, lat):
    x = (lon - LON0) / (LON1 - LON0) * MAP_W
    y = (_merc(LAT1) - _merc(lat)) / (_merc(LAT1) - _merc(LAT0)) * MAP_H
    return (x, y)


LANDS = [
    # North America
    [(-168, 65), (-155, 71), (-125, 70), (-95, 72), (-80, 70), (-62, 60), (-56, 52), (-66, 45),
     (-70, 42), (-76, 35), (-81, 31), (-80, 25), (-82, 29), (-90, 30), (-97, 27), (-97, 22),
     (-91, 19), (-87, 21), (-88, 16), (-83, 15), (-83, 10), (-79, 9), (-77, 8), (-86, 12),
     (-92, 15), (-105, 20), (-110, 24), (-114, 31), (-118, 34), (-124, 40), (-124, 48),
     (-130, 55), (-140, 60), (-152, 58), (-165, 60)],
    # Greenland
    [(-73, 78), (-60, 82), (-30, 83), (-20, 75), (-22, 70), (-42, 60), (-50, 64), (-55, 70), (-70, 76)],
    # Cuba
    [(-85, 22), (-80, 23.2), (-74, 20), (-77, 19.8)],
    # South America
    [(-77, 8), (-72, 12), (-62, 10.5), (-50, 0), (-35, -5), (-38, -13), (-40, -22), (-48, -26),
     (-53, -34), (-58, -38), (-65, -42), (-68, -52), (-74, -50), (-73, -40), (-71, -30),
     (-70, -18), (-76, -14), (-81, -5), (-80, 0), (-78, 3)],
    # Iceland, Ireland, Great Britain
    [(-24, 64), (-22, 66.5), (-15, 66.5), (-13.5, 65), (-18, 63.4)],
    [(-10, 51.5), (-6, 52), (-6, 54.5), (-8, 55.2), (-10, 54)],
    [(-5.5, 50), (1.5, 51), (1.7, 52.8), (-0.3, 54), (-2, 56), (-1.8, 57.6), (-3, 58.6),
     (-5, 58.6), (-6, 57), (-5, 55), (-3, 54.8), (-4.5, 53.3), (-3, 51.5), (-5, 51.7)],
    # Scandinavia and Finland
    [(5, 58), (5, 62), (12, 66), (17, 70), (28, 71), (31, 70), (30, 62), (28, 60.5), (22, 60),
     (21.5, 63), (25, 65.5), (22, 65.8), (18, 62.5), (19, 60), (16.5, 57), (14, 55.5),
     (12.5, 56.2), (11, 58.8), (8, 58)],
    # Eurasia
    [(-10, 36), (-9.5, 43.5), (-1.5, 43.5), (-4.5, 48), (-1.5, 49.5), (2, 51), (4, 51.5),
     (4.7, 53), (8, 53.6), (8, 57), (10.5, 57.7), (12, 56), (14, 55.4), (19, 54.5), (21, 57),
     (23.5, 58), (24, 59.5), (29, 60), (30, 62), (35, 65), (40, 64.5), (44, 67), (55, 68),
     (60, 69), (70, 73), (80, 73), (100, 77), (115, 74), (130, 71), (140, 72), (160, 70),
     (180, 69), (180, 62), (165, 60), (155, 59), (160, 54), (156, 51), (143, 59), (135, 55),
     (140, 48), (132, 43), (129, 41), (129, 35), (126, 35), (125, 40), (121, 39), (122, 37),
     (119, 35), (122, 30), (120, 26), (117, 23.5), (114, 22.3), (110, 21), (108, 21.5),
     (106, 19), (109, 12), (105, 9), (100, 13), (99, 9), (103.5, 1.5), (101, 3), (98.5, 8),
     (98, 16), (94, 17), (92, 21), (87, 21.5), (80, 15), (77, 8), (73, 17), (72.5, 21),
     (67, 24.5), (57, 25.5), (56, 27), (52, 28), (50, 30), (48, 30), (50, 26), (56, 26),
     (59, 22.5), (57, 19), (52, 16), (45, 13), (43, 13), (39, 21), (35, 28), (34, 31),
     (35.5, 35), (36, 36.5), (30, 36.3), (27, 37), (26, 40), (23, 40), (24, 38), (22, 36.5),
     (19.5, 40), (19.5, 42), (13.5, 45.5), (12.3, 45), (16, 40), (15.6, 38), (12.5, 41.8),
     (10, 44), (6, 43), (3, 43.3), (3, 42), (0, 40), (-0.5, 38), (-2, 36.7), (-6, 36)],
    # Africa
    [(-17, 21), (-16, 28), (-10, 30), (-6, 36), (-2, 35.2), (10, 37.2), (11, 34), (20, 31),
     (25, 31.5), (32, 31.2), (34.5, 28), (33, 24), (36, 22), (39, 16), (43, 12), (51, 12),
     (48, 6), (41, -2), (40, -11), (35, -20), (35, -25), (32, -29), (27, -34), (20, -35),
     (18, -31), (12, -18), (13, -12), (12, -5), (9, -1), (9, 4), (5, 5.5), (-3, 5), (-8, 4.5),
     (-13, 8), (-17, 14)],
    # Madagascar, Japan, Taiwan, Sumatra, Borneo, Australia
    [(44, -25), (47, -25), (50, -15), (49, -12), (44, -17)],
    [(130, 31), (134, 34), (140, 35), (141, 38), (141.5, 41.5), (140, 40), (136, 36), (132, 34)],
    [(120.2, 22.5), (121.9, 25.2), (121.2, 22)],
    [(95, 5.5), (98, 4), (106, -6), (102, -4)],
    [(109, 1.5), (116, 7), (119, 5), (116, -4), (110, -3)],
    [(113, -22), (114, -26), (115, -34), (130, -31), (140, -38), (150, -37), (153, -28),
     (146, -19), (142, -11), (136, -12), (130, -12), (122, -17)],
]

SEAS = [
    # Black Sea (with the Sea of Azov) and the Caspian
    [(28, 41.2), (28, 43), (29.5, 45.3), (33, 46), (33.5, 44.5), (36, 45.3), (38, 47),
     (39.5, 47), (38, 45), (41.5, 41.8), (36, 41.5), (31, 41.2)],
    [(47, 45), (50, 47), (53, 46.5), (53, 42), (54, 37.5), (50, 37), (49, 39.5), (47.5, 42.5)],
]

# ---------------------------------------------------------------- extra icons

def icon_climate(d, x, y, s):
    cx, cy, r = x + s * 0.42, y + s * 0.55, s * 0.36
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=3)
    d.arc([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r], 90, 270, fill=INK, width=2)
    d.arc([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r], 270, 90, fill=INK, width=2)
    d.line([cx - r, cy, cx + r, cy], fill=INK, width=2)
    # oil drop, struck through
    dx, dy = x + s - 14, y + 14
    d.polygon([(dx, dy - 12), (dx - 8, dy + 2), (dx + 8, dy + 2)], fill=RED)
    d.ellipse([dx - 8, dy - 6, dx + 8, dy + 10], fill=RED)
    d.line([dx - 12, dy + 12, dx + 12, dy - 12], fill=INK, width=3)


def icon_game(d, x, y, s):
    d.rounded_rectangle([x + 2, y + s * 0.3, x + s - 2, y + s * 0.82], radius=12, fill=INK)
    cy = y + s * 0.56
    d.rectangle([x + 11, cy - 2, x + 23, cy + 2], fill=PAPER)
    d.rectangle([x + 15, cy - 6, x + 19, cy + 6], fill=PAPER)
    d.ellipse([x + s - 18, cy - 8, x + s - 11, cy - 1], fill=RED)
    d.ellipse([x + s - 26, cy + 1, x + s - 19, cy + 8], fill=PAPER)
    f = F(SANS_BOLD, 14)
    d.text((x + s / 2 - 8, y + 1), "VI", font=f, fill=RED)


def draw_summit(d, x, y, w, h):
    """Three leaders behind their flags at one table (drawn silhouettes)."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 228, 218))
    band = 26
    d.rectangle([x, y, x + w, y + band], fill=RED)
    bf = F(SANS_BOLD, 14)
    t = "APEC 2026  ·  SHENZHEN  ·  FIRST THREE-WAY SUMMIT"
    d.text((x + (w - text_w(d, t, bf)) / 2, y + 5), t, font=bf, fill=WHITE)
    names = (("TRUMP", flag_us), ("XI", flag_cn), ("PUTIN", flag_ru))
    table_y = y + h - 46
    fw, fh = 54, 36
    for i, (name, fn) in enumerate(names):
        cx = x + w * (i + 0.5) / 3
        fn(d, cx - fw / 2, y + band + 8, fw, fh)
        hr = 17
        hy = table_y - 62
        d.pieslice([cx - 40, hy + 26, cx + 40, hy + 106], 180, 360, fill=(52, 54, 62))
        d.ellipse([cx - hr, hy - hr + 8, cx + hr, hy + hr + 8], fill=(52, 54, 62))
    d.rectangle([x + 8, table_y, x + w - 8, table_y + 12], fill=(120, 86, 58))
    d.rectangle([x + 8, table_y + 12, x + w - 8, y + h - 6], fill=(96, 68, 46))
    nf = F(SANS_BOLD, 15)
    for i, (name, _) in enumerate(names):
        cx = x + w * (i + 0.5) / 3
        tw = text_w(d, name, nf) + 16
        d.rectangle([cx - tw / 2, table_y + 16, cx + tw / 2, table_y + 36], fill=WHITE, outline=INK)
        d.text((cx - tw / 2 + 8, table_y + 18), name, font=nf, fill=INK)


# ---------------------------------------------------------------- content
# Lead = 1, cells = 2..9, briefs = 10.. ; region is for the region bar.
# Every item happened or was first reported on Thursday 19 November 2026.

DATE_LONG = "Thursday 19 November 2026"

LEAD = dict(
    n=1, region="ASIA", where="SHENZHEN · SUMMIT", ll=(114.1, 22.5),
    head="Trump, Xi & Putin hold first-ever three-way summit",
    text=("The US, Chinese and Russian leaders met on the sidelines of the APEC summit "
          "in Shenzhen, China — their first trilateral meeting. "
          "Trump left China without meeting Kim Jong-un."),
)

CELLS = [
    dict(n=2, region="EUROPE", where="THE HAGUE", ll=(4.3, 52.1), icon=icon_scales,
         head="World Court: Myanmar committed genocide against Rohingya",
         text="First such ICJ ruling against a state."),
    dict(n=3, region="AMERICAS", where="NEW YORK", ll=(-74.0, 40.7), icon=icon_chart,
         head="Anthropic debuts on Nasdaq at ~$1.5T valuation",
         text="Ticker ANT; IPO priced at $83, above the $70–78 range."),
    dict(n=4, region="EUROPE", where="KERCH · KYIV", ll=(36.5, 45.3), icon=icon_bridge,
         head="Ukraine hits Kerch Bridge again; strikes hit Kyiv embassies",
         text="Third strike in four days halts rail; Austrian, Dutch embassies damaged."),
    dict(n=5, region="MIDEAST", where="RIYADH", ll=(46.7, 24.7), icon=icon_tower,
         head="Houthi strike hits Riyadh's tallest tower",
         text="PIF Tower damaged as Iran war spreads; no casualties reported."),
    dict(n=6, region="EUROPE", where="ANTALYA · COP31", ll=(30.7, 36.9), icon=icon_climate,
         head="COP31 draft drops fossil fuels and $120bn aid goal",
         text="Talks in Turkey are due to end Friday; text not yet final."),
    dict(n=7, region="EUROPE", where="COPENHAGEN", ll=(12.6, 55.7), icon=icon_arctic,
         head="Denmark approves Arctic security pact with Greenland & US",
         text="Covers the Arctic and North Atlantic."),
    dict(n=8, region="AMERICAS", where="BOGOTÁ", ll=(-74.1, 4.6), icon=icon_protest,
         head="Mass protests in Colombia over taxes & cost of living",
         text="Second nationwide protest; police use water cannon."),
    dict(n=9, region="GLOBAL", where="WORLDWIDE", ll=None, icon=icon_game,
         head="GTA VI finally goes on sale after two delays",
         text="Rockstar's game unlocks at midnight local time on PS5 and Xbox."),
]

BRIEFS = [
    dict(n=10, region="ASIA", where="Seoul", ll=(127.0, 37.6), off=(0, 0),
         text="Top court sends ex-PM Han Duck-soo's martial-law case back for retrial."),
    dict(n=11, region="ASIA", where="Odisha", ll=(84.9, 19.3), off=(-9, 11),
         text="Coast evacuated to shelters as Cyclone Akvan nears landfall."),
    dict(n=12, region="OCEANIA", where="Canberra", ll=(149.1, -35.3), off=(0, 0),
         text="Jobless rate jumps to 4.9%, highest since 2021."),
    dict(n=13, region="EUROPE", where="Berlin", ll=(13.4, 52.5), off=(16, -11),
         text="Merz rejects a “Yalta 2.0” for Ukraine at Coalition of the Willing talks."),
    dict(n=14, region="EUROPE", where="Brussels", ll=(4.35, 50.85), off=(-20, 9),
         text="EU deal delays methane rules for fuel importers by two years."),
    dict(n=15, region="MIDEAST", where="Tehran", ll=(51.4, 35.7), off=(14, -7),
         text="Iran calls chemical-weapons allegations “fraudulent”."),
    dict(n=16, region="MIDEAST", where="Gaza", ll=(34.4, 31.4), off=(-6, 14),
         text="Israel ends one-day Nuseirat raid."),
    dict(n=17, region="ASIA", where="Ulaanbaatar", ll=(106.9, 47.9), off=(0, 0),
         text="President Khürelsükh's resignation accepted."),
    dict(n=18, region="ASIA", where="Bangladesh", ll=(91.8, 22.4), off=(7, -11),
         text="Suspected arson at Muhammad Yunus's ancestral home."),
    dict(n=19, region="AFRICA", where="Senegal", ll=(-17.4, 14.7), off=(0, 0),
         text="Dozens missing after migrant boat capsizes."),
    dict(n=20, region="AFRICA", where="Mogadishu", ll=(45.3, 2.0), off=(0, 0),
         text="Somalia expels UAE ambassador."),
    dict(n=21, region="AFRICA", where="Accra", ll=(-0.2, 5.6), off=(0, 0),
         text="Ghana defends $61m presidential jet purchase."),
    dict(n=22, region="AMERICAS", where="Florida", ll=(-80.2, 26.1), off=(0, 0),
         text="Floods shut Broward and Miami-Dade schools."),
    dict(n=23, region="AMERICAS", where="Brasília", ll=(-47.9, -15.8), off=(0, 0),
         text="Senate passes fiscal package 69–2."),
]

MAP_OFFSETS = {1: (0, 0), 2: (-21, -12), 3: (0, 0), 4: (14, -8), 5: (0, 0), 6: (-16, 4),
               7: (0, -17), 8: (0, 0)}

SOURCES = ("Sources: Reuters, AP, AFP, Euronews, Al Jazeera, RTÉ, CBS Miami, ABS, "
           "European Commission, Rockstar Games, Fortune, Morning Star, allAfrica, Rio Times")

REGION_ORDER = ["ASIA", "EUROPE", "MIDEAST", "AFRICA", "AMERICAS", "OCEANIA", "GLOBAL"]


# ---------------------------------------------------------------- map (numbered)

MAP_W, MAP_H = 330, 188
LON0, LON1, LAT0, LAT1 = -108.0, 158.0, -42.0, 72.0

LANDS += [
    [(166.5, -46), (172.5, -40.5), (174.5, -36.5), (178.5, -37.5), (176, -41.5), (169, -46.5)],
    [(144.6, -40.7), (148.3, -40.9), (147.8, -43.2), (145.2, -42.6)],
    [(-72, -50), (-68, -55), (-66, -55), (-69, -52)],
]


def _y(lat):
    return (_merc(LAT1) - _merc(lat)) / (_merc(LAT1) - _merc(LAT0)) * MAP_H


def proj(lon, lat):
    return ((lon - LON0) / (LON1 - LON0) * MAP_W, _y(lat))


def marker(md, x, y, n, r=7):
    md.ellipse([x - r, y - r, x + r, y + r], fill=RED, outline=WHITE, width=1)
    f = F(SANS_BOLD, 9 if n < 10 else 8)
    s = str(n)
    md.text((x - md.textlength(s, font=f) / 2, y - 5), s, font=f, fill=WHITE)


def draw_map():
    m = Image.new("RGB", (MAP_W, MAP_H), SEA)
    md = ImageDraw.Draw(m)
    for poly in LANDS:
        md.polygon([proj(*p) for p in poly], fill=LAND)
    for poly in SEAS:
        md.polygon([proj(*p) for p in poly], fill=SEA)
    pts = [(LEAD["n"], LEAD["ll"], (0, 0))]
    pts += [(c["n"], c["ll"], MAP_OFFSETS.get(c["n"], (0, 0))) for c in CELLS if c["ll"]]
    pts += [(b["n"], b["ll"], b["off"]) for b in BRIEFS]
    # true positions first, then leaders, then numbered markers on top
    for n, (lon, lat), (ox, oy) in pts:
        x, y = proj(lon, lat)
        if ox or oy:
            md.line([x, y, x + ox, y + oy], fill=INK, width=1)
            md.ellipse([x - 2, y - 2, x + 2, y + 2], fill=INK)
    for n, (lon, lat), (ox, oy) in pts:
        x, y = proj(lon, lat)
        x, y = min(max(x + ox, 8), MAP_W - 8), min(max(y + oy, 8), MAP_H - 8)
        marker(md, x, y, n)
    return m


# ---------------------------------------------------------------- page

def build(out):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    inner = W - 2 * MARGIN
    L, R = MARGIN, W - MARGIN

    # --- masthead: the date is the headline
    d.rectangle([0, 0, W, 6], fill=RED)
    kf = F(SANS_BOLD, 14)
    d.text((L, 14), "THE WORLD TODAY", font=kf, fill=RED)
    total = 1 + len(CELLS) + len(BRIEFS)
    rt = f"ONE DAY'S WORLD NEWS  ·  {total} STORIES  ·  ALL FROM THIS ONE DAY"
    d.text((R - text_w(d, rt, kf), 14), rt, font=kf, fill=INK)
    d.line([L, 34, R, 34], fill=INK, width=2)
    df = F(SERIF_BOLD, 74)
    while text_w(d, DATE_LONG, df) > inner:
        df = F(SERIF_BOLD, df.size - 2)
    d.text(((W - text_w(d, DATE_LONG, df)) / 2, 36), DATE_LONG, font=df, fill=INK)
    sf = F(SERIF_ITALIC, 18)
    sub = ("Three leaders at one table in Shenzhen · The World Court rules on Myanmar · "
           "COP31 draft drops fossil fuels")
    while text_w(d, sub, sf) > inner:
        sf = F(SERIF_ITALIC, sf.size - 1)
    d.text(((W - text_w(d, sub, sf)) / 2, 122), sub, font=sf, fill=RED)

    # --- region bar
    counts = {}
    for it in [LEAD] + CELLS + BRIEFS:
        counts[it["region"]] = counts.get(it["region"], 0) + 1
    regs = [r for r in REGION_ORDER if counts.get(r)]
    by = 150
    rf = F(SANS_BOLD, 12)
    x = L
    min_w = {r: text_w(d, f"{r} {counts[r]}", rf) + 14 for r in regs}
    spare = inner - sum(min_w.values()) - 3 * (len(regs) - 1)
    for i, r in enumerate(regs):
        wdt = min_w[r] + spare * counts[r] / total
        d.rectangle([x, by, x + wdt, by + 20], fill=RED if i % 2 == 0 else INK)
        lab = f"{r} {counts[r]}"
        d.text((x + (wdt - text_w(d, lab, rf)) / 2, by + 3), lab, font=rf, fill=WHITE)
        x += wdt + 3

    # --- lead
    top = by + 32
    ill_w, ill_h = 400, 184
    draw_summit(d, L, top, ill_w, ill_h)
    tx = L + ill_w + 22
    twd = R - tx
    num_tag(d, tx, top, LEAD["n"], LEAD["where"])
    hf, hl = fit(d, LEAD["head"], SERIF_BOLD, twd, 3, 36, 26)
    ty = draw_lines(d, tx, top + 26, hl, hf, INK, lead=1.1)
    sf2, sl = fit(d, LEAD["text"], SERIF, twd, 4, 17, 14)
    ty = draw_lines(d, tx, ty + 6, sl, sf2, DETAIL, lead=1.3)
    lead_bottom = max(top + ill_h, ty) + 12
    d.line([L, lead_bottom, R, lead_bottom], fill=INK, width=3)

    # --- footer (date check), measured first
    foot_f = F(SANS, 12)
    check = ("DATE CHECK  Every story on this page happened, or was first reported, on "
             "Thursday 19 November 2026.")
    foot_h = 40
    foot_top = H - 14 - foot_h

    # --- bottom band: map + numbered briefs
    band_h = MAP_H + 26
    band_top = foot_top - 10 - band_h

    # --- 4 x 2 grid of stories between lead and band
    g_top, g_bot = lead_bottom + 2, band_top - 10
    cw = inner / 4
    ch = (g_bot - g_top) / 2
    pad = 10
    icon_s = 50
    for i, c in enumerate(CELLS):
        r, k = divmod(i, 4)
        cx, cy = L + k * cw, g_top + r * ch
        if k:
            d.line([cx, cy + 8, cx, cy + ch - 8], fill=RULE, width=1)
        if r:
            d.line([cx + (0 if k == 0 else 8), cy, cx + cw - (0 if k == 3 else 8), cy], fill=RULE, width=1)
        x0 = cx + (pad if k else 0)
        x1 = cx + cw - (pad if k < 3 else 0)
        wd = x1 - x0
        t = cy + 8
        c["icon"](d, x0, t, icon_s)
        num_tag(d, x0 + icon_s + 8, t + 14, c["n"], c["where"], max_w=wd - icon_s - 8)
        hy = t + icon_s + 6
        limit = cy + ch - 4
        dfnt, dl = fit(d, c["text"], SANS, wd, 2, 15, 12)
        d_h = 4 + len(dl) * line_h(dfnt, 1.22)
        for hs in range(21, 14, -1):
            hfn, hln = fit(d, c["head"], SERIF_BOLD, wd, 3, hs, 14)
            if hy + len(hln) * line_h(hfn, 1.12) + d_h <= limit:
                break
        hy = draw_lines(d, x0, hy, hln, hfn, INK, lead=1.12)
        end = draw_lines(d, x0, hy + 4, dl, dfnt, DETAIL, lead=1.22)
        assert end <= limit + 2, f"cell overflow: {c['where']} ({end:.0f} > {limit:.0f})"

    # --- map
    d.line([L, band_top - 4, R, band_top - 4], fill=INK, width=2)
    cap = F(SANS_BOLD, 12)
    d.text((L, band_top + 2), "WHERE IT HAPPENED", font=cap, fill=RED)
    d.text((L + text_w(d, "WHERE IT HAPPENED  ", cap), band_top + 3),
           "numbers match the stories", font=F(SERIF_ITALIC, 11), fill=GREY)
    my = band_top + 22
    img.paste(draw_map(), (int(L), int(my)))
    d.rectangle([L, my, L + MAP_W - 1, my + MAP_H - 1], outline=RULE, width=1)

    # --- briefs, two columns
    bx = L + MAP_W + 18
    d.text((bx, band_top + 2), "ALSO ON THURSDAY 19 NOVEMBER 2026", font=cap, fill=RED)
    colw = (R - bx - 16) / 2
    for size in range(14, 10, -1):
        bf, bbf = F(SANS, size), F(SANS_BOLD, size)
        hts = [len(brief_lines(d, b, bbf, bf, colw - 22)) * line_h(bf, 1.2) + 4 for b in BRIEFS]
        half = min(range(1, len(BRIEFS)), key=lambda k: max(sum(hts[:k]), sum(hts[k:])))
        layouts, ok = [], True
        for col in (BRIEFS[:half], BRIEFS[half:]):
            yy = band_top + 24
            rows = []
            for b in col:
                lines = brief_lines(d, b, bbf, bf, colw - 22)
                rows.append((b, lines, yy))
                yy += len(lines) * line_h(bf, 1.2) + 4
            ok = ok and yy <= band_top + band_h + 2
            layouts.append(rows)
        if ok:
            break
    for ci, rows in enumerate(layouts):
        x0 = bx + ci * (colw + 16)
        for b, lines, yy in rows:
            marker(d, x0 + 8, yy + bf.size / 2 + 1, b["n"])
            for li, ln in enumerate(lines):
                ly = yy + li * line_h(bf, 1.2)
                if li == 0:
                    d.text((x0 + 20, ly), b["where"], font=bbf, fill=INK)
                    off = text_w(d, b["where"] + " ", bbf)
                    d.text((x0 + 20 + off, ly), ln, font=bf, fill=DETAIL)
                else:
                    d.text((x0 + 20, ly), ln, font=bf, fill=DETAIL)

    # --- footer
    d.rectangle([L, foot_top, R, foot_top + foot_h], outline=RED, width=2)
    cx0, cy0 = L + 12, foot_top + 10
    d.line([cx0, cy0 + 6, cx0 + 5, cy0 + 11, cx0 + 14, cy0], fill=RED, width=3)
    cf = F(SANS_BOLD, 12)
    d.text((cx0 + 22, foot_top + 7), check, font=cf, fill=INK)
    srcf = foot_f
    while text_w(d, SOURCES, srcf) > inner - 34:
        srcf = F(SANS, srcf.size - 1)
    d.text((cx0 + 22, foot_top + 25), SOURCES, font=srcf, fill=GREY)
    d.rectangle([0, H - 5, W, H], fill=RED)

    img.save(out, "PNG", optimize=True)
    return os.path.getsize(out)


def num_tag(d, x, y, n, where, max_w=None):
    marker(d, x + 8, y + 8, n, r=8)
    f = F(SANS_BOLD, 13)
    while max_w and text_w(d, where, f) > max_w - 22 and f.size > 9:
        f = F(SANS_BOLD, f.size - 1)
    d.text((x + 21, y + 1), where, font=f, fill=RED)


def brief_lines(d, b, bold, reg, width):
    """Wrap a brief whose first line starts after the bold place name."""
    lead_w = text_w(d, b["where"] + " ", bold)
    words, lines, cur, avail = b["text"].split(), [], "", width - lead_w
    for w in words:
        t = w if not cur else cur + " " + w
        if text_w(d, t, reg) <= avail:
            cur = t
        else:
            lines.append(cur)
            cur, avail = w, width
    lines.append(cur)
    return lines


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "entry.png")
    size = build(out)
    assert size <= 1048576, size
    print(f"wrote {out} ({size} bytes)")
