---
title: RMD L5005 · Community Sources
description: "Annotated public implementations and firsthand reports, with motor-family and protocol limits."
---

# RMD L5005 community and implementation evidence

**Research checked 8 October 2026** · [Return to the control and tuning reference](rmd-l5005-control-and-tuning.md).

Public forums, GitHub issues/comments and repository source were inspected. This is a bounded source search, not a claim to have found every post. No motor was accessed, commanded, calibrated, flashed or tested. Source dates below describe the report or implementation; the check date is separate. Unpinned source links describe code inspected at that date and may change.

!!! note "Read the model match before the result"
    Evidence for the exact **RMD-L-5005-100-C** suffix and current firmware is sparse. **Near-exact** means a source names L5005 / RMD-L-5005 without establishing the full suffix, board revision and firmware. **Analogue** means another motor family or generation. An analogue can suggest a discriminating test; it does not establish a safe setting or fix for this unit.

    No convincing exact-L5005 public minimum smooth-speed, cogging-compensation, thermal-soak, continuous-hold or 24/7 endurance validation was established. Nominal ratings and demos do not provide those guarantees.

## Closest L5005 implementations

### 1 · OpenFFBoard force-feedback build

**Near-exact L5005 · firsthand maintainer report · 3 February 2025.** [Project log](https://hackaday.io/project/163904-open-ffboard/log/238222-myactuator-rmd-can-motor-support) describes a working compact RC-style force-feedback controller and reports update limitations below 100 Hz in that setup. Full suffix and firmware are unstated; the bottleneck is not isolated to command processing, feedback or configuration. Do not turn it into a universal L5005 CAN-rate ceiling. [Mechanical build](https://www.printables.com/model/1172877-rc-style-openffboard-controller-with-rmd-l5005) adds provenance, not measured smoothness or lifetime evidence.

### 2 · OpenFFBoard feedback, offsets and fault handling

**Implementation associated with that demo · generic RMD class · source inspected October 2026.** [RmdMotorCAN.cpp](https://github.com/Ultrawipf/OpenFFBoard/blob/master/Firmware/FFBoard/UserExtensions/Src/RmdMotorCAN.cpp) requests automatic multi-turn-angle reports with a coded 10 ms minimum interval and offers active-request mode. It notes coarse torque-response position, stores a host-side offset because the author reports unreliable motor-side storage, starts via zero-current torque control and stops via zero current plus disable. Fault flags gate enabling. These are code decisions, not definitive exact-unit semantics.

The default feedback path is not a complete fault-telemetry supervisor. The [header](https://github.com/Ultrawipf/OpenFFBoard/blob/master/Firmware/FFBoard/UserExtensions/Inc/RmdMotorCAN.h) defaults to 1000 in 0.01 A units: **10 A is not an L5005-safe default**. Review transactions, current limits and supervision before adapting the class.

### 3 · Humanoid head with three L5005 motors

**Near-exact RMD-L-5005 CAN · authors' project/source · README last changed 23 February 2025; inspected October 2026.** [Voice_Driven_Humanoid_Head](https://github.com/acromtech/Voice_Driven_Humanoid_Head) lists three motors, Raspberry Pi 4, Ubuntu 24.04 and USB-CAN. [RobotNeck.py](https://github.com/acromtech/Voice_Driven_Humanoid_Head/blob/laptop_simu/software/lib/RobotNeck.py) uses its L.V1 class, six byte-style RAM gains, startup angles and single-turn position commands. It is a comparable articulated-load use case, without calibrated slow-speed or endurance results.

The inspected code leaves its initialization acceleration argument unused, writes encoder offsets and closes CAN before its shutdown stop calls. [MyActuatorRMD.py](https://github.com/acromtech/Voice_Driven_Humanoid_Head/blob/laptop_simu/software/lib/MyActuatorRMD.py) separates L.V1/L.V2 and X.V2/X.V3; those library labels do not identify the user's protocol. Legacy byte-gain writes are not a current V4.2 recipe.

## Smoothness and trajectory analogues

### 4 · Streamed targets stepping; planner workaround

**Analogue: X8-Pro-H V3 1:6 and X8-Pro V2 1:9 · reproduced and solved report · 27–28 June 2024.** [Issue #10](https://github.com/2b-t/myactuator_rmd/issues/10) reports a 0.5 Hz, 30° sinusoidal target pausing across command intervals from 0.1 to 100 ms; the maintainer reproduced it. [Zero position-planning acceleration/deceleration](https://github.com/2b-t/myactuator_rmd/issues/10#issuecomment-2197400490) produced smooth curves on both reported units; changing maximum velocity alone had not fixed it. The reporter relays vendor guidance around 2 ms request/reply spacing. Cadence alone had not cured the symptom.

[No firmware update was required](https://github.com/2b-t/myactuator_rmd/issues/10#issuecomment-2197409044). The [follow-up](https://github.com/2b-t/myactuator_rmd/issues/10#issuecomment-2197494074) warns that zero planning limits caused abrupt acceleration and overshoot on a large standalone move. This supports comparing planner modes, not blindly removing acceleration constraints on an L5005.

### 5 · Hybrid mode buzzing, stall and firmware sensitivity

**Analogue: X8-Pro-H V3 / X8-Pro V2 · experimental implementation · 2024–2025.** [Issue #9](https://github.com/2b-t/myactuator_rmd/issues/9#issuecomment-2229087593) describes buzzing or faults under small external loads despite gain trials; switching between hybrid and conventional modes reportedly required shutdown. Whole-bus shutdown occurred, but the proposed power-distribution cause remained a hypothesis.

A [follow-up](https://github.com/2b-t/myactuator_rmd/issues/9#issuecomment-2327556086) compares stall behavior on firmware 2023041301 versus 2022101701. [Later discussion](https://github.com/2b-t/myactuator_rmd/issues/9#issuecomment-3221568630) calls discrete-command behavior only semi-reliable and path tracking untested. Record exact firmware; neither hybrid mode nor that older X firmware is an established L5005 cure.

### 6 · ROS latency and noisy feedback

**Analogue: X8 Pro V2 / X8Pro-H · measured integration discussion · June 2024.** [ROS discussion](https://github.com/2b-t/myactuator_rmd_ros/pull/1#issuecomment-2156685589) reports 1.7–2 ms round-trip latency with MKS CANable V1.0. Blocking status requests consume loop time. A [measurement correction](https://github.com/2b-t/myactuator_rmd_ros/pull/1#issuecomment-2161303461) distinguishes motor-side and end-to-end latency; the earlier 1.1 ms figure measured something different.

[Low-pass filtering](https://github.com/2b-t/myactuator_rmd_ros/pull/1#issuecomment-2155678593) improved noisy torque/velocity feedback, with a user confirming improvement. Filtered telemetry does not prove physical cogging disappeared. The thread's early startup-to-zero behavior describes that historical interface, not necessarily the current release.

## CAN reliability and generation mismatches

### 7 · Eight-byte payload solved motion failure

**Analogue: RMD12025; later L-7015 23T · solved forum reports · February/June 2024.** [RobotShop discussion](https://community.robotshop.com/forum/t/unable-to-control-an-rmd-actuator-from-myactuator-via-can/104196) reports successful reads and vendor-tool movement, but failed host motion. Sending **eight payload bytes rather than four** solved the first user's issue. A later L7015 user obtained status replies with a Feather M4 lower-level CAN driver, correct transceiver state and eight-byte frames at his configured 250 kbps. That confirms communication only; it does not set an L5005 bitrate or validate movement.

### 8 · Oscillation after a copied zero-position command

**Analogue: L-7015 23T · unresolved incident · 22 May 2024.** [RMDCANDemo issue #1](https://github.com/tigakub/RMDCANDemo/issues/1) describes working status reads followed by substantial oscillation and apparent failure after a zero-position command. No root cause or recovery is documented. It does not establish a motor defect or protocol bug; it demonstrates why telemetry alone cannot validate a sample driver's motion scale, frame or behavior.

### 9 · Multiple writers and response races

**Analogue: X6-S2, Pi 5, CANable 2.0/candleLight · partly solved integration · April 2025.** [Issue #19](https://github.com/2b-t/myactuator_rmd/issues/19#issuecomment-2794323371) used separate ROS nodes for status and motion. The SDK is not thread-safe; competing transactions can consume the wrong reply. [A mutex fixed the ROS failure](https://github.com/2b-t/myactuator_rmd/issues/19#issuecomment-2801671346), while a separate terminal reproduction remained unresolved. The user's zero-offset power-cycle requirement is a unit-specific observation, not a general rule.

### 10 · Multi-motor BusError and stale replies

**Analogue: X8-Pro-H V3 / X8-Pro V2, 3–4 motors per channel · unresolved · July 2024 onward.** [Issue #11](https://github.com/2b-t/myactuator_rmd/issues/11) reports BusErrors during streaming and later unexpected earlier reply opcodes despite claimed termination and sequential code. The [maintainer notes](https://github.com/2b-t/myactuator_rmd/issues/11#issuecomment-2274039617) that blocking transaction time belongs in trajectory elapsed time; a sleep interval alone is not cadence. Single-actuator C++ operation for hours is an analogue, not L5005 endurance proof. A later different-model ID-setting issue is separate.

### 11 · Electrical rework fixed intermittent errors

**Analogue: RH-17/RH-20 five-motor setup, SH-C30A adapter · reported successful follow-up · 2025.** [Issue #23 follow-up](https://github.com/2b-t/myactuator_rmd/issues/23#issuecomment-2957717050) reports errors stopping after electrical rework, 300–600 µs command timings in that setup, and faster but noisier tracking with the planner disabled. Those are not L5005 performance limits. Do not adopt the thread's precise error-bit diagnosis without payload bits and actual captures: a CAN error-class ID alone does not establish receive-buffer overflow.

### 12 · Protocol mismatch and failed firmware update

**Analogue: X6 MC300A / X6-S2 and X8-Pro · unresolved forum reports · October–November 2022.** [Arduino discussion](https://forum.arduino.cc/t/controlling-my-actuator-motor-with-can-bus-shield/1042204) describes driver/protocol mismatches, rewritten OpenFFBoard support for an older protocol, and lost CAN after firmware from newer setup software. No verified recovery follows. Match board, firmware and protocol; obtain a vendor-approved update/recovery plan before flashing.

### 13 · Correct configuration software mattered

**Analogue: RMD-S V2; later L-7025 · solved S-series / unresolved L-series · 2023 and January 2025.** [RobotShop thread](https://community.robotshop.com/forum/t/myactuator-rmd-s-motors-software-problem/100123) records an S-V2 returning data but failing product-info reads until the vendor supplied matched software. A later L7025 report using Assistant V2 has no published resolution. USB detection is not a matched-tool test; the solved S report does not establish an L fix.

## Holding, shutdown and reboot evidence

### 14 · Last velocity continuing after host or bus failure

**Analogue: four X8 motors, revision unstated · open unvalidated issue · 5 October 2026.** [StarCrawler #32](https://github.com/star-uma/StarCrawler/issues/32) states motors retain velocity after ESP32 hang/reset or CAN loss. Motor-local communication protection and the proposed 100–200 ms setting were unconfirmed, with no completed unplug test. A host watchdog cannot send stop over a failed bus; do not copy the proposed timeout as an L5005 remedy.

[Related #22](https://github.com/star-uma/StarCrawler/issues/22) attributes multi-motor failures to star topology and potentially excessive termination, but rewiring/acceptance items remained unchecked. It is a proposed diagnosis, not a completed repair.

### 15 · Zero-offset persistence varies

**Analogue: X-10-100 versus X8 Pro V2 · report and counter-test · February 2026.** [Issue #26](https://github.com/2b-t/myactuator_rmd/issues/26) reports zero changes after power cycles on X10. The [maintainer's X8-V2 test](https://github.com/2b-t/myactuator_rmd/issues/26#issuecomment-3881337299), firmware 2023020601, behaved correctly. Closure for inactivity did not resolve X10. Stored zero and measuring unpowered multi-turn travel are different guarantees.

## Libraries and experimental routes

### 16 · PolyU-Robocon legacy CAN library

**Legacy protocol V1.61 / Mbed OS 6.13 · repository updated March 2022.** [Library](https://github.com/PolyU-Robocon/RMD-motor-can-bus-lib) lists tests on L7015, L9015/L9010 and X8, with no L5005 test. It includes gain, acceleration, torque, speed and position primitives. A [RobotShop recommendation](https://community.robotshop.com/forum/t/trying-to-get-started-using-a-myactuator-rmd-l-9015-can-servo-motor/105919) explicitly came from a responder who had not used the motor. Neither source validates current L5005 writes.

### 17 · Arduino RMDX generation warning

**X-series protocol V2.4 / RMDX V1 · source inspected October 2026.** [RMDX-Arduino](https://github.com/matthieuvigne/RMDX-Arduino) warns that RMDX-V2's V3 driver differs and describes a basic torque/velocity hello-world. Shared opcodes and a repository name do not establish L-series compatibility or advanced-control readiness.

### 18 · Historical RS485 RMD-L implementation

**Legacy L-series RS485, Arduino Mega · inspected October 2026.** [GYEMS-Servo](https://github.com/rasheeddo/GYEMS-Servo) documents half-duplex direction control and about 170 µs response delay in its setup, with 12-bit angle decoding and old mode/range assumptions. It is neither a CAN driver nor a verified current 14-bit L5005 match.

### 19 · SimpleFOC replacement is an exploratory hardware project

**L-4015 and other unspecified models · community discussion · March 2023 onward, with 2025 follow-ups.** [SimpleFOC thread](https://community.simplefoc.com/t/simplefoc-on-rmd-l-driver/3139) covers customization, Pi CAN trouble, discovery of L V4.2 docs and board replacement anecdotes. It identifies MCU/framework and reverse-engineering hurdles, without a successful drop-in conversion or controlled L5005 low-speed fix. Reflashing is not established as a quick remedy.

## Apply the evidence as tests

1. Match the full motor, driver, firmware and protocol; keep legacy CAN, current L, X hybrid and RS485 examples separate.
2. Compare a bounded onboard-planned move with a timestamped host-generated path. Direct tracking, if supported, shifts trajectory-limit responsibility to the host.
3. Use one transaction owner, match ID/opcode replies, and measure actual latency/cadence.
4. Diagnose electrical errors separately: frame length, termination, topology, IDs, transceiver state, references, adapter and supply.
5. Test boot, stop, output-disable, lost host/bus, faults and recovery as distinct states. Closing software does not prove torque is disabled.
6. Establish thermal/holding margins with the real balanced payload. Use the [main diagnostic sequence](rmd-l5005-control-and-tuning.md#practical-diagnostic-order) for the order and guardrails.

## Evidence not established

No exact-SKU universal gains, calibration cure, cogging table, minimum smooth speed, enclosed holding-current derating or 24/7 field record was verified. Marketing claims and scraped/generated manuals were not treated as firsthand results. The search covered modern/legacy names and public issue trackers; inaccessible private groups, support conversations and unindexed discussions remain outside its scope.
