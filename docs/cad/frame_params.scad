// =============================================================================
// frame_params.scad · Engineered Lighting — every number the frame is built from
// =============================================================================
// BOTH frame.scad and assembly.scad `include` this file. That is the whole
// anti-drift mechanism: there is exactly one copy of every dimension, and the
// assembly view cannot disagree with the parts you print.
//
// Anything marked MEASURE-ME came off a drawing, not off calipers. fit_coupon
// checks every one of them for 3 g of PETG before a real part is printed.
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
t_bridge = 9;     // yoke bridge
t_arm    = 10;    // yoke arms
cr_wall  = 8;     // cradle side plates

/* [Frame — the head] */
cr_len   = 32;    // cradle length along the housing axis
plate_z  = 17;    // side plates rise this far ABOVE the split line
base_z   = 16;    // ...and the saddle reaches this far below it
cap_z    = 20;    // cap's outer height
clamp_nip  = 0.4; // the cap's bore sits this low, so it PINCHES before it bottoms
cap_bolt_x = 17.5; cap_bolt_y = 11;
keel_chamf = 9;   // dead-corner chamfer under the saddle

/* [Frame — the yoke] */
drop      = 32;   // bridge underside -> tilt axis. Must clear head_sweep.
arm_pad_d = 54;   // round pad at the tilt axis (covers the rear bolt circle)
arm_neck  = 30;   // arm width where it meets the bridge
arm_pocket_d = 36; // lightening pocket in the pad's outer face
boss_recess = 1;  // locating recess depth — KEEP WELL UNDER out_boss_h

/* [Frame — the pan hard stop] */
stop_r    = 31;   // post and groove centreline radius
stop_w    = 8.4;  // groove width, radial
stop_deep = 4;    // groove depth (of t_bridge — the floor still carries the arms)
stop_arc  = 345;  // groove sweep -> ~307 deg of usable travel
post_w    = 20;   // post width, tangential

/* [Frame — cable management] */
trough_w  = 7;    // one channel size, used everywhere
trough_d  = 5;
wire_hole_d = 12; // through both hollow shafts and both plates

/* [Hardware] */
m3_clear = 3.4;  m3_pilot = 2.55; m3_head_d = 6.4;
m4_clear = 4.5;  m4_head_d = 8.4;
bearing_od = 22; bearing_id = 8; bearing_w = 7;
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
post_h  = motor_len + out_boss_h - boss_recess + 3;
stub_len = t_arm + carrier_t + trun_gap + 0.9;
boss_locate_d = out_boss_d + 0.4;

// what has to clear what
head_sweep = sqrt(pow(cr_len / 2, 2) + pow(cap_z, 2));
slide_range = cr_len - payload_body;

// which output-flange holes sit ABOVE the split line: the only ones a driver can
// reach, which is why the boss gets turned one hole "up" before you bolt it
function out_bolt_z(i) = out_bcd / 2 * cos(out_bolt_a0 + i * 360 / out_bolt_n);
function out_bolt_up(i) = out_bolt_z(i) > 2;
