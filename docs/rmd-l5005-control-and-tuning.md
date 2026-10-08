---
title: RMD L5005 · Control and Tuning
description: "Model-specific sources and diagnostic order for smooth low-speed motion and reliable holding."
---

# RMD L5005 control and tuning

**Research checked 8 October 2026** · A reference companion to [Choosing the Motors](02-choosing-the-motors.md), [Stage 5 characterization](03-build-the-gimbal.md#stage-5-characterize-the-measurements-everything-depends-on), and [bench wiring](03a-wire-the-bench.md).

!!! note "Model, driver and firmware applicability"
    This page concerns the **MYACTUATOR RMD-L-5005-100-C**, the direct-drive **CAN** variant. The manufacturer identifies it with the former **L-5005-35T** name. That name mapping does not establish identical driver hardware, firmware or settings across batches. Record the motor label, driver generation, firmware date, protocol revision and configuration-tool version before applying any command or tuning advice.

    **Manufacturer documentation** below describes published capabilities. **Project observation** identifies a result already recorded on this bench. **Proposed test** means a diagnostic recommendation that has not been verified on the present unit. This research did not operate a motor or inspect the running gimbal-bench firmware.

## Start with evidence

Capture one motor's identity, settings, raw CAN traffic and power rail before changing gains. Two leads deserve early checks:

- **Holding disappears while idle:** the [project commissioning contract](06-message-contract.md) specifies a **3000 ms motor communication watchdog**, serviced by polling at least once per second while armed. Confirm the actual configuration and traffic during a stationary target. A documented requirement is not proof that the running controller implements it.
- **Motion pauses between streamed targets:** the L-series protocol distinguishes planned point-to-point motion from direct position tracking. A speed limit alone does not establish that a 5–15 Hz target stream will be smooth. Compare a bounded single move with the same path sent as nearby targets.

These are **proposed tests, not confirmed diagnoses**. Disabling the watchdog, zeroing planner settings, recalibrating, restoring factory settings or flashing firmware changes persistent or safety behavior. Establish version compatibility, save the available settings, support the load and define a rollback before such a bench experiment.

### Diagnostic priority by evidence

| Priority | Candidate | Discriminating observation |
|---|---|---|
| First for lost hold | Idle communication timeout | Compare release with receive gaps near the configured 3 seconds |
| First for streamed stepping | Onboard planner and repeated waypoints | Compare a single move with streaming; X8 analogues report this symptom |
| Next | Supply droop / current limiting | Rail voltage and limit entry during the event |
| Then | Host state, resets, competing writers | Disconnects, stale replies and controller uptime |
| Then | Version/configuration mismatch | Match gain encoding and settings to firmware |
| Then | Load, friction, heat | Compare bare/installed axes and current versus angle/time |
| Last | Gains, calibration, intrinsic ripple | No universal L5005 tuning or cogging cure was established |

This is an investigation order inferred from the sources, not a set of calculated failure probabilities.

## Published specifications for the L5005

The [manufacturer model page](https://www.myactuator.com/l-5005-details) maps **RMD-L-5005-100-C / -R** to the previous **L-5005-35T** name. **C = CAN; R = RS485**. Use the [L5005 parameter package](https://www.myactuator.com/_files/archives/cab28a_c35ed01c7b0d47c5b7e25ed70ed57edc.zip?dn=L-5005-251029.zip), containing **L-5005 251029.pdf**, for the current model specifications. The L Series Product Manual 251029 repeats them on printed D-11/12 (PDF page 6).

| Property | Published value | Applicability or limit |
|---|---|---|
| Nominal motor voltage | 24 V | Measure at the motor during movement |
| Driver input range | 12–24 V | Does not invalidate this project's 12 V fault observation |
| Nominal torque / current | 0.13 Nm / 1.67 A | Not an enclosed continuous-stall qualification |
| Maximum instantaneous torque / current | 0.42 Nm / 5 A | Not a continuous holding allowance |
| Driver current label | 5 A normal / 8 A instantaneous | Do not substitute driver capability for motor or wiring limits |
| Feedback | Single 14-bit magnetic encoder | About 0.02197° per count: 360° / 16384 |
| Listed control precision | 0.01° | Catalog specification; not measured installed accuracy or repeatability |
| Torque constant / pole pairs | 0.08 Nm/A / 14 | Confirm current convention; retain factory motor constants |
| CAN bitrate | 1 Mbit/s | Distinct from application target-update rate |
| Working temperature | −20 to 55 °C | The 120 °C demagnetization value is not a safe operating target |
| Driver / control | MC100; current, speed and position loops; S-curve listed | Behavior depends on installed firmware and settings |

[An older distributor catalog](https://a2v.fr/brushless/moteur-brushless-pancake-rmd-l-5005.php) lists **0.001° control precision**. The current manufacturer sheet lists **0.01°**. Record the revision and resolve conflicts with the manufacturer; do not choose the finer number by preference. Neither is the same quantity as encoder resolution.

## Match the documentation to the unit

Keep **product/winding identity**, **driver hardware generation**, **motor firmware**, and **host protocol/tool versions** separate.

The [L-series download hub](https://www.myactuator.com/downloads-lseries) links **Motor Motion Protocol V4.2-250208.pdf**, labelled for **V3 driver**, and **MC Series Brushless Servo Driver Manual-240611.pdf**. The [setup-software hub](https://www.myactuator.com/downloads-setupsoftware) lists **L5005 under Setup Software V3.0**. X-series V4/V4.1 downloads and protocol V4.4 are separate; a larger version number is not an L5005 upgrade instruction.

Protocol V4.2 changed PID transactions to **indexed floating-point gains**; its history dates that change **28 May 2024**. Older examples use packed byte-sized gains. The vendor SDK240913 package still includes that legacy byte-gain layout, so its gain-write functions are not a verified match for current L V4.2 indexed floats. A successful angle read does not validate a library's parameter writes. The setup GUI's older gain scaling also differs from the newer protocol format.

The [vendor-hosted SDK240913 package](https://www.myactuator.com/_files/archives/cab28a_ff037359c635421b87128c3bfb2059d2.zip?dn=SDK-240913.zip) contains the **2b-t/myactuator_rmd** project and a ROS companion. Its README describes an **X-series** driver. Use it as an implementation reference, checking every required transaction against the installed L-series protocol. Vendor hosting does not guarantee every command is compatible.

## Diagnose smooth movement

### Planner behavior and command cadence

**Manufacturer documentation:** V4.2 §2.21, printed pages 47–48, describes absolute-position control. Nonzero position-planning acceleration generates an acceleration/deceleration move. Zero selects direct position tracking through the PI controller. The speed-limit field still matters; zero speed limit has a separate special meaning. This is a mode distinction, **not a suggested setting change**.

**Proposed test:** compare one small safe sweep with the same path sent as a target stream. Keep one host writer, stable measured cadence, the same load and the same travel/speed bounds. Log commanded and measured angles with timestamps. If the single sweep is smooth while streaming pulses at the update rate, investigate planner interaction before increasing gains. Angle-dependent ripple and load-dependent oscillation point to different causes.

The acceleration-write command in §2.5 writes **RAM and ROM**. Do not put it in a high-rate control loop. The normal planner range and zero special case must be interpreted for the actual firmware.

### Command resolution, telemetry and beam placement

A position command can express hundredths of a degree, while the published 14-bit encoder has about **0.022° per count**. Neither proves repeatable beam placement under load. At a 3 m throw, one count corresponds to about **1.15 mm** near normal incidence (calculated geometrically); optics, mechanical flex and controller behavior can dominate.

V4.2 motion-command replies report angle and velocity at coarser scales than dedicated angle reads. Coarse replies can make a trace look stepped. Use version-correct dedicated angle/encoder telemetry alongside video or an optical spot measurement; do not estimate low-speed velocity by differentiating coarse one-degree samples.

### Mechanical and electrical load

**Proposed test:** compare the bare motor, a balanced installed axis and the final wired head. Inspect cable spring torque, rubbing, preload, alignment, screw depth, structural resonance and gravity loading when the symptom appears only after assembly. Direct drive removes gearbox backlash, not cogging, bearing drag or mount compliance.

Use **0.13 Nm nominal**, rather than 0.42 Nm peak, as the first sustained-load screening value. A 100 g mass 4 cm off axis creates about **0.039 Nm** at worst orientation before cable load and acceleration. This calculation is not a load approval; use actual mass, center of mass, duty cycle and thermal environment.

**Project observation, 31 July 2026:** [Doc 3](03-build-the-gimbal.md#stage-1-bench-setup-and-the-three-rules) records a unit answering reads around 12 V, faulting when asked to move and losing replies until a power cycle. The general driver manual describes undervoltage as a recoverable level-2 condition. Preserve the bench result as unit-specific evidence; do not assume every L5005 firmware latches or loses CAN identically. Check rail droop and supply current-limit entry when the power stage energizes.

### Gain adjustment and calibration

The integrated control implementation is proprietary, but its gains are **not categorically untunable**. The current protocol documents current, speed and position-loop gain reads/writes; the setup manual describes loop settings and encoder calibration. Support and scaling depend on version.

Record the original settings and compare motors first. If tuning is justified, change one variable within a vendor-confirmed procedure; prefer reversible RAM-only gain trials when supported. Calibration can move the motor and is a separate operation. The driver manual warns that disassembly can disturb encoder alignment and calibration.

## Diagnose holding and recovery

### Log the motor state separately from the host state

Distinguish **host connected**, **motor powered**, **motor communicating**, **closed-loop active**, **position held**, and **motion allowed**. A lit LED or angle reply does not prove holding torque is active.

In V4.2, shutdown disables output and clears the running closed-loop state; stop preserves the closed-loop mode while stopping motion. Inspect the bytes behind a library's stop, shutdown, disable, release or run function. Do not copy a legacy enable opcode across generations by name alone.

### Keep the watchdog useful

**Project requirement:** a **3000 ms communication watchdog** with **≥1 Hz status polling while armed**, distinct from the higher-level MQTT target timeout. Verify that the embedded controller owns servicing and continues during stationary targets, browser closure and resolver disconnect. Motor safety and holding must not depend on an open browser or an awake laptop.

**Manufacturer documentation:** a communication timeout cuts output and requires stable continuous communication before running again. It does not settle every firmware's timer-refresh messages, persistence across power cycles, recovery sequence or interaction with active transmit-only telemetry. Traffic emitted by the motor does not prove that it receives a heartbeat.

**Proposed test:** verify those details on the actual unit. Retain timeout protection; define holding with a healthy authorized controller and a safe mechanical outcome when communication or torque disappears. Support gravity-loaded payloads during communication-loss tests.

### Preserve fault evidence before resetting

Capture raw fault bits, LED pattern, motor voltage/temperature, host reset reason, CAN error counters, missed responses and timestamps. A power cycle can restore operation while hiding the cause. The driver manual distinguishes slow warning flashes from fast serious-error flashes and warns about overload, blocked heat conduction and sudden large gain changes.

Repeated resets or enable retries are not a reliability strategy. The [PCB documentation](09-understand-the-pcb.md) states that its SAFE gate controls lighting and does not remove motor power; emergency motion protection remains a separate requirement.

### Host timeouts and CAN recovery

**Conditional lead:** if the actual controller is ESPHome, inspect [API](https://esphome.io/components/api/), [MQTT](https://esphome.io/components/mqtt/) and [Wi-Fi](https://esphome.io/components/wifi/) reboot policies. Their current documentation describes default **15-minute** reboot timeouts when the corresponding API client, MQTT broker or Wi-Fi connection is absent. Only enabled components and the compiled settings apply; Wi-Fi AP mode is excluded. An enabled API without a connecting client can cause periodic reboots. A release near 15 minutes makes this layer worth checking alongside the 3-second motor watchdog. This does not establish that the bench runs ESPHome; define offline behavior before changing recovery settings.

The ESP32-C6 is not categorically limited to power-cycle recovery from CAN bus-off: [ESP-IDF v5.1.4 documents software recovery](https://docs.espressif.com/projects/esp-idf/en/v5.1.4/esp32c6/api-reference/peripherals/twai.html). APIs/state transitions depend on driver version, and a particular bench sketch may lack recovery. Clear or reject stale motion targets before returning to service. [Linux SocketCAN documentation](https://docs.kernel.org/networking/can.html) covers adapter error frames, counters and recovery.

## Practical diagnostic order

1. **Record identity and baseline.** Capture labels, driver/firmware date, protocol revision, CAN/reply IDs, bitrate, host source commit, adapter firmware and active-reply setting. Read gains, planners, limits, zero offsets, current limits and watchdog using a verified path. Mark settings without demonstrated readback; do not claim a complete backup.
2. **Observe one supported motor without configuration changes.** Use the existing approved current-limited supply and known safe travel. Capture two minutes of stationary holding and a safely reproducible symptom with monotonic CAN timestamps. Correlate hold loss with gaps near 3 seconds, voltage changes, uptime resets or host restarts.
3. **Prove supply and physical bus.** With power removed, verify about 60 Ω across the completed pair: two 120 Ω end terminators. Check actual termination in every device, twisted pair, short stubs, hardware-appropriate reference connection and duplicate IDs. Measure voltage at the motor through start/reversal/hold. Distinguish DC bus current from winding/torque current; retain the wiring and PCB commissioning limits. [Doc 3c](03c-prove-the-bus.md) covers the independent bus proof.
4. **Separate trajectory effects.** Compare a single bounded move with streamed targets using identical travel, load and limits. Only after baseline capture should a qualified operator compare documented planner modes or adjust a gain, with saved settings and rollback.
5. **Test holding and recovery separately.** Compare normal idle polling, application disconnect with embedded polling continuing, and supported communication loss. Determine required recovery state transitions and a fresh bounded target. Startup needs fresh telemetry, valid zero/limits and deliberate motion authorization. Stored multi-turn state cannot measure turns made while unpowered.
6. **Qualify progressively.** Repeat with both axes, final wiring and lighting loads. Run attended tests to thermal equilibrium at the intended worst-case ambient. Define beam jitter, tracking error, noise, temperature and recovery acceptance limits first. A four-hour hold is a useful screen, not a 24/7 lifetime or product-safety qualification.

## Bring to the next tuning session

- Motor identity/version for each unit and the actual controller/host source commits.
- Recorded settings and a symptom video distinguishing buzz, angle ripple, waypoint pauses, release, reset or failed re-enable.
- Raw timestamped CAN log, dedicated angle data, reply latency and command cadence.
- Torque current, bus voltage, temperature, fault bits and uptime where supported.
- Supply/current-limit settings, wiring lengths, termination and adapter firmware.
- Payload mass/offset, cable routing, travel limits, enclosure temperature and what **always on** must mean: powered, holding or ready to resume.

## Manufacturer sources

All links were checked for this research on **8 October 2026**. Filename dates identify document/package revisions; undated web pages are retrieval entry points. Link to public originals; the manuals are not republished here.

| Source | Revision and use | Limit |
|---|---|---|
| [L5005 model page](https://www.myactuator.com/l-5005-details) | Undated; current/legacy name mapping | Does not identify installed firmware |
| [L-series download hub](https://www.myactuator.com/downloads-lseries) | Undated; model drawings and L-family manuals | Match the driver generation |
| [L5005 parameter/CAD package](https://www.myactuator.com/_files/archives/cab28a_c35ed01c7b0d47c5b7e25ed70ed57edc.zip?dn=L-5005-251029.zip) | 251029; L-5005 parameter PDF, drawing and STEP | Catalog values are not installed measurements |
| [L-series protocol/manual bundle](https://www.myactuator.com/_files/archives/cab28a_8136b0f46af3455ea383921d5aa02ce5.zip?dn=%28L%29Protocol+and+manual+of+V3+-251029.zip) | Product Manual 251029; MC Driver Manual 240611; Motion Protocol V4.2-250208 | Gains/planners §2.1–2.5; telemetry §2.12–2.16; shutdown/stop §2.17–2.18; position modes §2.21; firmware date §2.29; timeout §2.30; identity/active replies §2.32–2.33; faults §8; history §9 |
| [Setup compatibility hub](https://www.myactuator.com/downloads-setupsoftware) and [Setup V3 package](https://www.myactuator.com/_files/archives/cab28a_a8a48972a3264924aec4cc4b388b7e77.zip?dn=MYACTUATOR_Setup+software_V3.0_20230204.zip) | Package 20230204; manual pp. 9–11 gains/limits/planners, 12–13 calibration, 14–15 restore/update | An update interface does not supply an approved firmware image or authorize flashing |
| [Official SDK hub](https://www.myactuator.com/downloads-sdk) and [SDK240913 archive](https://www.myactuator.com/_files/archives/cab28a_ff037359c635421b87128c3bfb2059d2.zip?dn=SDK-240913.zip) | 240913; community SDK and ROS wrapper | Bundled README describes X-series; review each L-series transaction |
| [Dings software page](https://www.dingsmotionusa.com/software-download) and [L5005 product page](https://www.dingsmotionusa.com/rmd-l-5005) | Undated; distributor corroboration | Manufacturer revision-controlled PDFs take priority for disputed values |

## Community reports and example code

The [community and implementation source index](rmd-l5005-community-sources.md) annotates **19 source groups**, separating near-exact L5005 builds from other motor families and legacy protocols. Start with the [OpenFFBoard L5005 build](https://hackaday.io/project/163904-open-ffboard/log/238222-myactuator-rmd-can-motor-support), [three-motor humanoid head](https://github.com/acromtech/Voice_Driven_Humanoid_Head), [X8 streamed-position issue](https://github.com/2b-t/myactuator_rmd/issues/10), and [unresolved L7015 oscillation incident](https://github.com/tigakub/RMDCANDemo/issues/1). These are implementation evidence and diagnostic leads; none establishes exact-unit 24/7 suitability.

## Questions for the manufacturer

Request approved protocol/setup versions for the actual serial numbers, firmware identity/release notes, recovery sequence and watchdog refresh/persistence semantics. Ask for low-speed tracking guidance, safe planner/gain ranges, any supported encoder/cogging calibration, and static-hold derating versus ambient and mounting heat path. Confirm whether the supplied configuration has a brake: a generic protocol field does not establish fitted hardware. No supplier was contacted for this research.

## Scope and remaining evidence gaps

This reference is curated research and a diagnostic plan. The current running gimbal-bench implementation and physical settings were unavailable for direct verification. No motor commands, parameter writes, calibration, firmware updates or hardware tests were performed for this research. No public L5005 continuous-duty derating curve, exact-unit firmware release history or independently verified 24/7 lighting-gimbal endurance result was established. Request those from the manufacturer when needed for deployment.
