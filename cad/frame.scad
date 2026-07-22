// frame.scad — Engineered Lighting gimbal frame (Doc 3b · Print the Frame)
// Motor: MyActuator RMD-L-5005 (Ø49 × ~24 mm body, 92 g).
// Geometry truth = MyActuator's L-series 2D drawing + YOUR calipers.
// Every MEASURE-ME value is a placeholder nominal: measure the real motor on
// arrival, update, re-render. Print fit_coupon() before any real part.

/* [Part selector] */
part = "coupon"; // [coupon, pan_base, yoke, head_shell, all]

/* [Motor interface — MEASURE-ME] */
flange_bolt_circle_d = 30;   // MEASURE-ME — output-flange bolt-circle diameter
flange_bolt_d        = 3.2;  // MEASURE-ME — bolt clearance hole (M3 assumed)
flange_bolt_n        = 4;    // MEASURE-ME — bolt count per the drawing
flange_center_bore_d = 8.1;  // drawing: 8.1 mm thru-bore on the "S" variant
                             // (12.7 mm on the "L") — verify with calipers on arrival
body_d               = 49;   // drawing: Ø49 body — verify with calipers on arrival
body_len             = 24;   // drawing: ~24 mm body — verify with calipers on arrival
connector_clearance  = 12;   // MEASURE-ME — depth behind the 4-pin connector + cable bend

/* [Payload + frame] */
flashlight_d = 25;   // MEASURE-ME — flashlight/LED head barrel diameter
arm_offset   = 8;    // daylight between yoke arm and motor body
wall         = 4;    // structural wall thickness
bearing_od   = 22;   // 608 bearing OD (683 = 7 mm) — measure the one you bought
bearing_w    = 7;    // bearing width
clamp_ear_w  = 30;   // C-clamp ear width
hard_stop_h  = 6;    // hard-stop post/tab height

$fn = 64;

// ---- helpers ---------------------------------------------------------------
module flange_bolts(h = 10) {
  for (i = [0 : flange_bolt_n - 1])
    rotate([0, 0, i * 360 / flange_bolt_n])
      translate([flange_bolt_circle_d / 2, 0, -1])
        cylinder(d = flange_bolt_d, h = h + 2);
}

// ---- 1 · fit coupon: print me first (~5 min) -------------------------------
// A 3 mm ring matching the flange interface. Bolts thread + ring seats flush
// before any 20-minute part prints.
module fit_coupon() {
  difference() {
    cylinder(d = flange_bolt_circle_d + 4 * wall, h = 3);
    translate([0, 0, -1]) cylinder(d = flange_center_bore_d, h = 5);
    flange_bolts(3);
  }
}

// ---- 2 · pan base: clamps to the shelf, motor hangs from it ----------------
// Hard-stop post exists because the encoder is single-turn: the frame, not
// software, guarantees the motor can never wind past one revolution.
module pan_base() {
  difference() {
    union() {
      cylinder(d = body_d + 2 * wall, h = wall);                       // motor plate
      translate([-(clamp_ear_w / 2), body_d / 2 - 1, 0])               // clamp ear
        cube([clamp_ear_w, clamp_ear_w + 1, wall]);
      translate([body_d / 2 - 2, -hard_stop_h / 2, wall - 0.01])       // pan hard stop
        cube([wall, hard_stop_h, hard_stop_h]);
    }
    translate([0, 0, -1]) cylinder(d = flange_center_bore_d, h = wall + 2);
    flange_bolts(wall);
  }
}

// ---- 3 · yoke: U-bracket on the pan flange ---------------------------------
// One arm carries the tilt motor body; the other a bearing pocket. Arms rise
// with ≤45° hull transitions so the X1C prints them support-free, arms-up.
module yoke_arm(bore_d, pocket_depth) {
  arm_h = body_d / 2 + arm_offset + bore_d / 2 + wall;
  difference() {
    hull() {                                                            // ≤45° root
      cube([wall + pocket_depth, body_d / 2, 1]);
      translate([0, body_d / 8, arm_h * 0.35])
        cube([wall + pocket_depth, body_d / 4, arm_h * 0.65]);
    }
    translate([-1, body_d / 4, arm_h - bore_d / 2 - wall])              // bore/pocket
      rotate([0, 90, 0])
        cylinder(d = bore_d, h = pocket_depth + 1);
    translate([wall + pocket_depth - 3, body_d / 2 - 6, arm_h * 0.4])   // zip-tie point
      rotate([90, 0, 0]) cylinder(d = 4, h = body_d / 2);
  }
}

module yoke() {
  span = body_d + 2 * arm_offset;
  difference() {
    cylinder(d = flange_bolt_circle_d + 4 * wall, h = wall);            // flange disc
    translate([0, 0, -1]) cylinder(d = flange_center_bore_d, h = wall + 2);
    flange_bolts(wall);
  }
  translate([span / 2, -body_d / 4, 0]) yoke_arm(body_d, body_len / 2); // motor arm
  mirror([1, 0, 0])
    translate([span / 2, -body_d / 4, 0]) yoke_arm(bearing_od, bearing_w); // bearing arm
  translate([-hard_stop_h / 2, flange_bolt_circle_d / 2 + wall, wall - 0.01])
    cube([hard_stop_h, wall, hard_stop_h]);                             // tilt hard stop
}

// ---- 4 · head shell: payload on the tilt flange ----------------------------
// Counterweight slot (M5 bolt + stacked nuts) exists because balance is the
// silence mechanism: a balanced head holds at near-zero current.
module head_shell() {
  tail = 40;
  difference() {
    union() {
      cylinder(d = flange_bolt_circle_d + 4 * wall, h = wall);          // flange disc
      translate([0, 0, wall - 0.01])                                    // payload bore
        cylinder(d = flashlight_d + 2 * wall, h = flashlight_d);
      translate([-(flashlight_d / 2), -(flange_bolt_circle_d / 2) - tail, 0])
        cube([flashlight_d, tail, wall]);                               // counterweight tail
    }
    translate([0, 0, wall]) cylinder(d = flashlight_d, h = flashlight_d + 1);
    flange_bolts(wall);
    translate([-2.65, -(flange_bolt_circle_d / 2) - tail + 4, -1])      // M5 slot
      cube([5.3, tail - 8, wall + 2]);
  }
}

// ---- render ----------------------------------------------------------------
if (part == "coupon") fit_coupon();
if (part == "pan_base") pan_base();
if (part == "yoke") yoke();
if (part == "head_shell") head_shell();
if (part == "all") {
  fit_coupon();
  translate([80, 0, 0]) pan_base();
  translate([0, 100, 0]) yoke();
  translate([100, 100, 0]) head_shell();
}
