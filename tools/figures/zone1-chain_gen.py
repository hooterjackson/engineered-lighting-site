# -*- coding: utf-8 -*-
"""
zone1-chain: one LED zone's complete signal path across the three real parts.
Panels L->R: PCA9685 channel block (ch 0-2) | ULN2803A | Valent X tape pads.

Orientation verification (done by crop-zooming the silkscreen before writing this):
- IMG_2452 (PCA9685): board photographed with control header at TOP; channel block
  runs down the left side, channel 0 topmost (nearest control header). Columns from
  board edge inward: GND (x~620), V+ (x~730), PWM (x~837). Numerals 0,1,2,3 at x~900-925.
  No rotation needed.
- IMG_2456 (ULN2803A): printing already upright ("ULN2803A / 99AQ6 V6 / MYS 99 350"),
  notch (semicircular recess) verified at the LEFT end center (~x340, y1700).
  Bottom row L->R = pins 1..9 (IN1..IN8, 9=GND), top row L->R = pins 18..10.
  No rotation needed.
- IMG_2450 (tape): cut line at top, half-moon pads L->R = 24V+, W, N, C
  (silkscreen letters below each pad). No rotation needed.
"""
from PIL import Image, ImageDraw, ImageFont

BASE = r"C:\Users\Marcelo\AppData\Local\Temp\claude\C--Claude-gimbal-bench\bc442eb3-8a91-49f8-a2b1-fd632e9c7a40\scratchpad\anno"
OUT = BASE + r"\zone1-chain.jpg"

# ---------------------------------------------------------------- COORDS (ORIGINAL pixels)
COORDS = {
    "pca": {
        "file": r"C:\Claude\PrototypeImages\IMG_2452.jpg",
        "crop": (520, 290, 970, 790),           # channel block, ch0..ch3
        "pwm_ch0": (832, 413),                  # PWM column = interior (rightmost) column
        "pwm_ch1": (833, 517),                  # (gold-annulus centroids, computed)
        "pwm_ch2": (835, 621),
    },
    "uln": {
        "file": r"C:\Claude\PrototypeImages\IMG_2456.jpg",
        "crop": (260, 1390, 1740, 2010),        # whole DIP-18, notch left, printing upright
        "in1": (417, 1930),                     # bottom row pin 1  (leftmost)
        "in2": (563, 1932),                     # bottom row pin 2
        "in3": (710, 1934),                     # bottom row pin 3
        "out1_p18": (417, 1485),                # top row leftmost = pin 18 = OUT1
        "out2_p17": (563, 1485),                # pin 17 = OUT2
        "out3_p16": (710, 1485),                # pin 16 = OUT3
        "gnd_p9": (1597, 1928),                 # bottom row rightmost = pin 9 = GND
    },
    "tape": {
        "file": r"C:\Claude\PrototypeImages\IMG_2450.jpg",
        "crop": (420, 600, 1760, 1350),         # pad row + silkscreen 24V+/W/N/C
        "pad_24v": (548, 755),
        "pad_w": (752, 760),
        "pad_n": (1385, 750),
        "pad_c": (1608, 755),
    },
}

# ---------------------------------------------------------------- layout (canvas)
W, H = 1860, 935
PANEL = {  # name: (paste_x, paste_y, scale)
    "pca":  (60, 170, 1.12),
    "uln":  (700, 400, 0.37838),
    "tape": (1360, 430, 0.35),
}

def cv(part, key):
    """original-pixel coord -> canvas coord"""
    px, py, s = PANEL[part][:3]
    x0, y0, _, _ = COORDS[part]["crop"]
    ox, oy = COORDS[part][key]
    return (round(px + (ox - x0) * s), round(py + (oy - y0) * s))

AMBER, GREY, BLUE = "#c47a00", "#7a7a7a", "#2e86c1"
RED, BLACK = "#d62828", "#222222"
INK = "#222233"

F = lambda name, size: ImageFont.truetype(r"C:\Windows\Fonts\%s" % name, size)
f_title, f_sub = F("arialbd.ttf", 40), F("arial.ttf", 22)
f_cap, f_lab = F("arialbd.ttf", 24), F("arialbd.ttf", 20)
f_note = F("arial.ttf", 21)

img = Image.new("RGB", (W, H), "#ffffff")
d = ImageDraw.Draw(img)

# ---------------------------------------------------------------- panels
for name in ("pca", "uln", "tape"):
    c = COORDS[name]
    px, py, s = PANEL[name]
    im = Image.open(c["file"]).convert("RGB").crop(c["crop"])
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    img.paste(im, (px, py))
    d.rectangle([px - 2, py - 2, px + im.width + 1, py + im.height + 1],
                outline="#333344", width=3)
    PANEL[name] = (px, py, s, im.width, im.height)  # keep size

def wire(pts, color):
    d.line(pts, fill="#ffffff", width=14, joint="curve")
    for p in (pts[0], pts[-1]):
        d.ellipse([p[0]-7, p[1]-7, p[0]+7, p[1]+7], fill="#ffffff")
    d.line(pts, fill=color, width=8, joint="curve")
    for p in (pts[0], pts[-1]):
        d.ellipse([p[0]-4, p[1]-4, p[0]+4, p[1]+4], fill=color)

def ring(p, color, r=22):
    x, y = p
    d.ellipse([x-r, y-r, x+r, y+r], outline="#ffffff", width=9)
    d.ellipse([x-r, y-r, x+r, y+r], outline=color, width=5)

def tag(center, text, color, font=f_lab):
    x, y = center
    bb = d.textbbox((0, 0), text, font=font)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    hw, hh = tw//2 + 7, th//2 + 6
    d.rectangle([x-hw, y-hh, x+hw, y+hh], fill="#ffffff", outline=color, width=2)
    d.text((x - tw//2 - bb[0], y - th//2 - bb[1]), text, font=font, fill=INK)

# ---------------------------------------------------------------- wires
p_ch0, p_ch1, p_ch2 = cv("pca","pwm_ch0"), cv("pca","pwm_ch1"), cv("pca","pwm_ch2")
p_in1, p_in2, p_in3 = cv("uln","in1"), cv("uln","in2"), cv("uln","in3")
p_o1, p_o2, p_o3 = cv("uln","out1_p18"), cv("uln","out2_p17"), cv("uln","out3_p16")
p_g9 = cv("uln","gnd_p9")
t_24, t_w, t_n, t_c = cv("tape","pad_24v"), cv("tape","pad_w"), cv("tape","pad_n"), cv("tape","pad_c")

# hub PWM -> ULN inputs (nested, no crossings; enter bottom pins from below).
# Each wire jogs down right after its hole so the horizontal run passes BETWEEN
# the channel numerals (silkscreen bands canvas-y ~291-329, 400-450, 504-556, 627-680).
wire([p_ch0, (464, p_ch0[1]), (464, 368), (655, 368), (655, 670), (p_in1[0], 670), p_in1], AMBER)
wire([p_ch1, (464, p_ch1[1]), (464, 490), (625, 490), (625, 695), (p_in2[0], 695), p_in2], GREY)
wire([p_ch2, (464, p_ch2[1]), (464, 600), (595, 600), (595, 720), (p_in3[0], 720), p_in3], BLUE)

# ULN outputs (top-left pins) over the chip to the tape pads
wire([p_o1, (p_o1[0], 370), (t_w[0], 370), t_w], AMBER)
wire([p_o2, (p_o2[0], 335), (t_n[0], 335), t_n], GREY)
wire([p_o3, (p_o3[0], 300), (t_c[0], 300), t_c], BLUE)

# +24 V bus -> tape 24V+ (through the inter-panel gap; touches neither chip panel)
bus_box = (1180, 720, 1440, 776)
wire([(1310, 720), (1310, 410), (t_24[0], 410), t_24], RED)
d.rectangle(bus_box, fill="#ffffff", outline=RED, width=2)
bt = "+24 V BUS (WAGO)"
bb = d.textbbox((0, 0), bt, font=f_lab)
d.text(((bus_box[0]+bus_box[2])//2 - (bb[2]-bb[0])//2,
        (bus_box[1]+bus_box[3])//2 - (bb[3]-bb[1])//2 - bb[1]), bt, font=f_lab, fill=INK)

# GND stub from ULN pin 9
wire([p_g9, (p_g9[0], 648)], BLACK)
tag((p_g9[0], 668), "GND STAR", BLACK)

# ---------------------------------------------------------------- rings
for p, col in [(p_ch0, AMBER), (p_ch1, GREY), (p_ch2, BLUE),
               (p_in1, AMBER), (p_in2, GREY), (p_in3, BLUE),
               (p_o1, AMBER), (p_o2, GREY), (p_o3, BLUE),
               (p_g9, BLACK),
               (t_24, RED), (t_w, AMBER), (t_n, GREY), (t_c, BLUE)]:
    ring(p, col)

# ---------------------------------------------------------------- labels
# row-aligned tags in the panel's left margin (PWM-hole x-zone is full of silkscreen)
tag((94, p_ch0[1]), "ch 0", AMBER)
tag((94, p_ch1[1]), "ch 1", GREY)
tag((94, p_ch2[1]), "ch 2", BLUE)
tag((p_in1[0], 652), "IN1", AMBER)
tag((p_in2[0]+8, 672), "IN2", GREY)
tag((p_in3[0]+16, 692), "IN3", BLUE)
tag((1010, 370), "OUT1 \u00b7 p18", AMBER)
tag((1150, 335), "OUT2 \u00b7 p17", GREY)
tag((1290, 300), "OUT3 \u00b7 p16", BLUE)
tag((1368, 410), "24V+", RED)
tag((t_w[0], 404), "W \u2212", AMBER)
tag((t_n[0], 404), "N \u2212", GREY)
tag((t_c[0], 404), "C \u2212", BLUE)

# ---------------------------------------------------------------- captions
def caption(part, text, cx=None, ty=None):
    px, py, s, w, h = PANEL[part]
    bb = d.textbbox((0, 0), text, font=f_cap)
    cx = px + w//2 if cx is None else cx
    ty = py + h + 10 if ty is None else ty
    d.text((cx - (bb[2]-bb[0])//2, ty), text, font=f_cap, fill=INK)
caption("pca", "hub #1 \u00b7 channels 0\u00b71\u00b72")
caption("uln", "ULN2803A \u00b7 chip 1", cx=1010, ty=712)   # dodge IN3 tag + GND STAR label
caption("tape", "Valent X tape \u00b7 zone 1")

# ---------------------------------------------------------------- title
d.text((40, 28), "Doc 4a \u00b7 One zone\u2019s whole trip, pad to pad", font=f_title, fill="#111111")
d.text((40, 84), "Zone 1 across the real parts \u2014 three 3.3 V signals in, three switched returns out, "
                 "and +24 V that touches neither chip.", font=f_sub, fill="#555555")

# ---------------------------------------------------------------- note strips
def strip(y0, y1, bg, border, ink, text):
    d.rectangle([40, y0, 1820, y1], fill=bg, outline=border, width=2)
    bb = d.textbbox((0, 0), text, font=f_note)
    d.text((60, (y0+y1)//2 - (bb[3]-bb[1])//2 - bb[1]), text, font=f_note, fill=ink)
strip(795, 845, "#fbfbf7", "#888888", "#444444",
      "One color = one white, the whole way: amber = warm 1800 K \u00b7 grey = neutral 3500 K \u00b7 "
      "blue = cool 6500 K \u2014 always in W / N / C order.")
strip(857, 907, "#fdecec", "#cc3333", "#8a1c1c",
      "+24 V NEVER ENTERS A HUB OR THE ULN\u2019S INPUT SIDE \u2014 it runs bus \u2192 tape, "
      "and only the three negatives are switched (through the ULN, pin 9, to the star).")

img.save(OUT, quality=87)
print("saved", OUT, img.size)
for part in ("pca", "uln", "tape"):
    for k in COORDS[part]:
        if k not in ("file", "crop"):
            print(part, k, cv(part, k))
