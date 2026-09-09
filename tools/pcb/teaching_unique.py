"""Hand-written teaching entries for the named parts on LIGHT v0.2.

Everything a template cannot say generically lives here: the integrated
circuits, the connectors with their own stories, the discrete power parts and
the four capacitors whose job is timing rather than decoupling.

Every claim carries a kind (documented / inference / open) and an evidence
class. 'measured' is never used: no LIGHT v0.2 board has been powered.

Field contract per reference:
    name     short plain-language name
    circuit  key of teaching.CIRCUITS
    here     what this exact part does in this exact circuit (names real nets)
    how      how the underlying thing works, for a reader who does not know
    related  other references worth jumping to
    claims   [{kind, evidence, text, basis, bound_to?, source_file?}]
    open     unsettled questions
    assembly factory process notes that belong to this part
    inspect  what to look at on an assembled board, where that is specific
"""

INTENT = "intended"
CAD = "cad-checked"
MODEL = "modelled-current"
HIST = "simulated-historical"

UNIQUE = {

    # ---------------------------------------------------------------- controller
    "U1": {
        "name": "ESP32-C6 radio module (the controller)",
        "circuit": "mcu",
        "here": (
            "The brain and the radio. It runs the fixture's firmware, talks to both PWM expanders and the "
            "temperature sensor over I2C_SDA and I2C_SCL, drives the three spotlight requests SPOT1_PWM, "
            "SPOT2_PWM and SPOT3_PWM, speaks CAN to the motors through CAN_TX and CAN_RX, and raises "
            "LIGHT_ENABLE when it wants light. Its reset pin MCU_EN is held by R1 and C1 and can be pulled "
            "down by S1 or by the supervisor through R42."
        ),
        "how": (
            "A pre-certified radio module: a chip, a crystal, flash memory, matching components and a printed "
            "antenna on a small board, tested as a unit so the fixture does not have to solve radio layout. It "
            "solders down by castellated edge pads plus a large ground pad underneath. The module's pad numbers "
            "are not GPIO numbers -- pad 25 is the serial transmit line, which the chip calls GPIO16 -- so "
            "always read the map rather than counting pins."
        ),
        "related": ["R1", "C1", "C2", "C3", "S1", "S2", "R2", "R3", "J15", "U2", "U3", "U4", "U17", "J18"],
        "claims": [
            {"kind": "documented", "evidence": INTENT,
             "text": "Fixed assignments: GPIO2 and GPIO3 are the I2C pair; GPIO6 and GPIO7 are CAN transmit and "
                     "receive; GPIO10, GPIO11 and GPIO18 are the three spotlight PWM outputs; GPIO0 carries the "
                     "lighting-enable request and GPIO1 reads whether USB is present.",
             "basis": "engineering-history/firmware_port_map.md"},
            {"kind": "documented", "evidence": INTENT,
             "text": "Module pad numbers are not GPIO numbers. Pad 25 is U0TXD (GPIO16) on net UART_TX and pad 24 "
                     "is U0RXD (GPIO17) on net UART_RX.",
             "basis": "hardware-current/hardware/rev-a/EL.kicad_sym symbol pin names"},
            {"kind": "documented", "evidence": CAD,
             "text": "The module's antenna area is kept clear of copper on all eight layers, and its body "
                     "overhangs the board edge above the flat -- that overhang is deliberate, not a drawing error.",
             "basis": "hardware-current/reports/mechanical-final-audit.json (rf_copper_keepout)"},
            {"kind": "documented", "evidence": INTENT,
             "text": "Pad 22 is deliberately left unconnected, and pad 29 is the ground pad, which appears as "
                     "nine separate shapes in the footprint.",
             "basis": "board.json pins and pads for U1"},
        ],
        "open": [
            "No firmware has been built or flashed for this board. The channel map is an integration contract, "
            "not shipped code.",
            "Radio behaviour with a real enclosure, cables and metal fasteners nearby is unmeasured.",
        ],
        "assembly": ["37 physical pad shapes for 29 logical pins; nine of them are the single ground pad."],
        "inspect": "Check pin 1 orientation and that the antenna end is the one overhanging the flat edge.",
    },

    "U2": {
        "name": "PWM expander at address 0x40",
        "circuit": "pwm",
        "here": (
            "Generates the dimming waveforms for ambient channels 1 to 15 -- zones 1 to 5, warm, neutral and "
            "cool each. The controller talks to it over I2C_SDA and I2C_SCL at address 0x40, its outputs run to "
            "PWM_01 through PWM_15, and PCA_OE can disable every output at once."
        ),
        "how": (
            "One 16-channel PWM generator saves the controller from timing 21 dimming signals itself: the "
            "firmware writes a duty value per channel over two wires, and the chip produces the waveform "
            "continuously. Its outputs here are configured open-drain, meaning each output can only pull its pin "
            "down to ground or let go, never drive it high -- so an external pull-up decides the high level."
        ),
        "related": ["U1", "U3", "C40", "C42", "R7", "R8", "U6", "U13"],
        "claims": [
            {"kind": "documented", "evidence": INTENT,
             "text": "Firmware must set MODE2 to 0x00 (OUTDRV=0, INVRT=0, OUTNE=00) and read it back. Because the "
                     "outputs are open-drain, physical light duty is the complement of the sink-active duty "
                     "written to the chip.",
             "basis": "hardware-current/engineering/design_parts.json (U2 note) and firmware_port_map.md"},
            {"kind": "documented", "evidence": INTENT,
             "text": "Outputs 0 to 14 are logical channels 1 to 15; output 15 is unused and must stay in the "
                     "reviewed disabled state.",
             "basis": "engineering-history/firmware_port_map.md"},
            {"kind": "documented", "evidence": INTENT,
             "text": "Pin 22 is deliberately unconnected.",
             "basis": "board.json pins for U2"},
        ],
        "open": ["The I2C bus should start at 100 kHz; 400 kHz needs a fresh rise-time measurement on hardware."],
        "assembly": ["TSSOP-28 on 0.65 mm pitch."],
    },

    "U3": {
        "name": "PWM expander at address 0x41",
        "circuit": "pwm",
        "here": (
            "Generates the dimming waveforms for ambient channels 16 to 21 -- zone 6 and zone 7. It shares "
            "I2C_SDA and I2C_SCL with the first expander but answers at 0x41, and shares PCA_OE so both chips "
            "are inhibited together. Only six of its sixteen outputs are used; the rest are explicitly "
            "unconnected."
        ),
        "how": (
            "Identical to the first expander, with its address strap tied differently so two chips can share one "
            "two-wire bus. Every I2C device on a bus needs its own address, which is why the second one answers "
            "at 0x41."
        ),
        "related": ["U1", "U2", "C41", "C43", "R7", "R8", "U6", "U13"],
        "claims": [
            {"kind": "documented", "evidence": INTENT,
             "text": "Two channels are routing-driven remaps: logical PWM 18 is output 13 on package pin 20, and "
                     "logical PWM 20 is output 12 on package pin 19. Never derive this chip's output index by "
                     "subtracting 16 from the logical channel number.",
             "basis": "engineering-history/firmware_port_map.md, confirmed against board.json pin nets"},
            {"kind": "documented", "evidence": INTENT,
             "text": "Ten pins are deliberately unconnected: 8, 10, 12, 13, 15, 16, 17, 18, 21 and 22.",
             "basis": "board.json pins for U3"},
        ],
        "open": ["The I2C bus should start at 100 kHz; 400 kHz needs a fresh rise-time measurement on hardware."],
        "assembly": ["TSSOP-28 on 0.65 mm pitch."],
    },

    # ---------------------------------------------------------------- gating
    "U5": {
        "name": "Quad AND gate: ARM and the spotlight PWMs",
        "circuit": "gating",
        "here": (
            "Does two jobs. One gate combines the firmware's LIGHT_ENABLE with the physical ARM switch to "
            "produce LIGHT_REQUEST_ARMED. The other three gate each spotlight request against "
            "LIGHT_ENABLE_SAFE, so SPOT1_PWM, SPOT2_PWM and SPOT3_PWM only reach the drivers as SPOT1_CTRL, "
            "SPOT2_CTRL and SPOT3_CTRL while the board is genuinely safe to light."
        ),
        "how": (
            "An AND gate's output is high only when both its inputs are high. Putting the physical switch and "
            "the software request into an AND gate means neither alone can turn the lights on -- the hardware "
            "enforces it whatever the firmware does. The spotlight PWM signals keep their normal polarity "
            "through these gates; the open-drain inversion applies only to the ambient channels."
        ),
        "related": ["U19", "U18", "U6", "U13", "J17", "R5", "R4", "U7", "U8", "U9"],
        "claims": [
            {"kind": "documented", "evidence": INTENT,
             "text": "Only pin 11 changed in the supply-fall correction, from LIGHT_ENABLE_SAFE to "
                     "LIGHT_REQUEST_ARMED, so the arming decision happens before the supervisor qualifies it.",
             "basis": "engineering-history/rev_a_inhibit_correction.md"},
            {"kind": "documented", "evidence": INTENT,
             "text": "Spotlight PWM polarity is positive through these gates and must not inherit the ambient "
                     "channels' open-drain inversion.",
             "basis": "engineering-history/firmware_port_map.md"},
        ],
        "open": [],
        "assembly": ["TSSOP-14 on 0.65 mm pitch."],
    },

    "U6": {
        "name": "Inverter for the expanders' output-enable",
        "circuit": "gating",
        "here": (
            "Turns LIGHT_ENABLE_SAFE into PCA_OE. The expanders' output-enable is active-low, so this inverter "
            "makes 'safe to light' mean 'outputs enabled' and, more importantly, makes the loss of SAFE disable "
            "every ambient output at once."
        ),
        "how": (
            "An inverter outputs the opposite of its input. It is needed because the enable signal is asserted "
            "high while the expanders' control pin is asserted low. Pairing it with R6, which holds PCA_OE high "
            "by default, means the ambient outputs are disabled unless something actively enables them."
        ),
        "related": ["U2", "U3", "R6", "U19", "C5"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "Pin 1 is deliberately unconnected.", "basis": "board.json pins for U6"}],
        "open": [],
    },

    "U13": {
        "name": "Gate-bias load switch",
        "circuit": "gating",
        "here": (
            "Supplies GATE_BIAS, the rail that feeds all 21 ambient gate pull-ups, from +3V3. Its enable pin is "
            "LIGHT_ENABLE_SAFE, so when the board is not safe to light the gate pull-ups have no supply at all "
            "and no ambient channel can be switched on, whatever the expanders do."
        ),
        "how": (
            "A load switch is a transistor with control circuitry that connects or disconnects a rail on "
            "command. This one also has a quick-output-discharge path that actively drains the rail when it "
            "switches off, so the gates do not float down slowly through leakage."
        ),
        "related": ["U19", "U5", "C514", "C515", "R514", "U2", "U3"],
        "claims": [
            {"kind": "documented", "evidence": INTENT,
             "text": "This part guarantees ON-low behaviour only at 0.35 V or below, which is why the project's "
                     "inhibit criterion is at most 0.35 V on TP7 with 0.30 V as the measurement target -- not the "
                     "0.5 V an earlier checklist used.",
             "basis": "engineering-history/partial_power_review.md and rev_a_inhibit_correction.md"},
            {"kind": "documented", "evidence": INTENT,
             "text": "The quick-discharge resistance is a typical value, not guaranteed across a loss of supply.",
             "basis": "hardware-current/engineering/design_parts.json (U13 note)"},
        ],
        "open": ["Pin 4 is deliberately unconnected.",
                 "Gate decay time without the quick-discharge path is a calculation, not an observation."],
    },

    "U18": {
        "name": "3.3 V supply supervisor",
        "circuit": "gating",
        "here": (
            "Watches +3V3 and releases READY_3V3 only when the rail is genuinely up. That signal qualifies the "
            "lighting request at U19, tells the USB data mux it may connect the host through the R41/R39 "
            "divider, and reaches the controller's reset node through R42."
        ),
        "how": (
            "A supervisor is a small comparator with a reference and a delay: it holds its output low while the "
            "rail is below its threshold and for a set time after it rises, then lets go. Ordinary logic gates "
            "behave unpredictably while their own supply is collapsing, which is exactly when a lighting circuit "
            "must stay off, so the decision is given to a part designed for it."
        ),
        "related": ["U19", "R42", "U1", "C44", "U17", "R41", "R39"],
        "claims": [
            {"kind": "documented", "evidence": INTENT,
             "text": "Its delay pin is left open, which selects the datasheet's 12-28 ms delay.",
             "basis": "board.json pins for U18 and the part's datasheet"},
            {"kind": "documented", "evidence": MODEL,
             "text": "The trip point is nominally 3.07 V, and a conservative maximum rising threshold of "
                     "3.193951 V leaves only about 24 mV above the radio module's 3.0 V minimum. That is "
                     "arithmetic on datasheet limits, not a measurement.",
             "basis": "engineering-history/rev_a_inhibit_correction.md"},
        ],
        "open": [
            "Real falling-edge timing and reset recovery are hardware observations that have not been made.",
            "No finite detector can guarantee a response before 3.0 V for an arbitrarily fast collapse.",
        ],
    },

    "U19": {
        "name": "Schmitt AND gate: the SAFE decision",
        "circuit": "gating",
        "here": (
            "Produces LIGHT_ENABLE_SAFE from LIGHT_REQUEST_ARMED and READY_3V3. This is the single node the "
            "whole lighting side hangs on: it enables the gate-bias switch, releases the spotlight supply "
            "through U14's shutdown pin, and, inverted by U6, enables the expanders' outputs."
        ),
        "how": (
            "A Schmitt-trigger input has different thresholds for rising and falling edges, so a slow or noisy "
            "input still produces one clean transition instead of chattering. That matters here because the "
            "reset network feeding this gate rises slowly. A plain AND gate was rejected for exactly this "
            "reason: its input-transition-rate limit is violated by that slow edge."
        ),
        "related": ["U18", "U5", "U13", "U14", "U6", "R514", "C45"],
        "claims": [
            {"kind": "documented", "evidence": INTENT,
             "text": "This configurable gate is wired as an AND: pin 1 is IN1 tied to ground and pin 3 is IN0. An "
                     "earlier note that swapped those two pins is superseded.",
             "basis": "engineering-history/rev_a_inhibit_correction.md"},
            {"kind": "documented", "evidence": INTENT,
             "text": "SAFE gates lighting only. It does not remove motor power, and it is not an independent "
                     "watchdog on the controller. Firmware must reinitialise and be armed again after a supply "
                     "fault; no lighting command may be silently restored.",
             "basis": "hardware-current/engineering (inhibit correction) and ENGINEERING-CONTEXT"},
        ],
        "open": ["The gate's behaviour is not guaranteed by its datasheet while the 3.3 V rail is between 0 and "
                 "1.65 V, so the collapse region is reasoned about rather than specified."],
    },

    # ---------------------------------------------------------------- input protection
    "J1": {
        "name": "24 V input terminal",
        "circuit": "input",
        "here": (
            "The board's only power inlet. Contact 1 is VIN24_RAW and contact 2 is GND. Everything on the "
            "fixture is fed from here, through F1 and the reverse-blocking and eFuse stage, before it becomes "
            "the protected bus."
        ),
        "how": (
            "A spring-cage terminal: the stripped wire pushes straight into the opening and a spring clamps it, "
            "so there is no mating plug to buy or crimp. The external supply is a separate unit -- mains never "
            "reaches this PCB."
        ),
        "related": ["F1", "D500", "Q500", "U12", "TP2", "J16"],
        "claims": [
            {"kind": "documented", "evidence": INTENT,
             "text": "Use 0.5 mm2 / AWG20 conductors with a 6 mm strip length, and verify the exact wire "
                     "preparation against the manufacturer's data.",
             "basis": "hardware-current/manufacturing/enclosure_assembly_notes.md"},
            {"kind": "documented", "evidence": INTENT,
             "text": "The connector's 6 A nominal rating is not permission to run this board at 6 A. The initial "
                     "commissioning envelope is 4 A for the whole board.",
             "basis": "hardware-current/manufacturing/enclosure_assembly_notes.md and enclosure_addendum.md"},
            {"kind": "documented", "evidence": INTENT,
             "text": "This port mates upward, out of the front face -- perpendicular to the board, not toward any "
                     "edge.",
             "basis": "hardware-current/reports/mechanical-final-audit.json (port mating faces)"},
        ],
        "open": ["Confirm the physical contact numbering on the assembled unit before applying power."],
        "inspect": "Confirm contact 1 really is the positive terminal on the board in front of you before wiring it.",
    },

    "D500": {
        "name": "Input transient suppressor",
        "circuit": "input",
        "here": (
            "Sits across VIN24_FUSED and ground, right where the supply enters, to clamp voltage spikes coming "
            "in on the cable before they reach the reverse-blocking transistor and the eFuse."
        ),
        "how": (
            "A transient-voltage-suppression diode is normally an open circuit, but conducts hard once the "
            "voltage across it exceeds its rated standoff, dumping the spike's energy instead of letting it pass "
            "downstream. This one is bidirectional, so it clamps spikes of either polarity."
        ),
        "related": ["F1", "Q500", "U501", "U500", "C501"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "Its specified clamping voltage at the rated pulse current is 53.3 V, which is why "
                            "local flat-clamp devices were added downstream: 53 V is far too high to treat the "
                            "spotlight driver's 40 V input limit as protected by this part alone.",
                    "basis": "engineering-history/bom_audit.md"}],
        "open": ["This is a pulse device. It is not a brake and not a continuous energy sink."],
    },

    "Q500": {
        "name": "Reverse-blocking transistor",
        "circuit": "input",
        "here": (
            "Sits in the positive path between VIN24_FUSED and VIN24_RPP, driven by the eFuse through "
            "EFUSE_BGATE. If the supply is connected backwards it stays off, so nothing downstream sees reverse "
            "voltage."
        ),
        "how": (
            "A MOSFET conducts in one direction only when its gate is driven, but its body diode conducts the "
            "other way regardless -- so orientation matters. Facing it this way and having the eFuse control the "
            "gate gives a blocking switch that also drops far less voltage than a plain series diode would."
        ),
        "related": ["U12", "Q501", "C502", "D500", "F1"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "A 100 V part was chosen deliberately. A 60 V alternative was rejected because a "
                            "negative clamped input and a charged output can add across the blocking transistor.",
                    "basis": "engineering-history/bom_audit.md and design_parts.json (Q500 notes)"}],
        "open": [],
        "assembly": ["The footprint merges the physical drain terminals and the exposed drain into one pad; "
                     "orientation and land pattern were flagged for inspection before release."],
    },

    "Q501": {
        "name": "Reverse gate pull-down",
        "circuit": "input",
        "here": (
            "Pulls EFUSE_BGATE down quickly to VIN24_FUSED when the eFuse asserts EFUSE_DRV, so the "
            "reverse-blocking transistor turns off fast rather than coasting."
        ),
        "how": (
            "Turning a power MOSFET off means removing the charge on its gate. Doing that through a small "
            "signal transistor is much faster than relying on a resistor, and speed is the point when the "
            "purpose is to stop reverse current."
        ),
        "related": ["Q500", "U12"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "Its gate is driven by the eFuse, not by firmware. Turning the blocking "
                            "transistor off quickly is the whole reason this part exists: a resistor alone "
                            "would let the gate coast down while reverse current flowed.",
                    "basis": "hardware-current/engineering/design_parts.json (Q501 notes)"}],
        "open": [],
    },

    "U12": {
        "name": "24 V eFuse (the main protection chip)",
        "circuit": "input",
        "here": (
            "The board's real protection. It takes VIN24_RPP, controls the reverse-blocking transistor through "
            "EFUSE_BGATE and EFUSE_DRV, and produces the protected bus V24_BUS on pins 17 and 18. Its "
            "behaviour is programmed by the resistors around it: R500 sets the current limit, R501/R502 the "
            "undervoltage lockout, R503/R504 the overvoltage cutoff, R505/R506 the power-good threshold, and "
            "C503 the output ramp rate."
        ),
        "how": (
            "An eFuse is an electronic circuit breaker. Unlike a wire fuse it limits current actively, ramps its "
            "output up gently so a large capacitance does not draw a huge inrush, watches for over- and "
            "undervoltage, and reports what it sees. Where a fuse is a one-shot weak link, this is a switch with "
            "opinions -- and here it is the part that decides what the board may draw."
        ),
        "related": ["Q500", "Q501", "R500", "R501", "R502", "R503", "R504", "R505", "R506",
                    "R507", "R508", "R509", "C503", "C504", "TP8"],
        "claims": [
            {"kind": "documented", "evidence": MODEL,
             "text": "R500 at 4.02 kOhm sets a functional threshold of roughly 4.14-4.86 A once tolerance is "
                     "included. That is a calculation from the datasheet, and it is not a guaranteed "
                     "instantaneous maximum or a statement about the board's ampacity.",
             "basis": "engineering-history/power_review.md"},
            {"kind": "documented", "evidence": INTENT,
             "text": "Its mode pin is left open, which selects current-limit-then-latch-off. After a latched "
                     "fault the part is reset only by grounding the reset test point; never power its shutdown "
                     "pin from the downstream 3.3 V rail.",
             "basis": "hardware-current/engineering/design_parts.json (U12 notes)"},
            {"kind": "documented", "evidence": INTENT,
             "text": "The power-good output goes only to its pull-up R509. It does not reach the controller and "
                     "does not gate anything downstream.",
             "basis": "board.json nets for EFUSE_PGOOD"},
            {"kind": "documented", "evidence": MODEL,
             "text": "C503 gives a typical 49.9 ms output ramp, which charges the nominal 1000 uF bulk capacitor "
                     "at roughly 0.48 A. A very low supply current limit can therefore prevent normal startup, "
                     "and that is not evidence of a board fault.",
             "basis": "engineering-history/first_hardware_checklist.md"},
        ],
        "open": ["Pins 11 and 19 to 24 are deliberately unconnected.",
                 "No powered test of the protection behaviour has been performed."],
        "assembly": ["VQFN-24 on 0.5 mm pitch with a thermal pad; the pad is defined by eleven physical shapes, "
                     "nine of which are thermal vias."],
    },

    "C503": {
        "name": "eFuse output ramp capacitor",
        "circuit": "input",
        "here": (
            "Sets how quickly the eFuse ramps V24_BUS up at startup, between EFUSE_DVDT and ground. It is the "
            "reason the bulk capacitor charges gently instead of slamming the supply with an inrush."
        ),
        "how": (
            "The chip charges this capacitor with a fixed current, and its output voltage follows that ramp. A "
            "bigger capacitor means a slower, gentler start. Without a controlled ramp, switching on a large "
            "bulk capacitor looks like a short circuit for a few milliseconds."
        ),
        "related": ["U12", "C504"],
        "claims": [{"kind": "documented", "evidence": MODEL,
                    "text": "The typical ramp is about 49.9 ms, charging 1000 uF at roughly 0.48 A; a plus-20 % "
                            "bulk sensitivity alone is about 0.58 A, before logic demand.",
                    "basis": "engineering-history/first_hardware_checklist.md"}],
        "open": [],
    },

    # ---------------------------------------------------------------- protected bus
    "C504": {
        "name": "Bulk capacitor on the protected bus",
        "circuit": "bus",
        "here": (
            "The 1000 uF can on the back of the board, between V24_BUS and ground. It is the local energy store "
            "that absorbs the motors' current spikes so the external supply and the cable do not have to follow "
            "them."
        ),
        "how": (
            "An electrolytic capacitor stores far more energy per unit volume than a ceramic one, which is what "
            "you want for slow, large demands. It is polarised: fitted backwards it will fail, sometimes "
            "violently, so its polarity marking has to match the board."
        ),
        "related": ["U12", "U501", "D505", "J16", "J12", "J13"],
        "claims": [
            {"kind": "documented", "evidence": MODEL,
             "text": "At 24 V this capacitor stores about 0.288 J. For scale, dumping 0.1 J into an ideal "
                     "unloaded bus would raise it to about 27.9 V and 0.4 J to about 37.1 V -- which is why it "
                     "cannot be treated as a sink for motor regeneration.",
             "basis": "engineering-history/power_review.md"},
        ],
        "open": ["Whether the motors' regenerative energy has anywhere to go is an open hardware question. Do "
                 "not rely on this capacitor, the transient suppressors or a reverse-blocked supply to absorb it."],
        "assembly": [
            "Provisional engineering-derived land pattern: the manufacturer publishes termination dimensions but "
            "no recommended land, and the footprint has no paste apertures.",
            "The part's profile allows one reflow at 230 C peak for at most 5 s, so it is a factory controlled "
            "final installation after ordinary two-sided reflow, not a part that rides through both passes.",
        ],
        "inspect": "Check polarity and seating before power. This is the part whose orientation matters most.",
    },

    "D505": {
        "name": "Bus negative-transient diode",
        "circuit": "bus",
        "here": (
            "Cathode on V24_BUS, anode on ground. It bounds how far the protected bus can be driven below "
            "ground by a transient -- for instance when an inductive load is disconnected."
        ),
        "how": (
            "A diode conducts in one direction only. Facing it this way, it does nothing at all in normal "
            "operation and conducts only if the rail is pushed negative, clamping the excursion to about one "
            "diode drop below ground."
        ),
        "related": ["C504", "U501", "U12"],
        "claims": [],
        "open": ["Bounded negative excursions only. This is not a regenerative brake."],
    },

    "U501": {
        "name": "Flat clamp on the protected bus",
        "circuit": "bus",
        "here": (
            "A 27 V transient protector across V24_BUS and ground, placed beside the bulk capacitor and the "
            "motor branch entry -- the point where a motor transient would arrive."
        ),
        "how": (
            "An ordinary suppressor's clamping voltage rises steeply with current; a flat-clamp device holds a "
            "much tighter voltage across its whole current range. That matters here because the parts "
            "downstream have a 40 V-class limit and the input suppressor alone clamps at 53 V."
        ),
        "related": ["C504", "D505", "U500", "D500"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "Rated 27 V standoff with a 35 V maximum clamp at 35 A for an 8/20 us pulse. Its DC "
                            "breakdown current limit is 12 mA, which explicitly excludes continuous braking.",
                    "basis": "engineering-history/power_review.md and bom_audit.md"}],
        "open": ["Motor regeneration remains a separate qualification. This part is a pulse device."],
        "assembly": ["WSON-6 with a thermal pad; the pad and all ground pins need short, wide connections and "
                     "dense stitching."],
    },

    "J16": {
        "name": "Protected-bus service port",
        "circuit": "bus",
        "here": (
            "A two-way connector exposing V24_BUS and ground on the front face, intended as the connection "
            "point for a separately designed brake for the motors."
        ),
        "how": (
            "It is a tap on the protected bus, downstream of the eFuse, so anything connected here is inside the "
            "board's protection. It is a connection point, not an installed brake."
        ),
        "related": ["C504", "U501", "U12", "J12", "J13"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "An external brake needs a controlled chopper. A bare resistor across this port is "
                            "not a brake and is not what this connector is for.",
                    "basis": "hardware-current/manufacturing/enclosure_assembly_notes.md"}],
        "open": ["The brake itself is not designed, and the motors' regenerative behaviour is unmeasured."],
    },

    # ---------------------------------------------------------------- conversion
    "U10": {
        "name": "24 V to 5 V converter",
        "circuit": "buck5",
        "here": (
            "Makes the +5V rail from V24_LOGIC, the fused logic branch. It switches through BUCK5_SW into "
            "L500, senses its output through the R510/R511 divider on BUCK5_FB, and reports readiness on "
            "BUCK5_PGOOD."
        ),
        "how": (
            "A buck converter chops its input on and off rapidly and lets an inductor and capacitor average the "
            "result into a lower, steady voltage. Because it switches rather than burning off the difference as "
            "heat, it wastes far less energy than a linear regulator -- which matters when stepping 24 V down."
        ),
        "related": ["L500", "C506", "C507", "C508", "C509", "C510", "C511", "R510", "R511", "R512", "U11", "F11"],
        "claims": [
            {"kind": "documented", "evidence": INTENT,
             "text": "The 5 V budget is about 0.8 A in total, counting the 3.3 V converter's input draw and the "
                     "CAN transceiver. That is not 0.8 A of spare accessory power.",
             "basis": "hardware-current/engineering (power review)"},
            {"kind": "documented", "evidence": INTENT,
             "text": "The 400 kHz adjustable variant, with its enable tied to the input as the datasheet "
                     "prescribes. No USB supply is connected to this rail.",
             "basis": "hardware-current/engineering/design_parts.json (U10 note)"},
        ],
        "open": [
            "The coupled startup of this converter and the 3.3 V converter was never qualified: the exact vendor "
            "model would not run in the available simulator.",
            "A high-capacitance startup sensitivity requests a 1.526 A source peak in the isolated model. That "
            "does not predict this converter tripping; the real coupled behaviour is a bench question.",
        ],
        "assembly": ["SO PowerPAD-8 with a thermal pad and eight 0.2 mm vias, four of them beneath the paste. "
                     "The factory's via treatment for that pad is a declared hold point -- ordinary mask tenting "
                     "is not evidence of a sealed, solderable surface."],
    },

    "C509": {
        "name": "Bootstrap capacitor",
        "circuit": "buck5",
        "here": (
            "The only capacitor on the board that is not referenced to ground: it sits between BUCK5_BOOT and "
            "BUCK5_SW, riding on the 5 V converter's switching node."
        ),
        "how": (
            "The converter's high-side switch needs a gate voltage above its own source, and that source moves "
            "up and down with the switching node. A bootstrap capacitor is charged while the node is low and "
            "then floats up with it, carrying its charge along to supply the gate drive."
        ),
        "related": ["U10", "L500", "C508"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "This is the only capacitor on the board that is not referenced to ground: it "
                            "rides on the switching node, so probing it against ground during bring-up gives "
                            "a misleading reading.",
                    "basis": "board.json nets for C509"}],
        "open": [],
    },

    "L500": {
        "name": "5 V converter inductor",
        "circuit": "buck5",
        "here": (
            "The energy-storage inductor for the 5 V converter, between the switching node BUCK5_SW and the "
            "+5V rail. All of the 5 V rail's current passes through it."
        ),
        "how": (
            "In a buck converter the inductor is what makes the averaging work: it stores energy while the "
            "switch is on and releases it while the switch is off, so the output sees a nearly steady current "
            "even though the input is being chopped."
        ),
        "related": ["U10", "C510", "C511"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "Rated 2.5 A RMS with 5.5 A saturation and at most 0.170 Ohm of winding resistance.",
                    "basis": "hardware-current/engineering/design_parts.json"}],
        "open": [],
        "assembly": ["Custom land pattern derived from the manufacturer's drawing: the catalogue's 2.5 mm figure "
                     "is the gap between lands, not the pad width."],
    },

    "U11": {
        "name": "5 V to 3.3 V converter",
        "circuit": "buck3",
        "here": (
            "Makes +3V3 -- the rail the controller, both expanders, all the logic and the temperature sensor run "
            "from -- out of +5V. It switches through BUCK3_SW into L501 and senses its own output directly, "
            "reporting readiness on BUCK3_PGOOD."
        ),
        "how": (
            "Another buck converter, but a fixed-output version: instead of an external feedback divider it "
            "senses the rail directly through its output-sense pin, so there is no divider to get wrong."
        ),
        "related": ["L501", "C512", "C513", "R513", "U10", "U18"],
        "claims": [
            {"kind": "documented", "evidence": INTENT,
             "text": "The fixed 3.3 V variant: its feedback pin is grounded and the output-sense pin sits on the "
                     "regulated rail. There is no feedback divider.",
             "basis": "hardware-current/engineering/design_parts.json (U11 note)"},
            {"kind": "documented", "evidence": INTENT,
             "text": "The design reserves 0.6 A on the 3.3 V rail, within a 1 A ceiling for the part.",
             "basis": "hardware-current/engineering/design_parts.json"},
        ],
        "open": ["Five corrected isolated cases passed the declared rail screen in simulation, but the coupled "
                 "startup with the 5 V converter was not qualified."],
        "assembly": ["WSON-8, 2 x 2 mm, with a thermal pad."],
    },

    "L501": {
        "name": "3.3 V converter inductor",
        "circuit": "buck3",
        "here": (
            "The energy-storage inductor for the 3.3 V converter, between BUCK3_SW and the +3V3 rail that "
            "supplies all the logic on this board."
        ),
        "how": (
            "The same role as the 5 V converter's inductor: it smooths the chopped switching node into a steady "
            "current. It is physically smaller because this converter runs at a higher frequency and a lower "
            "voltage step."
        ),
        "related": ["U11", "C513"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "Rated 2.9 A RMS with 3 A saturation and at most 0.044 Ohm of winding resistance.",
                    "basis": "hardware-current/engineering/design_parts.json"}],
        "open": [],
    },

    # ---------------------------------------------------------------- spotlight supply
    "U14": {
        "name": "Spotlight supply eFuse",
        "circuit": "spot_supply",
        "here": (
            "Gates the spotlight rail. It takes V24_BUS and produces V24_SPOT for the three drivers, but only "
            "while LIGHT_ENABLE_SAFE is asserted on its shutdown pin -- so the spotlights lose their supply "
            "entirely, not just their control signal, when the board is not safe to light."
        ),
        "how": (
            "The same kind of electronic breaker as the main eFuse, with its own current limit set by R515 and "
            "its own overvoltage cutoff from R517/R518. Cutting the supply as well as the signal means a "
            "software fault or a stuck driver cannot light the spotlights while the board is disarmed."
        ),
        "related": ["U19", "R514", "R515", "R516", "R517", "R518", "R519", "R520", "R521",
                    "C516", "C517", "C518", "D501", "U500", "U7", "U8", "U9", "TP9"],
        "claims": [
            {"kind": "documented", "evidence": MODEL,
             "text": "R515 at 24.3 kOhm sets a current limit of about 0.494 A nominal.",
             "basis": "engineering-history/power_review.md"},
            {"kind": "documented", "evidence": INTENT,
             "text": "Its return, SPOT_RTN, is a separate island and is never tied directly to ground. The "
                     "exposed pad under this part is on that return, not on ground -- an important difference "
                     "when inspecting or reworking it.",
             "basis": "hardware-current/engineering/design_parts.json (U14 notes)"},
            {"kind": "documented", "evidence": INTENT,
             "text": "Its shutdown pin shares the 4.7 kOhm pull-down R514 with the gate-bias switch, so both "
                     "halves of the lighting inhibit fail to the same safe state.",
             "basis": "engineering-history/rev_a_inhibit_correction.md"},
        ],
        "open": ["Pins 4 and 13 are deliberately unconnected.",
                 "The inhibit thresholds are datasheet limits and calculations; none has been observed."],
        "assembly": ["HTSSOP-16 with a 3.3 x 3.3 mm thermal pad and six 0.2 mm vias beneath the paste. The "
                     "factory's via treatment and mask registration at the pad's chamfers are declared hold "
                     "points."],
    },

    "C516": {
        "name": "Spotlight eFuse ramp capacitor",
        "circuit": "spot_supply",
        "here": (
            "Sets how quickly V24_SPOT ramps up when lighting is enabled, between SPOT_EFUSE_DVDT and "
            "SPOT_RTN. Note the return: like the rest of that eFuse's small signals it references the spotlight "
            "return island, not ground."
        ),
        "how": (
            "As with the main eFuse, the chip charges this capacitor at a fixed current and its output follows "
            "that ramp, so the three drivers' input capacitors charge gently rather than as an inrush."
        ),
        "related": ["U14", "C519", "C521", "C523"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "It returns to SPOT_RTN, the spotlight eFuse's own island, not to ground. That "
                            "island is deliberately kept separate, so measuring anything on this part against "
                            "board ground is the wrong reference.",
                    "basis": "hardware-current/engineering/design_parts.json (U14 notes)"}],
        "open": [],
    },

    "D501": {
        "name": "Spotlight rail negative-transient diode",
        "circuit": "spot_supply",
        "here": (
            "Cathode on V24_SPOT and anode on ground, bounding how far the spotlight rail can be driven "
            "below ground. The three drivers switch inductive loads through long LED leads, which is "
            "exactly the arrangement that produces negative excursions on a rail."
        ),
        "how": (
            "Like the bus diode, it does nothing in normal operation and conducts only if the rail is pushed "
            "negative, which switching converters and long LED leads can do at the moment they turn off."
        ),
        "related": ["U14", "U500", "R521"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "Cathode on the rail, anode on ground: it does nothing in normal operation and "
                            "conducts only on a negative excursion. Fitted the other way round it would short "
                            "the spotlight supply.",
                    "basis": "board.json nets for D501"}],
        "open": [],
    },

    "U500": {
        "name": "Flat clamp on the spotlight rail",
        "circuit": "spot_supply",
        "here": (
            "A 27 V transient protector across V24_SPOT and ground, beside the spotlight drivers' decoupling. "
            "The drivers have a 40 V-class input limit, so a 53 V clamp at the board input is not enough on its "
            "own."
        ),
        "how": (
            "Same flat-clamp behaviour as the one on the bus: it holds a much tighter voltage across its current "
            "range than an ordinary suppressor, keeping transients inside the drivers' rating."
        ),
        "related": ["U14", "D501", "U7", "U8", "U9", "U501"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "27 V standoff, 35 V maximum clamp at 35 A for an 8/20 us pulse, and a 12 mA DC "
                            "breakdown limit that excludes continuous braking.",
                    "basis": "engineering-history/power_review.md"}],
        "open": [],
        "assembly": ["WSON-6 with a thermal pad."],
    },

    # ---------------------------------------------------------------- CAN
    "U4": {
        "name": "CAN transceiver",
        "circuit": "can",
        "here": (
            "Translates the controller's logic-level CAN_TX and CAN_RX into the differential pair CAN_H and "
            "CAN_L that leaves the board on the two motor connectors. It runs from +5V for the bus side and "
            "takes +3V3 on its logic-reference pin so it speaks the controller's voltage."
        ),
        "how": (
            "CAN sends each bit as the difference between two wires rather than as a voltage against ground, so "
            "interference that hits both wires equally cancels out. That is why it survives motor cabling. The "
            "transceiver is the part that drives and reads that differential pair."
        ),
        "related": ["U1", "U16", "R20", "R21", "R22", "JP1", "J12", "J13", "C20", "C21", "C22"],
        "claims": [
            {"kind": "documented", "evidence": INTENT,
             "text": "This board powers the smart motors and talks to them over CAN. It does not implement the "
                     "motors' internal drive electronics.",
             "basis": "ENGINEERING-CONTEXT (control paths)"},
            {"kind": "documented", "evidence": INTENT,
             "text": "The interface contract gives the motors CAN identifiers 0x141 for pan and 0x142 for tilt, "
                     "at a nominal 1 Mbit/s.",
             "basis": "engineering-history (interface contract) and ENGINEERING-CONTEXT"},
        ],
        "open": ["Bus signal integrity, cable topology and radio immunity with everything switching are "
                 "unmeasured."],
    },

    "U16": {
        "name": "CAN bus transient clamp",
        "circuit": "can",
        "here": (
            "A protection array across CAN_H and CAN_L to ground, guarding the transceiver's bus pins "
            "where the harness leaves the board through the two motor connectors. Bus wiring runs "
            "outside the enclosure alongside motor power, so it is the most exposed pair on the board."
        ),
        "how": (
            "Two suppression diodes referenced to ground. In normal operation they are invisible to the bus; "
            "during a transient they conduct and hold the bus pins inside the transceiver's limits. They "
            "reference ground only -- no rail feeds them."
        ),
        "related": ["U4", "J12", "J13"],
        "claims": [],
        "open": ["Electrostatic-discharge immunity has not been tested."],
    },

    "J12": {
        "name": "Motor 1 connector",
        "circuit": "can",
        "here": (
            "Motor 1's whole connection: contact 1 is V24_MOTOR1 from fuse F2, contact 2 is ground, and "
            "contacts 3 and 4 are CAN_H and CAN_L. It mates downward, out of the back face."
        ),
        "how": (
            "The smart motor takes power and a data bus over one four-way cable and does its own drive and "
            "encoder work internally. Keep the CAN pair twisted; the power pair should be the heavier gauge."
        ),
        "related": ["F2", "U4", "J13", "R22", "JP1", "C504"],
        "claims": [
            {"kind": "documented", "evidence": INTENT,
             "text": "Mating housing PAP-04V-S with SPHD-001T-P0.5 contacts; select AWG22 for the motor leads. "
                     "Two housings and eight contacts per fully cabled board.",
             "basis": "hardware-current/manufacturing/enclosure_assembly_notes.md"},
            {"kind": "documented", "evidence": INTENT,
             "text": "The connector's 3 A rating with AWG22 does not lift the 1 A branch fuse, and the initial "
                     "commissioning limit is 0.75 A per motor.",
             "basis": "hardware-current/engineering/enclosure_addendum.md"},
        ],
        "open": ["Motor regeneration into this port is an open hardware question."],
        "inspect": "This connector is rotated on the board -- check contact numbering against the assembly drawing, not against the board's edge.",
    },

    "J13": {
        "name": "Motor 2 connector",
        "circuit": "can",
        "here": (
            "Motor 2's connection, identical in shape to motor 1's: contact 1 is V24_MOTOR2 from fuse F3, "
            "contact 2 is ground, contacts 3 and 4 are the shared CAN_H and CAN_L pair. It mates downward, out "
            "of the back face."
        ),
        "how": (
            "Both motors sit on the same CAN bus and are told apart by their identifiers, not by their wiring. "
            "The two power feeds are separately fused so a fault in one motor does not take the other down."
        ),
        "related": ["F3", "U4", "J12", "R22", "JP1"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "Mating housing PAP-04V-S with SPHD-001T-P0.5 contacts; AWG22 for the motor leads, "
                            "CAN_H and CAN_L kept as a twisted pair.",
                    "basis": "hardware-current/manufacturing/enclosure_assembly_notes.md"}],
        "open": ["Motor regeneration into this port is an open hardware question."],
        "inspect": "Rotated the opposite way from J12 -- confirm contact numbering before wiring.",
    },

    # ---------------------------------------------------------------- USB island
    "J14": {
        "name": "USB-C connector",
        "circuit": "usb",
        "here": (
            "The programming and serial port. It brings in USB_VBUS -- which powers only the small sensing and "
            "isolation island, never the controller -- the data pair USB_DP_HOST and USB_DM_HOST, and the two "
            "configuration lines USB_CC1 and USB_CC2 that tell a host this board is a device."
        ),
        "how": (
            "USB-C is reversible, so the data pair appears twice in the connector and both copies are wired "
            "together here. This board is self-powered: it still needs external 24 V while USB is connected, "
            "because USB only supplies the island."
        ),
        "related": ["U15", "U17", "D30", "C30", "C31", "R30", "R31", "Q30", "R40", "R36"],
        "claims": [
            {"kind": "documented", "evidence": INTENT,
             "text": "Self-powered: USB_VBUS is used for sensing and for the data mux's supply only, and is never "
                     "tied to the 5 V or 3.3 V rails.",
             "basis": "hardware-current/engineering/design_parts.json (J14 note)"},
            {"kind": "documented", "evidence": INTENT,
             "text": "Its two SBU contacts are deliberately unconnected.",
             "basis": "board.json pins for J14"},
            {"kind": "documented", "evidence": CAD,
             "text": "Its four shield stakes are plated through-hole slots that must be soldered, plus two "
                     "unplated locating pegs. Zero through-hole component packages does not mean zero "
                     "through-hole solder joints.",
             "basis": "hardware-current/reports/drilled-solder-candidate.json and enclosure_assembly_notes.md"},
        ],
        "open": [
            "The 90 Ohm differential geometry for the USB pair is a request to the factory, not an accepted "
            "stack-up. Thirteen modelled two-dimensional cases on the native geometry spread from 71 to 114 Ohm.",
            "No USB certification, enumeration test or electrostatic-discharge test has been performed.",
        ],
        "assembly": ["The shield slots must keep their geometry and plating and must not be filled or capped."],
        "inspect": "Check that all four shield stakes are soldered, not just tacked, and that the slots are open.",
    },

    "U15": {
        "name": "USB data-line protection",
        "circuit": "usb",
        "here": (
            "Clamps transients on the host-side data pair USB_DM_HOST and USB_DP_HOST to ground, right where the "
            "cable arrives. It sits on the connector side of the data mux, so it protects the port whether or "
            "not the controller's own data lines are currently connected."
        ),
        "how": (
            "A pair of low-capacitance suppression diodes referenced to ground only. Low capacitance matters: "
            "anything hung on a high-speed data line slows its edges. This part has no supply pin, and that is "
            "the point -- see the claim below."
        ),
        "related": ["J14", "U17", "D30"],
        "claims": [{"kind": "documented", "evidence": HIST,
                    "text": "This replaced a part whose internal steering diodes tied to a local 5 V rail. In "
                            "that arrangement a host driving the data lines could push current into an absent "
                            "local supply; a simulation of the old circuit put roughly 2.5 V on a rail that "
                            "should have been dead. The replacement references ground only, so that path does "
                            "not exist.",
                    "basis": "engineering-history/rev_a_usb_correction.md",
                    "bound_to": "8959b828",
                    "source_file": "engineering-history/partial_power_review.md"}],
        "open": ["Pins 1 and 3 are deliberately unconnected.",
                 "Electrostatic-discharge immunity has not been tested."],
    },

    "D30": {
        "name": "USB bus-voltage protection",
        "circuit": "usb",
        "here": (
            "A dedicated clamp on USB_VBUS to ground, protecting the small USB island's supply where the "
            "cable arrives. The island is the only thing USB powers on this board, so this diode guards "
            "the presence-sense network and the data mux rather than any board rail."
        ),
        "how": (
            "A single-line suppression diode: invisible in normal operation, conducting during a transient. "
            "The data lines get their own protection separately, because their capacitance budget is tighter."
        ),
        "related": ["J14", "C30", "R40", "U17"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "The bus voltage gets its own clamp because the data lines' protection has a much "
                            "tighter capacitance budget: anything hung on a high-speed pair slows its edges.",
                    "basis": "engineering-history/rev_a_usb_correction.md"}],
        "open": ["Electrostatic-discharge immunity has not been tested."],
    },

    "Q30": {
        "name": "USB presence sensor",
        "circuit": "usb",
        "here": (
            "Tells the controller whether a USB host is plugged in. R34 and R35 divide USB_VBUS into "
            "USB_SENSE_BASE, which drives this transistor's base; its collector pulls USB_PRESENT_N down "
            "against R36 when a host is present."
        ),
        "how": (
            "A bipolar transistor conducts between collector and emitter in proportion to the small current "
            "into its base. Used as a switch like this, it converts 'is there 5 V on the cable?' into a clean "
            "logic level -- without connecting the two power domains, which a simple divider to a GPIO would do."
        ),
        "related": ["R34", "R35", "R36", "J14", "U17", "U1", "R40"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "USB sensing only: no host power reaches the logic supply through this path.",
                    "basis": "hardware-current/engineering/design_parts.json (Q30 note)"}],
        "open": ["Unplug timing was modelled across a range of transistor gains, giving 1.8 to 2.5 ms before the "
                 "signal releases. That is a model, not a measurement."],
    },

    "U17": {
        "name": "USB data multiplexer",
        "circuit": "usb",
        "here": (
            "Decides what the controller's USB data lines are connected to. While READY_3V3 is low -- meaning "
            "the 3.3 V rail is not qualified -- it parks USB_DP and USB_DM on the grounded resistors R37 and "
            "R38. Once the rail is qualified, the divider R41/R39 raises USB_READY_SELECT and it connects the "
            "host pair instead. It is powered from USB_VBUS, not from a board rail."
        ),
        "how": (
            "An analogue switch: it physically connects one of two pairs of pins to a common pair, like a "
            "railway point. Parking the controller's data lines on grounded resistors until its supply is "
            "healthy stops a plugged-in host from feeding current into a board that is not powered."
        ),
        "related": ["J14", "U15", "U18", "R37", "R38", "R39", "R41", "C31", "R32", "R33", "Q30"],
        "claims": [
            {"kind": "documented", "evidence": INTENT,
             "text": "Select low chooses the grounded parking pair; select high chooses the host pair; the "
                     "output-enable pin high isolates both. It is powered from the host's bus voltage, not from "
                     "local rails.",
             "basis": "hardware-current/engineering/design_parts.json (U17 note)"},
            {"kind": "documented", "evidence": MODEL,
             "text": "The select divider's calculated corners are at most 0.347 V for a definite low and at "
                     "least 1.719 V for a definite high, against the part's 0.39 V and 0.77 V limits.",
             "basis": "engineering-history/rev_a_usb_correction.md"},
        ],
        "open": [
            "The part's behaviour while its supply is between 0 and 1.62 V is not specified, so the "
            "partial-power region is reasoned about rather than guaranteed.",
            "Switch-overlap behaviour during selection was a sensitivity case in the model, not a vendor "
            "guarantee.",
        ],
        "assembly": ["UQFN-10, 1.4 x 1.8 mm on 0.4 mm pitch: the finest-pitch part on the board. Its local mask "
                     "webs and stencil registration are a declared review item, and its lands must not be "
                     "silently modified."],
    },

    # ---------------------------------------------------------------- sensor, service
    "U20": {
        "name": "Board temperature sensor",
        "circuit": "sensor",
        "here": (
            "A digital temperature sensor on the existing I2C bus at address 0x48, sharing I2C_SDA and I2C_SCL "
            "with the two PWM expanders. Its address pin is tied to ground to select that address, and its "
            "alert output is deliberately left unconnected."
        ),
        "how": (
            "It measures its own package temperature and reports a number over the bus, so no analogue input is "
            "needed. That means it reads the temperature of the PCB near where it sits -- not the air in the "
            "room, and not the temperature of the hottest part."
        ),
        "related": ["U1", "C46", "U2", "U3"],
        "claims": [
            {"kind": "documented", "evidence": INTENT,
             "text": "The implemented part is a digital I2C sensor, not a thermistor. Read register pointer 0 and "
                     "interpret the signed top 12 bits at 0.0625 C per count in normal mode.",
             "basis": "hardware-current/engineering/enclosure_addendum.md"},
            {"kind": "documented", "evidence": INTENT,
             "text": "Leaving the alert output floating is a documented deviation: the manufacturer's preference "
                     "for an unused alert is to ground it. The deviation is recorded rather than the hardware "
                     "changed.",
             "basis": "hardware-current/engineering/enclosure_addendum.md and ENGINEERING-CONTEXT"},
            {"kind": "documented", "evidence": INTENT,
             "text": "It is not an independent overtemperature cutoff. Nothing switches off because of it; "
                     "firmware decides what to do with the reading.",
             "basis": "ENGINEERING-CONTEXT"},
        ],
        "open": ["Compare it against a thermocouple during enclosure testing. Its relationship to the actual hot "
                 "spots is unknown until then."],
        "assembly": ["SOT-563, 1.6 x 1.2 mm."],
    },

    "S1": {
        "name": "RESET button",
        "circuit": "mcu",
        "here": (
            "Pulls MCU_EN to ground, restarting the controller. R1 and C1 hold that node high in normal "
            "operation, and the supervisor can pull it down through R42, so this button is one of three "
            "things that can put the module into reset."
        ),
        "how": (
            "The module restarts when its enable pin is pulled low and released. The capacitor on that node also "
            "gives a power-on delay, so the module comes out of reset after its supply has settled rather than "
            "during the rise."
        ),
        "related": ["U1", "R1", "C1", "R42", "U18", "S2"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "This button acts on the supervisor's output side through R42. It cannot override an "
                            "asserted supervisor, and releasing it does not restart the supervisor's own delay "
                            "timer.",
                    "basis": "engineering-history/rev_a_inhibit_correction.md"},
                   {"kind": "documented", "evidence": INTENT,
                    "text": "Firmware must reinitialise and require a fresh arming after every reset; no lighting "
                            "command may be automatically re-enabled.",
                    "basis": "engineering-history/rev_a_inhibit_correction.md"}],
        "open": [],
    },

    "S2": {
        "name": "BOOT button",
        "circuit": "mcu",
        "here": (
            "Pulls BOOT_GPIO9 to ground. Held down while the board is reset, it makes the module start in its "
            "built-in download mode instead of running the firmware in flash."
        ),
        "how": (
            "Boot straps are sampled once, as the module leaves reset. Holding this one low at that moment "
            "selects the bootloader, which is how a blank or broken board is recovered over USB."
        ),
        "related": ["U1", "R2", "R3", "S1", "J14"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "The strap is sampled only as the module leaves reset, so this button matters "
                            "during a reset and at no other time. R2 holds the line high the rest of the time.",
                    "basis": "hardware-current/engineering/enclosure_addendum.md"}],
        "open": [],
    },

    "J15": {
        "name": "UART service port",
        "circuit": "mcu",
        "here": (
            "A four-way service header carrying +3V3, ground and the serial pair: UART_TX is the board's output "
            "and UART_RX its input. It is the console when USB is not convenient."
        ),
        "how": (
            "A serial console needs the two lines crossed -- the board's transmit goes to the adapter's receive. "
            "This connector is deliberately a different size from the ambient strip connectors so a strip cable "
            "cannot be forced into it."
        ),
        "related": ["U1", "S1", "S2", "J17"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "3.3 V logic. The adapter must not drive the power contact; it is there to reference "
                            "or feed a low-power adapter, not to power the board.",
                    "basis": "hardware-current/engineering/design_parts.json (J15 note)"}],
        "open": [],
    },

    "J17": {
        "name": "ARM switch connector",
        "circuit": "gating",
        "here": (
            "Where the physical ARM switch plugs in: contact 1 is +3V3 and contact 2 is ARM. With nothing "
            "connected, R5 holds ARM low, so the board reads as disarmed."
        ),
        "how": (
            "The ARM signal is one of the two inputs to the AND gate that produces the lighting request, so a "
            "physical switch -- or the absence of one -- can veto lighting no matter what the firmware asks for. "
            "It ships open, which means disarmed."
        ),
        "related": ["R5", "U5", "U19", "U13", "U14"],
        "claims": [{"kind": "documented", "evidence": INTENT,
                    "text": "The connector is a different size from the ambient ports so a strip cable cannot be "
                            "plugged in here, and it ships open, which means disarmed.",
                    "basis": "hardware-current/manufacturing/enclosure_assembly_notes.md"}],
        "open": ["ARM gates lighting only. It does not remove motor power."],
    },
}

# Revision-specific changes: pin roles are still checked by the data builder.
UNIQUE["U5"]["name"] = "Schmitt-input spotlight permission gate"
UNIQUE["U5"]["here"] = "The Nexperia 74HCS08PWJ gates SPOT1_PWM, SPOT2_PWM and SPOT3_PWM with LIGHT_ENABLE_SAFE to drive the three spotlight CTRL paths. Its fourth gate ANDs LIGHT_ENABLE and ARM into LIGHT_REQUEST_ARMED. This replaces the earlier logic part; the three output pull-downs are now 910 ohm."
UNIQUE["U5"]["how"] = "Each AND gate requires both the spotlight request and the shared safety permission. Schmitt inputs provide hysteresis for a changing input level; they do not establish glitch-free power sequencing or a tested falling-edge waveform."
UNIQUE["U5"]["claims"] = [{"kind":"documented","evidence":CAD,"text":"Exact selection is 74HCS08PWJ with 910 ohm R526/R527/R528; logical pin parity passes on the final revision.","basis":"Current BOM, schematic and native pin parity"}]
UNIQUE["U5"]["open"] = ["Hardware timing, supply sequencing and off-state behavior remain unmeasured."]
UNIQUE["C504"]["assembly"] = ["AFK108M50P44T-F has a provisional custom land and intentionally no paste aperture. It permits one reflow: the factory must approve and perform final installation without exposing it to both board passes."]
