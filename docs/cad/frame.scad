// =============================================================================
// frame.scad · Engineered Lighting — robotic spotlight, PRINTED FRAME
// v5 (2026-07-30)
// =============================================================================
//
// Six printed parts, two coupons. Numbers live in frame_params.scad; this file
// is nothing but geometry, so there is one place to edit and one place to look.
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
//   fit_coupon       both motor bolt circles + both diameters, for 3 g of PETG.
//   bore_gauge       the real clamp in miniature: does the housing slide?
//
// WHAT CHANGED IN v5, and why
//  · The bridge was a 96 × 73 slab; 74% of the frame's plastic was in the yoke
//    and base plate. It is now a disc sized by the hard-stop groove plus two arm
//    pads, and the arms are keyholes with a pocket in each pad. The base plate
//    lost its oversized hub.
//  · Cable management is now ONE channel size (trough_w × trough_d) run in three
//    places that a bundle actually travels, instead of shallow grooves plus six
//    speculative zip-tie slot pairs. Two tie points remain, both where the cable
//    would otherwise swing.
//  · Deleted outright: four "tie-down" holes in the bridge, four zip slots on the
//    base-plate hub, the right arm's cable channel, and one of the cap's two wire
//    channels. None of them did anything.
//  · Every printed part still prints with ZERO supports, and every fastener is
//    still reachable in the order the parts go together.
//
// BUILD ORDER
//  1 fit_coupon + bore_gauge, against the real motor and the real housing.
//  2 Yoke onto the pan motor while the yoke is EMPTY: stand it on its arm tips,
//    motor into the bridge recess boss-down, six M3 up from underneath.
//  3 Base plate down onto the motor's rear: four M4 through the counterbores.
//  4 Cradle onto the tilt motor: turn the boss until one hole points straight up,
//    drive the three bolts above the split line.
//  5 Trunnion onto the cradle's right plate: three screws, heads outside.
//  6 Head up between the arms; four M4 through the LEFT ARM from the outside.
//  7 608 into the carrier, carrier over the stub, three screws LEFT LOOSE. Swing
//    the head through full travel, then tighten.
//  8 Wires: cradle -> tilt motor's bore -> arm trough -> bridge trough -> pan
//    motor's bore -> base-plate trough. Two ties.
//  9 Housing into the saddle, cap on, slide to balance, then nip the four screws.
// =============================================================================

include <frame_params.scad>

/* [What to render] */
part = "all"; // [fit_coupon, bore_gauge, base_plate, yoke, cradle, cradle_cap, trunnion, bearing_carrier, all]

$fn = 64;

echo(str("v5  span_in=", 2 * span_h, "  bridge_dia=", 2 * bridge_r, "  arm_h=", arm_h,
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
module arc_prism(r_in, r_out, angle, h) {       // ring segment, h tall, on +X
  rotate([0, 0, -angle / 2])
    rotate_extrude(angle = angle) translate([r_in, 0]) square([r_out - r_in, h]);
}
// one tie point = two slots a cable tie threads through. Cut along Z.
module tie_slots(spacing = 9) {
  for (s = [-1, 1]) translate([0, s * spacing / 2, 0])
    linear_extrude(80, center = true) offset(r = 1.2) square([5, 0.1], center = true);
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
    bolt_ring(rear_bcd, m4_clear, rear_bolt_n, 9, rear_bolt_a0);
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
    for (x = [-cap_bolt_x, cap_bolt_x]) translate([x, 0, plate_z - 14])
      cylinder(d = m3_pilot, h = 16);
  }
  translate([0, gl + 8, 0]) difference() {                          // cap half
    union() {
      translate([-blk_in, -gl / 2, 0]) cube([2 * blk_in, gl, cap_z]);
      for (x = [-cap_bolt_x, cap_bolt_x]) translate([x, 0, plate_z + clamp_nip])
        hull() {
          cylinder(d = 11, h = cap_z - plate_z - clamp_nip);
          translate([(blk_in - abs(x)) * sign(x), 0, 0])
            cylinder(d = 11, h = cap_z - plate_z - clamp_nip);
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
  hub_d = rear_bcd + m4_head_d + 6;                 // only as big as the bolts need
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
        translate([0, 0, -8])                        // gusset, grows OUTWARD only
          arc_prism(stop_r - stop_w / 2 + 0.7, stop_r + stop_w / 2 + 5,
                    2 * asin(post_w / 2 / stop_r), 8);
      }
    }
    bolt_ring(rear_bcd, m4_clear, rear_bolt_n, 3 * t_plate, rear_bolt_a0);
    translate([0, 0, t_plate + 0.8])
      bolt_ring(rear_bcd, m4_head_d, rear_bolt_n, 8, rear_bolt_a0);   // flush heads
    cylinder(d = wire_hole_d, h = 3 * t_plate, center = true);
    // ONE cable trough: out of the pan motor's bore and sideways off the hub.
    // Sideways, not aft: aft is where the hard-stop post and the C-clamp live,
    // and the shelf only overhangs the tongue, so the side is open air.
    translate([0, 0, t_plate]) trough(hub_d / 2 + 1, trough_w, 3.5);
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
    // --- bridge: cable route. A trough under the bridge from the centre out to
    //     the arm, then a notch through the bridge's rim so the bundle crosses to
    //     the arm's OUTER face, where the second trough takes it down to the
    //     motor. Both troughs are 3.5 mm deep, so the bridge keeps 5.5 mm of
    //     floor and the arm keeps 6.5 mm of web.
    translate([0, 0, -t_bridge + 3.5]) rotate([0, 0, 180]) trough(span_h, trough_w, 3.5);
    translate([-arm_out - 0.01, -trough_w / 2, -t_bridge - 0.01])
      cube([4, trough_w, t_bridge + 0.02]);

    // --- LEFT arm: the tilt motor bolts to its inner face ----------------
    translate([-arm_x, 0, z_tilt]) {
      bolt_ring_x(rear_bcd, m4_clear, rear_bolt_n, 4 * t_arm, rear_bolt_a0);
      rotate([0, 90, 0]) cylinder(d = wire_hole_d + 1, h = 4 * t_arm, center = true);
      translate([-t_arm / 2 - 0.01, 0, 0]) rotate([0, 90, 0])        // lightening pocket
        cylinder(d = arm_pocket_d, h = 4);
    }
    // --- RIGHT arm: stub passes through; carrier screws from outside -----
    translate([arm_x, 0, z_tilt]) {
      rotate([0, 90, 0]) cylinder(d = wire_hole_d + 1, h = 4 * t_arm, center = true);
      bolt_ring_x(carrier_bcd, m3_pilot, 3, 2.4 * t_arm, 90);
      translate([t_arm / 2 - 4 + 0.01, 0, 0]) rotate([0, 90, 0])
        cylinder(d = arm_pocket_d, h = 4);
    }
    // --- LEFT arm outer face: the cable trough + the second tie point ----
    translate([-arm_out + 3.5, 0, z_tilt]) rotate([0, -90, 0]) {
      trough(-z_tilt + 2, trough_w, 3.5);
      translate([-26, 0, 0]) tie_slots();                            // tie point 2 of 2
    }
  }
}

// =============================================================================
// 5 · cradle — the head's saddle. Housing axis = Y, tilt axis = X.
// The space above the split line is empty while you bolt the motor on: that is
// what makes the three output-flange bolts reachable.
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
    rotate([90, 0, 0]) translate([0, 0, -cr_len / 2]) linear_extrude(cr_len) cradle_profile();

    // the three reachable output-flange bolts
    for (i = [0 : out_bolt_n - 1]) if (out_bolt_up(i))
      rotate([out_bolt_a0 + i * 360 / out_bolt_n, 0, 0]) translate([0, 0, out_bcd / 2])
        rotate([0, 90, 0]) cylinder(d = m3_clear, h = 3 * cr_wall, center = true);
    translate([x_left - 0.01, 0, 0]) rotate([0, 90, 0])
      cylinder(d = boss_locate_d, h = boss_recess + 0.01);
    // wire: straight through on the axis into the motor's hollow shaft
    rotate([0, 90, 0]) translate([0, 0, x_left - 1]) cylinder(d = wire_hole_d - 2, h = cr_wall + 2);
    // trunnion: three screws, driven from OUTSIDE
    translate([blk_in + cr_wall / 2, 0, 0]) bolt_ring_x(trun_bcd, m3_pilot, 3, cr_wall + 5, 90);
    // the four cap screws
    for (x = [-cap_bolt_x, cap_bolt_x], y = [-cap_bolt_y, cap_bolt_y])
      translate([x, y, plate_z - 14]) cylinder(d = m3_pilot, h = 16);
    // balance trim: an M4 through the keel, on the vertical centreline
    translate([0, 0, -base_z + 3.4]) rotate([90, 0, 0])
      cylinder(d = m4_clear, h = cr_len + 2, center = true);
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
          translate([-blk_in, 0]) square([2 * blk_in, cap_z]);
          translate([0, -clamp_nip]) intersection() {                // upper half-bore
            circle(d = bore_d);
            translate([-bore_d, 0]) square([2 * bore_d, bore_d]);
          }
          translate([-(blk_in - trough_w / 2 - 1), trough_d / 2 + 0.4])   // ONE wire channel
            square([trough_w, trough_d], center = true);
          for (s = [-1, 1]) translate([s * blk_in, cap_z]) rotate(45)
            square([6, 6], center = true);
        }
      for (x = [-cap_bolt_x, cap_bolt_x], y = [-cap_bolt_y, cap_bolt_y])
        translate([x, y, plate_z + clamp_nip]) hull() {
          cylinder(d = 11, h = cap_z - plate_z - clamp_nip);
          translate([(blk_in - abs(x)) * sign(x), 0, 0])
            cylinder(d = 11, h = cap_z - plate_z - clamp_nip);
        }
    }
    for (x = [-cap_bolt_x, cap_bolt_x], y = [-cap_bolt_y, cap_bolt_y])
      translate([x, y, plate_z]) cylinder(d = m3_clear, h = cap_z);
    // lightening pocket in the cap's outer face. It prints as a first-layer
    // pocket (the cap goes on the bed outside-down) and it takes mass off the
    // ABOVE-axis side, so it makes the head lighter AND better balanced.
    translate([0, 0, cap_z - 3.5]) linear_extrude(4)
      offset(r = 3) offset(r = -3) square([2 * blk_in - 9, cr_len - 10], center = true);
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
      translate([0, 0, trun_t - 0.01]) cylinder(d1 = trun_flange_d - 6, d2 = 12, h = 4);
      translate([0, 0, trun_t]) cylinder(d = bearing_id - 0.15, h = stub_len);
      translate([0, 0, trun_t + stub_len - 1])
        cylinder(d1 = bearing_id - 0.15, d2 = bearing_id - 1.8, h = 1);
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
      cylinder(d = bearing_od + 0.05, h = bearing_w + 0.4);
    rotate([0, 90, 0]) cylinder(d = bearing_od - 4, h = 3 * carrier_t, center = true);
    rotate([0, 90, 0]) cylinder(d1 = bearing_od - 1, d2 = bearing_od - 4, h = 1.5);
    translate([carrier_t / 2, 0, 0]) bolt_ring_x(carrier_bcd, m3_clear + 0.8, 3, 3 * carrier_t, 90);
  }
}

// =============================================================================
// print orientations — `part="x"` emits a slice-ready part
// =============================================================================
module p_fit_coupon()      { fit_coupon(); }
module p_bore_gauge()      { translate([0, 0, base_z]) bore_gauge(); }
module p_base_plate()      { translate([0, 0, t_plate]) rotate([180, 0, 0]) base_plate(); }
module p_yoke()            { rotate([180, 0, 0]) yoke(); }
module p_cradle()          { translate([0, 0, base_z]) cradle(); }
module p_cradle_cap()      { translate([0, 0, cap_z]) rotate([180, 0, 0]) cradle_cap(); }
module p_trunnion()        { rotate([0, -90, 0]) trunnion(); }
module p_bearing_carrier() { rotate([0, -90, 0]) bearing_carrier(); }

if (part == "fit_coupon")           p_fit_coupon();
else if (part == "bore_gauge")      p_bore_gauge();
else if (part == "base_plate")      p_base_plate();
else if (part == "yoke")            p_yoke();
else if (part == "cradle")          p_cradle();
else if (part == "cradle_cap")      p_cradle_cap();
else if (part == "trunnion")        p_trunnion();
else if (part == "bearing_carrier") p_bearing_carrier();
else if (part == "all") {
  translate([  0, -70, 0]) rotate([0, 0, 90]) p_base_plate();
  translate([  0,  16, 0])                    p_yoke();
  translate([-84,  20, 0])                    p_cradle();
  translate([-84,  74, 0])                    p_cradle_cap();
  translate([-26,  84, 0])                    p_bore_gauge();
  translate([ 78,  76, 0])                    p_fit_coupon();
  translate([ 74,  14, 0])                    p_bearing_carrier();
  translate([116,  50, 0])                    p_trunnion();
}
