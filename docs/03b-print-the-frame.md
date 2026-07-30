---
title: 3b · Print the Frame
description: "The gimbal's printed frame: six parts that print flat with no supports, every joint a bolt you can see, every fit derived from three numbers you measure off your own printer, and three cheap test pieces that find out before anything expensive prints."
---

# Doc 3b · Print the Frame — Six Parts, Three Test Pieces, No Guesswork

**Engineered Lighting prototype series · July 2026**
The frame chapter [Doc 3](03-build-the-gimbal.md) stage 7 points at. Context, fixed: the motors are **RMD-L-5005** (Ø49 × ~24 mm, 92 g, mounting holes on *both* faces), the spotlight payload is the **DLH-3UP-EH aluminum LED housing** (Ø0.99" finned barrel, 1.26" overall, flush front face — nothing protrudes — and a hollow 1/2"-14 NPT rear stub the wires come out of), the printer is a **Bambu Lab X1C**, and the material is **PETG Basic** (PETG-CF for the yoke if it's on hand). Iteration is the plan, not a failure mode.

!!! agent-prompt "🤖 Give this to your agent"

    ```text
    You're my bench agent for the Engineered Lighting gimbal frame
    (chapter: engineering.engineered.lighting/03b-print-the-frame/). The
    RMD-L-5005 motors and my calipers are on the bench, a Bambu Lab X1C is
    on the network, and cad/frame_params.scad, cad/frame.scad and
    cad/assembly.scad from this chapter are in my repo. Start by proposing
    a plan and wait for my approval before executing anything. The first
    part to print is tol_coupon, which measures my printer, not the design
    — I will report which test hole my M3 drops through, which post the
    608 turns freely on, and which ring it presses into, and you set
    hole_comp, hole_comp_h and shaft_comp in frame_params.scad from that.
    Then fit_coupon and bore_gauge against the real motor and the real
    housing. Here are my caliper measurements: [paste the MEASURE-ME list
    with your numbers]. Every edit goes in frame_params.scad — frame.scad
    is geometry only. Re-render with the openscad CLI after each round.
    Done when: all three tolerance constants came off a part I printed,
    every MEASURE-ME value is replaced by a measured one, and the coupon
    seats flush on both faces of the real motor. Report back: the
    parameter diff after each round and the exact commands you ran.
    ```

    *[How to run this prompt →](00b-ai-native-workflow.md)*

*Printing stalled — bad first layers, fit that won't converge, no printer time? A hand-drilled aluminum bar or plywood yoke made from a 1:1 printed drawing is a legitimate v0; the geometry is a few brackets, not art.*

## The six parts

| Part | What it is |
|---|---|
| `base_plate` | The only part that touches the world. The pan motor's **rear cover** bolts up into it, heads counterbored flush so the plate still sits flat under a shelf; a tongue reaches aft for the C-clamp; a buttressed post hangs 29 mm down into the yoke's swing plane as the pan hard stop. |
| `yoke` | Bridge and both arms, **one piece**. Prints standing on its bridge with the arms pointing up — zero supports, and there is no joint to align because there is no joint. |
| `cradle` | The head's saddle. Bolts to the tilt motor's output boss, carries the trunnion, holds the lower half of the housing bore. |
| `cradle_cap` | The other half of the clamp. Four screws pinch the housing between the two halves. |
| `trunnion` | The printed axle stub. There is no steel axle in this design. |
| `bearing_carrier` | Holds the 608 on the idle side and, on purpose, has oversize screw holes so it can *find* the axis instead of fighting it. |

Plus three test pieces that exist to be wrong cheaply, in the order you print them:

**`tol_coupon`** measures *your printer*. FDM gets holes and shafts wrong in opposite directions — a hole comes out undersize, a post comes out oversize — and every fit in this project is derived from three constants that describe by how much. The coupon prints four candidate values for each: find which hole your M3 drops through, which post your 608 slides onto and turns freely on, and which ring it presses into. Type those three numbers into `frame_params.scad` and every part in the set resizes itself. It is 45 g and you print it once, ever.

**`fit_coupon`** then checks the *motor*: a 3 mm disc carrying both bolt circles, the centre bore, and scribe rings at the boss and body diameters. **`bore_gauge`** checks the *housing*: a 14 mm slice of the real clamp — put the real barrel in it and find out whether Ø25.75 actually slides.

## The rules the design follows

**Every joint is a bolt you can see.** No tabs, no slots, no square nuts buried in pockets, nothing friction-fit. Printed-to-motor joints bolt into the motor's own threaded holes; printed-to-printed joints are machine screws self-tapping into printed pilot holes, with heat-set M3 inserts as the upgrade if anything ever works loose.

**The motors are bolted by their rear covers.** Both RMD faces carry mounting holes, and the rear one is a flat plate, so the mating surface is unambiguous. The tilt motor's body therefore lives *inside* the yoke with its connector hanging in free air, and both motors are bolted through a plate from the outside, where a driver can reach.

**Nothing is sized in absolute millimetres if a fit depends on it.** `m3_clear`, the 608's bore, the trunnion's stub, the recess that lands on the motor boss — all of them come out of fit functions driven by the three numbers `tol_coupon` measures. This is not decoration: the previous revision drew the trunnion stub at 7.85 mm to enter an 8.00 mm bearing, and because external cylinders print *over* size it would have come out at about 8.0 and never gone in.

**Where a printed part lands on a rotating boss, it lands on the boss and nothing else.** The locating recess is 1 mm deep against a boss that stands about 4 mm proud. That margin is deliberate: a part that bottomed out on the *stator* face would clamp the motor solid.

**Nothing that has to be round prints as a bridge.** The bearing pocket is a first-layer-accurate hole in a flat-printed carrier. The clamp bore is two valleys, one in the saddle and one in the cap, each printed concave-up. Lightening pockets are hexagons with a vertex up, so their roofs are a 60° peak rather than a 32 mm bridge. Every part is oriented inside the file, so `part="yoke"` gives you a slice-ready STL.

**Only three bolts hold the head to the tilt motor, and that's the point.** A bolt driven along the tilt axis needs a straight run for the driver, and the head's own body blocks any hole below the split line. So the design uses the three output-flange holes that sit *above* the split line, driven while the cap is off and the whole space above the bore is open air. Turn the output boss until one hole points straight up before you start. Three M3 on a 30 mm bolt circle carry the head's ~100 g and the motor's torque with an embarrassing margin.

**Both axes are hollow, and the cable route is one open channel.** The LED wires leave the housing's rear stub, run forward along a channel cut into the inner face of the cradle's motor-side plate, pass through that plate on the axis and straight through the **tilt motor's hollow shaft**, out through the arm, up a trough in the arm's outer face, around the corner, along a trough under the bridge and up through the **pan motor's hollow shaft**. Every millimetre of it is open from the outside, so the bundle drops in *after* everything is bolted together — there is no tunnel to thread and no service loop to snag. Two zip-tie points, one on the arm and one on the base plate. Verify that through-bore on arrival — it's a MEASURE-ME; if it turns out solid, the tie points are already there for external routing.

## The parametric scaffold

The frame is three OpenSCAD files. [`cad/frame_params.scad`](cad/frame_params.scad) holds **every number, once** — motor interface, payload, thicknesses, the print-tolerance constants and the fit functions built on them, then one derived chain that sets the machine's size. [`cad/frame.scad`](cad/frame.scad) is nothing but geometry, and [`cad/assembly.scad`](cad/assembly.scad) draws the whole machine. Both of the latter `include` the parameters file, so the assembly view cannot disagree with the parts you print. Placeholders are marked **MEASURE-ME**, and every one of them is checked by a coupon.

```scad
/* [Motor interface — MEASURE-ME] */
out_boss_d   = 36;    // MEASURE-ME  rotating output boss OD
out_boss_h   = 4;     // MEASURE-ME  how far the boss stands proud
out_bcd      = 30;    // MEASURE-ME  output-flange bolt circle
rear_bcd     = 43;    // MEASURE-ME  REAR cover bolt circle — this is the mount
shaft_bore_d = 8.1;   // MEASURE-ME  hollow through-bore (8.1 "S" / 12.7 "L")

/* [Print tolerances — MEASURE these with tol_coupon] */
hole_comp   = 0.25;  // vertical holes come out this much UNDERSIZE
hole_comp_h = 0.40;  // horizontal holes come out worse — the roof sags
shaft_comp  = 0.15;  // external cylinders come out this much OVERSIZE

function free_h(nom)  = nom + 0.5 + hole_comp;   // bolt drops through
function tap_h(nom)   = nom - 0.45 + hole_comp;  // self-taps into PETG
function slip_s(nom)  = nom - 0.15 - shaft_comp; // shaft that must TURN in a bore

/* [Payload — DLH-3UP-EH, off LEDdynamics' drawing] */
payload_od    = 25.15; // Ø0.99" over the fin crests — the clamped diameter
payload_clear = 0.6;   // slide fit: Ø25.75 ≈ 1.014", slides by hand
boss_recess   = 1;     // locating recess — KEEP WELL UNDER out_boss_h
```

Render any part, or the whole plate, from the CLI:

```bash
openscad -o tol_coupon.stl -D 'part="tol_coupon"' cad/frame.scad   # print this first
openscad -o cradle.stl     -D 'part="cradle"'     cad/frame.scad
openscad -o plate.stl      -D 'part="all"'        cad/frame.scad
```

## X1C print settings, per part

| Part | Material | Walls / infill / layer | Orientation | Roughly |
|---|---|---|---|---|
| `tol_coupon` | PETG Basic | 3 / 15% / 0.2 mm | flat, as emitted | ~1½ h · 45 g |
| `fit_coupon` | PETG Basic | 4 / 30% / 0.2 mm | flat, as emitted | 20 min · 9 g |
| `bore_gauge` | PETG Basic | 4 / 40% / 0.2 mm | as emitted | 35 min · 18 g |
| `base_plate` | PETG Basic | 4 / 40% gyroid / 0.2 mm | post UP; installs post DOWN | 2 h · 38 g |
| `yoke` | PETG-CF if on hand | 5 / 40% gyroid / 0.2 mm | arms UP, bridge on the bed | 6 h · 96 g |
| `cradle` | PETG Basic | 4 / 40% gyroid / 0.2 mm | as emitted, bore a valley | 1½ h · 21 g |
| `cradle_cap` | PETG Basic | 4 / 40% / 0.2 mm | inverted, bore a valley | 45 min · 11 g |
| `trunnion` | PETG Basic | 5 / 60% / 0.2 mm | stub UP | 30 min · 6 g |
| `bearing_carrier` | PETG Basic | 4 / 40% / 0.2 mm | pocket UP | 30 min · 9 g |

The masses are measured off the exported STLs at PETG's density and a 0.92 packing factor, not guessed: **181 g for the machine**, 72 g for the three test pieces, and the yoke is more than half the machine on its own. Times are slicer estimates at these settings and will move with your profile. `part="all"` lays every part flat, but that layout is 206 × 265 mm — a picture of the set, not a bed. Split it in two on a 256 mm X1C. There is not a single support in the set and no overhang steeper than 60°.

## How it all goes together

Open [`cad/assembly.scad`](cad/assembly.scad) in OpenSCAD and press F5. It `use`s `frame.scad` — importing the part modules without running that file's own render block — and `include`s the same `frame_params.scad`, so the assembly can never drift from the printed geometry. It draws **every part and every one of the 27 bolts** — both motors with their real bolt patterns, the 608, the LED housing with its flush front, the wire runs, the C-clamp and the shelf. A `view` dropdown flips exploded ↔ assembled, `pan` and `tilt` pose it, `show_cap` unchecks to look inside the clamp, and `clip` takes a section through the whole thing.

## Build order

Each step ends with something you can check by hand, and each one leaves the next step's fasteners reachable — that ordering is a property of the geometry, not a hope.

1. **`tol_coupon` first, before anything else.** Set `hole_comp`, `hole_comp_h` and `shaft_comp` from what it tells you. *Done when you have written three numbers into `frame_params.scad` that came off a part you printed, not out of this document.*
2. **Then the other two coupons.** *Done when the output-flange bolts thread the inner circle, the rear-cover bolts thread the outer circle, the disc seats flush on the boss, and the real housing slides into the bore gauge and locks when you nip its screws.* Fix the parameters here; a 20-minute reprint beats a 6-hour one.
3. **Yoke onto the pan motor, while the yoke is still empty.** Stand it on its arm tips, drop the motor into the bridge's locating recess boss-down, drive six M3 up from underneath. Turn the motor first so its **side connector faces the base plate's cable trough** — one of the other three positions puts the connector straight into the hard-stop post. *Done when the motor sits square and the yoke doesn't rock.* Do it now — once the head is in, those six bolts are behind it.
4. **Base plate down onto the pan motor's rear**, four M4 through the counterbores. *Done when the plate sits flat on a table with the yoke hanging free and swinging to the hard stop in both directions.*
5. **Cradle onto the tilt motor**, on the bench. Turn the output boss until one hole points straight up, then drive the three bolts above the split line. *Done when the cradle is rigid on the motor and the motor still turns freely by hand.*
6. **Trunnion onto the cradle's right plate**, three screws, heads outside. *Done when the stub runs true — spin it against a fixed pencil mark and watch for wobble.*
7. **Head up between the arms**, four M4 through the **left arm from the outside** into the tilt motor's rear holes. *Done when the head hangs on one side and swings.*
8. **608 into the carrier, carrier over the stub, three screws — left loose.** Swing the head through its whole travel, *then* tighten. *Done when the head is supported on both sides and still falls under its own weight from any angle. If it binds, back those three screws off and let the carrier move.*
9. **Wires** through both hollow shafts, then the C-clamp onto the shelf.
10. **Housing in, cap on, balance.** Lay the housing into the saddle, slide it along the bore until the powered-off head stays where you leave it, *then* pull the four cap screws down. There is no trim bolt and no counterweight, because the balance is drawn in: the tilt axis sits 1.45 mm **above** the housing's axis, which is where the measured centre of mass of the whole head — saddle, cap, trunnion and barrel — actually lands. Then back to [Doc 3 stage 7](03-build-the-gimbal.md#stage-7-print-the-frame-balance-the-head).

The bore is 32 mm long against a 22.6 mm finned barrel, so there are **9.4 mm of slide** — but it is now trim, not the balance mechanism. Solving for where the tilt axis has to sit puts the head's centre of mass on it to within 0.2 mm across any plausible housing weight, which is a gravity torque under 0.1 mN·m. Balance *is* the silence mechanism: centre of mass on the tilt axis means near-zero hold current, which means a cool, quiet motor. The slide is there for when your barrel is not the one on the drawing.

## Two things worth knowing before you print

**The pan hard stop is mechanical because the encoder is single-turn and the whole cable bundle passes through the pan axis.** A post on the base plate rides in an arc groove in the bridge, giving about **307°** of travel with the dead wedge pointed aft. It sits at a 31 mm radius, and because it is the one feature on this machine that gets *hit* — a 30 mm blade printed standing up, loaded across its layers, which is the weakest direction a printed part has — it carries a tapered buttress down 80% of its length that turns it into a T-section loaded along them. Even so, set a conservative current limit before you first test travel, and if it ever shears, an M6 bolt drops into the same position as the metal upgrade.

**Tilt is limited in firmware, not by a stop.** The frame clears a full rotation — the head's swing radius is 24.5 mm against a 32 mm drop, and that was checked by intersecting the posed head with the yoke as solids at 0 and ±90° rather than by eye — so what limits tilt is the cable and the servo's own position limits. A mechanical stop that close to the tilt axis could not survive stall torque, and pretending otherwise would be worse than saying so.

## BoM delta

Two additions to [Doc 3's BoM](03-build-the-gimbal.md#bill-of-materials-buy-this-350405-total): **digital calipers ($10–20)**, because the whole chapter runs on measurements, and a **small hardware handful (~$10)**: eight M4 socket cap screws in 16 and 20 mm, about twenty M3 in 14–20 mm, and M2.5 screws instead of M4 if the rear circle turns out to be tapped M2.5. No square nuts, no captive hardware, nothing exotic, and no counterweight — the tilt axis is drawn 1.45 mm above the housing's axis, which is exactly where the head's centre of mass sits, so there is nothing to trim. Filament and the 608 are already in the list.
