# spot-driver_gen.py — figure 'spot-driver' for the hardware doc site (photo-anno family style)
# Source: C:\Claude\PrototypeImages\IMG_2453.jpg (2160x2880), rotated 180 deg before annotating
# so the input-edge silkscreen ("IN3 IN2", "IN1 GND", "- VIN +") reads upright.
# NOTE: the board's own print is mixed — OUT labels / AL8860 / 330 markings are printed 180 deg
# relative to the input-edge labels, so they read inverted in this frame; the +/- glyphs are
# rotation-safe and every pad assignment below was read from zoom-crops of the print itself.
#
# COORDS are POST-ROTATION pixels in the full 2160x2880 rotated frame (rot = src.rotate(180)).
# Verified by zoom-cropping the rotated image with coordinate grids.
from PIL import Image, ImageDraw, ImageFont

SRC = r"C:\Claude\PrototypeImages\IMG_2453.jpg"
OUT = r"C:\Users\Marcelo\AppData\Local\Temp\claude\C--Claude-gimbal-bench\bc442eb3-8a91-49f8-a2b1-fd632e9c7a40\scratchpad\anno\spot-driver.jpg"

# ---------------- ground-truth coordinates (post-rotation pixels) ----------------
COORDS = {
    # input edge (bottom of rotated frame) — silk reads upright: "IN3 IN2" "IN1 GND" "- VIN +"
    "IN3":   (715, 1890),   # left pad of "IN3 IN2" group ("IN3" printed over it)
    "IN2":   (827, 1883),   # right pad of "IN3 IN2" group
    "IN1":   (1033, 1876),  # left pad of "IN1 GND" group
    "GND":   (1143, 1870),  # right pad of "IN1 GND" group
    "VIN-":  (1425, 1882),  # square pad under the printed "-" of "- VIN +"
    "VIN+":  (1590, 1878),  # round pad under the printed "+", beside the mounting tab
    # output edge (top of rotated frame), pairs left->right are OUT3, OUT2, OUT1;
    # print reads "+ OUT_n -" with "+" over the square pad, "-" over the round pad
    "OUT3-": (652, 902),    # round pad
    "OUT3+": (816, 899),    # square pad
    "OUT2-": (1027, 879),
    "OUT2+": (1183, 881),
    "OUT1-": (1377, 878),
    "OUT1+": (1541, 866),
    # explainer components (channel 1 column, nearest VIN)
    "AL8860": (1462, 1470),  # SOT-25 marked "A5 2f T / AL8860"
    "IND330": (1445, 1214),  # power inductor marked "330" (33 uH)
    "R300":   (1452, 1627),  # center of the ch1 sense PAIR - two R300s side by side
}

# ---------------- style ----------------
RED    = "#d62828"
BLACK  = "#222222"
BLUE_IN = "#1d6fd6"
AMBER  = "#c47a00"
GREY   = "#7a7a7a"
BLUE_OUT = "#2e86c1"
GREEN  = "#3f7c55"
INK    = "#222233"
CAUT_B = "#c9a227"
CAUT_T = "#6b5200"
DANGER = "#cc3333"
BORDER = "#333344"

F_TITLE = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 40)
F_SUB   = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 22)
F_LAB   = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 21)
F_CAUT  = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 20)
F_CAP   = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 24)

# photo crop (post-rotation frame) and placement
CROP = (290, 680, 1925, 2070)          # tight to board + ~40 px margin
PX, PY = 40, 215                        # photo top-left on canvas
CW = 40 + (CROP[2] - CROP[0]) + 40      # 1715
CH = 1876

def cvs(p):   # rotated-frame pixel -> canvas pixel
    return (p[0] - CROP[0] + PX, p[1] - CROP[1] + PY)

def ring(d, center, r, color, ry=None):
    cx, cy = cvs(center)
    ry = ry if ry is not None else r
    d.ellipse([cx - r - 2, cy - ry - 2, cx + r + 2, cy + ry + 2], outline="white", width=9)
    d.ellipse([cx - r, cy - ry, cx + r, cy + ry], outline=color, width=5)

def leader(d, pts, color):
    d.line(pts, fill="white", width=7, joint="curve")
    d.line(pts, fill=color, width=3, joint="curve")

def label_box(d, cx_or_x, y, lines, color, font=F_LAB, text_color=INK, anchor="center", bw=2, pad=(11, 7)):
    widths = [d.textbbox((0, 0), t, font=font)[2] for t in lines]
    lh = font.size + 7
    w = max(widths) + 2 * pad[0]
    h = len(lines) * lh + 2 * pad[1] - 3
    x = cx_or_x - w // 2 if anchor == "center" else cx_or_x
    d.rectangle([x, y, x + w, y + h], fill="white", outline=color, width=bw)
    ty = y + pad[1] - 1
    for t, tw in zip(lines, widths):
        d.text((x + (w - tw) // 2, ty), t, font=font, fill=text_color)
        ty += lh
    return (x, y, x + w, y + h)

img = Image.new("RGB", (CW, CH), "white")
d = ImageDraw.Draw(img)

# ---- photo ----
rot = Image.open(SRC).rotate(180)
photo = rot.crop(CROP)
img.paste(photo, (PX, PY))
d.rectangle([PX - 3, PY - 3, PX + photo.width + 2, PY + photo.height + 2],
            outline=BORDER, width=3)

# ---- title / subtitle ----
d.text((40, 28), "Doc 4b \u00b7 The three-channel driver \u2014 every block named",
       font=F_TITLE, fill="#111111")
d.text((40, 84), "One constant-current buck per channel. Twin R300 sense resistors set ~660 mA \u2014 "
       "dim by pulsing the INs, never by the rail.", font=F_SUB, fill="#555555")

# ---- rings ----
ring(d, COORDS["VIN+"], 46, RED)
ring(d, COORDS["VIN-"], 40, BLACK)
for k in ("IN1", "IN2", "IN3"):
    ring(d, COORDS[k], 40, BLUE_IN)
ring(d, COORDS["GND"], 36, BLACK)
ring(d, COORDS["OUT3-"], 42, BLUE_OUT); ring(d, COORDS["OUT3+"], 40, BLUE_OUT)
ring(d, COORDS["OUT2-"], 42, GREY);     ring(d, COORDS["OUT2+"], 40, GREY)
ring(d, COORDS["OUT1-"], 42, AMBER);    ring(d, COORDS["OUT1+"], 40, AMBER)
ring(d, COORDS["AL8860"], 72, GREEN)
ring(d, COORDS["IND330"], 147, GREEN)
ring(d, COORDS["R300"], 80, GREEN, ry=52)

# ---- polarity glyphs at the OUT rings (per the print: + = square pad, - = round pad) ----
F_PM = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 40)
for kp in ("OUT3+", "OUT2+", "OUT1+"):
    x, y = cvs(COORDS[kp])
    d.text((x, y + 66), "+", font=F_PM, fill="#222233", anchor="mm", stroke_width=5, stroke_fill="#ffffff")
for kn in ("OUT3-", "OUT2-", "OUT1-"):
    x, y = cvs(COORDS[kn])
    d.text((x, y + 66), "−", font=F_PM, fill="#222233", anchor="mm", stroke_width=5, stroke_fill="#ffffff")

# ---- output-edge labels (band above photo), leaders down to both rings of each pair ----
out_groups = [
    ("OUT3 \u00b1 \u2192 one die", BLUE_OUT, "OUT3-", "OUT3+", 42, 40),
    ("OUT2 \u00b1 \u2192 one die", GREY,     "OUT2-", "OUT2+", 42, 40),
    ("OUT1 \u00b1 \u2192 one die", AMBER,    "OUT1-", "OUT1+", 42, 40),
]
for text, color, kn, kp, rn, rp in out_groups:
    n, p = cvs(COORDS[kn]), cvs(COORDS[kp])
    cx = (n[0] + p[0]) // 2
    leader(d, [(cx - 28, 172), (n[0], n[1] - rn - 8)], color)
    leader(d, [(cx + 28, 172), (p[0], p[1] - rp - 8)], color)
    label_box(d, cx, 130, [text], color)

# ---- shared danger note (right of the output side, on the cardboard) ----
label_box(d, 1382, 470, ["six conductors \u2014 returns", "NEVER share a wire"],
          DANGER, anchor="left", bw=3)

# ---- explainer-component labels (right cardboard column, leaders left) ----
b = label_box(d, 1390, 686, ["330 = 33 \u00b5H"], GREEN, anchor="left")
leader(d, [(b[0] - 2, (b[1] + b[3]) // 2), (cvs(COORDS["IND330"])[0] + 128, cvs(COORDS["IND330"])[1] - 66)], GREEN)

b = label_box(d, 1390, 925, ["AL8860 \u2014 one CC", "buck per channel"], GREEN, anchor="left")
leader(d, [(b[0] - 2, (b[1] + b[3]) // 2), (cvs(COORDS["AL8860"])[0] + 66, cvs(COORDS["AL8860"])[1] - 28)], GREEN)

b = label_box(d, 1390, 1098, ["2\u00d7 R300 in parallel = 0.15 \u03a9", "\u2192 ~660 mA, fixed"], GREEN, anchor="left")
leader(d, [(b[0] - 2, (b[1] + b[3]) // 2), (cvs(COORDS["R300"])[0] + 66, cvs(COORDS["R300"])[1] - 34)], GREEN)

# ---- input-edge labels (band below photo), leaders up to rings ----
def up_label(d, key, text, color, row_y, r):
    c = cvs(COORDS[key])
    leader(d, [(c[0], row_y + 4), (c[0], c[1] + r + 8)], color)
    label_box(d, c[0], row_y, [text], color)

# row A
up_label(d, "IN3",  "IN3 \u2190 GPIO18", BLUE_IN, 1630, 40)
up_label(d, "IN1",  "IN1 \u2190 GPIO10", BLUE_IN, 1630, 40)
up_label(d, "VIN-", "VIN \u2212 \u2014 to the ground star", BLACK, 1630, 40)
# row B
up_label(d, "IN2",  "IN2 \u2190 GPIO11", BLUE_IN, 1692, 40)
up_label(d, "GND",  "GND \u2014 beeps to VIN\u2212 (S3)", BLACK, 1692, 36)
up_label(d, "VIN+", "VIN + \u2014 fused +24 V bus", RED, 1692, 46)

# ---- caution tag near the IN block ----
label_box(d, 700, 1754, ["inputs float ON \u2014 10 k\u03a9 pulldown on each (S5)"],
          CAUT_B, font=F_CAUT, text_color=CAUT_T, bw=3)

# ---- caption under the photo ----
cap = "this build\u2019s driver \u00b7 AL8860 \u00d73 \u00b7 twin R300s → ~660 mA per channel"
w = d.textbbox((0, 0), cap, font=F_CAP)[2]
d.text(((CW - w) // 2, 1822), cap, font=F_CAP, fill=INK)

img.save(OUT, quality=87)
print("saved", OUT, img.size)
