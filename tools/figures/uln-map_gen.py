# -*- coding: utf-8 -*-
"""Figure 'uln-map' -- annotated pin map of the ULN2803A photo.

Source: C:\\Claude\\PrototypeImages\\IMG_2456.jpg (2160x2880).
Chip lies landscape, printing upright, notch at LEFT (verified in zoom crops);
no rotation needed. 18-pin DIP: bottom row L->R = pins 1..9 (IN1..IN8, GND),
top row L->R = pins 18..10 (OUT1..OUT8, COM). OUT = 19 - IN, directly across.
"""
from PIL import Image, ImageDraw, ImageFont

SRC = r"C:\Claude\PrototypeImages\IMG_2456.jpg"
OUT = (r"C:\Users\Marcelo\AppData\Local\Temp\claude\C--Claude-gimbal-bench"
       r"\bc442eb3-8a91-49f8-a2b1-fd632e9c7a40\scratchpad\anno\uln-map.jpg")

# ---- ground truth in ORIGINAL pixels (verified against zoom crops) ----------
# pin positions = center of the visible metal face of each pin.
COORDS = {
    # bottom row, left -> right (pin 1 starts at the notch end)
    "pin1":  (412, 1932),  "pin2":  (560, 1932),  "pin3":  (708, 1932),
    "pin4":  (856, 1932),  "pin5":  (1004, 1932), "pin6":  (1152, 1932),
    "pin7":  (1301, 1932), "pin8":  (1449, 1932), "pin9":  (1597, 1932),
    # top row, left -> right (pin 18 is across from pin 1)
    "pin18": (417, 1497),  "pin17": (564, 1497),  "pin16": (712, 1497),
    "pin15": (859, 1497),  "pin14": (1006, 1497), "pin13": (1154, 1497),
    "pin12": (1301, 1497), "pin11": (1448, 1497), "pin10": (1595, 1497),
    # the semicircular notch on the left edge of the body
    "notch": (360, 1708),
}
TOP_TIP_Y, TOP_BODY_Y = 1462, 1530     # top pin outer tip / body top edge
BOT_BODY_Y, BOT_TIP_Y = 1902, 1968     # body bottom edge / bottom pin outer tip

# ---- crop + paste geometry --------------------------------------------------
CROP = (140, 1385, 1740, 2025)         # tight around chip, extra room at left
PX, PY = 70, 300                       # paste position on canvas
S = 1660.0 / (CROP[2] - CROP[0])       # paste scale (1660 px wide photo)
W, H = 1800, 1210

def cx(ox): return int(round(PX + (ox - CROP[0]) * S))
def cy(oy): return int(round(PY + (oy - CROP[1]) * S))

# ---- palette ----------------------------------------------------------------
INK      = "#222233"
NOTCH_C  = "#c2571a"
ZONE_A   = "#c47a00"
ZONE_B   = "#2e86c1"
GREY_C   = "#7a7a7a"
BLUE_C   = "#2e86c1"
AMBER_C  = "#c47a00"
RED_C    = "#cc3333"
CAUT_BG, CAUT_BD, CAUT_TX = "#fffbe8", "#c9a227", "#6b5200"

FD = r"C:\Windows\Fonts"
f_title  = ImageFont.truetype(FD + r"\arialbd.ttf", 40)
f_sub    = ImageFont.truetype(FD + r"\arial.ttf",   22)
f_lab    = ImageFont.truetype(FD + r"\arialbd.ttf", 22)
f_lab20  = ImageFont.truetype(FD + r"\arialbd.ttf", 20)
f_num    = ImageFont.truetype(FD + r"\arialbd.ttf", 20)
f_caut_b = ImageFont.truetype(FD + r"\arialbd.ttf", 22)
f_caut_r = ImageFont.truetype(FD + r"\arial.ttf",   22)

canvas = Image.new("RGB", (W, H), "#ffffff")
d = ImageDraw.Draw(canvas)

# ---- photo ------------------------------------------------------------------
photo = Image.open(SRC).crop(CROP)
pw, ph = int(round(photo.width * S)), int(round(photo.height * S))
photo = photo.resize((pw, ph), Image.LANCZOS)
canvas.paste(photo, (PX, PY))
d.rectangle([PX - 3, PY - 3, PX + pw + 2, PY + ph + 2], outline="#333344", width=3)
PHOTO_BOT = PY + ph

def tw(font, s): return d.textlength(s, font=font)

def label_box(center_x, center_y, text, border, font=f_lab):
    w = tw(font, text)
    x0, x1 = center_x - w / 2 - 10, center_x + w / 2 + 10
    d.rectangle([x0, center_y - 22, x1, center_y + 22],
                fill="#ffffff", outline=border, width=2)
    d.text((center_x - w / 2, center_y - 12), text, font=font, fill=INK)
    return (x0, center_y - 22, x1, center_y + 22)

def ring(x, y, r, color, wu=9, wc=5):
    d.ellipse([x - r, y - r, x + r, y + r], outline="#ffffff", width=wu + wc)
    d.ellipse([x - r, y - r, x + r, y + r], outline=color, width=wc)

def badge(x, y, s):
    w = max(30, tw(f_num, s) + 14)
    d.rounded_rectangle([x - w / 2, y - 15, x + w / 2, y + 15], radius=8,
                        fill="#ffffff", outline="#333344", width=2)
    d.text((x - tw(f_num, s) / 2, y - 11), s, font=f_num, fill=INK)

def varrow(x, y0, y1, color):
    d.line([(x, y0), (x, y1)], fill="#ffffff", width=14)
    d.line([(x, y0), (x, y1)], fill=color, width=6)
    for ty, sgn in ((y0, 1), (y1, -1)):
        tri = [(x, ty), (x - 12, ty + sgn * 22), (x + 12, ty + sgn * 22)]
        d.polygon(tri, fill="#ffffff", outline="#ffffff", width=6)
        d.polygon(tri, fill=color)

# ---- title ------------------------------------------------------------------
d.text((40, 28), "Doc 4a \u00b7 How to read the ULN2803", font=f_title,
       fill="#111111")
d.text((40, 82), "Count from the notch and every pin explains itself \u2014 "
                 "inputs along the bottom, their switches directly across.",
       font=f_sub, fill="#555555")

# ---- cross arrows (drawn before their shared label) -------------------------
for a, b, col in (("pin1", "pin18", AMBER_C), ("pin2", "pin17", GREY_C),
                  ("pin3", "pin16", BLUE_C)):
    x = (cx(COORDS[a][0]) + cx(COORDS[b][0])) // 2
    varrow(x, cy(TOP_BODY_Y) + 14, cy(BOT_BODY_Y) - 14, col)
label_box((cx(COORDS["pin2"][0]) + cx(COORDS["pin3"][0])) // 2 + 30, 644,
          "directly across: OUT = 19 \u2212 IN", "#333344", font=f_lab20)

# ---- notch ring + label -----------------------------------------------------
nx, ny = cx(COORDS["notch"][0]), cy(COORDS["notch"][1])
ring(nx, ny, 30, NOTCH_C)
d.rectangle([78, 566, 246, 648], fill="#ffffff", outline=NOTCH_C, width=2)
d.text((92, 578), "the notch =", font=f_lab20, fill=INK)
d.text((92, 606), "the pin-1 end", font=f_lab20, fill=INK)
d.line([(246, 622), (nx - 36, ny - 5)], fill=NOTCH_C, width=3)

# ---- pin numerals -----------------------------------------------------------
for n in range(1, 10):                                   # bottom row: 1..9
    x = cx(COORDS["pin%d" % n][0])
    d.line([(x, cy(BOT_TIP_Y) + 2), (x, 918)], fill="#333344", width=2)
    badge(x, 935, str(n))
for n in range(18, 9, -1):                               # top row: 18..10
    x = cx(COORDS["pin%d" % n][0])
    d.line([(x, 362), (x, cy(TOP_TIP_Y) - 2)], fill="#333344", width=2)
    badge(x, 346, str(n))

# ---- role labels: OUT row (above) -------------------------------------------
def brace(x_from, x_to, y, box_cx, box_edge, tick_to, color):
    d.line([(box_cx, box_edge), (box_cx, y)], fill=color, width=2)
    d.line([(x_from, y), (x_to, y)], fill=color, width=2)
    for x in (x_from, (x_from + x_to) // 2, x_to):
        d.line([(x, y), (x, tick_to)], fill=color, width=2)

bx = label_box((cx(417) + cx(712)) // 2, 163,
               "OUT 18\u00b717\u00b716 \u2014 zone A returns out", ZONE_A)
brace(cx(417), cx(712), 240, (cx(417) + cx(712)) // 2, bx[3], 296, ZONE_A)
bx = label_box((cx(859) + cx(1154)) // 2, 163,
               "OUT 15\u00b714\u00b713 \u2014 zone B", ZONE_B)
brace(cx(859), cx(1154), 240, (cx(859) + cx(1154)) // 2, bx[3], 296, ZONE_B)
bx = label_box(1560, 163, "COM p10 \u2014 leave EMPTY", RED_C)
d.line([(cx(1595), bx[3]), (cx(1595), 296)], fill=RED_C, width=2)

# ---- role labels: IN row (below) --------------------------------------------
bx = label_box((cx(412) + cx(708)) // 2, 1034,
               "IN 1\u00b72\u00b73 \u2014 zone A signals in", ZONE_A)
brace(cx(412), cx(708), 990, (cx(412) + cx(708)) // 2, bx[1], 968, ZONE_A)
bx = label_box((cx(856) + cx(1152)) // 2, 1034,
               "IN 4\u00b75\u00b76 \u2014 zone B", ZONE_B)
brace(cx(856), cx(1152), 990, (cx(856) + cx(1152)) // 2, bx[1], 968, ZONE_B)
bx = label_box(1555, 1034, "GND p9 \u2192 straight to the star", "#111111")
d.line([(cx(1597), bx[1]), (cx(1597), 968)], fill="#111111", width=2)

# ---- caution strip ----------------------------------------------------------
d.rectangle([40, 1080, 1760, 1176], fill=CAUT_BG, outline=CAUT_BD, width=3)
bold = "SEAT IT BY THE NOTCH, NEVER BY HABIT"
rest = (" \u2014 a chip in backwards puts the tape\u2019s 24 V returns on its "
        "logic inputs and dies at first power.")
d.text((70, 1098), bold, font=f_caut_b, fill=CAUT_TX)
d.text((70 + tw(f_caut_b, bold), 1098), rest, font=f_caut_r, fill=CAUT_TX)
d.text((70, 1132), "Match the notch to the socket\u2019s notch before power.",
       font=f_caut_r, fill=CAUT_TX)

canvas.save(OUT, quality=87)
print("saved", canvas.size)
