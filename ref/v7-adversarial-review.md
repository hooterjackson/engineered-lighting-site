# Adversarial review of the v7 frame

What this is: the review the ground-up brief asks for, of `docs/cad/` as it
stood on main at commit `f6e54be` (`frame.scad` v7, `frame_params.scad` v7 plus
the housing-tolerance fix, `assembly.scad` v6).

Method: six independent lenses — does it match the real motor, fits and
tolerances, geometry that does nothing, printability, assembly order, boolean
interference — each finding then handed to a separate reviewer whose job was to
**refute** it from the file bytes, defaulting to refuted when it could not be
independently reproduced.

**49 findings raised. 29 survived refutation. 20 were refuted.** Of the 29, seven
were artifacts of a mismatched file set on disk while the review ran (see the
last section), leaving **14 distinct real defects** after collapsing duplicates.

Six of the lenses independently found the same blocking defect. That is the one
to read first.

---

## Blocking

### 1. The cradle has no output-flange bolt holes at all

`frame.scad:324-326`. The clearance cut is

```
rotate([0, 90, 0]) cylinder(d = m3_clear_x, h = 3 * cr_wall, center = true)
```

`rotate([0,90,0])` lays the cylinder along X through the origin, so with
`center = true` it spans **x = −12.000 … +12.000**. The outer `rotate([a,0,0])`
swings it around the bolt circle in Y-Z and cannot change its X extent.

The plate it is supposed to pierce — the one that lands on the motor's output
face — spans **x = −22.865 … −14.865** (`x_left = −22.865`, `cr_wall = 8`).

**The nearest ends are 2.865 mm apart. There is zero overlap. The cut removes
no material.**

Verified by boolean: `intersection(cradle_solid, that exact cut)` returns
*"Current top level object is empty"* and OpenSCAD writes no STL, while the
same cut moved onto the plate removes 190.828 mm³ — which matches the closed
form for two Ø3.90 × 8 mm prisms at `$fn=64` (190.8276 mm³) to four decimals.
The cradle solid alone is 20 725.023 mm³, so the method was detecting material.

Both reachable holes are missing, not one: `out_bolt_up(i)` is true for i=0 and
i=3 (`out_bolt_z` = +8.83883 for both).

**Consequence:** the two M3 on the Ø25 circle are the only attachment from the
head to the tilt motor. The cradle prints with a solid, unbroken motor-side
plate. The head cannot be bolted on. Because the cut is a pure no-op it changes
no mass and shows in no render — the part looks perfect.

This is the defect the whole "geometry that does nothing" class exists to catch,
and it is still the biggest one in the file.

### 2. Step 6 cannot be performed — the head does not fit between the arms

`frame.scad:73`. Arm inner faces sit at x = ±39.815, a clear gap of 79.630 mm.
The step-6 sub-assembly is tilt motor (23.900) + cradle (45.730) + trunnion
flange (6.000) = 75.630 mm, leaving **4.000 mm of axial slack**.

But the trunnion stub has to end up protruding `t_arm + carrier_t + 0.9` =
**19.900 mm** past the right arm's inner face to reach its bearing.

Short by 15.900 mm. At the position where the stub tip is merely flush with the
right arm, the tilt motor's rear face is at x = −59.715 — **9.9 mm outboard of
the left arm's outer face**, i.e. the motor would have to pass through a 10 mm
arm. `intersection(yoke, head_sub translated −19.9)` = 12 300.51 mm³.

**Consequence:** the machine cannot be assembled. Every part is fine alone and
the assembled render is clean; this only appears when you try to build it, after
~180 g of PETG. `span_h` is derived from the *assembled* stack-up and nothing in
the chain accounts for insertion travel.

### 3. Step 9 — the cap cannot seat, because step 4's screw heads are in its slot

`frame.scad:353`. `cap_w = slot_fit(2*blk_in)` = 29.030, so the cap body's
motor-side face is at x = −14.515. The step-4 output-flange screws seat on the
plate's inner face at x = −14.865. Clearance for the head: **0.350 mm**. An M3
socket cap head is 3.0 mm tall, reaching x = −11.865.

**Interference 2.650 mm.** `intersection(cradle_cap, the two seated heads)` =
161.38 mm³. Nothing counterbores them.

**Consequence:** fasteners installed at step 4 are trapped behind a part
installed at step 9 — the exact defect class already in the log. The cap sits
2.65 mm high, so the clamp gap becomes 3.44 mm instead of 0.79 and the four cap
screws pull the ears down onto nothing.

### 4. The trunnion's three M3 heads land inside the shank beside them

`frame.scad:398`. Bolt circle radius `trun_bcd/2` = 9.000; the Ø14 shank rises
from the same face the heads bear on, radius 7.000. With the file's own
`m3_head_d` = 6.4 the head's inner edge is at 5.800 — **1.200 mm inside the
shank**. With a real ISO 4762 head (Ø5.5) it is still 0.750 mm inside.
`intersection(trunnion, three heads)` = 31.8 mm³ in three islands.

Build step 5 ("three screws, heads outside") cannot be executed with any
standard M3.

### 5. `bore_gauge` prints its second half floating 16 mm above the platform

`frame.scad:504`. `p_bore_gauge()` translates by `base_z` only, leaving the cap
half a 29 × 14 × 22 mm solid in mid-air. This is build-order step 1 — the piece
printed before anything else — in a project whose hard requirement is zero
supports.

---

## Major

### 6. The base plate's cable-tie point is sealed by the motor's own rear face

`frame.scad:214`. The tie must loop through one slot, round the far side and
back through the other — but the far side is the plate face the motor is bolted
flat against. There is no return path once step 3 is done, and the wires are laid
at step 8. Threading the tie beforehand traps it in the joint.

### 7. `fit_coupon`'s two bolt circles merge into four slots

`frame.scad:133`. The Ø25 M3 circle and the Ø28.284 M2.5 circle overlap, so the
holes merge: an M3 and an M2.5 both drop through the same slot regardless of
whether either circle is right. The coupon whose entire job is to prove both
motor interfaces for 3 g of PETG proves neither — against the exact failure mode
(invented bolt circles) that caused this rebuild.

### 8. `assembly.scad` specifies M3 screws longer than the hole exists

`assembly.scad:179` and `:162`. The view calls for M3×13 and M3×14 into the
output flange. **The tapped hole is 2.5 mm deep** (`ref/RMD-L-5005-S.md`, read
out of the vendor STEP) and breaks through into the rotor cavity at x = 2.5.
Both screws bottom 2.5–3.5 mm before the head seats, so neither joint is ever
clamped and the tips are inside the motor.

Found independently by the review and by the STEP parse. It is also why the
motor model in `assembly.scad` hides the collision: it draws no blind hole.

### 9. `p_cradle` emits the part 1.740 mm below the build platform

`frame.scad:507`. `translate([0,0,base_z]) cradle()` ignores the `−axis_z`
offset inside `cradle()`. A slicer that clips to the platform silently removes
the bottom 1.740 mm of the keel — the material under the bore drops from 3.135
to 1.395 mm, and both 45° keel chamfers, the part's entire first-layer
footprint, go with it.

### 10. `bore_gauge` does not measure the part it stands in for

`frame.scad:504`. Its cap bore prints as an 87° dome — a sagging arch — where
the real `cradle_cap` prints the same bore as a valley. The sag is toward the
barrel, so the gauge reads tight exactly where the real part is not.

### 11. The yoke's hard-stop groove roof is 1565 mm² of flat bridging

`frame.scad:249`. Unsupported runs of 45.65 mm, against a designed post
clearance of **0.600 mm**. PETG will not hold 0.6 mm over 45 mm. If it sags the
post rides on the groove floor.

---

## Minor

### 12. `cradle_cap`'s crown pocket is a 23.03 × 25.00 mm flat bridge

`frame.scad:375`. Same class as the logged defect *"a 32 mm circular pocket roof
printed as a bridge where a hexagon with a vertex up would have been a
self-supporting 60° peak"* — fixed on the yoke arms, not here. The 3.925 mm of
material carrying the clamp bore is printed on top of the droop.

### 13. `tie_slots` sit 0.150 mm from the cable trough wall

`frame.scad:214`, in two parts. The slicer discards the sliver, so the channel
opens from 7.00 to 10.70 mm over 3.4 mm of its run.

### 14. The connector-clocking instruction is on the wrong build step

`frame.scad:67`. Step 2 says to turn the motor so its connector faces the cable
trough, but the clocking is fixed at step 3 by the rear square, which offers only
four positions. Following the file costs up to three teardowns.

---

## What was refuted, and why it matters

Twenty findings did not survive. The refutations were as valuable as the
confirmations, because a confident wrong finding is the failure mode this
project is trying to escape. Examples:

- **"The clamp bottoms out and grips air on the bottom of the tolerance band."**
  Refuted by direct evaluation: `clamp_nip` = 0.790 against a worst-case
  required travel of 0.480 for a minimum (24.77 mm) barrel. The cap still has
  0.310 mm of gap left when it grips the smallest barrel the drawing allows.
  **The housing-tolerance fix in the newer `frame_params.scad` works.**
- **"The cap's four ears collapse onto the bore axis."** Refuted: `cap_bolt_x`
  = 17.765, not 0.

Both of those fired because of the next section.

## A caveat on how this review was run

While the six lenses were working, the working tree held an **uncommitted v8
`frame_params.scad` next to v7 geometry** — my own in-flight rewrite. Five
findings are about that skew, and two more (the two refuted above) are
downstream of it: names that exist only in v7 evaluate to `undef` under v8, and
`undef` silently collapses geometry.

That is not a defect in the design, but it is worth recording for two reasons.
First, the reviewers caught it unprompted and correctly re-resolved their
arithmetic against the committed pair — which is why the numbers above are
trustworthy. Second, **it is a live demonstration of open unknown #2 in the
brief**: a mismatched file set produces `WARNING: Ignoring unknown variable`,
then writes a valid STL and exits 0. A slicer accepts it. That is exactly how
the Downloads-folder file set produces "only some of the parts render", and it
happened again, to me, inside this repo, within an hour of reading the log.

The version banner exists precisely so this is visible. It worked.
