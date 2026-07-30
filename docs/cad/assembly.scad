// =============================================================================
// assembly.scad  ·  Engineered Lighting — robotic spotlight, WHOLE MACHINE (v4)
// =============================================================================
//
// This file INCLUDES frame.scad, so it uses the real printed geometry AND the
// real numbers — nothing here can drift from what you print. Everything else in
// the machine is drawn too: both motors with their actual bolt patterns, the
// 608, the DLH-3UP-EH housing (flush front — no protruding lens), the wires, the
// C-clamp, the shelf, and EVERY SINGLE BOLT.
//
//   view = "assembled" | "exploded"
//   pan / tilt  — pose it. The pan limits are the real hard-stop limits.
//   Open in OpenSCAD, press F5, orbit with the mouse.
//
// Colours:  gold = base plate · orange = yoke · teal = head parts
//           grey = bought metal · dark grey = fasteners
// =============================================================================

include <frame.scad>
part = "none";                       // frame.scad draws nothing; we place it here

/* [Pose] */
view  = "assembled";  // [assembled, exploded]
pan   = 0;            // [-155:5:155]
tilt  = 0;            // [-90:5:90]
slide = 0;            // [-4:0.5:4]  housing fore/aft trim inside the clamp
/* [Show] */
show_bolts  = true;
show_wires  = true;
show_shelf  = true;
show_beam   = false;
show_cap    = true;   // uncheck to look inside the clamp
clip        = "none"; // [none, front, side] section cut, to check what mates what
trim_stack  = 0;      // [0:6] washers on the keel trim bolt

e       = (view == "exploded") ? 1 : 0;
E_SHELF = 90 * e;
E_PANM  = 34 * e;
E_YOKE  = 76 * e;
E_TILTM = 46 * e;
E_HEAD  = 58 * e;
E_TRUN  = 30 * e;
E_CARR  = 40 * e;
E_BRG   = 62 * e;
E_HOUS  = 66 * e;
E_CAP   = 40 * e;
E_BOLT  = 22 * e;

yoke_z  = -(motor_len + out_boss_h) + boss_recess;   // yoke origin, on the pan axis
zt      = yoke_z + z_tilt;                           // world height of the tilt axis
stack_t = t_plate + 16;                              // plate + shelf, what the clamp grabs

// ----------------------------------------------------------------- hardware --
module screw(d = 3, len = 12, hd = m3_head_d, hh = 2.6) {
  color("#33343a") { cylinder(d = hd, h = hh); translate([0, 0, -len]) cylinder(d = d, h = len + 0.1); }
}
module washer(od = 9, id = 4.4, t = 1)   { color("#55565e") difference() {
    cylinder(d = od, h = t); cylinder(d = id, h = 3 * t, center = true); } }

// screws around a bolt circle, driven along -Z (head at z = 0)
module screw_ring(bcd, n, a0, len, d = 3, hd = m3_head_d) {
  for (i = [0 : n - 1]) rotate([0, 0, a0 + i * 360 / n])
    translate([bcd / 2, 0, 0]) screw(d, len, hd);
}

// ------------------------------------------------------------- bought parts --
module rmd_motor() {                 // origin = REAR face centre, body along +Z
  color("#b8bcc3") difference() {
    union() {
      cylinder(d = motor_d, h = motor_len);
      translate([0, 0, motor_len]) cylinder(d = out_boss_d, h = out_boss_h);
    }
    cylinder(d = shaft_bore_d, h = 3 * motor_len, center = true);
    bolt_ring(rear_bcd, m4_clear, rear_bolt_n, 14, rear_bolt_a0);                  // rear threads
    translate([0, 0, motor_len + out_boss_h]) bolt_ring(out_bcd, m3_clear, out_bolt_n, 14, out_bolt_a0);
    translate([0, 0, motor_len - 0.6]) difference() {                              // face/boss step line
      cylinder(d = motor_d + 1, h = 0.6); cylinder(d = out_boss_d + 2, h = 2, center = true); }
  }
  color("#24252a") translate([motor_d / 2 - 1.5, -7, motor_len / 2 - 7]) cube([7, 14, 14]);  // 4-pin
}
module rmd_pigtail(len = 12) { color("#26262b") translate([motor_d / 2 + 5, 0, motor_len / 2])
  rotate([0, 90, 0]) cylinder(d = 5, h = len); }

module bearing608() {                // origin = inner face, axis +Z
  color("#8d929b") difference() { cylinder(d = bearing_od, h = bearing_w);
    cylinder(d = bearing_id, h = 3 * bearing_w, center = true); }
  color("#5b5f67") translate([0, 0, -0.1]) difference() {
    cylinder(d = bearing_od - 3.4, h = bearing_w + 0.2);
    cylinder(d = bearing_id + 3.4, h = 3 * bearing_w, center = true); }
}

// DLH-3UP-EH: Ø0.99" finned barrel, 0.89" body, 1/2"-14 NPT rear stub.
// The front face is FLUSH — the emitters sit recessed behind the front rim.
module led_housing() {               // origin = centre of the finned body, beam +Y
  rotate([-90, 0, 0]) {
    color("#9aa0a9") {
      for (i = [0 : 4]) translate([0, 0, -payload_body / 2 + i * payload_body / 5])
        cylinder(d = payload_od, h = payload_body / 5 * 0.6);                      // fin crests
      translate([0, 0, -payload_body / 2]) cylinder(d = payload_od - 2.6, h = payload_body);
      translate([0, 0, -payload_body / 2 - payload_stub_l])
        cylinder(d = payload_stub_d, h = payload_stub_l + 0.4);                    // NPT stub
    }
    color("#34363c") translate([0, 0, payload_body / 2 - 3]) cylinder(d = payload_od - 4.4, h = 3);
    color("#f4ecc9") for (i = [0 : 2]) rotate([0, 0, i * 120 + 30])
      translate([4.7, 0, payload_body / 2 - 1.5]) cube([3.45, 3.45, 0.9], center = true);
    if (show_beam) color("#fff3c4", 0.13) translate([0, 0, payload_body / 2])
      cylinder(d1 = 16, d2 = 74, h = 120);
  }
}

module c_clamp() {                   // origin = middle of the clamped stack, front face
  color("#4a4d54") {
    translate([-9, -34, -10]) cube([18, 34, 10]);              // lower jaw, under the tongue
    translate([-9, -34, stack_t]) cube([18, 34, 10]);           // upper pad, on the shelf
    translate([-9, -1, -10]) cube([18, 9, stack_t + 20]);       // spine, at the shelf edge
    translate([0, -20, -21]) cylinder(d = 6.5, h = 12);         // screw
    translate([0, -20, -27]) cylinder(d = 17, h = 5.5);         // handle pad
  }
}
module shelf() { color("#c9a678") translate([-78, -168, t_plate]) cube([156, 122, 16]); }

// ------------------------------------------------------------------ wires ----
module wire(pts, d = 4.4) {
  color("#26262b") for (i = [0 : len(pts) - 2]) hull() {
    translate(pts[i]) sphere(d = d); translate(pts[i + 1]) sphere(d = d); }
}

module scene() {
// =============================================================================
//                                   SCENE
// world: pan axis = Z · tilt axis = X · beam fires +Y · base plate face at z = 0
// =============================================================================

// 1 · shelf + C-clamp on the base plate's aft tongue
if (show_shelf) translate([0, 0, E_SHELF]) { shelf(); translate([0, -62, 0]) c_clamp(); }

// 2 · base plate (post hangs down into the yoke's swing plane)
color("#d8a93a") base_plate();

// 3 · pan motor: REAR bolted up under the plate, output boss facing down
translate([0, 0, -E_PANM]) {
  rotate([180, 0, 0]) rotate([0, 0, 90]) { rmd_motor(); rmd_pigtail(); }
  if (show_bolts) translate([0, 0, t_plate - 3.2 + E_BOLT])
    screw_ring(rear_bcd, rear_bolt_n, rear_bolt_a0, t_plate + 6, 4, m4_head_d);
}

// ---------------------------------------------------------------- pan group --
rotate([0, 0, pan]) translate([0, 0, yoke_z - E_YOKE]) {

  color("#e8862a") yoke();

  // 4 · the six bolts that hold the yoke on the pan output — driven UP from
  //     under the bridge, reachable between the arms
  if (show_bolts) translate([0, 0, -t_bridge - E_BOLT]) rotate([180, 0, 0])
    screw_ring(out_bcd, out_bolt_n, out_bolt_a0, t_bridge + 5);

  // 5 · tilt motor: REAR bolted to the LEFT arm's inner face, body inside the yoke
  translate([-span_h - E_TILTM, 0, z_tilt]) rotate([0, 90, 0]) rotate([0, 0, -90])
    { rmd_motor(); rmd_pigtail(); }
  if (show_bolts) translate([-span_h - t_arm - E_TILTM - E_BOLT, 0, z_tilt]) rotate([0, -90, 0])
    screw_ring(rear_bcd, rear_bolt_n, rear_bolt_a0, t_arm + 7, 4, m4_head_d);

  // ------------------------------------------------------------- head group --
  translate([0, 0, z_tilt]) rotate([tilt, 0, 0]) translate([0, 0, -E_HEAD]) {

    color("#39c0bd") translate([bore_x, 0, 0]) cradle();

    // 6 · the THREE output-flange bolts that a driver can actually reach — the
    //     ones above the split line, driven while the cap is still off
    if (show_bolts) translate([bore_x + x_left + cr_wall, 0, 0])
      for (i = [0 : out_bolt_n - 1]) if (out_bolt_z(i) > 2)
        rotate([out_bolt_a0 + i * 360 / out_bolt_n, 0, 0]) translate([0, 0, out_bcd / 2])
          rotate([0, 90, 0]) translate([0, 0, E_BOLT]) screw(3, cr_wall + 5);

    // 7 · trunnion — the printed axle
    color("#2aa8a5") translate([bore_x + x_right + E_TRUN, 0, 0]) trunnion();
    if (show_bolts) translate([bore_x + x_right + trun_t + E_TRUN + E_BOLT, 0, 0])
      rotate([0, 90, 0]) rotate([0, 0, 90]) screw_ring(18, 3, 0, trun_t + 9);

    // 8 · the housing lays into the saddle; the cap pinches it. Slide it along
    //     the bore to balance BEFORE the four cap screws go tight.
    translate([bore_x, slide, -E_HOUS]) led_housing();
    if (show_cap) color("#39c0bd") translate([bore_x, 0, E_CAP]) cradle_cap();
    if (show_bolts) for (x = [-cap_bolt_x, cap_bolt_x], y = [-cap_bolt_y, cap_bolt_y])
      translate([bore_x + x, y, cap_z + E_CAP + E_BOLT]) screw(3, cap_z - 4);

    // 9 · fine balance trim: washers on an M4 through the keel
    if (show_bolts && trim_stack > 0) translate([bore_x, cr_len / 2 + 1, -base_z + 3.6])
      rotate([-90, 0, 0]) {
        for (i = [0 : trim_stack - 1]) translate([0, 0, i * 1.1]) washer();
        translate([0, 0, trim_stack * 1.1]) screw(4, cr_len + trim_stack * 1.1 + 3, m4_head_d);
      }
    if (show_wires) wire([[bore_x + x_left + 4, 0, 0], [bore_x - blk_in + 3, 0, 2.6],
                          [bore_x - blk_in + 3, -cr_len / 2 - 3, 2.6],
                          [bore_x, slide - payload_body / 2 - payload_stub_l + 1, 0]], 4.0);
  }

  // 10 · 608 in its carrier, bolted to the RIGHT arm — tighten LAST so the
  //      bearing can find the axis the motor actually defines
  translate([span_h + t_arm + E_CARR, 0, z_tilt]) {
    color("#39c0bd") bearing_carrier();
    translate([carrier_t - bearing_w - 0.3 + E_BRG, 0, 0]) rotate([0, 90, 0]) bearing608();
    if (show_bolts) translate([carrier_t + E_BOLT, 0, 0]) rotate([0, 90, 0]) rotate([0, 0, 90])
      screw_ring(34, 3, 0, carrier_t + t_arm + 1);
  }

  // 11 · wires: tilt motor's hollow shaft -> out through the arm -> up the arm's
  //      cable channel -> through the bridge -> up the pan motor's hollow shaft
  if (show_wires) {
    // LED bundle: out of the tilt motor's hollow shaft, through the arm, up its
    // cable channel, along the bridge underside, then up the pan motor's bore
    wire([[-span_h - 2, 0, z_tilt], [-arm_out - 1, 0, z_tilt],
          [-arm_out + 1.5, -9, z_tilt + 6], [-arm_out + 1.5, -9, -t_bridge - 5],
          [-18, -9, -t_bridge - 5], [-2, -3, -t_bridge - 2], [0, 0, 4]], 4.0);
    // the tilt motor's own 4-pin pigtail joins the same run
    wire([[-span_h + motor_len / 2, -motor_d / 2 - 14, z_tilt],
          [-arm_out + 1.5, -12, z_tilt + 16], [-arm_out + 1.5, -12, -t_bridge - 5]], 3.4);
  }
}
if (show_wires) wire([[0, 0, -6], [0, 0, t_plate + 3]]);

// exploded-view guide lines
module guide(a, b) { color("#9a9a9a", 0.85) hull() {
  translate(a) sphere(d = 1.1); translate(b) sphere(d = 1.1); } }
if (view == "exploded") {
  guide([0, 0, E_SHELF + 20], [0, 0, yoke_z - E_YOKE - 12]);
  guide([-span_h - t_arm - E_TILTM - E_BOLT - 14, 0, zt - E_YOKE],
        [span_h + t_arm + E_CARR + E_BRG + 26, 0, zt - E_YOKE]);
  guide([bore_x, 0, zt - E_YOKE - 4], [bore_x, 0, zt - E_YOKE - E_HEAD - E_HOUS - 14]);
}
}

// section cuts, for checking that things really engage
if (clip == "none") scene();
else intersection() {
  scene();
  if (clip == "front") translate([-400, -400, -400]) cube([800, 400, 800]);
  else translate([-400, -400, -400]) cube([400, 800, 800]);
}
