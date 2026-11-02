// =============================================================================
// checks.scad · Engineered Lighting — the frame's boolean test suite
// =============================================================================
// Driven by tools/run_checks.py, which renders each check to an STL and
// measures its volume. OpenSCAD writes NO FILE AT ALL when a result is empty,
// and for most of these checks that is the pass condition.
//
// TWO KINDS OF CHECK, and they read in opposite directions:
//
//   hole:*   A HOLE THAT MUST EXIST. The probe is the ideal hole. It is
//            intersected with the FINISHED part, so:
//                empty  -> the material really was removed -> PASS
//                solid  -> the cut missed and the hole is not there -> FAIL
//            This is the inversion that catches the defect v7 shipped and that
//            I then shipped again in the yoke's arm: a cut whose coordinates
//            put it outside the part removes nothing, changes no mass, and
//            renders as a clean solid. Nothing but a boolean sees it.
//
//   clash:*  TWO THINGS THAT MUST NOT TOUCH. Straight intersection of the two,
//            positioned exactly as the assembly positions them:
//                empty  -> PASS
//                solid  -> collision, and the volume says how bad
//
// Everything is positioned from frame_params.scad, so a check cannot drift
// away from the geometry it is checking.
// =============================================================================

include <frame_params.scad>
use <frame.scad>

check = "none";
$fn = 64;
ep = 0.01;

// -----------------------------------------------------------------------------
// probes — the ideal shape of each hole that must exist
// -----------------------------------------------------------------------------

// the two reachable output-flange bolts through the cradle's motor-side plate
module probe_cradle_out_bolts() {
  for (i = [0 : out_bolt_n - 1]) if (out_bolt_up(i))
    rotate([out_bolt_a0 + i * 360 / out_bolt_n, 0, 0])
      translate([0, 0, out_bcd / 2]) rotate([0, 90, 0])
        translate([0, 0, 0.5]) cylinder(d = m3_clear_x - 0.6, h = cr_wall - 1);
}

// the tilt motor's wire path through the cradle's plate
module probe_cradle_wire() {
  translate([0.5, 0, 0]) rotate([0, 90, 0])
    cylinder(d = wire_hole_d - 3, h = cr_wall - 1);
}

// the tilt motor's rear bolt square through the yoke's arm
module probe_yoke_arm_bolts() {
  translate([0, 0, z_tilt])
    for (i = [0 : rear_bolt_n - 1])
      rotate([rear_bolt_a0 + i * 360 / rear_bolt_n, 0, 0])
        translate([0, 0, rear_bcd / 2]) rotate([0, 90, 0])
          translate([0, 0, arm_out + 0.5]) cylinder(d = m25_clear_x - 0.5, h = t_arm - 1);
}

// the tilt motor's wire path through the arm
module probe_yoke_arm_wire() {
  translate([arm_out + 0.5, 0, z_tilt]) rotate([0, 90, 0])
    cylinder(d = wire_hole_d - 4, h = t_arm - 1);
}

// the pan output bolts through the bridge
module probe_yoke_bridge_bolts() {
  translate([0, 0, -t_bridge + 0.5])
    bolt_ring_probe(out_bcd, m3_clear - 0.6, out_bolt_n, t_bridge - 1, out_bolt_a0);
}
module bolt_ring_probe(bcd, d, n, h, a0 = 0) {
  for (i = [0 : n - 1]) rotate([0, 0, a0 + i * 360 / n])
    translate([bcd / 2, 0, 0]) cylinder(d = d, h = h);
}

// the pan motor's rear bolts through the base plate
module probe_plate_bolts() {
  translate([0, 0, 0.5]) bolt_ring_probe(rear_bcd, m25_clear - 0.5, rear_bolt_n,
                                         t_plate - 1, rear_bolt_a0);
}

// the pan motor's wire path through the base plate
module probe_plate_wire() {
  translate([0, 0, 0.5]) cylinder(d = wire_hole_d - 3, h = t_plate - 1);
}

// the clamp screws through the cap
module probe_cap_screws() {
  for (sx = [-1, 1], sy = [-1, 1])
    translate([cr_wall + blk_in + sx * cap_bolt_x, sy * cap_bolt_y / 2,
               -axis_z + clamp_nip + 0.5])
      cylinder(d = m3_clear - 0.6, h = cap_z - clamp_nip - 1);
}

// -----------------------------------------------------------------------------
// assembly placement — one definition, used by every clash check
// -----------------------------------------------------------------------------
// ONE assembly frame, defined once. z_tilt is a YOKE-LOCAL coordinate (the
// yoke's own origin is its bridge TOP face), and the yoke itself is placed at
// z = -motor_len. Using z_tilt directly as an assembly coordinate puts the head
// motor_len too high and every head-vs-yoke clash fires spuriously — which is
// exactly what happened on the first run of this suite. Same class as reading a
// centre of mass in the wrong frame, which is in the defect log.
yoke_z     = -motor_len;              // yoke local z=0 -> assembly z
z_tilt_asm = yoke_z + z_tilt;         // the tilt axis, in ASSEMBLY coordinates

module at_tilt_motor()  { translate([out_face_x, 0, z_tilt_asm]) children(); }
module at_head(t = 0)   { translate([out_face_x, 0, z_tilt_asm]) rotate([t, 0, 0]) children(); }

// the tilt motor sits with its OUTPUT FACE at out_face_x, body running -X
module tilt_motor_at()  { at_tilt_motor() motor_solid_local(); }
module tilt_stator_at() { at_tilt_motor() motor_stator_local(); }
// local copies so checks.scad does not depend on frame.scad's `use` scope
module motor_solid_local() {
  rotate([0, -90, 0]) difference() {
    union() {
      cylinder(d1 = out_flat_od, d2 = motor_d, h = out_chamfer);
      translate([0, 0, out_chamfer]) cylinder(d = motor_d, h = motor_len - out_chamfer);
    }
    translate([0, 0, -ep]) cylinder(d = shaft_bore_d, h = motor_len + 1);
  }
}
module motor_stator_local() {
  rotate([0, -90, 0]) translate([0, 0, stator_x])
    cylinder(d = motor_d, h = motor_len - stator_x);
}
// the pan motor hangs under the base plate: rear face at z = 0, output at -motor_len
module pan_motor_at() { translate([0, 0, yoke_z]) motor_solid_local_z(); }
module motor_solid_local_z() {
  difference() {
    union() {
      cylinder(d1 = out_flat_od, d2 = motor_d, h = out_chamfer);
      translate([0, 0, out_chamfer]) cylinder(d = motor_d, h = motor_len - out_chamfer);
    }
    translate([0, 0, -ep]) cylinder(d = shaft_bore_d, h = motor_len + 1);
  }
}

// the payload, in the saddle
module payload_at() {
  translate([out_face_x + cr_wall + blk_in, 0, z_tilt_asm - axis_z]) rotate([90, 0, 0])
    cylinder(d = payload_od + payload_tol, h = payload_len, center = true);
}

// the yoke sits below the pan motor: its bridge TOP face at z = -motor_len
module yoke_at() { translate([0, 0, yoke_z]) yoke(); }
module cradle_at(t = 0) { at_head(t) cradle(); }
module cap_at(t = 0)    { at_head(t) cradle_cap(); }

// =============================================================================
// DISPATCH
// =============================================================================

// --- holes that must exist (expect EMPTY) ---
if      (check == "hole:cradle_out_bolts") intersection() { cradle(); probe_cradle_out_bolts(); }
else if (check == "hole:cradle_wire")      intersection() { cradle(); probe_cradle_wire(); }
else if (check == "hole:yoke_arm_bolts")   intersection() { yoke();   probe_yoke_arm_bolts(); }
else if (check == "hole:yoke_arm_wire")    intersection() { yoke();   probe_yoke_arm_wire(); }
else if (check == "hole:yoke_bridge_bolts")intersection() { yoke();   probe_yoke_bridge_bolts(); }
else if (check == "hole:plate_bolts")      intersection() { base_plate(); probe_plate_bolts(); }
else if (check == "hole:plate_wire")       intersection() { base_plate(); probe_plate_wire(); }
else if (check == "hole:cap_screws")       intersection() { cradle_cap(); probe_cap_screws(); }

// --- things that must not touch (expect EMPTY) ---
// the head against the tilt motor, at rest and at both tilt extremes
else if (check == "clash:cradle_v_motor_0")   intersection() { cradle_at(0);   tilt_motor_at(); }
else if (check == "clash:cradle_v_motor_p90") intersection() { cradle_at(90);  tilt_motor_at(); }
else if (check == "clash:cradle_v_motor_m90") intersection() { cradle_at(-90); tilt_motor_at(); }
else if (check == "clash:cap_v_motor_0")      intersection() { cap_at(0);      tilt_motor_at(); }
else if (check == "clash:cap_v_motor_p90")    intersection() { cap_at(90);     tilt_motor_at(); }
else if (check == "clash:cap_v_motor_m90")    intersection() { cap_at(-90);    tilt_motor_at(); }
// the head against the yoke, at rest and at both extremes
else if (check == "clash:cradle_v_yoke_0")    intersection() { cradle_at(0);   yoke_at(); }
else if (check == "clash:cradle_v_yoke_p90")  intersection() { cradle_at(90);  yoke_at(); }
else if (check == "clash:cradle_v_yoke_m90")  intersection() { cradle_at(-90); yoke_at(); }
else if (check == "clash:cap_v_yoke_p90")     intersection() { cap_at(90);     yoke_at(); }
else if (check == "clash:cap_v_yoke_m90")     intersection() { cap_at(-90);    yoke_at(); }
// the payload itself must clear the yoke through the whole sweep
else if (check == "clash:payload_v_yoke_p90") intersection() {
  translate([out_face_x, 0, z_tilt_asm]) rotate([90, 0, 0])
    translate([-out_face_x, 0, -z_tilt_asm]) payload_at();
  yoke_at();
}
// the cap must clear the motor-side plate (it is 0.5 mm away by design)
else if (check == "clash:cap_v_cradle")       intersection() { cradle(); cradle_cap(); }
// nothing printed may enter the STATOR zone — that is what clamps a motor solid
else if (check == "clash:cradle_v_stator")    intersection() { cradle_at(0); tilt_stator_at(); }
else if (check == "clash:yoke_v_pan_motor")   intersection() { yoke_at(); pan_motor_at(); }
else if (check == "clash:plate_v_pan_motor")  intersection() { base_plate(); pan_motor_at(); }
// The hard-stop post must clear the bridge at EVERY heading. Rotating the yoke
// through 72 positions and intersecting is correct but takes minutes; it also
// asks a muddled question, because the LUG is supposed to hit the post. The
// sharp question is: does the post foul the bridge DISC? As the yoke turns, the
// disc sweeps a cylinder of radius bridge_r over the bridge's own z-range, so
// one intersection against that swept volume answers it for all headings at
// once.
else if (check == "clash:post_v_bridge")      intersection() {
  base_plate();
  translate([0, 0, yoke_z - t_bridge]) cylinder(r = bridge_r, h = t_bridge);
}
// At pan = 0 the machine must be at MID-TRAVEL, not sitting on its own stop.
// The lug and the post at the same azimuth means home IS the limit and half the
// travel is on the wrong side of it.
else if (check == "clash:lug_v_post_home")    intersection() { base_plate(); yoke_at(); }
// ...and the post must stop short of the ARM, which sweeps the same way
else if (check == "clash:post_v_arm")         intersection() {
  base_plate();
  translate([0, 0, z_tilt_asm - arm_pad_r])
    cylinder(r = sqrt(pow(-arm_out, 2) + pow(arm_w / 2, 2)),
             h = -z_tilt - t_bridge + arm_pad_r);
}

// --- visual: the whole machine ---
else if (check == "assembly") {
  color("#d8a93a") base_plate();
  color("#b8bcc3") pan_motor_at();
  color("#e8862a") yoke_at();
  color("#b8bcc3") tilt_motor_at();
  color("#39c0bd") cradle_at(0);
  color("#2aa8a5") cap_at(0);
  color("#9aa0a9") payload_at();
}
