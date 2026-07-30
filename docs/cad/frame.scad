// =============================================================================
// frame.scad · Engineered Lighting — robotic spotlight, PRINTED FRAME
// v8 (2026-07-30)  — ground-up rebuild, single-arm cantilever
// =============================================================================
//
// FOUR printed parts, three test coupons. Numbers live in frame_params.scad;
// this file is nothing but geometry.
//
//   base_plate   pan motor bolts up into it; carries the C-clamp tongue, the
//                cable trough, and the hard-stop post.
//   yoke         ONE piece, ONE arm. A bridge disc that bolts to the pan
//                output, and a single arm carrying the tilt motor.
//   cradle       the head's saddle: bolts to the tilt output, holds the
//                housing's lower half.
//   cradle_cap   upper half of the clamp.
//   tol_coupon   PRINT THIS FIRST. Measures your printer's hole shrink and
//                shaft growth, which every fit in the project derives from.
//   fit_coupon   both motor bolt circles, on SEPARATE tiles so neither can
//                mask the other.
//   bore_gauge   the real clamp in miniature: does the housing slide?
//
// WHAT CHANGED IN v8, AND WHY
//
//  · THE IDLE SIDE IS GONE. No trunnion, no bearing carrier, no 608, six fewer
//    screws, one fewer arm — 62 g of a 177 g machine. The head cantilevers off
//    the tilt motor's own output. The load case, including what is unverified
//    about it, is in frame_params.scad and echoed below on every render.
//    It also deletes two blocking defects outright: the head that could not be
//    inserted between two arms (needed 19.9 mm of travel, had 4.0) and the
//    trunnion screw heads that landed inside their own shank.
//
//  · THE MOTOR IS READ, NOT GUESSED. ref/RMD-L-5005-S.STEP is in the repo and
//    ref/RMD-L-5005-S.md says what came out of it. There is no output boss; the
//    face is flat; nothing protrudes past D49; the stationary housing starts
//    3.0 mm back from the output face; and the output's tapped holes are 2.5 mm
//    deep and break into the rotor cavity. Every M3 length here derives from
//    that last number instead of being chosen.
//
//  · EVERY HOLE THAT MUST EXIST IS PROVEN TO EXIST. v7's cradle had no
//    output-flange bolt holes at all — the cut was a centred cylinder 2.865 mm
//    short of the plate, so it removed nothing, changed no mass and showed in
//    no render. Here, a cut that must break through is defined by the two
//    PLANES it has to span, and checks.scad measures what each one removes.
//
//  · NOTHING BRIDGES. The hard stop is a post and a lug that collide, not a
//    post in an arc groove, so v7's 1565 mm2 of flat groove roof over a 0.6 mm
//    clearance does not exist. Round pockets are hexagons vertex-up. Horizontal
//    holes get their own fit class and a self-supporting roof.
//
//  · PRINT ORIENTATION IS CHECKED, NOT ASSERTED. v7's p_cradle put the part
//    1.74 mm below the bed and bore_gauge floated its second half 16 mm in the
//    air. Every p_* module here lands the part ON z = 0, and checks.scad
//    measures the exported STL to prove it.
//
// BUILD ORDER
//  0 tol_coupon. Set hole_comp / hole_comp_h / shaft_comp from what it tells
//    you. Everything below assumes those three numbers are yours, not mine.
//  1 fit_coupon against the real motor, bore_gauge against the real housing.
//  2 Cradle onto the tilt motor: turn the output until two holes sit above the
//    split line, then two M3 x 10 through the plate. Do this on the bench with
//    the motor loose, while a driver still reaches straight in.
//  3 Tilt motor onto the yoke arm, from OUTSIDE the arm: four M2.5 x 16 through
//    the arm into the motor's rear square. The head is already on and hangs
//    inboard; nothing is trapped.
//  4 Yoke onto the pan motor: four M3 x 10 up through the bridge.
//  5 Base plate down onto the pan motor's rear: four M2.5 x 16 through the
//    plate's counterbores. THE CONNECTOR CLOCKING IS DECIDED HERE, not earlier.
//    The rear square offers exactly four positions, so turn the motor NOW so
//    its connector faces the cable trough at 270 deg. (v7 put this instruction
//    on the step where turning the motor cannot change it, costing up to three
//    teardowns.)
//  6 Wires: housing -> the channel in the cradle's plate -> tilt motor's bore
//    -> down the arm's trough -> under the bridge -> pan motor's bore -> the
//    base plate's trough -> out aft along the tongue. Ties at the two slots.
//  7 Housing into the saddle, cap on, slide to balance, then nip the four M3.
// =============================================================================

include <frame_params.scad>

/* [What to render] */
part = "all"; // [tol_coupon, fit_coupon, bore_gauge, base_plate, yoke, cradle, cradle_cap, all]

$fn = 64;
eps = 0.01;      // only ever used to break coplanar faces, never as a fit

// -----------------------------------------------------------------------------
// SANITY — the derived chain, echoed and asserted. Read these numbers.
// -----------------------------------------------------------------------------
echo(str(cad_version, " frame · arm_reach=", arm_reach, "  bore_x=", bore_x,
         "  z_tilt=", z_tilt, "  bridge_r=", bridge_r));
echo(str("  head: sweep=", head_sweep, " vs drop=", drop,
         " (clears by ", drop - head_sweep, ")   slide=", slide_range, " mm"));
echo(str("  plate_z=", plate_z, " must be >= bolt_pad_z + axis_z = ", bolt_pad_z + axis_z));
echo(str("  M3 into the output flange: M3 x ", out_screw_len(t_bridge),
         " (bridge), M3 x ", out_screw_len(cr_wall),
         " (cradle) — the tapped hole is only ", out_thread_depth, " deep"));
echo(str("  hard stop: post r=", stop_post_r, ", inner edge ",
         stop_post_r - stop_post_d / 2, " vs bridge_r ", bridge_r,
         "; travel ", pan_travel_deg, " deg"));
echo(str("  CANTILEVER: ", head_load_N, " N radial, ", head_moment_Nm,
         " N.m overhung = ", head_moment_Nm / motor_peak_Nm * 100,
         "% of peak torque; bolt pry ", bolt_pry_N, " N"));

assert(drop > head_sweep + 2,
       "drop must clear head_sweep with margin — the head would hit the bridge");
assert(plate_z >= bolt_pad_z + axis_z,
       "plate_z does not reach the highest reachable output bolt's head");
assert(stop_post_r - stop_post_d / 2 > bridge_r,
       "the hard-stop post would foul the bridge disc as the yoke turns");
assert(stop_engage < t_bridge,
       "the hard-stop post would punch through the bridge");
assert(out_thread_use < out_thread_depth,
       "output screws would bottom in the motor's tapped hole");
assert(trough_d <= t_bridge - 2, "cable trough leaves less than 2 mm of web");
// the clamp screws must clear the bore on the inside and the saddle edge outside
assert(cap_bolt_x - m3_clear / 2 > bore_d / 2,
       "clamp screws would break into the payload bore");
assert(cap_bolt_x + m3_clear / 2 < blk_in,
       "clamp screws would break out of the side of the saddle");
// and the cap must not touch the motor-side plate
assert(cap_clear_plate > 0.3, "cap would rub the motor-side plate");
// the clamp must NEVER bottom out: the nip has to exceed the worst-case travel
// needed to reach a minimum-tolerance barrel, or the screws clamp air
assert(clamp_nip > (bore_d - (payload_od - payload_tol)) / 2,
       "clamp bottoms out before it grips a minimum-tolerance barrel");

// -----------------------------------------------------------------------------
// HELPERS
// -----------------------------------------------------------------------------

// A ring of holes drilled along Z. h is the FULL length and it is centred.
module bolt_ring(bcd, d, n, h, a0 = 0) {
  for (i = [0 : n - 1]) rotate([0, 0, a0 + i * 360 / n])
    translate([bcd / 2, 0, 0]) cylinder(d = d, h = h, center = true);
}

// The same ring drilled along X. THIS IS THE ONE v7 GOT WRONG: it used a
// centred cylinder and left it 2.865 mm short of the plate it had to pierce.
// Here the caller passes the two X PLANES the hole must span, so the hole is
// defined by the material it has to get through rather than by a length that
// has to be guessed right. Overshoot is added at both ends automatically.
module bolt_ring_x(bcd, d, n, x0, x1, a0 = 0, over = 2) {
  for (i = [0 : n - 1]) rotate([a0 + i * 360 / n, 0, 0])
    translate([0, 0, bcd / 2]) rotate([0, 90, 0])
      translate([0, 0, x0 - over]) cylinder(d = d, h = (x1 - x0) + 2 * over);
}

// Only the holes whose heads a driver can actually reach (above the split line).
module out_bolts_up_x(d, x0, x1, over = 2) {
  for (i = [0 : out_bolt_n - 1]) if (out_bolt_up(i))
    rotate([out_bolt_a0 + i * 360 / out_bolt_n, 0, 0])
      translate([0, 0, out_bcd / 2]) rotate([0, 90, 0])
        translate([0, 0, x0 - over]) cylinder(d = d, h = (x1 - x0) + 2 * over);
}

// A horizontal (bridged) round hole, drawn as a hexagon with a VERTEX UP so its
// roof is two 60 deg faces instead of a flat bridge. Sized across flats to the
// nominal, so a cable or bolt of that size still passes.
module hex_hole_x(d, x0, x1, over = 2) {
  translate([x0 - over, 0, 0]) rotate([0, 90, 0]) rotate([0, 0, 30])
    cylinder(d = d / cos(30), h = (x1 - x0) + 2 * over, $fn = 6);
}

// Hex pocket, vertex up, cut downward into a face. Same reason.
module hex_pocket(d, depth) {
  rotate([0, 0, 30]) cylinder(d = d / cos(30), h = depth, $fn = 6);
}

// The motor as an OBSTRUCTION. Origin = the OUTPUT FACE, body along -X, which
// is how every printed part meets it. Used by the assembly view and by
// checks.scad; no printed part depends on it.
module motor_solid() {
  rotate([0, -90, 0]) difference() {
    union() {
      cylinder(d1 = out_flat_od, d2 = motor_d, h = out_chamfer);
      translate([0, 0, out_chamfer])
        cylinder(d = motor_d, h = motor_len - out_chamfer);
    }
    translate([0, 0, -eps]) cylinder(d = shaft_bore_d, h = motor_len + 1);
  }
}

// The STATIONARY part of it. Anything a printed part touches in here clamps the
// motor solid, which is the whole reason stator_x was worth reading out of the
// STEP.
module motor_stator_zone() {
  rotate([0, -90, 0]) translate([0, 0, stator_x])
    cylinder(d = motor_d + 2 * connector_plug_clear, h = motor_len - stator_x);
}

// -----------------------------------------------------------------------------
// BASE PLATE
// origin: pan axis. Plate occupies z = 0 .. t_plate. The pan motor's REAR face
// mates at z = 0 and the motor hangs below. Tongue runs -Y to the C-clamp.
// -----------------------------------------------------------------------------
module base_plate() {
  difference() {
    union() {
      cylinder(r = hub_r, h = t_plate);
      translate([-tongue_w / 2, -tongue_len, 0])
        cube([tongue_w, tongue_len, t_plate]);

      rotate([0, 0, stop_post_a]) {
        // spur out to the post
        hull() {
          cylinder(r = hub_r, h = t_plate);
          translate([stop_post_r, 0, 0]) cylinder(d = stop_post_d + 6, h = t_plate);
        }
        // the post itself, hanging DOWN past the motor into the bridge's plane
        translate([stop_post_r, 0, -post_h]) cylinder(d = stop_post_d, h = post_h + eps);
        // Tapered buttress. The post is struck TANGENTIALLY, so the buttress is
        // swept in the tangential plane where the bending actually is. Worst
        // case is the motor's own peak torque: 0.42 N.m at stop_post_r is about
        // 11 N, giving under 1 MPa in the post's root section — 25x margin even
        // across layer lines. This is cheap insurance on top of that, because a
        // hard stop is the one feature that gets hit.
        for (s = [-1, 1]) translate([stop_post_r, 0, 0]) rotate([0, 0, s * 90])
          rotate([90, 0, 0]) linear_extrude(height = stop_post_d, center = true)
            polygon([[0, 0], [0, -butt_h], [stop_post_d * 0.9, 0]]);
      }
    }

    // pan motor's rear bolt square, counterbored from the TOP
    translate([0, 0, t_plate / 2])
      bolt_ring(rear_bcd, m25_clear, rear_bolt_n, t_plate + 2, rear_bolt_a0);
    translate([0, 0, t_plate - m25_head_h])
      bolt_ring(rear_bcd, m25_head_d + 0.6, rear_bolt_n, 2 * m25_head_h + eps, rear_bolt_a0);

    // RELIEF for the motor's own cover-screw heads: they sit on a D44 circle
    // only 0.300 mm below the rear face, so a flat plate clears them by 0.3 mm
    // and a first-layer blob does not. Take 0.8 mm out and stop worrying.
    translate([0, 0, -eps]) difference() {
      cylinder(d = cover_head_bcd + cover_head_d + 3, h = 0.8 + eps);
      translate([0, 0, -1]) cylinder(d = cover_head_bcd - cover_head_d - 3, h = 3);
    }

    // the pan motor's hollow shaft comes up here
    translate([0, 0, -eps]) cylinder(d = wire_hole_d, h = t_plate + 1);

    // cable trough: centre hole -> aft along the tongue, OPEN on top, one
    // continuous channel with no gap and no tunnel
    translate([-trough_w / 2, -(hub_r + tongue_len), t_plate - trough_d])
      cube([trough_w, hub_r + tongue_len, trough_d + 1]);

    // cable-tie slots straddling the trough. They stay tie_clear away from the
    // trough wall: v7's sat 0.150 mm off it, the slicer discarded the sliver
    // and the slot merged into the channel.
    for (yy = [-24, -42]) for (s = [-1, 1])
      translate([s * (trough_w / 2 + tie_clear), yy - 1.7, -eps])
        cube([2.2, 3.4, t_plate + 1]);
  }
}

// -----------------------------------------------------------------------------
// YOKE — bridge disc + ONE arm
// origin: pan axis. The bridge's TOP face (which mates to the pan output) is at
// z = 0, so the bridge occupies z = -t_bridge .. 0. The arm hangs down on -X.
// -----------------------------------------------------------------------------
module yoke() {
  difference() {
    union() {
      translate([0, 0, -t_bridge]) cylinder(r = bridge_r, h = t_bridge);

      // hard-stop lug: a radial finger on the rim, full bridge thickness, open
      // on every side. Nothing to bridge, nothing to sag.
      rotate([0, 0, stop_lug_a]) translate([0, 0, -t_bridge])
        linear_extrude(height = t_bridge)
          polygon([[0, -stop_lug_w / 2], [stop_lug_r, -stop_lug_w / 2],
                   [stop_lug_r, stop_lug_w / 2], [0, stop_lug_w / 2]]);

      // the arm: a neck at the bridge, widening to the motor pad at the bottom
      hull() {
        translate([arm_out, -arm_neck_w / 2, -t_bridge]) cube([t_arm, arm_neck_w, eps]);
        translate([arm_out, -arm_w / 2, z_tilt]) cube([t_arm, arm_w, eps]);
      }
      // round pad about the tilt axis, so the rear bolt circle has meat
      translate([arm_out, 0, z_tilt]) rotate([0, 90, 0])
        cylinder(r = arm_pad_r, h = t_arm);
    }

    // --- bridge: pan output bolts, driven UP from underneath ---
    translate([0, 0, -t_bridge / 2])
      bolt_ring(out_bcd, m3_clear, out_bolt_n, t_bridge + 2, out_bolt_a0);

    // the pan motor's hollow shaft
    translate([0, 0, -t_bridge - eps]) cylinder(d = wire_hole_d, h = t_bridge + 1);

    // cable trough under the bridge, OPEN downward, running out toward the arm
    translate([-bridge_r, -trough_w / 2, -t_bridge - eps])
      cube([bridge_r, trough_w, trough_d + eps]);

    // --- arm: the tilt motor's rear square, drilled from OUTSIDE so a driver
    // can reach the heads at step 3 with the head already fitted ---
    // USE THE HELPER. I first hand-rolled this transform and put the holes at
    // x = +17.4..+29.4 while the arm sits at -28.4..-18.4 — the identical
    // never-cut-anything defect I had just reviewed v7 for, made the identical
    // way: by writing a length and a sign instead of naming the two planes the
    // hole has to get through. bolt_ring_x takes x0 and x1 for that reason.
    translate([0, 0, z_tilt])
      bolt_ring_x(rear_bcd, m25_clear_x, rear_bolt_n, arm_out, arm_in, rear_bolt_a0);
    // ...and their head counterbores, sunk into the OUTER face
    translate([0, 0, z_tilt])
      bolt_ring_x(rear_bcd, m25_head_d + 0.6, rear_bolt_n,
                  arm_out, arm_out + m25_head_h, rear_bolt_a0, over = 1);

    // the tilt motor's hollow shaft through the arm — horizontal, so hex roof
    translate([0, 0, z_tilt]) hex_hole_x(wire_hole_d, arm_out, arm_in);

    // cable trough down the arm's OUTER face, open outward, from the tilt axis
    // up to the bridge's trough. One continuous open channel.
    translate([arm_out - eps, -trough_w / 2, z_tilt])
      cube([trough_d + eps, trough_w, -z_tilt - t_bridge + trough_d]);

    // hex lightening pocket in the arm, vertex up, cut from the outer face.
    // Stays inside the rear bolts' head seats.
    translate([arm_out - eps, 0, z_tilt]) rotate([0, 90, 0])
      hex_pocket(arm_pocket_d, arm_pocket_z + eps);
  }
}

// -----------------------------------------------------------------------------
// CRADLE — the head's saddle
// origin: the TILT AXIS, in the plane of the motor's OUTPUT FACE.
//   x = 0 .. cr_wall          the plate that lands on the output face
//   x = cr_wall .. head_len   the saddle
//   payload axis: along Y at z = -axis_z.   split line: z = -axis_z
// -----------------------------------------------------------------------------
module cradle() {
  difference() {
    union() {
      translate([0, -cr_len / 2, -axis_z - base_z])
        cube([cr_wall, cr_len, base_z + plate_z]);
      translate([cr_wall, -cr_len / 2, -axis_z - base_z])
        cube([2 * blk_in, cr_len, base_z]);
    }

    // THE BORE, along Y at the payload axis, plus everything above the split
    // line. Open upward, so in print orientation this is a valley and never a
    // roof.
    translate([cr_wall + blk_in, cr_len / 2 + 1, -axis_z]) rotate([90, 0, 0])
      cylinder(d = bore_d, h = cr_len + 2);
    translate([cr_wall + blk_in - bore_d / 2, -cr_len / 2 - 1, -axis_z])
      cube([bore_d, cr_len + 2, base_z + plate_z + 1]);

    // --- the two output-flange bolt holes ---
    // Defined by the two X PLANES they must span. This is the v7 blocking
    // defect and the reason the helper takes x0 and x1 instead of a length.
    out_bolts_up_x(m3_clear_x, 0, cr_wall);

    // the tilt motor's hollow shaft through the plate — horizontal, hex roof
    hex_hole_x(wire_hole_d, 0, cr_wall);

    // cable channel in the plate's INNER face, from the rear edge in to the
    // bore. Open along its whole length: the cable is laid in, not threaded.
    translate([cr_wall - trough_d, -cr_len / 2 - eps, -trough_w / 2])
      cube([trough_d + eps, cr_len / 2 + eps, trough_w]);

    // cap-screw pilots, self-tapping, down from the split line
    for (sx = [-1, 1], sy = [-1, 1])
      translate([cr_wall + blk_in + sx * cap_bolt_x, sy * cap_bolt_y / 2,
                 -axis_z - pilot_len]) cylinder(d = m3_pilot, h = pilot_len + eps);

    // dead-corner chamfers under the saddle
    for (s = [-1, 1])
      translate([cr_wall - eps, s * cr_len / 2, -axis_z - base_z])
        rotate([45, 0, 0]) translate([0, -keel_chamf / 2, -keel_chamf / 2])
          cube([2 * blk_in + 2 * eps, keel_chamf, keel_chamf]);
  }
}

// -----------------------------------------------------------------------------
// CRADLE CAP — upper half of the clamp
// Same origin as the cradle. Its bore sits clamp_nip ABOVE the split line, so
// the SCREWS set the grip and it can never bottom out on a small barrel.
// -----------------------------------------------------------------------------
module cradle_cap() {
  difference() {
    // A plain block. No ears: with one side plate there is nothing for an ear to
    // land on, and this puts the cap's full height under every screw head
    // instead of the 2.6 mm ear in the defect log.
    translate([cr_wall + blk_in - cap_w / 2, -cr_len / 2, -axis_z + clamp_nip])
      cube([cap_w, cr_len, cap_z - clamp_nip]);
    // the bore's upper half, and everything below the split line
    translate([cr_wall + blk_in, cr_len / 2 + 1, -axis_z]) rotate([90, 0, 0])
      cylinder(d = bore_d, h = cr_len + 2);
    translate([cr_wall + blk_in - bore_d / 2, -cr_len / 2 - 1, -axis_z - base_z])
      cube([bore_d, cr_len + 2, base_z]);
    // clamp screws
    for (sx = [-1, 1], sy = [-1, 1])
      translate([cr_wall + blk_in + sx * cap_bolt_x, sy * cap_bolt_y / 2, -axis_z - 1])
        cylinder(d = m3_clear, h = cap_z + 2);

    // NO CROWN POCKET. v7 had one and it was a 23 x 25 mm flat bridge carrying
    // the clamp's bore. I first "fixed" that by making it a hexagon — which is
    // wrong, and worth writing down: the vertex-up trick only helps a hole whose
    // AXIS IS HORIZONTAL, where the hexagon's apex becomes the roof. A pocket
    // cut straight down into a face has a flat roof whatever its plan shape is,
    // and this cap prints crown-DOWN (so the bore is a valley), which turns that
    // roof into a 32.7 mm bridge directly under the clamp.
    //
    // So there is no pocket. If this ever needs lightening, the print-safe way
    // is channels running along Y, through the crown, hexagonal in section with
    // a vertex up — open at both ends, so nothing bridges. There is 7.1 mm of
    // crown above the bore to play with. It is not worth the ~3 g here, and the
    // mass is answered anyway: axis_z absorbs it by construction.
  }
}

// -----------------------------------------------------------------------------
// TEST COUPONS
// -----------------------------------------------------------------------------

// Measures the three numbers every fit in this project derives from.
module tol_coupon() {
  w = 84; h = 34; t = 4;
  difference() {
    cube([w, h, t]);
    for (i = [0 : 6]) translate([8 + i * 11, 9, -eps])
      cylinder(d = 3 + (i - 3) * 0.1, h = t + 1);          // vertical holes
    for (i = [0 : 6]) translate([8 + i * 11, h + 1, t / 2]) rotate([90, 0, 0])
      cylinder(d = 3 + (i - 3) * 0.1, h = 16);             // horizontal holes
  }
  for (i = [0 : 4]) translate([13 + i * 15, 26, t])        // external posts
    cylinder(d = 8 + (i - 2) * 0.1, h = 5);
}

// Both motor bolt circles, on SEPARATE TILES. v7 drew them concentrically and
// they overlapped into four merged slots, so an M3 and an M2.5 dropped through
// the same hole and the coupon proved neither circle. Separated, each tile
// tests exactly one interface.
module fit_coupon() {
  t = 3;
  s1 = out_bcd / 2 + m3_head_d / 2 + 4;             // each tile only as big as
  s2 = rear_bcd / 2 + m25_head_d / 2 + 4;           // its own circle needs
  difference() {                                    // OUTPUT face: D25, 4 x M3
    translate([-s1, -s1, 0]) cube([2 * s1, 2 * s1, t]);
    translate([0, 0, t / 2]) bolt_ring(out_bcd, m3_clear, out_bolt_n, t + 2, out_bolt_a0);
    translate([0, 0, -eps]) cylinder(d = shaft_bore_d + 0.4, h = t + 1);
  }
  translate([s1 + s2 + 8, 0, 0]) difference() {     // REAR square: 20x20, 4 x M2.5
    translate([-s2, -s2, 0]) cube([2 * s2, 2 * s2, t]);
    translate([0, 0, t / 2]) bolt_ring(rear_bcd, m25_clear, rear_bolt_n, t + 2, rear_bolt_a0);
    translate([0, 0, -eps]) cylinder(d = wire_hole_d, h = t + 1);
  }
}

// The clamp in miniature: same bore, same nip, same screws, 12 mm of it.
// BOTH HALVES SIT ON THE BED, and the cap half is laid crown-down so its bore
// prints as a valley exactly as the real cradle_cap does. v7 emitted this half
// floating 16 mm in the air AND printed its bore as a sagging 87 deg dome, so
// the gauge measured a shape the real part never has.
module bore_gauge() {
  gl = 12;
  difference() {                                            // saddle half
    translate([0, -gl / 2, 0]) cube([2 * blk_in, gl, base_z]);
    translate([blk_in, gl / 2 + 1, base_z]) rotate([90, 0, 0])
      cylinder(d = bore_d, h = gl + 2);
    translate([blk_in - bore_d / 2, -gl / 2 - 1, base_z]) cube([bore_d, gl + 2, base_z]);
  }
  translate([2 * blk_in + 8, 0, 0]) difference() {          // cap half, crown down
    translate([0, -gl / 2, 0]) cube([cap_w, gl, cap_z - clamp_nip]);
    translate([cap_w / 2, gl / 2 + 1, cap_z - clamp_nip]) rotate([90, 0, 0])
      cylinder(d = bore_d, h = gl + 2);
    translate([cap_w / 2 - bore_d / 2, -gl / 2 - 1, cap_z - clamp_nip])
      cube([bore_d, gl + 2, base_z]);
  }
}

// =============================================================================
// PRINT ORIENTATIONS — every one lands the part ON z = 0.
// checks.scad measures the exported STL to prove it, rather than trusting this.
// =============================================================================
module p_tol_coupon()  { tol_coupon(); }
module p_fit_coupon()  { fit_coupon(); }
module p_bore_gauge()  { bore_gauge(); }

// base plate: flipped, so the hard-stop post stands UP off the bed and the
// counterbored face is the last layer.
//   model z spans -post_h .. +t_plate; rotate([180,0,0]) makes that -t_plate ..
//   +post_h; so the lift is t_plate, NOT post_h. Getting this wrong left the
//   part floating 20.900 mm in the air, which the bed check in
//   tools/run_checks.py caught by measuring the exported STL.
module p_base_plate()  { translate([0, 0, t_plate]) rotate([180, 0, 0]) base_plate(); }

// yoke: the bridge's mating face DOWN on the bed, arm standing up as a vertical
// wall on a Ø(2*bridge_r) footprint.
//   model z spans (z_tilt - arm_pad_r) .. 0, so rotate([180,0,0]) alone already
//   puts the lowest point at 0. No lift at all.
module p_yoke()        { rotate([180, 0, 0]) yoke(); }

// cradle: as modelled — the bore already opens upward, so it is a valley. The
// offset is axis_z + base_z, NOT base_z: v7 dropped the axis_z term and put the
// part 1.740 mm below the bed, where a slicer clips away the keel's entire
// first-layer footprint.
module p_cradle()      { translate([0, 0, axis_z + base_z]) cradle(); }

// cap: crown down, so the bore is a valley and it prints on its flat top.
//   model z spans (-axis_z + clamp_nip) .. (-axis_z + cap_z); after the flip the
//   lowest point is -(cap_z - axis_z), so that is the lift.
module p_cradle_cap()  { translate([0, 0, cap_z - axis_z]) rotate([180, 0, 0]) cradle_cap(); }

// Model-vs-print export. Mass properties MUST be read in MODEL coordinates:
// a centre of mass taken off a print-orientation export is a transform away
// from the frame every other number in this project is written in, and reading
// one as the other is a defect that already shipped here once. tools/meshcheck.py
// refuses to print a CoM without a stated frame for the same reason.
orient = "print";   // [print, model]

module emit(p) {
  if (orient == "model") {
    if      (p == "base_plate") base_plate();
    else if (p == "yoke")       yoke();
    else if (p == "cradle")     cradle();
    else if (p == "cradle_cap") cradle_cap();
    else if (p == "tol_coupon") tol_coupon();
    else if (p == "fit_coupon") fit_coupon();
    else if (p == "bore_gauge") bore_gauge();
  } else {
    if      (p == "base_plate") p_base_plate();
    else if (p == "yoke")       p_yoke();
    else if (p == "cradle")     p_cradle();
    else if (p == "cradle_cap") p_cradle_cap();
    else if (p == "tol_coupon") p_tol_coupon();
    else if (p == "fit_coupon") p_fit_coupon();
    else if (p == "bore_gauge") p_bore_gauge();
  }
}

if      (part == "tol_coupon")  emit("tol_coupon");
else if (part == "fit_coupon")  emit("fit_coupon");
else if (part == "bore_gauge")  emit("bore_gauge");
else if (part == "base_plate")  emit("base_plate");
else if (part == "yoke")        emit("yoke");
else if (part == "cradle")      emit("cradle");
else if (part == "cradle_cap")  emit("cradle_cap");
else if (part == "__legacy__")  p_tol_coupon();
else if (part == "all") {
  translate([  0,   0, 0]) p_yoke();
  translate([110,   0, 0]) p_base_plate();
  translate([200,   0, 0]) p_cradle();
  translate([260,   0, 0]) p_cradle_cap();
  translate([  0, 120, 0]) p_tol_coupon();
  translate([110, 120, 0]) p_fit_coupon();
  translate([210, 120, 0]) p_bore_gauge();
}
