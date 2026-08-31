# -*- coding: utf-8 -*-
"""frame-orientations: the full print plate annotated so a builder slices
every part in its ONE correct pose. Source render: parts-all.png (1300x1100).
All COORDS are in SOURCE pixels of parts-all.png; the canvas math converts."""

from PIL import Image, ImageDraw, ImageFont

SRC = r"C:\Claude\engineered-lighting-site\docs\cad\renders\parts-all.png"
OUT = r"C:\Users\Marcelo\AppData\Local\Temp\claude\C--Claude-gimbal-bench\bc442eb3-8a91-49f8-a2b1-fd632e9c7a40\scratchpad\anno\frame-orientations.jpg"

# ---------------------------------------------------------------- fonts
F = r"C:\Windows\Fonts"
f_title = ImageFont.truetype(F + r"\arialbd.ttf", 40)
f_sub   = ImageFont.truetype(F + r"\arial.ttf", 22)
f_badge = ImageFont.truetype(F + r"\arialbd.ttf", 20)
f_name  = ImageFont.truetype(F + r"\arialbd.ttf", 21)
f_rule  = ImageFont.truetype(F + r"\arial.ttf", 17)
f_strip = ImageFont.truetype(F + r"\arial.ttf", 20)
f_cap   = ImageFont.truetype(F + r"\arial.ttf", 18)

# ---------------------------------------------------------------- geometry
# Source render is pasted 1:1; vertical crop trims dead whitespace.
CROP_TOP = 150          # source rows 0..150 are empty
OFF_X, OFF_Y = 150, 190 # paste offset of the (cropped) render on the canvas
def cx(x): return x + OFF_X
def cy(y): return y - CROP_TOP + OFF_Y

W, H = 1600, 1140
INK    = "#111111"
GREY   = "#555555"
LINE   = "#333344"
WHITE  = "#ffffff"

# COORDS: identified part features in SOURCE pixels of parts-all.png
# (verified against the part-*.png identity renders by crop-zoom)
COORDS = {
    "bore_gauge_half1":  (323, 317),   # left small block, orange half-pipe valley
    "bore_gauge_half2":  (520, 317),   # right small block, same valley
    "cradle_cap":        (702, 300),   # rect block, valley center, 2+2 clean holes
    "tol_coupon":        (300, 456),   # wide plate, row of 7 gauge holes (pins on top)
    "fit_coupon_tile1":  (672, 440),   # square tile, SMALL center bore
    "fit_coupon_tile2":  (860, 440),   # square tile, LARGE center bore
    "yoke_arm":          (320, 745),   # dark vertical arm standing 59.6 mm tall
    "yoke_disc":         (412, 760),   # bridge/disc flat on the bed
    "base_plate_post":   (812, 783),   # hard-stop post seen end-on (pointing UP)
    "base_plate_body":   (700, 650),   # windowed plate body, big face on the bed
    "cradle":            (1010, 820),  # back-plate + hourglass bore valley
}

im = Image.new("RGB", (W, H), WHITE)
d = ImageDraw.Draw(im)

# ---------------------------------------------------------------- render
src = Image.open(SRC).convert("RGB").crop((0, CROP_TOP, 1300, 940))
im.paste(src, (OFF_X, OFF_Y))
d = ImageDraw.Draw(im)

# ---------------------------------------------------------------- header
d.text((40, 28), "Doc 3b · The print plate — every part in its one pose",
       font=f_title, fill=INK)
d.text((40, 84),
       "The export already lays each part the way it must print. "
       "Slice it as it lands — re-orienting a part is how bridges appear.",
       font=f_sub, fill=GREY)

# amber badge
btxt = ("ORIENTATION: YES — every part has ONE pose · "
        "bores print as valleys · zero supports")
bw = d.textbbox((0, 0), btxt, font=f_badge)[2]
bx0, by0 = 40, 126
bx1, by1 = bx0 + bw + 28, by0 + 40
d.rounded_rectangle([bx0, by0, bx1, by1], radius=9,
                    fill="#fffbe8", outline="#c9a227", width=2)
d.text((bx0 + 14, by0 + 9), btxt, font=f_badge, fill="#6b5200")

# ---------------------------------------------------------------- labels
def label(box_xy, name, rules, targets, border=LINE):
    """White label box + leader line(s). box_xy in canvas px, targets in source px."""
    x, y = box_xy
    pad = 10
    wids = [d.textbbox((0, 0), name, font=f_name)[2]] + \
           [d.textbbox((0, 0), r, font=f_rule)[2] for r in rules]
    bw_ = max(wids) + 2 * pad
    bh_ = pad * 2 + 26 + len(rules) * 22
    rect = (x, y, x + bw_, y + bh_)
    for tx, ty in targets:
        tcx, tcy = cx(tx), cy(ty)
        # leader starts at middle of the box side facing the target
        sx = rect[0] if tcx < rect[0] else (rect[2] if tcx > rect[2] else (rect[0] + rect[2]) // 2)
        sy = rect[1] if tcy < rect[1] else (rect[3] if tcy > rect[3] else (rect[1] + rect[3]) // 2)
        d.line([sx, sy, tcx, tcy], fill=LINE, width=3)
        d.ellipse([tcx - 5, tcy - 5, tcx + 5, tcy + 5], fill=LINE)
    d.rectangle(rect, fill=WHITE, outline=border, width=2)
    d.text((x + pad, y + pad - 1), name, font=f_name, fill=INK)
    for i, r in enumerate(rules):
        d.text((x + pad, y + pad + 25 + i * 22), r, font=f_rule, fill="#444444")

# bore_gauge — both halves, flat as emitted
label((166, 216), "bore_gauge — both halves flat",
      ["as emitted, valleys facing up"],
      [COORDS["bore_gauge_half1"], COORDS["bore_gauge_half2"]])

# cradle_cap — crown DOWN
label((1090, 250), "cradle_cap — crown DOWN",
      ["bore prints as a valley, holes clear"],
      [COORDS["cradle_cap"]])

# tol_coupon — the red-border one (box sits LEFT of the plate, no overlap)
label((44, 438), "tol_coupon — PRINT ME FIRST",
      ["it calibrates three numbers", "in frame_params.scad"],
      [COORDS["tol_coupon"]], border="#cc3333")

# fit_coupon — two tiles on purpose
label((1180, 420), "fit_coupon — two tiles on purpose",
      ["concentric circles would merge"],
      [COORDS["fit_coupon_tile2"]])

# yoke — tallest part
label((166, 660), "yoke — bridge on the bed",
      ["arm points UP — 59.6 mm,", "tallest part on the plate"],
      [COORDS["yoke_arm"]])

# base_plate — flipped
label((1090, 600), "base_plate — flipped",
      ["hard-stop post UP,", "big face on the bed"],
      [COORDS["base_plate_post"]])

# cradle — as emitted
label((1288, 800), "cradle — as emitted",
      ["bore prints as a valley"],
      [COORDS["cradle"]])

# ---------------------------------------------------------------- strip + caption
sy0, sy1 = 1000, 1058
d.rectangle([40, sy0, W - 40, sy1], fill="#f2f2f5", outline="#cccccc", width=2)
stxt = ("One job, 207.5 \u00d7 169.7 mm — fits a 256 mm bed. PETG, walls/infill "
        "per the chapter\u2019s table; the yoke takes PETG-CF if on hand.")
sw = d.textbbox((0, 0), stxt, font=f_strip)[2]
d.text(((W - sw) // 2, sy0 + 17), stxt, font=f_strip, fill="#333333")

d.text((40, 1080), "frame v8 · the whole set, print-posed", font=f_cap, fill="#777777")

# ---------------------------------------------------------------- border + save
d.rectangle([0, 0, W - 1, H - 1], outline=LINE, width=3)
im.save(OUT, "JPEG", quality=90)
print("saved", OUT, im.size)
