// assembly.scad — HOW THE GIMBAL GOES TOGETHER (Engineered Lighting · Doc 3b)
//
// Companion to frame.scad v3: this file `use`s the REAL part modules, so the
// assembly view can never drift from the printed geometry. Motors, bearing,
// DLH-3UP-EH LED housing, hardware, C-clamp and shelf appear as mockups.
//
//   view = "assembled"  → everything in its final position
//   view = "exploded"   → pulled apart along the axes, guide lines shown
//
// Open in OpenSCAD, press F5, orbit with the mouse. The numbered comments
// below match Doc 3b's build order.

use <frame.scad>

/* [View] */
view = "exploded"; // [exploded, assembled]

// ---- placement numbers (keep in sync with frame.scad's params) -------------------
flange_bolt_circle_d = 30;
body_d      = 49;
body_len    = 24;
boss_len    = 8;      // how far the output boss stands proud of the motor face
payload_od  = 25.15;
arm_offset  = 8;
t           = 6;
bearing_od  = 22;
bearing_w   = 7;
ring_w      = 10;
arm_w       = 60;

span    = body_d + 2 * arm_offset;         // 65 — inner face to inner face
drop    = body_d / 2 + arm_offset;         // 32.5 — bridge underside → tilt axis
arm_h   = drop + 28;
z_bridge = -(body_len + boss_len);         // bridge TOP face (mates the pan boss face)
z_tilt   = z_bridge - t - drop;            // tilt-axis height
head_L   = 49;

$fn = 64;

// exploded offsets (all 0 when assembled)
e = (view == "exploded") ? 1 : 0;
E_SHELF = 96 * e;    // shelf + clamp, up
E_BASE  = 62 * e;    // pan base, up
E_PANM  = 32 * e;    // pan motor, up
E_ARM   = 34 * e;    // arm plates, out ±x
E_TILTM = 40 * e;    // tilt motor, further out -x
E_BRG   = 26 * e;    // bearing, out +x
E_M8    = 46 * e;    // M8 axle, further out +x
E_HEAD  = 46 * e;    // head plates, down
E_RING  = 30 * e;    // cradle ring, toward viewer (-y)
E_LIGHT = 64 * e;    // housing, down + toward viewer

// ---- mockups (bought parts) --------------------------------------------------------
module motor(boss_at_top = false) {          // RMD-L-5005 stand-in, body along +z
  color("Silver") cylinder(d = body_d, h = body_len);
  color("DimGray") translate([0, 0, boss_at_top ? body_len : -boss_len])
    cylinder(d = flange_bolt_circle_d + 4, h = boss_len);
}
module bearing608() {
  color("LightSteelBlue") difference() {
    cylinder(d = bearing_od, h = bearing_w, center = true);
    cylinder(d = 8, h = bearing_w + 2, center = true);
  }
}
module led_housing() {                       // DLH-3UP-EH mockup: barrel along y, beam +y
  color([.72, .74, .78]) rotate([-90, 0, 0]) {
    translate([0, 0, -11.3]) cylinder(d = 23.5, h = 22.6);            // finned core
    for (i = [0 : 4]) translate([0, 0, -10 + i * 4.6])                // the fins
      cylinder(d = payload_od, h = 2.6);
    translate([0, 0, -20.7]) cylinder(d = 20.3, h = 9.4);             // 1/2"-14 NPT stub
  }
  color([.2, .2, .22]) rotate([-90, 0, 0]) translate([0, 0, -26.7])   // wires out the back
    cylinder(d = 5, h = 7);
  color([.95, .93, .75]) rotate([-90, 0, 0]) translate([0, 0, 11.3])  // optic
    cylinder(d = 21, h = 1.6);
  color("LemonChiffon") rotate([-90, 0, 0]) translate([0, 0, 13])     // the beam
    cylinder(d1 = 22, d2 = 52, h = 32);
}
module m8_axle() {                            // shaft along +z local, hex behind origin
  color([.42, .42, .46]) {
    cylinder(d = 7.8, h = 26);
    translate([0, 0, -5]) cylinder(d = 13, h = 5, $fn = 6);
  }
}
module c_clamp() {
  color([.35, .35, .38]) {
    translate([-7, -4, -7])  cube([14, 40, 7]);
    translate([-7, -4, 21])  cube([14, 40, 7]);
    translate([-7, 30, -7])  cube([14, 6, 35]);
    translate([0, 8, -16])   cylinder(d = 5, h = 10);
    translate([0, 8, -19])   cylinder(d = 14, h = 4);
  }
}
module shelf() { color("BurlyWood") translate([-58, 16, 6.2]) cube([116, 74, 16]); }

// ================================ SCENE ==============================================
// pan axis = world Z · tilt axis = world X · beam fires +y into the room.
// Printed parts keep their own colors per subassembly:
//   gold = pan base · orange = yoke (bridge + arms) · teal = head parts.

// 1 · shelf + C-clamp; pan base's ear goes under the clamp
rotate([0, 0, 180]) translate([0, 0, E_SHELF]) { shelf(); translate([0, 38, 0]) c_clamp(); }
rotate([0, 0, 180]) translate([0, 0, E_BASE]) rotate([180, 0, 0])
  translate([0, 0, -t]) color("Gold") pan_base();   // post-side down, into the swing plane

//     pan motor — BACK bolts up under the plate, output boss faces down
translate([0, 0, -body_len + E_PANM]) motor(boss_at_top = false);

// 2 · yoke bridge bolts to the pan output flange
translate([0, 0, z_bridge - t]) color("Orange") yoke_bridge();

// 3 · arm plates tab up into the bridge (M3s + square nuts lock them)
//     local→world: x↦y, y↦z, z↦x  (rotate([90,0,90]))
translate([-span / 2 - t - E_ARM, 0, z_bridge - t]) rotate([90, 0, 90])
  color("Orange") arm_motor();
translate([span / 2 + E_ARM, 0, z_bridge - t]) rotate([90, 0, 90])
  color("Orange") arm_bearing();

// 6a · tilt motor — body OUTSIDE the left arm, face-bolted to it; its boss
//      reaches through the arm's window into the gap
translate([-span / 2 - t - body_len - E_ARM - E_TILTM, 0, z_tilt]) rotate([0, 90, 0])
  motor(boss_at_top = true);

// 4 · head boss plate on the tilt boss (bolted on the desk, before step 6)
translate([-span / 2 + boss_len - t, 0, z_tilt - E_HEAD]) rotate([90, 0, 90])
  color("MediumTurquoise") head_boss_plate();

// 5 · head main plate spans the gap; end plate catches the far side
translate([-span / 2 + boss_len, -8 - t / 2, z_tilt - E_HEAD]) rotate([90, 0, 90])
  color("MediumTurquoise") head_main_plate();
translate([-span / 2 + boss_len + head_L, 0, z_tilt - E_HEAD]) rotate([90, 0, 90])
  color("MediumTurquoise") head_end_plate();

// 6b · 608 presses into the bearing arm; the M8 axle slides through it
//      into the end plate's captive nut — head now held on BOTH sides
translate([span / 2 + t + 4 - bearing_w / 2 + E_ARM + E_BRG, 0, z_tilt]) rotate([0, 90, 0])
  bearing608();
translate([span / 2 + t + 8 + E_ARM + E_M8, 0, z_tilt]) rotate([0, -90, 0]) m8_axle();

// 7 · cradle ring face-bolts over the main plate's window; the housing
//     slides through — slide to balance, then nip the pinch bolt
translate([-span / 2 + boss_len + head_L / 2, -5 - E_RING, z_tilt - E_HEAD]) rotate([-90, 0, 0])
  color("MediumTurquoise") cradle_ring();
translate([-span / 2 + boss_len + head_L / 2, -3 - E_RING, z_tilt - E_HEAD - E_LIGHT])
  led_housing();

// exploded-view guide lines
module axis_line(a, b) {
  color([.55, .55, .55]) hull() { translate(a) sphere(d = 1.2); translate(b) sphere(d = 1.2); }
}
if (view == "exploded") {
  axis_line([0, 0, E_SHELF + 2], [0, 0, z_bridge - 8]);                        // pan axis
  axis_line([-span / 2 - t - body_len - E_ARM - E_TILTM - 8, 0, z_tilt],
            [span / 2 + t + 34 + E_ARM + E_M8, 0, z_tilt]);                    // tilt axis
  axis_line([0, -4, z_tilt - 4], [0, -4, z_tilt - E_HEAD - E_LIGHT + 8]);      // head drop
}
