# -*- coding: utf-8 -*-
"""frame-exploded: annotated exploded CAD render of the gimbal frame (Doc 3b).

House photo-anno style. Coordinates in COORDS are SOURCE pixels of
exploded.png (1200x950), verified by crop-zoom against the part reference
renders (part-base_plate / part-yoke / part-cradle / part-cradle_cap /
assembly.png).
"""
from PIL import Image, ImageDraw, ImageFont

SRC = r"C:\Claude\engineered-lighting-site\docs\cad\renders\exploded.png"
OUT = r"C:\Users\Marcelo\AppData\Local\Temp\claude\C--Claude-gimbal-bench\bc442eb3-8a91-49f8-a2b1-fd632e9c7a40\scratchpad\anno\frame-exploded.jpg"

# ---------------------------------------------------------------- geometry --
W, H = 1600, 1300          # canvas
OX, OY = 200, 175          # render paste offset (source px + (OX,OY) = canvas)

# Every labeled feature, in SOURCE pixels of exploded.png (1200x950).
COORDS = {
    # printed parts
    "base_plate_surface": (530, 230),   # gold plate top face, left of trough
    "base_plate_trough":  (575, 230),   # cable trough slot in the plate
    "yoke_disc":          (555, 585),   # orange bridge disc, left edge
    "yoke_arm":           (540, 655),   # the ONE arm, same piece
    "cradle_body":        (860, 745),   # lower teal saddle bracket
    "cradle_rear_plate":  (715, 710),   # face that bolts to tilt OUTPUT
    "cradle_cap_body":    (862, 555),   # upper teal clamp half
    # motors + housing
    "pan_motor_body":     (562, 430),   # grey puck under the base plate
    "pan_motor_rear":     (612, 383),   # its rear face (up) - connector clocking
    "tilt_motor_body":    (615, 720),   # grey puck at the yoke arm
    "housing_barrel":     (815, 658),   # plain cylinder, no bolt circle
    # screws
    "pan_rear_screws":    (652, 157),   # 4x M2.5x16 above the plate
    "yoke_bridge_screw":  (600, 572),   # M3x10 at the bridge (into pan OUTPUT)
    "tilt_rear_screws":   (380, 610),   # 4x M2.5x16 pointing into the arm
    "cap_screws":         (852, 478),   # 4x M3x25 above the cradle_cap
}

def cv(name):
    x, y = COORDS[name]
    return (x + OX, y + OY)

# ------------------------------------------------------------------- fonts --
FD = r"C:\Windows\Fonts"
f_title = ImageFont.truetype(FD + r"\arialbd.ttf", 40)
f_sub   = ImageFont.truetype(FD + r"\arial.ttf", 22)
f_badge = ImageFont.truetype(FD + r"\arialbd.ttf", 20)
f_label = ImageFont.truetype(FD + r"\arialbd.ttf", 21)
f_lsub  = ImageFont.truetype(FD + r"\arial.ttf", 14)
f_tag   = ImageFont.truetype(FD + r"\arialbd.ttf", 18)
f_tsub  = ImageFont.truetype(FD + r"\arial.ttf", 14)
f_caut  = ImageFont.truetype(FD + r"\arialbd.ttf", 17)
f_caut2 = ImageFont.truetype(FD + r"\arial.ttf", 15)
f_capt  = ImageFont.truetype(FD + r"\arialbd.ttf", 24)
f_note  = ImageFont.truetype(FD + r"\arial.ttf", 18)

INK   = "#333344"
DARK  = "#222233"
BLUE  = dict(border="#1d6fd6", fill="#eef4fd", text="#123c6e")
RED   = dict(border="#cc3333", fill="#fdecec", text="#8a1c1c")
GREEN = dict(border="#3f7c55", fill="#eef6ef", text="#2a5539")
CAUT  = dict(border="#c9a227", fill="#fdf6dd", text="#6b5200")

# ------------------------------------------------------------------ canvas --
img = Image.new("RGB", (W, H), "#ffffff")
d = ImageDraw.Draw(img)

d.text((40, 28), "Doc 3b \u00b7 The frame, exploded \u2014 every part, every screw",
       font=f_title, fill="#111111")
d.text((40, 82), "Four printed parts, two motors, one housing \u2014 and one law about screw length.",
       font=f_sub, fill="#555555")

badge = "SCREWS: M3\u00d710 into ANY motor output \u2014 longer bottoms out INSIDE the motor"
bw = d.textlength(badge, font=f_badge)
d.rounded_rectangle((40, 110, 40 + bw + 28, 154), radius=9,
                    fill=RED["fill"], outline=RED["border"], width=2)
d.text((54, 120), badge, font=f_badge, fill=RED["text"])

# render + 3px border
src = Image.open(SRC).convert("RGB")
img.paste(src, (OX, OY))
d.rectangle((OX - 3, OY - 3, OX + 1200 + 2, OY + 950 + 2), outline=INK, width=3)

# ------------------------------------------------------------ annotations --
# Each entry: lines [(text, font)], top-left, style, target (canvas), leader color
def box_of(lines, xy, pad=(12, 8), gap=3):
    x, y = xy
    w = max(d.textlength(t, font=f) for t, f in lines)
    h = sum((f.size + gap) for t, f in lines) - gap
    return (x, y, x + w + 2 * pad[0], y + h + 2 * pad[1])

def clamp_start(rect, target):
    x0, y0, x1, y1 = rect
    tx, ty = target
    return (min(max(tx, x0), x1), min(max(ty, y0), y1))

white_labels = [
    ([("base_plate", f_label)],                              (270, 240), cv("base_plate_surface")),
    ([("pan motor", f_label), ("RMD-L-5005", f_lsub)],       (255, 508), cv("pan_motor_body")),
    ([("yoke", f_label)],                                    (240, 670), cv("yoke_disc")),
    ([("tilt motor", f_label), ("RMD-L-5005", f_lsub)],      (420, 1035), cv("tilt_motor_body")),
    ([("housing barrel", f_label)],                          (1180, 770), cv("housing_barrel")),
    ([("cradle_cap", f_label)],                              (1170, 540), cv("cradle_cap_body")),
    ([("cradle", f_label)],                                  (1180, 950), cv("cradle_body")),
]

tags = [
    ([("4\u00d7 M2.5\u00d716", f_tag),
      ("through base_plate \u2192 pan motor rear", f_tsub)], (940, 260), BLUE, cv("pan_rear_screws")),
    ([("M3\u00d710", f_tag),
      ("yoke bridge \u2192 pan motor output (\u00d74)", f_tsub)], (240, 600), RED, cv("yoke_bridge_screw")),
    ([("4\u00d7 M2.5\u00d716", f_tag),
      ("through yoke arm \u2192 tilt motor rear", f_tsub)],  (250, 790), BLUE, cv("tilt_rear_screws")),
    ([("M3\u00d710", f_tag),
      ("cradle \u2192 tilt motor output (\u00d72)", f_tsub)],          (940, 1030), RED, cv("cradle_rear_plate")),
    ([("4\u00d7 M3\u00d725", f_tag),
      ("printed-to-printed \u2014 long is fine here", f_tsub)], (1100, 330), GREEN, cv("cap_screws")),
    ([("clock the connector toward the cable trough NOW", f_caut),
      ("\u2014 the rear square has exactly 4 positions", f_caut2)], (240, 390), CAUT, cv("pan_motor_rear")),
]

# pass 1: rects
wl_rects = [box_of(lines, xy) for lines, xy, tgt in white_labels]
tg_rects = [box_of(lines, xy, pad=(10, 7)) for lines, xy, sty, tgt in tags]

# pass 2: leaders + dots (under boxes)
for (lines, xy, tgt), rect in zip(white_labels, wl_rects):
    s = clamp_start(rect, tgt)
    d.line([s, tgt], fill=INK, width=2)
    d.ellipse((tgt[0] - 4, tgt[1] - 4, tgt[0] + 4, tgt[1] + 4), fill=INK)
for (lines, xy, sty, tgt), rect in zip(tags, tg_rects):
    s = clamp_start(rect, tgt)
    d.line([s, tgt], fill=sty["border"], width=2)
    d.ellipse((tgt[0] - 4, tgt[1] - 4, tgt[0] + 4, tgt[1] + 4), fill=sty["border"])

# pass 3: boxes + text
def draw_box(rect, lines, xy, fill, border, tcol, pad=(12, 8), gap=3):
    d.rectangle(rect, fill=fill, outline=border, width=2)
    ty = xy[1] + pad[1]
    for t, f in lines:
        d.text((xy[0] + pad[0], ty), t, font=f, fill=tcol)
        ty += f.size + gap

for (lines, xy, tgt), rect in zip(white_labels, wl_rects):
    draw_box(rect, lines, xy, "#ffffff", INK, DARK)
for (lines, xy, sty, tgt), rect in zip(tags, tg_rects):
    draw_box(rect, lines, xy, sty["fill"], sty["border"], sty["text"], pad=(10, 7))

# ------------------------------------------------------- caption + note strip
capt = "frame v8 \u00b7 exploded \u00b7 print none of this until the coupons pass"
cw = d.textlength(capt, font=f_capt)
d.text((OX + 600 - cw / 2, 1143), capt, font=f_capt, fill=DARK)

note = ("No bearings anywhere \u2014 v8 deleted them. The head cantilevers off the "
        "tilt motor\u2019s own output, which carries about 3.5% of its peak torque.")
d.rectangle((40, 1195, 1560, 1252), fill="#fbfbf7", outline="#888888", width=2)
nw = d.textlength(note, font=f_note)
d.text((800 - nw / 2, 1214), note, font=f_note, fill="#444444")

img.save(OUT, "JPEG", quality=90)
print("saved", OUT, img.size)
for (lines, xy, tgt), rect in zip(white_labels, wl_rects):
    print("label", lines[0][0], "rect", rect, "->", tgt)
for (lines, xy, sty, tgt), rect in zip(tags, tg_rects):
    print("tag", lines[0][0][:24], "rect", rect, "->", tgt)
