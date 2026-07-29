// frame.scad — Engineered Lighting gimbal frame · v3 (Doc 3b · Print the Frame)
//
// Motor:   MyActuator RMD-L-5005 (Ø49 × ~24 mm, 92 g).
// Payload: DLH-3UP-EH aluminum LED housing (Ø0.99" finned barrel, 1.26" long,
//          hollow 1/2"-14 NPT rear = wire exit). The housing is BOTH the
//          star's heatsink and the head's sliding balance mass; the cradle
//          ID is payload_od + payload_clear ≈ 25.75 mm ≈ 1.014" so it slips
//          in and glides. A ~Ø25 mm flashlight fits as the bench stand-in.
//
// v3 REDESIGN (2026-07-29, from Marcelo's fit review of v2):
//   · EVERY part prints FLAT exactly as modeled — no supports anywhere.
//     Strength comes from bolted joints, not tall fragile prints.
//   · Motors are BOLTED, never friction-fit: the pan base uses the motor's
//     back-cover mounting pattern; the tilt arm face-mounts the motor
//     around a boss clearance window. (A collar can't even slide over the
//     body — the 4-pin connector is in the way. Face-mounting leaves the
//     connector hanging in free air.)
//   · Plates join with one repeated T-joint: printed tabs drop into slots,
//     then two M3 bolts pass through the slotted plate into SQUARE NUTS
//     side-loaded into pockets in the tabbed plate. Print flat, bolt square.
//   · The head's second support is an M8 bolt: outside → through the 608 in
//     the bearing arm → into the captive M8 nut in the head end plate.
//
// ASSEMBLY ORDER (the design is built around this — see Doc 3b):
//   1  pan motor's BACK bolts under pan_base; C-clamp the ear to a shelf.
//   2  yoke_bridge bolts to the pan output flange.
//   3  arm_motor + arm_bearing tab up into the bridge; 2× M3 each, nuts in
//      the arms' edge pockets. You now have a rigid hanging U.
//   4  head_boss_plate bolts to the TILT motor's output flange — on the
//      desk, with room to swing a driver.
//   5  head_main_plate tabs into the boss plate (2× M3); head_end_plate
//      tabs onto its far edge (drop the M8 nut into its pocket first).
//   6  tilt motor — head hanging on it — face-bolts to arm_motor from the
//      outside. Press the 608 into arm_bearing's pocket. Slide the M8 in
//      from outside, through the bearing, into the end-plate nut. The head
//      is now supported on BOTH sides of the yoke.
//   7  cradle_ring face-bolts over the main plate's housing window (3× M3).
//      Slide the LED housing through; balance; nip the ring's pinch bolt.
//
// BALANCING (two orthogonal trims): slide the housing fore/aft in the
// cradle for beam-axis balance, then slide the M5 + nuts up/down the tail
// slot for the vertical trim. Powered-off head stays posed = done.
//
// Geometry truth = MyActuator's L-series 2D drawing + the housing drawing +
// YOUR calipers. Every MEASURE-ME is a placeholder nominal. Print the
// fit_coupon FIRST — it proves BOTH motor bolt patterns at once.

/* [Part selector] */
part = "coupon"; // [coupon, pan_base, yoke_bridge, arm_motor, arm_bearing, head_boss_plate, head_main_plate, head_end_plate, cradle_ring, all]

/* [Motor interface — MEASURE-ME] */
flange_bolt_circle_d = 30;   // MEASURE-ME — output-flange bolt circle
flange_bolt_d        = 3.2;  // MEASURE-ME — output-flange bolt clearance (M3?)
flange_bolt_n        = 4;    // MEASURE-ME — bolt count per the drawing
flange_center_bore_d = 8.1;  // drawing: 8.1 mm thru-bore ("S" variant; 12.7 on "L")
boss_clear_d         = 34;   // MEASURE-ME — output flange OD + 2 mm swing room
mount_bolt_circle_d  = 43;   // MEASURE-ME — FRONT face-mount holes around the boss
mount_bolt_d         = 2.8;  // MEASURE-ME — front mount clearance (M2.5 assumed)
mount_bolt_n         = 4;    // MEASURE-ME — count per the drawing
back_bolt_circle_d   = 43;   // MEASURE-ME — BACK cover mounting holes (pan side)
back_bolt_d          = 2.8;  // MEASURE-ME — back mount clearance (M2.5 assumed)
back_bolt_n          = 4;    // MEASURE-ME — count per the drawing
body_d               = 49;   // drawing: Ø49 body — verify on arrival
body_len             = 24;   // drawing: ~24 mm body — verify on arrival

/* [Payload + frame] */
payload_od    = 25.15; // MEASURE-ME — DLH-3UP-EH barrel, Ø0.99" per its drawing
payload_clear = 0.6;   // slide fit: slip in, glide to balance
ring_w        = 10;    // cradle ring thickness (grip on the finned barrel)
arm_offset    = 8;     // daylight between arm plate and motor body
t             = 6;     // plate thickness, everywhere
bearing_od    = 22;    // 608 (683 = 7 mm) — measure the one you bought
bearing_w     = 7;     // bearing width
m8_clear      = 8.4;   // M8 axle clearance
clamp_ear_w   = 30;    // C-clamp ear width
hard_stop_h   = 6;     // pan hard-stop post height

$fn = 64;

// ---- derived -------------------------------------------------------------------
cradle_id = payload_od + payload_clear;    // ≈ 25.75 mm ≈ 1.014"
span      = body_d + 2 * arm_offset;       // inner face → inner face of the arms
drop      = body_d / 2 + arm_offset;       // bridge underside → tilt axis
arm_w     = 60;                            // arm plate width  (covers the Ø43 pattern)
arm_h     = drop + 28;                     // arm plate height (axis 28 above the toe)
gap       = 0.4;                           // printed tab/slot clearance
nut_w     = 5.8;                           // M3 square nut pocket (5.5 nominal)
nut_t     = 2.7;                           //   ... pocket thickness (2.4 nominal)
head_L    = 49;                            // head: boss-plate face → end-plate face
                                           // (spans the yoke gap so the M8 engages
                                           //  its nut just inboard of the bearing)
js_arm    = 13;                            // arm↔bridge joint: tab centers ±13
jb_arm    = 25;                            //   ... bolt lines at ±25
js_head   = 9;                             // head joints: tab centers ±9
jb_head   = 21;                            //   ... bolt lines at ±21

// ---- shared bits ------------------------------------------------------------------
module bolt_circle(bcd, d, n, h = t, a0 = 0) {
  for (i = [0 : n - 1]) rotate([0, 0, a0 + i * 360 / n])
    translate([bcd / 2, 0, -1]) cylinder(d = d, h = h + 2);
}
// Tabs along a part's +y edge (edge line y=0), poking +y by one thickness.
module tabs_up(centers, w = 12) {
  for (c = centers) translate([c - w / 2, -0.01, 0]) cube([w, t + 0.01, t]);
}
// Edge hardware for the tabbed part: M3 pilot drilled INTO the y=0 edge at
// x = each bolt line, plus a square-nut pocket 8 mm in, loaded from the top face.
module edge_bolt_cuts(lines) {
  for (c = lines) {
    translate([c, 0.01, t / 2]) rotate([90, 0, 0]) cylinder(d = 3.2, h = 17);
    translate([c - nut_w / 2, -8 - nut_w, t / 2 - nut_t / 2])
      cube([nut_w, nut_w, t]);                       // open to the top face
  }
}
// Cuts for the slotted plate: tab slots + M3 clearance, along a line x = x0.
module slot_line_cuts(x0, centers, lines, w = 12) {
  for (c = centers)
    translate([x0 - (t + gap) / 2, c - (w + gap) / 2, -1])
      cube([t + gap, w + gap, t + 2]);
  for (c = lines) translate([x0, c, -1]) cylinder(d = 3.4, h = t + 2);
}

// ---- 1 · fit coupon: print me first (~5 min) ---------------------------------------
// One 3 mm disc proves EVERYTHING against the real motor: output-flange bolts
// thread the inner circle, face-mount bolts thread the outer circle, the
// center bore clears, and the scribed groove shows the boss swing clearance.
module fit_coupon() {
  difference() {
    cylinder(d = mount_bolt_circle_d + 12, h = 3);
    translate([0, 0, -1]) cylinder(d = flange_center_bore_d, h = 5);
    bolt_circle(flange_bolt_circle_d, flange_bolt_d, flange_bolt_n, 3);
    bolt_circle(mount_bolt_circle_d, mount_bolt_d, mount_bolt_n, 3, 45);
    translate([0, 0, 2.2]) difference() {                        // boss-clearance scribe
      cylinder(d = boss_clear_d + 1, h = 1);
      translate([0, 0, -1]) cylinder(d = boss_clear_d - 1, h = 3);
    }
  }
}

// ---- 2 · pan base: clamps to the shelf, pan motor bolts UNDER it -------------------
// Uses the motor's BACK-cover holes; output flange faces down at the yoke.
// The hard-stop post is a Ø8 pillar on the ear, LONG enough to reach down
// into the yoke bridge's swing plane — the bridge corner meets it at the
// travel limit. (Install the plate post-side DOWN; it prints post-up, flat.)
module pan_base() {
  difference() {
    union() {
      cylinder(d = body_d + 2 * t, h = t);                           // motor plate
      translate([-(clamp_ear_w / 2), body_d / 2 - 1, 0])             // clamp ear
        cube([clamp_ear_w, clamp_ear_w + 1, t]);
      translate([0, 48, t - 0.01]) cylinder(d = 8, h = 32);          // pan hard stop
    }
    translate([0, 0, -1]) cylinder(d = 14, h = t + 2);               // wire pass
    bolt_circle(back_bolt_circle_d, back_bolt_d, back_bolt_n);       // back-cover bolts
  }
}

// ---- 3 · yoke bridge: flat bar on the pan output flange ----------------------------
// The arms tab into it from below; M3s drop through into the arms' edge nuts.
module yoke_bridge() {
  L = span + 2 * t + 28;
  difference() {
    translate([-L / 2, -30, 0]) cube([L, 60, t]);
    translate([0, 0, -1]) cylinder(d = flange_center_bore_d, h = t + 2);
    bolt_circle(flange_bolt_circle_d, flange_bolt_d, flange_bolt_n);    // pan flange
    for (sx = [-1, 1])
      slot_line_cuts(sx * (span + t) / 2, [-js_arm, js_arm], [-jb_arm, jb_arm]);
  }
}

// ---- 4/5 · the two arm plates -------------------------------------------------------
// Flat plates; the tilt axis crosses them `drop` below the bridge underside.
module arm_blank() {
  difference() {
    translate([-arm_w / 2, -arm_h, 0]) cube([arm_w, arm_h, t]);
    edge_bolt_cuts([-jb_arm, jb_arm]);
    for (sx = [-1, 1]) translate([sx * (arm_w / 2 - 7), -arm_h + 8, -1])
      cylinder(d = 4.2, h = t + 2);                                  // zip-tie points
  }
  tabs_up([-js_arm, js_arm]);
}
module arm_motor() {                        // tilt motor face-bolts to this one
  difference() {
    arm_blank();
    translate([0, -drop, -1]) cylinder(d = boss_clear_d, h = t + 2);   // boss window
    translate([0, -drop, 0])
      bolt_circle(mount_bolt_circle_d, mount_bolt_d, mount_bolt_n, t, 45);
    translate([0, -drop + boss_clear_d / 2 + 8, -1]) cylinder(d = 2.9, h = t + 2);
      // ^ tilt hard-stop: thread an M3 standoff here once travel is chosen
  }
}
module arm_bearing() {                      // the 608 lives in this one
  // The 608 is 7 wide but the plate is 6 thick, so a printed boss pad grows
  // the seat: 4 mm pad + 6 mm plate = 7 mm pocket with a 3 mm shoulder.
  // The pad is on the top print face — still prints flat, no supports.
  difference() {
    union() {
      arm_blank();
      translate([0, -drop, 0]) cylinder(d = bearing_od + 12, h = t + 4);  // boss pad
    }
    translate([0, -drop, -1]) cylinder(d = m8_clear, h = t + 6);          // M8 through
    translate([0, -drop, 3])                                              // 608 pocket,
      cylinder(d = bearing_od + 0.4, h = t + 4);                          // 3 mm shoulder
  }
}

// ---- 6 · head boss plate: bolts to the TILT output flange --------------------------
// Its flange pattern is rotated 45° so the bolts sit clear of the slot line.
module head_boss_plate() {
  difference() {
    translate([-16, -28, 0]) cube([32, 56, t]);
    translate([0, 0, -1]) cylinder(d = flange_center_bore_d, h = t + 2);
    bolt_circle(flange_bolt_circle_d, flange_bolt_d, flange_bolt_n, t, 45);
    slot_line_cuts(-8, [-js_head, js_head], [-jb_head, jb_head]);
      // ^ the main plate joins along this line, offset -8 so that plate +
      //   ring together grip the housing near the CENTER of its barrel
  }
}

// ---- 7 · head main plate: one flat part carries the whole head ---------------------
// Housing window mid-span (the ring does the gripping — together ~16 mm of
// guided bore), ring bolt holes around it, tabs on BOTH short edges, and a
// tail below with a VERTICAL M5 slot: the housing slide trims fore/aft
// balance, the M5 stack trims up/down. Prints flat.
module head_main_plate() {
  difference() {
    union() {
      translate([0, -28, 0]) cube([head_L, 56, t]);
      translate([head_L / 2 - 8, -58, 0]) cube([16, 32, t]);           // trim tail
      // tabs, left edge (→ boss plate) and right edge (→ end plate)
      for (c = [-js_head, js_head]) {
        translate([-t, c - 6, 0]) cube([t + 0.01, 12, t]);
        translate([head_L - 0.01, c - 6, 0]) cube([t + 0.01, 12, t]);
      }
    }
    translate([head_L / 2, 0, -1]) cylinder(d = cradle_id + 1, h = t + 2); // window
    translate([head_L / 2, 0, 0]) bolt_circle(cradle_id + 10, 3.4, 2, t, 90);
    translate([head_L / 2 - 2.65, -52, -1]) cube([5.3, 20, t + 2]);    // M5 trim slot
    // edge bolts + nut pockets, both short edges
    for (c = [-jb_head, jb_head]) {
      translate([0.01, c, t / 2]) rotate([0, -90, 0]) cylinder(d = 3.2, h = 17);
      translate([8, c - nut_w / 2, t / 2 - nut_t / 2]) cube([nut_w, nut_w, t]);
      translate([head_L - 0.01, c, t / 2]) rotate([0, 90, 0]) cylinder(d = 3.2, h = 17);
      translate([head_L - 8 - nut_w, c - nut_w / 2, t / 2 - nut_t / 2])
        cube([nut_w, nut_w, t]);
    }
  }
}

// ---- 8 · head end plate: catches the M8 axle ----------------------------------------
module head_end_plate() {
  difference() {
    translate([-16, -28, 0]) cube([32, 56, t]);
    translate([0, 0, -1]) cylinder(d = m8_clear, h = t + 2);
    translate([0, 0, t - 3.3]) cylinder(d = 15.4, h = 4, $fn = 6);     // captive M8 nut
    slot_line_cuts(-8, [-js_head, js_head], [-jb_head, jb_head]);
      // ^ same slot line as the boss plate: both plates mount in the same
      //   orientation, main plane offset -8 from the tilt-axis centerline
  }
}

// ---- 9 · cradle ring: the DLH housing's pinch clamp ---------------------------------
// Prints FLAT (strongest hoop), then face-bolts over the main plate's window.
// Slit + ears: one M3 pinches the ring closed once the head balances.
module cradle_ring() {
  difference() {
    union() {
      cylinder(d = cradle_id + 10, h = ring_w);                        // the ring
      for (a = [90, 270]) rotate([0, 0, a])                            // bolt lugs
        translate([cradle_id / 2 - 1, -6, 0]) cube([9.5, 12, ring_w]);
      translate([cradle_id / 2 - 1, -8, 0]) cube([13, 16, ring_w]);    // pinch ears
    }
    translate([0, 0, -1]) cylinder(d = cradle_id, h = ring_w + 2);     // payload bore
    translate([cradle_id / 2 - 2, -1, -1]) cube([17, 2, ring_w + 2]);  // slit
    translate([cradle_id / 2 + 7, -9, ring_w / 2]) rotate([-90, 0, 0]) // pinch bolt
      cylinder(d = 3.2, h = 18);
    for (a = [90, 270]) rotate([0, 0, a])                              // lug bolts
      translate([cradle_id / 2 + 5, 0, -1]) cylinder(d = 3.4, h = ring_w + 2);
  }
}

// ---- render --------------------------------------------------------------------------
// ALL parts print flat exactly as modeled — nothing needs supports.
if (part == "coupon") fit_coupon();
if (part == "pan_base") pan_base();
if (part == "yoke_bridge") yoke_bridge();
if (part == "arm_motor") arm_motor();
if (part == "arm_bearing") arm_bearing();
if (part == "head_boss_plate") head_boss_plate();
if (part == "head_main_plate") head_main_plate();
if (part == "head_end_plate") head_end_plate();
if (part == "cradle_ring") cradle_ring();
if (part == "all") {                        // one X1C plate, everything flat
  fit_coupon();
  translate([78, 0, 0]) pan_base();
  translate([0, 78, 0]) yoke_bridge();
  translate([-72, -72, 0]) arm_motor();
  translate([0, -72, 0]) arm_bearing();
  translate([64, -86, 0]) head_boss_plate();
  translate([52, 140, 0]) head_main_plate();
  translate([112, -86, 0]) head_end_plate();
  translate([-72, 16, 0]) cradle_ring();
}
