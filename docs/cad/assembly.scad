// assembly.scad — HOW THE GIMBAL GOES TOGETHER (Engineered Lighting · Doc 3b)
// Companion to cad/frame.scad: same parameters, but every part shown IN PLACE,
// with the motors, 608 bearing, DLH LED housing, C-clamp and shelf as mockups.
//
//   view = "assembled"  → everything in its final position
//   view = "exploded"   → pulled apart along the two axes, guide lines shown
//
// Open this in OpenSCAD, press F5, and orbit with the mouse.
//
// This mirrors frame.scad v2's corrected geometry (bridged yoke arms,
// pinch-collar cradle crossing the tilt axis, M8-through-608 axle) with the
// motors, bearing, DLH-3UP-EH LED housing, C-clamp and shelf as mockups, so
// you can see every part in place before anything prints.

/* [View] */
view = "exploded"; // [exploded, assembled]

/* [Motor interface — same values as frame.scad] */
flange_bolt_circle_d = 30;
flange_bolt_d        = 3.2;
flange_bolt_n        = 4;
flange_center_bore_d = 8.1;
body_d               = 49;
body_len             = 24;

/* [Payload + frame] */
payload_od    = 25.15; // DLH-3UP-EH aluminum LED housing — Ø0.99" per its drawing
payload_clear = 0.6;   // slide fit: the housing glides in the cradle to balance
cradle_w      = 12;    // cradle grip width on the finned barrel
arm_offset   = 8;
wall         = 4;
bearing_od   = 22;  // 608
bearing_id   = 8;
bearing_w    = 7;
clamp_ear_w  = 30;
hard_stop_h  = 6;

$fn = 64;

// ---- derived -----------------------------------------------------------------
span    = body_d + 2 * arm_offset;          // daylight between the two arms
disc_d  = flange_bolt_circle_d + 4 * wall;  // every flange disc
drop    = body_d / 2 + arm_offset;          // yoke-arm root → tilt axis
z_disc  = -(body_len + 2 + wall);           // yoke disc top face (under pan boss)
z_tilt  = z_disc - drop;                    // tilt-axis height (world)
x_head  = -span / 2 + body_len / 2 + 2;     // head-shell flange plane
cradle_id = payload_od + payload_clear;     // ≈ 25.75 mm ≈ 1.014"
ring_od   = cradle_id + 2 * wall;
ring_c    = wall + ring_od / 2;             // head local: barrel crosses tilt axis here

// exploded offsets (all 0 when assembled)
e = (view == "exploded") ? 1 : 0;
E_SHELF = 100 * e;
E_BASE  = 64 * e;
E_PANM  = 34 * e;
E_TILTM = 36 * e;   // out -x
E_BRG   = 30 * e;   // out +x
E_HEAD  = 44 * e;   // down
E_LIGHT = 84 * e;   // further down

// ---- helpers -------------------------------------------------------------------
module flange_bolts(h = 10) {
  for (i = [0 : flange_bolt_n - 1])
    rotate([0, 0, i * 360 / flange_bolt_n])
      translate([flange_bolt_circle_d / 2, 0, -1])
        cylinder(d = flange_bolt_d, h = h + 2);
}
module disc_with_holes() {
  difference() {
    cylinder(d = disc_d, h = wall);
    translate([0, 0, -1]) cylinder(d = flange_center_bore_d, h = wall + 2);
    flange_bolts(wall);
  }
}

// ---- mockups (bought parts, not printed) -----------------------------------------
module motor(boss_at_top = false) {          // RMD-L-5005 stand-in, body along +z
  color("Silver") cylinder(d = body_d, h = body_len);
  color("DimGray") translate([0, 0, boss_at_top ? body_len : -2])
    cylinder(d = flange_bolt_circle_d + 4, h = 2);
}
module bearing608() {
  color("LightSteelBlue") difference() {
    cylinder(d = bearing_od, h = bearing_w, center = true);
    cylinder(d = bearing_id, h = bearing_w + 2, center = true);
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
module c_clamp() {                           // wraps shelf + ear at the ear
  color([.35, .35, .38]) {
    translate([-7, -4, -7])  cube([14, 40, 7]);       // lower jaw (under the ear)
    translate([-7, -4, 21])  cube([14, 40, 7]);       // upper jaw (over the shelf)
    translate([-7, 30, -7])  cube([14, 6, 35]);       // spine
    translate([0, 8, -16])   cylinder(d = 5, h = 10); // screw
    translate([0, 8, -19])   cylinder(d = 14, h = 4); // handle pad
  }
}
module shelf() { color("BurlyWood") translate([-58, 16, 4.2]) cube([116, 74, 16]); }

// ---- printed parts (corrected where frame.scad is a scaffold) --------------------
module pan_base() {
  color("Gold") difference() {
    union() {
      cylinder(d = body_d + 2 * wall, h = wall);
      translate([-(clamp_ear_w / 2), body_d / 2 - 1, 0])
        cube([clamp_ear_w, clamp_ear_w + 1, wall]);                    // clamp ear
      translate([body_d / 2 - 2, -hard_stop_h / 2, wall - 0.01])
        cube([wall, hard_stop_h, hard_stop_h]);                        // pan hard stop
    }
    translate([0, 0, -1]) cylinder(d = flange_center_bore_d, h = wall + 2);
    flange_bolts(wall);
  }
}

module yoke_arm(bore, t) {                   // hanging slab ending in a collar
  slab_len = drop - bore / 2 - wall + 8;     // overlaps the collar by ~8
  translate([0, -body_d / 4, -slab_len]) cube([t, body_d / 2, slab_len + 0.01]);
  translate([0, 0, -drop]) rotate([0, 90, 0]) difference() {
    cylinder(d = bore + 2 * wall, h = t);                              // collar
    translate([0, 0, -1]) cylinder(d = bore, h = t + 2);
  }
}

module yoke() {
  color("Orange") {
    translate([0, 0, -wall]) disc_with_holes();                        // pan-flange disc
    // FIX 1: bridge bar joins the disc to both arm roots
    difference() {
      translate([-(span / 2 + wall + body_len / 2), -body_d / 4, -wall])
        cube([span + 2 * wall + body_len / 2 + bearing_w, body_d / 2, wall]);
      translate([0, 0, -wall - 1]) cylinder(d = flange_center_bore_d, h = wall + 2);
    }
    translate([span / 2, 0, -wall]) yoke_arm(bearing_od, wall + bearing_w);       // bearing arm
    translate([-span / 2 - wall - body_len / 2, 0, -wall])
      yoke_arm(body_d + 0.6, wall + body_len / 2);                                // motor arm
    translate([-hard_stop_h / 2, flange_bolt_circle_d / 2 + wall, -2 * wall])     // tilt stop
      cube([hard_stop_h, wall, wall]);
  }
}

module head_shell() {                        // local +z = tilt axis; beam = local +y
  color("MediumTurquoise") difference() {
    union() {
      disc_with_holes();                                               // bolts to tilt flange
      translate([0, 0, wall - 0.01]) cylinder(d = disc_d, h = 4);      // gusset
      // FIX 2: pinch-collar cradle rotated 90° — the housing CROSSES the
      // tilt axis, so tilting sweeps the beam instead of rolling it.
      translate([0, 0, ring_c]) rotate([-90, 0, 0])
        cylinder(d = ring_od, h = cradle_w, center = true);
      translate([ring_od / 2 - wall, -cradle_w / 2, ring_c - 5])       // pinch ears
        cube([wall + 6, cradle_w, 10]);
      translate([-2, -cradle_w / 2, ring_c])                           // spine
        cube([4, cradle_w, ring_od / 2 + 4]);
      // FIX 3: end plate — an M8 bolt through the 608 threads in here
      translate([0, 0, ring_c + ring_od / 2]) cylinder(d = flange_bolt_circle_d, h = wall);
      translate([-2, -62, ring_c + 14]) cube([4, 58, 18]);             // counterweight tail
    }
    translate([0, 0, ring_c]) rotate([-90, 0, 0])                      // payload bore
      cylinder(d = cradle_id, h = cradle_w + 20, center = true);
    translate([cradle_id / 2 - 1, -(cradle_w + 2) / 2, ring_c - 1])    // pinch slit
      cube([wall + 10, cradle_w + 2, 2]);
    translate([0, 0, ring_c + ring_od / 2 - 1]) cylinder(d = 8.2, h = wall + 2); // M8 hole
    translate([-3, -56, ring_c + 20.35]) cube([6, 38, 5.3]);           // M5 slot
  }
  // M5 counterweight mock (bolt + stacked nuts riding the slot)
  color([.3, .3, .33]) translate([-6, -40, ring_c + 23]) rotate([0, 90, 0])
    cylinder(d = 11, h = 12, $fn = 6);
}

// ---- exploded-view guide lines -----------------------------------------------
module axis_line(a, b) {
  color([.55, .55, .55]) hull() { translate(a) sphere(d = 1.2); translate(b) sphere(d = 1.2); }
}

// ================================ SCENE ==========================================
// pan axis = world Z (vertical) · tilt axis = world X (horizontal)
// shelf + clamp ear live on the -y side; the beam fires +y into the open room

// 1 · shelf + C-clamp (the bench's stand-in for "hanging from the ceiling")
rotate([0, 0, 180]) translate([0, 0, E_SHELF]) { shelf(); translate([0, 38, 0]) c_clamp(); }

// 2 · pan base — ear under the clamp, motor plate cantilevers past the shelf edge
rotate([0, 0, 180]) translate([0, 0, E_BASE]) pan_base();

//     pan motor — BODY bolts up against the plate, output flange faces DOWN
translate([0, 0, -body_len + E_PANM]) motor(boss_at_top = false);

// 3 · yoke — its disc bolts to the pan output flange, arms hang down
translate([0, 0, z_disc + wall]) yoke();

// 4a · tilt motor — body slides into the motor-arm collar, flange faces INWARD
translate([-span / 2 - body_len / 2 - E_TILTM, 0, z_tilt]) rotate([0, 90, 0])
  motor(boss_at_top = true);

// 4b · 608 bearing — presses into the bearing-arm collar
translate([span / 2 + wall + bearing_w / 2 + E_BRG, 0, z_tilt]) rotate([0, 90, 0])
  bearing608();

// 5 · head shell — disc onto the tilt flange; the M8 axle bolt slides in
//     through the bearing from outside and lands in the end plate
translate([x_head, 0, z_tilt - E_HEAD]) rotate([0, 90, 0]) head_shell();
translate([span / 2 + wall + bearing_w + 5 + E_BRG + 22 * e, 0, z_tilt])
  rotate([0, -90, 0]) color([.42, .42, .46]) {
    cylinder(d = 7.8, h = 30);                                         // M8 axle bolt
    translate([0, 0, -4.5]) cylinder(d = 13, h = 4.5, $fn = 6);        // its hex head
  }

// 6 · LED housing — slides through the cradle, balanced across the tilt axis
translate([x_head + ring_c, 0, z_tilt - E_HEAD - E_LIGHT]) led_housing();

if (view == "exploded") {
  axis_line([0, 0, E_SHELF + 2], [0, 0, z_disc - 6]);                          // pan axis
  axis_line([-span / 2 - body_len - E_TILTM - 8, 0, z_tilt],
            [span / 2 + wall + bearing_w + E_BRG + 10, 0, z_tilt]);            // tilt axis
  axis_line([x_head + ring_c, 0, z_tilt - 2],
            [x_head + ring_c, 0, z_tilt - E_HEAD - E_LIGHT + 6]);              // head drop
}
