// =============================================================================
// frame.scad · Engineered Lighting — robotic spotlight, PRINTED FRAME
// v7 (2026-07-30)
// =============================================================================
//
// Six printed parts, three test pieces. Numbers live in frame_params.scad; this
// file is nothing but geometry: one place to edit, one place to look.
//
//   base_plate       hub + aft tongue. Pan motor bolts up into it; the tongue
//                    carries the C-clamp and the pan hard-stop post.
//   yoke             ONE piece. The bridge is a DISC (only as big as the hard
//                    stop needs) with two arm pads; the arms are keyholes.
//   cradle           the head's saddle: bolts to the tilt boss, holds the
//                    housing's lower half, carries the trunnion.
//   cradle_cap       upper half of the clamp.
//   trunnion         the printed axle stub. No steel axle anywhere.
//   bearing_carrier  the 608's home, with oversize screws so it FINDS the axis.
//   tol_coupon       PRINT THIS FIRST. Measures your printer's hole shrink and
//                    shaft growth, which every fit in the project is derived from.
//   fit_coupon       both motor bolt circles + both diameters, for 3 g of PETG.
//   bore_gauge       the real clamp in miniature: does the housing slide?
//
// WHAT CHANGED IN v7, and why
//  · THE MOTOR. Everything below used to be built on an invented output flange:
//    six holes on a 30 mm circle, and an M4 rear mount on 43. The RMD-L manual
//    Rev 1.01 says four M3 on 25, and a rear of four M2.5 on a 20 x 20 square.
//    Every bolt circle here was wrong and every part was oversized to suit. The
//    machine lost 18 g by being drawn against the real motor instead.
//  · The manual publishes no output boss at all, so out_boss_h now defaults to
//    ZERO — a flat front face — and every dimension that depended on a boss
//    derives itself from that number rather than assuming one exists.
//  · Only two output holes clear the split line now, not three. Two M3 at
//    r = 12.5 hold the head with about 20x margin on the motor's peak torque,
//    but it is a real reduction and it is stated here rather than buried.
//  · The trunnion is a STEPPED shaft. Only the 9 mm inside the 608 has to be
//    7.7 mm; v6 ran that diameter the whole 24 mm, most of it spanning air and
//    plate as a bare cantilever. Ø14 there is 11x stiffer for 1.9 g.
//  · cap_bolt_x is DERIVED from the plane the motor mates on. The cap's ear
//    landing inside the motor was caught by boolean intersection twice; a
//    derived position means it cannot come back whatever the boss turns out
//    to be.
//  · The cradle's local bolt pad is gone — with the highest reachable bolt at
//    8.84 mm instead of 15, plate_z covers it outright.
//
// WHAT CHANGED IN v6
//  · TOLERANCES. Nothing before v6 compensated for the fact that FDM gets holes
//    and shafts wrong in OPPOSITE directions. The trunnion's stub was modelled
//    at 7.85 mm to enter an 8.00 mm bearing and would have printed at ~8.0 — the
//    machine could not have been assembled. Every fit is now derived from three
//    measured numbers via the fit functions in frame_params.scad, and tol_coupon
//    exists to measure them on YOUR printer.
//  · Holes drilled sideways get their own fit class, because a horizontal hole
//    prints with a sagging roof and comes out worse than a vertical one.
//  · BALANCE BY CONSTRUCTION: the tilt axis sits axis_z above the housing's
//    axis, which puts the measured centre of mass of the whole head ON it.
//  · The hard-stop post carries a tapered buttress down 80% of its length.
//  · The cable route is ONE open channel end to end.
//  · The clamp actually fits: the cap's body is a derived slip fit in the slot
//    it drops into, instead of being drawn exactly as wide as it.
//
// BUILD ORDER
//  0 tol_coupon. Set hole_comp / hole_comp_h / shaft_comp from what it tells
//    you. Everything below assumes those three numbers are yours, not mine.
//  1 fit_coupon + bore_gauge, against the real motor and the real housing.
//  2 Yoke onto the pan motor while the yoke is EMPTY: stand it on its arm tips,
//    motor into the bridge recess boss-down, four M3 up from underneath. Turn the
//    motor so its side connector faces the base plate's cable trough — one of the
//    other three positions puts it straight into the hard-stop post.
//  3 Base plate down onto the motor's rear: four M2.5 through the counterbores.
//  4 Cradle onto the tilt motor: turn the boss until two holes sit above centre,
//    drive the bolts above the split line (two of them, at out_bolt_a0 = 45).
//  5 Trunnion onto the cradle's right plate: three screws, heads outside.
//  6 Head up between the arms; four M2.5 through the LEFT ARM from the outside.
//  7 608 into the carrier, carrier over the stub, three screws LEFT LOOSE. Swing
//    the head through full travel, then tighten.
//  8 Wires: cradle -> tilt motor's bore -> arm trough -> bridge trough -> pan
//    motor's bore -> base-plate trough. Two ties.
//  9 Housing into the saddle, cap on, slide to balance, then nip the four screws.
// =============================================================================

include <frame_params.scad>

/* [What to render] */
part = "all"; // [tol_coupon, fit_coupon, bore_gauge, base_plate, yoke, cradle, cradle_cap, trunnion, bearing_carrier, all]

$fn = 64;

echo(str(cad_version, " frame  span_in=", 2 * span_h, "  bridge_dia=", 2 * bridge_r, "  arm_h=", arm_h,
         "  head_sweep=", head_sweep, " vs drop=", drop, "  slide=", slide_range, "mm"));

// ---------------------------------------------------------------- helpers ----
module bolt_ring(bcd, d, n, h, a0 = 0) {        // ring in XY, drilled along Z
  for (i = [0 : n - 1]) rotate([0, 0, a0 + i * 360 / n])
    translate([bcd / 2, 0, 0]) cylinder(d = d, h = h, center = true);
}
module bolt_ring_x(bcd, d, n, len, a0 = 0) {    // ring in YZ, drilled along X
  for (i = [0 : n - 1]) rotate([a0 + i * 360 / n, 0, 0])
    translate([0, 0, bcd / 2]) rotate([0, 90, 0]) cylinder(d = d, h = len, center = true);
}
// buttress: ring segment whose OUTER radius tapers from r_root at the top face
// down to r_tip at -h. Prints as an overhanging-free slope in the part's own
// print orientation (post up), so no supports.
module arc_taper(r_in, r_tip, r_root, angle, h) {
  rotate([0, 0, -angle / 2]) rotate_extrude(angle = angle)
    polygon([[r_in, -h], [r_tip, -h], [r_root, 0], [r_in, 0]]);
}
module arc_prism(r_in, r_out, angle, h) {       // ring segment, h tall, on +X
  rotate([0, 0, -angle / 2])
    rotate_extrude(angle = angle) translate([r_in, 0]) square([r_out - r_in, h]);
}
// one tie point = two slots a cable tie threads through. Cut along Z.
// Sized for the tie and nothing more: on the arm these have to live in the 7.5 mm
// between the bridge's underside and the top of the tilt motor's body.
module tie_slots(spacing = 9, w = 3.4, t = 1.6) {
  for (s = [-1, 1]) translate([0, s * spacing / 2, 0])
    linear_extrude(80, center = true) offset(r = t / 2) square([w - t, 0.1], center = true);
}
module trough(len, w = trough_w, d = trough_d) { // channel along +X, cut into +Z
  translate([0, -w / 2, -d]) cube([len, w, d + 0.01]);
}

// =============================================================================
// 1 · fit_coupon — the cheapest part in the project and the most important
// =============================================================================
module fit_coupon() {
  d = motor_d + 8;
  difference() {
    union() {
      cylinder(d = d, h = 3);
      translate([0, -d / 2 - 4, 0]) linear_extrude(3)
        offset(r = 3) square([16, 4], center = true);
    }
    bolt_ring(out_bcd,  m3_clear, out_bolt_n,  9, out_bolt_a0);
    bolt_ring(rear_bcd, m25_clear, rear_bolt_n, 9, rear_bolt_a0);
    cylinder(d = shaft_bore_d, h = 9, center = true);
    for (dia = [out_boss_d, motor_d]) translate([0, 0, 2.4]) difference() {
      cylinder(d = dia + 0.5, h = 2);
      translate([0, 0, -1]) cylinder(d = dia - 0.5, h = 4);
    }
    translate([0, out_bcd / 2 - 8, 2.2]) linear_extrude(1.2)
      text("OUT", size = 4.5, halign = "center", valign = "center");
    translate([0, -rear_bcd / 2 + 5, 2.2]) linear_extrude(1.2)
      text("REAR", size = 4.5, halign = "center", valign = "center");
  }
}

// =============================================================================
// 2 · bore_gauge — a 14 mm slice of the real clamp, both halves, one print
// =============================================================================
module bore_gauge() {
  gl = 14;
  difference() {                                                    // saddle half
    translate([x_left, -gl / 2, -base_z]) cube([x_right - x_left, gl, base_z + plate_z]);
    translate([0, -gl / 2 - 1, 0]) rotate([-90, 0, 0]) cylinder(d = bore_d, h = gl + 2);
    translate([-blk_in, -gl / 2 - 1, 0.02]) cube([2 * blk_in, gl + 2, plate_z + 1]);
    for (x = [-cap_bolt_x, cap_bolt_x]) translate([x, 0, plate_z - pilot_len])
      cylinder(d = m3_pilot, h = pilot_len + 2);
  }
  translate([0, gl + 8, 0]) difference() {                          // cap half
    union() {
      translate([-cap_w / 2, -gl / 2, 0]) cube([cap_w, gl, cap_z]);
      for (x = [-cap_bolt_x, cap_bolt_x]) translate([x, 0, plate_z + clamp_nip])
        hull() {
          cylinder(d = cap_ear_d, h = cap_z - plate_z - clamp_nip);
          translate([(cap_w / 2 - abs(x)) * sign(x), 0, 0])
            cylinder(d = cap_ear_d, h = cap_z - plate_z - clamp_nip);
        }
    }
    translate([0, -gl / 2 - 1, -clamp_nip]) rotate([-90, 0, 0]) cylinder(d = bore_d, h = gl + 2);
    translate([-bore_d, -gl / 2 - 1, -bore_d - clamp_nip]) cube([2 * bore_d, gl + 2, bore_d]);
    for (x = [-cap_bolt_x, cap_bolt_x]) translate([x, 0, plate_z]) cylinder(d = m3_clear, h = cap_z);
  }
}

// =============================================================================
// 3 · base_plate — hub for the motor, tongue for the clamp and the hard stop.
// prints POST UP; installs POST DOWN. origin = the face the motor's rear meets.
// =============================================================================
module base_plate() {
  // the bolt circle is only Ø28, but the plate is what the motor's Ø49 rear face
  // lands on, so it wants to cover most of that or the motor rocks on four screws
  hub_d = max(rear_bcd + m25_head_d + 6, motor_d - 5);
  tongue_w = 2 * (post_w / 2 + 6);
  difference() {
    union() {
      linear_extrude(t_plate) offset(r = 5) offset(r = -5) union() {
        circle(d = hub_d);
        translate([-tongue_w / 2, -78]) square([tongue_w, 78]);
      }
      rotate([0, 0, 270]) {                          // hard-stop post, aft
        translate([0, 0, -post_h])
          arc_prism(stop_r - stop_w / 2 + 0.7, stop_r + stop_w / 2 - 0.7,
                    2 * asin(post_w / 2 / stop_r), post_h);
        // The post is a 30 mm blade printed standing up, and a hard stop is the
        // one feature on this machine that gets HIT. So it gets a buttress that
        // runs almost its whole length, tapering OUTWARD-only (inward is the
        // motor) and stopping short of the bridge's top face. Turns a slab
        // loaded across its layers into a T-section loaded along them.
        arc_taper(stop_r - stop_w / 2 + 0.7, stop_r + stop_w / 2 - 0.7,
                  stop_r + stop_w / 2 + 5, 2 * asin(post_w / 2 / stop_r), butt_h);
      }
    }
    bolt_ring(rear_bcd, m25_clear, rear_bolt_n, 3 * t_plate, rear_bolt_a0);
    // 3 deep, so a 2.5 mm cap head sinks fully below the face. This counterbore
    // prints as a FIRST-LAYER pocket (the plate goes on the bed face-down), which
    // is why it can be a free_h fit and not a bridged-hole fit.
    translate([0, 0, t_plate - 0.5])
      bolt_ring(rear_bcd, free_h(m25_head_d), rear_bolt_n, 6, rear_bolt_a0);
    cylinder(d = wire_hole_d, h = 3 * t_plate, center = true);
    // ONE cable trough: out of the pan motor's bore and sideways off the hub.
    // Sideways, not aft: aft is where the hard-stop post and the C-clamp live,
    // and the shelf only overhangs the tongue, so the side is open air.
    translate([0, 0, t_plate]) trough(hub_d / 2 + 1);   // one channel size, again
    translate([hub_d / 2 - 7, 0, 0]) tie_slots();                    // tie point 1 of 2
  }
}

// =============================================================================
// 4 · yoke — bridge disc + two keyhole arms, one piece.
// prints ARMS UP, bridge on the bed. origin = centre of the bridge's TOP face.
// =============================================================================
module arm_blank() {          // keyhole: round pad at the tilt axis, neck to the bridge
  hull() {
    translate([0, 0, -t_bridge + 0.01]) linear_extrude(0.01)
      square([t_arm, arm_neck], center = true);
    translate([0, 0, z_tilt]) rotate([0, 90, 0]) cylinder(d = arm_pad_d, h = t_arm, center = true);
  }
}

module yoke() {
  difference() {
    union() {
      // bridge = a disc only as big as the hard stop needs, waisted out to a pad
      // under each arm. The waist is the load path; everything else is air.
      translate([0, 0, -t_bridge]) linear_extrude(t_bridge)
        for (s = [-1, 1]) hull() {
          circle(r = bridge_r);
          translate([s * arm_x, 0]) offset(r = 4) offset(r = -4)
            square([t_arm, arm_neck + 6], center = true);
        }
      for (s = [-1, 1]) translate([s * arm_x, 0, 0]) arm_blank();
    }

    // --- bridge: pan output interface ------------------------------------
    translate([0, 0, -boss_recess]) cylinder(d = boss_locate_d, h = boss_recess + 1);
    bolt_ring(out_bcd, m3_clear, out_bolt_n, 3 * t_bridge, out_bolt_a0);
    cylinder(d = wire_hole_d, h = 3 * t_bridge, center = true);
    // --- bridge: hard-stop groove, island at +Y so home is mid-travel ----
    rotate([0, 0, 90 + (360 - stop_arc) / 2]) rotate_extrude(angle = stop_arc)
      translate([stop_r - stop_w / 2, -stop_deep]) square([stop_w, stop_deep + 0.01]);
    // --- bridge: cable route. ONE channel, open to the outside for its whole
    //     length: it runs under the bridge from the hub to the arm's OUTER face,
    //     turns the corner, and goes down the arm to the tilt axis. You lay the
    //     bundle in from outside after everything is bolted together — there is
    //     no tunnel to thread and no notch to line up. It is 3 mm deep against
    //     the hard-stop groove's 3, so the bridge keeps a 2 mm web where they
    //     cross, and the head's sweep still clears the bundle by 6.4 mm.
    translate([0, 0, -t_bridge + trough_d]) rotate([0, 0, 180]) trough(arm_out);

    // --- LEFT arm: the tilt motor bolts to its inner face ----------------
    translate([-arm_x, 0, z_tilt]) {
      bolt_ring_x(rear_bcd, m25_clear_x, rear_bolt_n, 4 * t_arm, rear_bolt_a0);
      rotate([0, 90, 0]) cylinder(d = wire_hole_d + 1, h = 4 * t_arm, center = true);
      // lightening pocket, OUTER face only — the motor mates the inner one. Hex
      // with a vertex up so the pocket roof is a 60 deg peak, not a 32 mm bridge.
      translate([-t_arm / 2 - 0.01, 0, 0]) rotate([0, 90, 0])
        cylinder(d = arm_pocket_d, h = arm_pocket_z, $fn = 6);
    }
    // --- RIGHT arm: stub passes through; carrier screws from outside -----
    translate([arm_x, 0, z_tilt]) {
      // clearance for the trunnion's SHANK — no wire has ever come through here
      rotate([0, 90, 0]) cylinder(d = free_hx(shank_d) + 1.5, h = 4 * t_arm, center = true);
      bolt_ring_x(carrier_bcd, m3_pilot_x, 3, 2.4 * t_arm, 90);
      // pocket the INNER face here: the carrier has to land on a flat outer one.
      // The hex's flats fall inside the pilot circle, so all three screws still
      // thread the full 10 mm.
      translate([-t_arm / 2 - 0.01, 0, 0]) rotate([0, 90, 0])
        cylinder(d = arm_pocket_d, h = arm_pocket_z, $fn = 6);
    }
    // --- LEFT arm outer face: the trough turns the corner and runs down to the
    //     tilt axis, where it meets the hole through to the motor's hollow bore.
    //     One tie, placed just below the bridge because that is the only station
    //     where the arm's inner face is clear of the motor body.
    translate([-arm_out - 0.01, 0, z_tilt]) rotate([0, -90, 0]) {
      trough(-z_tilt);
      translate([28, 0, 0]) tie_slots();                             // tie point 2 of 2
    }
  }
}

// =============================================================================
// 5 · cradle — the head's saddle. Housing axis = Y, tilt axis = X.
// The space above the split line is empty while you bolt the motor on: that is
// what makes the reachable output-flange bolts reachable.
// =============================================================================
module cradle_profile() {
  difference() {
    union() {
      translate([x_left, -base_z]) square([x_right - x_left, base_z]);
      translate([x_left, 0]) square([cr_wall, plate_z]);
      translate([blk_in, 0]) square([cr_wall, plate_z]);
    }
    translate([0, 0.02]) intersection() {                     // lower half-bore
      circle(d = bore_d);
      translate([-bore_d, -bore_d]) square([2 * bore_d, bore_d]);
    }
    for (sx = [-1, 1]) translate([sx * x_right, -base_z]) rotate(45)   // dead corners
      square([keel_chamf * 1.414, keel_chamf * 1.414], center = true);
  }
}

module cradle() {
  difference() {
    // origin = the TILT AXIS. The bore sits axis_z below it, which is the whole
    // balancing trick: no ballast, no trim washers, just an axis_z offset.
    // v6 needed a local pad here because the flange's top bolt sat 19.7 mm above
    // the axis. On the real bolt circle the highest reachable one is at 8.84, so
    // plate_z covers it outright and the pad is gone — a whole feature deleted by
    // getting the motor's dimensions right instead of guessing them.
    translate([0, 0, -axis_z])
      rotate([90, 0, 0]) translate([0, 0, -cr_len / 2]) linear_extrude(cr_len) cradle_profile();

    // the reachable output-flange bolts: the ones above the split line
    for (i = [0 : out_bolt_n - 1]) if (out_bolt_up(i))
      rotate([out_bolt_a0 + i * 360 / out_bolt_n, 0, 0]) translate([0, 0, out_bcd / 2])
        rotate([0, 90, 0]) cylinder(d = m3_clear_x, h = 3 * cr_wall, center = true);
    translate([x_left - 0.01, 0, 0]) rotate([0, 90, 0])
      cylinder(d = boss_locate_d, h = boss_recess + 0.01);
    // wire: straight through on the axis into the motor's hollow shaft
    rotate([0, 90, 0]) translate([0, 0, x_left - 1]) cylinder(d = wire_hole_d - 2, h = cr_wall + 2);
    // trunnion: three screws, driven from OUTSIDE
    translate([blk_in + cr_wall / 2, 0, 0]) bolt_ring_x(trun_bcd, m3_pilot_x, 3, cr_wall + 5, 90);
    // the four cap screws
    for (x = [-cap_bolt_x, cap_bolt_x], y = [-cap_bolt_y, cap_bolt_y])
      translate([x, y, plate_z - axis_z - pilot_len]) cylinder(d = m3_pilot, h = pilot_len + 2);
    // The wires leave the housing's NPT stub at the REAR of the bore and have to
    // reach the tilt axis to get into the motor's hollow shaft. The 2.3 mm the
    // bore's shoulder leaves is not a cable route, so cut one: a channel along
    // the left plate's inner face from the rear opening to the axis hole.
    translate([x_left + cr_wall - trough_d, -cr_len / 2 - 1, -trough_w / 2])
      cube([trough_d + 0.01, cr_len / 2 + 1, trough_w]);
  }
}

// -----------------------------------------------------------------------------
// 5b · cradle_cap — prints INVERTED, so its half-bore is a valley
// -----------------------------------------------------------------------------
module cradle_cap() {
  difference() {
    union() {
      rotate([90, 0, 0]) translate([0, 0, -cr_len / 2]) linear_extrude(cr_len)
        difference() {
          translate([-cap_w / 2, 0]) square([cap_w, cap_z]);
          translate([0, -clamp_nip]) intersection() {                // upper half-bore
            circle(d = bore_d);
            translate([-bore_d, 0]) square([2 * bore_d, bore_d]);
          }
          for (s = [-1, 1]) translate([s * cap_w / 2, cap_z]) rotate(45)
            square([6, 6], center = true);
        }
      // ears: full height from the landing face to the cap's crown, so the M3
      // pulls on 5.6 mm of plastic instead of a 2.6 mm flange
      for (x = [-cap_bolt_x, cap_bolt_x], y = [-cap_bolt_y, cap_bolt_y])
        translate([x, y, plate_z + clamp_nip]) hull() {
          cylinder(d = cap_ear_d, h = cap_z - plate_z - clamp_nip);
          translate([(cap_w / 2 - abs(x)) * sign(x), 0, 0])
            cylinder(d = cap_ear_d, h = cap_z - plate_z - clamp_nip);
        }
    }
    for (x = [-cap_bolt_x, cap_bolt_x], y = [-cap_bolt_y, cap_bolt_y])
      translate([x, y, plate_z]) cylinder(d = m3_clear, h = cap_z);
    // lightening pocket in the cap's outer face. It prints as a first-layer
    // pocket (the cap goes on the bed outside-down) and it takes mass off the
    // ABOVE-axis side, so it makes the head lighter AND better balanced.
    translate([0, 0, cap_z - cap_pocket]) linear_extrude(cap_pocket + 1)
      offset(r = 3) offset(r = -3) square([cap_w - 6, cr_len - 7], center = true);
  }
}

// =============================================================================
// 6 · trunnion — the printed axle. Prints STUB UP.
// origin = the cradle face it bolts to; stub runs +X
// =============================================================================
module trunnion() {
  difference() {
    rotate([0, 90, 0]) union() {
      cylinder(d = trun_flange_d, h = trun_t);
      // STEPPED. Only the last stretch has to be 7.7 mm, because only the last
      // stretch is inside the bearing. Everything before it — the gap, the arm,
      // most of the carrier — was a 7.7 mm plastic cantilever in v6 for no
      // reason. Ø14 through that span is 11x the bending stiffness for 1.9 g,
      // and the step faces UP in print orientation, so it needs no support.
      translate([0, 0, trun_t - 0.01]) cylinder(d = shank_d, h = shank_len + 0.01);
      translate([0, 0, trun_t + shank_len]) cylinder(d = stub_d, h = journal_len - 1);
      translate([0, 0, trun_t + stub_len - 1])                        // lead-in
        cylinder(d1 = stub_d, d2 = stub_d - 1.6, h = 1);
    }
    translate([trun_t / 2, 0, 0]) bolt_ring_x(trun_bcd, m3_clear, 3, 3 * trun_t, 90);
  }
}

// =============================================================================
// 7 · bearing_carrier — the 608 pocket is a first-layer-accurate hole, and the
// screw holes are oversize on purpose: this part FINDS the axis.
// origin = the arm's outer face; body runs +X
// =============================================================================
module bearing_carrier() {
  difference() {
    rotate([0, 90, 0]) cylinder(d = carrier_d, h = carrier_t);
    translate([carrier_t - bearing_w - 0.3, 0, 0]) rotate([0, 90, 0])
      cylinder(d = bearing_pocket_d, h = bearing_w + 0.4);
    rotate([0, 90, 0]) cylinder(d = bearing_od - 4, h = 3 * carrier_t, center = true);
    rotate([0, 90, 0]) cylinder(d1 = bearing_od - 1, d2 = bearing_od - 4, h = 1.5);
    translate([carrier_t / 2, 0, 0]) bolt_ring_x(carrier_bcd, m3_clear + 0.8, 3, 3 * carrier_t, 90);
  }
}

// =============================================================================
// 0 · tol_coupon — the part that MEASURES your printer, so every fit above is
// derived from a number you own instead of a number I guessed.
//
// Two tiles, one plate, no supports, 45 g of PETG, and you print it once. Every
// label is the candidate value in HUNDREDTHS of a millimetre.
//
//   HOLES tile  · top row  : M3 must DROP THROUGH under its own weight.
//                            The lowest label that does -> hole_comp
//                 mid row  : M3 must CUT ITS OWN THREAD without splitting the
//                            boss. The label that does -> confirms hole_comp
//                 the wall : same test, drilled sideways (these bridge, so they
//                            always come out worse) -> hole_comp_h
//   SHAFT tile  · posts    : the 608 must slide on and TURN freely, no rock.
//                            The largest label that does -> shaft_comp
//                 rings    : the 608 must PRESS in with thumb pressure and stay.
//                            The label that does -> confirms hole_comp
// =============================================================================
module tol_coupon() {
  ct = 4;                                       // tile thickness
  cand   = [0.15, 0.25, 0.35, 0.45];            // hole_comp   candidates
  cand_h = [0.25, 0.40, 0.55, 0.70];            // hole_comp_h candidates
  cand_s = [0.10, 0.15, 0.20, 0.30];            // shaft_comp  candidates
  wx = 40; wt = 6; wz = 24;                     // the sideways-hole wall

  module lbl(v, sz = 3.6) linear_extrude(1.1)
    text(str(round(v * 100)), size = sz, halign = "center", valign = "center");

  // ---- tile 1: holes ----------------------------------------------------
  difference() {
    union() {
      translate([-54, -20, 0]) cube([94 + wt, 40, ct]);
      translate([wx, -18, 0]) cube([wt, 36, wz]);       // wall stands on the tile
    }
    for (i = [0 : 3]) translate([-46 + i * 12, 0, 0]) {
      translate([0,  10, -1]) cylinder(d = 3 + 0.5 + cand[i], h = ct + 2);
      translate([0, -10, -1]) cylinder(d = 3 - 0.45 + cand[i], h = ct + 2);
      translate([0,  16.5, ct - 1]) lbl(cand[i], 3.4);       // beside, not on top
      translate([0, -16.5, ct - 1]) lbl(cand[i], 3.4);
    }
    translate([2, 12, ct - 1]) linear_extrude(1.1) text("M3 FREE", size = 4.2);
    translate([2, 6, ct - 1]) linear_extrude(1.1) text("3.65-3.95", size = 3);
    translate([2, -10, ct - 1]) linear_extrude(1.1) text("M3 TAP", size = 4.2);
    translate([2, -16, ct - 1]) linear_extrude(1.1) text("2.70-3.00", size = 3);
    // sideways holes: two heights x two positions, drilled along +X
    for (i = [0 : 3]) {
      py = (i % 2 == 0) ? -9 : 9;
      pz = (i < 2) ? 10 : 19;
      translate([wx - 1, py, pz]) rotate([0, 90, 0])
        cylinder(d = 3 + 0.5 + cand_h[i], h = wt + 2);
      // extrude OUTWARD from 1.1 deep so the digits don't come out mirrored
      translate([wx + wt - 1.1, py, pz - 5]) rotate([90, 0, 90]) lbl(cand_h[i], 3.6);
    }
  }

  // ---- tile 2: shafts ---------------------------------------------------
  // posts on 16 mm centres so a Ø22 bearing can drop over one without fouling
  // its neighbour. The press-fit tests are RINGS, not pockets: a 6 mm ring costs
  // 0.8 cm3 and tests the same bore as a pocket sunk in a plate thick enough to
  // hold one, which is why this whole coupon is 4 mm thick instead of 5.
  translate([0, 56, 0]) difference() {
    union() {
      translate([-54, -22, 0]) cube([120, 44, ct]);
      for (i = [0 : 3]) translate([-46 + i * 16, -2, 0])
        cylinder(d = 8 - 0.15 - cand_s[i], h = 11);     // 608 slides ON these
      for (i = [0 : 1]) translate([26 + i * 28, 0, 0])
        cylinder(d = bearing_od + 4, h = 6);            // 608 PRESSES into these
    }
    for (i = [0 : 3]) translate([-46 + i * 16, -2, 0]) {
      cylinder(d = 3.6, h = 40, center = true);         // hollow: prints faster
      translate([0, 11, ct - 1]) lbl(cand_s[i], 3.4);
    }
    for (i = [0 : 1]) translate([26 + i * 28, 0, 0]) {
      cylinder(d = bearing_od + 0.10 + cand[i * 2 + 1], h = 20, center = true);
      translate([0, 15.5, ct - 1]) lbl(cand[i * 2 + 1], 3.4);
    }
    translate([-52, 15, ct - 1]) linear_extrude(1.1) text("608 FIT", size = 4.2);
    translate([-52, -19, ct - 1]) linear_extrude(1.1) text("posts 7.7-7.9   rings 22.3 / 22.5", size = 3.2);
  }
}

// =============================================================================
// print orientations — `part="x"` emits a slice-ready part
// =============================================================================
module p_tol_coupon()      { tol_coupon(); }
module p_fit_coupon()      { fit_coupon(); }
module p_bore_gauge()      { translate([0, 0, base_z]) bore_gauge(); }
module p_base_plate()      { translate([0, 0, t_plate]) rotate([180, 0, 0]) base_plate(); }
module p_yoke()            { rotate([180, 0, 0]) yoke(); }
module p_cradle()          { translate([0, 0, base_z]) cradle(); }
module p_cradle_cap()      { translate([0, 0, cap_z]) rotate([180, 0, 0]) cradle_cap(); }
module p_trunnion()        { rotate([0, -90, 0]) trunnion(); }
module p_bearing_carrier() { rotate([0, -90, 0]) bearing_carrier(); }

if (part == "tol_coupon")           p_tol_coupon();
else if (part == "fit_coupon")      p_fit_coupon();
else if (part == "bore_gauge")      p_bore_gauge();
else if (part == "base_plate")      p_base_plate();
else if (part == "yoke")            p_yoke();
else if (part == "cradle")          p_cradle();
else if (part == "cradle_cap")      p_cradle_cap();
else if (part == "trunnion")        p_trunnion();
else if (part == "bearing_carrier") p_bearing_carrier();
// every part, laid out flat. This is a picture of the set, not a bed: it is
// 203 x 233 mm, so a 256 mm bed takes it in two jobs.
else if (part == "all") {
  translate([  49.8,   37.7, 0]) p_yoke();
  translate([ 137.2,   37.5, 0]) p_fit_coupon();
  translate([ 187.7,   13.0, 0]) p_trunnion();
  translate([  54.0,  104.4, 0]) p_tol_coupon();
  translate([ 152.0,  106.4, 0]) p_base_plate();
  translate([  22.9,  200.4, 0]) p_bore_gauge();
  translate([  77.6,  209.4, 0]) p_cradle();
  translate([ 131.8,  209.4, 0]) p_cradle_cap();
  translate([ 183.1,  213.4, 0]) p_bearing_carrier();
}
