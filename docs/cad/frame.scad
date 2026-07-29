// frame.scad — Engineered Lighting gimbal frame (Doc 3b · Print the Frame)
// Motor: MyActuator RMD-L-5005 (Ø49 × ~24 mm body, 92 g).
// Payload: DLH-3UP-EH aluminum LED housing (Ø0.99" finned barrel, 1.26" long,
//   1/2"-14 NPT rear stub with a hollow wire passage) — the housing is BOTH
//   the star's heatsink and the head's sliding balance mass. A ~Ø25 mm
//   flashlight fits the same cradle as the bench stand-in.
// Geometry truth = MyActuator's L-series 2D drawing + the housing drawing +
// YOUR calipers. Every MEASURE-ME value is a placeholder nominal: measure the
// real parts on arrival, update, re-render. Print fit_coupon() before any
// real part.
//
// v2 (2026-07-29): yoke arms joined to the flange disc by a bridge bar (they
// were separate floating bodies); collar bores teardropped so the yoke still
// prints arms-up support-free; head shell rebuilt as a pinch-collar cradle —
// the payload barrel now CROSSES the tilt axis (so tilt sweeps the beam
// instead of rolling it) and an M8 bolt through the far arm's 608 bearing
// into the end plate is the head's second support (Doc 3b step 4's "stub").

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
payload_od    = 25.15; // MEASURE-ME — DLH-3UP-EH housing barrel, Ø0.99" per its drawing
payload_clear = 0.6;   // slide fit: the housing must slip in and glide to balance
cradle_w      = 12;    // cradle grip width on the housing's finned barrel
arm_offset    = 8;     // daylight between yoke arm and motor body
wall          = 4;     // structural wall thickness
bearing_od    = 22;    // 608 bearing OD (683 = 7 mm) — measure the one you bought
bearing_id    = 8;     // its bore: the M8 axle bolt rides in it (683 → M3)
bearing_w     = 7;     // bearing width
clamp_ear_w   = 30;    // C-clamp ear width
hard_stop_h   = 6;     // hard-stop post/tab height

$fn = 64;

// ---- derived ---------------------------------------------------------------
cradle_id = payload_od + payload_clear;   // ≈ 25.75 mm ≈ 1.014" — "just over 1 inch"
span      = body_d + 2 * arm_offset;      // daylight between the two yoke arms
drop      = body_d / 2 + arm_offset;      // arm root plane → tilt axis
disc_d    = flange_bolt_circle_d + 4 * wall;

// ---- helpers ---------------------------------------------------------------
module flange_bolts(h = 10) {
  for (i = [0 : flange_bolt_n - 1])
    rotate([0, 0, i * 360 / flange_bolt_n])
      translate([flange_bolt_circle_d / 2, 0, -1])
        cylinder(d = flange_bolt_d, h = h + 2);
}

// A bore with a 45° teardrop roof, running along +x. The apex points to -z =
// the sky when the yoke prints arms-up, so the printer never bridges the
// bore's ceiling. The roof is truncated just inside the collar wall, leaving
// a short flat the printer bridges easily (~2 mm on the bearing collar,
// ~15 mm on the motor collar — both trivial for the X1C).
// (Model arms hang -z; on the plate the part is flipped.)
module bore_teardrop(d, len) {
  r   = d / 2;
  cap = r + wall - 1;                       // truncate inside the collar wall
  hw  = max(r * 1.414 - cap, 0.6);          // half-width of the flat at the cap
  rotate([0, 90, 0]) linear_extrude(height = len)
    union() {
      circle(d = d);
      polygon([[r * 0.707, r * 0.707], [r * 0.707, -r * 0.707],
               [cap, -hw], [cap, hw]]);
    }
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
// One arm's collar carries the tilt motor body; the other's holds the 683/608
// bearing. Arms hang from a bridge bar (v2 fix — they were floating), and the
// collar bores are teardropped so arms-up printing needs no supports.
module yoke_arm(bore, t) {
  slab_len = drop - bore / 2 - wall + 8;   // root plane → overlap the collar by ~8
  difference() {
    translate([0, -body_d / 4, -slab_len]) cube([t, body_d / 2, slab_len + 0.01]);
    translate([t / 2, 0, -slab_len + 5]) rotate([90, 0, 0])            // zip-tie hole
      cylinder(d = 4, h = body_d, center = true);
  }
  translate([0, 0, -drop]) difference() {
    rotate([0, 90, 0]) cylinder(d = bore + 2 * wall, h = t);           // collar
    translate([-1, 0, 0]) bore_teardrop(bore, t + 2);
  }
}

module yoke() {
  difference() {
    union() {
      translate([0, 0, -wall]) difference() {                          // flange disc
        cylinder(d = disc_d, h = wall);
        flange_bolts(wall);
      }
      translate([-(span / 2 + wall + body_len / 2), -body_d / 4, -wall]) // v2: bridge bar
        cube([span + 2 * wall + body_len / 2 + bearing_w, body_d / 2, wall]);
      translate([-hard_stop_h / 2, flange_bolt_circle_d / 2 + wall, -2 * wall])
        cube([hard_stop_h, wall, wall]);                               // tilt hard stop
    }
    translate([0, 0, -wall - 1]) cylinder(d = flange_center_bore_d, h = wall + 2);
  }
  translate([span / 2, 0, -wall]) yoke_arm(bearing_od, wall + bearing_w);   // bearing arm
  translate([-span / 2 - wall - body_len / 2, 0, -wall])
    yoke_arm(body_d + 0.6, wall + body_len / 2);                           // motor arm
}

// ---- 4 · head shell: pinch-collar cradle on the tilt flange ----------------
// The housing slides through the cradle so its barrel CROSSES the tilt axis
// (beam ⊥ axis — tilt sweeps elevation), then the M3 pinch bolt locks the
// balance position. The end plate's Ø8.2 hole takes an M8×30 bolt pushed
// through the 608 from outside — that bolt IS the "head-side stub", and it
// makes assembly trivial: bolt the flange first, slide the M8 in last.
// The counterweight tail (M5 bolt + stacked nuts) stays for fine trim —
// balance is the silence mechanism.
module head_shell() {
  ring_od = cradle_id + 2 * wall;
  ring_c  = wall + ring_od / 2;            // barrel axis crosses the flange axis here
  difference() {
    union() {
      cylinder(d = disc_d, h = wall);                                  // flange disc
      translate([0, 0, wall - 0.01]) cylinder(d = disc_d, h = 4);      // gusset
      translate([0, 0, ring_c]) rotate([-90, 0, 0])                    // cradle ring
        cylinder(d = ring_od, h = cradle_w, center = true);
      translate([ring_od / 2 - wall, -cradle_w / 2, ring_c - 5])       // pinch ears
        cube([wall + 6, cradle_w, 10]);
      translate([-2, -cradle_w / 2, ring_c])                           // spine
        cube([4, cradle_w, ring_od / 2 + 4]);
      translate([0, 0, ring_c + ring_od / 2])                          // end plate
        cylinder(d = flange_bolt_circle_d, h = wall);
      translate([-2, -62, ring_c + 14]) cube([4, 58, 18]);             // counterweight tail
    }
    translate([0, 0, -1]) cylinder(d = flange_center_bore_d, h = wall + 6);
    flange_bolts(wall + 4);
    translate([0, 0, ring_c]) rotate([-90, 0, 0])                      // payload bore
      cylinder(d = cradle_id, h = cradle_w + 20, center = true);
    translate([cradle_id / 2 - 1, -(cradle_w + 2) / 2, ring_c - 1])    // pinch slit
      cube([wall + 10, cradle_w + 2, 2]);
    translate([ring_od / 2 + 3, 0, ring_c - 8])                        // M3 pinch bolt
      cylinder(d = 3.2, h = 16);
    translate([0, 0, ring_c + ring_od / 2 - 1])                        // M8 axle hole
      cylinder(d = 8.2, h = wall + 2);
    translate([-3, -56, ring_c + 20.35]) cube([6, 38, 5.3]);           // M5 slot
  }
}

// ---- render ----------------------------------------------------------------
// Print orientations (Doc 3b's table): coupon + pan base flat; yoke arms-up
// (teardrops make it support-free); head shell CRADLE FLAT on the plate
// (payload bore vertical) — the flange disc, spine, end plate and tail all
// print as vertical walls, and there is no stub to print (it's the M8 bolt).
if (part == "coupon") fit_coupon();
if (part == "pan_base") pan_base();
if (part == "yoke") yoke();
if (part == "head_shell") head_shell();
if (part == "all") {
  fit_coupon();
  translate([90, 0, 0]) pan_base();
  translate([0, 130, 0]) yoke();
  translate([115, 130, 0]) head_shell();
}
