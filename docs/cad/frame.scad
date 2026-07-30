// =============================================================================
// frame.scad  ·  Engineered Lighting — robotic spotlight, PRINTED FRAME
// v4 (2026-07-30) — redesigned from the ground up.
// =============================================================================
//
// SIX printed parts and two five-minute test coupons. That's the whole frame.
//
//   base_plate       clamps to the shelf; the PAN motor bolts under it
//   yoke             ONE piece: bridge + both arms (no joinery, nothing to align)
//   cradle           the head's saddle: bolts to the TILT output, holds the housing
//   cradle_cap       the other half of the clamp — pinches the housing
//   trunnion         the printed axle stub (there is no steel axle in this design)
//   bearing_carrier  holds the 608 and lets the tilt axis self-align
//   fit_coupon       proves BOTH motor bolt circles before any real filament
//   bore_gauge       proves the housing slide-and-clamp fit
//
// -----------------------------------------------------------------------------
// THE SEVEN RULES THIS DESIGN FOLLOWS
// -----------------------------------------------------------------------------
// 1  Every part prints flat-out with ZERO supports and no long bridges. The
//    orientation is baked in: `part="yoke"` emits the part already oriented.
// 2  Nothing is friction-fit or tabbed together. Every printed-to-printed joint
//    is a bolt you can see, and every printed-to-MOTOR joint is a bolt going
//    into the motor's own threaded holes.
// 3  The motors are bolted by their REAR covers. Both RMD faces carry mounting
//    holes; the rear ones are used here because the rear is a flat plate, so the
//    mating surface is unambiguous. (No collar could ever slide over an RMD body
//    anyway — the 4-pin connector is in the way.)
// 4  Every surface that has to be ROUND and accurate prints as a vertical hole
//    or a first-layer pocket. Nothing that locates anything prints as a bridge.
// 5  Where a printed part bolts to a rotating output boss, it lands ON THE BOSS
//    and nowhere else — boss_recess is deliberately much smaller than the boss
//    height, because a part that bottoms out on the stator would clamp the motor
//    solid.
// 6  Both axes are hollow: wires run through the tilt motor, up the arm, through
//    the bridge and up through the pan motor. No service loop to snag.
// 7  Anything read off a drawing instead of off calipers is marked MEASURE-ME
//    and is used by fit_coupon, so it gets checked for 12 g of PETG.
//
// -----------------------------------------------------------------------------
// BUILD ORDER (each step ends with something you can check by hand)
// -----------------------------------------------------------------------------
// 1  fit_coupon + bore_gauge. The coupon bolts to both faces of a real motor;
//    the gauge takes the real housing and clamps it. Fix the numbers HERE.
// 2  YOKE ONTO THE PAN MOTOR FIRST. Stand the yoke on its arm tips, drop the pan
//    motor into the bridge's locating recess (boss down), and drive six M3 up
//    from underneath. Do this while the yoke is EMPTY — once the head is in, those
//    six bolts are behind it.
// 3  base_plate down onto the pan motor's rear: four M4 through the counterbores.
//    You now have plate on top, motor, yoke hanging.
// 4  cradle -> tilt motor, on the bench: turn the output boss until one hole
//    points straight up, then drive the three bolts that sit ABOVE the split line.
//    They are the only three a driver can reach, and three is plenty.
// 5  trunnion -> cradle's right plate: three screws, heads outside. Head done.
// 6  Lift that subassembly up between the arms and bolt through the LEFT ARM from
//    the OUTSIDE into the tilt motor's rear holes. The head hangs on one side.
// 7  608 into bearing_carrier, carrier over the trunnion stub, three screws into
//    the right arm — LEFT LOOSE. Swing the head through its whole travel, THEN
//    tighten: the oversize screw holes let the bearing find the true axis.
// 8  Wires, through both hollow shafts. C-clamp to the shelf.
// 9  Lay the housing into the saddle, cap on, four screws. Slide it to balance
//    before you nip them down; fine trim is washers on an M4 through the keel.
//
// Companion: assembly.scad — every part, every bolt, poseable in pan and tilt.
// =============================================================================

/* [What to render] */
part = "all"; // [fit_coupon, bore_gauge, base_plate, yoke, cradle, cradle_cap, trunnion, bearing_carrier, all, none]

/* [Motor interface — MEASURE-ME] */
// RMD-L-5005. The nominals below are read off MyActuator's L-series drawing;
// every one of them is a guess until the coupon says otherwise.
motor_d      = 49;    // body OD — drawing
motor_len    = 24;    // rear face to front face — drawing
out_boss_d   = 36;    // MEASURE-ME  rotating output boss OD
out_boss_h   = 4;     // MEASURE-ME  how far the boss stands proud of the front face
out_bcd      = 30;    // MEASURE-ME  output-flange bolt circle
out_bolt_n   = 6;     // MEASURE-ME  how many holes in it
out_bolt_a0  = 0;     // MEASURE-ME  angle of the first hole
rear_bcd     = 43;    // MEASURE-ME  REAR cover bolt circle — this is the mount
rear_bolt_n  = 4;     // MEASURE-ME
rear_bolt_a0 = 45;    // MEASURE-ME
shaft_bore_d = 8.1;   // MEASURE-ME  hollow through-bore (8.1 on "S", 12.7 on "L")

/* [Payload — DLH-3UP-EH, off LEDdynamics' drawing] */
payload_od     = 25.15; // Ø0.99" over the fin crests — the clamped diameter
payload_body   = 22.6;  // 0.89" finned length: all the grip there is
payload_stub_d = 21.3;  // 1/2"-14 NPT major dia (the rear stub is the wire exit)
payload_stub_l = 9.4;   // 1.26" overall − 0.89" body
payload_clear  = 0.6;   // slide fit — "just over an inch", slides by hand
                        // the bore is cr_len long, the housing 32 mm: the extra
                        // 4 mm plus the clamp's grip is your whole balance range

/* [Frame] */
t_plate   = 8;    // base plate
t_bridge  = 9;    // yoke bridge
t_arm     = 10;   // yoke arms
drop      = 38;   // bridge underside -> tilt axis (must clear the head's swing)
arm_w_top = 40;   // arm width where it leaves the bridge
arm_w_bot = 54;   // arm width at the tilt axis (must cover the rear bolt circle)
cr_len    = 36;   // cradle length along the housing axis
cr_wall   = 8;    // cradle side plates: motor side and trunnion side
plate_z   = 18;   // side plates rise this far ABOVE the split line
base_z    = 20;   // ...and the saddle reaches this far below it
cap_z     = 22;   // cap's outer height
clamp_nip = 0.4;  // the cap's bore sits this low, so it PINCHES before it bottoms
cap_bolt_x = 17.5; cap_bolt_y = 11;   // the four cap screws
boss_recess = 1;  // locating recess depth — KEEP WELL UNDER out_boss_h
stop_r    = 31;   // pan hard-stop radius (post and groove centreline)
stop_w    = 8;    // groove width, radial
stop_deep = 4;    // groove depth
stop_arc  = 345;  // groove sweep -> 311 deg of usable pan travel

/* [Hardware] */
m3_clear = 3.4;  m3_pilot = 2.55; m3_head_d = 6.4;   // pilot = self-tapping into PETG
m4_clear = 4.5;  m4_head_d = 8.4;
bearing_od = 22; bearing_id = 8; bearing_w = 7;

$fn = 64;

// ---------------------------------------------------------------- derived ----
bore_d   = payload_od + payload_clear;          // 25.75 ≈ 1.014"
blk_in   = bore_d / 2 + 2;                      // 2 mm shoulder each side of the bore
x_left   = -(blk_in + cr_wall);                 // outer face of the motor-side plate
x_mate   = x_left + boss_recess;                // ...and the plane that lands on the boss
x_right  =   blk_in + cr_wall;                  // face the trunnion bolts to
trun_t   = 6;                                   // trunnion flange thickness
trun_gap = 4;                                   // clearance so the head drops into the yoke
carrier_t = 9;
boss_locate_d = out_boss_d + 0.4;

// the one chain that sets the whole machine's size
span_h   = (motor_len + out_boss_h - x_mate + x_right + trun_t + trun_gap) / 2;
arm_x    = span_h + t_arm / 2;                  // arm centreline
arm_out  = span_h + t_arm;
bore_x   = -span_h + motor_len + out_boss_h - x_mate;  // head's place on the tilt axis
z_tilt   = -t_bridge - drop;
arm_below = rear_bcd / 2 + 5;
arm_h    = drop + arm_below;
bridge_y = 2 * (stop_r + stop_w / 2 + 2);
post_h   = motor_len + out_boss_h - boss_recess + 3;   // 3 mm into the groove
stub_len = t_arm + carrier_t + trun_gap + 0.9;
head_sweep = sqrt(pow(cr_len / 2, 2) + pow(cap_z, 2));

echo(str("v4  span_in=", 2 * span_h, "  bore_x=", bore_x, "  arm_h=", arm_h,
         "  head_sweep=", head_sweep, " vs drop=", drop,
         "  slide=", cr_len - payload_body, "mm  stub_len=", stub_len));

// ---------------------------------------------------------------- helpers ----
module bolt_ring(bcd, d, n, h, a0 = 0) {        // ring in XY, drilled along Z
  for (i = [0 : n - 1]) rotate([0, 0, a0 + i * 360 / n])
    translate([bcd / 2, 0, 0]) cylinder(d = d, h = h, center = true);
}

module bolt_ring_x(bcd, d, n, len, a0 = 0) {    // ring in YZ, drilled along X
  for (i = [0 : n - 1]) rotate([a0 + i * 360 / n, 0, 0])
    translate([0, 0, bcd / 2]) rotate([0, 90, 0]) cylinder(d = d, h = len, center = true);
}

module zip_pair_z(spacing = 8) {                // two slots through a Z-thickness plate
  for (s = [-1, 1]) translate([0, s * spacing / 2, 0])
    linear_extrude(60, center = true) offset(r = 1.2) square([6, 0.1], center = true);
}
module zip_pair_x(spacing = 8) { rotate([0, 90, 0]) zip_pair_z(spacing); }

module arc_prism(r_in, r_out, angle, h) {       // ring segment h tall, centred on +X
  rotate([0, 0, -angle / 2])
    rotate_extrude(angle = angle) translate([r_in, 0]) square([r_out - r_in, h]);
}

// =============================================================================
// 1 · fit_coupon — bolts to a real motor before any real part is printed
// =============================================================================
module fit_coupon() {
  d = rear_bcd + 14;
  difference() {
    union() {
      cylinder(d = d, h = 3);
      translate([0, -d / 2 - 4, 0]) linear_extrude(3)
        offset(r = 3) square([16, 4], center = true);          // grab tab
    }
    bolt_ring(out_bcd,  m3_clear, out_bolt_n,  9, out_bolt_a0);
    bolt_ring(rear_bcd, m4_clear, rear_bolt_n, 9, rear_bolt_a0);
    cylinder(d = shaft_bore_d, h = 9, center = true);
    // scribe rings: lay the coupon on the motor and read the fit by eye
    for (dia = [out_boss_d, motor_d]) translate([0, 0, 2.4]) difference() {
      cylinder(d = dia + 0.5, h = 2);
      translate([0, 0, -1]) cylinder(d = dia - 0.5, h = 4);
    }
    // legends, so the two circles can't be mixed up
    translate([0, out_bcd / 2 - 8, 2.2]) linear_extrude(1.2)
      text("OUT", size = 4.5, halign = "center", valign = "center");
    translate([0, -rear_bcd / 2 + 5, 2.2]) linear_extrude(1.2)
      text("REAR", size = 4.5, halign = "center", valign = "center");
  }
}

// =============================================================================
// 2 · bore_gauge — one slice of the cradle's clamp: slide fit + pinch test
// =============================================================================
module bore_gauge() {
  gl = 14;
  difference() {                                                 // saddle slice
    translate([x_left, -gl / 2, -base_z]) cube([x_right - x_left, gl, base_z + plate_z]);
    translate([0, -gl / 2 - 1, 0]) rotate([-90, 0, 0]) cylinder(d = bore_d, h = gl + 2);
    translate([-blk_in, -gl / 2 - 1, 0.02]) cube([2 * blk_in, gl + 2, plate_z + 1]);
    for (x = [-cap_bolt_x, cap_bolt_x]) translate([x, 0, plate_z - 15])
      cylinder(d = m3_pilot, h = 17);
  }
  translate([0, gl + 6, 0]) difference() {                       // cap slice, printed alongside
    translate([-blk_in, -gl / 2, 0]) cube([2 * blk_in, gl, cap_z]);
    translate([0, -gl / 2 - 1, -clamp_nip]) rotate([-90, 0, 0]) cylinder(d = bore_d, h = gl + 2);
    translate([-bore_d, -gl / 2 - 1, -bore_d - clamp_nip]) cube([2 * bore_d, gl + 2, bore_d]);
    for (x = [-cap_bolt_x, cap_bolt_x]) translate([x, 0, 0]) {
      cylinder(d = m3_clear, h = cap_z);
      translate([0, 0, 5.2]) cylinder(d = m3_head_d, h = cap_z);
    }
  }
  translate([0, gl + 6, 0]) for (x = [-cap_bolt_x, cap_bolt_x], sx = [1])   // feet on the cap slice
    translate([x, 0, plate_z + clamp_nip]) hull() {
      cylinder(d = 11, h = cap_z - plate_z - clamp_nip);
      translate([(blk_in - abs(x)) * sign(x), 0, 0]) cylinder(d = 11, h = cap_z - plate_z - clamp_nip);
    }
}

// =============================================================================
// 3 · base_plate — the only part that touches the world.
// prints POST UP; installs POST DOWN, motor and post both under the plate.
// origin = centre of the face the pan motor's rear cover bolts to
// =============================================================================
module base_plate() {
  difference() {
    union() {
      linear_extrude(t_plate) offset(r = 6) offset(r = -6) union() {
        offset(r = 8) square([68, 62], center = true);       // hub over the motor
        translate([-22, -90]) square([44, 62]);              // aft tongue for the C-clamp
      }
      rotate([0, 0, 270]) {                                  // hard-stop post, aft
        translate([0, 0, -post_h])
          arc_prism(stop_r - stop_w / 2 + 0.7, stop_r + stop_w / 2 - 0.7, 34, post_h);
        translate([0, 0, -7])                                // gusset, grows OUTWARD only
          arc_prism(stop_r - stop_w / 2 + 0.7, stop_r + 8, 34, 7);
      }
    }
    // pan motor: rear cover bolts UP into the plate, heads counterbored flush
    bolt_ring(rear_bcd, m4_clear, rear_bolt_n, 3 * t_plate, rear_bolt_a0);
    translate([0, 0, t_plate + 0.8])
      bolt_ring(rear_bcd, m4_head_d, rear_bolt_n, 8, rear_bolt_a0);   // 3.2 deep
    cylinder(d = 13, h = 3 * t_plate, center = true);         // wire pass
    for (y = [-52, -72]) translate([0, y, 0]) rotate([0, 0, 90]) zip_pair_z();
    for (x = [-30, 30]) translate([x, 25, 0]) zip_pair_z();
  }
}

// =============================================================================
// 4 · yoke — bridge + both arms in ONE part. Prints ARMS UP, bridge on the bed.
// origin = centre of the bridge's TOP face; the boss lands boss_recess below it
// =============================================================================
module arm_blank() {
  hull() {
    translate([0, 0, -t_bridge - 0.01]) linear_extrude(0.01)
      square([t_arm, arm_w_top], center = true);
    translate([0, 0, -t_bridge - arm_h]) linear_extrude(0.01)
      square([t_arm, arm_w_bot], center = true);
  }
}

module yoke() {
  difference() {
    union() {
      translate([0, 0, -t_bridge]) linear_extrude(t_bridge)
        offset(r = 8) offset(r = -8) square([2 * arm_out, bridge_y], center = true);
      for (s = [-1, 1]) translate([s * arm_x, 0, 0]) arm_blank();
    }

    // --- bridge: pan output interface --------------------------------------
    translate([0, 0, -boss_recess]) cylinder(d = boss_locate_d, h = boss_recess + 1);
    bolt_ring(out_bcd, m3_clear, out_bolt_n, 3 * t_bridge, out_bolt_a0);
    cylinder(d = 13, h = 3 * t_bridge, center = true);                // wire pass
    // --- bridge: pan hard-stop groove (island at +Y, so home is mid-travel) -
    rotate([0, 0, 97.5]) rotate_extrude(angle = stop_arc)
      translate([stop_r - stop_w / 2, -stop_deep]) square([stop_w, stop_deep + 0.01]);
    // --- bridge: tie-down holes in the dead corners -------------------------
    for (sx = [-1, 1], sy = [-1, 1]) translate([sx * 32, sy * 30, 0])
      cylinder(d = 10, h = 3 * t_bridge, center = true);
    // --- bridge underside: cable run from the left arm to the centre --------
    translate([-arm_out, -13.5, -t_bridge - 0.01]) cube([arm_out, 9, 3]);

    // --- LEFT arm: the tilt motor bolts to its inner face -------------------
    translate([-arm_x, 0, z_tilt]) {
      bolt_ring_x(rear_bcd, m4_clear, rear_bolt_n, 4 * t_arm, rear_bolt_a0);
      rotate([0, 90, 0]) cylinder(d = 13, h = 4 * t_arm, center = true);   // wire pass
      translate([t_arm / 2 - 1.2, 0, 0]) rotate([0, 90, 0])
        cylinder(d = rear_bcd - 9, h = 2.5, center = true);                // cover relief
    }
    // --- RIGHT arm: trunnion stub passes; carrier screws from the outside ---
    translate([arm_x, 0, z_tilt]) {
      rotate([0, 90, 0]) cylinder(d = 13, h = 4 * t_arm, center = true);
      bolt_ring_x(34, m3_pilot, 3, 2.4 * t_arm, 90);
    }
    // --- both arms: cable channel up the outer face + zip anchors -----------
    for (s = [-1, 1]) translate([s * arm_out, -13.5, 0]) {
      translate([s == -1 ? 0 : -3, 0, z_tilt]) cube([3, 9, -z_tilt]);
      for (z = [z_tilt + 15, z_tilt + 33]) translate([0, 4.5, z]) zip_pair_x();
    }
  }
}

// =============================================================================
// 5 · cradle — the head, as a SPLIT CLAMP. The housing lays into the saddle and
// the cap pinches it, so nothing has to thread through a long bore and the whole
// space above the split line is empty while you bolt the motor on.
// Housing axis = Y, tilt axis = X, origin = where they cross.
// =============================================================================
// which of the output-flange holes sit ABOVE the split line — the only ones a
// driver can reach, and the reason the boss gets turned one hole "up" first
function out_bolt_z(i) = out_bcd / 2 * cos(out_bolt_a0 + i * 360 / out_bolt_n);

module cradle_profile() {
  difference() {
    union() {
      translate([x_left, -base_z]) square([x_right - x_left, base_z]);      // saddle base
      translate([x_left, 0]) square([cr_wall, plate_z]);                    // motor-side plate
      translate([blk_in, 0]) square([cr_wall, plate_z]);                    // trunnion-side plate
    }
    translate([0, 0.02]) intersection() {                                   // lower half-bore
      circle(d = bore_d);
      translate([-bore_d, -bore_d]) square([2 * bore_d, bore_d]);
    }
    for (sx = [-1, 1]) translate([sx * x_right, -base_z]) rotate(45)        // corner chamfers
      square([4.6, 4.6], center = true);
  }
}

module cradle() {
  difference() {
    rotate([90, 0, 0]) translate([0, 0, -cr_len / 2])
      linear_extrude(cr_len) cradle_profile();

    // --- motor-side plate: the three reachable output-flange bolts ---------
    for (i = [0 : out_bolt_n - 1]) if (out_bolt_z(i) > 2)
      rotate([out_bolt_a0 + i * 360 / out_bolt_n, 0, 0]) translate([0, 0, out_bcd / 2])
        rotate([0, 90, 0]) cylinder(d = m3_clear, h = 3 * cr_wall, center = true);
    translate([x_left - 0.01, 0, 0]) rotate([0, 90, 0])                     // boss recess
      cylinder(d = boss_locate_d, h = boss_recess + 0.01);
    // wire path: straight through on the axis into the motor's hollow shaft. The
    // bundle then runs aft along the channel in the cap's corner (see cradle_cap).
    rotate([0, 90, 0]) translate([0, 0, x_left - 1]) cylinder(d = 10, h = cr_wall + 2);

    // --- trunnion-side plate: three screws, driven from OUTSIDE ------------
    translate([blk_in + cr_wall / 2, 0, 0]) bolt_ring_x(18, m3_pilot, 3, cr_wall + 5, 90);

    // --- the four cap screws ----------------------------------------------
    for (x = [-cap_bolt_x, cap_bolt_x], y = [-cap_bolt_y, cap_bolt_y])
      translate([x, y, plate_z - 15]) cylinder(d = m3_pilot, h = 17);

    // --- trim-weight hole, on the vertical centreline ---------------------
    translate([0, 0, -base_z + 3.6]) rotate([90, 0, 0])
      cylinder(d = m4_clear, h = cr_len + 2, center = true);
  }
}

// -----------------------------------------------------------------------------
// 5b · cradle_cap — the other half of the clamp. Prints INVERTED (its outside on
// the bed), so its half-bore is a valley: accurate, no supports.
// -----------------------------------------------------------------------------
module cradle_cap() {
  difference() {
    union() {
      rotate([90, 0, 0]) translate([0, 0, -cr_len / 2]) linear_extrude(cr_len)
        difference() {
          translate([-blk_in, 0]) square([2 * blk_in, cap_z]);
          translate([0, -clamp_nip]) intersection() {                       // upper half-bore
            circle(d = bore_d);
            translate([-bore_d, 0]) square([2 * bore_d, bore_d]);
          }
          for (sx = [-1, 1]) translate([sx * (blk_in - 3), 2.6])            // wire channels
            square([6, 5.2], center = true);
          for (s = [-1, 1]) translate([s * blk_in, cap_z]) rotate(45)
            square([4.6, 4.6], center = true);
        }
      // four feet that land on the side plates
      for (x = [-cap_bolt_x, cap_bolt_x], y = [-cap_bolt_y, cap_bolt_y])
        translate([x, y, plate_z + clamp_nip]) hull() {
          cylinder(d = 11, h = cap_z - plate_z - clamp_nip);
          translate([(blk_in - abs(x)) * sign(x), 0, 0])
            cylinder(d = 11, h = cap_z - plate_z - clamp_nip);
        }
    }
    for (x = [-cap_bolt_x, cap_bolt_x], y = [-cap_bolt_y, cap_bolt_y])
      translate([x, y, plate_z]) {
        cylinder(d = m3_clear, h = cap_z);
        translate([0, 0, 5.2]) cylinder(d = m3_head_d, h = cap_z);          // counterbore
      }
  }
}

// =============================================================================
// 6 · trunnion — the printed axle. Prints STUB UP: no bridge, no steel.
// origin = the cradle face it bolts to; stub runs +X
// =============================================================================
module trunnion() {
  difference() {
    rotate([0, 90, 0]) union() {
      cylinder(d = 26, h = trun_t);                                    // flange
      cylinder(d1 = 26, d2 = 12, h = 5);                               // taper into the stub
      translate([0, 0, trun_t]) cylinder(d = bearing_id - 0.15, h = stub_len);
      translate([0, 0, trun_t + stub_len - 1])                         // lead-in chamfer
        cylinder(d1 = bearing_id - 0.15, d2 = bearing_id - 1.8, h = 1);
    }
    translate([trun_t / 2, 0, 0]) bolt_ring_x(18, m3_clear, 3, 3 * trun_t, 90);
  }
}

// =============================================================================
// 7 · bearing_carrier — the 608 pocket prints as a first-layer-accurate hole.
// Oversize screw holes on purpose: this part FINDS the axis, it doesn't set it.
// origin = the arm's outer face; body runs +X
// =============================================================================
module bearing_carrier() {
  difference() {
    rotate([0, 90, 0]) cylinder(d = 46, h = carrier_t);
    // bearing pocket, opening outward so you can see and push on the bearing
    translate([carrier_t - bearing_w - 0.3, 0, 0]) rotate([0, 90, 0])
      cylinder(d = bearing_od + 0.05, h = bearing_w + 0.4);
    rotate([0, 90, 0]) cylinder(d = bearing_od - 4, h = 3 * carrier_t, center = true);
    rotate([0, 90, 0]) cylinder(d1 = bearing_od - 1, d2 = bearing_od - 4, h = 1.5);
    translate([carrier_t / 2, 0, 0]) bolt_ring_x(34, m3_clear + 0.8, 3, 3 * carrier_t, 90);
  }
}

// =============================================================================
// print orientations — `part="x"` gives you a slice-ready part
// =============================================================================
module p_fit_coupon()      { fit_coupon(); }
module p_bore_gauge()      { bore_gauge(); }
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
  // one X1C plate (256 x 256), everything flat, nothing touching
  translate([  0, -84, 0]) rotate([0, 0, 90]) p_base_plate();
  translate([  0,   5, 0])                    p_yoke();
  translate([-88,  62, 0])                    p_cradle();
  translate([-86, 104, 0])                    p_cradle_cap();
  translate([-24,  88, 0])                    p_bore_gauge();
  translate([ 78,  78, 0])                    p_fit_coupon();
  translate([ 82, -14, 0])                    p_bearing_carrier();
  translate([116,  22, 0])                    p_trunnion();
}
