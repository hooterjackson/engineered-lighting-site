---
title: 2 · Choosing the Motors
---

# Doc 2 · Choosing the Motors — Why Smart CAN Actuators Won

**Engineered Lighting prototype series · July 2026**

## The purchase this decision produces

The full build shopping list (wiring, supply, tools) lives in **Doc 3's BoM**. This doc's outcome is the part at the heart of it:

| Part | Qty | Est. | What it is and why it's the pick |
|---|---|---|---|
| **MyActuator RMD-L-4005-100-C** | 2 | $60–120 | A "smart servo": brushless gimbal motor, 18-bit absolute encoder, and a factory-tuned FOC controller sealed into one Ø39.6 × 23 mm, 65 g puck. Direct drive — no gears to whine or wear. Runs natively on the fixture's 12–24 V bus and is commanded over CAN in single 8-byte messages ("go to 32.5° at 10°/s"); all motion control happens inside the part. One becomes the pan axis, one the tilt. Ordering note: select the **-C (CAN)** variant — the same listings carry an RS485 "-R" twin, and "-25T" is this motor's deprecated old name. US sources: Amazon, RobotShop, Dings Motion USA |
| Caddx GM2 bare 2-axis gimbal *(optional)* | 1 | $70 | A working 30 g UART-commanded FPV gimbal — a great study article for control feel and micro-scale mechanical packaging (its motors are sized for 5–20 g cameras, so it's a reference, not the actuator) |

Everything else evaluated — bare motors + DIY control stacks, hobby servos, drone motors, the other integrated actuators — is covered in the decision journey below, so the reasoning stays legible without cluttering the shopping list.

---

## Concepts (plain English)

- **BLDC (brushless motor):** three coils of wire pushing a ring of magnets. No contacts to wear, no gears — silent by construction. But it's "dumb": something must energize the right coils at the right moments.
- **FOC (field-oriented control):** the math that drives a BLDC smoothly — steering the magnetic field continuously instead of in steps. FOC done well = silky, silent motion; FOC done badly = buzzing and vibration. Tuning FOC yourself is the hard part of DIY.
- **Absolute encoder:** a magnetic angle sensor on the shaft that knows the position instantly at power-on. The RMD-L's is 18-bit ≈ 0.001° resolution — about 170× finer than we need. One honest limit: it's **single-turn** — it knows the angle *within* one revolution but can't count full turns made while unpowered (irrelevant if the frame has hard stops, which ours will).
- **Integrated smart actuator:** motor + encoder + FOC controller + firmware sealed in one unit, commanded over a digital bus. You skip motor drivers, encoder mounting, and control-loop tuning entirely. This category is why round 1's plan died.
- **CAN bus:** a rugged two-wire network from the automotive world. Every device has an address; messages are 8-byte packets; wiring is one twisted pair shared by all devices. Our ESP32-C6 has a CAN controller on-chip (Espressif calls it TWAI).
- **KV rating:** motor speed per volt. High-KV motors (drone racing) are wound to spin fast; gimbal motors are low-KV, wound for smooth torque at near-zero speed. Same size, opposite personalities — why cheap tiny drone motors can't do this job.
- **Cogging:** the magnetic "clickiness" you feel turning a motor by hand — magnets snapping between preferred positions. Visible as tiny stutter at very low speeds; good gimbal motors and good FOC minimize it.
- **Direct drive:** load bolted straight to the motor, no gearbox. Zero backlash, zero gear noise. The whole camera-gimbal industry is direct drive — and so are we.

---

## The decision journey (what we searched, in order)

**1. "Use what DJI uses" — a wall.** The Osmo-Pocket-scale motors (~Ø12–15 mm) are proprietary: no published dimensions, no purchasable parts, no pinouts. Teardowns show what's inside (a standard driver chip, MP6536, plus Hall sensors and flex cables — no slip rings), but the connectors are undocumented and the newer devices speak private digital buses. Even controlling a DJI phone gimbal over Bluetooth is a dead end — the best reverse-engineering effort gets telemetry but the device *silently ignores* motor commands. **Verdict: don't build on DJI hardware.**

**2. The buyable floor.** The smallest true gimbal motor money can buy is the CopterLab PM1105 — Ø12×16 mm bare, 12 g, ~1 N·cm, $21.71. Genuinely Osmo-scale, but right at our torque floor (needs a very strictly balanced head). The workhorse class is one size up: **2804-class** (Ø35 mm, ~50 g, 2.5–3.4 N·cm), sold with factory-mounted encoders. Nothing between ~Ø18 mm and Ø35 mm ships with an encoder — a real market gap, confirmed by the builder community.

**3. The DIY path and its documented pain.** Bare gimbal motor + encoder + open-source FOC (SimpleFOC) works — there are lovely precedents (a "practically noiseless" pan/tilt camera turret; a fully open-source smartphone gimbal with CAD and PCBs). But the forums also document the failure modes honestly: encoder mounting quality is the #1 killer, low-speed cogging resists tuning, and open-loop shortcuts are *never* quiet. Budget: weeks. And the convenient two-axis driver board we'd have used (MKS Dual FOC) turned out to have a community reliability record bad enough to withdraw it.

**4. The category that ends the debate: integrated smart actuators.** Robotics vendors now sell exactly what we were about to hand-build, factory-tuned and sealed:

| Actuator | Size | Torque (nom/peak) | Bus | Volts | Price/axis | Verdict |
|---|---|---|---|---|---|---|
| **MyActuator RMD-L-4005** | **Ø39.6×23 mm, 65 g** | 7 / 25 N·cm | CAN + RS485 | **12–24 V** | ~$30–60/axis | **Winner** — direct drive, 18-bit absolute encoder, native on our 24 V bus, US distributor + Amazon |
| M5Stack RollerCAN | 40 mm cube, 83 g | 6.5 N·cm @16 V | CAN/RS485 | 6–16 V | $37–44 | Cheapest; not 24 V; torque marginal |
| SteadyWin GIM3505 (driver SKU) | Ø43×30 mm | — | CAN/RS485 | 12–48 V | $76–120 | Fine; China-only shipping; SKU confusion (encoder-only vs driver versions) |
| CubeMars GL40 II | Ø46×33.5 mm, 125 g | 25 / 68 N·cm | CAN | 16 V | $134 | The premium "quiet gimbal actuator" if RMD disappoints |
| DYNAMIXEL XL330 | 20×34×26 mm, 18 g | 10 N·cm | TTL serial | 5 V | $27 | Tiny and charming — but **geared** (plastic gears = noise) and 5 V. Wrong physics for silence |

**Why the RMD-L-4005 wins, in product terms:** each axis becomes a *part* instead of a project. The fixture always knows where the beam points (absolute encoder → no homing dance, survives power loss). Torque headroom (25 N·cm peak vs 8.83 worst-case unbalanced) makes head balancing good-practice rather than mandatory. And the electronics shrink: the ESP32-C6 already has CAN on-chip, so the whole motion subsystem needs one $2 transceiver chip — no motion co-processor, no driver boards, no encoder wiring.

**The trade-offs, honestly:** the control loop is a black box (if it whines at hold, you can't retune it — that's the first bench measurement in Doc 3); it's ~5 mm fatter than the smallest bare motors; it's a Chinese vendor with a US distributor; and at production volume you'd cost-down to your own driver on the fixture PCB — the RMD-L is the prototype accelerant and the behavioral reference for that later design.

**5. Reality checks from adjacent worlds.** FPV drone gimbals (Caddx GM2: 30 g, $70, PWM/UART, even natively supported by ArduPilot autopilots) prove the control patterns but are motored for 5–20 g cameras — a payload class too small for our head. And architectural lighting already has a patented motorized recessed spotlight line (**Forma MOTOLUX**, ±40° dual-axis, DMX/Casambi — patent US 11215345): the category exists commercially, validating the concept and requiring a freedom-to-operate review before our commercial fixture.

---

## Risks carried forward

- **Hold-state whine** is the one unknown that matters: a statically held BLDC can whine at some operating points, and the RMD's sealed loop can't be retuned. Doc 3, stage 5 measures it before anything else depends on it.
- **Speed vs. silence:** follow-me needs 54–80°/s pan on close passes (Doc 5's math); noise at those speeds is unmeasured — same stage-5 bench item.
- **Protocol drift:** older stock has shipped with older protocol docs — trust the PDF in the box over any byte layout written here.
- **Patents:** Forma (motorized recessed fixtures) and Position Imaging US 12,190,542 (beam self-calibration, see Doc 5) — counsel review before commercialization.

## Further reading

RMD-L-4005 — myactuator.com/l-4005-details · dingsmotionusa.com/rmd-l-4005 · Protocol manual — search "RMD Motor Motion Protocol V4.01 PDF" · Osmo Mobile 8 teardown — chargerlab.com · SimpleFOC community (the DIY evidence base) — community.simplefoc.com · GoodDog silent gimbal head — gooddog.ai/bumble/gimbal-electronics · SaraKIT quiet pan/tilt — hackaday.io/project/193511 · Caddx GM series + ArduPilot — ardupilot.org/copter/docs/common-caddx-gimbal.html · Forma MOTOLUX — formalighting.com
