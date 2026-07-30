# Robotic spotlight frame — ground-up redesign brief

Paste this whole file as the first message of a new session.

---

## What I want

Design the printed frame for a two-axis robotic spotlight **from scratch**, in OpenSCAD. Do not start from the existing files. Read them as evidence of what has already gone wrong, then design fresh.

Work in this order, and don't skip ahead:

1. **Establish the component data.** Sources or nothing — see "Two open unknowns" below.
2. **Adversarial review** of the current design (`docs/cad/` in the repo). The defect log below is the accumulated result of four previous rounds; treat it as a list of rules the new design must not violate.
3. **Design and build** the new files.
4. **Second adversarial pass on your own work** — render every part and the assembly, look at the images, run the interference check, re-measure mass and balance. Screenshot everything and actually inspect it.
5. Deliver files + renders, then push.

Take the time to do 4 properly. Every previous round shipped a new defect because the validation was thinner than the design work.

---

## The machine

A pan/tilt spotlight for a home lighting system. Documented as an engineering notebook at **engineering.engineered.lighting**, repo **`hooterjackson/engineered-lighting-site`**, CAD lives in `docs/cad/`.

- **Two motors**, MyActuator RMD-L-5005 (CAN variant). Pan motor hangs the whole machine from a base plate; tilt motor drives the head.
- **Payload**: a LEDdynamics DLH-3UP-EH aluminium spotlight housing — a Ø25 mm barrel — held in a printed clamp.
- **One 608ZZ bearing** on the idle side of the tilt axis.
- Printed in PETG on a Bambu Lab X1C. Zero supports is a hard requirement.
- Bench-mounted via a C-clamp on a tongue off the base plate.

Current parts: `base_plate`, `yoke` (bridge + two arms, one piece), `cradle` + `cradle_cap` (the clamp), `trunnion` (printed axle), `bearing_carrier`. Plus three test pieces: `tol_coupon`, `fit_coupon`, `bore_gauge`. **You are not obliged to keep this parts breakdown** — if a better architecture exists, argue for it. Consider seriously whether the idle side (trunnion + carrier + bearing + 6 screws) earns its place against a single-arm cantilever on the tilt motor's own output bearing.

---

## Two open unknowns — resolve these FIRST

Everything else downstream depends on them, and both previous rounds of guessing produced designs that could not be built.

### 1. The motor's output face

**Does the whole front face rotate, or only an inner disc? Is there a raised boss, and how far does it stand proud?**

This decides whether a printed plate can land flat on the face or must land on a boss and nothing else. A part that bottoms on the stationary housing clamps the motor solid.

Not published anywhere reachable. Evidence so far: the RMD-L manual's RMD-50 drawing shows **no circle between Ø25 and Ø48** on the output view, and the *same manual* explicitly dimensions bosses on the RMD-90 and RMD-120. Suggestive of a flat face; not proof.

**How to close it:** `https://www.dingsmotionusa.com/s/RMD-L-5005-S.STEP`. STEP is plain ASCII — parse `CYLINDRICAL_SURFACE` radii and their axial positions, and the sorted list of distinct radii answers boss diameter, boss height and connector protrusion in one shot. Every host serving it was blocked from the previous session's sandbox; try again, and if it's still blocked ask me to download it and hand it over.

### 2. Does `assembly.scad` render all six printed parts

On my machine it renders only some of them; on the previous session's it rendered all of them, including with a deliberately mismatched file set. Unresolved. Before designing around it, have me run this in OpenSCAD alongside the three `.scad` files and report **which parts appear and exactly what the console says**:

```scad
include <frame_params.scad>
use <frame.scad>
echo(cad_version);
translate([  0,0,0]) yoke();
translate([120,0,0]) base_plate();
translate([220,0,0]) cradle();
translate([300,0,0]) cradle_cap();
translate([360,0,0]) trunnion();
translate([420,0,0]) bearing_carrier();
```

A `WARNING: Ignoring unknown variable` line names the cause immediately.

---

## Verified component data

Everything below has a source. **Anything not on this list, treat as unknown** and either find a source or make the design tolerate both answers.

### RMD-L-5005 motor
Source: *RMD-L Series Servo Actuator User Manual Rev 1.01*, §2.1 "RMD-50 SERIES" drawing — mirrored at `github.com/tigakub/RMD-L`. Plus `dingsmotionusa.com/rmd-l-collection/l-5005-motor-characteristics`.

| | |
|---|---|
| Output flange | **4 × M3 on Ø25 bolt circle** |
| Rear mount | **4 × M2.5 on a 20 × 20 mm square** (= Ø28.28 at 45°) |
| Body | Ø49, height **23.9 mm**, mass **92 g** |
| Through-bore | **Ø8.1** ("S" variant) or Ø12.7 ("L") — two different STEP files, assume mechanically distinct |
| Torque | 0.13 N·m rated, 0.42 N·m peak, 1360 rpm, 14-bit encoder |
| Load ratings | **Not published.** No bearing-load section exists in the manual. |

Earlier versions of this design used six output holes on Ø30 and an M4 rear on Ø43. Both were invented. That error alone made every part oversized by ~11%.

### DLH-3UP-EH housing
Source: `ledsupply.com/content/pdf/DLH-3UP-EH-Assembly.pdf` Rev A, and the LEDSupply product page.

| | |
|---|---|
| Clamped diameter | Ø0.99" = **25.15 mm, ±0.38 mm** ← the drawing's own two-place-decimal tolerance |
| Overall length | 1.26" = 32 mm |
| Surface | **Not finned** — "4 small channels around the diameter of the sleeve", i.e. grooves cut in |
| Mass | **0.9 oz = 25.5 g** |
| Rear stub | 1/2"-14 NPT external, 1/8"-27 NPS internal, **1/8" (3.175 mm) wire hole** |
| Optic | Ø20 mm Carclo triple TIR, ~6 mm tall, sits inside, no holder needed for the 3-Up |
| Material | 6061-T6 |

**±0.38 mm on the clamped diameter is the single most important number for the clamp.** A 0.76 mm spread. The clamp must never bottom out — the screws set the grip, not a hard stop.

**The sleeve unscrews from the slug.** Clamping the sleeve does not restrain the slug. Not a load path in this frame, but worth a build note.

**Unverified on that drawing:** it carries dimensions `0.89`, `0.80`, `0.70` and states what none of them measure. `0.89" = 22.6 mm` has been assumed to be the sleeve length (the grip length available) — plausible, unconfirmed. The stub length is *not* `1.26 − 0.89`; the 1-Up sheet gives a different difference for the same stub.

### 608ZZ bearing
8 × 22 × 7 mm, standard. Bore and OD are toleranced to about −0.008 mm / −0.009 mm (normal class). ZZ or 2RS both fine, ABEC rating irrelevant at these speeds.

---

## Defect log — every real defect found across four rounds

Each of these shipped or nearly shipped. They are the rules.

**Fits and tolerances**
- A printed shaft drawn at 7.85 mm to enter an 8.00 mm bearing bore. External cylinders print **over** size — it would have come out ~8.0 and never gone in. Nothing in the file compensated for print error at all.
- Holes drilled horizontally treated the same as vertical ones. A horizontal hole bridges and its roof sags; it needs its own fit class.
- A block drawn exactly as wide as the slot it drops into. The block grows and the slot shrinks — 0.4 mm of interference.
- A clamp whose hard stop closed before it touched a minimum-tolerance barrel. It would have gripped air.
- A bearing pocket at nominal + 0.05, i.e. interference on a steel race.

**Geometry that did nothing, or the wrong thing**
- A wire channel cut entirely inside a bore — it removed no material.
- Two "lightening pockets" whose placement expression collapsed: a no-op on one arm, a sealed void inside the other.
- A lead-in chamfer unioned *inside* the full-diameter shaft it was meant to chamfer.
- A wire hole copied by symmetry to a side no wire passes through.
- A cable route with a 6 mm gap in it and a 3.5 mm-deep tunnel no cable could be laid into.
- Yoke arms rendered 8.7 mm clear of the bridge — not connected to the part at all.

**Interference — none of these were visible in a render**
- The clamp cap's ear standing inside the tilt motor's output boss.
- The same ear inside the motor *again* after the boss went away and the whole Ø49 body became the obstruction.
- The pan motor's side connector standing inside the hard-stop post.
- A base-plate gusset through the pan motor's body.
- A cable trough cut through the root of the hard-stop post.

**Assembly and print direction**
- Bolts with no straight driver path to them — a one-piece ring clamp where the part's own body blocked every approach.
- Fasteners trapped behind a subassembly installed earlier.
- A 30 mm blade of a hard stop printed standing up, loaded across its layers, with no buttress. Layer adhesion is the weakest direction a printed part has, and a hard stop is the one feature that gets hit.
- Clamp ears 2.6 mm thick carrying the full clamp load of an M3.
- A 32 mm circular pocket roof printed as a bridge where a hexagon with a vertex up would have been a self-supporting 60° peak.
- A shaft run at its minimum diameter along its whole length when only the last 9 mm was inside the bearing — the rest an unsupported plastic cantilever with the head hanging off it.

**Process**
- A `module` defined inside an `if` block — parser error.
- A patch that silently didn't apply because of whitespace, leaving a part rendering empty.
- STL centre-of-mass read straight out of a file exported in *print* orientation and interpreted as if it were in model coordinates. Wrong by the transform.

---

## Design rules that came out of it

- **Every number lives in one file.** `frame_params.scad` is `include`d by both the geometry and the assembly, so the assembly view cannot disagree with the parts you print.
- **Every fit is derived, never typed.** Three measured constants — vertical hole shrink, bridged hole shrink, external shaft growth — and fit functions built on them: `free_h`, `free_hx`, `tap_h`, `press_h`, `slip_s`, `loc_h`, `slot_fit`. A `tol_coupon` part measures those three on the user's own printer, and it is printed before anything else.
- **Anything that must be round prints as a vertical hole or a first-layer pocket.** Never as a bridge.
- **Every joint is a bolt you can see.** No captive nuts, nothing friction-fit. Printed-to-motor joints use the motor's own threads; printed-to-printed self-taps into pilot holes.
- **Where a part lands on a rotating boss it lands on the boss and nothing else** — if a boss exists at all. Derive the recess from the boss height so it disappears when the height is zero.
- **Assembly order is a property of the geometry, not a hope.** Every step must leave the next step's fasteners reachable by a straight driver.
- **Balance by construction, not ballast.** Offsetting the tilt axis above the payload's axis costs nothing and puts the head's measured centre of mass on the axis. It deleted a trim bolt and a washer stack.
- **Zero supports, no overhang past 60°.**
- Print orientation is declared per part inside the file — `part="yoke"` emits a slice-ready STL.

---

## Validation — do all of this, not some of it

**Render and look.** Headless: `xvfb-run -a openscad -o out.png -D 'part="x"' --imgsize=W,H --projection=p --colorscheme=Tomorrow --autocenter --viewall --camera=0,0,0,rx,ry,rz,0`. Then actually read the image. Several defects above were visible and went unnoticed because renders were generated but not inspected.

**Boolean interference check.** The single highest-value technique found. Emit `intersection() { partA_positioned(); partB_positioned(); }` to an STL and measure its volume. Zero volume or no file at all means clear; anything else is a collision. Run it for the head vs the yoke at tilt 0 and ±90°, head vs both motors, plate vs motor, carrier vs arm. **This caught three collisions that no render showed.** Note that OpenSCAD writes no file at all when the result is empty — that is the success signal.

**Mass properties.** `trimesh` on exported STLs gives volume and centre of mass. Use it to (a) find where the plastic actually is before deciding what to lighten, and (b) solve for the tilt-axis offset that nulls the head's CoM. **Export in model coordinates for this, not print orientation** — the transform will silently corrupt the answer otherwise.

**Watertightness.** Check every exported STL.

**Sanity-echo the derived chain** and read the numbers. Span, sweep vs drop, web thicknesses where two pockets cross, thread engagement depths.

---

## Repo and push protocol

If you are running with direct git access, just commit and push normally.

If the only write path is the GitHub MCP connector (`git push` fails, no credentials; direct API/curl blocked):

- `push_files` is **text only** — never send base64 or binary.
- One commit per call, full file content each time.
- **Read the final local bytes immediately before pushing.** Never reconstruct a file from memory or from an earlier read.
- Verify after every push: `git show origin/main:$f | diff - $f | wc -l` must be `0`.

Either way, the site must build clean: `python3 -m mkdocs build --strict`, and `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 -m pytest tests/e2e -q` (9 tests).

**Current repo state:** `frame_params.scad` and `frame.scad` are v7 on main. `assembly.scad` is still v6 — it works with the v7 pair but lacks a version banner and draws M4-sized screw graphics on an M2.5 circle. There is a newer `frame_params.scad` than main delivered as a file in the previous session, carrying the housing tolerance work described above; ask me for it.

---

## Docs that need updating when the CAD settles

- `docs/03b-print-the-frame.md` — the frame chapter. Currently describes v6 numbers.
- `docs/03-build-the-gimbal.md` — row 11 of the BoM still reads "683 or 608 bearings". There is no 683 in this design; it's one 608ZZ, and it needs its own row with the rows below renumbered.
- `docs/bom-checklist.md` — already has the 608 as its own line.

---

## Deliverables

- `frame_params.scad`, `frame.scad`, `assembly.scad` — or a better file structure if you can justify one.
- STL for every part, watertight, in print orientation.
- Renders: every part individually, the full parts layout, the assembly assembled / exploded / sectioned / at tilt extremes.
- A short written adversarial review of the old design and of your own new one, with the numbers behind each claim.
- Pushed to the repo once verified.

**Tell me plainly when a number is unverified.** The whole reason this is a rebuild is that a design was shipped on invented dimensions. "Not published, here's how the design tolerates either answer" is a good outcome. A confident wrong number is not.
