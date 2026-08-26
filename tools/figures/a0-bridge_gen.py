# -*- coding: utf-8 -*-
"""Figure 'a0-bridge': PCA9685 A0 address-jumper pads, open vs solder-bridged,
with the CP8b resistance check spelled out under each panel.
Source: clean board photo IMG_2452.jpg (2160x2880)."""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = r"C:/Claude/PrototypeImages/IMG_2452.jpg"
OUT = r"C:/Users/Marcelo/AppData/Local/Temp/claude/C--Claude-gimbal-bench/bc442eb3-8a91-49f8-a2b1-fd632e9c7a40/scratchpad/anno/a0-bridge.jpg"

# ---- COORDS: everything in ORIGINAL IMG_2452.jpg pixels (2160x2880) -----------
COORDS = {
    # bounding box of the six-pair I2C address strip (A5 top ... A0 bottom)
    "strip_bbox": (1467, 1755, 1625, 2370),
    # per-pair centers (pair = left+right pad), top of strip to bottom
    "pair_centers": {
        "A5": (1532, 1801), "A4": (1535, 1906), "A3": (1538, 2011),
        "A2": (1541, 2116), "A1": (1544, 2220), "A0": (1547, 2327),
    },
    # A0 pad-pair: individual pad centers and pad size (w,h)
    "a0_pad_left":  (1516, 2327),
    "a0_pad_right": (1578, 2327),
    "pad_size": (50, 64),
    # region cropped for the panels (includes A2, A1, A0 + silkscreen)
    "crop_box": (1370, 2020, 1680, 2430),
    # crop is rotated 90 deg CCW so the A2/A1/A0 silkscreen reads upright
    "rotate": "CCW90",
}

# ---- layout -------------------------------------------------------------------
CANVAS_W = 1600
PANEL_W  = 700
LX, RX   = 40, 860            # panel left edges
PANEL_TOP = 176
GREEN, RED = "#3f7c55", "#cc3333"
INK = "#222233"

CX0, CY0, CX1, CY1 = COORDS["crop_box"]
CW, CH = CX1 - CX0, CY1 - CY0          # 310 x 410
S = PANEL_W / float(CH)                # scale after rotation (rotated width = CH)
PANEL_H = int(round(CW * S))

def o2p(px, py):
    """original photo px -> panel-local px (after CCW90 rotate + scale)."""
    rx = (py - CY0)
    ry = (CW - 1) - (px - CX0)
    return (rx * S, ry * S)

def font(bold, size):
    p = r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"
    return ImageFont.truetype(p, size)

# ---- build the shared panel image --------------------------------------------
src = Image.open(SRC)
crop = src.crop(COORDS["crop_box"]).transpose(Image.ROTATE_90)
panel_base = crop.resize((PANEL_W, PANEL_H), Image.LANCZOS)

pad_l = o2p(*COORDS["a0_pad_left"])    # bottom pad in panel frame
pad_r = o2p(*COORDS["a0_pad_right"])   # top pad in panel frame
pair_c = ((pad_l[0] + pad_r[0]) / 2.0, (pad_l[1] + pad_r[1]) / 2.0)
pad_w, pad_h = COORDS["pad_size"]
# in the rotated frame the pad's w/h swap: extent along x = pad_h, along y = pad_w
ext_x, ext_y = pad_h * S, pad_w * S
pair_span_y = abs(pad_l[1] - pad_r[1]) + ext_y     # full pair height

def draw_ring(im, color):
    d = ImageDraw.Draw(im)
    rx, ry = ext_x / 2 + 26, pair_span_y / 2 + 22
    bb = [pair_c[0] - rx, pair_c[1] - ry, pair_c[0] + rx, pair_c[1] + ry]
    d.ellipse(bb, outline="#ffffff", width=9)
    d.ellipse(bb, outline=color, width=5)

def draw_blob(im):
    """silver-grey solder blob spanning both A0 pads."""
    cx, cy = pair_c
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rx, ry = 46, 82
    # darker rim: slightly bigger shape underneath
    for (ox, oy, fx, fy) in [(0, 0, 1.0, 1.0), (-4, -30, 0.86, 0.42), (3, 32, 0.9, 0.44)]:
        d.ellipse([cx - rx * fx + ox - 4, cy - ry * fy + oy - 4,
                   cx + rx * fx + ox + 4, cy + ry * fy + oy + 4], fill="#5d616a")
    # body
    for (ox, oy, fx, fy) in [(0, 0, 1.0, 1.0), (-4, -30, 0.86, 0.42), (3, 32, 0.9, 0.44)]:
        d.ellipse([cx - rx * fx + ox, cy - ry * fy + oy,
                   cx + rx * fx + ox, cy + ry * fy + oy], fill="#9aa0a9")
    # soft inner shading (lower right, blended) + small specular highlight
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.ellipse([cx - 6, cy + 14, cx + rx - 8, cy + ry - 16], fill="#7e848e")
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    lay.paste(sh, (0, 0), sh)
    hi = Image.new("RGBA", im.size, (0, 0, 0, 0))
    dh = ImageDraw.Draw(hi)
    dh.ellipse([cx - 24, cy - 54, cx + 2, cy - 14], fill="#e6e9ee")
    dh.ellipse([cx - 18, cy - 44, cx - 4, cy - 26], fill="#f7f9fb")
    hi = hi.filter(ImageFilter.GaussianBlur(2.5))
    lay.paste(hi, (0, 0), hi)
    lay = lay.filter(ImageFilter.GaussianBlur(1.4))
    im.paste(lay, (0, 0), lay)

def draw_probe(im, tip, direction, color):
    """probe glyph: silver needle at the tip, slim colored handle behind it."""
    d = ImageDraw.Draw(im)
    L = 132
    dx, dy = direction
    n = math.hypot(dx, dy); dx, dy = dx / n, dy / n
    px, py = -dy, dx
    def at(t): return (tip[0] + t * L * dx, tip[1] + t * L * dy)
    # colored handle: trapezoid from 28% to 100% of length
    n0, b = at(0.28), at(1.0)
    poly = [(n0[0] + 5 * px, n0[1] + 5 * py), (b[0] + 15 * px, b[1] + 15 * py),
            (b[0] - 15 * px, b[1] - 15 * py), (n0[0] - 5 * px, n0[1] - 5 * py)]
    d.polygon(poly, fill=color, outline="#ffffff")
    # silver needle from the pad-touching tip back to the handle
    d.line([tip, at(0.31)], fill="#8f959d", width=7)
    d.line([tip, at(0.31)], fill="#ccd1d8", width=3)

def label_box(d, xy, text, border, f):
    tw = d.textlength(text, font=f)
    x, y = xy
    box = [x, y, x + tw + 26, y + f.size + 18]
    d.rectangle(box, fill="#ffffff", outline=border, width=2)
    d.text((x + 13, y + 9), text, font=f, fill=INK)
    return box

def meter_box(d, cx, y, text, f):
    tw = d.textlength(text, font=f)
    box = [cx - tw / 2 - 18, y, cx + tw / 2 + 18, y + f.size + 22]
    d.rectangle(box, fill="#ffffff", outline="#000000", width=2)
    d.text((cx - tw / 2, y + 11), text, font=f, fill="#111111")
    return box[3]

def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for wd in text.split(" "):
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = wd
    if cur: lines.append(cur)
    return lines

# ---- panels -------------------------------------------------------------------
tip_r = (pad_r[0] + 30, pad_r[1] - 6)   # on the top pad's gold, right of the blob
tip_l = (pad_l[0] + 30, pad_l[1] + 6)   # on the bottom pad's gold
left_p = panel_base.copy()
draw_probe(left_p, tip_r, (0.75, -0.66), "#c8322b")
draw_probe(left_p, tip_l, (0.75, 0.66), "#1a1a1a")
draw_ring(left_p, GREEN)

right_p = panel_base.copy()
draw_blob(right_p)
draw_probe(right_p, tip_r, (0.75, -0.66), "#c8322b")
draw_probe(right_p, tip_l, (0.75, 0.66), "#1a1a1a")
draw_ring(right_p, RED)

# ---- canvas -------------------------------------------------------------------
canvas = Image.new("RGB", (CANVAS_W, 1100), "#ffffff")
d = ImageDraw.Draw(canvas)

f_title = font(True, 40); f_sub = font(False, 22)
f_cap = font(True, 24);   f_lab = font(True, 21)
f_met = font(True, 21);   f_dgr = font(True, 20)

d.text((40, 28), "Doc 4a \u00b7 The A0 blob, before and after", font=f_title, fill="#111111")
d.text((40, 86), "The same pads on both boards \u2014 hub #1 keeps them open, "
                 "hub #2 gets the bridge, and CP8b is how you prove which is which.",
       font=f_sub, fill="#555555")

for x0, im, cap in [(LX, left_p, "hub #1 \u2014 A0 stays OPEN"),
                    (RX, right_p, "hub #2 \u2014 A0 BRIDGED with solder")]:
    cw = d.textlength(cap, font=f_cap)
    d.text((x0 + PANEL_W / 2 - cw / 2, 138), cap, font=f_cap, fill=INK)
    canvas.paste(im, (x0, PANEL_TOP))
    d.rectangle([x0 - 3, PANEL_TOP - 3, x0 + PANEL_W + 2, PANEL_TOP + PANEL_H + 2],
                outline="#333344", width=3)

# label boxes inside panels (over the desk sliver at panel top-left)
dl = ImageDraw.Draw(canvas)
label_box(dl, (LX + 16, PANEL_TOP + 12), "\u2192 answers at 0x40", GREEN, f_lab)
label_box(dl, (RX + 16, PANEL_TOP + 12), "\u2192 answers at 0x41", RED, f_lab)

# meter readings under panels
my = PANEL_TOP + PANEL_H + 18
b1 = meter_box(dl, LX + PANEL_W / 2, my, "meter across the pair: high \u2014 k\u03a9 or OL", f_met)
b2 = meter_box(dl, RX + PANEL_W / 2, my, "meter across the pair: ~0 \u03a9", f_met)

# danger strip
dg_text = ("A BLOB CAN LOOK BRIDGED AND TOUCH ONLY ONE PAD \u2014 it photographs "
           "beautifully and fails CP8b. Measure, don\u2019t admire: near 0 \u03a9 on "
           "hub #2, high on hub #1. Bridge with everything unpowered, BEFORE the "
           "board\u2019s bus wires land.")
sy = int(max(b1, b2)) + 26
lines = wrap(dl, dg_text, f_dgr, CANVAS_W - 80 - 48)
sh = 20 + len(lines) * 30 + 14
dl.rectangle([40, sy, CANVAS_W - 40, sy + sh], fill="#fdecec", outline=RED, width=3)
for i, ln in enumerate(lines):
    dl.text((64, sy + 17 + i * 30), ln, font=f_dgr, fill="#8a1c1c")

canvas = canvas.crop((0, 0, CANVAS_W, sy + sh + 36))
canvas.save(OUT, quality=87)
print("saved", OUT, canvas.size)
