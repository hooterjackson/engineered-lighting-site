// =============================================================================
// assembly.scad · Engineered Lighting — robotic spotlight, THE WHOLE MACHINE
// v8 (2026-07-30)
// =============================================================================
//
//   include <frame_params.scad>   <- the same single copy of every dimension
//   use     <frame.scad>          <- the real printed parts, as modules only
//
// `use` imports the part modules without running frame.scad's own render block,
// so this file draws the assembly and only the assembly.
//
// IF THE VERSION BANNER BELOW PRINTS `undef`, STOP. Your frame_params.scad is
// not the one these files were written against, and OpenSCAD will quietly
// collapse the missing names to undef, drop the geometry they position, write
// a valid-looking STL and exit 0. That is how you get "only some of the parts
// render". Work in the repo, not in a downloads folder with older copies.
//
//   view  = assembled | exploded
//   pan / tilt / slide            pose it
//   show_cap = false              look inside the clamp
//   clip = none | front | side    section it
//
// Colours: gold = base plate · orange = yoke · teal = head · grey = bought
// =============================================================================

include <frame_params.scad>
use <frame.scad>

/* [Pose] */
view  = "assembled";  // [assembled, exploded]
pan   = 0;            // [-180:5:180]
tilt  = 0;            // [-90:5:90]
slide = 0;            // [-4:0.5:4]
/* [Show] */
show_bolts = true;
show_wires = true;
show_bench = true;
show_cap   = true;
show_beam  = false;
clip       = "none";  // [none, front, side]

$fn = 48;
ep = 0.01;

echo(str(cad_version, " assembly · if this says undef you have a mismatched file set"));

e       = (view == "exploded") ? 1 : 0;
E_BENCH = 90 * e;  E_PLATE = 34 * e;  E_PANM = 20 * e;  E_YOKE = 76 * e;
E_TILTM = 46 * e;  E_HEAD  = 40 * e;  E_CAP  = 58 * e;  E_BOLT = 18 * e;
E_HOUS  = 24 * e;   // payload lifts OUT of the saddle, upward, and less far
                    // than the cap so the order reads: cap off, housing out.

// ONE assembly frame, stated once. z_tilt is a YOKE-LOCAL coordinate (the
// yoke's origin is its bridge TOP face); the yoke hangs at z = -motor_len.
// Conflating those two frames is what made the first run of checks.scad report
// six collisions that were not there.
yoke_z     = -motor_len;
z_tilt_asm = yoke_z + z_tilt;

// ------------------------------------------------------------------ bought --
module screw(d = 3, len = 12, hd = m3_head_d, hh = m3_head_h) {
  color("#33343a") { cylinder(d = hd, h = hh); translate([0, 0, -len]) cylinder(d = d, h = len + ep); }
}
// heads at z = 0, driven -Z
module screw_ring(bcd, n, a0, len, d = 3, hd = m3_head_d, hh = m3_head_h) {
  for (i = [0 : n - 1]) rotate([0, 0, a0 + i * 360 / n])
    translate([bcd / 2, 0, 0]) screw(d, len, hd, hh);
}

// The motor, drawn from the STEP's real numbers: a flat D47 output annulus, a
// 1 mm 45 deg chamfer out to D49, and NO BOSS. Origin = the OUTPUT FACE, body
// running -Z, so it meets a printed part exactly as the real one does.
module rmd_motor() {
  difference() {
    union() {
      color("#b8bcc3") {
        rotate([180, 0, 0]) {
          cylinder(d1 = out_flat_od, d2 = motor_d, h = out_chamfer);
          translate([0, 0, out_chamfer]) cylinder(d = motor_d, h = motor_len - out_chamfer);
        }
      }
      // the connectors are RECESSES in the real casting, so nothing is drawn
      // standing out of the barrel. Nothing on this motor exceeds D49.
    }
    translate([0, 0, ep]) cylinder(d = shaft_bore_d, h = motor_len + 2, center = true);
    // the output's tapped holes, 2.5 mm deep, breaking into the rotor cavity
    translate([0, 0, -out_thread_depth])
      for (i = [0 : out_bolt_n - 1]) rotate([0, 0, out_bolt_a0 + i * 360 / out_bolt_n])
        translate([out_bcd / 2, 0, 0]) cylinder(d = out_bolt_d - 0.5, h = out_thread_depth + ep);
  }
  // The rear square's tapped holes are INSIDE the casting; drawing them as
  // solid cylinders inside the body just makes coincident surfaces and a
  // z-fighting starburst on the rear face. They are not drawn.
}

// DLH-3UP-EH. Beam fires +Y; barrel axis along Y. Not finned — four channels
// cut into a smooth sleeve — so the drawn diameter is the real clamped one.
module led_housing() {
  rotate([-90, 0, 0]) {
    color("#9aa0a9") {
      difference() {
        cylinder(d = payload_od, h = payload_body, center = true);
        for (i = [0 : 3]) rotate([0, 0, i * 90])
          translate([payload_od / 2, 0, 0]) cube([1.2, 3, payload_body + 2], center = true);
      }
      translate([0, 0, -payload_body / 2 - payload_stub_l])
        cylinder(d = payload_stub_d, h = payload_stub_l + ep);
    }
    color("#34363c") translate([0, 0, payload_body / 2 - 3]) cylinder(d = payload_od - 4.4, h = 3);
    color("#f4ecc9") for (i = [0 : 2]) rotate([0, 0, i * 120 + 30])
      translate([4.7, 0, payload_body / 2 - 1.4]) cube([3.4, 3.4, 0.9], center = true);
    if (show_beam) color("#fff3c4", 0.13)
      translate([0, 0, payload_body / 2]) cylinder(d1 = 16, d2 = 74, h = 120);
  }
}

module c_clamp() {
  color("#4a4d54") {
    translate([-9, -30, -10]) cube([18, 30, 10]);
    translate([-9, -30, t_plate]) cube([18, 30, 10]);
    translate([-9, -2, -10]) cube([18, 10, t_plate + 20]);
    translate([0, -18, -21]) cylinder(d = 6.5, h = 12);
    translate([0, -18, -27]) cylinder(d = 17, h = 5.5);
  }
}
// The bench edge. The machine hangs OFF it: only the aft tongue lands on the
// bench, and the hub — with the pan motor and everything under it — overhangs
// the edge. So the bench must stop short of the hub, not run under it.
bench_edge_y = -(hub_r + 3);
module bench() {
  color("#c9a678") translate([-90, bench_edge_y - 130, -16]) cube([180, 130, 16]);
}

module wire(pts, d = 4.6) {
  color("#26262b") for (i = [0 : len(pts) - 2]) hull() {
    translate(pts[i]) sphere(d = d); translate(pts[i + 1]) sphere(d = d); }
}
module guide(a, b) {
  color("#9a9a9a", 0.8) hull() { translate(a) sphere(d = 1.1); translate(b) sphere(d = 1.1); }
}

// =============================================================================
//                                   SCENE
// world: pan axis = Z · tilt axis = X · beam fires +Y · plate's mating face z=0
// =============================================================================
module scene() {

  // 1 · bench and C-clamp, gripping the base plate's aft tongue
  if (show_bench) translate([0, 0, -E_BENCH]) {
    bench();
    translate([0, bench_edge_y - 14, 0]) c_clamp();
  }

  // 2 · base plate
  translate([0, 0, E_PLATE]) {
    color("#d8a93a") base_plate();
    if (show_bolts) translate([0, 0, t_plate - m25_head_h + E_BOLT])
      screw_ring(rear_bcd, rear_bolt_n, rear_bolt_a0, t_plate + 8,
                 rear_bolt_d, m25_head_d, m25_head_h);
  }

  // 3 · pan motor, hanging under the plate: REAR up, OUTPUT down
  translate([0, 0, -E_PANM]) rmd_motor();

  // ------------------------------------------------------------ pan group ---
  rotate([0, 0, pan]) translate([0, 0, yoke_z - E_YOKE]) {

    color("#e8862a") yoke();

    // 4 · four M3 up through the bridge into the pan output. M3 x 10: the
    //     tapped hole is 2.5 mm deep and opens into the rotor, so a longer
    //     screw bottoms and never clamps.
    if (show_bolts) translate([0, 0, -t_bridge - E_BOLT]) rotate([180, 0, 0])
      screw_ring(out_bcd, out_bolt_n, out_bolt_a0, out_screw_len(t_bridge));

    // 5 · tilt motor on the arm's INNER face, output facing +X (inboard)
    translate([arm_in + E_TILTM, 0, z_tilt]) rotate([0, 90, 0]) rmd_motor();
    // ...bolted from OUTSIDE the arm, so a driver reaches the heads
    if (show_bolts) translate([arm_out - E_BOLT - E_TILTM, 0, z_tilt]) rotate([0, -90, 0])
      screw_ring(rear_bcd, rear_bolt_n, rear_bolt_a0, t_arm + rear_thread_depth - 2,
                 rear_bolt_d, m25_head_d, m25_head_h);

    // ------------------------------------------------------- head group ----
    translate([0, 0, z_tilt]) rotate([tilt, 0, 0]) translate([E_HEAD, 0, 0]) {

      color("#39c0bd") translate([out_face_x, 0, 0]) cradle();

      // 6 · the two output-flange bolts a driver can reach: the ones above the
      //     split line, driven while the cap is still off. M3 x 10.
      if (show_bolts) translate([out_face_x + cr_wall + E_BOLT, 0, 0])
        for (i = [0 : out_bolt_n - 1]) if (out_bolt_up(i))
          rotate([out_bolt_a0 + i * 360 / out_bolt_n, 0, 0])
            translate([0, 0, out_bcd / 2]) rotate([0, 90, 0])
              screw(3, out_screw_len(cr_wall));

      // 7 · the housing lies in the saddle; the cap pinches it. Both sit
      //     axis_z BELOW the tilt axis — that offset IS the balance.
      translate([out_face_x + cr_wall + blk_in, slide, -axis_z + E_HOUS]) led_housing();
      if (show_cap) color("#2aa8a5") translate([out_face_x, 0, E_CAP]) cradle_cap();
      if (show_bolts) for (sx = [-1, 1], sy = [-1, 1])
        translate([out_face_x + cr_wall + blk_in + sx * cap_bolt_x, sy * cap_bolt_y / 2,
                   -axis_z + cap_z + E_CAP + E_BOLT])
          screw(3, cap_z - clamp_nip + pilot_len - 2);

      // 8 · the head's share of the cable run: out of the housing's rear stub,
      //     along the channel in the motor-side plate, then onto the tilt axis
      //     and into the motor's hollow shaft
      if (show_wires) wire([
        [out_face_x + cr_wall + blk_in, slide - payload_body / 2 - payload_stub_l + 1, -axis_z],
        [out_face_x + cr_wall - trough_d / 2, -cr_len / 2 + 3, -axis_z],
        [out_face_x + cr_wall - trough_d / 2, -3, 0],
        [out_face_x + 2, 0, 0], [out_face_x - 3, 0, 0]]);
    }

    // 9 · the frame's share: through the tilt motor's bore, out of the arm, up
    //     the arm's outer trough, along the bridge trough, up the pan bore
    if (show_wires) wire([
      [arm_in - 2, 0, z_tilt], [arm_out + trough_d / 2, 0, z_tilt],
      [arm_out + trough_d / 2, 0, -t_bridge - trough_d],
      [arm_out + 6, 0, -t_bridge + trough_d / 2],
      [-10, 0, -t_bridge + trough_d / 2], [0, 0, 4]]);
  }

  // 10 · and up out of the pan motor into the base plate's trough, aft
  if (show_wires) translate([0, 0, E_PLATE]) wire([
    [0, 0, -motor_len + 4], [0, 0, t_plate - trough_d / 2],
    [0, -20, t_plate - trough_d / 2], [0, -tongue_len + 6, t_plate - trough_d / 2]]);

  if (view == "exploded") {
    guide([0, 0, E_PLATE + t_plate + 14], [0, 0, yoke_z - E_YOKE - t_bridge - 14]);
    guide([arm_out - E_TILTM - E_BOLT - 16, 0, z_tilt_asm - E_YOKE],
          [out_face_x + E_HEAD + head_len + 16, 0, z_tilt_asm - E_YOKE]);
    guide([out_face_x + E_HEAD + cr_wall + blk_in, 0, z_tilt_asm - E_YOKE + cap_z + E_CAP + 12],
          [out_face_x + E_HEAD + cr_wall + blk_in, 0, z_tilt_asm - E_YOKE - base_z - 8]);
  }
}

if (clip == "none") scene();
else intersection() {
  scene();
  if (clip == "front") translate([-400, -400, -400]) cube([800, 400, 800]);
  else translate([-400, -400, -400]) cube([400, 800, 800]);
}
