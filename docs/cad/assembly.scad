// =============================================================================
// assembly.scad · Engineered Lighting — robotic spotlight, THE WHOLE MACHINE
// v5 (2026-07-30)
// =============================================================================
//
// HOW THIS FILE STAYS HONEST
//   include <frame_params.scad>   <- the same single copy of every dimension
//   use     <frame.scad>          <- the real printed parts, as modules only
//
// `use` imports the part modules WITHOUT running frame.scad's own render block,
// so this file always draws the assembly and only the assembly. There is no
// override trick and nothing to go wrong: open it, press F5, and the whole
// machine is there.
//
// WHAT IS IN HERE
//   printed:  base_plate · yoke · cradle · cradle_cap · trunnion · bearing_carrier
//   bought:   2 × RMD-L-5005 (with their real bolt patterns and connectors),
//             608 bearing, DLH-3UP-EH LED housing (flush front), C-clamp, shelf
//   fitted:   all 27 screws, the balance-trim washer stack, and the whole cable
//             run — housing → tilt motor's hollow shaft → arm trough → bridge
//             trough → pan motor's hollow shaft → base-plate trough
//
//   view  = assembled | exploded          pan / tilt / slide  — pose it
//   show_cap = false                      look inside the clamp
//   clip  = front | side                  section it
//
// Colours: gold = base plate · orange = yoke · teal = head · grey = bought metal
// =============================================================================

include <frame_params.scad>
use <frame.scad>

/* [Pose] */
view  = "assembled";  // [assembled, exploded]
pan   = 0;            // [-150:5:150]
tilt  = 0;            // [-90:5:90]
slide = 0;            // [-4:0.5:4]
/* [Show] */
show_bolts = true;
show_wires = true;
show_shelf = true;
show_cap   = true;
show_beam  = false;
trim_stack = 3;       // [0:8] washers on the keel trim bolt (3 nulls the CoM)
clip       = "none";  // [none, front, side]

$fn = 48;

e       = (view == "exploded") ? 1 : 0;
E_SHELF = 86 * e;   E_PANM = 32 * e;  E_YOKE = 74 * e;  E_TILTM = 44 * e;
E_HEAD  = 54 * e;   E_TRUN = 28 * e;  E_CARR = 38 * e;  E_BRG   = 58 * e;
E_HOUS  = 62 * e;   E_CAP  = 38 * e;  E_BOLT = 20 * e;

yoke_z  = -(motor_len + out_boss_h) + boss_recess;
zt      = yoke_z + z_tilt;
stack_t = t_plate + 16;
hx      = bore_x;                       // the head's place along the tilt axis

// ------------------------------------------------------------------ fasteners --
module screw(d = 3, len = 12, hd = m3_head_d, hh = 2.6) {
  color("#33343a") { cylinder(d = hd, h = hh); translate([0, 0, -len]) cylinder(d = d, h = len + 0.1); }
}
module washer(od = 9, id = 4.4, t = 1) { color("#55565e") difference() {
  cylinder(d = od, h = t); cylinder(d = id, h = 3 * t, center = true); } }
module screw_ring(bcd, n, a0, len, d = 3, hd = m3_head_d) {   // heads at z=0, driven -Z
  for (i = [0 : n - 1]) rotate([0, 0, a0 + i * 360 / n]) translate([bcd / 2, 0, 0]) screw(d, len, hd);
}

// --------------------------------------------------------------- bought parts --
module rmd_motor() {                    // origin = REAR face centre, body along +Z
  color("#b8bcc3") difference() {
    union() {
      cylinder(d = motor_d, h = motor_len);
      translate([0, 0, motor_len]) cylinder(d = out_boss_d, h = out_boss_h);
    }
    cylinder(d = shaft_bore_d, h = 3 * motor_len, center = true);
    bolt_ring(rear_bcd, m4_clear, rear_bolt_n, 14, rear_bolt_a0);
    translate([0, 0, motor_len + out_boss_h])
      bolt_ring(out_bcd, m3_clear, out_bolt_n, 14, out_bolt_a0);
    translate([0, 0, motor_len - 0.6]) difference() {          // face/boss step line
      cylinder(d = motor_d + 1, h = 0.6); cylinder(d = out_boss_d + 2, h = 2, center = true); }
  }
  color("#24252a") translate([motor_d / 2 - 1.5, -7, motor_len / 2 - 7]) cube([7, 14, 14]);
  color("#26262b") translate([motor_d / 2 + 5, 0, motor_len / 2])
    rotate([0, 90, 0]) cylinder(d = 5, h = 11);
}

module bearing608() {                   // origin = inner face, axis +Z
  color("#8d929b") difference() { cylinder(d = bearing_od, h = bearing_w);
    cylinder(d = bearing_id, h = 3 * bearing_w, center = true); }
  color("#5b5f67") translate([0, 0, -0.1]) difference() {
    cylinder(d = bearing_od - 3.4, h = bearing_w + 0.2);
    cylinder(d = bearing_id + 3.4, h = 3 * bearing_w, center = true); }
}

// DLH-3UP-EH — flush front rim, emitters recessed behind it, NPT stub at the back
module led_housing() {                  // origin = centre of the finned body, beam +Y
  rotate([-90, 0, 0]) {
    color("#9aa0a9") {
      for (i = [0 : 4]) translate([0, 0, -payload_body / 2 + i * payload_body / 5])
        cylinder(d = payload_od, h = payload_body / 5 * 0.6);
      translate([0, 0, -payload_body / 2]) cylinder(d = payload_od - 2.6, h = payload_body);
      translate([0, 0, -payload_body / 2 - payload_stub_l])
        cylinder(d = payload_stub_d, h = payload_stub_l + 0.4);
    }
    color("#34363c") translate([0, 0, payload_body / 2 - 3]) cylinder(d = payload_od - 4.4, h = 3);
    color("#f4ecc9") for (i = [0 : 2]) rotate([0, 0, i * 120 + 30])
      translate([4.7, 0, payload_body / 2 - 1.5]) cube([3.4, 3.4, 0.9], center = true);
    if (show_beam) color("#fff3c4", 0.13) translate([0, 0, payload_body / 2])
      cylinder(d1 = 16, d2 = 74, h = 120);
  }
}

module c_clamp() {
  color("#4a4d54") {
    translate([-9, -34, -10]) cube([18, 34, 10]);
    translate([-9, -34, stack_t]) cube([18, 34, 10]);
    translate([-9, -1, -10]) cube([18, 9, stack_t + 20]);
    translate([0, -20, -21]) cylinder(d = 6.5, h = 12);
    translate([0, -20, -27]) cylinder(d = 17, h = 5.5);
  }
}
module shelf() { color("#c9a678") translate([-78, -168, t_plate]) cube([156, 122, 16]); }

module guide(a, b) { color("#9a9a9a", 0.8) hull() {
  translate(a) sphere(d = 1.1); translate(b) sphere(d = 1.1); } }

module wire(pts, d = 4.6) {
  color("#26262b") for (i = [0 : len(pts) - 2]) hull() {
    translate(pts[i]) sphere(d = d); translate(pts[i + 1]) sphere(d = d); }
}

// =============================================================================
//                                    SCENE
// world: pan axis = Z · tilt axis = X · beam fires +Y · base plate's face at z=0
// =============================================================================
module scene() {

  // 1 · shelf and C-clamp, gripping the base plate's aft tongue
  if (show_shelf) translate([0, 0, E_SHELF]) { shelf(); translate([0, -56, 0]) c_clamp(); }

  // 2 · base plate — the hard-stop post hangs down into the bridge's groove
  color("#d8a93a") base_plate();

  // 3 · pan motor: REAR bolted up under the plate, output boss facing down
  translate([0, 0, -E_PANM]) {
    rotate([180, 0, 0]) rotate([0, 0, 90]) rmd_motor();
    if (show_bolts) translate([0, 0, t_plate - 3.2 + E_BOLT])
      screw_ring(rear_bcd, rear_bolt_n, rear_bolt_a0, t_plate + 7, 4, m4_head_d);
  }

  // ------------------------------------------------------------- pan group ----
  rotate([0, 0, pan]) translate([0, 0, yoke_z - E_YOKE]) {

    color("#e8862a") yoke();

    // 4 · six M3 up through the bridge into the pan output boss
    if (show_bolts) translate([0, 0, -t_bridge - E_BOLT]) rotate([180, 0, 0])
      screw_ring(out_bcd, out_bolt_n, out_bolt_a0, t_bridge + 5);

    // 5 · tilt motor: REAR bolted to the LEFT arm's inner face, body inside the yoke
    translate([-span_h - E_TILTM, 0, z_tilt]) rotate([0, 90, 0]) rotate([0, 0, -90]) rmd_motor();
    if (show_bolts) translate([-span_h - t_arm - E_TILTM - E_BOLT, 0, z_tilt]) rotate([0, -90, 0])
      screw_ring(rear_bcd, rear_bolt_n, rear_bolt_a0, t_arm + 8, 4, m4_head_d);

    // -------------------------------------------------------- head group ----
    translate([0, 0, z_tilt]) rotate([tilt, 0, 0]) translate([0, 0, -E_HEAD]) {

      color("#39c0bd") translate([hx, 0, 0]) cradle();

      // 6 · the three output-flange bolts a driver can reach: the ones above the
      //     split line, driven while the cap is still off
      if (show_bolts) translate([hx + x_left + cr_wall, 0, 0])
        for (i = [0 : out_bolt_n - 1]) if (out_bolt_up(i))
          rotate([out_bolt_a0 + i * 360 / out_bolt_n, 0, 0]) translate([0, 0, out_bcd / 2])
            rotate([0, 90, 0]) translate([0, 0, E_BOLT]) screw(3, cr_wall + 6);

      // 7 · trunnion, the printed axle — three screws, heads outside
      color("#2aa8a5") translate([hx + x_right + E_TRUN, 0, 0]) trunnion();
      if (show_bolts) translate([hx + x_right + trun_t + E_TRUN + E_BOLT, 0, 0])
        rotate([0, 90, 0]) rotate([0, 0, 90]) screw_ring(trun_bcd, 3, 0, trun_t + 9);

      // 8 · the housing lays in; the cap pinches it. Slide to balance FIRST.
      translate([hx, slide, -E_HOUS]) led_housing();
      if (show_cap) color("#39c0bd") translate([hx, 0, E_CAP]) cradle_cap();
      if (show_bolts) for (x = [-cap_bolt_x, cap_bolt_x], y = [-cap_bolt_y, cap_bolt_y])
        translate([hx + x, y, cap_z + E_CAP + E_BOLT]) screw(3, cap_z - 3);

      // 9 · balance trim — measured: the head sits 1.5 mm above the axis, which
      //     three M4 washers on the keel bolt cancel
      if (show_bolts && trim_stack > 0)
        translate([hx, cr_len / 2 + 1, -base_z + 3.4]) rotate([-90, 0, 0]) {
          for (i = [0 : trim_stack - 1]) translate([0, 0, i * 1.1]) washer();
          translate([0, 0, trim_stack * 1.1]) screw(4, cr_len + trim_stack * 1.1 + 4, m4_head_d);
        }

      // the head's share of the cable run: out of the housing's stub, forward
      // along the channel in the cap's corner, into the motor's hollow shaft
      if (show_wires) wire([
        [hx, slide - payload_body / 2 - payload_stub_l + 1, 0],
        [hx - blk_in + trough_w / 2 + 1, slide - 13, 2.9],
        [hx - blk_in + trough_w / 2 + 1, -2, 2.9],
        [hx + x_left + 3, 0, 0.5], [hx + x_left - 2, 0, 0]]);
    }

    // 10 · 608 in its carrier on the RIGHT arm — three screws, tightened LAST
    translate([span_h + t_arm + E_CARR, 0, z_tilt]) {
      color("#39c0bd") bearing_carrier();
      translate([carrier_t - bearing_w - 0.3 + E_BRG, 0, 0]) rotate([0, 90, 0]) bearing608();
      if (show_bolts) translate([carrier_t + E_BOLT, 0, 0]) rotate([0, 90, 0]) rotate([0, 0, 90])
        screw_ring(carrier_bcd, 3, 0, carrier_t + t_arm + 2);
    }

    // 11 · the frame's share of the cable run: through the tilt motor's hollow
    //      shaft, out through the arm, up the arm trough, along the bridge
    //      trough, then up through the pan motor's hollow shaft
    if (show_wires) wire([
      [-span_h - 2, 0, z_tilt], [-arm_out - 1, 0, z_tilt],
      [-arm_out + 1.6, 0, z_tilt + 6], [-arm_out + 1.6, 0, -t_bridge - 4],
      [-arm_out + 2, 0, -t_bridge + 1.6], [-14, 0, -t_bridge + 1.6], [0, 0, 4]]);
  }
  // 12 · and out of the pan motor into the base plate's trough, aft to the world
  if (show_wires) wire([[0, 0, -6], [0, 0, t_plate - 1.7], [30, 0, t_plate - 1.7],
                        [42, 0, t_plate - 6]]);

  if (view == "exploded") {
    guide([0, 0, E_SHELF + 20], [0, 0, yoke_z - E_YOKE - 10]);
    guide([-span_h - t_arm - E_TILTM - E_BOLT - 14, 0, zt - E_YOKE],
          [span_h + t_arm + E_CARR + E_BRG + 24, 0, zt - E_YOKE]);
    guide([hx, 0, zt - E_YOKE - 4], [hx, 0, zt - E_YOKE - E_HEAD - E_HOUS - 12]);
  }
}

if (clip == "none") scene();
else intersection() {
  scene();
  if (clip == "front") translate([-400, -400, -400]) cube([800, 400, 800]);
  else translate([-400, -400, -400]) cube([400, 800, 800]);
}
