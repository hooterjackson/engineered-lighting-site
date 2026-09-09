---
title: 10 · The Flex Circuits
description: "Three passive flexible circuits that replace the fixture's hand-cut wiring: an arm ribbon and two cylinder bands that solder straight onto the LED strip ends. Routed, digitally checked, quoted — not built."
hide:
  - toc
---

# Doc 10 · The Flex Circuits — Wiring That Is Manufactured, Not Cut

**Engineered Lighting prototype series · September 2026**
The main board in [Doc 9](09-understand-the-pcb.md) now consolidates six radial LED sockets into one locking interface. Everything its
connectors reach — six ambient zones around a cylinder, three spotlight pairs, two motors — has so far
been wire, cut and stripped and soldered by hand, one conductor at a time. These three flexible
circuits replace most of that with something a factory makes to a drawing.

The latest main board groups all three spotlight pairs in **J9**, beside **J13 tilt**. Ordinary wires
connect those plugs to the unchanged static arm ribbon; **J12 pan** terminates separately. The wire
loop across the pan joint must accommodate 180 degrees in each direction. This is not a dynamic-flex
qualification. The six spotlight conductors remain separate, including their three LED-minus returns.

They are **passive**: copper, insulating film and solder pads. No components, no connectors fitted, no
firmware. That is the point. A flex circuit is a wiring harness that can be checked before it is
built, and reproduced identically the next time.

<!-- el-pcb:generated flex-boards start -->

<div class="el-pcb-scroll">
<table class="el-pcb-table">
<thead><tr>
<th>Circuit</th><th>Design</th><th>Size</th><th>Copper layers</th><th>Pads / contacts</th><th>What it does</th>
</tr></thead>
<tbody>
<tr><td>Arm ribbon</td><td><code>gimbal-static-v0.2</code></td><td>152.4 &times; 9.2 mm</td><td>1</td><td>70</td><td>Carries motor power, the CAN pair and three spotlight pairs along the arm. Static: it does not flex in service, and ordinary wires cross the moving joints.</td></tr>
<tr><td>Upper cylinder band</td><td><code>led-upper-v0.3</code></td><td>325.0 &times; 42.9 mm</td><td>2</td><td>126</td><td>Connects main J2 directly through a 30-contact insertion tail to six separately fused zones; 96 lands solder to strip ends.</td></tr>
<tr><td>Lower cylinder band</td><td><code>led-lower-v0.2</code></td><td>325.0 &times; 7.9 mm</td><td>2</td><td>96</td><td>The mirrored lower band, feeding the same six zones from the other side.</td></tr>
</tbody></table></div>

<!-- el-pcb:generated flex-boards end -->

!!! warning "Status as of 8 September 2026 — routed and checked, not ordered"

    All three designs pass native electrical-rule and design-rule checks, schematic parity, an
    independent pin-and-topology oracle, and a comparison of the exported manufacturing data against
    the native design. Those results are in the table under [what has been checked](#flex-validation).

    **Submitted to JLCPCB for engineering quotation; no payment or production release.** The unchanged static gimbal now has a PCBWay inquiry; the upper and lower LED flexes
    still await a compatible custom-stack submission route. The request is two of each
    circuit, six passive circuits in total, for two fixture prototypes. The manufacturer has not
    accepted the stack-up, coverlay, stiffeners or tolerances, and there has been **no physical
    qualification of any kind**: no fit coupon, no solder sample, no bend or motion testing.

    The central-interface main and upper flex v0.3 originally changed together. The later grouped-arm
    and branding changes affect only the main board; all three flex files remain byte-identical.
    One continuing fit risk affects whether these
    can be ordered at all, and it has its own section: [the alignment hold](#fit-hold).

??? info "Words this chapter uses — open this if any of them are new"

    | Word | What it means here |
    |---|---|
    | **Flex circuit** | A printed circuit on a thin plastic film instead of rigid fibreglass, so it can bend or wrap. |
    | **Polyimide (PI)** | The plastic film these are built on. Tough, heat-resistant, and the reason a flex can be soldered at all. |
    | **Coverlay** | The insulating film bonded over the copper, doing the job a solder mask does on a rigid board. Its artwork describes the **openings**, not the covering. |
    | **Adhesiveless core** | A film with the copper bonded directly to it, without a glue layer. Thinner and better behaved when bent. |
    | **Stiffener** | A local patch of extra material bonded where the circuit must *not* flex — under a soldered joint, for example. |
    | **ENIG** | Electroless nickel, immersion gold: a flat, solderable, non-tarnishing finish. |
    | **Rail** | One conductor carrying one thing. Here: `+24V`, and the three white channels `W`, `N` and `C`. |
    | **Developed length** | The length a wrapped band must be cut to so that it fits once curved. Longer than the cylinder's diameter suggests, and sensitive to what it wraps over. |
    | **Neutral radius** | The radius at which the circuit neither stretches nor compresses as it bends. It sets the developed length. |
    | **Bare circuit** | What is being quoted: the circuit alone, with nothing soldered to it. |

## The three circuits { #circuits }

Choose a circuit, then turn layers on and off. Hovering or tapping a pad shows what it carries;
clicking or tapping pins that summary so you can jump to its row in the connection table.

<div id="el-flex" class="el-pcb el-flex" data-base="../assets/pcb/flex-v0.2/" data-state="nojs" markdown="0">
<div class="el-flex-fallback">
<p><strong>The flex viewer needs JavaScript.</strong> Without it, the construction drawings below show each circuit, and every pad is listed in the <a href="#connections">connection tables</a>.</p>
</div>
</div>

??? info "What this view shows — and what it does not"

    These are the circuits' own **manufacturing layers**, rendered from the exported artwork: the
    copper, the coverlay openings and the printed legend. The colours are view colours chosen for
    contrast, not the colours of the finished part, which is specified as ENIG copper under yellow
    coverlay with a black legend.

    The small round markers are **pad locations from each circuit's connection table**, not the exact
    pad outlines — the real shapes are in the copper and coverlay layers underneath them. On the two
    cylinder bands, `F.Mask` and `B.Mask` are coverlay openings on a flex circuit, not solder-mask
    instructions for a rigid board.

    The arm ribbon has **one** physical copper layer. Its KiCad file shows an empty back-copper layer;
    that is an editor artefact and must never be ordered as a second layer.

## How the wiring is arranged { #arrangement }

### The arm ribbon

Ten conductors run the length of the arm in parallel lanes: motor `+24V` and `GND` on the two widest,
then the `CAN_H` / `CAN_L` pair, then three spotlight pairs. Seven termination banks are spaced along
it — the input `J1` plus six more — and the ribbon is **cut at the marked line** for whichever length
the arm needs. Cut lengths of 25.4, 50.8, 76.2, 101.6, 127.0 and 152.4 mm are all verified.

It is **static**. It does not flex while the fixture moves; ordinary wires with service loops cross
the moving joints, exactly as [Doc 1](01-how-we-got-here.md)'s rule requires. No repeated-motion
qualification is claimed, because none is needed and none has been done.

### The two cylinder bands

Each band wraps the cylinder and feeds six ambient zones, four rails each. The flat zone order is
Z4, Z5, Z6, Z1, Z2, Z3, which puts the seam between Z3 and Z4 and the input tab between Z6 and Z1 —
away from the common connection area, so one tab can feed three zones in each direction. All four
rails are **parallel-load interconnects**. They are never a series string, and the six fused feeds
from the main board stay separate the whole way.

Where a band meets an LED strip, the copper finger overlaps the strip's own end pad by a nominal
1 mm, with a 0.3 mm plated hole through the joint for solder access and anchoring. That hole is not a
connector socket.

### The tail is the plug { #insertion-tail }

Upper v0.3 (`0af25f8f`) replaces the v0.2 wire-solder tab. The **gold fingers on
the back face slide directly into main J2**; they are not pads for soldering wires.
The rigid main remains inside the cylinder while the flexible band wraps around
it. Keep the tail long enough to reach and bend gently: the overall upper board
height is 42.9 mm, including 35 mm above the band's upper edge. Do not crease the
stiffened insertion section or shorten it based on the old solder-pad picture.

The connector uses thirty 1 mm-pitch contacts, grouped in zone order
**4, 5, 6, 1, 2, 3**, with **+,+,W,N,C** in each group. The front stiffener is
opposite the back gold contacts. The required **0.30 ±0.05 mm is the total**
insertion thickness, including copper, film, plating, adhesive and support.
Finger gold requires at least 0.10 µm over nickel; ordinary 2 microinch ENIG is
not the same specification. Exact tip exposure, coverlay and stack need supplier
review. These are fabrication requirements, not measured dimensions.

The 96 strip-end lands and retained band routes did not change. Some outer strip
lands still look isolated when only the upper flex is viewed: the intended path
continues through matching rails inside the real strip, into a lower-band bridge
and up the next strip. The independent installed-CAM model reaches all 192 strip
ends on the correct 24 rails **only if those real through-rails exist**. Check them
unpowered; net labels alone cannot prove the assembled path.

An isolated current-tail/contact screen predicts a worst loop drop of **[0.1044 V](assets/pcb/flex-v0.2/tail-resistance-screen.json)**
under assumed 85 °C copper, 30 µm copper thickness, reduced conductor widths and
the stated connector resistance. It excludes the rest of the LED circuit and
does not predict heating. The 0.60 A positive / 0.20 A channel cases are stress
screens, not continuous operating ratings. Initial commissioning remains at most
0.50 A RMS per radial zone with local fuse air at most 85 °C, subject to measured
loads and PWM duty limits. Actual temperatures and currents are unknown.

## The alignment hold — still a fabrication gate { #fit-hold }

!!! trap "Print the template and dry-fit before anything is fabricated"

    The bands are positioned against a **modelled** cylinder: a neutral radius of 51.975 mm and a
    developed length of 324.97 mm, giving a 13.607 mm pitch across 24 strips. Underneath them sits
    1.1 mm double-sided adhesive whose datasheet allows a typical ±10 % thickness tolerance.

    That tolerance alone moves the far-end pad alignment by up to **0.346 mm** over half a turn,
    against a nominal lateral copper margin of **0.30 mm** each side — before any fabrication or
    assembly error is added. The measured strip is also 0.7 mm thick without a specified copper
    neutral radius or facet shape, so the real mounted curve is not established.

    Use the current upper **template-1-to-1.svg** from the downloads at actual size and check its scale.
    The retained A3 PDF is **historical v0.2**: its upper-tail drawing is obsolete and cannot qualify
    the new insertion fit. Its unchanged lower/arm portions remain reference material. Dry-fit
    every pad position on the actual compressed stack. **If the alignment misses, measure that stack
    and regenerate the geometry — do not stretch the circuit, and do not approve fabrication.** This
    is a known sensitivity, not a passed physical test.

## What the copper loses { #electrical }

The full-path table below is **historical**, calculated with upper v0.2 (`a5acd2a0`), not the new
insertion tail. The lower and arm geometry has not changed. Keep these earlier sensitivity results
for their reasoning; do not use their full-loop totals to qualify the current assembly. They include
assumed strip through-rails and joints, exclude the controller and external cabling, and are not measurements.

<!-- el-pcb:generated flex-electrical start -->

<div class="el-pcb-scroll">
<table class="el-pcb-table">
<thead><tr>
<th>Sensitivity case</th><th>Worst LED strip supply loss</th><th>Gimbal motor loop</th><th>Each spotlight pair</th><th>Assumed copper temperature</th><th>Assumed copper</th>
</tr></thead>
<tbody>
<tr><td>Historical upper v0.2: nominal model</td><td>0.342 V</td><td>0.094 V</td><td>0.091 V</td><td>20 &deg;C</td><td>35 &micro;m</td></tr>
<tr><td>Historical upper v0.2: hot/thin screening</td><td>0.583 V</td><td>0.137 V</td><td>0.133 V</td><td>85 &deg;C</td><td>30 &micro;m</td></tr>
<tr><td>Historical upper v0.2: high-resistance joints sensitivity</td><td>0.903 V</td><td>0.137 V</td><td>0.133 V</td><td>85 &deg;C</td><td>30 &micro;m</td></tr>
</tbody></table></div>

<!-- el-pcb:generated flex-electrical end -->

The project's wiring budget is 3 % of 24 V, which is **0.72 V for the whole path** — not just for
these circuits. The historical nominal case was inside it; the historical high-resistance-joint sensitivity
was not, which is the point of including it. A bad solder joint is a repair, not a tolerance to
design around: measure the loaded voltage and fix the joint.

Temperatures in that table are **inputs**, not predictions. Copper loss and actual bonded temperature
have to be checked during the first powered tests.

## Building and installing them { #install }

The engineering notes linked below summarize the current construction and open checks. The steps
that most affect whether this works:

- **Check the cut segment unpowered first.** Matching `+24V` / `W` / `N` / `C` labels must conduct end
  to end, and no component may encroach on the joint.
- **The outside view is authoritative** when wrapping. The lower band's artwork already points its
  fingers upward; do not mirror it to match the upper band.
- **Make a supported sample joint before committing.** Pre-tin lightly, support the finger, and check
  both interfaces wet without bridging.
- **Foam goes on band backs only**, stopping 0.7 mm short of the finger roots, and never under a strip
  body. Form gently: no crease, and no repeated bend at a via, a solder land or a stiffener edge.
- **Before power**, compare the delivered netlist and check every pair for isolation. After the strips
  are connected, expect 24 isolated zone rails. Use a low-voltage continuity test, not a high-voltage
  insulation tester, across populated LEDs. Confirm no rail reaches the aluminium.
- **Power one zone at a time**, then measure full-load voltage drop, current and temperature.

## Every pad, and what it carries { #connections }

Each row is one strip/ribbon solder pad or one of the thirty J100 insertion contacts. Selecting a pad in the viewer marks its row here; the summary's button
scrolls to it.

<!-- el-pcb:generated flex-connections start -->

<div class="el-pcb-index">
<details>
<summary>Arm ribbon <span class="el-pcb-count">70 pads</span></summary>
<div class="el-pcb-scroll">
<table class="el-pcb-table">
<thead><tr>
<th>Reference</th><th>Pin</th><th>Carries</th><th>Role</th><th>Position (mm)</th>
</tr></thead>
<tbody>
<tr data-flex-row="gimbal:J6:1"><td>J6</td><td>1</td><td>V24_MOTOR2</td><td></td><td>144.60, 20.95</td></tr>
<tr data-flex-row="gimbal:J6:2"><td>J6</td><td>2</td><td>GND</td><td></td><td>144.60, 22.35</td></tr>
<tr data-flex-row="gimbal:J6:3"><td>J6</td><td>3</td><td>CAN_H</td><td></td><td>144.60, 23.40</td></tr>
<tr data-flex-row="gimbal:J6:4"><td>J6</td><td>4</td><td>CAN_L</td><td></td><td>144.60, 24.10</td></tr>
<tr data-flex-row="gimbal:J6:5"><td>J6</td><td>5</td><td>SPOT1_LED_PLUS</td><td></td><td>144.60, 24.82</td></tr>
<tr data-flex-row="gimbal:J6:6"><td>J6</td><td>6</td><td>SPOT1_LED_MINUS</td><td></td><td>144.60, 25.57</td></tr>
<tr data-flex-row="gimbal:J6:7"><td>J6</td><td>7</td><td>SPOT2_LED_PLUS</td><td></td><td>144.60, 26.32</td></tr>
<tr data-flex-row="gimbal:J6:8"><td>J6</td><td>8</td><td>SPOT2_LED_MINUS</td><td></td><td>144.60, 27.07</td></tr>
<tr data-flex-row="gimbal:J6:9"><td>J6</td><td>9</td><td>SPOT3_LED_PLUS</td><td></td><td>144.60, 27.82</td></tr>
<tr data-flex-row="gimbal:J6:10"><td>J6</td><td>10</td><td>SPOT3_LED_MINUS</td><td></td><td>144.60, 28.57</td></tr>
<tr data-flex-row="gimbal:J3:1"><td>J3</td><td>1</td><td>V24_MOTOR2</td><td></td><td>68.40, 20.95</td></tr>
<tr data-flex-row="gimbal:J3:2"><td>J3</td><td>2</td><td>GND</td><td></td><td>68.40, 22.35</td></tr>
<tr data-flex-row="gimbal:J3:3"><td>J3</td><td>3</td><td>CAN_H</td><td></td><td>68.40, 23.40</td></tr>
<tr data-flex-row="gimbal:J3:4"><td>J3</td><td>4</td><td>CAN_L</td><td></td><td>68.40, 24.10</td></tr>
<tr data-flex-row="gimbal:J3:5"><td>J3</td><td>5</td><td>SPOT1_LED_PLUS</td><td></td><td>68.40, 24.82</td></tr>
<tr data-flex-row="gimbal:J3:6"><td>J3</td><td>6</td><td>SPOT1_LED_MINUS</td><td></td><td>68.40, 25.57</td></tr>
<tr data-flex-row="gimbal:J3:7"><td>J3</td><td>7</td><td>SPOT2_LED_PLUS</td><td></td><td>68.40, 26.32</td></tr>
<tr data-flex-row="gimbal:J3:8"><td>J3</td><td>8</td><td>SPOT2_LED_MINUS</td><td></td><td>68.40, 27.07</td></tr>
<tr data-flex-row="gimbal:J3:9"><td>J3</td><td>9</td><td>SPOT3_LED_PLUS</td><td></td><td>68.40, 27.82</td></tr>
<tr data-flex-row="gimbal:J3:10"><td>J3</td><td>10</td><td>SPOT3_LED_MINUS</td><td></td><td>68.40, 28.57</td></tr>
<tr data-flex-row="gimbal:J2:1"><td>J2</td><td>1</td><td>V24_MOTOR2</td><td></td><td>43.00, 20.95</td></tr>
<tr data-flex-row="gimbal:J2:2"><td>J2</td><td>2</td><td>GND</td><td></td><td>43.00, 22.35</td></tr>
<tr data-flex-row="gimbal:J2:3"><td>J2</td><td>3</td><td>CAN_H</td><td></td><td>43.00, 23.40</td></tr>
<tr data-flex-row="gimbal:J2:4"><td>J2</td><td>4</td><td>CAN_L</td><td></td><td>43.00, 24.10</td></tr>
<tr data-flex-row="gimbal:J2:5"><td>J2</td><td>5</td><td>SPOT1_LED_PLUS</td><td></td><td>43.00, 24.82</td></tr>
<tr data-flex-row="gimbal:J2:6"><td>J2</td><td>6</td><td>SPOT1_LED_MINUS</td><td></td><td>43.00, 25.57</td></tr>
<tr data-flex-row="gimbal:J2:7"><td>J2</td><td>7</td><td>SPOT2_LED_PLUS</td><td></td><td>43.00, 26.32</td></tr>
<tr data-flex-row="gimbal:J2:8"><td>J2</td><td>8</td><td>SPOT2_LED_MINUS</td><td></td><td>43.00, 27.07</td></tr>
<tr data-flex-row="gimbal:J2:9"><td>J2</td><td>9</td><td>SPOT3_LED_PLUS</td><td></td><td>43.00, 27.82</td></tr>
<tr data-flex-row="gimbal:J2:10"><td>J2</td><td>10</td><td>SPOT3_LED_MINUS</td><td></td><td>43.00, 28.57</td></tr>
<tr data-flex-row="gimbal:J4:1"><td>J4</td><td>1</td><td>V24_MOTOR2</td><td></td><td>93.80, 20.95</td></tr>
<tr data-flex-row="gimbal:J4:2"><td>J4</td><td>2</td><td>GND</td><td></td><td>93.80, 22.35</td></tr>
<tr data-flex-row="gimbal:J4:3"><td>J4</td><td>3</td><td>CAN_H</td><td></td><td>93.80, 23.40</td></tr>
<tr data-flex-row="gimbal:J4:4"><td>J4</td><td>4</td><td>CAN_L</td><td></td><td>93.80, 24.10</td></tr>
<tr data-flex-row="gimbal:J4:5"><td>J4</td><td>5</td><td>SPOT1_LED_PLUS</td><td></td><td>93.80, 24.82</td></tr>
<tr data-flex-row="gimbal:J4:6"><td>J4</td><td>6</td><td>SPOT1_LED_MINUS</td><td></td><td>93.80, 25.57</td></tr>
<tr data-flex-row="gimbal:J4:7"><td>J4</td><td>7</td><td>SPOT2_LED_PLUS</td><td></td><td>93.80, 26.32</td></tr>
<tr data-flex-row="gimbal:J4:8"><td>J4</td><td>8</td><td>SPOT2_LED_MINUS</td><td></td><td>93.80, 27.07</td></tr>
<tr data-flex-row="gimbal:J4:9"><td>J4</td><td>9</td><td>SPOT3_LED_PLUS</td><td></td><td>93.80, 27.82</td></tr>
<tr data-flex-row="gimbal:J4:10"><td>J4</td><td>10</td><td>SPOT3_LED_MINUS</td><td></td><td>93.80, 28.57</td></tr>
<tr data-flex-row="gimbal:J5:1"><td>J5</td><td>1</td><td>V24_MOTOR2</td><td></td><td>119.20, 20.95</td></tr>
<tr data-flex-row="gimbal:J5:2"><td>J5</td><td>2</td><td>GND</td><td></td><td>119.20, 22.35</td></tr>
<tr data-flex-row="gimbal:J5:3"><td>J5</td><td>3</td><td>CAN_H</td><td></td><td>119.20, 23.40</td></tr>
<tr data-flex-row="gimbal:J5:4"><td>J5</td><td>4</td><td>CAN_L</td><td></td><td>119.20, 24.10</td></tr>
<tr data-flex-row="gimbal:J5:5"><td>J5</td><td>5</td><td>SPOT1_LED_PLUS</td><td></td><td>119.20, 24.82</td></tr>
<tr data-flex-row="gimbal:J5:6"><td>J5</td><td>6</td><td>SPOT1_LED_MINUS</td><td></td><td>119.20, 25.57</td></tr>
<tr data-flex-row="gimbal:J5:7"><td>J5</td><td>7</td><td>SPOT2_LED_PLUS</td><td></td><td>119.20, 26.32</td></tr>
<tr data-flex-row="gimbal:J5:8"><td>J5</td><td>8</td><td>SPOT2_LED_MINUS</td><td></td><td>119.20, 27.07</td></tr>
<tr data-flex-row="gimbal:J5:9"><td>J5</td><td>9</td><td>SPOT3_LED_PLUS</td><td></td><td>119.20, 27.82</td></tr>
<tr data-flex-row="gimbal:J5:10"><td>J5</td><td>10</td><td>SPOT3_LED_MINUS</td><td></td><td>119.20, 28.57</td></tr>
<tr data-flex-row="gimbal:J7:1"><td>J7</td><td>1</td><td>V24_MOTOR2</td><td></td><td>170.00, 20.95</td></tr>
<tr data-flex-row="gimbal:J7:2"><td>J7</td><td>2</td><td>GND</td><td></td><td>170.00, 22.35</td></tr>
<tr data-flex-row="gimbal:J7:3"><td>J7</td><td>3</td><td>CAN_H</td><td></td><td>170.00, 23.40</td></tr>
<tr data-flex-row="gimbal:J7:4"><td>J7</td><td>4</td><td>CAN_L</td><td></td><td>170.00, 24.10</td></tr>
<tr data-flex-row="gimbal:J7:5"><td>J7</td><td>5</td><td>SPOT1_LED_PLUS</td><td></td><td>170.00, 24.82</td></tr>
<tr data-flex-row="gimbal:J7:6"><td>J7</td><td>6</td><td>SPOT1_LED_MINUS</td><td></td><td>170.00, 25.57</td></tr>
<tr data-flex-row="gimbal:J7:7"><td>J7</td><td>7</td><td>SPOT2_LED_PLUS</td><td></td><td>170.00, 26.32</td></tr>
<tr data-flex-row="gimbal:J7:8"><td>J7</td><td>8</td><td>SPOT2_LED_MINUS</td><td></td><td>170.00, 27.07</td></tr>
<tr data-flex-row="gimbal:J7:9"><td>J7</td><td>9</td><td>SPOT3_LED_PLUS</td><td></td><td>170.00, 27.82</td></tr>
<tr data-flex-row="gimbal:J7:10"><td>J7</td><td>10</td><td>SPOT3_LED_MINUS</td><td></td><td>170.00, 28.57</td></tr>
<tr data-flex-row="gimbal:J1:1"><td>J1</td><td>1</td><td>V24_MOTOR2</td><td></td><td>23.00, 20.95</td></tr>
<tr data-flex-row="gimbal:J1:2"><td>J1</td><td>2</td><td>GND</td><td></td><td>23.00, 22.35</td></tr>
<tr data-flex-row="gimbal:J1:3"><td>J1</td><td>3</td><td>CAN_H</td><td></td><td>23.00, 23.40</td></tr>
<tr data-flex-row="gimbal:J1:4"><td>J1</td><td>4</td><td>CAN_L</td><td></td><td>23.00, 24.10</td></tr>
<tr data-flex-row="gimbal:J1:5"><td>J1</td><td>5</td><td>SPOT1_LED_PLUS</td><td></td><td>23.00, 24.82</td></tr>
<tr data-flex-row="gimbal:J1:6"><td>J1</td><td>6</td><td>SPOT1_LED_MINUS</td><td></td><td>23.00, 25.57</td></tr>
<tr data-flex-row="gimbal:J1:7"><td>J1</td><td>7</td><td>SPOT2_LED_PLUS</td><td></td><td>23.00, 26.32</td></tr>
<tr data-flex-row="gimbal:J1:8"><td>J1</td><td>8</td><td>SPOT2_LED_MINUS</td><td></td><td>23.00, 27.07</td></tr>
<tr data-flex-row="gimbal:J1:9"><td>J1</td><td>9</td><td>SPOT3_LED_PLUS</td><td></td><td>23.00, 27.82</td></tr>
<tr data-flex-row="gimbal:J1:10"><td>J1</td><td>10</td><td>SPOT3_LED_MINUS</td><td></td><td>23.00, 28.57</td></tr>
</tbody></table></div>
</details>
<details>
<summary>Upper cylinder band <span class="el-pcb-count">126 pads</span></summary>
<div class="el-pcb-scroll">
<table class="el-pcb-table">
<thead><tr>
<th>Reference</th><th>Pin</th><th>Carries</th><th>Role</th><th>Position (mm)</th>
</tr></thead>
<tbody>
<tr data-flex-row="upper:J43:1"><td>J43</td><td>1</td><td>Z4_T23_24V</td><td>strip solder overlap</td><td>48.39, 47.20</td></tr>
<tr data-flex-row="upper:J43:2"><td>J43</td><td>2</td><td>Z4_T23_W</td><td>strip solder overlap</td><td>50.42, 47.20</td></tr>
<tr data-flex-row="upper:J43:3"><td>J43</td><td>3</td><td>Z4_T23_N</td><td>strip solder overlap</td><td>56.01, 47.20</td></tr>
<tr data-flex-row="upper:J43:4"><td>J43</td><td>4</td><td>Z4_T23_C</td><td>strip solder overlap</td><td>58.04, 47.20</td></tr>
<tr data-flex-row="upper:J64:1"><td>J64</td><td>1</td><td>ZONE6_24V</td><td>strip solder overlap</td><td>170.85, 47.20</td></tr>
<tr data-flex-row="upper:J64:2"><td>J64</td><td>2</td><td>ZONE6_W</td><td>strip solder overlap</td><td>172.89, 47.20</td></tr>
<tr data-flex-row="upper:J64:3"><td>J64</td><td>3</td><td>ZONE6_N</td><td>strip solder overlap</td><td>178.48, 47.20</td></tr>
<tr data-flex-row="upper:J64:4"><td>J64</td><td>4</td><td>ZONE6_C</td><td>strip solder overlap</td><td>180.51, 47.20</td></tr>
<tr data-flex-row="upper:J41:1"><td>J41</td><td>1</td><td>unconnected-(J41-Pin_1-Pad1)</td><td>strip solder overlap</td><td>21.18, 47.20</td></tr>
<tr data-flex-row="upper:J41:2"><td>J41</td><td>2</td><td>unconnected-(J41-Pin_2-Pad2)</td><td>strip solder overlap</td><td>23.21, 47.20</td></tr>
<tr data-flex-row="upper:J41:3"><td>J41</td><td>3</td><td>unconnected-(J41-Pin_3-Pad3)</td><td>strip solder overlap</td><td>28.80, 47.20</td></tr>
<tr data-flex-row="upper:J41:4"><td>J41</td><td>4</td><td>unconnected-(J41-Pin_4-Pad4)</td><td>strip solder overlap</td><td>30.83, 47.20</td></tr>
<tr data-flex-row="upper:J12:1"><td>J12</td><td>1</td><td>Z1_T23_24V</td><td>strip solder overlap</td><td>198.07, 47.20</td></tr>
<tr data-flex-row="upper:J12:2"><td>J12</td><td>2</td><td>Z1_T23_W</td><td>strip solder overlap</td><td>200.10, 47.20</td></tr>
<tr data-flex-row="upper:J12:3"><td>J12</td><td>3</td><td>Z1_T23_N</td><td>strip solder overlap</td><td>205.69, 47.20</td></tr>
<tr data-flex-row="upper:J12:4"><td>J12</td><td>4</td><td>Z1_T23_C</td><td>strip solder overlap</td><td>207.72, 47.20</td></tr>
<tr data-flex-row="upper:J14:1"><td>J14</td><td>1</td><td>unconnected-(J14-Pin_1-Pad1)</td><td>strip solder overlap</td><td>225.28, 47.20</td></tr>
<tr data-flex-row="upper:J14:2"><td>J14</td><td>2</td><td>unconnected-(J14-Pin_2-Pad2)</td><td>strip solder overlap</td><td>227.31, 47.20</td></tr>
<tr data-flex-row="upper:J14:3"><td>J14</td><td>3</td><td>unconnected-(J14-Pin_3-Pad3)</td><td>strip solder overlap</td><td>232.90, 47.20</td></tr>
<tr data-flex-row="upper:J14:4"><td>J14</td><td>4</td><td>unconnected-(J14-Pin_4-Pad4)</td><td>strip solder overlap</td><td>234.94, 47.20</td></tr>
<tr data-flex-row="upper:J21:1"><td>J21</td><td>1</td><td>ZONE2_24V</td><td>strip solder overlap</td><td>238.89, 47.20</td></tr>
<tr data-flex-row="upper:J21:2"><td>J21</td><td>2</td><td>ZONE2_W</td><td>strip solder overlap</td><td>240.92, 47.20</td></tr>
<tr data-flex-row="upper:J21:3"><td>J21</td><td>3</td><td>ZONE2_N</td><td>strip solder overlap</td><td>246.51, 47.20</td></tr>
<tr data-flex-row="upper:J21:4"><td>J21</td><td>4</td><td>ZONE2_C</td><td>strip solder overlap</td><td>248.54, 47.20</td></tr>
<tr data-flex-row="upper:J51:1"><td>J51</td><td>1</td><td>unconnected-(J51-Pin_1-Pad1)</td><td>strip solder overlap</td><td>75.61, 47.20</td></tr>
<tr data-flex-row="upper:J51:2"><td>J51</td><td>2</td><td>unconnected-(J51-Pin_2-Pad2)</td><td>strip solder overlap</td><td>77.64, 47.20</td></tr>
<tr data-flex-row="upper:J51:3"><td>J51</td><td>3</td><td>unconnected-(J51-Pin_3-Pad3)</td><td>strip solder overlap</td><td>83.23, 47.20</td></tr>
<tr data-flex-row="upper:J51:4"><td>J51</td><td>4</td><td>unconnected-(J51-Pin_4-Pad4)</td><td>strip solder overlap</td><td>85.26, 47.20</td></tr>
<tr data-flex-row="upper:J52:1"><td>J52</td><td>1</td><td>Z5_T23_24V</td><td>strip solder overlap</td><td>89.21, 47.20</td></tr>
<tr data-flex-row="upper:J52:2"><td>J52</td><td>2</td><td>Z5_T23_W</td><td>strip solder overlap</td><td>91.24, 47.20</td></tr>
<tr data-flex-row="upper:J52:3"><td>J52</td><td>3</td><td>Z5_T23_N</td><td>strip solder overlap</td><td>96.83, 47.20</td></tr>
<tr data-flex-row="upper:J52:4"><td>J52</td><td>4</td><td>Z5_T23_C</td><td>strip solder overlap</td><td>98.87, 47.20</td></tr>
<tr data-flex-row="upper:J11:1"><td>J11</td><td>1</td><td>ZONE1_24V</td><td>strip solder overlap</td><td>184.46, 47.20</td></tr>
<tr data-flex-row="upper:J11:2"><td>J11</td><td>2</td><td>ZONE1_W</td><td>strip solder overlap</td><td>186.49, 47.20</td></tr>
<tr data-flex-row="upper:J11:3"><td>J11</td><td>3</td><td>ZONE1_N</td><td>strip solder overlap</td><td>192.08, 47.20</td></tr>
<tr data-flex-row="upper:J11:4"><td>J11</td><td>4</td><td>ZONE1_C</td><td>strip solder overlap</td><td>194.11, 47.20</td></tr>
<tr data-flex-row="upper:J54:1"><td>J54</td><td>1</td><td>ZONE5_24V</td><td>strip solder overlap</td><td>116.43, 47.20</td></tr>
<tr data-flex-row="upper:J54:2"><td>J54</td><td>2</td><td>ZONE5_W</td><td>strip solder overlap</td><td>118.46, 47.20</td></tr>
<tr data-flex-row="upper:J54:3"><td>J54</td><td>3</td><td>ZONE5_N</td><td>strip solder overlap</td><td>124.05, 47.20</td></tr>
<tr data-flex-row="upper:J54:4"><td>J54</td><td>4</td><td>ZONE5_C</td><td>strip solder overlap</td><td>126.08, 47.20</td></tr>
<tr data-flex-row="upper:J42:1"><td>J42</td><td>1</td><td>Z4_T23_24V</td><td>strip solder overlap</td><td>34.78, 47.20</td></tr>
<tr data-flex-row="upper:J42:2"><td>J42</td><td>2</td><td>Z4_T23_W</td><td>strip solder overlap</td><td>36.82, 47.20</td></tr>
<tr data-flex-row="upper:J42:3"><td>J42</td><td>3</td><td>Z4_T23_N</td><td>strip solder overlap</td><td>42.40, 47.20</td></tr>
<tr data-flex-row="upper:J42:4"><td>J42</td><td>4</td><td>Z4_T23_C</td><td>strip solder overlap</td><td>44.44, 47.20</td></tr>
<tr data-flex-row="upper:J100:1"><td>J100</td><td>1</td><td>ZONE4_24V</td><td>B-side insertion contact; no solder</td><td>167.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:2"><td>J100</td><td>2</td><td>ZONE4_24V</td><td>B-side insertion contact; no solder</td><td>168.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:3"><td>J100</td><td>3</td><td>ZONE4_W</td><td>B-side insertion contact; no solder</td><td>169.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:4"><td>J100</td><td>4</td><td>ZONE4_N</td><td>B-side insertion contact; no solder</td><td>170.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:5"><td>J100</td><td>5</td><td>ZONE4_C</td><td>B-side insertion contact; no solder</td><td>171.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:6"><td>J100</td><td>6</td><td>ZONE5_24V</td><td>B-side insertion contact; no solder</td><td>172.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:7"><td>J100</td><td>7</td><td>ZONE5_24V</td><td>B-side insertion contact; no solder</td><td>173.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:8"><td>J100</td><td>8</td><td>ZONE5_W</td><td>B-side insertion contact; no solder</td><td>174.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:9"><td>J100</td><td>9</td><td>ZONE5_N</td><td>B-side insertion contact; no solder</td><td>175.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:10"><td>J100</td><td>10</td><td>ZONE5_C</td><td>B-side insertion contact; no solder</td><td>176.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:11"><td>J100</td><td>11</td><td>ZONE6_24V</td><td>B-side insertion contact; no solder</td><td>177.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:12"><td>J100</td><td>12</td><td>ZONE6_24V</td><td>B-side insertion contact; no solder</td><td>178.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:13"><td>J100</td><td>13</td><td>ZONE6_W</td><td>B-side insertion contact; no solder</td><td>179.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:14"><td>J100</td><td>14</td><td>ZONE6_N</td><td>B-side insertion contact; no solder</td><td>180.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:15"><td>J100</td><td>15</td><td>ZONE6_C</td><td>B-side insertion contact; no solder</td><td>181.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:16"><td>J100</td><td>16</td><td>ZONE1_24V</td><td>B-side insertion contact; no solder</td><td>182.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:17"><td>J100</td><td>17</td><td>ZONE1_24V</td><td>B-side insertion contact; no solder</td><td>183.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:18"><td>J100</td><td>18</td><td>ZONE1_W</td><td>B-side insertion contact; no solder</td><td>184.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:19"><td>J100</td><td>19</td><td>ZONE1_N</td><td>B-side insertion contact; no solder</td><td>185.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:20"><td>J100</td><td>20</td><td>ZONE1_C</td><td>B-side insertion contact; no solder</td><td>186.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:21"><td>J100</td><td>21</td><td>ZONE2_24V</td><td>B-side insertion contact; no solder</td><td>187.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:22"><td>J100</td><td>22</td><td>ZONE2_24V</td><td>B-side insertion contact; no solder</td><td>188.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:23"><td>J100</td><td>23</td><td>ZONE2_W</td><td>B-side insertion contact; no solder</td><td>189.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:24"><td>J100</td><td>24</td><td>ZONE2_N</td><td>B-side insertion contact; no solder</td><td>190.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:25"><td>J100</td><td>25</td><td>ZONE2_C</td><td>B-side insertion contact; no solder</td><td>191.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:26"><td>J100</td><td>26</td><td>ZONE3_24V</td><td>B-side insertion contact; no solder</td><td>192.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:27"><td>J100</td><td>27</td><td>ZONE3_24V</td><td>B-side insertion contact; no solder</td><td>193.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:28"><td>J100</td><td>28</td><td>ZONE3_W</td><td>B-side insertion contact; no solder</td><td>194.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:29"><td>J100</td><td>29</td><td>ZONE3_N</td><td>B-side insertion contact; no solder</td><td>195.98, 6.75</td></tr>
<tr data-flex-row="upper:J100:30"><td>J100</td><td>30</td><td>ZONE3_C</td><td>B-side insertion contact; no solder</td><td>196.98, 6.75</td></tr>
<tr data-flex-row="upper:J22:1"><td>J22</td><td>1</td><td>Z2_T23_24V</td><td>strip solder overlap</td><td>252.50, 47.20</td></tr>
<tr data-flex-row="upper:J22:2"><td>J22</td><td>2</td><td>Z2_T23_W</td><td>strip solder overlap</td><td>254.53, 47.20</td></tr>
<tr data-flex-row="upper:J22:3"><td>J22</td><td>3</td><td>Z2_T23_N</td><td>strip solder overlap</td><td>260.12, 47.20</td></tr>
<tr data-flex-row="upper:J22:4"><td>J22</td><td>4</td><td>Z2_T23_C</td><td>strip solder overlap</td><td>262.15, 47.20</td></tr>
<tr data-flex-row="upper:J34:1"><td>J34</td><td>1</td><td>unconnected-(J34-Pin_1-Pad1)</td><td>strip solder overlap</td><td>334.14, 47.20</td></tr>
<tr data-flex-row="upper:J34:2"><td>J34</td><td>2</td><td>unconnected-(J34-Pin_2-Pad2)</td><td>strip solder overlap</td><td>336.17, 47.20</td></tr>
<tr data-flex-row="upper:J34:3"><td>J34</td><td>3</td><td>unconnected-(J34-Pin_3-Pad3)</td><td>strip solder overlap</td><td>341.76, 47.20</td></tr>
<tr data-flex-row="upper:J34:4"><td>J34</td><td>4</td><td>unconnected-(J34-Pin_4-Pad4)</td><td>strip solder overlap</td><td>343.79, 47.20</td></tr>
<tr data-flex-row="upper:J44:1"><td>J44</td><td>1</td><td>ZONE4_24V</td><td>strip solder overlap</td><td>62.00, 47.20</td></tr>
<tr data-flex-row="upper:J44:2"><td>J44</td><td>2</td><td>ZONE4_W</td><td>strip solder overlap</td><td>64.03, 47.20</td></tr>
<tr data-flex-row="upper:J44:3"><td>J44</td><td>3</td><td>ZONE4_N</td><td>strip solder overlap</td><td>69.62, 47.20</td></tr>
<tr data-flex-row="upper:J44:4"><td>J44</td><td>4</td><td>ZONE4_C</td><td>strip solder overlap</td><td>71.65, 47.20</td></tr>
<tr data-flex-row="upper:J32:1"><td>J32</td><td>1</td><td>Z3_T23_24V</td><td>strip solder overlap</td><td>306.92, 47.20</td></tr>
<tr data-flex-row="upper:J32:2"><td>J32</td><td>2</td><td>Z3_T23_W</td><td>strip solder overlap</td><td>308.96, 47.20</td></tr>
<tr data-flex-row="upper:J32:3"><td>J32</td><td>3</td><td>Z3_T23_N</td><td>strip solder overlap</td><td>314.55, 47.20</td></tr>
<tr data-flex-row="upper:J32:4"><td>J32</td><td>4</td><td>Z3_T23_C</td><td>strip solder overlap</td><td>316.58, 47.20</td></tr>
<tr data-flex-row="upper:J53:1"><td>J53</td><td>1</td><td>Z5_T23_24V</td><td>strip solder overlap</td><td>102.82, 47.20</td></tr>
<tr data-flex-row="upper:J53:2"><td>J53</td><td>2</td><td>Z5_T23_W</td><td>strip solder overlap</td><td>104.85, 47.20</td></tr>
<tr data-flex-row="upper:J53:3"><td>J53</td><td>3</td><td>Z5_T23_N</td><td>strip solder overlap</td><td>110.44, 47.20</td></tr>
<tr data-flex-row="upper:J53:4"><td>J53</td><td>4</td><td>Z5_T23_C</td><td>strip solder overlap</td><td>112.47, 47.20</td></tr>
<tr data-flex-row="upper:J23:1"><td>J23</td><td>1</td><td>Z2_T23_24V</td><td>strip solder overlap</td><td>266.10, 47.20</td></tr>
<tr data-flex-row="upper:J23:2"><td>J23</td><td>2</td><td>Z2_T23_W</td><td>strip solder overlap</td><td>268.14, 47.20</td></tr>
<tr data-flex-row="upper:J23:3"><td>J23</td><td>3</td><td>Z2_T23_N</td><td>strip solder overlap</td><td>273.72, 47.20</td></tr>
<tr data-flex-row="upper:J23:4"><td>J23</td><td>4</td><td>Z2_T23_C</td><td>strip solder overlap</td><td>275.76, 47.20</td></tr>
<tr data-flex-row="upper:J62:1"><td>J62</td><td>1</td><td>Z6_T23_24V</td><td>strip solder overlap</td><td>143.64, 47.20</td></tr>
<tr data-flex-row="upper:J62:2"><td>J62</td><td>2</td><td>Z6_T23_W</td><td>strip solder overlap</td><td>145.67, 47.20</td></tr>
<tr data-flex-row="upper:J62:3"><td>J62</td><td>3</td><td>Z6_T23_N</td><td>strip solder overlap</td><td>151.26, 47.20</td></tr>
<tr data-flex-row="upper:J62:4"><td>J62</td><td>4</td><td>Z6_T23_C</td><td>strip solder overlap</td><td>153.29, 47.20</td></tr>
<tr data-flex-row="upper:J24:1"><td>J24</td><td>1</td><td>unconnected-(J24-Pin_1-Pad1)</td><td>strip solder overlap</td><td>279.71, 47.20</td></tr>
<tr data-flex-row="upper:J24:2"><td>J24</td><td>2</td><td>unconnected-(J24-Pin_2-Pad2)</td><td>strip solder overlap</td><td>281.74, 47.20</td></tr>
<tr data-flex-row="upper:J24:3"><td>J24</td><td>3</td><td>unconnected-(J24-Pin_3-Pad3)</td><td>strip solder overlap</td><td>287.33, 47.20</td></tr>
<tr data-flex-row="upper:J24:4"><td>J24</td><td>4</td><td>unconnected-(J24-Pin_4-Pad4)</td><td>strip solder overlap</td><td>289.36, 47.20</td></tr>
<tr data-flex-row="upper:J63:1"><td>J63</td><td>1</td><td>Z6_T23_24V</td><td>strip solder overlap</td><td>157.25, 47.20</td></tr>
<tr data-flex-row="upper:J63:2"><td>J63</td><td>2</td><td>Z6_T23_W</td><td>strip solder overlap</td><td>159.28, 47.20</td></tr>
<tr data-flex-row="upper:J63:3"><td>J63</td><td>3</td><td>Z6_T23_N</td><td>strip solder overlap</td><td>164.87, 47.20</td></tr>
<tr data-flex-row="upper:J63:4"><td>J63</td><td>4</td><td>Z6_T23_C</td><td>strip solder overlap</td><td>166.90, 47.20</td></tr>
<tr data-flex-row="upper:J33:1"><td>J33</td><td>1</td><td>Z3_T23_24V</td><td>strip solder overlap</td><td>320.53, 47.20</td></tr>
<tr data-flex-row="upper:J33:2"><td>J33</td><td>2</td><td>Z3_T23_W</td><td>strip solder overlap</td><td>322.56, 47.20</td></tr>
<tr data-flex-row="upper:J33:3"><td>J33</td><td>3</td><td>Z3_T23_N</td><td>strip solder overlap</td><td>328.15, 47.20</td></tr>
<tr data-flex-row="upper:J33:4"><td>J33</td><td>4</td><td>Z3_T23_C</td><td>strip solder overlap</td><td>330.18, 47.20</td></tr>
<tr data-flex-row="upper:J13:1"><td>J13</td><td>1</td><td>Z1_T23_24V</td><td>strip solder overlap</td><td>211.68, 47.20</td></tr>
<tr data-flex-row="upper:J13:2"><td>J13</td><td>2</td><td>Z1_T23_W</td><td>strip solder overlap</td><td>213.71, 47.20</td></tr>
<tr data-flex-row="upper:J13:3"><td>J13</td><td>3</td><td>Z1_T23_N</td><td>strip solder overlap</td><td>219.30, 47.20</td></tr>
<tr data-flex-row="upper:J13:4"><td>J13</td><td>4</td><td>Z1_T23_C</td><td>strip solder overlap</td><td>221.33, 47.20</td></tr>
<tr data-flex-row="upper:J31:1"><td>J31</td><td>1</td><td>ZONE3_24V</td><td>strip solder overlap</td><td>293.32, 47.20</td></tr>
<tr data-flex-row="upper:J31:2"><td>J31</td><td>2</td><td>ZONE3_W</td><td>strip solder overlap</td><td>295.35, 47.20</td></tr>
<tr data-flex-row="upper:J31:3"><td>J31</td><td>3</td><td>ZONE3_N</td><td>strip solder overlap</td><td>300.94, 47.20</td></tr>
<tr data-flex-row="upper:J31:4"><td>J31</td><td>4</td><td>ZONE3_C</td><td>strip solder overlap</td><td>302.97, 47.20</td></tr>
<tr data-flex-row="upper:J61:1"><td>J61</td><td>1</td><td>unconnected-(J61-Pin_1-Pad1)</td><td>strip solder overlap</td><td>130.03, 47.20</td></tr>
<tr data-flex-row="upper:J61:2"><td>J61</td><td>2</td><td>unconnected-(J61-Pin_2-Pad2)</td><td>strip solder overlap</td><td>132.07, 47.20</td></tr>
<tr data-flex-row="upper:J61:3"><td>J61</td><td>3</td><td>unconnected-(J61-Pin_3-Pad3)</td><td>strip solder overlap</td><td>137.65, 47.20</td></tr>
<tr data-flex-row="upper:J61:4"><td>J61</td><td>4</td><td>unconnected-(J61-Pin_4-Pad4)</td><td>strip solder overlap</td><td>139.69, 47.20</td></tr>
</tbody></table></div>
</details>
<details>
<summary>Lower cylinder band <span class="el-pcb-count">96 pads</span></summary>
<div class="el-pcb-scroll">
<table class="el-pcb-table">
<thead><tr>
<th>Reference</th><th>Pin</th><th>Carries</th><th>Role</th><th>Position (mm)</th>
</tr></thead>
<tbody>
<tr data-flex-row="lower:J41:1"><td>J41</td><td>1</td><td>Z4_B12_24V</td><td>strip solder overlap</td><td>21.18, 39.20</td></tr>
<tr data-flex-row="lower:J41:2"><td>J41</td><td>2</td><td>Z4_B12_W</td><td>strip solder overlap</td><td>23.21, 39.20</td></tr>
<tr data-flex-row="lower:J41:3"><td>J41</td><td>3</td><td>Z4_B12_N</td><td>strip solder overlap</td><td>28.80, 39.20</td></tr>
<tr data-flex-row="lower:J41:4"><td>J41</td><td>4</td><td>Z4_B12_C</td><td>strip solder overlap</td><td>30.83, 39.20</td></tr>
<tr data-flex-row="lower:J42:1"><td>J42</td><td>1</td><td>Z4_B12_24V</td><td>strip solder overlap</td><td>34.78, 39.20</td></tr>
<tr data-flex-row="lower:J42:2"><td>J42</td><td>2</td><td>Z4_B12_W</td><td>strip solder overlap</td><td>36.82, 39.20</td></tr>
<tr data-flex-row="lower:J42:3"><td>J42</td><td>3</td><td>Z4_B12_N</td><td>strip solder overlap</td><td>42.40, 39.20</td></tr>
<tr data-flex-row="lower:J42:4"><td>J42</td><td>4</td><td>Z4_B12_C</td><td>strip solder overlap</td><td>44.44, 39.20</td></tr>
<tr data-flex-row="lower:J43:1"><td>J43</td><td>1</td><td>Z4_B34_24V</td><td>strip solder overlap</td><td>48.39, 39.20</td></tr>
<tr data-flex-row="lower:J43:2"><td>J43</td><td>2</td><td>Z4_B34_W</td><td>strip solder overlap</td><td>50.42, 39.20</td></tr>
<tr data-flex-row="lower:J43:3"><td>J43</td><td>3</td><td>Z4_B34_N</td><td>strip solder overlap</td><td>56.01, 39.20</td></tr>
<tr data-flex-row="lower:J43:4"><td>J43</td><td>4</td><td>Z4_B34_C</td><td>strip solder overlap</td><td>58.04, 39.20</td></tr>
<tr data-flex-row="lower:J44:1"><td>J44</td><td>1</td><td>Z4_B34_24V</td><td>strip solder overlap</td><td>62.00, 39.20</td></tr>
<tr data-flex-row="lower:J44:2"><td>J44</td><td>2</td><td>Z4_B34_W</td><td>strip solder overlap</td><td>64.03, 39.20</td></tr>
<tr data-flex-row="lower:J44:3"><td>J44</td><td>3</td><td>Z4_B34_N</td><td>strip solder overlap</td><td>69.62, 39.20</td></tr>
<tr data-flex-row="lower:J44:4"><td>J44</td><td>4</td><td>Z4_B34_C</td><td>strip solder overlap</td><td>71.65, 39.20</td></tr>
<tr data-flex-row="lower:J51:1"><td>J51</td><td>1</td><td>Z5_B12_24V</td><td>strip solder overlap</td><td>75.61, 39.20</td></tr>
<tr data-flex-row="lower:J51:2"><td>J51</td><td>2</td><td>Z5_B12_W</td><td>strip solder overlap</td><td>77.64, 39.20</td></tr>
<tr data-flex-row="lower:J51:3"><td>J51</td><td>3</td><td>Z5_B12_N</td><td>strip solder overlap</td><td>83.23, 39.20</td></tr>
<tr data-flex-row="lower:J51:4"><td>J51</td><td>4</td><td>Z5_B12_C</td><td>strip solder overlap</td><td>85.26, 39.20</td></tr>
<tr data-flex-row="lower:J52:1"><td>J52</td><td>1</td><td>Z5_B12_24V</td><td>strip solder overlap</td><td>89.21, 39.20</td></tr>
<tr data-flex-row="lower:J52:2"><td>J52</td><td>2</td><td>Z5_B12_W</td><td>strip solder overlap</td><td>91.24, 39.20</td></tr>
<tr data-flex-row="lower:J52:3"><td>J52</td><td>3</td><td>Z5_B12_N</td><td>strip solder overlap</td><td>96.83, 39.20</td></tr>
<tr data-flex-row="lower:J52:4"><td>J52</td><td>4</td><td>Z5_B12_C</td><td>strip solder overlap</td><td>98.87, 39.20</td></tr>
<tr data-flex-row="lower:J53:1"><td>J53</td><td>1</td><td>Z5_B34_24V</td><td>strip solder overlap</td><td>102.82, 39.20</td></tr>
<tr data-flex-row="lower:J53:2"><td>J53</td><td>2</td><td>Z5_B34_W</td><td>strip solder overlap</td><td>104.85, 39.20</td></tr>
<tr data-flex-row="lower:J53:3"><td>J53</td><td>3</td><td>Z5_B34_N</td><td>strip solder overlap</td><td>110.44, 39.20</td></tr>
<tr data-flex-row="lower:J53:4"><td>J53</td><td>4</td><td>Z5_B34_C</td><td>strip solder overlap</td><td>112.47, 39.20</td></tr>
<tr data-flex-row="lower:J54:1"><td>J54</td><td>1</td><td>Z5_B34_24V</td><td>strip solder overlap</td><td>116.43, 39.20</td></tr>
<tr data-flex-row="lower:J54:2"><td>J54</td><td>2</td><td>Z5_B34_W</td><td>strip solder overlap</td><td>118.46, 39.20</td></tr>
<tr data-flex-row="lower:J54:3"><td>J54</td><td>3</td><td>Z5_B34_N</td><td>strip solder overlap</td><td>124.05, 39.20</td></tr>
<tr data-flex-row="lower:J54:4"><td>J54</td><td>4</td><td>Z5_B34_C</td><td>strip solder overlap</td><td>126.08, 39.20</td></tr>
<tr data-flex-row="lower:J61:1"><td>J61</td><td>1</td><td>Z6_B12_24V</td><td>strip solder overlap</td><td>130.03, 39.20</td></tr>
<tr data-flex-row="lower:J61:2"><td>J61</td><td>2</td><td>Z6_B12_W</td><td>strip solder overlap</td><td>132.07, 39.20</td></tr>
<tr data-flex-row="lower:J61:3"><td>J61</td><td>3</td><td>Z6_B12_N</td><td>strip solder overlap</td><td>137.65, 39.20</td></tr>
<tr data-flex-row="lower:J61:4"><td>J61</td><td>4</td><td>Z6_B12_C</td><td>strip solder overlap</td><td>139.69, 39.20</td></tr>
<tr data-flex-row="lower:J62:1"><td>J62</td><td>1</td><td>Z6_B12_24V</td><td>strip solder overlap</td><td>143.64, 39.20</td></tr>
<tr data-flex-row="lower:J62:2"><td>J62</td><td>2</td><td>Z6_B12_W</td><td>strip solder overlap</td><td>145.67, 39.20</td></tr>
<tr data-flex-row="lower:J62:3"><td>J62</td><td>3</td><td>Z6_B12_N</td><td>strip solder overlap</td><td>151.26, 39.20</td></tr>
<tr data-flex-row="lower:J62:4"><td>J62</td><td>4</td><td>Z6_B12_C</td><td>strip solder overlap</td><td>153.29, 39.20</td></tr>
<tr data-flex-row="lower:J63:1"><td>J63</td><td>1</td><td>Z6_B34_24V</td><td>strip solder overlap</td><td>157.25, 39.20</td></tr>
<tr data-flex-row="lower:J63:2"><td>J63</td><td>2</td><td>Z6_B34_W</td><td>strip solder overlap</td><td>159.28, 39.20</td></tr>
<tr data-flex-row="lower:J63:3"><td>J63</td><td>3</td><td>Z6_B34_N</td><td>strip solder overlap</td><td>164.87, 39.20</td></tr>
<tr data-flex-row="lower:J63:4"><td>J63</td><td>4</td><td>Z6_B34_C</td><td>strip solder overlap</td><td>166.90, 39.20</td></tr>
<tr data-flex-row="lower:J64:1"><td>J64</td><td>1</td><td>Z6_B34_24V</td><td>strip solder overlap</td><td>170.85, 39.20</td></tr>
<tr data-flex-row="lower:J64:2"><td>J64</td><td>2</td><td>Z6_B34_W</td><td>strip solder overlap</td><td>172.89, 39.20</td></tr>
<tr data-flex-row="lower:J64:3"><td>J64</td><td>3</td><td>Z6_B34_N</td><td>strip solder overlap</td><td>178.48, 39.20</td></tr>
<tr data-flex-row="lower:J64:4"><td>J64</td><td>4</td><td>Z6_B34_C</td><td>strip solder overlap</td><td>180.51, 39.20</td></tr>
<tr data-flex-row="lower:J11:1"><td>J11</td><td>1</td><td>Z1_B12_24V</td><td>strip solder overlap</td><td>184.46, 39.20</td></tr>
<tr data-flex-row="lower:J11:2"><td>J11</td><td>2</td><td>Z1_B12_W</td><td>strip solder overlap</td><td>186.49, 39.20</td></tr>
<tr data-flex-row="lower:J11:3"><td>J11</td><td>3</td><td>Z1_B12_N</td><td>strip solder overlap</td><td>192.08, 39.20</td></tr>
<tr data-flex-row="lower:J11:4"><td>J11</td><td>4</td><td>Z1_B12_C</td><td>strip solder overlap</td><td>194.11, 39.20</td></tr>
<tr data-flex-row="lower:J12:1"><td>J12</td><td>1</td><td>Z1_B12_24V</td><td>strip solder overlap</td><td>198.07, 39.20</td></tr>
<tr data-flex-row="lower:J12:2"><td>J12</td><td>2</td><td>Z1_B12_W</td><td>strip solder overlap</td><td>200.10, 39.20</td></tr>
<tr data-flex-row="lower:J12:3"><td>J12</td><td>3</td><td>Z1_B12_N</td><td>strip solder overlap</td><td>205.69, 39.20</td></tr>
<tr data-flex-row="lower:J12:4"><td>J12</td><td>4</td><td>Z1_B12_C</td><td>strip solder overlap</td><td>207.72, 39.20</td></tr>
<tr data-flex-row="lower:J13:1"><td>J13</td><td>1</td><td>Z1_B34_24V</td><td>strip solder overlap</td><td>211.68, 39.20</td></tr>
<tr data-flex-row="lower:J13:2"><td>J13</td><td>2</td><td>Z1_B34_W</td><td>strip solder overlap</td><td>213.71, 39.20</td></tr>
<tr data-flex-row="lower:J13:3"><td>J13</td><td>3</td><td>Z1_B34_N</td><td>strip solder overlap</td><td>219.30, 39.20</td></tr>
<tr data-flex-row="lower:J13:4"><td>J13</td><td>4</td><td>Z1_B34_C</td><td>strip solder overlap</td><td>221.33, 39.20</td></tr>
<tr data-flex-row="lower:J14:1"><td>J14</td><td>1</td><td>Z1_B34_24V</td><td>strip solder overlap</td><td>225.28, 39.20</td></tr>
<tr data-flex-row="lower:J14:2"><td>J14</td><td>2</td><td>Z1_B34_W</td><td>strip solder overlap</td><td>227.31, 39.20</td></tr>
<tr data-flex-row="lower:J14:3"><td>J14</td><td>3</td><td>Z1_B34_N</td><td>strip solder overlap</td><td>232.90, 39.20</td></tr>
<tr data-flex-row="lower:J14:4"><td>J14</td><td>4</td><td>Z1_B34_C</td><td>strip solder overlap</td><td>234.94, 39.20</td></tr>
<tr data-flex-row="lower:J21:1"><td>J21</td><td>1</td><td>Z2_B12_24V</td><td>strip solder overlap</td><td>238.89, 39.20</td></tr>
<tr data-flex-row="lower:J21:2"><td>J21</td><td>2</td><td>Z2_B12_W</td><td>strip solder overlap</td><td>240.92, 39.20</td></tr>
<tr data-flex-row="lower:J21:3"><td>J21</td><td>3</td><td>Z2_B12_N</td><td>strip solder overlap</td><td>246.51, 39.20</td></tr>
<tr data-flex-row="lower:J21:4"><td>J21</td><td>4</td><td>Z2_B12_C</td><td>strip solder overlap</td><td>248.54, 39.20</td></tr>
<tr data-flex-row="lower:J22:1"><td>J22</td><td>1</td><td>Z2_B12_24V</td><td>strip solder overlap</td><td>252.50, 39.20</td></tr>
<tr data-flex-row="lower:J22:2"><td>J22</td><td>2</td><td>Z2_B12_W</td><td>strip solder overlap</td><td>254.53, 39.20</td></tr>
<tr data-flex-row="lower:J22:3"><td>J22</td><td>3</td><td>Z2_B12_N</td><td>strip solder overlap</td><td>260.12, 39.20</td></tr>
<tr data-flex-row="lower:J22:4"><td>J22</td><td>4</td><td>Z2_B12_C</td><td>strip solder overlap</td><td>262.15, 39.20</td></tr>
<tr data-flex-row="lower:J23:1"><td>J23</td><td>1</td><td>Z2_B34_24V</td><td>strip solder overlap</td><td>266.10, 39.20</td></tr>
<tr data-flex-row="lower:J23:2"><td>J23</td><td>2</td><td>Z2_B34_W</td><td>strip solder overlap</td><td>268.14, 39.20</td></tr>
<tr data-flex-row="lower:J23:3"><td>J23</td><td>3</td><td>Z2_B34_N</td><td>strip solder overlap</td><td>273.72, 39.20</td></tr>
<tr data-flex-row="lower:J23:4"><td>J23</td><td>4</td><td>Z2_B34_C</td><td>strip solder overlap</td><td>275.76, 39.20</td></tr>
<tr data-flex-row="lower:J24:1"><td>J24</td><td>1</td><td>Z2_B34_24V</td><td>strip solder overlap</td><td>279.71, 39.20</td></tr>
<tr data-flex-row="lower:J24:2"><td>J24</td><td>2</td><td>Z2_B34_W</td><td>strip solder overlap</td><td>281.74, 39.20</td></tr>
<tr data-flex-row="lower:J24:3"><td>J24</td><td>3</td><td>Z2_B34_N</td><td>strip solder overlap</td><td>287.33, 39.20</td></tr>
<tr data-flex-row="lower:J24:4"><td>J24</td><td>4</td><td>Z2_B34_C</td><td>strip solder overlap</td><td>289.36, 39.20</td></tr>
<tr data-flex-row="lower:J31:1"><td>J31</td><td>1</td><td>Z3_B12_24V</td><td>strip solder overlap</td><td>293.32, 39.20</td></tr>
<tr data-flex-row="lower:J31:2"><td>J31</td><td>2</td><td>Z3_B12_W</td><td>strip solder overlap</td><td>295.35, 39.20</td></tr>
<tr data-flex-row="lower:J31:3"><td>J31</td><td>3</td><td>Z3_B12_N</td><td>strip solder overlap</td><td>300.94, 39.20</td></tr>
<tr data-flex-row="lower:J31:4"><td>J31</td><td>4</td><td>Z3_B12_C</td><td>strip solder overlap</td><td>302.97, 39.20</td></tr>
<tr data-flex-row="lower:J32:1"><td>J32</td><td>1</td><td>Z3_B12_24V</td><td>strip solder overlap</td><td>306.92, 39.20</td></tr>
<tr data-flex-row="lower:J32:2"><td>J32</td><td>2</td><td>Z3_B12_W</td><td>strip solder overlap</td><td>308.96, 39.20</td></tr>
<tr data-flex-row="lower:J32:3"><td>J32</td><td>3</td><td>Z3_B12_N</td><td>strip solder overlap</td><td>314.55, 39.20</td></tr>
<tr data-flex-row="lower:J32:4"><td>J32</td><td>4</td><td>Z3_B12_C</td><td>strip solder overlap</td><td>316.58, 39.20</td></tr>
<tr data-flex-row="lower:J33:1"><td>J33</td><td>1</td><td>Z3_B34_24V</td><td>strip solder overlap</td><td>320.53, 39.20</td></tr>
<tr data-flex-row="lower:J33:2"><td>J33</td><td>2</td><td>Z3_B34_W</td><td>strip solder overlap</td><td>322.56, 39.20</td></tr>
<tr data-flex-row="lower:J33:3"><td>J33</td><td>3</td><td>Z3_B34_N</td><td>strip solder overlap</td><td>328.15, 39.20</td></tr>
<tr data-flex-row="lower:J33:4"><td>J33</td><td>4</td><td>Z3_B34_C</td><td>strip solder overlap</td><td>330.18, 39.20</td></tr>
<tr data-flex-row="lower:J34:1"><td>J34</td><td>1</td><td>Z3_B34_24V</td><td>strip solder overlap</td><td>334.14, 39.20</td></tr>
<tr data-flex-row="lower:J34:2"><td>J34</td><td>2</td><td>Z3_B34_W</td><td>strip solder overlap</td><td>336.17, 39.20</td></tr>
<tr data-flex-row="lower:J34:3"><td>J34</td><td>3</td><td>Z3_B34_N</td><td>strip solder overlap</td><td>341.76, 39.20</td></tr>
<tr data-flex-row="lower:J34:4"><td>J34</td><td>4</td><td>Z3_B34_C</td><td>strip solder overlap</td><td>343.79, 39.20</td></tr>
</tbody></table></div>
</details>
</div>

<!-- el-pcb:generated flex-connections end -->

## What has been checked — and what has not { #flex-validation }

<!-- el-pcb:generated flex-validation start -->

<div class="el-pcb-scroll">
<table class="el-pcb-table">
<thead><tr>
<th>Circuit</th><th>ERC</th><th>DRC</th><th>Unconnected</th><th>Parity</th><th>Pin oracle</th><th>Pads / CAM flashes</th><th>CAM tracks</th><th>CAM drills</th>
</tr></thead>
<tbody>
<tr><td>Arm ribbon</td><td>0</td><td>0</td><td>0</td><td>0</td><td>PASS</td><td>70 / 70</td><td>10</td><td>0</td></tr>
<tr><td>Upper cylinder band</td><td>0</td><td>0</td><td>0</td><td>0</td><td>PASS</td><td>126 / 222</td><td>252</td><td>192</td></tr>
<tr><td>Lower cylinder band</td><td>0</td><td>0</td><td>0</td><td>0</td><td>PASS</td><td>96 / 192</td><td>144</td><td>192</td></tr>
</tbody></table></div>

<!-- el-pcb:generated flex-validation end -->

Each of those ran against the routed design. "Pads / CAM flashes" compares the native design against
the exported manufacturing data. The lower band has 96 two-sided lands and 192 flashes. The new
upper has 96 two-sided strip lands plus 30 **back-only** insertion contacts: 126 pads and 222 copper
flashes. The viewer and its registration test use the actual copper side for those thirty contacts.

None of the following has been done:

- No circuit has been fabricated, so nothing has been measured, soldered or fitted.
- The manufacturer has not accepted the stack-up, coverlay thickness and registration, stiffener
  geometry, or the requested tolerances — outline ±0.10 mm, pad position ±0.05 mm, coverlay alignment
  ±0.025 mm where a 0.05 mm capture is used.
- The mounted pad alignment has not passed a template or coupon check. See [the hold](#fit-hold).
- Adhesion of the tape to real cured coverlay and to aluminium is untested, and no safety insulation
  rating is credited to the adhesive.
- No repeated-motion flex qualification is claimed for any of the three, and none is needed for the
  arm ribbon, which is static.
- No CAN signal integrity, no radio, no thermal and no powered test of any kind.

## Downloads { #flex-downloads }

Native KiCad sources, the connection tables, the construction drawings and the manufacturing archives.
Use the current upper insertion drawing and actual-size SVG template first. The A3 PDF is retained
only as a labelled historical reference; its old upper tail is not the current outline.

<!-- el-pcb:generated flex-downloads start -->

<div class="el-pcb-scroll">
<table class="el-pcb-table">
<thead><tr>
<th>Circuit</th><th>File</th><th>Size</th><th>SHA-256 (first 12)</th><th>Download</th>
</tr></thead>
<tbody>
<tr><td>Arm ribbon</td><td>gimbal-static-v0.2.kicad_pcb</td><td>46 kB</td><td><code>7136c5c343da</code></td><td><a href="../assets/pcb/flex-v0.2/gimbal/kicad/gimbal-static-v0.2.kicad_pcb">download</a></td></tr>
<tr><td>Arm ribbon</td><td>gimbal-static-v0.2.kicad_sch</td><td>55 kB</td><td><code>4aca27d215ee</code></td><td><a href="../assets/pcb/flex-v0.2/gimbal/kicad/gimbal-static-v0.2.kicad_sch">download</a></td></tr>
<tr><td>Arm ribbon</td><td>gimbal-static-v0.2.kicad_pro</td><td>9 kB</td><td><code>1ba7cd743f92</code></td><td><a href="../assets/pcb/flex-v0.2/gimbal/kicad/gimbal-static-v0.2.kicad_pro">download</a></td></tr>
<tr><td>Arm ribbon</td><td>fp-lib-table</td><td>128 bytes</td><td><code>9e2b7618924d</code></td><td><a href="../assets/pcb/flex-v0.2/gimbal/kicad/fp-lib-table">download</a></td></tr>
<tr><td>Arm ribbon</td><td>connection-table.csv</td><td>2 kB</td><td><code>459719df5bce</code></td><td><a href="../assets/pcb/flex-v0.2/gimbal/connection-table.csv">download</a></td></tr>
<tr><td>Arm ribbon</td><td>stiffener-regions.csv</td><td>835 bytes</td><td><code>e8a7fa70a77b</code></td><td><a href="../assets/pcb/flex-v0.2/gimbal/stiffener-regions.csv">download</a></td></tr>
<tr><td>Arm ribbon</td><td>design-intent.json</td><td>3 kB</td><td><code>4873f8171e94</code></td><td><a href="../assets/pcb/flex-v0.2/gimbal/design-intent.json">download</a></td></tr>
<tr><td>Arm ribbon</td><td>verification.json</td><td>2 kB</td><td><code>b17837cfa26f</code></td><td><a href="../assets/pcb/flex-v0.2/gimbal/verification.json">download</a></td></tr>
<tr><td>Arm ribbon</td><td>construction.svg</td><td>8 kB</td><td><code>c8e4610622c3</code></td><td><a href="../assets/pcb/flex-v0.2/gimbal/construction.svg">download</a></td></tr>
<tr><td>Arm ribbon</td><td>overview.svg</td><td>12 kB</td><td><code>6091172d0e5a</code></td><td><a href="../assets/pcb/flex-v0.2/gimbal/overview.svg">download</a></td></tr>
<tr><td>Arm ribbon</td><td>fabrication archive (Gerbers, drills, maps)</td><td>7 kB</td><td><code>39804422f9dc</code></td><td><a href="../assets/pcb/flex-v0.2/gimbal/FLEX-v0.2-gimbal-fabrication.zip">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>led-upper-v0.3.kicad_pcb</td><td>292 kB</td><td><code>0af25f8f72fb</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/led-upper-v0.3.kicad_pcb">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>led-upper-v0.3.kicad_sch</td><td>105 kB</td><td><code>444302c3b7c2</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/led-upper-v0.3.kicad_sch">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>led-upper-v0.3.kicad_pro</td><td>9 kB</td><td><code>48649b473816</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/led-upper-v0.3.kicad_pro">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>fp-lib-table</td><td>133 bytes</td><td><code>a347ee4b351d</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/fp-lib-table">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>connection-table.csv</td><td>8 kB</td><td><code>71203eb69de1</code></td><td><a href="../assets/pcb/flex-v0.2/upper/connection-table.csv">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>stiffener-regions.csv</td><td>169 bytes</td><td><code>f66766c13ecb</code></td><td><a href="../assets/pcb/flex-v0.2/upper/stiffener-regions.csv">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>design-intent.json</td><td>125 kB</td><td><code>46f93887face</code></td><td><a href="../assets/pcb/flex-v0.2/upper/design-intent.json">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>verification.json</td><td>2 kB</td><td><code>712510f6a3d0</code></td><td><a href="../assets/pcb/flex-v0.2/upper/verification.json">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>insertion-drawing.svg</td><td>19 kB</td><td><code>b1fa13bb2e6e</code></td><td><a href="../assets/pcb/flex-v0.2/upper/insertion-drawing.svg">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>template-1-to-1.svg</td><td>54 kB</td><td><code>2d3fbf2c9c41</code></td><td><a href="../assets/pcb/flex-v0.2/upper/template-1-to-1.svg">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J100-pin-map.csv</td><td>1000 bytes</td><td><code>dc771ec84b33</code></td><td><a href="../assets/pcb/flex-v0.2/upper/J100-pin-map.csv">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J100_FPC30_BottomContacts.kicad_mod</td><td>7 kB</td><td><code>817b137589b8</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J100_FPC30_BottomContacts.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J11_Solder4.kicad_mod</td><td>2 kB</td><td><code>d73bcea3a092</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J11_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J12_Solder4.kicad_mod</td><td>2 kB</td><td><code>cf86ac5d1d7f</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J12_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J13_Solder4.kicad_mod</td><td>2 kB</td><td><code>df856b8b5084</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J13_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J14_Solder4.kicad_mod</td><td>2 kB</td><td><code>7005f5608e9c</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J14_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J21_Solder4.kicad_mod</td><td>2 kB</td><td><code>dd015cb845db</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J21_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J22_Solder4.kicad_mod</td><td>2 kB</td><td><code>fc0b9c78bb50</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J22_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J23_Solder4.kicad_mod</td><td>2 kB</td><td><code>ab7e579640c3</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J23_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J24_Solder4.kicad_mod</td><td>2 kB</td><td><code>6e227cbef29d</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J24_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J31_Solder4.kicad_mod</td><td>2 kB</td><td><code>d3fb900ae237</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J31_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J32_Solder4.kicad_mod</td><td>2 kB</td><td><code>b1a463026f84</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J32_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J33_Solder4.kicad_mod</td><td>2 kB</td><td><code>2b629c1f9019</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J33_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J34_Solder4.kicad_mod</td><td>2 kB</td><td><code>f5165a31c6c7</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J34_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J41_Solder4.kicad_mod</td><td>2 kB</td><td><code>b8f3080dc557</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J41_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J42_Solder4.kicad_mod</td><td>2 kB</td><td><code>9cd0a3ac81e3</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J42_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J43_Solder4.kicad_mod</td><td>2 kB</td><td><code>20a7b988ac29</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J43_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J44_Solder4.kicad_mod</td><td>2 kB</td><td><code>47e436c0c672</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J44_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J51_Solder4.kicad_mod</td><td>2 kB</td><td><code>f85cea63eee6</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J51_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J52_Solder4.kicad_mod</td><td>2 kB</td><td><code>f8c4963ec030</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J52_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J53_Solder4.kicad_mod</td><td>2 kB</td><td><code>6ca4678b07d5</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J53_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J54_Solder4.kicad_mod</td><td>2 kB</td><td><code>d43f88342e77</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J54_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J61_Solder4.kicad_mod</td><td>2 kB</td><td><code>7462e5d1cb9e</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J61_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J62_Solder4.kicad_mod</td><td>2 kB</td><td><code>c46b413b839d</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J62_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J63_Solder4.kicad_mod</td><td>2 kB</td><td><code>cea0ef06a98e</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J63_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>J64_Solder4.kicad_mod</td><td>2 kB</td><td><code>345d9708db2d</code></td><td><a href="../assets/pcb/flex-v0.2/upper/kicad/ELFlex.pretty/J64_Solder4.kicad_mod">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>FLEX-v0.3-upper-KiCad-project.zip</td><td>92 kB</td><td><code>f5f6adc194ca</code></td><td><a href="../assets/pcb/flex-v0.2/upper/FLEX-v0.3-upper-KiCad-project.zip">download</a></td></tr>
<tr><td>Upper cylinder band</td><td>fabrication archive (Gerbers, drills, maps)</td><td>60 kB</td><td><code>243b050e5e1d</code></td><td><a href="../assets/pcb/flex-v0.2/upper/FLEX-v0.3-upper-fabrication.zip">download</a></td></tr>
<tr><td>Lower cylinder band</td><td>led-lower-v0.2.kicad_pcb</td><td>260 kB</td><td><code>21db9dba94c6</code></td><td><a href="../assets/pcb/flex-v0.2/lower/kicad/led-lower-v0.2.kicad_pcb">download</a></td></tr>
<tr><td>Lower cylinder band</td><td>led-lower-v0.2.kicad_sch</td><td>80 kB</td><td><code>af6adde4732b</code></td><td><a href="../assets/pcb/flex-v0.2/lower/kicad/led-lower-v0.2.kicad_sch">download</a></td></tr>
<tr><td>Lower cylinder band</td><td>led-lower-v0.2.kicad_pro</td><td>595 bytes</td><td><code>fd016441b542</code></td><td><a href="../assets/pcb/flex-v0.2/lower/kicad/led-lower-v0.2.kicad_pro">download</a></td></tr>
<tr><td>Lower cylinder band</td><td>fp-lib-table</td><td>133 bytes</td><td><code>a347ee4b351d</code></td><td><a href="../assets/pcb/flex-v0.2/lower/kicad/fp-lib-table">download</a></td></tr>
<tr><td>Lower cylinder band</td><td>connection-table.csv</td><td>10 kB</td><td><code>bc008507bd45</code></td><td><a href="../assets/pcb/flex-v0.2/lower/connection-table.csv">download</a></td></tr>
<tr><td>Lower cylinder band</td><td>stiffener-regions.csv</td><td>86 bytes</td><td><code>4993f8b120f8</code></td><td><a href="../assets/pcb/flex-v0.2/lower/stiffener-regions.csv">download</a></td></tr>
<tr><td>Lower cylinder band</td><td>design-intent.json</td><td>71 kB</td><td><code>a2b7d4c552a3</code></td><td><a href="../assets/pcb/flex-v0.2/lower/design-intent.json">download</a></td></tr>
<tr><td>Lower cylinder band</td><td>verification.json</td><td>2 kB</td><td><code>a0a0fbd1e3c8</code></td><td><a href="../assets/pcb/flex-v0.2/lower/verification.json">download</a></td></tr>
<tr><td>Lower cylinder band</td><td>construction.svg</td><td>10 kB</td><td><code>14a1b38779ee</code></td><td><a href="../assets/pcb/flex-v0.2/lower/construction.svg">download</a></td></tr>
<tr><td>Lower cylinder band</td><td>overview.svg</td><td>45 kB</td><td><code>819b82cf5a53</code></td><td><a href="../assets/pcb/flex-v0.2/lower/overview.svg">download</a></td></tr>
<tr><td>Lower cylinder band</td><td>fabrication archive (Gerbers, drills, maps)</td><td>56 kB</td><td><code>7683f432a580</code></td><td><a href="../assets/pcb/flex-v0.2/lower/FLEX-v0.2-lower-fabrication.zip">download</a></td></tr>
<tr><td>All three</td><td>Historical v0.2 fit templates: upper tail obsolete; use current upper SVG</td><td>16 kB</td><td><code>a62821483bfb</code></td><td><a href="../assets/pcb/flex-v0.2/fit-templates-A3.pdf">download</a></td></tr>
<tr><td>All three</td><td>Engineering notes (Markdown source)</td><td>2 kB</td><td><code>d1d7c7d5ae44</code></td><td><a href="../assets/pcb/flex-v0.2/ENGINEERING-NOTES.txt">download</a></td></tr>
</tbody></table></div>

<!-- el-pcb:generated flex-downloads end -->

The per-circuit fabrication reviews sent to the manufacturer are deliberately **not** published here:
they carry vendor correspondence details. Public construction requirements are summarized in the engineering
notes and per-design intent files above. These downloads do not replace supplier process review.

## How this fits the rest of the fixture

| This circuit | Replaces | Connects to |
|---|---|---|
| Arm ribbon | Ten hand-cut wires along the arm | Motor 2 power, the CAN pair and three spotlight pairs |
| Upper cylinder band | Hand-soldered strip tails, upper half | Six separately fused zone feeds through main `J2` and upper `J100` |
| Lower cylinder band | Hand-soldered strip tails, lower half | The same six zones from below |

The new main `J2` and upper `J100` are a matched pair. [Doc 9](09-understand-the-pcb.md) supplies
their current pin map; `J9`–`J11` and `J13` retain the spotlight/arm interfaces.

## Risk register

| Risk | Why it matters | What would settle it |
|---|---|---|
| Mounted pad alignment | Adhesive tolerance alone can exceed the lateral copper margin over half a turn | The printed template dry-fitted on the actual compressed stack |
| Factory construction not accepted | Stack, coverlay registration and the 1.4 mm fingers all need explicit review | The manufacturer's response to the quotation package |
| Solder joint quality | The high-resistance sensitivity breaks the wiring budget | A supported sample joint, then loaded voltage measurement |
| Strip geometry assumed | The real strip may mount faceted rather than conforming | Full-size fit check on the real cylinder |
| Nothing ordered yet | Every number here is from the design, not from a part | Fabrication, after the holds above clear |

## Related reading

- [Doc 9 · Understand the PCB](09-understand-the-pcb.md) — the board these circuits plug into.
- [Doc 4a · Wire the Zones For Real](04a-wire-the-zones.md) — the hand-wired version these replace.
- [Doc 8 · Build the Fixture](08-build-the-fixture.md) — where the hand-cut harness lives today.
