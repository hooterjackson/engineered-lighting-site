// =============================================================================
// frame_params.scad · Engineered Lighting — every number the frame is built from
// v6 (2026-07-30)
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

/* [Motor interface — MEASURE-ME] */
motor_d      = 49;    // body OD — drawing
motor_len    = 24;    // rear face to front face — drawing
out_boss_d   = 36;    // MEASURE-ME  rotating output boss OD
out_boss_h   = 4;     // MEASURE-ME  how far the boss stands proud of the front face
out_bcd      = 30;    // MEASURE-ME  output-flange bolt circle
out_bolt_n   = 6;     // MEASURE-ME  how many holes in it
out_bolt_a0  = 0;     // MEASURE-ME  angle of the first hole (turn the boss to suit)
rear_bcd     = 43;    // MEASURE-ME  REAR cover bolt circle — this is the mount
rear_bolt_n  = 4;     // MEASURE-ME
rear_bolt_a0 = 45;    // MEASURE-ME
shaft_bore_d = 8.1;   // MEASURE-ME  hollow through-bore (8.1 on "S", 12.7 on "L")

/* [Payload — DLH-3UP-EH, off LEDdynamics' drawing] */
payload_od     = 25.15; // Ø0.99" over the fin crests — the clamped diameter
payload_body   = 22.6;  // 0.89" finned length
payload_stub_d = 21.3;  // 1/2"-14 NPT major dia — the rear stub is the wire exit
payload_stub_l = 9.4;   // 1.26" overall − 0.89" body
payload_clear  = 0.6;   // slide fit: Ø25.75 ≈ 1.014", slides by hand

/* [Frame — thicknesses] */
t_plate  = 7;     // base plate
t_bridge = 8;     // yoke bridge
t_arm    = 10;    // yoke arms
cr_wall  = 8;     // cradle side plates

/* [Frame — the head] */
// The tilt axis does NOT pass through the housing's axis: it sits a hair above
// it, so that the head's own centre of mass — cap, saddle, housing and all —
// lands ON the axis. Measured, not guessed: the printed parts were exported and
// weighed in software, giving 38.3 g of plastic whose CoM is 2.37 mm above the
// bore, against a housing of about 25 g sitting on it. Solve for where the axis
// has to be and you get the number below. It costs nothing — an offset is free —
// and it is why there is no trim-washer bolt in this design any more.
// Residual over a 18-32 g housing: under 0.2 mm, i.e. under 0.1 mN.m.
axis_z   = 1.45;  // = Mp*zp / (Mp + Mh)
cr_len   = 32;    // cradle length along the housing axis
plate_z  = 14;    // side plates rise this far ABOVE the split line. Only as far
                  // as the cap needs to land: every mm here is mass ABOVE the
                  // tilt axis, and it thins the cap's clamping ear.
base_z   = 16;    // ...and the saddle reaches this far below it
cap_z    = 20;    // cap's outer height
clamp_nip  = 0.4; // the cap's bore sits this low, so it PINCHES before it bottoms
cap_bolt_y = 11;  // cap-screw spacing along the housing axis
cap_ear_d  = 10;  // ear pad dia — keep the outer edge clear of the motor body
cap_pocket = 4;   // lightening pocket in the cap's crown (prints first-layer)
pilot_len  = 10;  // cap-screw thread depth in the plate. Must stop short of
                  // the trunnion's bolt ring at z = 0.
keel_chamf = 9;   // dead-corner chamfer under the saddle

/* [Frame — the yoke] */
drop      = 32;   // bridge underside -> tilt axis. Must clear head_sweep.
arm_pad_d = 54;   // round pad at the tilt axis (covers the rear bolt circle)
arm_neck  = 30;   // arm width where it meets the bridge
arm_pocket_d = 32; // hex lightening pocket in the pad (vertex up = no bridge)
arm_pocket_z = 4;  // ...and how deep (of t_arm). Leaves a 6 mm web.
boss_recess = 1;  // locating recess depth — KEEP WELL UNDER out_boss_h

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
bore_d  = payload_od + payload_clear;        // 25.75 ≈ 1.014"
blk_in  = bore_d / 2 + 2;                    // 2 mm shoulder each side of the bore
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
stub_len = t_arm + carrier_t + trun_gap + 0.9;
boss_locate_d = loc_h(out_boss_d);
cap_w   = slot_fit(2 * blk_in);              // cap body drops between the plates
cap_bolt_x = blk_in + cr_wall / 2;           // centred in the plate, not on its edge

// the flange bolt circle needs this much plate above the tilt axis, which is
// more than the cap's landing face needs — so it gets a local pad, not 6 mm of
// extra wall down the whole part
bolt_pad_z = out_bcd / 2 + m3_head_d / 2 + 1.5;

// what has to clear what — the farthest corner of the head from the tilt axis
head_sweep = max(sqrt(pow(cr_len / 2, 2) + pow(cap_z - axis_z, 2)),
                 sqrt(pow(cr_len / 2, 2) + pow(base_z + axis_z, 2)));
slide_range = cr_len - payload_body;

// which output-flange holes sit ABOVE the split line: the only ones a driver can
// reach, which is why the boss gets turned one hole "up" before you bolt it
function out_bolt_z(i) = out_bcd / 2 * cos(out_bolt_a0 + i * 360 / out_bolt_n);
function out_bolt_up(i) = out_bolt_z(i) > 2;
