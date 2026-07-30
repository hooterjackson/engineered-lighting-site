// =============================================================================
// frame_params.scad · Engineered Lighting — every number the frame is built from
// v7 (2026-07-30)
// =============================================================================
// BOTH frame.scad and assembly.scad `include` this file. That is the whole
// anti-drift mechanism: there is exactly one copy of every dimension, and the
// assembly view cannot disagree with the parts you print.
//
// Anything marked MEASURE-ME came off a drawing, not off calipers. fit_coupon
// checks every one of them for 3 g of PETG before a real part is printed — and
// tol_coupon comes before even that, because the fit functions further down are
// only as good as the three numbers you feed them.
// =============================================================================

cad_version = "v7";   // all three files echo this. If the three numbers below
                      // do not match on load, you have a mismatched set of files
                      // and that is why half the assembly is missing.

/* [Motor interface — RMD-L-5005]
   Read off the RMD-L Series Servo Actuator User Manual Rev 1.01, section 2.1,
   "RMD-50 SERIES" drawing — not off a guess. An earlier version of this file had
   six output holes on a 30 mm circle and an M4 rear mount; the motor has four
   M3 on 25, and the rear is M2.5. Everything downstream was oversized to suit.
   The two numbers the manual does NOT publish are still marked MEASURE-ME, and
   the design is built to tolerate either answer for them. */
motor_d      = 49;    // body OD — manual
motor_len    = 23.9;  // rear face to front face — manual, "5005(23.9mm)"
out_bcd      = 25;    // output-flange bolt circle — manual, 4 x M3
out_bolt_n   = 4;     // manual
out_bolt_d   = 3;     // M3 — manual
out_bolt_a0  = 45;    // turn the boss to suit: at 45 deg TWO holes clear the split
                      // line. At 0 only one does, and the head needs two.
rear_sq      = 20;    // REAR mount is a 20 x 20 SQUARE, not a circle — manual
rear_bolt_n  = 4;     // manual, 4 x M2.5
rear_bolt_d  = 2.5;   // M2.5 — manual. This is the whole machine's load path.
rear_bolt_a0 = 45;    // ...which as a bolt CIRCLE is rear_sq*sqrt(2) at 45 deg
rear_bcd     = rear_sq * sqrt(2);   // 28.28 — the square, expressed as a circle
shaft_bore_d = 8.1;   // 8.1 on the "S" bore variant, 12.7 on the "L" — Dings

/* [Motor interface — the two the manual does not give you. MEASURE-ME.] */
// The manual's front view is a flat Ø49 face with the bore and the four M3. No
// boss or spigot is drawn or dimensioned anywhere in it. So: measure yours.
//   · If a rotating boss stands proud, put its OD and height here and the
//     printed part lands on it and nothing else, which is what you want.
//   · If the front face is flat, leave out_boss_h at 0. The part then lands
//     flat on the face — fine IF the whole front face rotates, which is the
//     usual arrangement on a pancake actuator, and a disaster if it doesn't.
//     fit_coupon's scribe rings are how you find out, for 3 g of PETG.
out_boss_d   = 36;    // MEASURE-ME  rotating output boss OD (unused if h = 0)
out_boss_h   = 0;     // MEASURE-ME  how far it stands proud. 0 = flat face.

/* [Payload — DLH-3UP-EH, off LEDdynamics' own assembly drawing
   (ledsupply.com/content/pdf/DLH-3UP-EH-Assembly.pdf, Rev A) and spec table]

   Two things on that drawing changed this design, and both were things I had
   wrong before:

   1. THE TITLE BLOCK SAYS "TWO PLACE DECIMAL ± .015". The Ø0.99" is a two-place
      decimal, so the diameter you are clamping is 25.15 ± 0.38 mm — anywhere
      from 24.77 to 25.53. That is a 0.76 mm spread on the one dimension the
      whole clamp depends on, and it is why clamp_gap below is what it is.
   2. IT IS NOT FINNED. The product page says "4 small channels around the
      diameter of the sleeve" — grooves cut in, not rings standing out. So the
      clamp bears on a smooth cylindrical land interrupted four times, which is
      better for grip than fin crests, and means payload_od is a real diameter
      rather than a crest-to-crest figure.

   The barrel you grip is the SLEEVE, and the sleeve unscrews from the slug it
   is threaded onto. Nothing in this frame twists the housing about its own
   axis, so that is not a load path — but thread-lock it anyway before you
   clamp it, because a clamp on the sleeve does not hold the slug. */
payload_od     = 25.15; // Ø0.99" — the clamped diameter, and see the tolerance
payload_tol    = 0.38;  // ±, from the drawing's own two-place-decimal block
payload_len    = 32;    // 1.26" overall
payload_body   = 22.6;  // 0.89" on the drawing. UNVERIFIED: the drawing carries
                        // 0.89, 0.80 and 0.70 and states what none of them
                        // measure. This is the plausible reading — sleeve length
                        // — but measure yours before trusting the grip length.
payload_stub_d = 21.3;  // 1/2"-14 NPT major dia, from the thread standard, not
                        // from LEDdynamics — they publish only the thread spec
payload_stub_l = 9.4;   // UNVERIFIED, and probably wrong: this is 1.26" - 0.89",
                        // but the 1-Up sheet gives 1.46" - 1.06" = 0.40" for the
                        // same stub, so the subtraction does not mean this.
payload_wire_d = 3.175; // 1/8" centre hole — the wires' actual exit
// bore sized for the LARGEST the housing is allowed to be, plus a slide fit
payload_clear  = 0.2;
bore_d_calc    = payload_od + payload_tol + payload_clear;   // 25.73

/* [Frame — thicknesses] */
t_plate  = 7;     // base plate
t_bridge = 8;     // yoke bridge
t_arm    = 10;    // yoke arms
cr_wall  = 8;     // cradle side plates

/* [Frame — the head] */
// The tilt axis does NOT pass through the housing's axis: it sits a hair above
// it, so that the head's own centre of mass — cap, saddle, housing and all —
// lands ON the axis. Measured, not guessed: the printed parts were exported and
// weighed in software, giving 41.5 g of plastic whose CoM is 2.97 mm above the
// bore, against a housing of 25.5 g (LEDSupply publish 0.9 oz) sitting on it. Solve
// has to be and you get the number below. It costs nothing — an offset is free —
// and it is why there is no trim-washer bolt in this design any more.
// Residual over a 18-32 g housing: under 0.2 mm, i.e. under 0.1 mN.m.
axis_z   = 1.74;  // = Mp*zp / (Mp + Mh), Mh = 25.5 g published
cr_len   = 32;    // cradle length along the housing axis
plate_z  = 16;    // side plates rise this far ABOVE the split line. Only as far
                  // as the highest reachable output bolt needs — every mm here
                  // is mass ABOVE the tilt axis, and it thins the cap's ear.
base_z   = 16;    // ...and the saddle reaches this far below it
cap_z    = 22;    // cap's outer height — set by the ear, not the bore: the ear
                  // is cap_z - plate_z - clamp_nip thick and an M3 pulls on it
// THE CLAMP MUST NEVER BOTTOM OUT. This was a real defect: with a 0.4 mm nip and
// a bore cut for the housing's max diameter, a min-tolerance barrel needs the cap
// to travel 0.49 mm before it even touches — so the ears would land on the plates
// and the screws would clamp air. The gap is now larger than the worst-case slop
// by construction, which means the SCREWS set the grip, not a hard stop, and any
// barrel inside the drawing's tolerance is held.
clamp_gap  = payload_tol / 2 + 0.5 + payload_clear / 2;   // 0.79
clamp_nip  = clamp_gap;   // the cap's bore sits this low
cap_bolt_y = 11;  // cap-screw spacing along the housing axis
cap_ear_d  = 9;   // ear pad dia. cap_bolt_x below keeps its outer edge inboard
                  // of the motor's face plane, which is what actually matters.
cap_pocket = 6;   // lightening pocket in the cap's crown (prints first-layer).
                  // Every gram taken off here is a gram taken off ABOVE the axis.
pilot_len  = 10;  // cap-screw thread depth in the plate. Must stop short of
                  // the trunnion's bolt ring at z = 0.
keel_chamf = 9;   // dead-corner chamfer under the saddle

/* [Frame — the yoke] */
drop      = 32;   // bridge underside -> tilt axis. Must clear head_sweep.
arm_neck  = 30;   // arm width where it meets the bridge
// hex lightening pocket. Max radius must stay INSIDE the rear bolts' head
// seats: heads start at rear_bcd/2 - m25_head_d/2 = 11.7, so 22/2 = 11 clears.
arm_pocket_d = 22; // vertex up, so the roof is a 60 deg peak, not a bridge
arm_pocket_z = 4;  // ...and how deep (of t_arm). Leaves a 6 mm web.
// locating recess: a quarter of the boss's height, capped at 1 mm, and it
// disappears entirely on a flat-faced motor. Never let this reach out_boss_h —
// a part that bottoms on the STATOR face clamps the motor solid.
boss_recess = min(1, out_boss_h / 4);

/* [Frame — the pan hard stop] */
stop_r    = 31;   // post and groove centreline radius
stop_w    = 8.4;  // groove width, radial
stop_deep = 3;    // groove depth. The cable trough cuts 3 from the other side,
                  // so this number and trough_d must sum to less than t_bridge.
stop_arc  = 345;  // groove sweep -> ~307 deg of usable travel
post_w    = 20;   // post width, tangential

/* [Frame — cable management] */
trough_w  = 7;    // one channel size, used everywhere
trough_d  = 3;    // shallow on purpose: t_bridge - stop_deep - trough_d = 2 mm web
wire_hole_d = 12; // through both hollow shafts and both plates

/* [Print tolerances — MEASURE these with tol_coupon, don't trust the defaults] */
// FDM gets holes and shafts wrong in OPPOSITE directions, which is the whole
// reason this block exists. Print tol_coupon, find which test hole your M3 drops
// through and which test post your 608 slides onto, and set these two numbers.
// Every fit in every part is derived from them.
hole_comp   = 0.25;  // vertical holes come out this much UNDERSIZE
hole_comp_h = 0.40;  // horizontal holes come out worse — the roof sags
shaft_comp  = 0.15;  // external cylinders come out this much OVERSIZE

function free_h(nom)  = nom + 0.5 + hole_comp;     // bolt drops through, vertical
function free_hx(nom) = nom + 0.5 + hole_comp_h;   // ...drilled horizontally
function tap_h(nom)   = nom - 0.45 + hole_comp;    // self-taps into PETG
function tap_hx(nom)  = nom - 0.45 + hole_comp_h;
function press_h(nom) = nom + 0.10 + hole_comp;    // light press — a bearing OD
function slip_s(nom)  = nom - 0.15 - shaft_comp;   // shaft that must TURN in a bore
function loc_h(nom)   = nom + 0.70 + hole_comp;    // recess you seat by hand
// a printed BLOCK that has to drop into a printed SLOT loses both errors at
// once — the block grows, the slot shrinks — so the nominal has to give up both
function slot_fit(nom) = nom - 0.30 - shaft_comp - hole_comp;

/* [Hardware — every fit derived, nothing hardcoded] */
m25_clear = free_h(2.5); m25_clear_x = free_hx(2.5); m25_head_d = 4.9;
m3_clear = free_h(3);  m3_clear_x = free_hx(3);  m3_head_d = 6.4;
m3_pilot = tap_h(3);   m3_pilot_x = tap_hx(3);
m4_clear = free_h(4);  m4_clear_x = free_hx(4);  m4_head_d = 8.4;
bearing_od = 22; bearing_id = 8; bearing_w = 7;
bearing_pocket_d = press_h(bearing_od);
stub_d           = slip_s(bearing_id);
carrier_d = 40;  carrier_t = 9;  carrier_bcd = 30;
trun_flange_d = 26; trun_bcd = 18; trun_t = 6; trun_gap = 4;

// =============================================================================
// derived — the single chain that sets the whole machine's size
// =============================================================================
bore_d  = bore_d_calc;                       // 25.73 — sized for max material
blk_in  = bore_d / 2 + 2;                    // 2 mm shoulder each side of the bore
arm_pad_d = rear_bcd + m25_head_d + 8;       // pad only as big as the rear circle needs
x_left  = -(blk_in + cr_wall);               // outer face of the motor-side plate
x_mate  = x_left + boss_recess;              // ...the plane that lands on the boss
x_right =   blk_in + cr_wall;                // face the trunnion bolts to

span_h  = (motor_len + out_boss_h - x_mate + x_right + trun_t + trun_gap) / 2;
arm_x   = span_h + t_arm / 2;
arm_out = span_h + t_arm;
bore_x  = -span_h + motor_len + out_boss_h - x_mate;
z_tilt  = -t_bridge - drop;
arm_h   = drop + arm_pad_d / 2;
bridge_r = stop_r + stop_w / 2 + 2.5;        // the bridge is a DISC, not a slab
post_h  = motor_len + out_boss_h - boss_recess + stop_deep - 0.6;  // 0.6 off the floor
butt_h  = motor_len + out_boss_h - boss_recess - 3;  // buttress stops 3 mm above
                                                     // the bridge's top face
// the trunnion is a stepped shaft: fat where it is just spanning air and plate,
// thin only where it is actually inside the 608's bore
stub_len   = t_arm + carrier_t + trun_gap + 0.9;   // flange face to stub tip
shank_d    = 14;                                   // fat section OD
brg_face   = trun_gap + t_arm + carrier_t - bearing_w - 0.3;  // where the bore starts
shank_len  = brg_face - 1;                         // stop 1 mm short of it
journal_len = stub_len - shank_len;                // ...the rest is Ø stub_d
boss_locate_d = loc_h(out_boss_d);
cap_w   = slot_fit(2 * blk_in);              // cap body drops between the plates
// Centred in the plate — UNLESS that would push the ear past the plane the motor
// mates on, in which case the motor wins. On a flat-faced motor the whole Ø49
// body sits against x_left, so anything of the cap that crosses x_left is inside
// the motor. This is the third time that corner has bitten; deriving it means it
// cannot bite again whatever out_boss_h turns out to be.
cap_bolt_x = min(blk_in + cr_wall / 2, -x_left - cap_ear_d / 2 - 0.6);

// how far the plate has to reach above the tilt axis: to the highest bolt the
// driver can actually get to, plus its head and a little meat. With four holes
// at 45 deg that is 8.84 + 3.2 + 1.5 = 13.5, which plate_z now covers outright —
// so the local pad that v6 needed is gone, one whole feature deleted.
bolt_pad_z = max([for (i = [0 : out_bolt_n - 1]) if (out_bolt_up(i)) out_bolt_z(i)])
             + m3_head_d / 2 + 1.5;

// what has to clear what — the farthest corner of the head from the tilt axis
head_sweep = max(sqrt(pow(cr_len / 2, 2) + pow(cap_z - axis_z, 2)),
                 sqrt(pow(cr_len / 2, 2) + pow(base_z + axis_z, 2)));
slide_range = cr_len - payload_body;         // grip is on the SLEEVE only

// which output-flange holes sit ABOVE the split line: the only ones a driver can
// reach, which is why the boss gets turned one hole "up" before you bolt it
function out_bolt_z(i) = out_bcd / 2 * cos(out_bolt_a0 + i * 360 / out_bolt_n);
function out_bolt_up(i) = out_bolt_z(i) > 2;
