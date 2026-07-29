---
title: 3b · Print the Frame
description: "The gimbal's three printed parts, a parametric OpenSCAD scaffold with a five-minute fit coupon, and X1C print settings."
---

# Doc 3b · Print the Frame — Three Parts, One Coupon

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
    all four parts to STL with the openscad CLI, and tell me which part to
    print first — it should be the fit coupon. After each test fit I will
    report what is tight or loose; adjust the parameters and re-render
    until the coupon seats flush and the bolts thread. Done when: every
    MEASURE-ME value is replaced by a measured one and the printed coupon
    fits the flange. Report back: the parameter diff after each round and
    the exact openscad commands you ran.
    ```

    *[How to run this prompt →](00b-ai-native-workflow.md)*

*Printing stalled — bad first layers, fit that won't converge, no printer time? A hand-drilled aluminum bar or plywood yoke made from a 1:1 printed drawing is a legitimate v0; the geometry is three brackets, not art.*

## The three parts, specified

**Pan base.** A plate the pan motor body bolts to, with a **clamp ear** sized for the BoM's C-clamp so the assembly hangs from a shelf edge, and a **pan hard-stop post**. The hard stop exists because the encoder is single-turn: the frame, not software, guarantees the motor can never wind past one revolution ([Doc 3](03-build-the-gimbal.md)'s absolute-encoder concept).

**Yoke.** A U-bracket bolted to the pan output flange: two arms hanging from a bridge bar, each ending in a collar. One collar grips the **tilt motor body**; the other holds the **683/608 bearing** so the head is supported on both sides. The collar bores are **teardropped**, so the X1C prints the yoke arms-up with no supports. **Tilt hard-stop tabs** (same single-turn reason), plus **zip-tie points** on the arms — Doc 3's wiring rule: pigtails cross each joint as a droopy service loop, never taut, and the loop needs somewhere to anchor.

**Head shell.** A **pinch-collar cradle** on the tilt flange, sized so the LED housing glides through it (cradle ID = housing Ø + 0.6 mm ≈ 25.75 mm; a ~Ø25 mm flashlight fits the same cradle as the bench stand-in, and the star's wires exit through the housing's hollow rear NPT stub). The housing's barrel *crosses* the tilt axis: slide it fore/aft until the powered-off head balances, then an M3 pinch bolt locks it. An **end plate** takes an M8 bolt pushed through the 608 from outside — that bolt is the head's second support, and it goes in last, which makes assembly trivial. The **counterweight slot** (M5 bolt + stacked nuts) stays for fine trim, because balance *is* the silence mechanism: center of mass on the tilt axis means near-zero hold current, which means a cool, silent motor.

## The parametric scaffold

The whole frame is one OpenSCAD file — [`cad/frame.scad`](cad/frame.scad) — with every motor-interface dimension in a parameters block at the top. Placeholders are marked **MEASURE-ME**; the drawing-readable values carry their own *verify with calipers on arrival* comments (the center thru-bore, notably, ships in two variants: 8.1 mm "S" and 12.7 mm "L"). The fourth module is the cheapest insurance in the whole build: `fit_coupon()`, a 3 mm ring matching the flange bolt pattern and center bore. It prints in about five minutes and bolts onto the real motor **before** any real part spends filament.

```scad
/* [Motor interface — MEASURE-ME] */
flange_bolt_circle_d = 30;   // MEASURE-ME — output-flange bolt-circle diameter
flange_bolt_d        = 3.2;  // MEASURE-ME — bolt clearance hole (M3 assumed)
flange_bolt_n        = 4;    // MEASURE-ME — bolt count per the drawing
flange_center_bore_d = 8.1;  // drawing: 8.1 mm thru-bore on the "S" variant
                             // (12.7 mm on the "L") — verify with calipers on arrival
body_d               = 49;   // drawing: Ø49 body — verify with calipers on arrival
body_len             = 24;   // drawing: ~24 mm body — verify with calipers on arrival
connector_clearance  = 12;   // MEASURE-ME — depth behind the 4-pin connector + cable bend

/* [Payload + frame] */
payload_od    = 25.15; // MEASURE-ME — DLH-3UP-EH housing barrel, Ø0.99" per its drawing
payload_clear = 0.6;   // slide fit: the housing must slip in and glide to balance
arm_offset    = 8;     // daylight between yoke arm and motor body
```

One module per part — `fit_coupon()`, `pan_base()`, `yoke()`, `head_shell()` — behind a `part` selector, `$fn = 64`. Render any part from the CLI:

```bash
openscad -o coupon.stl -D 'part="coupon"' cad/frame.scad
```

## X1C print settings, per part

| Part | Material | Walls / infill / layer | Orientation | Notes |
|---|---|---|---|---|
| Fit coupon | PETG Basic | 4 / 40% gyroid / 0.2 mm | flat | ~5 min; print first, always |
| Pan base | PETG Basic | 4 / 40% gyroid / 0.2 mm | flat on the plate | — |
| Yoke | PETG-CF if on hand, else PETG Basic | 4 / 40% gyroid / 0.2 mm | **arms up**, brim on | no supports — arm roots stay ≤45° and the collar bores are teardropped |
| Head shell | PETG Basic | 4 / 40% gyroid / 0.2 mm | cradle flat (payload bore vertical) | disc, spine and tail print as vertical walls; the axle is an M8 bolt, not a printed stub |

The yoke's orientation is the one that matters: printed arms-up, layer lines run *along* each arm, so gravity and motor torque load the plastic across continuous perimeters instead of shearing the layer bonds at the arm roots.

## How it all goes together

![Gimbal assembly — exploded, numbered in build order, with the assembled result inset](assets/gimbal-assembly-guide.svg)

*Gold, orange and teal are the three printed parts; gray parts are bought. Open [`cad/assembly.scad`](cad/assembly.scad) in OpenSCAD to orbit this view live (a `view` dropdown flips exploded ↔ assembled).*

## Build order

1. **Print the fit coupon** → *done when the flange bolts thread through it and the ring seats flush on the real motor.* Anything off, fix the parameters now — five-minute reprints beat twenty-minute ones.
2. **Pan base** → *done when the motor body bolts to it and the C-clamp holds the assembly rigid on a shelf edge.*
3. **Yoke** on the pan flange → *done when it bolts down square and clears the motor body through full pan travel.*
4. **Tilt motor into its collar, 608 into the other** → *done when the motor body seats and the bearing presses home.*
5. **Head shell** → *done when it bolts to the tilt flange, the M8 axle slides through the bearing into the end plate, and the LED housing glides in the cradle with the pinch bolt holding it still.*
6. **Balance** — back to [Doc 3 stage 7](03-build-the-gimbal.md#stage-7-print-the-frame-balance-the-head): *done when the powered-off head stays posed anywhere you leave it.*

## BoM delta

One addition to [Doc 3's BoM](03-build-the-gimbal.md#bill-of-materials-buy-this-350405-total): **digital calipers ($10–20)** — the whole chapter runs on measurements. An X1C owner needs nothing else new; filament and bearings are already in the list.
