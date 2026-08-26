# -*- coding: utf-8 -*-
"""Doc 4a figure 'two-hubs': ESP32-C6 + two PCA9685 hubs, shared 4-wire I2C bus."""
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# COORDS: every pad position in ORIGINAL image pixels (verified by zoom-crops
# of the silkscreen). crop = tight box around the component (+~40px margin).
# ---------------------------------------------------------------------------
COORDS = {
    "c6": {
        "src": r"C:\Claude\PrototypeImages\IMG_2449.jpg",
        "crop": (310, 130, 1730, 2670),          # antenna up, portrait
        "pins": {                                 # verified: L col GND,3V3,RST...  R col GND,2,3,TX...
            "3V3": (450, 694),                    # left column, 2nd pin
            "GND": (1559, 534),                   # right column, top pin (square pad)
            "SDA": (1568, 652),                   # right column, GPIO2
            "SCL": (1570, 758),                   # right column, GPIO3
        },
    },
    "pca": {
        "src": r"C:\Claude\PrototypeImages\IMG_2452.jpg",
        "crop": (320, 80, 1840, 2820),            # portrait, control header at top
        "pads": {                                 # verified top header L->R: V+ VCC SDA SCL OE GND
            "V+":  (829, 196),
            "VCC": (932, 200),
            "SDA": (1034, 196),
            "SCL": (1137, 194),
            "OE":  (1241, 191),
            "GND": (1343, 189),
        },
        "a0_left":  (1516, 2328),                 # A0 solder-jumper pad pair (strip end, by corner GND)
        "a0_right": (1578, 2331),
    },
}

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
CANVAS_W, CANVAS_H = 1960, 1292
TARGET_H = 900.0
PASTE = {"c6": (40, 200), "hub1": (660, 200), "hub2": (1290, 200)}

C_PURPLE = "#7b2d8b"   # 3V3 / VCC
C_BLACK  = "#222222"   # GND
C_BLUE   = "#1d6fd6"   # SDA
C_TEAL   = "#0e8a7a"   # SCL
C_RED    = "#cc3333"
C_GREEN  = "#3f7c55"
INK      = "#222233"

LANE_Y = {"VCC": 112, "GND": 130, "SCL": 148, "SDA": 166}   # bus corridors above boards
FAN_X  = {"GND": 560, "SDA": 595, "SCL": 620}               # verticals right of the C6

FONT_DIR = r"C:\Windows\Fonts"
fb = lambda s: ImageFont.truetype(FONT_DIR + r"\arialbd.ttf", s)
fr = lambda s: ImageFont.truetype(FONT_DIR + r"\arial.ttf", s)

# ---------------------------------------------------------------------------
def prep(board_key):
    d = COORDS[board_key]
    im = Image.open(d["src"]).crop(d["crop"])
    scale = TARGET_H / im.height
    im = im.resize((round(im.width * scale), round(TARGET_H)), Image.LANCZOS)
    return im, scale

def to_canvas(board_key, paste_key, xy):
    d = COORDS[board_key]
    px, py = PASTE[paste_key]
    s = TARGET_H / (d["crop"][3] - d["crop"][1])
    return (px + (xy[0] - d["crop"][0]) * s, py + (xy[1] - d["crop"][1]) * s)

def polyline(dr, pts, width, color):
    dr.line(pts, fill=color, width=width, joint="curve")
    r = width / 2.0
    for (x, y) in pts:
        dr.ellipse([x - r, y - r, x + r, y + r], fill=color)

def wire(dr, paths, color):
    for p in paths:
        polyline(dr, p, 14, "white")
    for p in paths:
        polyline(dr, p, 8, color)

def ring(dr, cx, cy, r, color, wu=9, wc=5):
    dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline="white", width=wu)
    dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=wc)

def ering(dr, cx, cy, rx, ry, color, wu=9, wc=5):
    dr.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline="white", width=wu)
    dr.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=color, width=wc)

def junction(dr, cx, cy, color):
    dr.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill="white")
    dr.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=color)

def label_box(dr, x, y, lines, border, font, pad=7, anchor="lt", gap=3):
    ws = [dr.textbbox((0, 0), t, font=font)[2] for t in lines]
    hs = [dr.textbbox((0, 0), t, font=font)[3] for t in lines]
    bw = max(ws) + 2 * pad
    bh = sum(hs) + gap * (len(lines) - 1) + 2 * pad
    if anchor == "rt":
        x -= bw
    if anchor == "ct":
        x -= bw / 2
    dr.rectangle([x, y, x + bw, y + bh], fill="white", outline=border, width=2)
    ty = y + pad
    for t, h, w in zip(lines, hs, ws):
        dr.text((x + (bw - w) / 2, ty), t, font=font, fill=INK)
        ty += h + gap
    return (x, y, x + bw, y + bh)

def red_x(dr, cx, cy, arm=13):
    for dx, dy in [(-arm, -arm), (-arm, arm)]:
        dr.line([cx + dx, cy + dy, cx - dx, cy - dy], fill="white", width=9)
    for dx, dy in [(-arm, -arm), (-arm, arm)]:
        dr.line([cx + dx, cy + dy, cx - dx, cy - dy], fill=C_RED, width=5)

# ---------------------------------------------------------------------------
img = Image.new("RGB", (CANVAS_W, CANVAS_H), "white")
dr = ImageDraw.Draw(img)

# Title block
dr.text((40, 28), "Doc 4a · The second hub, on the real boards", font=fb(40), fill="#111111")
dr.text((40, 76), "Four wires leave the C6 and land on both hubs identically — "
                  "the only physical difference is one blob of solder.", font=fr(22), fill="#555555")

# Photos
for key, pkey in [("c6", "c6"), ("pca", "hub1"), ("pca", "hub2")]:
    im, _ = prep(key)
    px, py = PASTE[pkey]
    img.paste(im, (px, py))
    dr.rectangle([px - 3, py - 3, px + im.width + 2, py + im.height + 2],
                 outline="#333344", width=3)

# Canvas positions of every pad we touch
c6 = {k: to_canvas("c6", "c6", v) for k, v in COORDS["c6"]["pins"].items()}
h1 = {k: to_canvas("pca", "hub1", v) for k, v in COORDS["pca"]["pads"].items()}
h2 = {k: to_canvas("pca", "hub2", v) for k, v in COORDS["pca"]["pads"].items()}
a0_1 = tuple((a + b) / 2 for a, b in zip(to_canvas("pca", "hub1", COORDS["pca"]["a0_left"]),
                                         to_canvas("pca", "hub1", COORDS["pca"]["a0_right"])))
a0_2 = tuple((a + b) / 2 for a, b in zip(to_canvas("pca", "hub2", COORDS["pca"]["a0_left"]),
                                         to_canvas("pca", "hub2", COORDS["pca"]["a0_right"])))

# ---------------------------------------------------------------------------
# Wires (draw order = bottom lane first so later wires cross over cleanly)
# Each wire: main path C6 pin -> fan -> corridor -> drop to hub2 pad,
# plus a tap segment corridor -> hub1 pad (junction dot at the landing).
# ---------------------------------------------------------------------------
def bus(name, color, pin, lane_y, fan_x=None, from_left=False):
    p1, p2 = h1[name if name != "3V3" else "VCC"], h2[name if name != "3V3" else "VCC"]
    if from_left:  # 3V3 leaves the C6's left column, rides over the top
        main = [pin, (20, pin[1]), (20, lane_y), (p2[0], lane_y), p2]
    else:
        main = [pin, (fan_x, pin[1]), (fan_x, lane_y), (p2[0], lane_y), p2]
    tap = [(p1[0], lane_y), p1]
    wire(dr, [main, tap], color)
    return p1, p2

sda1, sda2 = bus("SDA", C_BLUE,   c6["SDA"], LANE_Y["SDA"], FAN_X["SDA"])
scl1, scl2 = bus("SCL", C_TEAL,   c6["SCL"], LANE_Y["SCL"], FAN_X["SCL"])
gnd1, gnd2 = bus("GND", C_BLACK,  c6["GND"], LANE_Y["GND"], FAN_X["GND"])
vcc1, vcc2 = bus("3V3", C_PURPLE, c6["3V3"], LANE_Y["VCC"], from_left=True)

# Junction dots at hub1 landings; endpoint rings at hub2
for (p, col) in [(vcc1, C_PURPLE), (gnd1, C_BLACK), (sda1, C_BLUE), (scl1, C_TEAL)]:
    junction(dr, p[0], p[1], col)
for (p, col) in [(vcc2, C_PURPLE), (gnd2, C_BLACK), (sda2, C_BLUE), (scl2, C_TEAL)]:
    ring(dr, p[0], p[1], 13, col)

# C6 pin markers + labels
for name, col in [("3V3", C_PURPLE), ("GND", C_BLACK), ("SDA", C_BLUE), ("SCL", C_TEAL)]:
    ring(dr, c6[name][0], c6[name][1], 14, col, wu=8, wc=5)
label_box(dr, 84, c6["3V3"][1] + 15, ["3V3"], C_PURPLE, fb(20), anchor="rt")
label_box(dr, 445, c6["GND"][1] - 15, ["GND"], C_BLACK, fb(20), anchor="rt")
label_box(dr, 449, c6["SDA"][1] - 14, ["GPIO2 · SDA"], C_BLUE, fb(20), anchor="rt")
label_box(dr, 449, c6["SCL"][1] - 14, ["GPIO3 · SCL"], C_TEAL, fb(20), anchor="rt")

# V+ stays unconnected: red X on both hubs + one shared label in the gap
red_x(dr, h1["V+"][0], h1["V+"][1])
red_x(dr, h2["V+"][0], h2["V+"][1])
bx = label_box(dr, 1224, 222, ["V+ stays", "empty"], C_RED, fb(20), anchor="ct")
# tiny red x glyphs beside the box tying it to the two markers
for cx in (bx[0] - 14, bx[2] + 14):
    dr.line([cx - 6, bx[1] + 8, cx + 6, bx[1] + 20], fill=C_RED, width=4)
    dr.line([cx - 6, bx[1] + 20, cx + 6, bx[1] + 8], fill=C_RED, width=4)

# A0 address pads: open on hub1 (green), bridged on hub2 (red + drawn solder blob)
ering(dr, a0_1[0] + 6, a0_1[1], 30, 18, C_GREEN)
label_box(dr, 1110, a0_1[1] - 28, ["A0 OPEN", "→ 0x40"], C_GREEN, fb(20))
# solder blob bridging hub2's A0 pad pair
bx0, by0 = a0_2
dr.ellipse([bx0 - 17, by0 - 11, bx0 + 17, by0 + 11], fill="#a8a8b0", outline="#787882", width=2)
dr.ellipse([bx0 - 10, by0 - 7, bx0 + 2, by0 - 1], fill="#e6e6ec")
ering(dr, a0_2[0] + 6, a0_2[1], 30, 18, C_RED)
label_box(dr, 1740, a0_2[1] - 28, ["A0 BRIDGED", "→ 0x41"], C_RED, fb(20))

# Captions
caps = [("ESP32-C6 — the one master", 40 + 252),
        ("hub #1 · 0x40 · zones 1–5", 660 + 250),
        ("hub #2 · 0x41 · zones 6–7", 1290 + 250)]
for text, cx in caps:
    w = dr.textbbox((0, 0), text, font=fb(24))[2]
    dr.text((cx - w / 2, 1114), text, font=fb(24), fill=INK)

# Caution strip
dr.rectangle([40, 1166, CANVAS_W - 40, 1246], fill="#fffbe8", outline="#c9a227", width=3)
lead = "SAME FOUR WIRES, TAPPED TWICE — "
body = ("tell the boards apart by the blob, never by the wiring. "
        "Bridge A0 with everything unpowered, BEFORE hub #2\u2019s bus wires land.")
lw = dr.textbbox((0, 0), lead, font=fb(19))[2]
dr.text((64, 1195), lead, font=fb(19), fill="#6b5200")
dr.text((64 + lw, 1195), body, font=fr(19), fill="#6b5200")

OUT = r"C:\Users\Marcelo\AppData\Local\Temp\claude\C--Claude-gimbal-bench\bc442eb3-8a91-49f8-a2b1-fd632e9c7a40\scratchpad\anno\two-hubs.jpg"
img.save(OUT, quality=87)
print("saved", OUT, img.size)
for n in ("3V3", "GND", "SDA", "SCL"):
    print("c6", n, tuple(round(v) for v in c6[n]))
for n in ("V+", "VCC", "SDA", "SCL", "GND"):
    print("h1", n, tuple(round(v) for v in h1[n]), "h2", n, tuple(round(v) for v in h2[n]))
print("a0", tuple(round(v) for v in a0_1), tuple(round(v) for v in a0_2))
