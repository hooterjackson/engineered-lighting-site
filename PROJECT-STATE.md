# PROJECT-STATE — Engineered Lighting · Robotic Spotlight

*Session-handoff file: the narrative of how this repo got here, and the site's own
build state. It replaces the chat history that produced this repo. Any Claude
(Cowork, Claude Code, claude.ai) on any machine can read it for context; update it
at the end of every working session.*

> ### What to work on next is not in this file — it is in `product-os`
>
> | Question | Authoritative source |
> |---|---|
> | What should I do next, and why? Is it blocked or gated? | **product-os** |
> | Is it actually *done*? (a SHA, a path, a dated note) | **product-os** |
> | How did this project get here, and what does the site say? | **this file** + `docs/` |
>
> Start a session from
> `https://raw.githubusercontent.com/hooterjackson/product-os/main/public/llms.txt`
> — fetchable from any tool, no clone needed. With a clone: `~/Claude/product-os`,
> then `python3 tools/rank.py`.
>
> **Cite the item ID in your first message** (`EL-004`, `SITE-002`). That one token
> is what links the conversation to the work; nothing else recovers it.
>
> This is a pointer, **not a merge** — do not sync the two by hand. When they
> disagree about *status or priority*, product-os wins. When either disagrees with
> a ruling or current bench evidence in `gimbal-bench`, the ruling wins and the
> stale side gets an item.

**Last updated:** 2026-09-07 (Doc 10: the FLEX v0.2 circuits, the pull_request CI trigger, the pinnable board tooltip) — *the last edit to **this file**, not to the repo.
`git log -1` is the repo's real state; this file lags it by design.*

## What this project is

The robotic spotlight for the Engineered Lighting fixture: a silent pan/tilt head
(smart CAN servo actuators, absolute encoders) carrying a high-CRI 3-up LED spot,
exposed to Home Assistant as ordinary entities AND autonomously aimed by a
camera-driven perception stack. Full context lives in the 10-doc series in `docs/`,
published at **https://engineering.engineered.lighting/** (this repo, MkDocs
Material, deployed via GitHub Actions).

## Current state (snapshot)

- **Site:** live — 7 chapters + Doc 3b (frame) + Doc 8 (fixture build, added
  2026-07-29) + **Doc 9 (PCB learning page, 2026-09-07 — implemented and
  validated locally on branch `doc9-understand-the-pcb`; NOT pushed, NOT
  published)** + BoM checklist + AI-workflow page. Adversarial review rounds
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
- **Motors purchased; bench is live.** Doc 3 **stage 4 passed 2026-07-31**:
  motor answering on CAN at 0x141, 0xA4 moves commanded and landed to 0.01
  degrees, and the no-homing power-cycle trick verified (the encoder reported
  80.21 deg after a power-off hand rotation). Getting there cost three
  diagnosed failures, all now written into the site: stranded wire fails in
  breadboard clips two ways (splay bare, cold-flow tinned); 12.0 V is this
  24 V-nominal motor's undervoltage-latch line, not a gentle bring-up; and
  when that latches, this unit takes its CAN interface down until a power
  cycle. Doc 4 (LED bench) and Doc 5 (camera) BoMs unordered. Valent X
  sourcing is resolved on the site - click-to-buy at BuyRite/LBC ($486
  spool), BTF FCOB listed as the budget bench substitute.
- **Hardware owned:** RTX 6000 Blackwell GPU box, Home Assistant install,
  Bambu Lab X1C printer (PETG/PETG-CF on hand assumed).

## Pending work queue (in order)

1. **Bench session, in this order** (the order is the safety property):
   flash **v2** and burn down its drill list first (SAFE replays, health
   injection drill) so a regression has one suspect; then flash **v3**;
   then `commission_verify.py` both motors; then **`commission_watchdog.py`
   BEFORE any velocity drill** - 0xB3 is the only protection that survives
   the ESP32 crashing mid-move. Then jog/vel/stop drills, one move through
   the bench-UI path (the first motion came from the USB-CAN adapter), and
   the remaining rituals: multiturn, zero, limits.
2. **Stage 5 characterization** - `tools/sweep_runner.py --live` walks the
   hold/sweep/resolution protocol with dB-meter cues.
3. **Stage 6** - motor B ALONE on the bus, re-addressed to 0x142 via
   `tools/readdress.py` (0x79 is a one-shot persistent flash write).
4. **Frame** - being designed BY HAND on this bench. Doc 3b's generated
   OpenSCAD scaffold stays published as worked reference (constraints,
   STEP-measured motor geometry, boolean test suite), not as a parts list;
   the chapter now says so at the top.
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
- Spotlight payload (2026-07-29, Marcelo's call): the Cree 3-up star mounts
  in a **DLH-3UP-EH** aluminum LED housing (Ø0.99" finned barrel, 1.26"
  long, hollow 1/2"-14 NPT rear stub = wire exit) — the housing is the
  star's heatsink AND the head's sliding balance mass. frame.scad is at
  **v3** (`b11accb`, 2026-07-29, redesigned after Marcelo's fit review of
  v2): nine flat-printed plates, zero supports, one repeated T-joint
  (printed tabs into slots + M3 bolts into side-loaded square nuts);
  motors BOLTED, never friction-fit (pan = back-cover bolt pattern under
  the base; tilt = face-mount pattern + boss-clearance window, body
  OUTSIDE the arm — the RMD's 4-pin side connector makes any collar
  impossible); 608 sits in a boss-padded full-depth pocket, M8 axle runs
  through it into a captive end-plate nut and installs LAST, so the head
  is supported on both sides and the assembly order is built into the
  geometry; head = boss/main/end plates + face-bolted **cradle_ring**
  (ID = payload_od + 0.6 ≈ 25.75 mm, pinch bolt locks the slide, ring +
  plate grip the barrel near its center); two orthogonal balance trims
  (slide the housing, then the M5 nuts in the tail slot).
  docs/cad/assembly.scad `use`s the real part modules (exploded ↔
  assembled views); Doc 3b rewritten to match ("Nine Flat Parts, One
  Coupon" — the coupon now proves BOTH motor bolt patterns). The planned
  Doc 3b assembly figure was dropped: binary/base64 can't ride the
  text-only GitHub connector (asset corrupted in transit, deleted in
  `ac67684`) — the doc points readers at assembly.scad instead. The
  motor-interface numbers (mount/back BCD 43, bolt Ø2.8, boss clear 34,
  boss len 8) are MEASURE-ME nominals awaiting the calipers step. BoM
  ripple NOT yet applied (Marcelo to call): where the housing purchase
  lands — it supersedes Doc 4's flat heatsink at the fixture stage.
  Doc 3b's BoM delta now carries the small-hardware handful (~$8: M3×10
  + square nuts, M8×35 + nut, M2.5 motor screws).
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
   — or, on an existing clone, **`git fetch` first**. A local tracking ref that
   has not been fetched will answer "up to date" while the remote is dozens of
   commits ahead; it has already lied here by 54.
2. Open the folder in Claude Code (or point a Cowork session at it).
3. Get the queue from product-os, not from this file — fetch
   `.../product-os/main/public/llms.txt` (link at the top) or run
   `python3 tools/rank.py` in `~/Claude/product-os`. Then, first message:
   *"Working on `<ITEM-ID>`. Read PROJECT-STATE.md and the docs it references,
   summarize the state that item depends on, and let's continue."*
4. Note: Cowork **local** sessions stay on the machine they ran on — this file
   carries the narrative and product-os carries the queue and the evidence.
   Neither is chat history. Keep both updated.

### 2026-07-31 — first motor motion; frame authorship; two corrections

**Stage 4 passed.** One RMD-L-5005 on the bench, answering 0x92 and executing
0xA4 to 0.01 deg, power-cycle trick verified. Three failures diagnosed on the
way, all now in the site: stranded motor CAN wires must land in screw
terminals (they fail bare AND tinned in breadboard clips); the motor rail runs
at **24 V** because 12.0 V is this unit's undervoltage-latch line; and a
latched fault takes its CAN interface down until power cycle (power cycle is
the verified recovery, 0x76 untested). LED codes are the fastest instrument:
solid = normal, slow flash = latched Level-2 error.

**Frame: designed by hand from here.** The generated OpenSCAD in Doc 3b stays
published as *worked reference* - the STEP-measured motor geometry, the
2.5 mm tapped depth, the cantilever load argument, the boolean test suite -
but the frame going on this bench is being drawn by hand with that as
inspiration. Doc 3b and Doc 3 stage 7 both say so now.

**Correction to the 2026-07-29 entry above:** it describes the RMD's port as a
"4-pin side connector". It is a **6-pin JST ZH** (VCC, VCC, GND, GND, CANH,
CANL - power doubled up), documented in Doc 3a. The collar-impossible
conclusion still holds; only the pin count was wrong.

**Correction to the frame ledger:** entries describing frame.scad at v3 (nine
flat plates, 608 bearing in a boss-padded pocket) were true as written; the
design has since moved to v8 - four parts, no bearing, no counterweight, the
tilt axis cantilevered off the motor output. See Doc 3b.

### 2026-07-31 (later) — the bench tool becomes a commissioning console

**Direction.** The gimbal debugger is being grown into the tool that sets up
the ESP32 for the whole project: gimbal first, then the LED engine, then
pairing to Home Assistant, then firmware updates. Built after a documentation
sweep (protocol V4.2 read end to end, both vendor manuals, Docs 4/6/7/8, the
Cree and Valent X datasheets) and an adversarial review that changed the
design rather than decorating it - the velocity command was redesigned, a
torque command was cut outright, and several ordering hazards were caught.

**Four decisions, recorded in the Doc 6 addendum where they belong:**

1. The spot star (warm XP-E2 + cool XP-E2 + PC Amber) sits behind ONE
   `light.spot1`, amber folded into the warm end of the CCT dial. No amber
   entity - that would be a second photometric write path.
2. The console is a sanctioned native-API client, but never a second aim
   writer.
3. Motor comm-loss watchdog 0xB3 = 3000 ms, coupled forever to >=1 Hz status
   polling while armed. Change them together or not at all.
4. Persistent motor writes stay in ritualized one-shot tools. Never firmware,
   never a UI button.

**Commissioning values sheet** (what the bench writes into the motors):
CAN ids pan 0x141 / tilt 0x142 · 0xB3 = 3000 ms · multi-turn save ON ·
travel limits mirroring +/-170 and +/-90 (UNIT UNDOCUMENTED - the tool
discovers it by probing) · accel planners in 100..60000 dps/s, and 0 on index
0 means direct tracking, not "no limit" · PID indexes are the non-contiguous
set {01,02,04,05,07,08,09} and float-format writes need motor firmware
>= 20240528.

**Known-unknowns kept as bench experiments:** 0xB6 active-reply semantics ·
whether 0x20-03 fault push persists · whether the motor-side angle limit
gates relative moves at all · what a relative move does to an axis already
running a speed loop (firmware refuses that combination until someone runs it
on purpose).

**Motor firmware updates: there is no field path.** Both manuals were checked.
Recovery and deep configuration go through the vendor's Windows setup software
over the motor's 4-pin serial port, so a USB-TTL adapter belongs in the bench
kit. This is also why `commission_verify.py` exists: a drive that loses its
CAN interface gets recovered by a factory restore that wipes its identity and
tuning, and the JSON snapshot is what makes that survivable.

**Naming:** the artifacts keep their names - the repo is still `gimbal-bench`,
the tool still lives in `tools/bench_ui`. "Commissioning console" is what it
is becoming, not a rename.

### 2026-09-07 — Doc 9: the LIGHT v0.1 PCB, viewable and downloadable

**What landed.** A final chapter, `docs/09-understand-the-pcb.md`, built around an
interactive viewer of the real board: `docs/js/pcb-viewer.js` (board viewer, part
finder, detail panel, parts-list cross-selection, 19-sheet schematic browser, hash
routing, a read-only `window.elPcb` debug API) and `docs/stylesheets/pcb.css`
(section 17, scoped to `.el-pcb` / `.el-sch`). Both registered in `mkdocs.yml`;
that plus two lines in `docs/.pages` are the only config changes.

**The governing hardware** is `engineered-lighting-rev-a.kicad_pcb`, SHA-256
`c046202efa3896d59d12bf19f55ed48b3a6c77532aac199a3a1e9a993e449310`. The page is
generated from the handoff folder prepared on 2026-09-06 and never modifies it.

**Generator.** `tools/pcb/` (standard library only) has three modes: `build
--handoff <folder>` verifies the hash chain and derives every published asset;
`render` regenerates the page's static blocks from the published JSON; `check`
re-verifies hashes, counts, the manifest and the generated blocks **without** the
handoff, so CI and the data tests can run it. Regenerate with:

```
python tools/pcb/build_pcb_assets.py build --handoff "<handoff folder>"
python tools/pcb/build_pcb_assets.py check
```

**Published assets** live under `docs/assets/pcb/light-v0.1/` — about 27 MB: 17
layer plots, 19 schematic sheets, the loose KiCad sources, the complete project
ZIP, the parts CSV, two PDFs, two assembly drawings, the fabrication reference,
and four derived JSON files. Largest single file is the 5.6 MB `.kicad_pcb`; the
previous repo maximum was a 634 kB photograph.

**`docs/assets/pcb/.gitattributes` is load-bearing.** `core.autocrlf=true` plus
CRLF source files would rewrite line endings on commit and break every SHA-256 in
the provenance chain on a Linux CI checkout. `* -text` prevents that; verified
with `git ls-files --eol` and by re-hashing the staged blobs.

**Manufacturing scope stated on the page** (as of 7 September 2026): PCBWay has
been asked to quote five fabricated boards, two of them fully assembled with all
248 purchased parts and three supplied bare. Nothing paid or authorised; assembly
process, stencil and via treatment and factory substitutions not approved. Hand
soldering appears only as optional rework. Older "bare boards for local hand
assembly" wording in the handoff and in the CSV comments is explicitly superseded.

**What the page does not claim.** No board has been powered; no firmware has been
built or flashed. Every component claim carries an evidence class — intended,
cad-checked, modelled-current, or simulated-historical bound to the older board
hash it actually came from. `measured` is never used, and a data test fails the
build if it appears.

**Checks run.** `mkdocs build --strict` twice, clean; the CI add-a-doc rehearsal;
`pytest tests/e2e -q` → **47 passed** (10 pre-existing, 14 new data checks, 23 new
browser checks). Screenshots in `test-artifacts/screens/pcb-*.png`. Layout verified
at 390, 1280 and 1800 px with no page-level horizontal scroll.

**Two fixes worth remembering.** `tests/e2e/conftest.py` now spawns
`sys.executable` rather than a literal `python3`, so the interpreter running the
tests is the one serving the site. And Material's `.md-typeset ul:not([hidden])`
rule outranks a plain class selector, so any list the viewer hides needs either
higher specificity or the `[hidden]` guard now at the top of `pcb.css`.

**Two-interpreter workflow on this machine.** The global Python 3.12 has MkDocs
but a broken pytest; the repo `.venv` has pytest and Playwright but no MkDocs.
Build with the global interpreter, test with `.venv/Scripts/python.exe -m pytest`.

**Open, and needing the owner's call before publication:**

1. The loose `.kicad_pcb` and 19 `.kicad_sch` files are published *in addition to*
   the project ZIP, as the brief asks — about 7 MB of duplication.
2. The fabrication-reference ZIP (Gerbers, drills, IPC-D-356) is derived from the
   same source and scanned clean of quote details, but has not been owner-reviewed.
3. Repository growth of roughly 27 MB.
4. Doc 9 hides its table of contents so the board and its detail panel fit side by
   side at 1280 px, as `bom-checklist.md` already does.

**Deployment.** Approved and performed the same day: branch pushed, pull request
1 merged with a merge commit (`77cdafa`), CI green, and the chapter is live at
https://engineering.engineered.lighting/09-understand-the-pcb/. The hash chain was
re-verified against files fetched back from the published site.

### 2026-09-07 (later) — Doc 10: the FLEX v0.2 circuits, a branch gate, and a board tooltip that stays put

Three separate pieces of work, in the order they were asked for.

**A `pull_request` trigger on the publish workflow.** The pull request for Doc 9
showed no checks at all, because `.github/workflows/publish.yml` only ran on pushes
to `main`. It now also runs on `pull_request` against `main`, so a branch is
validated *before* it lands rather than after. The `deploy` job carries
`if: github.event_name != 'pull_request'`, so a pull request can build and test but
can never publish, and `concurrency` is keyed by `github.ref` so a branch's run does
not cancel `main`'s. The social-card step still fails on CI for want of `cffi`; that
is pre-existing on `main` and unrelated.

**Doc 10 — `docs/10-the-flex-circuits.md`.** Three passive flexible circuits, from
their own KiCad sources, each governed by its own hash:

| Circuit | Design | Copper | Pads | `.kicad_pcb` SHA-256 (first 8) |
|---|---|---|---|---|
| Arm ribbon | `gimbal-static-v0.2` | 1 layer | 70 | `7136c5c3` |
| Upper cylinder band | `led-upper-v0.2` | 2 layers | 120 | `a5acd2a0` |
| Lower cylinder band | `led-lower-v0.2` | 2 layers | 96 | `21db9dba` |

`tools/pcb/flex.py` (invoked as `build_pcb_assets.py --flex`) verifies each hash,
renders 16 layer plots, extracts all 286 pads from the connection tables, publishes
the native sources and builds deterministic fabrication ZIPs. 53 files, 2.5 MB.

The one genuinely hard part was registration. KiCad plots these layers in a CAM
frame, not in board millimetres, so the pad coordinates from the connection table
would have landed somewhere plausible but wrong on top of them. `_frame()` parses
the `translate(A B) scale(1 -1) translate(C D)` wrapper KiCad emits and derives
`displayed_y = native_y − (D − B)`; `svgprep.prepare()` grew `wrap_transform` and
`view_box` parameters to apply it. `test_pads_are_drawn_on_the_copper` checks the
result the only way that means anything: it measures the rendered `F_Cu` bounding
box in the browser and asserts every one of the 286 markers falls inside it, on all
three boards.

One asset needed renaming. The review folder's `ENGINEERING-NOTES.md` is
Markdown, and anything ending `.md` under `docs/` is a chapter as far as MkDocs is
concerned — it was rendered as a page and awesome-pages appended it to the nav
*after* Doc 10. It is published as `ENGINEERING-NOTES.txt` instead; the bytes and
therefore the hash `34a74c6a3252` are unchanged. `test_no_asset_is_paged_by_mkdocs`
guards the whole `docs/assets` tree against a repeat.

`docs/js/flex-viewer.js` reuses the Doc 9 viewer through `window.elPcbKit`, a small
export of `PanZoom` and the DOM helpers. Two things it needed that Doc 9 did not:
these circuits are up to sixteen times longer than they are wide, so fitting the
whole length draws an unreadable hairline — the default view fills the frame with
the circuit's *height* and the reader pans along it, with a "Whole circuit" button
for the overview. And the layer cache originally stored `true` rather than the
markup, so returning to a board you had already visited rendered nothing; it now
caches `innerHTML`.

The page states its numbers honestly: the 0.346 mm worst-case alignment hold against
a 0.30 mm requirement is a computed margin, not a passed physical test, and nothing
has been submitted, ordered or paid for.

**A tooltip you can inspect without being moved.** Clicking a component on the Doc 9
board used to jump the page straight to that part's parts-list row, which on a phone
meant you could never look at a part without losing the board. Hover and click now
both open the same summary; clicking *pins* it, with a close button, and the jump to
the parts list is a button inside the summary. Hovering elsewhere no longer disturbs
a pinned summary, `markBOM` no longer scrolls, and `jumpToRow` does the scrolling and
announces it. Four tests cover the new behaviour, including a touch-only path that
asserts the page does not scroll on tap.

**Sitewide.** `docs/.pages`, `mkdocs.yml`, both document maps, the "ten-document"
phrasing, the `10 documents` hero chip, both reading paths, Doc 9's related reading
and Doc 8's forward-looking section. Doc 10 hides its table of contents for the same
reason Doc 9 does.

**Checks.** `mkdocs build --strict` twice with no warnings; `pytest tests/e2e -q`
green including 12 new flex tests; the asset scanner clean over both asset roots.


### 2026-09-08 - Docs 9/10 refreshed from the central LED revision

**Ground truth before site edits.** The accepted hardware cut, not the autorouting
experiments, supplied main LIGHT v0.2 and upper flex v0.3. All 773 entries in the
hardware FINAL-DIGITAL-ACCEPTANCE manifest rehashed without a mismatch. Accepted
manufacturing packages already existed; the missing piece was the site's handoff
and flex-review contract, not an absence of final board files.

| Board | Published native SHA-256 | Change |
|---|---|---|
| Main LIGHT v0.2 | `9c42ff8df4a3ef58ac7f16b248242f106f784dc73b5744aa6eeb2591ec120096` | New central J2 interface and reviewed routing/assembly corrections |
| Upper flex v0.3 | `0af25f8f72fb999db1bad16a8d59541a02c4eb95f838ada6dd6abadba8fe058d` | Full insertion tail with 30 back-side contacts |
| Lower flex v0.2 | `21db9dba94c6b4fd992e7c361f79d360b84270ea8c3a89099156e5972f7d6379` | Unchanged |
| Static gimbal v0.2 | `7136c5c343da3194c0ada81330edd99336b3078152bb8f1ce47f5da158f2287d` | Unchanged |

**Snapshot contracts.** The hardware repository now has
`handoff/claude-pcb-learning-2026-09-08` (196 manifest entries) and
`deliverables/FLEX-mixed-2026-09-08-review` (192 entries). Adapted versions of the
original viewer exporter, handoff packager and flex checker preserve their folder
shapes. The site verifies every manifest entry before derivation. It remains
read-only against both snapshots. Stable asset URL roots retain their old names;
revision fields and download filenames identify the actual new boards.

**What the chapters teach now.** J2 replaces six radial sockets with one Molex
30-contact interface. Zone order is 4,5,6,1,2,3, each +,+,W,N,C: twenty-four distinct
rails, with no joining of the six fused positives. The upper tail itself is the
plug, gold on the back and support on the front, with a 0.30 +/-0.05 mm total
insertion stack. Its full 42.9 mm outline remains. The main has 264 features,
243 fitted packages, 73 BOM rows and 20 schematic sheets. Four M3 holes, USB,
remaining ports and the branding are retained. Prose covers the In2 signal
exceptions, inherited In3 slot/PWM03 return-reference risk, U5 Schmitt replacement,
910-ohm CTRL pull-downs and C504's final factory installation.

**Evidence boundaries.** Current native/parity/physical-connectivity/CAM receipts
are hash-bound to the accepted revision; the site refresh does not claim to have
rerun those main engineering analyses. The upper snapshot's native ERC/DRC, parity,
endpoint oracle and standalone CAM checks were rerun: 126 pads, 222 copper flashes,
252 tracks and 192 drills. Installed strip connectivity remains conditional on
real strip through-rails. Historical per-part calculations link to the byte-exact
archived teaching record containing their original revision hashes. The current
tail/contact resistance screen is downloadable and deliberately excludes a
full-loop thermal qualification. The 0.346 mm alignment risk against 0.30 mm
remains. The old A3 PDF is explicitly historical because its upper tail is obsolete;
the current upper 1:1 SVG and insertion drawing are supplied instead.

**Publication.** Native sources, 20-sheet schematic/PDF, current placement CSV,
BOM, fabrication reference, complete upper native project and custom footprints
are linked. No generated marker content was hand-edited. No chapter was added or
removed, so sidebar/maps/counts/reading paths require no structural changes.
The lower and gimbal asset directories are byte-identical to main's prior commit.
The quotation status distinguishes submitted requests from payment or production
release; neither these PCBs nor their flex circuits have been made or powered.

**Viewer and maintenance.** The main header now derives its short hash from the
loaded data. The upper viewer opens on the insertion tail with B_Cu visible.
Its registration test checks J100 against back copper and all other markers
against front copper, retaining the original geometric tolerance. New tests cover
the exact paired main/flex pinmap, downloadable historical evidence, the full
prose hash and visible insertion contacts. `tools/pcb/README.md` documents both
contracts, explicit publishing rules, evidence vocabulary and the regeneration loop.

**Corrections to the incoming brief.** The final hardware packages existed outside
the older site-input folders. Flex hashes are self-described, but DESIGNS still
hard-codes directory names and required a v0.3 update. The old main builder checked
three governing hashes, not every input; full snapshot manifest verification is
now explicit. The workflow runs one strict build in the PR test job; its other
strict build is in the deploy job, which is skipped for PRs. Local validation
still runs the requested two strict builds. Work is on a branch for review;
merging and production release remain the owner's decisions.

**Validation.** Two asset builds were byte-identical across 163 generated asset/page files;
`render` and `check` passed for all fourteen blocks. Two strict MkDocs builds had
zero MkDocs warnings. The full suite passed: **68 tests**. The scanner inspected
160 published files and every ZIP member. The configured `els-site` preview and
browser screenshots were reviewed. Source/prose whitespace checks passed; original
CAD/SVG whitespace is deliberately preserved under the byte-exact asset policy.
All 161 staged asset files (including .gitattributes) matched their worktree bytes;
the main board reports `attr/-text` and both changed board blobs hash to the values
above. Every previously published lower/gimbal asset matched its existing Git blob.


## 2026-09-08 — PCB material appearance and reference cleanup

Added a Board materials / Engineering colors appearance control to Doc 9.
Material mode uses black substrate, white actual silkscreen, silver-colored pads,
and family-colored bodies recovered from closed native fabrication contours.
Unresolved contours remain outlines: no invented bounding-box component bodies.
These are illustrative 2D materials, explicitly not component 3D models or an
as-built photograph. Layer inspection and front/back interaction remain available.
Duplicate fabrication reference groups are suppressed at runtime, and assembly
references are off by default; the production silk stays authoritative in the
material view. Native sources, published hashes and all generated assets remain
unchanged. The ESP32 mechanical outline was checked directly against U1 User.Eco2
(18 x 25.5 mm, with a 6 mm antenna section). This annotation is guarded by the
exact current board hash; a changed board does not inherit these coordinates.
The shield and finishes are illustrative. The transparent canvas, black mask and
metallic pad gradients were visually inspected in the local preview.

**Validation.** Generator hash/scanner checks and two strict MkDocs builds pass.
The full browser/data suite passes: **70 tests**, including reference deduplication,
material switching, native module overhang and refusal to reuse that annotation
for a different board hash. No hardware sources or manufacturing files are
changed by this presentation update.


## 2026-09-08 — Grouped arm connectors and branded board snapshot

Doc 9 now consumes the deliberately cut cbb8d9fc learning handoff. Governing main
PCB SHA256: cbb8d9fc060c7f2b3e6b27b096a5728e789e816102ddba393c69e91020144abb.
The current native project, 20 schematic sheets, BOM, placement, layer views,
assembly drawings and fabrication reference agree: 262 features, 241 fitted
parts and 71 BOM rows. J9 is the six-contact spotlight connector beside the
separate J13 tilt harness; J10/J11 are removed and J12 pan remains separate.
Teaching explains the independent LED returns and the external pan service loop.
The back artwork contains the orbit logo, wordmark, website and Kahn quotation.

The black substrate, transparent canvas, white production silk, metallic pads,
colored component bodies and engineering-color alternative are preserved. The
hash guard for the unchanged U1 mechanical depiction is bound to the new board.
This remains an illustrative 2D view, not a photograph or full component model.

Electrical baseline 80195efd retains its original evidence attribution. Current
branding DRC and native/export preservation are separate records. Historical
analogue/thermal results were not relabeled as current. Submission prose states
the latest main package is prepared but not yet submitted, the unchanged gimbal
has a PCBWay inquiry, and upper/lower flex inquiries await a custom-stack route.
No hardware has been powered or production released.

All three flex design asset directories remain byte-exact; only the shared flex
index/provenance link to the new main hash changes. Doc 10 explains the updated
main-to-arm connection without inventing a new flex revision. No chapter was
added or removed, so navigation and document counts retain their existing shape.

Validation: two deterministic asset builds, render/check and two strict MkDocs
builds passed. All 71 tests passed, including material styling, module hash guard,
front/back and flex registration, and the new six-contact pin-map regression.
Front/back screenshots were reviewed; the configured els-site preview is served
locally. Publication scanner and source-byte checks remain enabled. Work stays
on the existing material-view review branch; no deployment or merge performed.
