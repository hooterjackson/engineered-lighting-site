# Prompt · Build out the frame chapter (Doc 3b)

*Paste into Claude Code in plan mode from this repo. Run AFTER the motor-swap
prompt (it assumes the RMD-L-5005 is the motor of record).*

Build out the frame-design portion of the gimbal build into a proper chapter.
Read Doc 3 stage 7 and the AI-workflow page first. Plan, then execute.

CREATE a new page "3b · Print the Frame" (filename to slot after Doc 3 in
nav, e.g. 03b-print-the-frame.md). Doc 3 stage 7 shrinks to a summary +
link ("the full frame chapter, with code and print settings → 3b").
Context now fixed: motor = RMD-L-5005 (Ø49 × ~24 mm, 92 g, output flange
per MyActuator's L-series 2D drawing); printer = Bambu Lab X1C; materials
= PETG Basic or PETG-CF.

CONTENTS:
1. The three parts, specified: pan base (clamp ear for a C-clamp, motor-
   body bolt pattern, pan hard-stop post), yoke (U-bracket on the pan
   output flange; one arm carries the tilt motor body, other arm a 683/608
   bearing pocket; tilt hard-stop tabs; service-loop zip-tie points), head
   shell (flashlight bore on the tilt flange, counterweight slot sized for
   an M5 bolt + stacked nuts, CoM on the tilt axis). Explain WHY each
   feature exists in one line each (hard stops ← single-turn encoder;
   counterweight ← silence via balance; loop points ← Doc 3 wiring rule).
2. A parametric OpenSCAD scaffold, shipped in the repo (assets or a
   /cad/ dir) AND shown in the page: a parameters block at top —
   flange_bolt_circle_d, flange_bolt_d, flange_center_bore_d, body_d=49,
   body_len≈24, connector_clearance, flashlight_d, arm_offset — with
   placeholder values clearly marked MEASURE-ME, one module per part,
   $fn sensible. Pull nominal values from MyActuator's L-5005 2D drawing
   where readable; every drawing-derived number gets a "verify with
   calipers on arrival" comment. Include a 4th module: fit_coupon() —
   a 3 mm-thick ring matching the flange bolt pattern + center bore, to
   print first in ~5 min and bolt on before any real part prints.
3. X1C print settings per part: material (PETG Basic default; PETG-CF for
   the yoke if on hand), 4 walls / 40% gyroid / 0.2 mm, orientation
   (pan base flat; yoke printed with arms UP so layer lines don't shear
   at the arm roots — explain the layer-line-strength reasoning in one
   sentence; head shell bore vertical), brim on the yoke, no supports if
   the yoke arms are designed with ≤45° transitions (design them so).
4. Build order with done-whens: print coupon → bolts thread + flange
   seats flush → pan base → motor mounts, clamp holds → yoke on pan
   flange → tilt motor in arm, spins free by hand at the bearing end →
   head shell → balance check from Doc 3 stage 7 (powered-off head stays
   posed). Iteration framing: 2–3 reprints is the normal path, parts are
   ~20-min prints.
5. The 🤖 agent prompt (site's standard admonition), covering the real
   loop: "Here are my caliper measurements: [list]. Update the parameters
   in frame.scad, render STLs, and tell me which part to print first. After
   each test fit I'll report what's tight/loose — adjust and re-render."
   Plus the escape hatch line: hand-drilled aluminum bar/plywood using a
   1:1 printed drawing is a legitimate v0 if printing stalls.
6. BoM delta: add calipers ($10–20, digital) to Doc 3's BoM + checklist if
   not present; note X1C owner needs nothing else new.

VERIFY: the .scad renders without errors in openscad CLI (add to CI if
cheap); page passes the add-a-doc nav test; Doc 3 stage 7 links resolve;
budget totals untouched except the calipers line (propagate per the
established budget-audit rule).
