# -*- coding: utf-8 -*-
"""
spot-star_gen.py -- figure 'spot-star' for Doc 4b.
Source photo: C:\\Claude\\PrototypeImages\\IMG_2507.jpg (2160x2880).
ROTATION: none. The 'SJX-1 / LUXDRIVE' silkscreen at the plate's bottom edge
reads upright in the raw photo (verified by zoom-crop), so the photo is used as-is.
All COORDS below are in SOURCE-PHOTO pixels of the unrotated IMG_2507.jpg.

Printed polarity, transcribed from the plate's own silkscreen (zoom-crops):
  top pair   : '+' printed above-left pad, '-' printed above-right pad
  left pair  : '-' (bar, rotated ~vertical) beside UPPER pad, '+' (cross) beside LOWER pad
  right pair : '+' (cross) beside UPPER pad, '-' (bar, rotated ~diagonal) beside LOWER pad
  (a small printed square dot sits at (1596,1664) below the right die's corner;
   it is NOT one of the +/- polarity glyphs and is left unannotated)
"""
import math
from PIL import Image, ImageDraw, ImageFont

SRC = r"C:\Claude\PrototypeImages\IMG_2507.jpg"
OUT = r"C:\Users\Marcelo\AppData\Local\Temp\claude\C--Claude-gimbal-bench\bc442eb3-8a91-49f8-a2b1-fd632e9c7a40\scratchpad\anno\spot-star.jpg"

COORDS = {
    # crop of the source photo used as the figure photo (tight to star, ~60px margin)
    "crop": (715, 1080, 1820, 2175),
    "hole_center": (1235, 1635),
    # LED die (package) centers
    "die_left": (1065, 1505),
    "die_right": (1520, 1525),
    "die_bottom": (1245, 1900),
    # solder-pad centers, grouped as the three electrical +/- pairs
    "pad_top_left": (1224, 1387),      # printed '+'
    "pad_top_right": (1354, 1394),     # printed '-'
    "pad_left_upper": (1022, 1682),    # printed '-'
    "pad_left_lower": (1072, 1815),    # printed '+'
    "pad_right_upper": (1508, 1732),   # printed '+'
    "pad_right_lower": (1433, 1838),   # printed '-'
    # positions of the plate's own printed polarity glyphs (for reference / kept clear)
    "print_top_plus": (1205, 1283),
    "print_top_minus": (1363, 1297),
    "print_left_minus": (911, 1704),
    "print_left_plus": (976, 1849),
    "print_right_plus": (1588, 1780),
    "print_right_minus": (1497, 1910),
    "print_right_dot_not_polarity": (1596, 1664),
}

AMBER = "#c47a00"
GREY = "#7a7a7a"
BLUE = "#2e86c1"
GREEN = "#3f7c55"
INK = "#333344"
TXT = "#222233"

F = lambda n, s: ImageFont.truetype(n, s)
arialbd = r"C:\Windows\Fonts\arialbd.ttf"
arial = r"C:\Windows\Fonts\arial.ttf"

W, H = 1800, 1446
canvas = Image.new("RGB", (W, H), "#ffffff")
d = ImageDraw.Draw(canvas)

# ---------- photo ----------
im = Image.open(SRC)
cx0, cy0, cx1, cy1 = COORDS["crop"]
photo = im.crop(COORDS["crop"])
PX, PY = 340, 140  # photo top-left on canvas
canvas.paste(photo, (PX, PY))
pw, ph = photo.size

def disp(p):
    return (p[0] - cx0 + PX, p[1] - cy0 + PY)

pd = ImageDraw.Draw(canvas)

# ---------- ring helpers ----------
def ring_ellipse(center, a, b, theta_deg, color, w_under=9, w_col=5):
    cx, cy = center
    th = math.radians(theta_deg)
    pts = []
    for i in range(121):
        t = 2 * math.pi * i / 120
        x = a * math.cos(t)
        y = b * math.sin(t)
        xr = cx + x * math.cos(th) - y * math.sin(th)
        yr = cy + x * math.sin(th) + y * math.cos(th)
        pts.append((xr, yr))
    pd.line(pts, fill="#ffffff", width=w_under, joint="curve")
    pd.line(pts, fill=color, width=w_col, joint="curve")

def pair_ring(p1, p2, color, pad_reach=100, minor=80):
    x1, y1 = disp(p1); x2, y2 = disp(p2)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    half = math.hypot(dx, dy) / 2
    theta = math.degrees(math.atan2(dy, dx))
    ring_ellipse((cx, cy), half + pad_reach, minor, theta, color)
    return (cx, cy)

def leader(p_from, p_to, dot=True):
    pd.line([p_from, p_to], fill="#ffffff", width=7)
    pd.line([p_from, p_to], fill=INK, width=3)
    if dot:
        x, y = p_to
        pd.ellipse([x - 7, y - 7, x + 7, y + 7], fill="#ffffff")
        pd.ellipse([x - 5, y - 5, x + 5, y + 5], fill=INK)

def label_box(x, y, lines, w, border=INK, font=None, pad=12, lh=27, fill="#ffffff", tcol=TXT):
    font = font or F(arialbd, 20)
    h = pad * 2 + lh * len(lines) - 5
    pd.rectangle([x, y, x + w, y + h], fill=fill, outline=border, width=2)
    for i, ln in enumerate(lines):
        pd.text((x + pad, y + pad + i * lh), ln, font=font, fill=tcol)
    return (x, y, x + w, y + h)

def glyph(pos, ch, color, size=36):
    x, y = disp(pos)
    f = F(arialbd, size)
    bb = pd.textbbox((0, 0), ch, font=f)
    pd.text((x - (bb[0] + bb[2]) / 2, y - (bb[1] + bb[3]) / 2), ch, font=f,
            fill=color, stroke_width=3, stroke_fill="#ffffff")

MINUS = "\u2212"

# ---------- rings (drawn before boxes so boxes sit on top) ----------
top_c = pair_ring(COORDS["pad_top_left"], COORDS["pad_top_right"], AMBER, pad_reach=68, minor=72)
left_c = pair_ring(COORDS["pad_left_upper"], COORDS["pad_left_lower"], GREY, pad_reach=68, minor=76)
right_c = pair_ring(COORDS["pad_right_upper"], COORDS["pad_right_lower"], BLUE, pad_reach=68, minor=76)

# green ring around ONE die (the right die) -- no color-identity claim
gx, gy = disp(COORDS["die_right"])
gx, gy, gr = gx - 3, gy - 15, 145
ring_ellipse((gx, gy), gr, gr, 0, GREEN)

# ---------- channel +/- glyphs on the pads, exactly as the print assigns them ----------
glyph(COORDS["pad_top_left"], "+", AMBER)
glyph(COORDS["pad_top_right"], MINUS, AMBER)
glyph(COORDS["pad_left_upper"], MINUS, GREY)
glyph(COORDS["pad_left_lower"], "+", GREY)
glyph(COORDS["pad_right_upper"], "+", BLUE)
glyph(COORDS["pad_right_lower"], MINUS, BLUE)

# ---------- shared pairs label (central placement, below the center hole) ----------
# leaders first, then the box on top of their near ends
leader((940, 720), (930, 535))            # up to amber top-pair ring
leader((700, 764), (748, 790))            # to grey left-pair ring
leader((1020, 764), (1008, 806))          # to blue right-pair ring
shared = label_box(695, 716, ["three \u00b1 pairs \u2014 one per", "driver channel, wired at S4"], 330)

# ---------- green die label (right margin) ----------
gbox = label_box(1478, 330, ["three lamps, one plate \u2014", "unlit they look alike;", "named by light at S8"], 302, border=GREEN)
leader((1478, 392), (gx + gr * 0.88, gy - gr * 0.47))

# ---------- aluminum plate label (left margin) ----------
abox = label_box(18, 548, ["aluminum plate = the heat", "path \u2014 it mounts to the", "heatsink before anything", "else (S1)"], 302)
leader((320, 618), (505, 645))

# ---------- title / subtitle ----------
pd.text((40, 28), "Doc 4b \u00b7 The star, on the plate itself", font=F(arialbd, 40), fill="#111111")
pd.text((40, 82), "Three separate lamps and their printed \u00b1 marks \u2014 the polarity you flag at S2, "
                  "and the dies you name by light at S8.", font=F(arial, 22), fill="#555555")

# ---------- photo border ----------
pd.rectangle([PX - 2, PY - 2, PX + pw + 1, PY + ph + 1], outline=INK, width=3)

# ---------- captions ----------
cap1 = "this build\u2019s star \u00b7 LuxDrive SJX-1 \u00b7 three isolated dies"
f24 = F(arialbd, 24)
bb = pd.textbbox((0, 0), cap1, font=f24)
pd.text((PX + (pw - bb[2]) / 2, PY + ph + 14), cap1, font=f24, fill=TXT)
cap2 = "ring colors = driver channels, not die colors"
f20 = F(arialbd, 20)
bb2 = pd.textbbox((0, 0), cap2, font=f20)
pd.text((PX + (pw - bb2[2]) / 2, PY + ph + 50), cap2, font=f20, fill="#555555")

# ---------- danger strip ----------
ds_y0, ds_y1 = 1336, 1406
pd.rectangle([40, ds_y0, W - 40, ds_y1], fill="#fdecec", outline="#cc3333", width=2)
lead = "NEVER BARE, NEVER THE BUS \u2014 "
rest = ("at this build\u2019s ~330 mA (as shipped) the star dissipates ~3 W; heatsink first, "
        "wall-aimed always, and 24 V never touches these pads.")
fb = F(arialbd, 22); fr = F(arial, 22)
lw = pd.textbbox((0, 0), lead, font=fb)[2]
rw = pd.textbbox((0, 0), rest, font=fr)[2]
lx = 40 + (W - 80 - lw - rw) // 2
ty = ds_y0 + (ds_y1 - ds_y0 - 26) // 2
pd.text((lx, ty), lead, font=fb, fill="#8a1c1c")
pd.text((lx + lw, ty), rest, font=fr, fill="#8a1c1c")

canvas.save(OUT, quality=87)
print("saved", OUT, canvas.size)
