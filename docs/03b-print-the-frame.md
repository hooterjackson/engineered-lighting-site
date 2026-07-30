---
title: 3b · Print the Frame
description: "The gimbal's printed frame: six parts that print flat with no supports, every joint a bolt into metal threads or a bolt you can see, plus two five-minute coupons that check the fit before anything expensive prints."
---

# Doc 3b · Print the Frame — Six Parts, Two Coupons, No Guesswork

**Engineered Lighting prototype series · July 2026**
The frame chapter [Doc 3](03-build-the-gimbal.md) stage 7 points at. Context, fixed: the motors are **RMD-L-5005** (Ø49 × ~24 mm, 92 g, mounting holes on *both* faces), the spotlight payload is the **DLH-3UP-EH aluminum LED housing** (Ø0.99" finned barrel, 1.26" overall, flush front face — nothing protrudes — and a hollow 1/2"-14 NPT rear stub the wires come out of), the printer is a **Bambu Lab X1C**, and the material is **PETG Basic** (PETG-CF for the yoke if it's on hand). Iteration is the plan, not a failure mode.

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
    fits both faces of the real motor. Report back: the parameter diff
    after each round and the exact openscad commands you ran.
    ```

    *[How to run this prompt →](00b-ai-native-workflow.md)*

*Printing stalled — bad first layers, fit that won't converge, no printer time? A hand-drilled aluminum bar or plywood yoke made from a 1:1 printed drawing is a legitimate v0; the geometry is three brackets, not art.*

## The six parts

| Part | What it is |
|---|---|
| `base_plate` | The only part that touches the world. The pan motor's **rear cover** bolts up into it, heads counterbored flush so the plate still sits flat under a shelf; a tongue reaches aft for the C-clamp; a stubby post hangs down into the yoke's swing plane as the pan hard stop. |
| `yoke` | Bridge and both arms, **one piece**. Prints standing on its bridge with the arms pointing up — zero supports, and there is no joint to align because there is no joint. |
| `cradle` | The head's saddle. Bolts to the tilt motor's output boss, carries the trunnion, holds the lower half of the housing bore. |
| `cradle_cap` | The other half of the clamp. Four screws pinch the housing between the two halves. |
| `trunnion` | The printed axle stub. There is no steel axle in this design. |
| `bearing_carrier` | Holds the 608 on the idle side and, on purpose, has oversize screw holes so it can *find* the axis instead of fighting it. |

Plus two coupons that exist to be wrong cheaply: **`fit_coupon`**, a 3 mm disc carrying *both* motor bolt circles, the centre bore and scribe rings at the boss and body diameters (8 minutes, 3 g), and **`bore_gauge`**, a 14 mm slice of the real clamp — put the real housing in it and find out whether Ø25.75 mm actually slides (25 minutes).

## The rules the design follows

**Every joint is a bolt you can see.** No tabs, no slots, no square nuts buried in pockets, nothing friction-fit. Printed-to-motor joints bolt into the motor's own threaded holes; printed-to-printed joints are machine screws self-tapping into printed pilot holes, with heat-set M3 inserts as the upgrade if anything ever works loose.

**The motors are bolted by their rear covers.** Both RMD faces carry mounting holes, and the rear one is a flat plate, so the mating surface is unambiguous. The tilt motor's body therefore lives *inside* the yoke with its connector hanging in free air, and both motors are bolted through a plate from the outside, where a driver can reach.

**Where a printed part lands on a rotating boss, it lands on the boss and nothing else.** The locating recess is 1 mm deep against a boss that stands about 4 mm proud. That margin is deliberate: a part that bottomed out on the *stator* face would clamp the motor solid.

**Nothing that has to be round prints as a bridge.** The bearing pocket is a first-layer-accurate hole in a flat-printed carrier. The clamp bore is two valleys, one in the saddle and one in the cap, each printed concave-up. Every part is oriented inside the file, so `part="yoke"` gives you a slice-ready STL.

**Only three bolts hold the head to the tilt motor, and that's the point.** A bolt driven along the tilt axis needs a straight run for the driver, and the head's own body blocks any hole below the split line. So the design uses the three output-flange holes that sit *above* the split line, driven while the cap is off and the whole space above the bore is open air. Turn the output boss until one hole points straight up before you start. Three M3 on a 30 mm bolt circle carry the head's ~100 g and the motor's torque with an embarrassing margin.

**Both axes are hollow.** The LED wires leave the housing's rear stub, run along a channel moulded into the cap's corner, pass through the cradle's motor plate on the axis, go straight through the **tilt motor's hollow shaft**, out through the arm, up the arm's cable channel, under the bridge and up through the **pan motor's hollow shaft**. There is no service loop to snag. Verify that through-bore on arrival — it's a MEASURE-ME; if it turns out solid, the zip-tie anchors on both arms are already there for external routing.

## The parametric scaffold

The whole frame is one OpenSCAD file — [`cad/frame.scad`](cad/frame.scad) — with every motor-interface dimension in a parameters block at the top and one derived chain that sets the machine's size from them. Placeholders are marked **MEASURE-ME**, and every one of them is checked by the coupon.

```scad
/* [Motor interface — MEASURE-ME] */
out_boss_d   = 36;    // MEASURE-ME  rotating output boss OD
out_boss_h   = 4;     // MEASURE-ME  how far the boss stands proud
out_bcd      = 30;    // MEASURE-ME  output-flange bolt circle
rear_bcd     = 43;    // MEASURE-ME  REAR cover bolt circle — this is the mount
shaft_bore_d = 8.1;   // MEASURE-ME  hollow through-bore (8.1 "S" / 12.7 "L")

/* [Payload — DLH-3UP-EH, off LEDdynamics' drawing] */
payload_od    = 25.15; // Ø0.99" over the fin crests — the clamped diameter
payload_clear = 0.6;   // slide fit: Ø25.75 ≈ 1.014", slides by hand
boss_recess   = 1;     // locating recess — KEEP WELL UNDER out_boss_h
```

Render any part, or the whole plate, from the CLI:

```bash
openscad -o cradle.stl -D 'part="cradle"' cad/frame.scad
openscad -o plate.stl  -D 'part="all"'    cad/frame.scad
```

## X1C print settings, per part

| Part | Material | Walls / infill / layer | Orientation | Roughly |
|---|---|---|---|---|
| `fit_coupon` | PETG Basic | 4 / 30% / 0.2 mm | flat, as emitted | 8 min · 3 g |
| `bore_gauge` | PETG Basic | 4 / 40% / 0.2 mm | as emitted | 25 min · 12 g |
| `base_plate` | PETG Basic | 4 / 40% gyroid / 0.2 mm | post UP; installs post DOWN | 2 h · 38 g |
| `yoke` | PETG-CF if on hand | 5 / 40% gyroid / 0.2 mm | arms UP, bridge on the bed | 4½ h · 70 g |
| `cradle` | PETG Basic | 4 / 40% gyroid / 0.2 mm | as emitted, bore a valley | 2½ h · 38 g |
| `cradle_cap` | PETG Basic | 4 / 40% / 0.2 mm | inverted, bore a valley | 1 h · 15 g |
| `trunnion` | PETG Basic | 5 / 60% / 0.2 mm | stub UP | 30 min · 6 g |
| `bearing_carrier` | PETG Basic | 4 / 40% / 0.2 mm | pocket UP | 35 min · 10 g |

Call it **12 hours and about 190 g** for the whole set, and the yoke is half of that. `part="all"` lays every part flat on one 256 mm plate. There is not a single support in the set and no overhang steeper than 45°.

## How it all goes together

Open [`cad/assembly.scad`](cad/assembly.scad) in OpenSCAD and press F5. It `include`s `frame.scad`, so the assembly can never drift from the printed geometry, and it draws **every part and every bolt** — both motors with their real bolt patterns, the 608, the LED housing with its flush front, the wire runs, the C-clamp and the shelf. A `view` dropdown flips exploded ↔ assembled, `pan` and `tilt` pose it, `show_cap` unchecks to look inside the clamp, and `clip` takes a section through the whole thing.

## Build order

Each step ends with something you can check by hand, and each one leaves the next step's fasteners reachable — that ordering is a property of the geometry, not a hope.

1. **Coupons first.** *Done when the output-flange bolts thread the inner circle, the rear-cover bolts thread the outer circle, the disc seats flush on the boss, and the real housing slides into the bore gauge and locks when you nip its screws.* Fix the parameters here; an 8-minute reprint beats a 4-hour one.
2. **Yoke onto the pan motor, while the yoke is still empty.** Stand it on its arm tips, drop the motor into the bridge's locating recess boss-down, drive six M3 up from underneath. *Done when the motor sits square and the yoke doesn't rock.* Do it now — once the head is in, those six bolts are behind it.
3. **Base plate down onto the pan motor's rear**, four M4 through the counterbores. *Done when the plate sits flat on a table with the yoke hanging free and swinging to the hard stop in both directions.*
4. **Cradle onto the tilt motor**, on the bench. Turn the output boss until one hole points straight up, then drive the three bolts above the split line. *Done when the cradle is rigid on the motor and the motor still turns freely by hand.*
5. **Trunnion onto the cradle's right plate**, three screws, heads outside. *Done when the stub runs true — spin it against a fixed pencil mark and watch for wobble.*
6. **Head up between the arms**, four M4 through the **left arm from the outside** into the tilt motor's rear holes. *Done when the head hangs on one side and swings.*
7. **608 into the carrier, carrier over the stub, three screws — left loose.** Swing the head through its whole travel, *then* tighten. *Done when the head is supported on both sides and still falls under its own weight from any angle. If it binds, back those three screws off and let the carrier move.*
8. **Wires** through both hollow shafts, then the C-clamp onto the shelf.
9. **Housing in, cap on, balance.** Lay the housing into the saddle, slide it along the bore until the powered-off head stays where you leave it, *then* pull the four cap screws down. Fine trim is washers on an M4 through the cradle's keel hole, fore or aft. Then back to [Doc 3 stage 7](03-build-the-gimbal.md#stage-7-print-the-frame-balance-the-head).

The bore is 36 mm long against a 32 mm housing, so there are about 4 mm of pure slide plus whatever the clamp will still hold at the extremes — which is enough, because clamping near the middle of the barrel is what makes the payload nearly balanced in the first place. Balance *is* the silence mechanism: centre of mass on the tilt axis means near-zero hold current, which means a cool, quiet motor.

## Two things worth knowing before you print

**The pan hard stop is mechanical because the encoder is single-turn and the whole cable bundle passes through the pan axis.** A post on the base plate rides in an arc groove in the bridge, giving about **311°** of travel with the dead wedge pointed aft. It sits at a 31 mm radius on a short, gusseted post precisely so that it can survive being hit; even so, set a conservative current limit before you first test travel, and if it ever shears, an M6 bolt drops into the same position as the metal upgrade.

**Tilt is limited in firmware, not by a stop.** The frame clears a full rotation — the head's swing radius is 28 mm against a 38 mm drop — so what limits tilt is the cable and the servo's own position limits. A mechanical stop that close to the tilt axis could not survive stall torque, and pretending otherwise would be worse than saying so.

## BoM delta

Two additions to [Doc 3's BoM](03-build-the-gimbal.md#bill-of-materials-buy-this-350405-total): **digital calipers ($10–20)**, because the whole chapter runs on measurements, and a **small hardware handful (~$10)**: eight M4 socket cap screws in 16 and 20 mm, about twenty M3 in 14–20 mm, one M4×45 with a few M4 washers for the balance trim, and M2.5 screws instead of M4 if the rear circle turns out to be tapped M2.5. No square nuts, no captive hardware, nothing exotic. Filament and the 608 bearing are already in the list.
