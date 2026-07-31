---
title: BoM Checklist
description: "Every purchase in the series in one interactive checklist — check items off as you order; progress persists in your browser."
hide:
  - toc
---

# Bill of Materials — interactive checklist

Every purchase in the series, in one list. Check items off as you order — state persists in your browser (nothing leaves your device). The full "Notes / traps" for each part live in the chapter BoM tables: [Doc 3](03-build-the-gimbal.md), [Doc 4](04-full-fixture-bench.md), [Doc 5](05-teach-it-to-aim.md), [Doc 8](08-build-the-fixture.md).

!!! note "Prices verified July 2026"
    All prices in the series were verified in July 2026 — **re-check live prices when ordering**. This is the docs' own pre-purchase-recheck rule (see [Doc 7's risk register](07-building-the-software.md)).

!!! tip "Two distinctions that cost more wrong orders than anything else on this page"
    **Solid and stranded wire are not interchangeable, and the listing photos look identical.** Breadboard contacts and soldered bus rails want **solid** core — stranded frays, buckles and reads intermittent in a breadboard, and won't hold its shape as a rail. Anything that flexes or gets handled wants **stranded** — the 24 V runs, the service loops across the pan/tilt joints. "Marine" and "silicone" wire is always stranded, and deliberately floppy.

    **On fuses the letters carry the meaning, not the millimetres.** In 5×20 mm, **GMC is slow-blow and GMA is fast**; in 6.3×32 mm, **MDL is slow and AGC is fast**. Same glass, same size, opposite behaviour. Automotive blade fuses (ATM/ATO/APM) are fast-acting and assortments rarely stock a 3 A at all. Every fuse in this series is a **time-delay** part, because motor inrush plus the bulk cap will nuisance-blow a fast one on power-up.

<div id="bom-global">
  <progress id="bom-bar" max="44" value="0" aria-labelledby="bom-global-text"></progress>
  <span id="bom-global-text">0/44 items</span>
</div>

<details open class="bom-section" data-section="d3" markdown="0">
<summary><strong><a href="../03-build-the-gimbal/">Doc 3 · Gimbal (~$350–405)</a></strong> <span class="bom-progress"></span></summary>
<div class="bom-scroll">
<table>
<thead><tr><th></th><th>Part</th><th>Qty</th><th>Est.</th><th>Where</th><th>Why</th></tr></thead>
<tbody>
<tr><td><input type="checkbox" class="bom-box" id="d3-motors" data-lo="215" data-hi="322.5" aria-label='MyActuator RMD-L-5005-100-C (CAN variant)'></td><td><label for="d3-motors">MyActuator RMD-L-5005-100-C (CAN variant)</label></td><td>2 (+1 spare rec.)</td><td>$215 / $322.50 for 3</td><td><a href="https://www.dingsmotionusa.com/rmd-l-5005">Dings Motion USA</a>, $107.50 ea</td><td>The smart pan/tilt actuators — order the <strong>-C (CAN)</strong> variant, and ask for mating cables for the <strong>6-pin JST ZH</strong> port — ZH, not the larger XH (<a href="../03a-wire-the-bench/">Doc 3a</a>); third unit = permanent bench spare</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-esp32" data-lo="9" data-hi="15" aria-label='ESP32-C6 dev board (ESP32-C6-DevKitC-1)'></td><td><label for="d3-esp32">ESP32-C6 dev board (ESP32-C6-DevKitC-1)</label></td><td>1</td><td>$9–15</td><td>Amazon, Adafruit, DigiKey</td><td>Same chip as the fixture — everything learned transfers</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-can-xcvr" data-lo="8" data-hi="8" aria-label='SN65HVD230 CAN transceiver breakout (Waveshare "CAN Board")'></td><td><label for="d3-can-xcvr">SN65HVD230 CAN transceiver breakout (Waveshare "CAN Board")</label></td><td>2 (1+spare)</td><td>$8</td><td>Amazon</td><td>The CAN line driver — turns chip signals into the differential wire pair</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-resistors" data-lo="1" data-hi="1" aria-label='120 Ω resistors, ¼ W'></td><td><label for="d3-resistors">120 Ω resistors, ¼ W</label></td><td>few</td><td>$1</td><td>any resistor kit</td><td>CAN bus termination</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-psu" data-lo="45" data-hi="60" aria-label='Bench power supply, ≥3 A continuous, adjustable current limit'></td><td><label for="d3-psu">Bench power supply, ≥3 A continuous, adjustable current limit</label></td><td>1</td><td>$45–60</td><td>Amazon (any 30 V/5 A unit)</td><td>Powers the whole bench — the adjustable current limit is smoke insurance</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-multimeter" data-lo="20" data-hi="20" aria-label='Multimeter'></td><td><label for="d3-multimeter">Multimeter</label></td><td>1</td><td>$20</td><td>Amazon</td><td>Non-negotiable — polarity check before every first power-up</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-breadboard" data-lo="10" data-hi="10" aria-label='Breadboard + jumper wires'></td><td><label for="d3-breadboard">Breadboard + jumper wires</label></td><td>1 kit</td><td>$10</td><td>Amazon</td><td>Signals only — power never routes through it</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-usbc" aria-label='USB-C data cable'></td><td><label for="d3-usbc">USB-C data cable</label></td><td>1</td><td>—</td><td>you own one</td><td>Charge-only cables are a classic trap</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-screws" data-lo="10" data-hi="10" aria-label='M2.5 + M3 screw assortment'></td><td><label for="d3-screws">M2.5 + M3 screw assortment</label></td><td>1 box</td><td>$10</td><td>Amazon</td><td>Confirm sizes against the motor drawing</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-usb-can" data-lo="20" data-hi="25" aria-label='USB-to-CAN adapter ("CANable" or clone)'></td><td><label for="d3-usb-can">USB-to-CAN adapter ("CANable" or clone) <span class="bom-optional">optional</span></label></td><td>1</td><td>$20–25</td><td>Amazon</td><td>Lets your laptop eavesdrop on the bus — turns "nothing happens" into evidence. <a href="../03a-wire-the-bench/">Doc 3a</a> shows where it taps in; <a href="../03c-prove-the-bus/">Doc 3c</a> proves your CAN side with it before any motor exists</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-printing" data-lo="20" data-hi="20" aria-label='PETG filament + FDM printer access'></td><td><label for="d3-printing">PETG filament + FDM printer access</label></td><td>~250 g</td><td>$20</td><td>Amazon / local makerspace</td><td>Six printed parts plus three test coupons, ~180 g of frame — a makerspace or print service works. See <a href="../03b-print-the-frame/">Doc 3b</a></td></tr>
<tr><td>—</td><td><label><s>608ZZ bearing, 8 × 22 × 7 mm</s> — <strong>no longer required</strong></label></td><td>0</td><td>$0</td><td>—</td><td>Frame v8 deleted the idle side of the tilt axis: no trunnion, no bearing carrier, no bearing. The head cantilevers off the tilt motor's own output, which carries 0.505 N and 0.0146 N·m — about 3.5% of the motor's peak torque. Kept here, struck through, so anyone who bought one against an earlier revision knows why it is not in the build</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-clamp" data-lo="10" data-hi="10" aria-label='C-clamp or small bench vise'></td><td><label for="d3-clamp">C-clamp or small bench vise</label></td><td>1</td><td>$10</td><td>hardware store</td><td>Clamps the bare motor before its first move</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-payload" aria-label='Payload stand-in: small flashlight or ~100 g weight'></td><td><label for="d3-payload">Payload stand-in: small flashlight or ~100 g weight</label></td><td>1</td><td>—</td><td>—</td><td>Real LED head comes from <a href="../04-full-fixture-bench/">Doc 4</a></td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-calipers" data-lo="10" data-hi="20" aria-label='Digital calipers'></td><td><label for="d3-calipers">Digital calipers</label></td><td>1</td><td>$10–20</td><td>Amazon</td><td>The frame chapter (<a href="../03b-print-the-frame/">Doc 3b</a>) runs on measurements</td></tr>
</tbody>
</table>
</div>
<p><button type="button" class="md-button" data-reset>Reset section</button> <button type="button" class="md-button" data-copy>Copy unchecked as shopping list</button></p>
</details>

<details open class="bom-section" data-section="d4" markdown="0">
<summary><strong><a href="../04-full-fixture-bench/">Doc 4 · LED bench (~$170–240)</a></strong> <span class="bom-progress"></span></summary>
<div class="bom-scroll">
<table>
<thead><tr><th></th><th>Part</th><th>Qty</th><th>Est.</th><th>Where</th><th>Why</th></tr></thead>
<tbody>
<tr><td><input type="checkbox" class="bom-box" id="d4-pca9685" data-lo="10" data-hi="30" aria-label='PCA9685 16-ch PWM breakout (Adafruit #815 or clone)'></td><td><label for="d4-pca9685">PCA9685 16-ch PWM breakout (Adafruit #815 or clone)</label></td><td>2</td><td>$30 / ~$10 clones</td><td><a href="https://www.adafruit.com/product/815">Adafruit</a>, Amazon</td><td>The PWM expanders — bridge the A0 jumper on board #2 (address 0x41)</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-uln2803" data-lo="10" data-hi="10" aria-label='ULN2803A driver IC, 18-pin DIP (+ sockets)'></td><td><label for="d4-uln2803">ULN2803A driver IC, 18-pin DIP (+ sockets)</label></td><td>4 (+1 spare)</td><td>$10</td><td><a href="https://www.adafruit.com/product/970">Adafruit #970</a>, Amazon</td><td>Lets 3.3 V dimmer signals switch the 24 V tape channels</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-soldering" data-lo="25" data-hi="40" aria-label='Soldering iron kit (iron, solder, flux, helping hands)'></td><td><label for="d4-soldering">Soldering iron kit (iron, solder, flux, helping hands)</label></td><td>1</td><td>$25–40</td><td>Amazon</td><td>For the tape-pad wires and the address jumper</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-picobuck" data-lo="17.5" data-hi="17.5" aria-label='SparkFun PicoBuck (PRT-13705)'></td><td><label for="d4-picobuck">SparkFun PicoBuck (PRT-13705)</label></td><td>1</td><td>$17.50</td><td><a href="https://www.sparkfun.com/products/13705">sparkfun.com</a></td><td>The spotlight's 3-channel constant-current driver, PWM-dimmable</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-tape" data-lo="486" data-hi="486" aria-label='Diode LED Valent X Tunable White spool (DI-24V-VLX-TW1865-016, 16.4 ft)'></td><td><label for="d4-tape">Diode LED Valent X Tunable White spool (DI-24V-VLX-TW1865-016, 16.4 ft)</label></td><td>1</td><td>$486</td><td><a href="https://buyriteelectric.com/products/diode-led-di-24v-vlx-tw1865-016-16-4ft-4-6w-ft-valent-x-tunable-white-led-tape-light-color-temperature-1800k-3500k-6500k-voltage-24v">BuyRite</a>, <a href="https://www.lbclightingpro.com/products/diode-led-valent-x-tunable-white-24v-4-6w-ft-16-4-ft-led-tape-light">LBC Lighting</a></td><td>7 short zones ≈ 3.3 ft used — one spool covers everything with spare. Budget bench substitute: <a href="https://www.amazon.com/dp/B08Q3RKCZH">BTF 24 V CCT FCOB</a> (~$30, 2-channel, no 1800 K)</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-star-optics" data-lo="15" data-hi="25" aria-label='Cree 3-up star (XP-G2/XP-L) + Carclo 10507 narrow-spot optic (grab 10508/10509 too)'></td><td><label for="d4-star-optics">Cree 3-up star (XP-G2/XP-L) + Carclo 10507 narrow-spot optic (grab 10508/10509 too)</label></td><td>1</td><td>$15–25 (optics $3 ea)</td><td><a href="https://www.ledsupply.com">LEDSupply</a></td><td>The spotlight payload — optics snap-swap in seconds, which <em>is</em> the beam-width experiment</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-heatsink" data-lo="8" data-hi="8" aria-label='Heatsink ≥2"×2" + thermal adhesive'></td><td><label for="d4-heatsink">Heatsink ≥2"×2" + thermal adhesive</label></td><td>1</td><td>$8</td><td>Amazon</td><td>The star cooks itself bare in under a minute — never run unmounted</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-wago" data-lo="15" data-hi="15" aria-label='WAGO 221 lever-nut assortment'></td><td><label for="d4-wago">WAGO 221 lever-nut assortment</label></td><td>1 pack</td><td>$15</td><td>Amazon, Home Depot</td><td>24 V power distribution — high current stays off the breadboard</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-fuse" data-lo="7" data-hi="7" aria-label='Inline fuse holder (5x20 mm) + T3.15AL250V slow-blow fuses'></td><td><label for="d4-fuse">Inline fuse holder (5×20 mm) + <strong>T3.15AL250V</strong> slow-blow fuses</label></td><td>1</td><td>$7</td><td>Amazon</td><td>Cheap insurance on the 24 V rail. <strong>Time-delay, not fast-acting.</strong> 3.15 A is the standard IEC value that <em>is</em> "3 A" — there is no 3.00 A in this family. Buy a few <strong>T4AL250V</strong> at the same time: that's the fuse you step to if you ever run 2× tape</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-buck" data-lo="7.95" data-hi="7.95" aria-label='Pololu D24V22F5 buck (24 V→5 V, 2.5 A)'></td><td><label for="d4-buck">Pololu D24V22F5 buck (24 V→5 V, 2.5 A)</label></td><td>1</td><td>$7.95</td><td><a href="https://www.pololu.com/product/2858">pololu.com/product/2858</a></td><td>Fixed 5 V, nothing to mis-adjust</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-wire" data-lo="20" data-hi="20" aria-label='10 kilohm resistors 1/4 W, 22 AWG solid-core signal wire, 18-20 AWG stranded for 24 V runs, extra breadboard'></td><td><label for="d4-wire">10 kΩ resistors <strong>¼ W</strong> · 22 AWG <strong>solid-core</strong> signal wire · 18–20 AWG <strong>stranded</strong> for 24 V runs · extra breadboard</label></td><td>—</td><td>$20</td><td>Amazon</td><td>Three jobs, and the wire is different for each. The 10 kΩ are the PicoBuck IN pulldowns — ~1 mW each, so ¼ W is 200× margin and the smaller body crowds the board less. Signal wire must be <strong>solid</strong> to hold in breadboard contacts. The 24 V feeds are <strong>stranded</strong> because they get handled. <strong>Correction to an earlier version of this row:</strong> it said a ULN output feeding a tape zone "carries amps, not milliamps." It does not. This build's seven zones share ~3.3 ft of 4.6 W/ft tape, so a zone is about <strong>90 mA</strong> — 24 AWG is fine for them. The number to respect is the ULN2803's own 500 mA per-channel ceiling</td></tr>
</tbody>
</table>
</div>
<p><button type="button" class="md-button" data-reset>Reset section</button> <button type="button" class="md-button" data-copy>Copy unchecked as shopping list</button></p>
</details>

<details open class="bom-section" data-section="d5" markdown="0">
<summary><strong><a href="../05-teach-it-to-aim/">Doc 5 · Per-room perception (~$120–320)</a></strong> <span class="bom-progress"></span></summary>
<div class="bom-scroll">
<table>
<thead><tr><th></th><th>Part</th><th>Qty</th><th>Est.</th><th>Where</th><th>Why</th></tr></thead>
<tbody>
<tr><td><input type="checkbox" class="bom-box" id="d5-camera" data-lo="80" data-hi="80" aria-label='PoE camera — Amcrest IP5M-T1179EW-AI-V3 (5 MP, 133° lens)'></td><td><label for="d5-camera">PoE camera — Amcrest IP5M-T1179EW-AI-V3 (5 MP, 133° lens)</label></td><td>1/room</td><td>$80</td><td><a href="https://www.amcrest.com">amcrest.com</a></td><td>The room's eyes — wide fixed lens, standard RTSP, one PoE cable, internet-isolated</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d5-camera-night" data-lo="185" data-hi="185" aria-label='Priority rooms: Loryta/Dahua IPC-T549M-ALED-S3 (full-color night vision)'></td><td><label for="d5-camera-night">Priority rooms: Loryta/Dahua IPC-T549M-ALED-S3 (full-color night vision) <span class="bom-optional">optional</span></label></td><td>opt.</td><td>$185</td><td><a href="https://empiretech01.com">empiretech01.com</a></td><td>Night matters — IR cameras output grayscale, degrading RGB-trained models</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d5-poe-switch" data-lo="150" data-hi="400" aria-label='PoE switch (8–16 port) + Cat6 runs'></td><td><label for="d5-poe-switch">PoE switch (8–16 port) + Cat6 runs</label></td><td>1/home</td><td>$150–400</td><td>Amazon</td><td>Cameras on their own VLAN with <strong>no internet route</strong> — privacy by construction</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d5-charuco" data-lo="10" data-hi="10" aria-label='ChArUco calibration board (print + mount on rigid backing)'></td><td><label for="d5-charuco">ChArUco calibration board (print + mount on rigid backing)</label></td><td>1</td><td>~$10</td><td>print it (<a href="https://calib.io">calib.io</a> generator)</td><td>Registers each camera to the room scan — rigid and flat matters</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d5-lidar-scan" aria-label='iPhone/iPad Pro with LiDAR (borrow one) + Polycam or Scaniverse app'></td><td><label for="d5-lidar-scan">iPhone/iPad Pro with LiDAR (borrow one) + Polycam or Scaniverse app</label></td><td>1</td><td>free–$</td><td>App Store</td><td>One-time room scan, ~1–3 cm accuracy — use Space Mode (LiDAR)</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d5-depth-cam" data-lo="359" data-hi="579" aria-label='Stereo depth camera — Orbbec Gemini 335L ($359) or Luxonis OAK-D Pro PoE ($579)'></td><td><label for="d5-depth-cam">Stereo depth camera — Orbbec Gemini 335L ($359) or Luxonis OAK-D Pro PoE ($579) <span class="bom-optional">optional, later</span></label></td><td>0–1</td><td>$359 / $579</td><td><a href="https://store.orbbec.com">store.orbbec.com</a>, <a href="https://shop.luxonis.com">shop.luxonis.com</a></td><td>Buy only after Tier-0 tracking measurably misses, not before</td></tr>
<tr class="bom-owned"><td>—</td><td>Already owned</td><td>—</td><td>—</td><td>—</td><td>RTX 6000 Blackwell box (runs all perception), the Doc 3/4 bench rig, Home Assistant + MQTT</td></tr>
</tbody>
</table>
</div>
<p><button type="button" class="md-button" data-reset>Reset section</button> <button type="button" class="md-button" data-copy>Copy unchecked as shopping list</button></p>
</details>

<details open class="bom-section" data-section="d8" markdown="0">
<summary><strong><a href="../08-build-the-fixture/">Doc 8 · Fixture build (~$105–120)</a></strong> <span class="bom-progress"></span></summary>
<div class="bom-scroll">
<table>
<thead><tr><th></th><th>Part</th><th>Qty</th><th>Est.</th><th>Where</th><th>Why</th></tr></thead>
<tbody>
<tr><td><input type="checkbox" class="bom-box" id="d8-protoboards" data-lo="15" data-hi="15" aria-label='Round prototyping PCB, 2.84" (72 mm), 593 plated holes'></td><td><label for="d8-protoboards">Round prototyping PCB, 2.84" (72 mm), 593 plated holes</label></td><td>1 pack of 4</td><td>$15</td><td><a href="https://www.etsy.com/listing/1785807382/vegetable-can-round-prototyping-pcb-w593">Etsy</a></td><td>All three get used — B1 power, B2 drivers, B3 logic — plus a spare. No power rails, which is why the trunk rule exists</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d8-irm" data-lo="25" data-hi="25" aria-label='Mean Well IRM-90-24ST (24 V · 3.75 A · potted · fanless · screw terminals)'></td><td><label for="d8-irm">Mean Well IRM-90-24ST (24 V · 3.75 A · potted · fanless · screw terminals)</label></td><td>1</td><td>~$25</td><td><a href="https://www.bravoelectro.com/irm-90-24.html">Bravo Electro</a>, DigiKey, Mouser</td><td>The fixture's PSU — ST (screw-terminal) on purpose: the plain IRM outspans a 72 mm round, so this one mounts to the body. Don't tin stranded ends before clamping them — solder cold-flows and the joint loosens</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d8-e26" data-lo="8" data-hi="12" aria-label='E26 socket-to-wire adapter (660 W rated, 18 AWG leads)'></td><td><label for="d8-e26">E26 socket-to-wire adapter (660 W rated, 18 AWG leads)</label></td><td>1 (+1 spare)</td><td>$8–12</td><td>Amazon, hardware store</td><td>The entire AC feed (~0.6–0.9 A at 120 V) — treat both leads as live; no wall dimmer on that circuit</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d8-headers" data-lo="7" data-hi="7" aria-label='Female pin-header socket strips, 2.54 mm break-away'></td><td><label for="d8-headers">Female pin-header socket strips, 2.54 mm break-away</label></td><td>1 kit</td><td>$7</td><td>Amazon</td><td>Socket every module — C6, both PCAs, CAN board, buck. Dead module = 10-second swap</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d8-jst" data-lo="12" data-hi="12" aria-label='JST-XH connector kit, pre-crimped leads (2/3/4-pin)'></td><td><label for="d8-jst">JST-XH connector kit, pre-crimped leads (2/3/4-pin)</label></td><td>1 kit</td><td>$12</td><td>Amazon</td><td>7 tape zones (4-pin) + the spot (3 ± pairs = six conductors, returns never shared). Solder the tails — never crimp</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d8-xt30" data-lo="8" data-hi="8" aria-label='XT30 connector pairs'></td><td><label for="d8-xt30">XT30 connector pairs</label></td><td>3 pairs</td><td>$8</td><td>Amazon</td><td>Motor power (one pair per motor) + the bench-feed break — JST-XH is a 3 A part; motor peaks hit 5–8 A</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d8-caps" data-lo="6" data-hi="6" aria-label='100 nF ceramic capacitors'></td><td><label for="d8-caps">100 nF ceramic capacitors</label></td><td>~10</td><td>$6</td><td>Amazon</td><td>One at every module's supply pins — long soldered rails need what the breadboard never did</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d8-bulk-cap" data-lo="3" data-hi="3" aria-label='Electrolytic bulk cap, 1000 µF / 35 V, low-ESR'></td><td><label for="d8-bulk-cap">Electrolytic bulk cap, 1000 µF / 35 V, low-ESR</label></td><td>1</td><td>$3</td><td>Amazon, DigiKey</td><td>Rides the motors' millisecond slew peaks. Start at 1000 µF — if the IRM hiccups at power-on, the cap is too big</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d8-standoffs" data-lo="9" data-hi="9" aria-label='Nylon M3 standoff kit'></td><td><label for="d8-standoffs">Nylon M3 standoff kit</label></td><td>1</td><td>$9</td><td>Amazon</td><td>Stack spacing + a vent path; nylon can't short against pad-side joints</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d8-bus-wire" data-lo="8" data-hi="8" aria-label='Bare tinned SOLID copper bus wire (bus bar wire), 16-18 AWG'></td><td><label for="d8-bus-wire">Bare tinned <strong>solid</strong> copper bus wire ("bus bar wire"), 16–18 AWG</label></td><td>1 roll</td><td>$8</td><td>Amazon</td><td>Becomes the two trunks — +24 V and ground. <strong>Solid, and bare.</strong> Stranded won't hold a rail; insulated just means stripping it at every junction. You <em>lay it along</em> a row of pads and solder each one — don't try to thread it, since 16 AWG is 1.3 mm against a ~1 mm hole. Keep the two rails on non-adjacent rows</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d8-strippers" data-lo="15" data-hi="15" aria-label='Wire strippers + flush cutters'></td><td><label for="d8-strippers">Wire strippers + flush cutters <span class="bom-optional">if not owned</span></label></td><td>1 each</td><td>~$15</td><td>Amazon</td><td>Never in an earlier BoM — the bench got by, but 100+ soldered joints won't</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d8-silicone-wire" data-lo="17" data-hi="17" aria-label='Silicone stranded wire, 24 AWG for signals and zone outputs plus 20 AWG for the 24 V feeds, and heat-shrink'></td><td><label for="d8-silicone-wire">Silicone <strong>stranded</strong> wire — 24 AWG signals <em>and</em> zone outputs, 20 AWG for the 24 V feeds — + heat-shrink <span class="bom-optional">if not owned</span></label></td><td>—</td><td>~$17</td><td>Amazon</td><td>Stranded is right here: it's all soldered, and the service loops across the pan/tilt joints want the floppiest wire available. Silicone insulation is worth paying for at 100+ joints — it won't shrink back and bare a neighbour when the iron brushes it. Get <strong>two gauges</strong>, but not for the reason an earlier version of this row gave: a tape zone is ~90 mA, so 24 AWG covers signals <em>and</em> zone outputs. The 20 AWG is for the <strong>24 V feeds</strong> that run the length of the fixture and carry every zone at once</td></tr>
<tr class="bom-owned"><td>—</td><td>Already owned</td><td>—</td><td>—</td><td>—</td><td>Everything else installs from Docs 3/4 — motors, C6, CAN board, PCAs, ULNs + sockets, PicoBuck, star + optics + heatsink, tape spool, Pololu buck, fuse holder + T3.15AL250V fuses (step to T4AL250V if you 2× the tape), screws, wire + 10 kΩ ¼ W stock. Retired: breadboards and WAGOs</td></tr>
</tbody>
</table>
</div>
<p><button type="button" class="md-button" data-reset>Reset section</button> <button type="button" class="md-button" data-copy>Copy unchecked as shopping list</button></p>
</details>

<style>
#bom-global { display: flex; align-items: center; gap: .8rem; margin: 1.2em 0; }
#bom-bar { flex: 1; height: .65rem; accent-color: var(--md-accent-fg-color); }
#bom-global-text { white-space: nowrap; font-size: .85em; color: var(--md-default-fg-color--light); }
.bom-section { margin: 1em 0; border: .05rem solid var(--md-default-fg-color--lightest); border-radius: .2rem; padding: .1rem .8rem .4rem; }
.bom-section summary { cursor: pointer; padding: .55rem 0; }
.bom-progress { font-size: .8em; color: var(--md-default-fg-color--light); margin-left: .4rem; }
.bom-scroll { overflow-x: auto; }
/* display:table overrides Material's inline-block for class-less tables —
   the whitespace text node before an inline-block table indents it and
   forces a phantom horizontal scroll */
.md-typeset .bom-scroll table { display: table; min-width: 46rem; width: 100%; }
/* Material's JS wraps tables in scrollwrap with -0.8rem bleed margins;
   inside .bom-scroll that just fakes 13px of overflow — neutralize it */
.md-typeset .bom-scroll .md-typeset__scrollwrap { margin: 0; overflow: visible; }
.md-typeset .bom-scroll .md-typeset__table { display: block; padding: 0; width: 100%; }
.bom-box { width: 1.15rem; height: 1.15rem; accent-color: var(--md-accent-fg-color); }
.bom-optional { font-size: .68em; border: .05rem solid var(--md-default-fg-color--lighter); border-radius: .6rem; padding: 0 .45em; vertical-align: middle; color: var(--md-default-fg-color--light); white-space: nowrap; }
.bom-owned td { color: var(--md-default-fg-color--light); }
input.bom-box:checked ~ * label, .bom-section tr:has(.bom-box:checked) label { text-decoration: line-through; opacity: .6; }
</style>
