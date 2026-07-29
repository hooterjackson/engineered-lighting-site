---
title: 3b · Print the Frame
description: "The gimbal's flat-printed, bolt-together parts: a parametric OpenSCAD scaffold with a five-minute fit coupon and X1C print settings."
---

# Doc 3b · Print the Frame — Nine Flat Parts, One Coupon

**Engineered Lighting prototype series · July 2026**
The frame chapter [Doc 3](03-build-the-gimbal.md) stage 7 points at. Context, fixed: motors are the **RMD-L-5005** (Ø49 × ~24 mm, 92 g, output flange per MyActuator's L-series 2D drawing), the spotlight payload is the **DLH-3UP-EH aluminum LED housing** (Ø0.99" finned barrel — the star's heatsink and the head's sliding balance mass in one part), the printer is a **Bambu Lab X1C**, and the material is **PETG Basic** (PETG-CF for the yoke if it's on hand). Iteration is the plan, not a failure mode: 2–3 reprints is the normal path, and every part is a ~20-minute print.

!!! agent-prompt "🤖 Give this to your agent"

    ```text
    You're my bench agent for the Engineered Lighting gimbal frame
    (chapter: engineering.engineered.lighting/03b-print-the-frame/). The
    RMD-L-5005 motors and my calipers are on the bench, a Bambu Lab X1C is
    on the network, and cad/frame.scad from this chapter is in my repo.
    Start by proposing a plan and wait for my approval before executing
    anything. Here are my caliper measurements: [paste the MEASURE-ME list
    with your numbers]. Update the parameters block in frame.scad, render
    every part to STL with the openscad CLI, and tell me which part to
    print first — it should be the fit coupon. After each test fit I will
    report what is tight or loose; adjust the parameters and re-render
    until the coupon seats flush and the bolts thread. Done when: every
    MEASURE-ME value is replaced by a measured one and the printed coupon
    fits the flange. Report back: the parameter diff after each round and
    the exact openscad commands you ran.
    ```

    *[How to run this prompt →](00b-ai-native-workflow.md)*

*Printing stalled — bad first layers, fit that won't converge, no printer time? A hand-drilled aluminum bar or plywood yoke made from a 1:1 printed drawing is a legitimate v0; the geometry is three brackets, not art.*

## The design rule: print flat, bolt square

Every part is a flat plate that prints exactly as modeled — **no supports,
anywhere**. Strength comes from bolted joints instead of tall fragile prints:
one repeated **T-joint** (printed tabs drop into slots, then two M3 bolts run
through the slotted plate into **square nuts** side-loaded into pockets in
the tabbed plate) joins everything. And the motors are **bolted, never
friction-fit** — a collar can't even slide over an RMD body, because the
4-pin connector is in the way.

**Pan base.** A plate the pan motor's **back cover bolts under** (its own
bolt pattern — MEASURE-ME), with a **clamp ear** for the BoM's C-clamp, a
center wire-pass hole, and a Ø8 **hard-stop post** long enough to reach down
into the bridge's swing plane (install the plate post-side down). The hard
stop exists because the encoder is single-turn: the frame, not software,
guarantees the motor can never wind past one revolution.

**Yoke = bridge + two arm plates.** The flat **bridge** bolts to the pan
output flange; the two arm plates tab up into it. The **motor arm** has a
boss-clearance window and the motor's **face-mount pattern**: the tilt motor
body sits *outside* the arm, face-bolted on, its output boss reaching
through the window into the gap — connector hanging in free air. The
**bearing arm** carries a printed boss pad so the 7 mm-wide **608** gets a
full-depth pocket with a shoulder, plus an M8 clearance hole. Zip-tie points
on both arms anchor the droopy service loops; an M3 hole above the axis
takes a **tilt hard-stop** standoff once travel is chosen.

**Head = boss plate + main plate + end plate + cradle ring.** The **boss
plate** bolts to the tilt output flange (pattern rotated 45° to clear the
joint). The **main plate** tabs into it, spans the yoke gap, and carries a
window sized over the housing; at its far edge the **end plate** holds a
captive M8 nut — the **M8 axle** slides in from outside, through the 608,
into that nut, so the head is supported on both sides and goes together
*last*. The **cradle ring** (ID = housing Ø + 0.6 mm ≈ 25.75 mm) face-bolts
over the window — ring + plate give ~16 mm of guided bore, gripping the
housing near the **center of its barrel**; a ~Ø25 mm flashlight fits as the
bench stand-in, and the star's wires exit the housing's hollow rear NPT
stub. Balancing has two orthogonal trims: **slide the housing** fore/aft and
nip the ring's pinch bolt, then **slide the M5 nuts** up the tail's vertical
slot. Balance *is* the silence mechanism: center of mass on the tilt axis
means near-zero hold current, which means a cool, silent motor.

## The parametric scaffold

The whole frame is one OpenSCAD file — [`cad/frame.scad`](cad/frame.scad) — with every motor-interface dimension in a parameters block at the top. Placeholders are marked **MEASURE-ME**; the drawing-readable values carry their own *verify with calipers on arrival* comments (the center thru-bore, notably, ships in two variants: 8.1 mm "S" and 12.7 mm "L"). One module is the cheapest insurance in the whole build: `fit_coupon()`, a 3 mm disc matching both motor bolt patterns and the center bore. It prints in about five minutes and bolts onto the real motor **before** any real part spends filament.

```scad
/* [Motor interface — MEASURE-ME] */
flange_bolt_circle_d = 30;   // MEASURE-ME — output-flange bolt circle
flange_center_bore_d = 8.1;  // drawing: 8.1 mm thru-bore ("S" variant; 12.7 on "L")
boss_clear_d         = 34;   // MEASURE-ME — output flange OD + 2 mm swing room
mount_bolt_circle_d  = 43;   // MEASURE-ME — FRONT face-mount holes around the boss
back_bolt_circle_d   = 43;   // MEASURE-ME — BACK cover mounting holes (pan side)
body_d               = 49;   // drawing: Ø49 body — verify on arrival

/* [Payload + frame] */
payload_od    = 25.15; // MEASURE-ME — DLH-3UP-EH housing barrel, Ø0.99" per its drawing
payload_clear = 0.6;   // slide fit: the housing must slip in and glide to balance
t             = 6;     // plate thickness, everywhere
```

One module per part — `fit_coupon()`, `pan_base()`, `yoke_bridge()`, `arm_motor()`, `arm_bearing()`, `head_boss_plate()`, `head_main_plate()`, `head_end_plate()`, `cradle_ring()` — behind a `part` selector (`"all"` lays every part flat on one plate), `$fn = 64`. The v3 coupon proves **both** motor bolt patterns, the center bore, and the boss clearance in one five-minute print. Render any part from the CLI:

```bash
openscad -o coupon.stl -D 'part="coupon"' cad/frame.scad
```

## X1C print settings, per part

| Part | Material | Walls / infill / layer | Orientation | Notes |
|---|---|---|---|---|
| Fit coupon | PETG Basic | 4 / 40% gyroid / 0.2 mm | flat | ~5 min; print first, always |
| Pan base | PETG Basic | 4 / 40% gyroid / 0.2 mm | flat (post up) | installs post-side down |
| Bridge + both arm plates | PETG-CF if on hand, else PETG Basic | 4 / 40% gyroid / 0.2 mm | flat | the load-bearing trio — CF stiffness pays off here |
| Head plates (boss / main / end) | PETG Basic | 4 / 40% gyroid / 0.2 mm | flat | drop the M8 nut into the end plate before joining |
| Cradle ring | PETG Basic | 4 / 40% gyroid / 0.2 mm | flat | printed on its face = strongest hoop for the pinch |

Every part lies flat, so layer lines run *along* every plate — bolts load
the plastic across continuous perimeters, and there is not a single
overhang in the whole set. `part="all"` arranges the complete frame on one
X1C plate.

## How it all goes together

Open [`cad/assembly.scad`](cad/assembly.scad) in OpenSCAD and press F5 to orbit the full assembly — a `view` dropdown flips exploded ↔ assembled, with the motors, bearing, LED housing, C-clamp and shelf shown as mockups around the printed parts.

## Build order

1. **Print the fit coupon** → *done when the output-flange bolts thread the inner circle, the face-mount bolts thread the outer circle, and the disc seats flush on the real motor.* Anything off, fix the parameters now — five-minute reprints beat twenty-minute ones.
2. **Pan base** → *done when the pan motor's back cover bolts under it and the C-clamp holds the assembly rigid on a shelf edge, post-side down.*
3. **Bridge on the pan flange, arms tabbed in** → *done when both arms bolt down square (M3s into their edge nuts) and the yoke swings freely to the hard-stop post.*
4. **Head on the desk** → *bolt the boss plate to the tilt motor's output flange; tab the main plate into it; tab the end plate on (M8 nut in its pocket first). Done when the head subassembly is rigid in your hands.*
5. **Marry head and yoke** → *face-bolt the tilt motor to its arm from outside; press the 608 into the bearing arm; slide the M8 through the bearing into the end-plate nut. Done when the head swings freely, supported on both sides.*
6. **Cradle ring + housing** → *ring face-bolts over the main plate's window; the LED housing glides through. Done when it slides with light finger pressure and the pinch bolt locks it.*
7. **Balance** — back to [Doc 3 stage 7](03-build-the-gimbal.md#stage-7-print-the-frame-balance-the-head): *slide the housing, then trim with the M5 stack. Done when the powered-off head stays posed anywhere you leave it.*

## BoM delta

Two additions to [Doc 3's BoM](03-build-the-gimbal.md#bill-of-materials-buy-this-350405-total): **digital calipers ($10–20)** — the whole chapter runs on measurements — and a **small hardware handful (~$8)**: ~10× M3×10 bolts with **square nuts**, one **M8×35 + nut** (the tilt axle), and M2.5 screws for the motor faces (length per the drawing). Filament and the 683/608 bearing are already in the list.
