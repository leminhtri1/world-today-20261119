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

# (label, [(lon, lat), ...], label anchor: 'r' right, 'l' left, 'a' above, 'b' below)
PLACES = [
    ("SHENZHEN", [(114.1, 22.5)], "b"),
    ("THE HAGUE", [(4.3, 52.1)], "l"),
    ("COPENHAGEN", [(12.6, 55.7)], "a"),
    ("KYIV / KERCH", [(30.5, 50.4), (36.5, 45.3)], "r"),
    ("RIYADH", [(46.7, 24.7)], "b"),
    ("NEW YORK", [(-74.0, 40.7)], "r"),
    ("BOGOTÁ", [(-74.1, 4.6)], "r"),
]


def draw_map():
    m = Image.new("RGB", (MAP_W, MAP_H), SEA)
    md = ImageDraw.Draw(m)
    for poly in LANDS:
        md.polygon([proj(*p) for p in poly], fill=LAND)
    for poly in SEAS:
        md.polygon([proj(*p) for p in poly], fill=SEA)
    lf = F(SANS_BOLD, 11)
    for label, pts, side in PLACES:
        xy = [proj(*p) for p in pts]
        for (x, y) in xy:
            md.ellipse([x - 4, y - 4, x + 4, y + 4], fill=RED, outline=WHITE, width=1)
        x, y = xy[0]
        tw = md.textlength(label, font=lf)
        if side == "r":
            x2 = max(px for px, _ in xy)
            tx, ty = x2 + 7, y - 7
        elif side == "l":
            tx, ty = x - 7 - tw, y - 7
        elif side == "a":
            tx, ty = x - tw / 2, y - 20
        else:
            tx, ty = x - tw / 2, y + 6
        tx = min(max(tx, 2), MAP_W - 2 - tw)
        md.text((tx, ty), label, font=lf, fill=INK)
    return m


# ---------------------------------------------------------------- content

DATE = "THURSDAY 19 NOVEMBER 2026"

LEAD_KICKER = "SHENZHEN, CHINA  ·  APEC SUMMIT"
LEAD_HEAD = "Trump, Xi & Putin hold first-ever three-way summit in Shenzhen"
LEAD_SUM = ("The US, Chinese and Russian leaders met on the sidelines of the APEC summit "
            "in Shenzhen, China — their first trilateral meeting. "
            "Trump left China without meeting Kim Jong-un.")

STORIES = [
    ("THE HAGUE", icon_scales,
     "World Court: Myanmar committed genocide against Rohingya",
     "First such ICJ ruling against a state."),
    ("NEW YORK", icon_chart,
     "Anthropic debuts on Nasdaq at ~$1.5T valuation",
     "Ticker ANT; IPO priced at $83, above the $70–78 range."),
    ("UKRAINE", icon_bridge,
     "Ukraine hits Kerch Bridge again; Russian strikes damage embassies in Kyiv",
     "Third strike in four days halts rail traffic; Austrian and Dutch embassies damaged."),
    ("RIYADH", icon_tower,
     "Houthi strike hits Riyadh's tallest tower",
     "Public Investment Fund Tower damaged as Iran war spreads; no casualties reported."),
    ("COPENHAGEN", icon_arctic,
     "Denmark approves Arctic security pact with Greenland & US",
     "Deal strengthens security in the Arctic and North Atlantic."),
    ("BOGOTÁ", icon_protest,
     "Mass protests in Colombia over taxes & cost of living",
     "Second nationwide protest; police use water cannon."),
]

TICKER = [
    "Mongolia: President Khürelsükh's resignation accepted",
    "Senegal: dozens missing after migrant boat capsizes",
    "Somalia expels UAE ambassador",
    "Bangladesh: suspected arson at Muhammad Yunus's ancestral home",
    "Gaza: Israel ends one-day Nuseirat raid",
]


# ---------------------------------------------------------------- page

def build(out):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    inner = W - 2 * MARGIN

    # Masthead
    d.rectangle([0, 0, W, 8], fill=RED)
    title_f = F(SERIF_BOLD, 64)
    title = "THE WORLD TODAY"
    tw = text_w(d, title, title_f)
    d.text(((W - tw) / 2, 18), title, font=title_f, fill=INK)
    y = 96
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=3)
    date_f = F(SANS_BOLD, 17)
    d.text((MARGIN, y + 8), DATE, font=date_f, fill=INK)
    tag = "ONE DAY'S WORLD NEWS"
    d.text((W - MARGIN - text_w(d, tag, date_f), y + 8), tag, font=date_f, fill=RED)
    y += 34
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=1)

    # Lead story (about 40% of the page incl. masthead)
    lead_top = y + 14
    panel_x = W - MARGIN - MAP_W
    text_wd = panel_x - 24 - MARGIN

    kick_f = F(SANS_BOLD, 15)
    d.rectangle([MARGIN, lead_top, MARGIN + text_w(d, LEAD_KICKER, kick_f) + 16, lead_top + 24], fill=RED)
    d.text((MARGIN + 8, lead_top + 4), LEAD_KICKER, font=kick_f, fill=WHITE)

    head_f, head_lines = fit(d, LEAD_HEAD, SERIF_BOLD, text_wd, 3, 42, 34)
    ty = draw_lines(d, MARGIN, lead_top + 34, head_lines, head_f, INK, lead=1.12)

    # three small flags in a row under the headline
    fx, fy = MARGIN, ty + 4
    flag_w, flag_h = 48, 32
    lab_f = F(SANS_BOLD, 13)
    for label, fn in (("USA", flag_us), ("CHINA", flag_cn), ("RUSSIA", flag_ru)):
        fn(d, fx, fy, flag_w, flag_h)
        d.text((fx + flag_w + 8, fy + flag_h / 2 - 8), label, font=lab_f, fill=INK)
        fx += flag_w + 8 + text_w(d, label, lab_f) + 22
    ty = fy + flag_h + 8

    sum_f, sum_lines = fit(d, LEAD_SUM, SERIF, text_wd, 4, 18, 15)
    ty = draw_lines(d, MARGIN, ty, sum_lines, sum_f, GREY, lead=1.32)

    # world map panel on the right
    cap_f = F(SANS_BOLD, 12)
    cap = "WHERE THE NEWS HAPPENED"
    map_y = max(lead_top + 22, (lead_top + ty) / 2 - MAP_H / 2 + 6)  # centred on the lead column
    d.text((panel_x, map_y - 20), cap, font=cap_f, fill=RED)
    img.paste(draw_map(), (int(panel_x), int(map_y)))
    d.rectangle([panel_x, map_y, panel_x + MAP_W - 1, map_y + MAP_H - 1], outline=RULE, width=1)
    map_bottom = map_y + MAP_H
    d.line([panel_x - 12, lead_top, panel_x - 12, max(ty, map_bottom)], fill=RULE, width=1)

    lead_bottom = max(ty, map_bottom) + 10
    d.line([MARGIN, lead_bottom, W - MARGIN, lead_bottom], fill=INK, width=3)

    # Ticker geometry first, so the grid can take what is left
    label = "IN BRIEF"
    lab_w = text_w(d, label, F(SANS_BOLD, 15)) + 24
    tick_wd = inner - lab_w - 24
    for size in range(18, 12, -1):
        tick_f = F(SANS, size)
        tick_lines = wrap_items(d, TICKER, tick_f, tick_wd)
        if len(tick_lines) <= 3:
            break
    TICK_LEAD = 1.5
    tick_h = len(tick_lines) * line_h(tick_f, TICK_LEAD) + 16
    tick_top = H - 20 - tick_h  # bottom margin below the strip

    # 2 x 3 grid
    grid_top = lead_bottom + 2
    grid_bot = tick_top - 10
    cell_w = inner / 3
    cell_h = (grid_bot - grid_top) / 2
    pad = 12
    icon_s = 60
    place_f = F(SANS_BOLD, 17)
    for i, (place, icon, head, detail) in enumerate(STORIES):
        r, c = divmod(i, 3)
        cx = MARGIN + c * cell_w
        cy = grid_top + r * cell_h
        if c:
            d.line([cx, cy + 10, cx, cy + cell_h - 10], fill=RULE, width=1)
        if r:
            d.line([cx + (0 if c == 0 else 10), cy, cx + cell_w - (0 if c == 2 else 10), cy], fill=RULE, width=1)
        x0 = cx + (pad if c else 0)
        x1 = cx + cell_w - (pad if c < 2 else 0)
        wd = x1 - x0
        top = cy + pad
        icon(d, x0, top, icon_s)
        d.text((x0 + icon_s + 12, top + 14), place, font=place_f, fill=RED)
        d.line([x0 + icon_s + 12, top + 37, x0 + icon_s + 12 + 40, top + 37], fill=RED, width=2)
        hy = top + icon_s + 8
        limit = cy + cell_h - 6
        df, dl = fit(d, detail, SANS, wd, 3, 17, 14)
        d_h = 6 + len(dl) * line_h(df, 1.25)
        for hsize in range(24, 16, -1):  # largest headline that leaves room for the detail
            hf, hl = fit(d, head, SERIF_BOLD, wd, 3, hsize, 16)
            if hy + len(hl) * line_h(hf, 1.12) + d_h <= limit:
                break
        hy = draw_lines(d, x0, hy, hl, hf, INK, lead=1.12)
        end = draw_lines(d, x0, hy + 6, dl, df, DETAIL, lead=1.25)
        assert end <= limit + 2, f"cell overflow: {place} ({end:.0f} > {limit:.0f})"

    # Ticker strip
    d.rectangle([MARGIN, tick_top, W - MARGIN, tick_top + tick_h], fill=INK)
    d.rectangle([MARGIN, tick_top, MARGIN + lab_w, tick_top + tick_h], fill=RED)
    lf = F(SANS_BOLD, 15)
    d.text((MARGIN + 12, tick_top + tick_h / 2 - 9), label, font=lf, fill=WHITE)
    lh = line_h(tick_f, TICK_LEAD)
    draw_lines(d, MARGIN + lab_w + 14, tick_top + 8 + (lh - tick_f.size) / 2 - 2,
               tick_lines, tick_f, WHITE, lead=TICK_LEAD)
    d.rectangle([0, H - 4, W, H], fill=RED)

    img.save(out, "PNG", optimize=True)
    return os.path.getsize(out)


def wrap_items(d, items, font, width):
    """Pack whole ticker items onto lines, separated by bullets."""
    sep = "  •  "
    lines, cur = [], ""
    for item in items:
        trial = item if not cur else cur + sep + item
        if text_w(d, trial, font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = item
            if text_w(d, item, font) > width:
                return [""] * 99  # item alone too wide: caller tries a smaller size
    if cur:
        lines.append(cur)
    return lines


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "entry.png")
    size = build(out)
    assert size <= 1048576, size
    print(f"wrote {out} ({size} bytes)")
