# PROJECT-STATE — Engineered Lighting · Robotic Spotlight

*Session-handoff file. Any Claude (Cowork, Claude Code, claude.ai) on any machine:
read this file first — it replaces the chat history that produced this repo.
Update it at the end of every working session.*

**Last updated:** 2026-07 (Cowork session, Marcelo's Mac)

## What this project is

The robotic spotlight for the Engineered Lighting fixture: a silent pan/tilt head
(smart CAN servo actuators, absolute encoders) carrying a high-CRI 3-up LED spot,
exposed to Home Assistant as ordinary entities AND autonomously aimed by a
camera-driven perception stack. Full context lives in the 7-doc series in `docs/`,
published at **https://engineering.engineered.lighting/** (this repo, MkDocs
Material, deployed via GitHub Actions).

## Current state (snapshot)

- **Site:** live, 7 chapters + BoM checklist + AI-workflow page. Two adversarial
  review rounds applied. Design pass (DESIGN.md) done.
- **Motors:** RMD-L-4005 sold out everywhere. **Decision: switch to RMD-L-5005**
  (same family/protocol, Ø49×~24 mm, 92 g, 42 N·cm peak, $107.50 at Dings Motion
  USA — confirmed in stock). **Ordering 3** (2 build + 1 spare/bench unit); ask
  for -C (CAN) variant + mating cables + protocol PDF. Docs/site do NOT yet
  reflect the swap → pending prompt #1 below.
- **Nothing else purchased yet.** Doc 4 (LED bench) and Doc 5 (camera) BoMs
  unordered. Valent X tape sourcing still unresolved (dealer-quote item).
- **Hardware owned:** RTX 6000 Blackwell GPU box, Home Assistant install,
  Bambu Lab X1C printer (PETG/PETG-CF on hand assumed).

## Pending work queue (in order)

1. **Run `prompts/2026-07-motor-swap-site-update.md`** in Claude Code (plan mode)
   — propagates the 5005 swap sitewide + outstanding review fixes. Includes the
   history rule (Doc 2's decision record keeps the 4005 story; addendum explains
   the swap) and a localStorage-ID pin so checklist state survives the rename.
2. **Run `prompts/2026-07-doc3b-frame-chapter.md`** — builds out the frame
   design/print stage into a new chapter 3b with a parametric OpenSCAD scaffold,
   fit-check coupon, and X1C print settings.
3. When Dings order ships: update Home's "current phase" line.
4. On motor arrival: Doc 3 stages 1–6 (bench bring-up); calipers → fill the
   OpenSCAD parameters → 3b build order.

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

## How to resume on any machine

1. `git clone https://github.com/hooterjackson/engineered-lighting-site.git`
2. Open the folder in Claude Code (or point a Cowork session at it).
3. First message: *"Read PROJECT-STATE.md and the docs it references; summarize
   state and the pending queue; then let's continue."*
4. Note: Cowork **local** sessions stay on the machine they ran on — this file
   is the continuity mechanism, not chat history. Keep it updated.
