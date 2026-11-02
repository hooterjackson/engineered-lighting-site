// =============================================================================
// frame_params.scad · Engineered Lighting — every number the frame is built from
// v8 (2026-07-30)  — ground-up rebuild
// =============================================================================
// BOTH frame.scad and assembly.scad `include` this file. That is the whole
// anti-drift mechanism: there is exactly one copy of every dimension, and the
// assembly view cannot disagree with the parts you print.
//
// PROVENANCE IS PART OF THE DATA. Every number below is tagged:
//
//   [STEP]    measured out of ref/RMD-L-5005-S.STEP by ref/step_dump.py.
//             These are face boundaries in the vendor's own solid model.
//   [MANUAL]  RMD-L Series Servo Actuator User Manual Rev 1.01, section 2.1.
//   [DRAWING] LEDdynamics DLH-3UP-EH assembly drawing Rev A.
//   [STD]     a published standard (thread series, bearing series).
//   [CHOICE]  a design decision of mine. Change it freely.
//   [MEASURE] you must measure it. The design tolerates a range, stated.
//   [UNVERIFIED] nobody publishes it. What the design does about that is
//             written next to it.
//
// v8 deleted the idle side of the tilt axis entirely — no trunnion, no bearing
// carrier, no 608, six fewer screws, one fewer yoke arm. The head cantilevers
// off the tilt motor's own output. The load numbers that justify that are in
// the CANTILEVER LOAD CASE block near the bottom, and they are echoed on every
// render so they cannot quietly stop being true.
// =============================================================================

cad_version = "v8";   // frame.scad and assembly.scad both echo this on load.
                      // If it prints `undef`, your frame_params.scad is not the
                      // one these files were written against — see the note in
                      // docs/03b-print-the-frame.md about stale copies.

// =============================================================================
// MOTOR — MyActuator RMD-L-5005, "S" bore variant
// =============================================================================
// Everything in this block is [STEP] unless marked otherwise, and five of the
// numbers are independently confirmed by [MANUAL]: D49, 23.9 long, 4 x M3 on
// D25, 4 x M2.5 on 20x20, D8.1 bore. That agreement is why the rest is trusted.
// Full write-up, including how it was parsed: ref/RMD-L-5005-S.md
motor_d        = 49;    // [STEP] body OD. Also the max radius ANYWHERE: R24.5.
motor_len      = 23.9;  // [STEP] output face to rear face

// --- the output end (this whole face rotates) -------------------------------
// The output rotor is a separate solid body in the STEP from the housing, and
// the housing does not begin until 3.0 mm back from the output face. So a plate
// laid on the output face turns with it, and has 3 mm of axial room at full D49
// before it touches the stator and clamps the motor solid.
out_flat_od    = 47;    // [STEP] flat annulus OD. Beyond this is the chamfer.
out_flat_id    = 10.1;  // [STEP] ...and its ID, the mouth of the bore chamfer
out_chamfer    = 1;     // [STEP] 45 deg, D47 -> D49 over the first 1.0 mm
stator_x       = 3.0;   // [STEP] ** the stationary housing starts here **
out_bcd        = 25;    // [STEP][MANUAL] output bolt circle
out_bolt_n     = 4;     // [STEP][MANUAL]
out_bolt_d     = 3;     // [STEP][MANUAL] M3 (D2.5 tap drill in the model)
out_bolt_a0    = 45;    // [CHOICE] turn the output so TWO holes clear the head's
                        // split line. At 0 only one does, and the head needs two.
// ** THE SINGLE MOST CONSTRAINING NUMBER IN THE WHOLE DESIGN **
// The tapped holes are 2.5 mm deep and they BREAK THROUGH into the rotor's
// internal cavity at x = 2.5 (the cavity floor is a D17..D42.2 face at exactly
// that plane). A screw longer than the hole does not bottom on metal, it enters
// the motor. Every M3 length in this design is derived from this number.
out_thread_depth = 2.5; // [STEP]
out_thread_use   = 2.3; // [CHOICE] what we actually allow ourselves to use, so
                        // there is 0.2 mm of air under every screw tip.
// If the vendor simplified the thread in the STEP and the real hole is deeper,
// a short screw still works perfectly. The error is one-sided and safe.

// --- there is no boss -------------------------------------------------------
// [STEP] Settled, not guessed: the output face is a flat annulus and it is the
// frontmost plane of the entire motor. Stand-proud is 0.000 mm. The parameter
// survives so that every dependent dimension still DERIVES from it — if you
// ever fit a different actuator that does have a boss, set these two and the
// recess, the mate plane and the span all follow. At 0 they vanish.
out_boss_d     = 0;     // [STEP] no boss exists
out_boss_h     = 0;     // [STEP] 0.000 mm proud
// A quarter of the boss height, capped at 1 mm. Never let this reach out_boss_h:
// a part that bottoms on the STATOR face clamps the motor solid.
boss_recess    = min(1, out_boss_h / 4);

// --- the rear end (this is what you bolt to) --------------------------------
rear_sq        = 20;    // [STEP][MANUAL] the rear mount is a 20 x 20 SQUARE
rear_bolt_n    = 4;     // [STEP][MANUAL]
rear_bolt_d    = 2.5;   // [STEP][MANUAL] M2.5. NOT M4, and NOT on D43.
rear_bolt_a0   = 45;    // ...which as a bolt CIRCLE is rear_sq*sqrt(2) at 45 deg
rear_bcd       = rear_sq * sqrt(2);   // 28.284
rear_thread_depth = 10.7;  // [STEP] x 13.2 -> 23.9. Generous, unlike the front.
// The motor's OWN cover screws: D4.5 heads on a D44 circle, sunk only 0.300 mm
// below the rear face. A flat plate clears them by 0.3 mm — so never put a
// raised pad or spigot on the rear-mating side of a plate near D44.
cover_head_bcd = 44;    // [STEP]
cover_head_d   = 4.5;   // [STEP]
cover_head_sunk = 0.3;  // [STEP] how far below the rear face the heads sit

shaft_bore_d   = 8.1;   // [STEP][MANUAL] "S" variant. The "L" is 12.7 and is a
                        // mechanically different part — do not mix the STEPs.

// --- the connectors ---------------------------------------------------------
// [STEP] Nothing on this motor protrudes past its own barrel: the maximum
// radius of any vertex in the model is exactly R24.5, checked band by band
// along the full 23.9 mm. The connectors are RECESSES cut into the casting,
// the deepest reaching only R23.16.
connector_protrusion = 0;  // [STEP] the motor itself needs no radial clearance
// [UNVERIFIED] BUT the mating cable plug is not in the STEP, and a plug pushed
// into those cavities will stand out, as will the cable's bend radius. Nobody
// publishes that figure. So the design does not assume zero: it keeps a stated
// radial gap at the connector azimuth and tells you to turn the connector into
// it at build time. If your plug is fatter than this, turn the motor, don't
// file the frame.
connector_plug_clear = 8;  // [CHOICE] radial air kept clear outside D49

motor_mass     = 92;    // [MANUAL] g, each

// =============================================================================
// PAYLOAD — LEDdynamics DLH-3UP-EH
// =============================================================================
// [DRAWING] The title block says TWO PLACE DECIMAL +/- .015, and D0.99" is a
// two-place decimal. So the barrel you clamp is 25.15 +/- 0.38 mm — anywhere
// from 24.77 to 25.53. A 0.76 mm spread on the one dimension the clamp depends
// on. That is why the clamp is a screw-set grip and never a hard stop.
payload_od     = 25.15; // [DRAWING] D0.99"
payload_tol    = 0.38;  // [DRAWING] +/-, from the drawing's own tolerance block
payload_len    = 32;    // [DRAWING] 1.26" overall
payload_mass   = 25.5;  // [DRAWING] 0.9 oz
payload_wire_d = 3.175; // [DRAWING] 1/8" centre hole — the wires' real exit
payload_stub_d = 21.3;  // [STD] 1/2"-14 NPT major dia. From the thread standard,
                        // not from LEDdynamics — they publish only the callout.
// [UNVERIFIED] The drawing carries 0.89, 0.80 and 0.70 and states what none of
// them measure. 0.89" = 22.6 mm is the plausible reading of "sleeve length",
// i.e. the grip length available. The design tolerates being wrong about it:
// the saddle is cr_len long and the clamp bears over whatever of it is barrel,
// so a shorter sleeve costs grip length, not fit. Measure yours before relying
// on slide_range.
payload_body   = 22.6;
// [UNVERIFIED] and probably wrong: 1.26" - 0.89" assumes the two dimensions are
// end to end. The 1-Up sheet gives 1.46" - 1.06" = 0.40" for the same stub, so
// the subtraction does not mean what it looks like. Only used to draw the stub
// in the assembly view; no printed feature depends on it.
payload_stub_l = 9.4;
// The sleeve unscrews from the slug it is threaded onto. Nothing here twists
// the housing about its own axis so it is not a load path, but thread-lock it
// before you clamp: a clamp on the sleeve does not restrain the slug.

// bore sized for the LARGEST barrel the drawing allows, plus a slide fit
payload_clear  = 0.2;   // [CHOICE]
bore_d         = payload_od + payload_tol + payload_clear;   // 25.73

// =============================================================================
// PRINT TOLERANCES — measure these with tol_coupon, do not trust my defaults
// =============================================================================
// FDM gets holes and shafts wrong in OPPOSITE directions, which is the whole
// reason this block exists. Print tol_coupon FIRST, find which test hole your M3
// drops through and which test post your parts slide onto, and set these three.
// Every fit in every part is derived from them and nothing is typed in raw.
hole_comp   = 0.25;  // [MEASURE] vertical holes come out this much UNDERSIZE
hole_comp_h = 0.40;  // [MEASURE] horizontal holes come out worse — the roof sags
shaft_comp  = 0.15;  // [MEASURE] external cylinders come out this much OVERSIZE

function free_h(nom)  = nom + 0.5 + hole_comp;     // bolt drops through, vertical
function free_hx(nom) = nom + 0.5 + hole_comp_h;   // ...drilled horizontally
function tap_h(nom)   = nom - 0.45 + hole_comp;    // self-taps into PETG
function tap_hx(nom)  = nom - 0.45 + hole_comp_h;
function loc_h(nom)   = nom + 0.70 + hole_comp;    // recess you seat by hand
// a printed BLOCK dropping into a printed SLOT loses both errors at once — the
// block grows and the slot shrinks — so the nominal has to give up both
function slot_fit(nom) = nom - 0.30 - shaft_comp - hole_comp;

/* [Hardware — every fit derived, nothing hardcoded] */
m25_clear = free_h(2.5); m25_clear_x = free_hx(2.5); m25_head_d = 4.9;
m3_clear  = free_h(3);   m3_clear_x  = free_hx(3);   m3_head_d  = 6.4;
m3_pilot  = tap_h(3);    m3_pilot_x  = tap_hx(3);
m3_head_h = 3.0;         m25_head_h  = 2.5;          // [STD] socket cap heads

// screw lengths that CANNOT bottom out in the motor, derived not chosen
function out_screw_len(through) = through + out_thread_use;

// =============================================================================
// FRAME — thicknesses
// =============================================================================
t_plate  = 7;     // [CHOICE] base plate
t_bridge = 8;     // [CHOICE] yoke bridge. With out_thread_use this makes the
                  // pan screws M3 x 10.3 -> buy M3 x 10.
t_arm    = 10;    // [CHOICE] the single yoke arm
cr_wall  = 8;     // [CHOICE] cradle's motor-side plate. Also -> M3 x 10.

// =============================================================================
// FRAME — the head
// =============================================================================
cr_len   = 32;    // [CHOICE] saddle length along the housing axis
base_z   = 16;    // [CHOICE] how far the saddle reaches below the split line
plate_z  = 16;    // [CHOICE] how far the motor-side plate rises above the split
                  // line. Every mm here is mass ABOVE the tilt axis, so it is as
                  // small as it can be — but it MUST reach the highest bolt a
                  // driver can get to, plus that bolt's head. That is
                  // bolt_pad_z (13.54, measured from the TILT axis) + axis_z
                  // (the split line sits axis_z below the tilt axis) = 15.28.
                  // 14 was not enough and the assert in frame.scad now says so.
cap_z    = 20;    // [CHOICE] cap's outer height
cap_bolt_y = 11;  // [CHOICE] cap-screw spacing along the housing axis
cap_ear_d  = 9;   // [CHOICE] ear pad diameter
cap_ear_t  = 4.5; // [CHOICE] ear thickness. 2.6 mm was a real defect: an M3
                  // head is D6.4 and pulls the ear in bending.
cap_pocket = 6;   // [CHOICE] lightening pocket in the crown, prints first-layer
pilot_len  = 9;   // [CHOICE] cap-screw thread depth in the saddle

// THE CLAMP MUST NEVER BOTTOM OUT. With a small nip and a bore cut for the
// housing's MAXIMUM diameter, a minimum-tolerance barrel needs the cap to
// travel further than the nip before it even touches — so the ears land on the
// plates and the screws clamp air. The gap is larger than the worst-case slop
// by construction, which means the SCREWS set the grip and any barrel inside
// the drawing's tolerance is actually held.
clamp_gap  = payload_tol / 2 + 0.5 + payload_clear / 2;   // 0.79
clamp_nip  = clamp_gap;

// THE TILT AXIS does not pass through the housing's axis: it sits axis_z ABOVE
// it, so the head's own centre of mass — saddle, cap, housing and all — lands
// ON the axis. The tilt motor then holds any angle with no static torque, and
// because the head's CoM does not move as it tilts, the whole machine's balance
// is independent of tilt angle too.
//
//   axis_z = Mp*zp / (Mp + Mh), Mp = printed head mass, zp = its CoM height
//   above the bore, Mh = payload mass.
//
// MEASURED off the exported STLs in MODEL coordinates by tools/meshcheck.py —
// never off a print-orientation export, which is a transform away and silently
// wrong. Re-solve with tools/solve_balance.py after any change to the head; the
// echo in frame.scad prints the residual so a stale value shows up rather than
// being assumed still true.
//
// DEFINED HERE, ABOVE head_sweep, ON PURPOSE. OpenSCAD assigns file-scope
// variables in source order and a forward reference evaluates to undef — it
// does not hoist. head_sweep uses axis_z, and with axis_z below it head_sweep
// silently became undef, which then propagated into drop's clearance check.
// Caught by echoing the derived chain; that is what the echo is for.
// Solved from the measured parts: printed head 44.197 g with its CoM 2.7598 mm
// above the split line, payload 25.500 g sitting on it.
//   axis_z = 44.197 * 2.7598 / (44.197 + 25.500) = 1.7501
// Residual as built: +0.0101 mm, i.e. 6.9e-06 N.m of standing tilt torque.
axis_z   = 1.75;  // [MEASURE] tools/solve_balance.py

// =============================================================================
// FRAME — the yoke
// =============================================================================
drop      = 32;   // [CHOICE] bridge underside -> tilt axis. Asserted > head_sweep.
arm_w     = 34;   // [CHOICE] arm width in Y. Must cover the rear bolt square
                  // (20 mm) plus head seats plus meat.
arm_pocket_d = 22; // [CHOICE] hex lightening pocket, VERTEX UP so its roof is a
                   // 60 deg self-supporting peak and never a bridge
arm_pocket_z = 4;  // [CHOICE] depth, of t_arm. Leaves a 6 mm web.

/* [Frame — the pan hard stop]
   v7 put a post on the base plate into an ARC GROOVE cut in the bridge's face.
   That groove is 1565 mm2 of flat roof with 45.65 mm unsupported runs, printed
   over a designed 0.600 mm post clearance. PETG will not hold that, and the sag
   lands on the post's tip. Cutting the groove through instead would very nearly
   detach the bridge's outer rim.

   So v8 has NO GROOVE AT ALL. A post hanging off the base plate and a radial
   LUG on the bridge's rim simply collide. Both are open on every side, so
   nothing bridges anything and the defect class disappears rather than being
   mitigated.

   The post lives entirely OUTSIDE the bridge disc so it cannot foul the rim as
   the yoke turns, and it stops short in Z before it reaches the arm. Both are
   asserted in frame.scad and checked by boolean in checks.scad. */
stop_post_d  = 8;    // [CHOICE] post diameter. Its RADIUS is derived below from
                     // bridge_r, so the post cannot end up fouling the rim.
stop_lug_w   = 12;   // [CHOICE] lug width, tangential
stop_post_a  = 0;    // [CHOICE] post azimuth. Kept AWAY from the cable trough at
                     // 270 deg — a trough cut through the root of this post is
                     // in the defect log.
stop_lug_a   = 180;  // [CHOICE] the LUG sits opposite the post, so pan = 0 is
                     // MID-TRAVEL and the machine reaches the stop at about
                     // +/-165 deg. With both at the same azimuth, pan = 0 IS
                     // the stop: the assembly view opens in collision and half
                     // the travel is on the wrong side of it.
stop_engage  = 4;    // [CHOICE] how far the post reaches into the bridge's
                     // thickness. Must stop above the arm: asserted.

/* [Frame — cable management] */
trough_w  = 7;    // [CHOICE] one channel size, used everywhere
trough_d  = 3;    // [CHOICE] t_bridge - stop_deep - trough_d = 2 mm web
wire_hole_d = 12; // [CHOICE] through both hollow shafts and both plates

/* [Frame — the base plate] */
tongue_len = 56;  // [CHOICE] how far the C-clamp tongue reaches aft
tongue_w   = 44;  // [CHOICE]

// =============================================================================
// DERIVED — the single chain that sets the whole machine's size
// =============================================================================
// which output holes sit ABOVE the split line: the only ones a driver reaches
function out_bolt_z(i) = out_bcd / 2 * cos(out_bolt_a0 + i * 360 / out_bolt_n);
function out_bolt_y(i) = out_bcd / 2 * sin(out_bolt_a0 + i * 360 / out_bolt_n);
function out_bolt_up(i) = out_bolt_z(i) > 2;

// The saddle's half-width. v7 used bore_d/2 + 2, which works only because v7's
// head had TWO side plates for the cap's ears to land on. With one plate the
// clamp screws have to pass through the SADDLE itself, beside the bore, so the
// shoulder has to be wide enough for an M3 and its walls:
//   m3_clear/2 (1.875) + wall (2.5) = 4.375 minimum. 8 gives a real wall.
cr_shoulder = 8;                          // [CHOICE] material each side of bore
blk_in  = bore_d / 2 + cr_shoulder;       // 20.865
// clamp screws: outboard of the bore, inboard of the saddle's edge
cap_bolt_x = blk_in - cap_ear_d / 2 - 0.5;
keel_chamf = 8;                           // [CHOICE] dead-corner chamfer, keel
tie_clear  = 1.2;                         // [CHOICE] tie slot to trough wall.
                                          // v7's 0.150 mm sliver was discarded
                                          // by the slicer and the slot merged
                                          // into the channel.
arm_pad_r  = rear_bcd / 2 + m25_head_d / 2 + 3;   // meat around the rear circle
x_mate  = cr_wall - boss_recess;          // plate thickness that actually stands
                                          // off the motor's face (recess eats in)

// The head hangs off the tilt motor's output. Along the tilt axis (X):
//   arm inner face .. motor .. output face .. cradle plate .. saddle
// arm_reach is solved in the BALANCE block below.
//
// MIND THE AXES. The tilt axis is X. The payload's own axis is Y, because the
// beam fires +Y — so cr_len (32) is the saddle's length along the BARREL, i.e.
// along Y, and the saddle's width along the tilt axis is 2*blk_in. The
// cantilever arm out to the head's centre is therefore cr_wall + blk_in, NOT
// cr_wall + cr_len/2. Getting that wrong overstates the overhung moment by 4%
// and, worse, puts the balance solve on the wrong axis.
head_len   = cr_wall + 2 * blk_in;        // cradle's full length along X (tilt)
head_cog_x = cr_wall + blk_in;            // head centre from the OUTPUT FACE —
                                          // the cantilever arm. Refined by
                                          // measurement in tools/solve_balance.py
// The cap is a plain block spanning the saddle, NOT a body-with-ears dropping
// between two plates. With one side plate there is nothing for an ear to land
// on, and a plain block puts ~19 mm of material under every screw head instead
// of an ear — v7's ears were 2.6 mm and that is in the defect log. It also
// removes the slot-fit problem entirely: nothing drops into anything.
// 1 mm narrower than the saddle so it cannot touch the motor-side plate.
cap_w   = 2 * blk_in - 1;
cap_clear_plate = (2 * blk_in - cap_w) / 2;   // gap to the plate: 0.5 mm

// how far the plate must reach above the tilt axis: to the highest bolt a
// driver can reach, plus its head and a little meat
bolt_pad_z = max([for (i = [0 : out_bolt_n - 1]) if (out_bolt_up(i)) out_bolt_z(i)])
             + m3_head_d / 2 + 1.5;

// the farthest corner of the head from the tilt axis — what `drop` must clear
head_sweep = max(sqrt(pow(cr_len / 2, 2) + pow(cap_z - axis_z, 2)),
                 sqrt(pow(cr_len / 2, 2) + pow(base_z + axis_z, 2)));
slide_range = cr_len - payload_body;      // grip is on the SLEEVE only

// =============================================================================
// BALANCE BY CONSTRUCTION — two axes, no ballast, no trim bolt
// =============================================================================
// 1. THE TILT AXIS — axis_z, defined further up next to the clamp because
//    head_sweep depends on it and OpenSCAD does not hoist. See the note there.
//
// 2. THE PAN AXIS IS DELIBERATELY *NOT* BALANCED, and it took measuring the
//    thing to see why. With one arm the hanging group's CoM sits +6.267 mm off
//    the pan axis (208.7 g: yoke, tilt motor, head, payload).
//
//    THE PAN AXIS IS VERTICAL AND GRAVITY IS PARALLEL TO IT. An offset along X
//    therefore produces NO TORQUE ABOUT THE PAN AXIS AT ALL — the motor holds
//    any heading on zero current no matter what this number is. All the offset
//    does is load the output bearing with 0.0128 N.m.
//
//    Nulling it would mean pushing the arm out until the head sat over the pan
//    axis: about 7 mm more reach, a bigger bridge disc, ~12 g, to delete a
//    0.0128 N.m moment on a journal 46.6 mm across. Bad trade. So arm_reach is
//    set by clearance and compactness instead, and the residual is reported by
//    tools/solve_balance.py rather than engineered away.
//
//    (The TILT axis is the opposite case and IS nulled — gravity is
//    perpendicular to it, so an offset there is a standing torque the motor
//    holds all day. That is what axis_z is for.)
//
//    What actually sets arm_reach: the arm's inner face has to clear the pan
//    output bolt heads on the bridge above it (12.5 + 3.2 = 15.7), and every
//    extra millimetre grows arm_root_r and therefore the whole bridge disc.
//    So it is near the minimum that leaves the bridge's own bolts drivable.
arm_reach = 18.4; // [CHOICE] pan axis -> arm's INNER face

// positions along X, all derived from arm_reach
arm_in   = -arm_reach;                    // arm's inner face (motor bolts here)
arm_out  = -arm_reach - t_arm;            // arm's outer face
out_face_x = arm_in + motor_len;          // the tilt motor's output face
bore_x   = out_face_x + head_cog_x;       // payload centre along X (the tilt axis)
z_tilt   = -t_bridge - drop;              // tilt axis, below the bridge underside

// The bridge is a DISC, only as big as it needs to be: it must cover the pan
// output bolt circle and the root of the arm. The arm's neck is arm_neck_w wide
// where it meets the bridge, so the far corner of that root sits at
// hypot(|arm_out|, arm_neck_w/2). Derived, so narrowing the neck shrinks the
// bridge automatically instead of leaving a disc sized for a shape that changed.
arm_neck_w = 20;                          // [CHOICE] arm width in Y at the bridge
arm_root_r = sqrt(pow(-arm_out, 2) + pow(arm_neck_w / 2, 2));
bridge_r   = max(out_bcd / 2 + m3_head_d / 2 + 4, arm_root_r + 2);

// The hard stop. The post must clear the bridge disc at every heading, so its
// INNER edge sits outside bridge_r with a stated gap — that is what stops it
// fouling the rim, and it is asserted rather than eyeballed.
stop_gap    = 2;                          // [CHOICE] post inner edge to bridge rim
stop_post_r = bridge_r + stop_gap + stop_post_d / 2;   // post centreline radius
stop_lug_r  = stop_post_r + stop_post_d / 2 + 1;       // lug reaches past the post
post_h      = motor_len + stop_engage;    // plate underside -> into the bridge
butt_h      = post_h - 4;                 // buttress stops short of the tip

// usable pan travel, after both obstructions — echoed so it is never a guess
stop_block_deg = 2 * asin(stop_post_d / 2 / stop_post_r)
               + 2 * asin(stop_lug_w / 2 / stop_post_r);
pan_travel_deg = 360 - stop_block_deg;

// The base plate's hub. Big enough for the rear bolt circle and its heads, but
// also at least as big as the motor it backs — a hub smaller than the motor
// leaves the D44 cover-screw heads hanging over the plate's edge and gives the
// rear face nothing to bear on around its rim.
hub_r    = max(rear_bcd / 2 + m25_head_d / 2 + 4, motor_d / 2 + 1);

// =============================================================================
// CANTILEVER LOAD CASE — what deleting the idle side actually asks of the motor
// =============================================================================
// v8 removed the trunnion, the bearing carrier, the 608 and the second yoke arm:
// 62 g of a 177 g machine, three printed parts, one bought part, six screws.
// The head now cantilevers off the tilt motor's own output bearing. These are
// the numbers that justified that, echoed on every render so that if the head
// ever grows, the change is visible instead of silent.
//
// [UNVERIFIED, and it is the one that matters] The RMD-L manual has no
// bearing-load section at all. There is no published radial or moment rating
// for this output. So this is an argument from load magnitude and from the
// journal diameter, NOT from a datasheet:
//   · [STEP] the rotor is journalled at D46.6 (its spigot at x 3.0..5.0 runs in
//     the housing's D46.6 bore). Moment capacity scales with that diameter.
//   · the demand below is ~3% of the motor's own peak torque.
// If a rating ever surfaces, check it against these two numbers.
g_accel   = 9.81;
head_mass_est = 26;   // [MEASURE] printed head, g — meshcheck reports the truth
head_load_N   = (head_mass_est + payload_mass) / 1000 * g_accel;
head_moment_Nm = head_load_N * head_cog_x / 1000;
motor_peak_Nm  = 0.42;   // [MANUAL]
// prying on the output bolts: the moment reacted across the D25 bolt circle
bolt_pry_N    = head_moment_Nm / (out_bcd / 1000);
