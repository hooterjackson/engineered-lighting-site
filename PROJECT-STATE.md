# PROJECT-STATE — Engineered Lighting · Robotic Spotlight

*Session-handoff file. Any Claude (Cowork, Claude Code, claude.ai) on any machine:
read this file first — it replaces the chat history that produced this repo.
Update it at the end of every working session.*

**Last updated:** 2026-07-29 (Cowork cloud session — reconciled against git history)

## What this project is

The robotic spotlight for the Engineered Lighting fixture: a silent pan/tilt head
(smart CAN servo actuators, absolute encoders) carrying a high-CRI 3-up LED spot,
exposed to Home Assistant as ordinary entities AND autonomously aimed by a
camera-driven perception stack. Full context lives in the 8-doc series in `docs/`,
published at **https://engineering.engineered.lighting/** (this repo, MkDocs
Material, deployed via GitHub Actions).

## Current state (snapshot)

- **Site:** live — 7 chapters + Doc 3b (frame) + Doc 8 (fixture build, added
  2026-07-29) + BoM checklist + AI-workflow page. Adversarial review rounds
  applied throughout, including a sitewide coherence pass after Doc 8 landed
  (seam fixes: Doc 8 body-interface note, Doc 3 + Doc 4 graduation
  pointers → Doc 8, Home card spans Docs 1–4 · 8, totals made derivable
  at $745–1085). Design pass (DESIGN.md) done.
- **Motor swap: DONE sitewide.** Earlier revisions of this file listed two
  prompts as pending; git history shows both were executed before it was
  committed. `8fb39bf` (2026-07-21) propagated RMD-L-4005 → **RMD-L-5005**
  through everything forward-looking (Doc 3 BoM $350–405, end-to-end total
  $640–985, Doc 2's availability addendum keeps the 4005 decision record,
  wiring-SVG labels edited, checklist localStorage IDs preserved). `db41f3f`
  (2026-07-22) added Doc 3b + `docs/cad/frame.scad` (parametric scaffold +
  fit coupon). The prompt files remain in `prompts/` as executed history.
- **Nothing purchased yet.** The Dings order (3× RMD-L-5005-100-C, $107.50 ea,
  2 build + 1 spare/bench unit) is NOT yet placed. Doc 4 (LED bench) and
  Doc 5 (camera) BoMs unordered. Valent X sourcing is resolved on the site —
  click-to-buy at BuyRite/LBC ($486 spool), BTF FCOB listed as the budget
  bench substitute.
- **Hardware owned:** RTX 6000 Blackwell GPU box, Home Assistant install,
  Bambu Lab X1C printer (PETG/PETG-CF on hand assumed).

## Pending work queue (in order)

1. **Place the Dings Motion USA order** — 3× RMD-L-5005-100-C (explicitly the
   -C CAN variant; ask for mating cables, one per motor + a spare; keep the
   protocol PDF that ships in the box — it's the authority on byte layouts).
2. When the order ships: update Home's "current phase" line (hero meta +
   footer in `docs/index.md`).
3. On motor arrival: Doc 3 stages 1–6 (bench bring-up); then calipers → fill
   frame.scad's MEASURE-ME parameters → Doc 3b's coupon-first build order.
4. **Later, post-bench — fixture integration v0 (hand-soldered):** port the
   Doc 4 architecture off the breadboards onto 2–3 stacked round protoboards
   ("vegetable can" round prototyping PCB, Etsy) inside a fixture body, fed
   from an E26 socket-to-wire adapter → internal 24 V PSU (decision in the
   ledger below; re-verify against the measured worst-case current from
   Doc 3 stage 10 / Doc 4 stage 7 before buying). Build notes banked now:
   reinforce the 24 V and ground rails with solid bus wire (protoboard
   traces don't carry motor current — motor power stays point-to-point in
   18–20 AWG), keep the star-ground topology, PSU on the bottom board away
   from logic, standoffs + a vent path between boards. Component deltas vs
   bench (2026-07-29): same parts, different construction — socket every
   module on female headers (C6 devkit, PCA9685s, SN65HVD230, buck; ULNs
   already socketed), WAGOs → soldered bus + pluggable pigtails (JST-XH
   per tape zone + spot; XT30 for motor power — XH is a 3 A part, RMD
   peaks hit 5–8 A), add 100 nF decoupling at
   each module's supply pins + the bulk cap from the PSU note. ULNs stay
   for v0 (first upgrade candidate if the enclosed soak runs them hot —
   MOSFETs belong to the real PCB per Doc 4). Star heatsink was specced
   for open bench — the enclosed head needs a path to outside air or a
   verified soak. Don't solder until Doc 4 stage 7 passes (freeze the
   validated architecture); first power-up of the stack still happens on
   the current-limited bench supply before the IRM goes in. Wiring docs
   drafted 2026-07-29 (chat deliverables → docs/ + docs/assets/): a
   lane-based system map (wiring-fv0-map.svg), six step diagrams
   (wiring-fv0-step1..6: power → brain → zone 1 → scale → spot → gimbal,
   each with done-when + traps), and chapter 08-build-the-fixture.md —
   all now IN THE REPO (docs/ + docs/assets/): Home + Doc 1 doc-maps
   gained row 8, the series became
   "eight-document", totals propagated $640–985 → $745–1085 sitewide,
   bom-checklist notes Doc 8's BoM lives in-chapter for now, and
   `mkdocs build --strict` verified. Review catches baked in: XT30
   for motor power, 3× 10 kΩ PicoBuck IN pulldowns vs full-on boot
   flash, bulk cap on the motor branch (start 1000 µF), bench-feed break
   in the bus, both-AC-leads-live rule, PCAs live WITH the ULNs on B2.
   The fixture BODY is Marcelo's own design track (his call, 2026-07-29)
   — the docs treat it as a parallel project, not a gap: Doc 8's scope
   note hands that track its interface list (IRM-90-24ST mount +
   terminal-cover room away from LED heat, strain-relieved E26 cord
   entry, 3× M3 standoffs + vent path for the 72 mm stack, tape ring at
   B2 height, full pan/tilt clearance + service-loop slack,
   heatsink→outside-air path, reachable B3 USB-C window). Doc 8's BoM
   folded into the interactive checklist 2026-07-29 (12 new d8-* ids —
   saved state untouched — 31→43 items, e2e count assertions updated;
   bearing drift fixed while in there: 683 or 608 per frame.scad +
   Doc 3b, where Doc 3's BoM had said 6804). Sitewide coherence review done
   2026-07-29; totals recomputed as the straight sum of per-doc highs —
   350–405 + 170–240 + 120–320 + 105–120 = **$745–1085** — and
   propagated (Home hero + footer, Doc 1 reading paths).

## Decisions ledger (one line each — full reasoning is in the docs)

- Actuators: integrated smart CAN servos over DIY FOC (Doc 2). 4005→5005 swap
  is availability-driven; geometry logic: 5005 keeps the slim pancake profile
  (siblings 4010/4015 grow in length, the dimension the yoke cares about).
- Alternates if family sells out again: CubeMars GL40 II (direct-drive, CAN,
  DigiKey) = buy-today fallback w/ protocol port; M5Stack RollerCAN ($44) = dev
  bridge. Full sweep was done July 2026 — Damiao/Robstride/CyberGear ruled out
  (geared/oversized/EOL).
- Beam: fixed Carclo 10507 (~16°); brightness abundant at 330 mA; no zoom
  hardware (beam naturally widens with throw — see Doc 5).
- Control: brightness through HA light entity only; aiming via MQTT
  `spotlight/target` (bench) → ESPHome native-API action (production);
  Auto/Hold/Manual select gates autonomy. Doc 6 is the arbiter when docs
  disagree.
- Software: stack + repo layout + hardware-free testing per Doc 7 (ESPHome
  host-platform simulated fixture is the CI trick). Licensing gates flagged for
  product phase: ESPHome GPLv3, Ultralytics AGPL.
- Fixture-v0 power (2026-07-29, sized smallest-possible-in-fixture): loads
  split steady vs transient — steady worst case ~25 W as designed (~40 W
  with 2× tape); dual-axis slews add ~30–40 W briefly; balanced hold ≈ 0 W.
  Smallest class: Mean Well **IRM** encapsulated PCB-mount bricks
  (87 × 52 × 29.5 mm, potted, fanless — solders onto the bottom
  protoboard). **IRM-60-24** (2.5 A) is the floor for the as-designed
  build (worst transient ~55–65 W vs its ~69 W hiccup floor — thin but
  real; add 1000–2200 µF low-ESR bulk on the 24 V rail near the motors).
  IRM-45 rejected: dual slews cross its 115% hiccup floor → rail drops
  mid-move. **IRM-90-24** (3.75 A, ~$23) has the IDENTICAL footprint and
  covers 2× tape with margin — same volume, no-regret pick. Fit check
  (2026-07-29): the chosen protoboards are 2.84"/72 mm rounds (Etsy
  "vegetable can" 4-pack, $15, 593 plated holes, no power rails) — the
  87×52 mm IRM outspans them, so use the **IRM-90-24ST** (screw-terminal,
  109×52×33.5 mm) mounted to the fixture body below the stack; that also
  keeps the heaviest part off solder pins near a vibrating gimbal. Plan on
  ~3 of the 4 rounds (power / drivers / logic — connectors eat area fast).
  Fixture-v0 BoM drafted 2026-07-29 (chat deliverable; fold into the
  future Doc 8). Keep the BoM's
  3 A slow-blow on the 24 V side; isolate + strain-relieve the
  line-voltage corner of the stack; no TRIAC/wall dimmer on the E26
  circuit (socket's 660 W rating is a non-issue at ≤100 W input);
  wall-switch power cuts already survivable (absolute encoders, no
  homing). Scaling: +4.6 W (+0.19 A @ 24 V) per foot of Valent X. Confirm
  against the stage-10 measured worst-case current before buying.
  Beginner-review deltas (2026-07-29, round 2): board allocation REVISED —
  B1 power / B2 drivers (PCAs move in WITH the ULNs + zone plugs) /
  B3 logic (C6 + SN65, bottom of stack: USB + antenna + CAN exit) — so
  only ~a dozen wires cross boards instead of all 21 dim signals; stack
  order PSU→B1→B2→B3→gimbal; build flat, stack last, inter-board slack
  1.5×. Chapter gained: Concepts block, five protoboard-soldering rules
  (incl. never-crimp JST + XT30 recessed-live convention), per-step time
  estimates, if-stuck ladders (ULN socket swap-test), a step-7 soak agent
  prompt, and the map gained a physical side-view panel. Wire strippers +
  flush cutters added to BoM maybes.
  Adversarial-review deltas (2026-07-29): 2× tape → DC fuse steps to 4 A
  SB (~3.1 A sustained nuisance-blows a 3 A); bulk cap starts at 1000 µF
  (IRM publishes no max capacitive load — downsize if power-on hiccups);
  spot wiring is 3 independent ± pairs (6 conductors, returns never
  shared); bench-supply limit → ~3 A for full-stack tests; IRM-ST block
  is L/N/+Vo/−Vo only (no FG — Class II, verified against the datasheet);
  Board 1 is over its 72 mm area budget → split power round + a
  driver/connector deck on the third round (wiring identical).

## How to resume on any machine

1. `git clone https://github.com/hooterjackson/engineered-lighting-site.git`
2. Open the folder in Claude Code (or point a Cowork session at it).
3. First message: *"Read PROJECT-STATE.md and the docs it references; summarize
   state and the pending queue; then let's continue."*
4. Note: Cowork **local** sessions stay on the machine they ran on — this file
   is the continuity mechanism, not chat history. Keep it updated.
