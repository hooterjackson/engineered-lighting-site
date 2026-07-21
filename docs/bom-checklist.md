---
title: BoM Checklist
description: "Every purchase in the series in one interactive checklist — check items off as you order; progress persists in your browser."
hide:
  - toc
---

# Bill of Materials — interactive checklist

Every purchase in the series, in one list. Check items off as you order — state persists in your browser (nothing leaves your device). The full "Notes / traps" for each part live in the chapter BoM tables: [Doc 3](03-build-the-gimbal.md), [Doc 4](04-full-fixture-bench.md), [Doc 5](05-teach-it-to-aim.md).

!!! note "Prices verified July 2026"
    All prices in the series were verified in July 2026 — **re-check live prices when ordering**. This is the docs' own pre-purchase-recheck rule (see [Doc 7's risk register](07-building-the-software.md)).

<div id="bom-global">
  <progress id="bom-bar" max="30" value="0" aria-labelledby="bom-global-text"></progress>
  <span id="bom-global-text">0/30 items</span>
</div>

<details open class="bom-section" data-section="d3" markdown="0">
<summary><strong>Doc 3 · Gimbal (~$185–290)</strong> <span class="bom-progress"></span></summary>
<div class="bom-scroll">
<table>
<thead><tr><th></th><th>Part</th><th>Qty</th><th>Est.</th><th>Where</th><th>Why</th></tr></thead>
<tbody>
<tr><td><input type="checkbox" class="bom-box" id="d3-motors" data-lo="60" data-hi="120" aria-label='MyActuator RMD-L-4005-100-C (CAN version)'></td><td><label for="d3-motors">MyActuator RMD-L-4005-100-C (CAN version)</label></td><td>2</td><td>$60–120</td><td>Amazon, RobotShop, dingsmotionusa.com</td><td>The smart pan/tilt actuators — select the <strong>-C (CAN)</strong> variant, ask for the mating cable</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-esp32" data-lo="9" data-hi="15" aria-label='ESP32-C6 dev board (ESP32-C6-DevKitC-1)'></td><td><label for="d3-esp32">ESP32-C6 dev board (ESP32-C6-DevKitC-1)</label></td><td>1</td><td>$9–15</td><td>Amazon, Adafruit, DigiKey</td><td>Same chip as the fixture — everything learned transfers</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-can-xcvr" data-lo="8" data-hi="8" aria-label='SN65HVD230 CAN transceiver breakout (Waveshare "CAN Board")'></td><td><label for="d3-can-xcvr">SN65HVD230 CAN transceiver breakout (Waveshare "CAN Board")</label></td><td>2 (1+spare)</td><td>$8</td><td>Amazon</td><td>The CAN line driver — turns chip signals into the differential wire pair</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-resistors" data-lo="1" data-hi="1" aria-label='120 Ω resistors, ¼ W'></td><td><label for="d3-resistors">120 Ω resistors, ¼ W</label></td><td>few</td><td>$1</td><td>any resistor kit</td><td>CAN bus termination</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-psu" data-lo="45" data-hi="60" aria-label='Bench power supply, ≥3 A continuous, adjustable current limit'></td><td><label for="d3-psu">Bench power supply, ≥3 A continuous, adjustable current limit</label></td><td>1</td><td>$45–60</td><td>Amazon (any 30 V/5 A unit)</td><td>Powers the whole bench — the adjustable current limit is smoke insurance</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-multimeter" data-lo="20" data-hi="20" aria-label='Multimeter'></td><td><label for="d3-multimeter">Multimeter</label></td><td>1</td><td>$20</td><td>Amazon</td><td>Non-negotiable — polarity check before every first power-up</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-breadboard" data-lo="10" data-hi="10" aria-label='Breadboard + jumper wires'></td><td><label for="d3-breadboard">Breadboard + jumper wires</label></td><td>1 kit</td><td>$10</td><td>Amazon</td><td>Signals only — power never routes through it</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-usbc" aria-label='USB-C data cable'></td><td><label for="d3-usbc">USB-C data cable</label></td><td>1</td><td>—</td><td>you own one</td><td>Charge-only cables are a classic trap</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-screws" data-lo="10" data-hi="10" aria-label='M2.5 + M3 screw assortment'></td><td><label for="d3-screws">M2.5 + M3 screw assortment</label></td><td>1 box</td><td>$10</td><td>Amazon</td><td>Confirm sizes against the motor drawing</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-usb-can" data-lo="20" data-hi="25" aria-label='USB-to-CAN adapter ("CANable" or clone)'></td><td><label for="d3-usb-can">USB-to-CAN adapter ("CANable" or clone) <span class="bom-optional">optional</span></label></td><td>1</td><td>$20–25</td><td>Amazon</td><td>Lets your laptop eavesdrop on the bus — turns "nothing happens" into evidence</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-printing" data-lo="20" data-hi="20" aria-label='PETG filament + FDM printer access; 6804 or 608 bearings'></td><td><label for="d3-printing">PETG filament + FDM printer access; 6804 or 608 bearings</label></td><td>—</td><td>$20</td><td>Amazon / local makerspace</td><td>For stage 7's three frame parts — a makerspace or print service works</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-clamp" data-lo="10" data-hi="10" aria-label='C-clamp or small bench vise'></td><td><label for="d3-clamp">C-clamp or small bench vise</label></td><td>1</td><td>$10</td><td>hardware store</td><td>Clamps the bare motor before its first move</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d3-payload" aria-label='Payload stand-in: small flashlight or ~100 g weight'></td><td><label for="d3-payload">Payload stand-in: small flashlight or ~100 g weight</label></td><td>1</td><td>—</td><td>—</td><td>Real LED head comes from Doc 4</td></tr>
</tbody>
</table>
</div>
<p><button type="button" class="md-button" data-reset>Reset section</button> <button type="button" class="md-button" data-copy>Copy unchecked as shopping list</button></p>
</details>

<details open class="bom-section" data-section="d4" markdown="0">
<summary><strong>Doc 4 · LED bench (~$170–240)</strong> <span class="bom-progress"></span></summary>
<div class="bom-scroll">
<table>
<thead><tr><th></th><th>Part</th><th>Qty</th><th>Est.</th><th>Where</th><th>Why</th></tr></thead>
<tbody>
<tr><td><input type="checkbox" class="bom-box" id="d4-pca9685" data-lo="10" data-hi="30" aria-label='PCA9685 16-ch PWM breakout (Adafruit #815 or clone)'></td><td><label for="d4-pca9685">PCA9685 16-ch PWM breakout (Adafruit #815 or clone)</label></td><td>2</td><td>$30 / ~$10 clones</td><td>Adafruit, Amazon</td><td>The PWM expanders — bridge the A0 jumper on board #2 (address 0x41)</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-uln2803" data-lo="10" data-hi="10" aria-label='ULN2803A driver IC, 18-pin DIP (+ sockets)'></td><td><label for="d4-uln2803">ULN2803A driver IC, 18-pin DIP (+ sockets)</label></td><td>4 (+1 spare)</td><td>$10</td><td>Adafruit #970, Amazon</td><td>Lets 3.3 V dimmer signals switch the 24 V tape channels</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-soldering" data-lo="25" data-hi="40" aria-label='Soldering iron kit (iron, solder, flux, helping hands)'></td><td><label for="d4-soldering">Soldering iron kit (iron, solder, flux, helping hands)</label></td><td>1</td><td>$25–40</td><td>Amazon</td><td>For the tape-pad wires and the address jumper</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-picobuck" data-lo="17.5" data-hi="17.5" aria-label='SparkFun PicoBuck (PRT-13705)'></td><td><label for="d4-picobuck">SparkFun PicoBuck (PRT-13705)</label></td><td>1</td><td>$17.50</td><td>sparkfun.com</td><td>The spotlight's 3-channel constant-current driver, PWM-dimmable</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-tape" aria-label='Diode LED Valent X Tunable White spool (DI-24V-VLX-TW1865-016, 16.4 ft)'></td><td><label for="d4-tape">Diode LED Valent X Tunable White spool (DI-24V-VLX-TW1865-016, 16.4 ft)</label></td><td>1</td><td>dealer quote</td><td>diodeled.com dealers</td><td>7 short zones ≈ 3.3 ft used — one spool covers everything with spare</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-star-optics" data-lo="15" data-hi="25" aria-label='Cree 3-up star (XP-G2/XP-L) + Carclo 10507 narrow-spot optic (grab 10508/10509 too)'></td><td><label for="d4-star-optics">Cree 3-up star (XP-G2/XP-L) + Carclo 10507 narrow-spot optic (grab 10508/10509 too)</label></td><td>1</td><td>$15–25 (optics $3 ea)</td><td>LEDSupply</td><td>The spotlight payload — optics snap-swap in seconds, which <em>is</em> the beam-width experiment</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-heatsink" data-lo="8" data-hi="8" aria-label='Heatsink ≥2"×2" + thermal adhesive'></td><td><label for="d4-heatsink">Heatsink ≥2"×2" + thermal adhesive</label></td><td>1</td><td>$8</td><td>Amazon</td><td>The star cooks itself bare in under a minute — never run unmounted</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-wago" data-lo="15" data-hi="15" aria-label='WAGO 221 lever-nut assortment'></td><td><label for="d4-wago">WAGO 221 lever-nut assortment</label></td><td>1 pack</td><td>$15</td><td>Amazon, Home Depot</td><td>24 V power distribution — high current stays off the breadboard</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-fuse" data-lo="7" data-hi="7" aria-label='Inline fuse holder + 3 A slow-blow fuses'></td><td><label for="d4-fuse">Inline fuse holder + 3 A slow-blow fuses</label></td><td>1</td><td>$7</td><td>Amazon</td><td>Cheap insurance on the 24 V rail</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-buck" data-lo="7.95" data-hi="7.95" aria-label='Pololu D24V22F5 buck (24 V→5 V, 2.5 A)'></td><td><label for="d4-buck">Pololu D24V22F5 buck (24 V→5 V, 2.5 A)</label></td><td>1</td><td>$7.95</td><td>pololu.com/product/2858</td><td>Fixed 5 V, nothing to mis-adjust</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d4-wire" data-lo="20" data-hi="20" aria-label='10 kΩ resistors, 22–24 AWG signal wire, 18–20 AWG for 24 V runs, extra breadboard'></td><td><label for="d4-wire">10 kΩ resistors, 22–24 AWG signal wire, 18–20 AWG for 24 V runs, extra breadboard</label></td><td>—</td><td>$20</td><td>Amazon</td><td>Signal wiring on the breadboard; the heavier gauge carries the 24 V runs</td></tr>
</tbody>
</table>
</div>
<p><button type="button" class="md-button" data-reset>Reset section</button> <button type="button" class="md-button" data-copy>Copy unchecked as shopping list</button></p>
</details>

<details open class="bom-section" data-section="d5" markdown="0">
<summary><strong>Doc 5 · Per-room perception (~$120–320)</strong> <span class="bom-progress"></span></summary>
<div class="bom-scroll">
<table>
<thead><tr><th></th><th>Part</th><th>Qty</th><th>Est.</th><th>Where</th><th>Why</th></tr></thead>
<tbody>
<tr><td><input type="checkbox" class="bom-box" id="d5-camera" data-lo="80" data-hi="80" aria-label='PoE camera — Amcrest IP5M-T1179EW-AI-V3 (5 MP, 133° lens)'></td><td><label for="d5-camera">PoE camera — Amcrest IP5M-T1179EW-AI-V3 (5 MP, 133° lens)</label></td><td>1/room</td><td>$80</td><td>amcrest.com</td><td>The room's eyes — wide fixed lens, standard RTSP, one PoE cable, internet-isolated</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d5-camera-night" data-lo="185" data-hi="185" aria-label='Priority rooms: Loryta/Dahua IPC-T549M-ALED-S3 (full-color night vision)'></td><td><label for="d5-camera-night">Priority rooms: Loryta/Dahua IPC-T549M-ALED-S3 (full-color night vision) <span class="bom-optional">optional</span></label></td><td>opt.</td><td>$185</td><td>empiretech01.com</td><td>Night matters — IR cameras output grayscale, degrading RGB-trained models</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d5-poe-switch" data-lo="150" data-hi="400" aria-label='PoE switch (8–16 port) + Cat6 runs'></td><td><label for="d5-poe-switch">PoE switch (8–16 port) + Cat6 runs</label></td><td>1/home</td><td>$150–400</td><td>Amazon</td><td>Cameras on their own VLAN with <strong>no internet route</strong> — privacy by construction</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d5-charuco" data-lo="10" data-hi="10" aria-label='ChArUco calibration board (print + mount on rigid backing)'></td><td><label for="d5-charuco">ChArUco calibration board (print + mount on rigid backing)</label></td><td>1</td><td>~$10</td><td>print it (calib.io generator)</td><td>Registers each camera to the room scan — rigid and flat matters</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d5-lidar-scan" aria-label='iPhone/iPad Pro with LiDAR (borrow one) + Polycam or Scaniverse app'></td><td><label for="d5-lidar-scan">iPhone/iPad Pro with LiDAR (borrow one) + Polycam or Scaniverse app</label></td><td>1</td><td>free–$</td><td>App Store</td><td>One-time room scan, ~1–3 cm accuracy — use Space Mode (LiDAR)</td></tr>
<tr><td><input type="checkbox" class="bom-box" id="d5-depth-cam" data-lo="359" data-hi="579" aria-label='Stereo depth camera — Orbbec Gemini 335L ($359) or Luxonis OAK-D Pro PoE ($579)'></td><td><label for="d5-depth-cam">Stereo depth camera — Orbbec Gemini 335L ($359) or Luxonis OAK-D Pro PoE ($579) <span class="bom-optional">optional, later</span></label></td><td>0–1</td><td>$359 / $579</td><td>store.orbbec.com, shop.luxonis.com</td><td>Buy only after Tier-0 tracking measurably misses, not before</td></tr>
<tr class="bom-owned"><td>—</td><td>Already owned</td><td>—</td><td>—</td><td>—</td><td>RTX 6000 Blackwell box (runs all perception), the Doc 3/4 bench rig, Home Assistant + MQTT</td></tr>
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
