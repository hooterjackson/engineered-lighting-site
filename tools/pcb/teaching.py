"""Circuit-specific teaching content for every feature on LIGHT v0.2.

Nothing here is generic. Each entry is built from the component's actual pins
and nets in board.json, from the reviewed fact tables below (firmware channel
map, connector contacts, package notes, test-point expectations), or from the
hand-written entries in teaching_unique.py. The build cross-checks every fact
table against board.json and fails on any disagreement, so this file cannot
drift away from the design it describes.

Evidence vocabulary (see VOCAB): no claim about this PCB may ever be labelled
'measured' -- no LIGHT v0.2 board has been powered.
"""

import re

import teaching_unique

VOCAB = {
    "claim_kinds": {
        "documented": "recorded in the design sources or the part's datasheet",
        "inference": "derived here from the design data; the derivation is stated",
        "open": "not settled by anything in the design record",
    },
    "evidence": {
        "intended": "design intent -- what the circuit is meant to do",
        "cad-checked": "checked by a CAD rule run on this exact layout (ERC, DRC, parity, net continuity, drill/land, mechanical)",
        "modelled-current": "a calculation or solver run against this exact layout, under stated assumptions",
        "simulated-historical": "a simulation bound to an earlier board revision; kept for its reasoning, not relabelled as current",
        "measured": "never used on this page -- no LIGHT v0.2 board has been powered",
    },
}

LEGEND = (
    "Nothing on this page is a measurement of this PCB. No LIGHT v0.2 board has been "
    "powered, and no firmware has been built or flashed. A clean CAD check means the "
    "files pass specific design rules; it neither replaces measurements nor proves the "
    "circuit works."
)

CIRCUITS = {
    "input": "24 V entry and protection",
    "bus": "The protected 24 V bus",
    "branch": "Branch fuses",
    "buck5": "24 V to 5 V",
    "buck3": "5 V to 3.3 V",
    "mcu": "The controller",
    "pwm": "The two PWM expanders",
    "ambient": "Ambient zone channels",
    "spot_supply": "The gated spotlight supply",
    "spot": "Spotlight constant-current drivers",
    "gating": "ARM, supervisor and the SAFE chain",
    "can": "CAN and the motor ports",
    "usb": "The USB-C island",
    "sensor": "Board temperature",
    "expansion": "Expansion pads and boot straps",
    "mechanical": "Mounting",
    "test": "Test points",
}

FAMILIES = {
    "ambient_mosfet": ("Ambient channel switch", "ambient"),
    "ambient_gate_series": ("Ambient gate series resistor", "ambient"),
    "ambient_gate_pulldown": ("Ambient gate pull-down", "ambient"),
    "ambient_gate_pullup": ("Ambient gate pull-up", "ambient"),
    "zone_connector": ("Ambient zone connector", "ambient"),
    "zone_fuse": ("Ambient zone fuse", "branch"),
    "motor_fuse": ("Motor branch fuse", "branch"),
    "logic_fuse": ("Logic branch fuse", "branch"),
    "input_fuse": ("Input backup fuse", "input"),
    "spot_driver": ("Spotlight driver", "spot"),
    "spot_sense": ("Spotlight current-sense resistor", "spot"),
    "spot_inductor": ("Spotlight inductor", "spot"),
    "spot_diode": ("Spotlight catch diode", "spot"),
    "spot_ctrl_pulldown": ("Spotlight CTRL pull-down", "spot"),
    "spot_connector": ("Spotlight output connector", "spot"),
    "spot_input_cap": ("Spotlight driver input capacitor", "spot"),
    "decoupling": ("Decoupling capacitor", None),
    "bulk": ("Bulk reservoir capacitor", None),
    "divider": ("Resistive divider leg", None),
    "pullup": ("Pull-up resistor", None),
    "pulldown": ("Pull-down resistor", None),
    "setting": ("Setting resistor", None),
    "test_point": ("Test point", "test"),
    "boot_strap_probe": ("Boot-strap probe pad", "expansion"),
    "expansion_pads": ("Expansion solder pads", "expansion"),
    "mounting_hole": ("Mounting hole", "mechanical"),
    "jumper": ("Solder jumper", "can"),
    "unique": ("Named part", None),
}

# --- reviewed fact tables -------------------------------------------------
# logical channel -> (expander, LED output index, package pin)
# Source: engineering-history/firmware_port_map.md, cross-checked against board.json.
CHANNELS = {
    1: ("U2", 0, 6), 2: ("U2", 1, 7), 3: ("U2", 2, 8), 4: ("U2", 3, 9),
    5: ("U2", 4, 10), 6: ("U2", 5, 11), 7: ("U2", 6, 12), 8: ("U2", 7, 13),
    9: ("U2", 8, 15), 10: ("U2", 9, 16), 11: ("U2", 10, 17), 12: ("U2", 11, 18),
    13: ("U2", 12, 19), 14: ("U2", 13, 20), 15: ("U2", 14, 21),
    16: ("U3", 0, 6), 17: ("U3", 1, 7), 18: ("U3", 13, 20),
    19: ("U3", 3, 9), 20: ("U3", 12, 19), 21: ("U3", 5, 11),
}
REMAPPED = {18, 20}
COLOURS = {0: ("warm", "W"), 1: ("neutral", "N"), 2: ("cool", "C")}
ZONE_CONN = {1: "J2", 2: "J2", 3: "J2", 4: "J2", 5: "J2", 6: "J2", 7: "J8"}

def positive_contact(zone):
    return 1 if zone == 7 else [4,5,6,1,2,3].index(zone)*5+1

def channel_contact(channel):
    zone=(channel-1)//3+1
    return (channel-1)%3 + (2 if zone==7 else positive_contact(zone)+2)
ZONE_FUSE = {1: "F4", 2: "F5", 3: "F6", 4: "F7", 5: "F8", 6: "F9", 7: "F10"}

# ref -> (face, mating direction, plain function, mating hardware)
# Source: hardware-current/manufacturing/enclosure_assembly_notes.md
CONNECTORS = {
    "J1": ("front", "mates upward, out of the front face",
           "the only power inlet: 24 V from the external supply",
           "Phoenix 1771091 top-entry spring terminal -- wires go straight in, there is no mating plug. "
           "0.5 mm2 / AWG20 conductors, 6 mm strip length."),
    "J2": ("front", "locking direct-insertion tail, gold facing the main board", "all six radial zones, separately fused",
           "Molex 2005280300, bottom-contact Front Flip, 30 contacts at 1 mm pitch. Upper flex J100 inserts directly; total insertion thickness 0.30 +/-0.05 mm. No solder on the fingers."),
    "J8": ("back", "mates downward, out of the back face", "ambient zone 7 (the bottom ring)",
           "JST GH 4-way vertical BM04B-GHS-TBT, mating GHR-04V-S"),
    "J9": ("back", "mates downward beside the tilt harness", "all three independent spotlight LED pairs",
           "JST GH 6-way vertical BM06B-GHS-TBT, mating GHR-06V-S; pins 1/2, 3/4 and 5/6 are separate channel pairs"),
    "J12": ("back", "mates downward, out of the back face", "motor 1: 24 V, ground and the CAN pair",
            "JST PA BM04B-PASS-TFT, mating PAP-04V-S with SPHD-001T-P0.5 contacts; AWG22 for the power leads, "
            "CAN_H and CAN_L kept as a twisted pair"),
    "J13": ("back", "mates downward, out of the back face", "motor 2: 24 V, ground and the CAN pair",
            "JST PA BM04B-PASS-TFT, mating PAP-04V-S with SPHD-001T-P0.5 contacts; AWG22 for the power leads, "
            "CAN_H and CAN_L kept as a twisted pair"),
    "J14": ("front", "mates sideways, into the front-face edge",
            "USB-C for programming and serial, alongside external 24 V",
            "GCT USB4105-GF-A: 16 contacts plus four soldered through-hole shield stakes"),
    "J15": ("front", "side-entry across the front face", "3.3 V UART service port",
            "JST SH 4-way SM04B-SRSS-TB -- deliberately a different size from the GH ambient ports so a strip "
            "cable cannot be plugged in here"),
    "J16": ("front", "side-entry across the front face",
            "a tap on the protected bus for a separately designed brake", "Molex Pico-Lock 2053380002"),
    "J17": ("front", "vertical mating from the front face", "the physical ARM switch",
            "JST PH 2-way B2B-PH-SM4-TB, mating PHR-2 with SPH-002T-P0.5S -- ships open, which means disarmed"),
    "J18": ("back", "bare pads on the back face; no header is fitted",
            "five spare GPIOs plus 3.3 V and ground",
            "no connector: 0.85 mm solder lands on 1.27 mm pitch"),
}

# footprint -> plain-language package description
PACKAGES = {
    "ELF:Molex_2005280300_30P_Central_LED": "Molex 30-contact 1 mm locking flex socket",
    "ELF:CP_CDE_AFK_CaseP_D16_H17_Provisional": "16 mm diameter aluminium capacitor; provisional custom land",
    "Button_Switch_SMD:SW_SPST_TL3305A": "surface-mount tactile button",
    "Capacitor_SMD:C_0603_1608Metric": "0603 chip capacitor (1.6 x 0.8 mm)",
    "Capacitor_SMD:C_0805_2012Metric": "0805 chip capacitor (2.0 x 1.25 mm)",
    "Capacitor_SMD:C_1206_3216Metric": "1206 chip capacitor (3.2 x 1.6 mm)",
    "Capacitor_SMD:C_1210_3225Metric": "1210 chip capacitor (3.2 x 2.5 mm)",
    "Connector_JST:JST_GH_BM02B-GHS-TBT_1x02-1MP_P1.25mm_Vertical": "JST GH 2-way vertical socket",
    "Connector_JST:JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical": "JST GH 4-way vertical socket",
    "Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal": "JST GH 4-way side-entry socket",
    "Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal": "JST SH 4-way side-entry socket (1 mm pitch)",
    "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal":
        "USB-C receptacle: 16 contacts plus four through-hole shield stakes",
    "Diode_SMD:D_SMA": "SMA surface-mount diode",
    "Diode_SMD:D_SMB": "SMB surface-mount diode",
    "Diode_SMD:D_SMC": "SMC surface-mount diode",
    "Diode_SMD:D_SOD-523": "SOD-523 miniature diode",
    "EL:ESP32-C6-WROOM-1": "castellated radio module with a ground pad under the body",
    "ELF:CP_CDE_AFK_CaseP_D16_H17_Provisional":
        "16 mm can electrolytic on provisional engineering-derived lands",
    "ELF:Enclosure_F1": "surface-mount fuse clips",
    "ELF:Enclosure_J1": "Phoenix PTSM top-entry spring terminal",
    "EL:JST_GH_BM06B-GHS-TBT_1x06-1MP_P1.25mm_Vertical": "JST GH six-contact vertical socket",
    "ELF:Enclosure_J10": "JST GH 2-way vertical socket (silkscreen variant)",
    "ELF:Enclosure_J16": "Molex Pico-Lock 2-way socket",
    "ELF:Enclosure_J17": "JST PH 2-way vertical socket",
    "ELF:Enclosure_J5": "JST GH 4-way side-entry socket (silkscreen variant)",
    "ELF:Enclosure_J6": "JST GH 4-way side-entry socket (silkscreen variant)",
    "ELF:Enclosure_J9": "JST GH 2-way vertical socket (silkscreen variant)",
    "ELF:Expansion_SolderPads_1x07_P1p27mm": "seven bare solder lands on 1.27 mm pitch",
    "ELF:JST_PA_BM04B_PASS_TFT_1x04_P2mm_Vertical": "JST PA 4-way vertical socket (2 mm pitch)",
    "ELF:L_Bourns_SRN6045": "6 x 6 mm shielded power inductor",
    "ELF:L_Bourns_SRP7050TA": "7 x 7 mm shielded power inductor",
    "ELF:SOT-23-6_FabPin1": "SOT-23-6",
    "ELF:TI_DDA0008B_EP2.71x3.4_ThermalVias_125um":
        "SO PowerPAD-8: eight leads plus a thermal pad with eight vias under the body",
    "ELF:TI_PWP0016A_EP3.3x3.3_6ThermalVias_125um":
        "HTSSOP-16 with a thermal pad and six vias under the body",
    "ELF:TI_RSW0010A_UQFN10_1p4x1p8_TMUXHS221F":
        "UQFN-10, 1.4 x 1.8 mm on 0.4 mm pitch -- the finest-pitch part on the board",
    "ELF:TestPoint_Pad_D1mm_NoComponentCourtyard": "1 mm bare probe pad",
    "Fuse:Fuse_Littelfuse-NANO2-451_453": "Nano2 surface-mount cartridge fuse",
    "Inductor_SMD:L_Bourns-SRN4018": "4 x 4 mm shielded power inductor",
    "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm":
        "two-pad solder jumper, open as manufactured",
    "MountingHole:MountingHole_3.2mm_M3": "3.2 mm unplated M3 hole",
    "Package_DFN_QFN:Texas_RGE0024H_VQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm_ThermalVias":
        "VQFN-24, 4 x 4 mm on 0.5 mm pitch, with a thermal pad",
    "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm": "SOIC-8",
    "Package_SO:TSSOP-14_4.4x5mm_P0.65mm": "TSSOP-14 on 0.65 mm pitch",
    "Package_SO:TSSOP-28_4.4x9.7mm_P0.65mm": "TSSOP-28 on 0.65 mm pitch",
    "Package_SON:Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm_ThermalVias":
        "WSON-8, 2 x 2 mm, with a thermal pad",
    "Package_SON:VSON-8_3.3x3.3mm_P0.65mm_NexFET": "VSON-8 power package with a large exposed drain",
    "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm_ThermalVias": "WSON-6, 2 x 2 mm, with a thermal pad",
    "Package_TO_SOT_SMD:SOT-23": "SOT-23, three leads",
    "Package_TO_SOT_SMD:SOT-23-5": "SOT-23-5",
    "Package_TO_SOT_SMD:SOT-23-6": "SOT-23-6",
    "Package_TO_SOT_SMD:SOT-363_SC-70-6": "SC-70-6",
    "Package_TO_SOT_SMD:SOT-563": "SOT-563, 1.6 x 1.2 mm -- the smallest logic package here",
    "Package_TO_SOT_SMD:TSOT-23-5": "TSOT-23-5",
    "Resistor_SMD:R_0603_1608Metric": "0603 chip resistor (1.6 x 0.8 mm)",
    "Resistor_SMD:R_0805_2012Metric": "0805 chip resistor (2.0 x 1.25 mm)",
    "TestPoint:TestPoint_Pad_D1.0mm": "1 mm bare probe pad",
}

# test point -> what the first-hardware checklist plans to look for there
# Source: engineering-history/first_hardware_checklist.md (planned checks only)
TP_EXPECT = {
    "TP1": "The measurement return for everything else. Check harness return continuity while the board is unpowered.",
    "TP2": "The applied supply voltage, upstream of all protection.",
    "TP3": "The protected bus after startup. Compare its drop against TP2 at the measured current.",
    "TP4": "Nominal 5 V; the project's initial static screening window is 4.75-5.25 V.",
    "TP5": "Nominal 3.3 V; the project's initial static screening window is 3.135-3.465 V.",
    "TP6": "With ARM open this should be disabled, approaching ground once stored charge has drained.",
    "TP7": "Low with the physical ARM switch open: at most 0.35 V, with 0.30 V as the measurement target.",
    "TP8": "The main eFuse's enable and reset node. Observe only at first; do not inject a voltage here.",
    "TP9": "The spotlight supply, disabled. Record how it decays rather than assuming it is instantly zero.",
    "TP10": "Idle high once logic is powered; later check the bus addresses and the waveform.",
    "TP11": "Idle high once logic is powered; later measure the 30-70 % rise time.",
    "TP12": "High while lighting is inhibited, with logic powered.",
}

# ref -> (owner IC, rail, role)
DECOUPLING = {
    "C2": ("U1", "+3V3", "the radio module's high-frequency bypass"),
    "C4": ("U5", "+3V3", "bypass for the AND gate that arms the spotlight PWM signals"),
    "C5": ("U6", "+3V3", "bypass for the inverter that drives the expanders' output-enable"),
    "C20": ("U4", "+5V", "bypass for the CAN transceiver's 5 V supply"),
    "C21": ("U4", "+3V3", "bypass for the CAN transceiver's 3.3 V logic-side supply"),
    "C22": ("U4", "+5V", "the larger companion reservoir for the CAN transceiver's 5 V supply"),
    "C40": ("U2", "+3V3", "high-frequency bypass for the first PWM expander"),
    "C41": ("U3", "+3V3", "high-frequency bypass for the second PWM expander"),
    "C42": ("U2", "+3V3", "the larger companion reservoir for the first PWM expander"),
    "C43": ("U3", "+3V3", "the larger companion reservoir for the second PWM expander"),
    "C44": ("U18", "+3V3", "bypass for the 3.3 V supervisor"),
    "C45": ("U19", "+3V3", "bypass for the Schmitt AND gate that produces SAFE"),
    "C46": ("U20", "+3V3", "bypass for the temperature sensor"),
    "C500": ("F1", "VIN24_FUSED", "high-frequency bypass on the incoming 24 V, just after the fuse"),
    "C502": ("Q500", "VIN24_RPP", "high-frequency bypass just after the reverse-blocking transistor"),
    "C505": ("U12", "V24_BUS", "high-frequency bypass on the protected bus at the eFuse's output"),
    "C507": ("U10", "V24_LOGIC", "the high-frequency partner to C506 at the 5 V converter's input"),
    "C514": ("U13", "+3V3", "bypass on the gate-bias switch's input"),
    "C515": ("U13", "GATE_BIAS", "bypass on the switched gate-bias rail itself"),
    "C517": ("U14", "V24_BUS", "bypass at the spotlight eFuse's input"),
    "C518": ("U14", "V24_SPOT", "bypass at the spotlight eFuse's output"),
    "C30": ("J14", "USB_VBUS", "bypass on the USB bus voltage right at the connector"),
    "C31": ("U17", "USB_VBUS", "bypass on the USB bus voltage at the data mux's supply pin"),
}

# ref -> (rail, role)
BULK = {
    "C1": ("MCU_EN", "the reset timing capacitor: together with R1 it holds the module in reset while 3.3 V rises"),
    "C3": ("+3V3", "the radio module's local energy reservoir for transmit bursts"),
    "C501": ("VIN24_FUSED", "a small bulk reservoir on the incoming 24 V, rated 100 V because it sits upstream of the cutoff"),
    "C506": ("V24_LOGIC", "the 5 V converter's input reservoir, which supplies its switching current pulses"),
    "C508": ("BUCK5_VCC", "the 5 V converter's internal-supply capacitor"),
    "C510": ("+5V", "half of the 5 V converter's output reservoir"),
    "C511": ("+5V", "half of the 5 V converter's output reservoir"),
    "C512": ("+5V", "the 3.3 V converter's input reservoir"),
    "C513": ("+3V3", "the 3.3 V converter's output reservoir, which is also where it senses the rail"),
}

# ref -> (partner, top net, tapped node, what the divider sets)
DIVIDERS = {
    "R501": ("R502", "VIN24_FUSED", "EFUSE_UVLO", "the eFuse's undervoltage lockout, so it refuses to turn on until the input is high enough"),
    "R502": ("R501", "VIN24_FUSED", "EFUSE_UVLO", "the eFuse's undervoltage lockout, so it refuses to turn on until the input is high enough"),
    "R503": ("R504", "VIN24_FUSED", "EFUSE_OVP", "the eFuse's overvoltage cutoff, set near 26.4 V"),
    "R504": ("R503", "VIN24_FUSED", "EFUSE_OVP", "the eFuse's overvoltage cutoff, set near 26.4 V"),
    "R505": ("R506", "V24_BUS", "EFUSE_PGTH", "the level at which the eFuse calls the bus good, nominally 21.0 V rising"),
    "R506": ("R505", "V24_BUS", "EFUSE_PGTH", "the level at which the eFuse calls the bus good, nominally 21.0 V rising"),
    "R510": ("R511", "+5V", "BUCK5_FB", "the feedback divider that sets the 5 V output"),
    "R511": ("R510", "+5V", "BUCK5_FB", "the feedback divider that sets the 5 V output"),
    "R517": ("R518", "V24_BUS", "SPOT_EFUSE_OVP", "the spotlight eFuse's overvoltage cutoff, near 26.2 V"),
    "R518": ("R517", "V24_BUS", "SPOT_EFUSE_OVP", "the spotlight eFuse's overvoltage cutoff, near 26.2 V"),
    "R34": ("R35", "USB_VBUS", "USB_SENSE_BASE", "the base drive for Q30, which senses that a USB host is plugged in"),
    "R35": ("R34", "USB_VBUS", "USB_SENSE_BASE", "the base drive for Q30, which senses that a USB host is plugged in"),
    "R41": ("R39", "READY_3V3", "USB_READY_SELECT", "the signal that tells the USB data mux whether the 3.3 V rail is qualified"),
    "R39": ("R41", "READY_3V3", "USB_READY_SELECT", "the signal that tells the USB data mux whether the 3.3 V rail is qualified"),
}

# ref -> (direction, rail, node, what it achieves)
PULLS = {
    "R1": ("up", "+3V3", "MCU_EN", "holds the module out of reset once 3.3 V is up; with C1 it sets the reset delay"),
    "R2": ("up", "+3V3", "BOOT_GPIO9", "keeps the boot strap high, so the module runs its own firmware unless S2 is held down"),
    "R3": ("up", "+3V3", "BOOT_GPIO8", "keeps the second boot strap in its normal state"),
    "R4": ("down", "GND", "LIGHT_ENABLE", "makes the firmware's lighting request default to off, including before any firmware runs"),
    "R5": ("down", "GND", "ARM", "makes the board read as disarmed whenever the ARM switch is open or unplugged"),
    "R6": ("up", "+3V3", "PCA_OE", "holds the expanders' outputs disabled by default, since output-enable is active-low"),
    "R7": ("up", "+3V3", "I2C_SDA", "gives the data line something to pull it high, because I2C devices can only pull down"),
    "R8": ("up", "+3V3", "I2C_SCL", "gives the clock line something to pull it high, because I2C devices can only pull down"),
    "R9": ("down", "GND", "SPOT1_PWM", "keeps spotlight 1's request off while the controller is unprogrammed or in reset"),
    "R10": ("down", "GND", "SPOT2_PWM", "keeps spotlight 2's request off while the controller is unprogrammed or in reset"),
    "R11": ("down", "GND", "SPOT3_PWM", "keeps spotlight 3's request off while the controller is unprogrammed or in reset"),
    "R20": ("up", "+3V3", "CAN_TX", "holds the transmit line in its idle state so an unprogrammed controller cannot jam the bus"),
    "R21": ("down", "GND", "CAN_STB", "ties the transceiver's standby pin low, which selects normal mode"),
    "R36": ("up", "+3V3", "USB_PRESENT_N", "holds the USB-present signal high, meaning absent, until Q30 pulls it down"),
    "R40": ("down", "GND", "USB_VBUS", "bleeds the small USB island so it cannot hold a stale 'USB is present' state after unplugging"),
    "R507": ("down", "GND", "EFUSE_IMON", "turns the eFuse's current-monitor output into a voltage"),
    "R508": ("up", "+3V3", "EFUSE_FLT_N", "lets the eFuse's fault output read high when there is no fault, since it can only pull down"),
    "R509": ("up", "+3V3", "EFUSE_PGOOD", "lets the eFuse's power-good output read high, since it can only pull down"),
    "R512": ("up", "+3V3", "BUCK5_PGOOD", "lets the 5 V converter's power-good output read high, since it can only pull down"),
    "R513": ("up", "+3V3", "BUCK3_PGOOD", "lets the 3.3 V converter's power-good output read high, since it can only pull down"),
    "R514": ("down", "GND", "LIGHT_ENABLE_SAFE", "holds SAFE low, so lighting stays inhibited whenever nothing is actively driving it"),
    "R519": ("down", "SPOT_RTN", "SPOT_EFUSE_IMON", "turns the spotlight eFuse's current-monitor output into a voltage"),
    "R520": ("up", "+3V3", "SPOT_EFUSE_FLT_N", "lets the spotlight eFuse's fault output read high, since it can only pull down"),
    "R521": ("down", "GND", "V24_SPOT", "bleeds the spotlight rail down after shutdown instead of leaving it at some leakage voltage"),
    "R526": ("down", "GND", "SPOT1_CTRL", "keeps driver 1 off if the gate ahead of it is not driving"),
    "R527": ("down", "GND", "SPOT2_CTRL", "keeps driver 2 off if the gate ahead of it is not driving"),
    "R528": ("down", "GND", "SPOT3_CTRL", "keeps driver 3 off if the gate ahead of it is not driving"),
    "R30": ("down", "GND", "USB_CC1", "is one of the two 5.1 k resistors that tell a USB-C host this board is a device"),
    "R31": ("down", "GND", "USB_CC2", "is one of the two 5.1 k resistors that tell a USB-C host this board is a device"),
    "R37": ("down", "GND", "USB_DP_PARK", "is the parking resistor the data mux selects while the controller's rail is not qualified"),
    "R38": ("down", "GND", "USB_DM_PARK", "is the parking resistor the data mux selects while the controller's rail is not qualified"),
}

# ref -> (node, what the value sets)
SETTINGS = {
    "R500": ("EFUSE_ILIM", "sets the main eFuse's current limit; 4.02 kOhm gives roughly 4.14-4.86 A once resistor tolerance is included"),
    "R515": ("SPOT_EFUSE_ILIM", "sets the spotlight eFuse's current limit; 24.3 kOhm gives about 0.494 A nominal"),
    "R516": ("SPOT_EFUSE_MODE", "selects how the spotlight eFuse behaves after a fault: latch off rather than retry"),
    "R42": ("MCU_EN", "isolates the supervisor's open-drain output from the module's reset network and limits the initial discharge current"),
    "R32": ("USB_DM_MCU", "is a zero-ohm link: a deliberate place to break the data line during bring-up"),
    "R33": ("USB_DP_MCU", "is a zero-ohm link: a deliberate place to break the data line during bring-up"),
    "R22": ("CAN_TERM", "is the 120 Ohm CAN terminator, in series with the JP1 solder jumper so it only counts when this board is one of the bus's two ends"),
}

# which functional section a ref belongs to, where the family alone does not say
CIRCUIT_OF = {}
for _r in ("C500", "C501", "C502", "C503", "D500", "F1", "J1", "Q500", "Q501", "U12",
           "R500", "R501", "R502", "R503", "R504", "R505", "R506", "R507", "R508", "R509"):
    CIRCUIT_OF[_r] = "input"
for _r in ("C504", "C505", "D505", "U501", "J16"):
    CIRCUIT_OF[_r] = "bus"
for _r in ("U10", "C506", "C507", "C508", "C509", "C510", "C511", "L500", "R510", "R511", "R512"):
    CIRCUIT_OF[_r] = "buck5"
for _r in ("U11", "C512", "C513", "L501", "R513"):
    CIRCUIT_OF[_r] = "buck3"
for _r in ("U1", "R1", "R2", "R3", "C1", "C2", "C3", "S1", "S2", "J15", "R9", "R10", "R11"):
    CIRCUIT_OF[_r] = "mcu"
for _r in ("U2", "U3", "C40", "C41", "C42", "C43", "R7", "R8"):
    CIRCUIT_OF[_r] = "pwm"
for _r in ("U5", "U6", "U13", "U18", "U19", "R4", "R5", "R6", "R42", "R514",
           "C4", "C5", "C44", "C45", "C514", "C515", "J17"):
    CIRCUIT_OF[_r] = "gating"
for _r in ("U4", "U16", "R20", "R21", "R22", "C20", "C21", "C22", "J12", "J13", "JP1"):
    CIRCUIT_OF[_r] = "can"
for _r in ("J14", "U15", "U17", "D30", "Q30", "C30", "C31",
           "R30", "R31", "R32", "R33", "R34", "R35", "R36", "R37", "R38", "R39", "R40", "R41"):
    CIRCUIT_OF[_r] = "usb"
for _r in ("U20", "C46"):
    CIRCUIT_OF[_r] = "sensor"
for _r in ("U14", "U500", "D501", "R515", "R516", "R517", "R518", "R519", "R520", "R521",
           "C516", "C517", "C518"):
    CIRCUIT_OF[_r] = "spot_supply"

CAD_CHECK = ("ERC, DRC, board-to-schematic parity and 163-net continuity all ran clean on this exact "
             "layout (cbb8d9fc).")


def zone_of(channel):
    return (channel - 1) // 3 + 1


def colour_of(channel):
    return COLOURS[(channel - 1) % 3]


def channel_of(ref):
    """R101 / R201 / R301 / Q101 -> 1 ... 21."""
    m = re.match(r"^[QR][123](\d\d)$", ref)
    if not m:
        return None
    n = int(m.group(1))
    return n if 1 <= n <= 21 else None


def classify(ref, comp):
    if ref in teaching_unique.UNIQUE:
        return "unique"
    if re.match(r"^H[1-4]$", ref):
        return "mounting_hole"
    if ref == "JP1":
        return "jumper"
    if ref == "J18":
        return "expansion_pads"
    if ref in ("TP13", "TP14", "TP15"):
        return "boot_strap_probe"
    if ref.startswith("TP"):
        return "test_point"
    if re.match(r"^Q1\d\d$", ref) and channel_of(ref):
        return "ambient_mosfet"
    if re.match(r"^R1\d\d$", ref) and channel_of(ref):
        return "ambient_gate_series"
    if re.match(r"^R2\d\d$", ref) and channel_of(ref):
        return "ambient_gate_pulldown"
    if re.match(r"^R3\d\d$", ref) and channel_of(ref):
        return "ambient_gate_pullup"
    if ref in ZONE_CONN.values():
        return "zone_connector"
    if ref in ZONE_FUSE.values():
        return "zone_fuse"
    if ref in ("F2", "F3"):
        return "motor_fuse"
    if ref == "F11":
        return "logic_fuse"
    if ref == "F1":
        return "input_fuse"
    if ref in ("U7", "U8", "U9"):
        return "spot_driver"
    if ref in ("R523", "R524", "R525"):
        return "spot_sense"
    if ref in ("L502", "L503", "L504"):
        return "spot_inductor"
    if ref in ("D502", "D503", "D504"):
        return "spot_diode"
    if ref in ("R526", "R527", "R528"):
        return "spot_ctrl_pulldown"
    if ref in ("J9", "J10", "J11"):
        return "spot_connector"
    if ref in ("C519", "C520", "C521", "C522", "C523", "C524"):
        return "spot_input_cap"
    if ref in DECOUPLING:
        return "decoupling"
    if ref in BULK:
        return "bulk"
    if ref in DIVIDERS:
        return "divider"
    if ref in PULLS:
        return "pullup" if PULLS[ref][0] == "up" else "pulldown"
    if ref in SETTINGS:
        return "setting"
    raise KeyError("no family for %s (nets %s)" % (ref, sorted(v for v in comp["pins"].values() if v)))


SPOT_GROUPS = {
    1: ("U7", "R523", "L502", "D502", "R526", "J9", "C519", "C520"),
    2: ("U8", "R524", "L503", "D503", "R527", "J9", "C521", "C522"),
    3: ("U9", "R525", "L504", "D504", "R528", "J9", "C523", "C524"),
}


def _spot_index(ref):
    for k, group in SPOT_GROUPS.items():
        if ref in group:
            return k, group
    return None, None


def _contacts(pins):
    return ", ".join("%s = %s" % (k, v) for k, v in sorted(pins.items(), key=lambda kv: int(kv[0])))


def build_entry(ref, comp):
    """Return the teaching entry for one reference (no nets/sheet/bom -- the
    builder adds those from board.json)."""
    family = classify(ref, comp)
    pins = comp["pins"]
    entry = {"family": family, "claims": [], "open": [], "related": [], "assembly": []}

    if family == "unique":
        entry.update(teaching_unique.UNIQUE[ref])
        entry["family"] = "unique"
        entry.setdefault("circuit", CIRCUIT_OF.get(ref, "mcu"))
        return entry

    if family == "ambient_mosfet":
        n = channel_of(ref)
        z = zone_of(n)
        cname, cletter = colour_of(n)
        dev, led, pin = CHANNELS[n]
        drain = pins["3"]
        contact = channel_contact(n)
        entry.update(
            name="Zone %d %s channel switch" % (z, cname),
            circuit="ambient",
            group={"zone": z, "colour": cname, "channel": n},
            here=("The low-side switch for the %s white LEDs in ambient zone %d. Its drain is %s, which leaves "
                  "the board on %s contact %d; the strip's positive end arrives on its zone-specific positive contact(s) from ZONE%d_24V "
                  "through fuse %s. Turning this transistor on completes that circuit to ground, which is why "
                  "%s is a switched return rather than a ground wire."
                  % (cname, z, drain, ZONE_CONN[z], contact, z, ZONE_FUSE[z], drain)),
            how=("An N-channel MOSFET conducts between drain and source once its gate sits a few volts above the "
                 "source. Here the source is ground, so the voltage on %s alone decides whether the zone's %s "
                 "LEDs light. This part was chosen on its resistance quoted at a low gate voltage rather than on "
                 "threshold voltage, because the gate is raised from a 3.3 V rail through a 2.2 kOhm resistor, "
                 "not driven hard by a gate driver." % (pins["1"], cname)),
            related=["R1%02d" % n, "R2%02d" % n, "R3%02d" % n, ZONE_CONN[z], ZONE_FUSE[z], dev],
        )
        entry["claims"] = [
            {"kind": "documented", "evidence": "intended",
             "text": "Channel %d is logical PWM %d: %s output %d, package pin %d, driving zone %d %s."
                     % (n, n, dev, led, pin, z, cname),
             "basis": "engineering-history/firmware_port_map.md, cross-checked against this board's nets"},
            {"kind": "documented", "evidence": "intended",
             "text": "The expander outputs are configured open-drain, so a low output holds this gate off and the "
                     "light is on when the output is released. Optical duty is the complement of the sink-active "
                     "duty the firmware writes.",
             "basis": "engineering-history/firmware_port_map.md"},
        ]
        if n in REMAPPED:
            entry["claims"].append(
                {"kind": "documented", "evidence": "intended",
                 "text": "This channel is a routing-driven remap: logical PWM %d is %s output %d on package pin %d, "
                         "not output %d. Never work out the second expander's output index by subtracting 16."
                         % (n, dev, led, pin, n - 16),
                 "basis": "engineering-history/firmware_port_map.md"})
        entry["open"] = ["Actual channel current is unmeasured. The project's provisional envelope is 0.2 A per "
                         "channel, and per-zone duty is scheduled so warm, neutral and cool never conduct at once."]
        return entry

    if family == "ambient_gate_series":
        n = channel_of(ref)
        z = zone_of(n)
        cname, _ = colour_of(n)
        dev, led, pin = CHANNELS[n]
        entry.update(
            name="Zone %d %s gate resistor" % (z, cname),
            circuit="ambient",
            group={"zone": z, "colour": cname, "channel": n},
            here=("Sits between %s, the expander node for channel %d, and %s, the gate of %s. All 21 ambient "
                  "channels have one, and it is the only thing between the expander pin and the transistor "
                  "gate." % (pins["1"], n, pins["2"], "Q1%02d" % n)),
            how=("A MOSFET gate behaves like a small capacitor, so switching it means charging and discharging "
                 "that capacitance. Without a series resistor the current spike is large and the edge rings. "
                 "220 Ohm slows the edge just enough to damp that without making the switch noticeably slower."),
            related=["Q1%02d" % n, "R2%02d" % n, "R3%02d" % n, dev],
        )
        entry["claims"] = [{"kind": "documented", "evidence": "intended",
                            "text": "Channel %d: %s output %d, package pin %d, feeds this resistor." % (n, dev, led, pin),
                            "basis": "engineering-history/firmware_port_map.md"}]
        return entry

    if family == "ambient_gate_pulldown":
        n = channel_of(ref)
        z = zone_of(n)
        cname, _ = colour_of(n)
        entry.update(
            name="Zone %d %s gate pull-down" % (z, cname),
            circuit="ambient",
            group={"zone": z, "colour": cname, "channel": n},
            here=("Holds %s, the gate of %s, down to ground whenever nothing else drives it: before the expander "
                  "is initialised, while the gate-bias supply is switched off, and any time the controller is in "
                  "reset." % (pins["1"], "Q1%02d" % n)),
            how=("100 kOhm is small enough to drain the gate's stored charge to ground, and large enough that it "
                 "barely loads the 2.2 kOhm pull-up when the channel is meant to be on. A gate left floating "
                 "could drift upward and switch its channel on unbidden."),
            related=["Q1%02d" % n, "R1%02d" % n, "R3%02d" % n],
        )
        entry["claims"] = [{"kind": "documented", "evidence": "intended",
                            "text": "Default-off is a design requirement: nothing lights until the firmware asks "
                                    "for it and the physical ARM switch agrees.",
                            "basis": "engineering-history/rev_a_inhibit_correction.md"}]
        return entry

    if family == "ambient_gate_pullup":
        n = channel_of(ref)
        z = zone_of(n)
        cname, _ = colour_of(n)
        dev, led, pin = CHANNELS[n]
        entry.update(
            name="Zone %d %s gate pull-up" % (z, cname),
            circuit="ambient",
            group={"zone": z, "colour": cname, "channel": n},
            here=("Connects the switched gate-bias rail %s to %s, the expander node for channel %d. This resistor "
                  "is what actually turns the channel on: the expander output is open-drain, so it can only pull "
                  "the node down, and releasing it lets this pull-up raise the gate."
                  % (pins["1"], pins["2"], n)),
            how=("GATE_BIAS only exists while U13 is switched on by SAFE, so this pull-up is powerless unless the "
                 "board is armed and the supervisor is satisfied. That is the point: the 21 gates cannot be raised "
                 "at all while lighting is inhibited, whatever the firmware writes to the expander."),
            related=["Q1%02d" % n, "R1%02d" % n, "R2%02d" % n, "U13", dev],
        )
        entry["claims"] = [
            {"kind": "documented", "evidence": "intended",
             "text": "Channel %d is %s output %d on package pin %d." % (n, dev, led, pin),
             "basis": "engineering-history/firmware_port_map.md"},
            {"kind": "documented", "evidence": "intended",
             "text": "The gate pull-ups are supplied only while LIGHT_ENABLE_SAFE is asserted.",
             "basis": "hardware-current/engineering/design_parts.json (U13 note)"},
        ]
        return entry

    if family == "zone_connector" and ref == "J2":
        entry.update(name="Six-zone locking flex interface", circuit="ambient",
            here="J2 carries all six radial LED zones through one insertion tail. ZONE1_24V through ZONE6_24V stay separately fused; each zone has two positive contacts and W/N/C switched returns. J3 through J7 no longer exist on this revision.",
            how="The flexible board itself is the cable end: its back gold fingers slide into a bottom-contact locking socket. Thirty contacts carry twenty-four distinct rails because the positive contact is doubled for each zone. The six zone positives are not joined together.",
            related=["F4","F5","F6","F7","F8","F9"],
            assembly=["Molex 2005280300: do not wash; maximum two reflows with connector upward in second pass. Preserve actuator access."],
            claims=[{"kind":"documented","evidence":"cad-checked","text":"Zone order along the tail is 4, 5, 6, 1, 2, 3; each five-contact group is +,+,W,N,C.","basis":"Current main J2 pins and matched upper J100 contract"}],
            open=["Actual insertion fit, final total tail thickness, plating and factory process remain unqualified."])
        return entry
    if family == "zone_connector":
        z = [k for k, v in ZONE_CONN.items() if v == ref][0]
        _face, direction, _function, mating = CONNECTORS[ref]
        entry.update(
            name="Ambient zone %d connector" % z,
            circuit="ambient",
            group={"zone": z},
            here=("Where ambient zone %d's tunable-white strip plugs in. Contacts in numeric order: %s. Contact 1 "
                  "is the strip's shared positive, fused on its own by %s; the other three are the switched "
                  "returns for warm, neutral and cool." % (z, _contacts(pins), ZONE_FUSE[z])),
            how=("The strip has one positive wire and three colour wires. All three colours share that positive, "
                 "so the shared contact carries the sum of the three channel currents -- a per-contact rating is "
                 "not a per-channel allowance. This connector %s." % direction),
            related=[ZONE_FUSE[z]] + ["Q1%02d" % (3 * (z - 1) + i) for i in (1, 2, 3)],
        )
        entry["claims"] = [{"kind": "documented", "evidence": "intended",
                            "text": "Mating hardware: %s." % mating,
                            "basis": "hardware-current/manufacturing/enclosure_assembly_notes.md"}]
        entry["open"] = ["Harness crimping, wire gauge and continuity are the assembler's to confirm. The "
                         "connector's own rating does not lift the 0.75 A branch fuse."]
        return entry

    if family in ("zone_fuse", "motor_fuse", "logic_fuse", "input_fuse"):
        branch = pins["2"]
        source = pins["1"]
        rating = comp["value"].split()[0]
        if family == "zone_fuse":
            z = [k for k, v in ZONE_FUSE.items() if v == ref][0]
            name = "Ambient zone %d fuse" % z
            what = "ambient zone %d's strip supply (%s), which leaves through %s" % (z, branch, ZONE_CONN[z])
            related = [ZONE_CONN[z], "U12"]
            circuit = "branch"
        elif family == "motor_fuse":
            motor = "1" if ref == "F2" else "2"
            port = "J12" if ref == "F2" else "J13"
            name = "Motor %s fuse" % motor
            what = "motor %s's 24 V supply (%s), which leaves through %s" % (motor, branch, port)
            related = [port, "U12"]
            circuit = "branch"
        elif family == "logic_fuse":
            name = "Logic branch fuse"
            what = "the logic branch (%s) that feeds the 5 V converter and everything downstream of it" % branch
            related = ["U10", "U12"]
            circuit = "branch"
        else:
            name = "Input backup fuse"
            what = "the whole board: it is the first thing the incoming supply meets after %s" % source
            related = ["J1", "U12", "Q500"]
            circuit = "input"
        entry.update(
            name=name, circuit=circuit,
            here=("A %s cartridge fuse protecting %s. Its two connections here are %s and %s, so every amp that "
                  "reaches that branch passes through this part." % (rating, what, source, branch)),
            how=("A fuse is a deliberate weak link: sustained current above its rating heats it until it opens, "
                 "disconnecting that branch permanently until the fuse is replaced. It protects the wiring and "
                 "limits what a fault downstream can draw. It does not regulate current, and its rating says "
                 "nothing about what the copper or the connectors can carry."),
            related=related,
        )
        if family == "input_fuse":
            entry["claims"] = [{"kind": "documented", "evidence": "intended",
                                "text": "F1 is backup protection. Functional current control is U12, the eFuse; a "
                                        "current-limited supply may stop this fuse ever opening.",
                                "basis": "hardware-current/engineering/design_parts.json (F1 notes)"}]
        else:
            entry["claims"] = [{"kind": "documented", "evidence": "cad-checked",
                                "text": "Every branch is fed through its own fuse: %s reaches %s only through this "
                                        "part." % (source, branch),
                                "basis": "80195efd electrical-baseline continuity check, preserved by cbb8d9fc silkscreen-only parity"}]
        entry["open"] = ["How this fuse coordinates with a real fault, and whether the branch wiring survives one, "
                         "has not been tested on hardware."]
        return entry

    if ref == "J9":
        entry.update(name="Three-channel spotlight connector", circuit="spot",
            here="One six-contact plug carries all three spotlight LED pairs: " + _contacts(pins) + ". It sits beside the separate J13 tilt connection, so their wires leave toward the same arm harness.",
            how="Pins 1/2, 3/4 and 5/6 serve channels 1, 2 and 3. A shared plastic housing does not join the circuits: each LED-minus returns to its own driver inductor, never to ground or another channel.",
            related=["U7", "U8", "U9", "L502", "L503", "L504", "J13"],
            claims=[{"kind":"documented", "evidence":"cad-checked", "text":"Six independent contacts replace the three former two-contact sockets. J10 and J11 are absent.", "basis":"Current native J9 pins and schematic parity"}],
            open=["The crimped wire harness, service loop across pan rotation and physical connector clearance still need bench verification."])
        return entry

    if family in ("spot_driver", "spot_sense", "spot_inductor", "spot_diode",
                  "spot_ctrl_pulldown", "spot_connector", "spot_input_cap"):
        k, group = _spot_index(ref)
        related = [r for r in group if r != ref]
        if family == "spot_driver":
            entry.update(
                name="Spotlight %d driver" % k,
                circuit="spot",
                here=("The constant-current driver for spotlight LED pair %d. Pin 5 takes the gated 24 V rail "
                      "(%s), pin 4 senses the current through %s, pin 1 is the switching node %s, and pin 3 is "
                      "the enable input %s, which only goes high when the firmware asks and SAFE agrees."
                      % (k, pins["5"], group[1], pins["1"], pins["3"])),
                how=("An LED's brightness follows its current, not its voltage, and a small voltage change makes a "
                     "large current change, so LEDs are driven with a controlled current. This part is a "
                     "hysteretic buck: it switches its internal transistor on until the voltage across the sense "
                     "resistor reaches an upper threshold, then off until it falls to a lower one. The inductor "
                     "carries the current smoothly through both phases and the catch diode gives it a path while "
                     "the switch is off."),
                related=related,
            )
            entry["claims"] = [
                {"kind": "documented", "evidence": "intended",
                 "text": "A 0.300 Ohm sense resistor sets a nominal 333 mA per channel.",
                 "basis": "engineering-history/power_review.md"},
                {"kind": "documented", "evidence": "modelled-current",
                 "text": "With the datasheet's 96-104 mV sense window and a 1 % resistor, the room-temperature "
                         "average lands in a 0.317-0.350 A band. That is arithmetic from the datasheet, not a "
                         "measurement.",
                 "basis": "engineering-history/power_review.md"},
                {"kind": "documented", "evidence": "intended",
                 "text": "Each channel's LED-minus returns only to its own inductor. It is not system ground and "
                         "must never be joined to another channel's return.",
                 "basis": "hardware-current/engineering/design_parts.json"},
            ]
            entry["open"] = ["Actual LED current, ripple, startup overshoot and inductor temperature are unmeasured."]
        elif family == "spot_sense":
            entry.update(
                name="Spotlight %d current sense" % k,
                circuit="spot",
                here=("The 0.300 Ohm resistor driver %s watches to regulate spotlight %d. It sits between the "
                      "gated rail %s and %s, so the whole LED current flows through it."
                      % (group[0], k, pins["1"], pins["2"])),
                how=("Current through a resistor produces a proportional voltage across it. The driver cannot "
                     "measure current directly, so it measures this voltage and switches to keep it inside a "
                     "fixed window. Change this resistor and you change the LED current."),
                related=related,
            )
            entry["claims"] = [{"kind": "documented", "evidence": "modelled-current",
                                "text": "0.300 Ohm with the driver's 96-104 mV window gives roughly 0.317-0.350 A, "
                                        "and the part dissipates about 0.038 W of its 0.125 W rating.",
                                "basis": "engineering-history/power_review.md"}]
        elif family == "spot_inductor":
            entry.update(
                name="Spotlight %d inductor" % k,
                circuit="spot",
                here=("Carries spotlight %d's LED current. Pin 1 is %s, the LED string's return, and pin 2 is the "
                      "driver's switching node %s. The LED current flows through this inductor, which is exactly "
                      "why the LED-minus wire is not a ground wire." % (k, pins["1"], pins["2"])),
                how=("An inductor resists sudden changes in the current through it. In a switching driver that is "
                     "the whole trick: the switch chops the supply on and off, and the inductor turns that "
                     "chopping into a nearly steady current through the LEDs."),
                related=related,
            )
            entry["claims"] = [{"kind": "documented", "evidence": "modelled-current",
                                "text": "A triangular-ripple model puts about 0.353 A RMS through this part and "
                                        "roughly 0.147 W of copper loss, against a 0.6 A RMS rating.",
                                "basis": "engineering-history/power_review.md"}]
            entry["assembly"] = ["Custom land pattern taken from the manufacturer's drawing; maximum reflow peak 250 C."]
        elif family == "spot_diode":
            entry.update(
                name="Spotlight %d catch diode" % k,
                circuit="spot",
                here=("Gives spotlight %d's inductor current somewhere to go while the driver's switch is off. Its "
                      "cathode is on the rail %s and its anode on the switching node %s." % (k, pins["1"], pins["2"])),
                how=("Interrupting current through an inductor produces a large voltage spike unless the current "
                     "has another path. This Schottky diode is that path: it conducts as soon as the switching "
                     "node swings, so the inductor keeps running instead of stressing the driver. Schottky parts "
                     "are used because they turn on quickly and drop little voltage."),
                related=related,
            )
            entry["claims"] = [{
                "kind": "documented", "evidence": "intended",
                "text": "Its cathode is on %s and its anode on %s. Fitted the other way round it would short "
                        "the rail every time the driver switched." % (pins["1"], pins["2"]),
                "basis": "board.json nets for this reference"}]
        elif family == "spot_ctrl_pulldown":
            entry.update(
                name="Spotlight %d CTRL pull-down" % k,
                circuit="spot",
                here=("Holds %s, driver %d's enable input, at ground whenever the AND gate ahead of it is not "
                      "actively driving -- for instance while the 3.3 V rail is still coming up." % (pins["1"], k)),
                how=("A logic input left floating can read either state. Tying it to ground through a resistor "
                     "makes off the default, while still letting the driving gate pull it high easily."),
                related=related + ["U5"],
            )
            entry["claims"] = [{
                "kind": "documented", "evidence": "intended",
                "text": "Spotlight %d is off by default: this resistor and the AND gate ahead of it both have "
                        "to be overcome before the driver is enabled." % k,
                "basis": "engineering-history/rev_a_inhibit_correction.md"}]
        elif family == "spot_connector":
            _face, direction, _function, mating = CONNECTORS[ref]
            entry.update(
                name="Spotlight %d output" % k,
                circuit="spot",
                here=("Where spotlight LED pair %d plugs in: %s. It %s, and its return contact belongs to this "
                      "channel alone." % (k, _contacts(pins), direction)),
                how=("Contact 2 is this channel's own return, and it goes to this channel's inductor -- not to "
                     "ground, and not to another channel. Joining spotlight returns together, or to ground, "
                     "breaks the current regulation and can damage the driver."),
                related=related,
            )
            entry["claims"] = [{"kind": "documented", "evidence": "intended",
                                "text": "Mating hardware: %s." % mating,
                                "basis": "hardware-current/manufacturing/enclosure_assembly_notes.md"}]
        else:
            entry.update(
                name="Spotlight %d input capacitor" % k,
                circuit="spot",
                here=("One of the pair of 10 uF capacitors that supply driver %s's switching current pulses "
                      "locally, between the gated rail %s and ground." % (group[0], pins["1"])),
                how=("A switching driver draws current in sharp pulses. Pulling those through the length of the "
                     "board would put noise on the shared rail and starve the driver at the moment it switches, "
                     "so each driver gets its own reservoir a few millimetres away."),
                related=related,
            )
            entry["claims"] = [{"kind": "inference", "evidence": "intended",
                                "text": "This capacitor belongs to spotlight channel %d specifically, even though "
                                        "all six sit on the same V24_SPOT net. The pairing comes from the reviewed "
                                        "placement cluster, not from the netlist." % k,
                                "basis": "engineering-history/power_clusters.json (spot template)"}]
        return entry

    if family == "decoupling":
        owner, rail, role = DECOUPLING[ref]
        entry.update(
            name="%s decoupling capacitor" % owner,
            circuit=CIRCUIT_OF.get(ref, CIRCUIT_OF.get(owner, "mcu")),
            here=("%s. It sits between %s and %s, placed within a few millimetres of %s, so that when %s "
                  "switches the current for that instant comes from here rather than down the length of copper "
                  "back to the regulator." % (role[0].upper() + role[1:], pins["1"], pins["2"], owner, owner)),
            how=("Every chip draws its supply current in bursts as it switches. The wiring back to the regulator "
                 "has enough inductance that those bursts would show up as dips on the rail, so each chip gets a "
                 "small capacitor right beside it to supply the burst locally. Small ceramics do this well "
                 "because they respond quickly; larger values handle slower demands."),
            related=[owner],
        )
        entry["claims"] = [{
            "kind": "inference", "evidence": "intended",
            "text": "This capacitor is assigned to %s from the reviewed decoupling table and its own nets "
                    "(%s and %s). On a dense two-sided board that assignment is an engineering reading of "
                    "the layout, not something the netlist states." % (owner, pins["1"], pins["2"]),
            "basis": "engineering-history/power_clusters.json and the part's nets in board.json"}]
        return entry

    if family == "bulk":
        rail, role = BULK[ref]
        entry.update(
            name="%s reservoir" % rail,
            circuit=CIRCUIT_OF.get(ref, "mcu"),
            here=("%s. Its two connections here are %s and %s, and unlike the small bypass capacitors nearby its "
                  "job is to hold enough charge for demands that last far longer than a single switching edge."
                  % (role[0].upper() + role[1:], pins["1"], pins["2"])),
            how=("Larger capacitance covers slower, bigger demands than a decoupling capacitor can: an inrush, a "
                 "radio transmit burst, or the gap between a switching converter's cycles. Ceramic capacitors "
                 "also lose a large fraction of their nominal value under DC bias, so the number printed on the "
                 "part is not the capacitance the circuit gets."),
            related=[],
        )
        entry["claims"] = [{
            "kind": "documented", "evidence": "intended",
            "text": "Ceramic capacitors lose a large part of their marked value under DC bias, so the "
                    "reservoir this circuit actually gets is smaller than the printed number. Two of this "
                    "board's reservoirs were re-selected for exactly that reason.",
            "basis": "engineering-history/rev_a_capacitor_correction.md"}]
        if ref in ("C3", "C512"):
            entry["claims"] = [{"kind": "documented", "evidence": "modelled-current",
                                "text": "This part was changed to a 22 uF 25 V X7R in a 1210 package after a "
                                        "capacitance review: under DC bias the previous choice fell below the "
                                        "reservoir the design needs. The screen used characterised sample data "
                                        "plus an engineering reserve, not guaranteed lifetime minima.",
                                "basis": "engineering-history/rev_a_capacitor_correction.md"}]
        return entry

    if family == "divider":
        partner, top, node, purpose = DIVIDERS[ref]
        entry.update(
            name="Divider leg on %s" % node,
            circuit=CIRCUIT_OF.get(ref, "input"),
            here=("One half of the divider that sets %s. Working with %s, it turns %s into a smaller voltage on "
                  "%s -- this part's own connections here are %s and %s. Change either resistor and the "
                  "threshold moves."
                  % (purpose, partner, top, node, pins["1"], pins["2"])),
            how=("Two resistors in series across a voltage produce a fraction of it at their junction, set by "
                 "their ratio. A chip that must react to a 24 V rail cannot look at it directly, because its "
                 "input pins work at a few volts, so the divider scales the rail into range. Changing either "
                 "resistor moves the threshold."),
            related=[partner],
        )
        entry["claims"] = [{
            "kind": "documented", "evidence": "intended",
            "text": "The threshold is set by the ratio of this resistor to %s, so both have to be right. "
                    "Neither value is adjustable in firmware." % partner,
            "basis": "hardware-current/engineering/design_parts.json"}]
        return entry

    if family in ("pullup", "pulldown"):
        direction, rail, node, purpose = PULLS[ref]
        entry.update(
            name="%s %s" % (node, "pull-up" if direction == "up" else "pull-down"),
            circuit=CIRCUIT_OF.get(ref, "mcu"),
            here=("Ties %s to %s, which %s. Its two connections here are %s and %s, and it is the part that "
                  "decides what %s reads when nothing on the board is actively driving it."
                  % (node, rail, purpose, pins["1"], pins["2"], node)),
            how=("A logic line that nothing is actively driving does not read as a clean high or low: it floats "
                 "and picks up noise. A resistor to a rail decides what the line reads when nobody drives it, "
                 "while staying weak enough for a driver to override."),
            related=[],
        )
        entry["claims"] = [{
            "kind": "documented", "evidence": "intended",
            "text": "%s therefore reads as %s whenever nothing is driving it, including before any firmware "
                    "runs." % (node, "high" if direction == "up" else "low"),
            "basis": "board.json nets, and the default-off requirement in the inhibit review"}]
        return entry

    if family == "setting":
        node, purpose = SETTINGS[ref]
        entry.update(
            name="Setting resistor on %s" % node,
            circuit=CIRCUIT_OF.get(ref, "input"),
            here=("Connected to %s, where it %s. Its two connections here are %s and %s, so its value is part of "
                  "the circuit's configuration rather than something firmware can change."
                  % (node, purpose, pins["1"], pins["2"])),
            how=("Many power-management chips are configured by a resistor rather than by software: the chip "
                 "pushes a known current out of the pin, or compares the pin against an internal reference, and "
                 "reads the resistor's value as a setting. The number is fixed when the board is built."),
            related=[],
        )
        entry["claims"] = [{
            "kind": "documented", "evidence": "intended",
            "text": "This is a configuration value chosen at design time. Changing it changes the circuit's "
                    "behaviour and needs the same review the original choice had.",
            "basis": "hardware-current/engineering/design_parts.json"}]
        return entry

    if family == "test_point":
        net = comp["value"]
        entry.update(
            name="Test point on %s" % net,
            circuit="test",
            here=("A bare 1 mm pad connected to %s, put there so that net can be probed during bring-up without "
                  "touching a component lead or bridging two of them. It is on the %s face."
                  % (net, "front" if comp["side"] == "F" else "back")),
            how=("A test point is copper the PCB makes for you: no part is fitted, nothing is purchased, and it "
                 "does not appear in the parts list. It exists so bring-up has somewhere safe to put a probe."),
            inspect=TP_EXPECT.get(ref),
            related=[],
        )
        entry["claims"] = [{"kind": "documented", "evidence": "intended",
                            "text": "The expectation above comes from the project's first-hardware checklist, "
                                    "which is a plan. Nothing on it has been carried out.",
                            "basis": "engineering-history/first_hardware_checklist.md"}]
        return entry

    if family == "boot_strap_probe":
        net = pins.get("1") or comp["value"]
        entry.update(
            name="Boot-strap probe pad (%s)" % net,
            circuit="expansion",
            here=("A bare pad on %s, one of the controller module's boot-strap pins. It is here so the strap can "
                  "be observed during bring-up, not so an accessory can be wired to it." % net),
            how=("Boot straps are pins the module samples once, as it leaves reset, to decide how to start. A "
                 "voltage imposed here during reset changes that decision, which is why these are probe points "
                 "and not general-purpose expansion pins."),
            related=["U1", "J18"],
        )
        entry["claims"] = [{"kind": "documented", "evidence": "intended",
                            "text": "Boot straps are not unrestricted expansion GPIOs: externally imposed levels "
                                    "during reset can change how the module boots.",
                            "basis": "hardware-current/engineering/enclosure_addendum.md"}]
        return entry

    if family == "mounting_hole":
        entry.update(
            name="M3 mounting hole",
            circuit="mechanical",
            here=("One of the four M3 holes that hold the board in the fixture. It is 3.2 mm and unplated, so it "
                  "makes no electrical connection to anything."),
            how=("Unplated -- NPTH -- means the hole has no copper barrel: it is purely mechanical. The four "
                 "holes form a trapezoid rather than a square: 34 mm across the upper pair, 48 mm across the "
                 "lower pair, 53.5 mm between the rows, so the board only fits its mounts one way round."),
            related=[r for r in ("H1", "H2", "H3", "H4") if r != ref],
        )
        entry["claims"] = [
            {"kind": "documented", "evidence": "cad-checked",
             "text": "Each hole reserves an 8 mm diameter for the screw head and standoff, and the mechanical "
                     "audit found no pad or courtyard from either face inside that reserve.",
             "basis": "hardware-current/reports/mechanical-final-audit.json"},
            {"kind": "documented", "evidence": "intended",
             "text": "Nonmetallic M3 screws and standoffs are recommended near the upper pair, which sits close to "
                     "the radio antenna. The 8 mm reserve is not permission to fit a larger washer.",
             "basis": "hardware-current/manufacturing/enclosure_assembly_notes.md"},
        ]
        entry["open"] = ["Radio behaviour inside a real enclosure, with real fasteners and cables, is unmeasured."]
        return entry

    if family == "expansion_pads":
        entry.update(
            name="Expansion solder pads",
            circuit="expansion",
            here=("Seven bare lands on the back face: %s. No header is fitted -- these are pads the PCB makes, "
                  "not a purchased connector." % _contacts(pins)),
            how=("The five GPIO lines are spare controller pins brought out so a future accessory can be soldered "
                 "on. They are 3.3 V logic with no protection of their own."),
            related=["U1"],
        )
        entry["claims"] = [{"kind": "documented", "evidence": "intended",
                            "text": "3.3 V logic only. Do not back-power the rail through these pads, and do not "
                                    "assume a spare peripheral power budget; any accessory needs its own input "
                                    "and output protection.",
                            "basis": "hardware-current/engineering/enclosure_addendum.md"}]
        return entry

    if family == "jumper":
        entry.update(
            name="CAN termination jumper",
            circuit="can",
            here=("Two bare pads in series with the 120 Ohm terminator R22, between %s and %s. As manufactured "
                  "the jumper is open, so the terminator is not connected." % (pins["1"], pins["2"])),
            how=("A CAN bus needs exactly two terminators, one at each physical end. Whether this board is an end "
                 "depends on how the harness is built, so termination is a solder decision rather than a fixed "
                 "part: bridge these two pads only if this board is one of the two ends."),
            related=["R22", "U4", "J12", "J13"],
        )
        entry["claims"] = [{"kind": "documented", "evidence": "intended",
                            "text": "Check for roughly 60 Ohm across the finished bus -- what two 120 Ohm "
                                    "terminators in parallel look like -- before powering it.",
                            "basis": "engineering-history/first_hardware_checklist.md"}]
        return entry

    raise KeyError("no template for family %s (%s)" % (family, ref))
