---
title: 1 · How We Got Here
description: "Round-1 research digest: the physics, vocabulary, and five lessons under every later decision."
---

# Doc 1 · How We Got Here — Gimbal Research, Round 1 (Archive)

**Engineered Lighting prototype series · July 2026**

## The project, in one paragraph

We're building the robotic spotlight for the Engineered Lighting fixture: a silent pan/tilt head (smart CAN servo motors, absolute encoders, no homing dance) carrying a high-CRI 3-up LED spot, living alongside the fixture's tunable-white ambient zones, exposed to Home Assistant as ordinary entities *and* aimed autonomously by a camera-driven perception stack — following people, lighting task surfaces and books, pointing at art when idle, never sweeping across eyes. This seven-document series takes it from research through a working bench prototype to the system architecture, with everything adversarially reviewed and every purchase specified.

## The document map

| # | Doc | What it is | You buy |
|---|---|---|---|
| 1 | [How We Got Here](01-how-we-got-here.md) | Round-1 research digest: the physics, vocabulary, and five lessons under every later decision. Archive — read for understanding | nothing |
| 2 | [Choosing the Motors](02-choosing-the-motors.md) | The decision journey to the RMD-L-4005 smart CAN actuators — what was evaluated, why integrated actuators won | (decision feeds Doc 3) |
| 3 | [Build the Gimbal](03-build-the-gimbal.md) | 10-stage bench build: motors answering on CAN by stage 4, a balanced aimed head by stage 8. Full BoM, wiring, code, AI-partner workflow | ~$185–290 |
| 4 | [Build the Full Fixture Bench](04-full-fixture-bench.md) | One ESP32-C6 running the whole fixture: 21 tunable-white channels + CC spotlight + gimbal, in ESPHome/Home Assistant | ~$170–240 |
| 5 | [Teach It to Aim](05-teach-it-to-aim.md) | The perception stack: cameras, ground-plane tracking, beam self-calibration, coordination, safety, user stories, phased roadmap (Phase 0 = a weekend) | ~$120–320 per room |
| 6 | [The Message Contract](06-message-contract.md) | The one page every component obeys: topics, schemas, units, watchdogs, and the dual-control architecture (HA entities + autonomy without fights). *When docs disagree, Doc 6 wins* | nothing |
| 7 | [Building the Software](07-building-the-software.md) | The code: pinned stack, repo layout, hardware-free testing (replay cameras, simulated fixtures), deployment, firmware growth path, licensing gates | nothing |

**Reading paths:** *Building this weekend?* → [Doc 3](03-build-the-gimbal.md), then [4](04-full-fixture-bench.md) (skim their concepts sections; Docs 1–[2](02-choosing-the-motors.md) optional background). *Understanding the choices?* → 1 → [2](02-choosing-the-motors.md), then skim [5](05-teach-it-to-aim.md). *Writing the software?* → [6](06-message-contract.md) → [7](07-building-the-software.md), with [5](05-teach-it-to-aim.md) as the spec. *Total prototype budget, all hardware:* roughly **$475–850** for one room end-to-end.

## Shopping list for this document: nothing

This is background reading — all purchases live in Docs [3](03-build-the-gimbal.md)–[5](05-teach-it-to-aim.md). What this doc carries is the *understanding*: the physics, the vocabulary, and five lessons every later decision rests on.

---

## The question we asked

Can the fixture's fixed spotlight become robotic — a motorized pan/tilt head that aims light anywhere in the room, silently, controlled by software? Round 1 surveyed how everyone else has ever built "a light that moves": stage lighting, camera gimbals, hobbyist builds.

## Concepts (plain English — these terms appear in every later doc)

- **Moving head / yoke:** the standard mechanical layout for a robotic light. A base rotates left–right (**pan**); a U-shaped bracket (the **yoke**) rides on it and tilts the lamp up–down (**tilt**). Every DJ club light is built this way.
- **Torque:** twisting force. Motors are rated by how much they can exert (we use newton-centimeters, N·cm). The tilt motor must fight gravity trying to flop the lamp head downward.
- **Stepper motor:** moves in fixed clicks ("steps"), no feedback — you *count* steps to know position. Cheap, precise, everywhere in 3D printers.
- **Microstepping / silent drivers:** electronics that slide a stepper *between* its clicks in tiny increments. This is what makes modern 3D printers quiet — a measured drop from 74 dB to **35 dB** just by swapping the driver chip (TMC-series "StealthChop").
- **Hobby servo:** a small motor+gearbox+position sensor in one box (the RC-car part). Convenient, but the cheap internal sensor "hunts" — constantly twitching, audibly, when holding a load.
- **BLDC gimbal motor:** the pancake-shaped brushless motors inside camera stabilizers. Direct drive (no gears at all), which is why camera gimbals are silent and smooth.
- **Encoder:** a position sensor on a joint. An **absolute** encoder knows the angle the moment power comes on — no "finding home" ritual.
- **Homing:** how a motor system without absolute encoders finds a reference point — usually by driving into a switch or a hard stop at startup. Commercial moving heads do a loud full-range "homing dance" on every power-up.
- **Slip ring vs. service loop:** two ways to get wires across a rotating joint. A slip ring (sliding contacts) allows endless rotation but adds noise and wear; a **service loop** (a slack coil of wire) limits rotation to a turn or so but is silent, free, and reliable.

## The five lessons that survived

**Lesson 1 — Stage lighting is the right idea at the wrong scale.** Commercial "mini" moving heads weigh 1.4–3.6 kg — 10–70× our ~50–150 g spotlight head — and their fans are the loudest thing in the room (a verified purchaser on a well-liked Chauvet: "the fans on these are really loud... very noticeable when [music is] not [playing]"). Even *quiet-rated* theatrical fixtures measure 39.6–49.5 dBA — too loud for a living room, where the ambient floor is ~30–40 dBA. **Design target set here: no fans, motion ≤~35 dBA, zero noise parked.**

**Lesson 2 — The torque problem is small, and balance nearly erases it.** Worst case (150 g head hanging 6 cm off the tilt axis): torque = mass × gravity × radius = **8.83 N·cm**. But *balance the head* so its center of mass sits on the tilt axis (like every camera gimbal requires) and the requirement collapses to **~1.5 N·cm** — small enough for thumb-sized motors, and it means near-zero current (silent, cool) while holding position for hours. Balance became a design requirement, not a nicety.

**Lesson 3 — Silence favors gearless designs and joint encoders.** The quietest documented builds either use steppers on silent drivers (good) or direct-drive BLDC with closed-loop control (best — a documented robot head on gimbal motors: "nearly completely silent," ~350 mA worst-case hold). Hobby servos lose on hunting noise; worm gears self-lock nicely (motor fully off while holding!) but waste >50% of torque to friction and can creep under building vibration. And putting the **absolute encoder on the joint itself** means the fixture wakes up already knowing where the beam points — the loud homing dance is deleted from the product.

**Lesson 4 — Skip the slip ring.** Commercial movers all chose limited rotation (540° pan) with a wire bundle over slip rings — and our beam power at 24 V is under 1 A, easy for a service loop of flexible silicone wire. Continuous rotation is a capability the coordinator doesn't need.

**Lesson 5 — There's no shortcut through cheap DMX moving heads.** Driving a $100 club light over DMX as a prototype fails three ways: 8-bit pan resolution (visible ~2° jumps on slow sweeps), loud fans, and the power-up homing dance. Buy one only as a teardown donor, never as the product path.

## What this round got wrong (and round 2 fixed)

Round 1's recommendation — NEMA-11 stepper motors + belt reduction + silent driver chips — was reasonable but built everything by hand: motor mounts, belts, tensioners, encoder mounting, motor-control firmware. Round 2 found the same outcome available as a **sealed smart actuator** (motor + encoder + tuned controller in one purchasable part, commanded digitally) — fewer parts, fewer failure modes, and it deleted most of round 1's engineering. Read [Doc 2](02-choosing-the-motors.md) for that decision.

## Further reading (the round-1 sources worth opening)

- isaac879 Pan-Tilt-Mount (the best-documented quiet stepper build; "almost completely silent in 16th microstepping") — [github.com/isaac879/Pan-Tilt-Mount](https://github.com/isaac879/Pan-Tilt-Mount)
- ETC's published fixture noise data (the only hard dBA numbers in stage lighting) — [support.etcconnect.com](https://support.etcconnect.com) (Ambient Fan Noise in dBA of LED Fixtures)
- Cameo moving-head teardown (how commercial movers home and drive) — [hackaday.io/project/28331](https://hackaday.io/project/28331)
- TMC2208 vs A4988 measured sound test (74 dB → 35 dB) — [the-diy-life.com](https://the-diy-life.com)
- GoodDog gimbal head (the near-silent BLDC precedent, with measured hold current) — gooddog.ai/bumble/gimbal-electronics
