#!/usr/bin/env python3
"""Build the published assets and generated page blocks for Doc 9.

Three modes:

  build --handoff H   read the hash-verified handoff, derive and copy every
                      published asset into docs/assets/pcb/light-v0.1/
  render              regenerate the page's static blocks from the published
                      JSON (no handoff needed)
  check               re-verify hashes, counts and generated blocks against
                      what is committed (no handoff needed -- this is what CI
                      and the data tests run)

The handoff is opened read-only. Nothing under it is ever written, and the
KiCad exporter is never re-run.

Standard library only: the site's requirements are pinned and CI installs
exactly that list.
"""

import argparse
import hashlib
import json
import math
import re
import shutil
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import svgprep  # noqa: E402
import teaching  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DOCS = REPO / "docs"
ASSETS = DOCS / "assets" / "pcb" / "light-v0.1"
PAGE = DOCS / "09-understand-the-pcb.md"

PCB_SHA = "c046202efa3896d59d12bf19f55ed48b3a6c77532aac199a3a1e9a993e449310"
ZIP_SHA = "029f02282a4500ad541a31513062dc8ef4b7426aef1c0547d51f07ee4b459d8d"
CSV_SHA = "d9308529a10ce194e19765466474dc2ceda12c8e35fa6eeddf06806462911756"
SHORT = "c046202e"
REVISION = "LIGHT v0.1 — enclosure revision"
SCHEMA = "el-pcb/1"
GENERATED = "2026-09-07"

SCOPE = (
    "As of 7 September 2026, PCBWay has been asked to quote five fabricated boards, two of them fully "
    "assembled with all 248 purchased parts and three supplied bare. Nothing has been paid or authorised, "
    "and the assembly process, stencil and via treatment and any factory substitutions are not approved."
)

LAYERS = [
    # id, KiCad name, kind, side, z, label, plain-language note
    ("Edge_Cuts", "Edge.Cuts", "edge", None, 0, "Board outline",
     "the shape the board is cut to, including the flat under the antenna"),
    ("In6_Cu", "In6.Cu", "copper", None, 1, "Inner copper 6 (In6.Cu)", "a ground layer"),
    ("In5_Cu", "In5.Cu", "copper", None, 2, "Inner copper 5 (In5.Cu)", "signals and protected branches"),
    ("In4_Cu", "In4.Cu", "copper", None, 3, "Inner copper 4 (In4.Cu)", "signals"),
    ("In3_Cu", "In3.Cu", "copper", None, 4, "Inner copper 3 (In3.Cu)", "a ground layer"),
    ("In2_Cu", "In2.Cu", "copper", None, 5, "Inner copper 2 (In2.Cu)", "24 V distribution"),
    ("In1_Cu", "In1.Cu", "copper", None, 6, "Inner copper 1 (In1.Cu)", "the ground reference under the outer layer"),
    ("B_Cu", "B.Cu", "copper", "B", 7, "Back copper (B.Cu)", "components, signals and local power on the back"),
    ("F_Cu", "F.Cu", "copper", "F", 8, "Front copper (F.Cu)", "components, signals and local power on the front"),
    ("B_Mask", "B.Mask", "mask", "B", 9, "Back mask openings",
     "where the coating is left off so copper stays exposed -- not the coating itself"),
    ("F_Mask", "F.Mask", "mask", "F", 9, "Front mask openings",
     "where the coating is left off so copper stays exposed -- not the coating itself"),
    ("B_Silkscreen", "B.Silkscreen", "silk", "B", 10, "Back silkscreen", "printed ink labels, not connections"),
    ("F_Silkscreen", "F.Silkscreen", "silk", "F", 10, "Front silkscreen", "printed ink labels, not connections"),
    ("B_Fab", "B.Fab", "fab", "B", 11, "Back assembly outlines",
     "component bodies and reference labels for assembly -- not an electrical layer"),
    ("F_Fab", "F.Fab", "fab", "F", 11, "Front assembly outlines",
     "component bodies and reference labels for assembly -- not an electrical layer"),
    ("B_Courtyard", "B.Courtyard", "courtyard", "B", 12, "Back courtyard",
     "the clearance each part reserves around itself -- nothing physical"),
    ("F_Courtyard", "F.Courtyard", "courtyard", "F", 12, "Front courtyard",
     "the clearance each part reserves around itself -- nothing physical"),
]

SHEET_PLAIN = {
    1: ("The hierarchy map. It has no components of its own -- each box is one of the other 18 sheets, "
        "labelled with its file name.", ["Start here to see how the design is divided"]),
    2: ("The controller: the radio module, its reset and boot circuitry, the UART service port and the ARM "
        "input.", ["U1", "S1", "S2", "J17"]),
    3: ("The power sequence: the supervisor and the gate that decides when lighting is allowed.", ["U18", "U19"]),
    4: ("CAN: the transceiver, its protection, the termination option and both motor connectors.",
        ["U4", "R22", "J12", "J13"]),
    5: ("The USB-C island: connector, protection, presence sensing and the data multiplexer.",
        ["J14", "U17", "U15", "Q30"]),
    6: ("The two PWM expanders and the I2C bus that reaches them.", ["U2", "U3", "R7", "R8"]),
    7: ("Ambient zone 1: three channels, each a gate network and a low-side switch.", ["Q101", "R101", "J2"]),
    8: ("Ambient zone 2, identical in shape to zone 1.", ["Q104", "J3"]),
    9: ("Ambient zone 3, identical in shape to zone 1.", ["Q107", "J4"]),
    10: ("Ambient zone 4, identical in shape to zone 1.", ["Q110", "J5"]),
    11: ("Ambient zone 5, identical in shape to zone 1.", ["Q113", "J6"]),
    12: ("Ambient zone 6, identical in shape to zone 1.", ["Q116", "J7"]),
    13: ("Ambient zone 7 -- the bottom ring. Its connector mates downward from the back face.", ["Q119", "J8"]),
    14: ("The test points: every pad bring-up expects to probe.", ["TP1", "TP7"]),
    15: ("Power, part 1: the input protection chain and the branch fuses.", ["U12", "Q500", "F1", "C504"]),
    16: ("Power, part 2: the 24 V input terminal and the two switching converters.", ["J1", "U10", "U11"]),
    17: ("Spotlight, part 1: the gated supply and the three constant-current driver cells.",
         ["U14", "U7", "U8", "U9"]),
    18: ("Spotlight, part 2: the driver outputs and their connectors.", ["J9", "J10", "J11"]),
    19: ("Monitoring and expansion: the temperature sensor, the expansion pads, the boot-strap probes and the "
         "mounting holes.", ["U20", "J18", "H1"]),
}

VALIDATION_PASSED = [
    ("Electrical rules (ERC)", "0 violations across all 19 schematic sheets", "KiCad 10.0.3 on this schematic"),
    ("Design rules (DRC)", "0 violations, 0 unconnected items, 0 parity errors", "KiCad 10.0.3 on this layout"),
    ("Board / schematic parity", "269 components in the manifest, the netlist export and the PCB; 780 logical "
     "pins, 751 assigned and 29 explicitly unconnected; 887 physical pad objects", "parity report"),
    ("Net continuity", "each of the 163 assigned nets forms exactly one connected island of copper",
     "mechanical audit"),
    ("Drill and solder lands", "795 holes and 852 solder-land faces screened; 0 unexpected overlaps, 76 "
     "intentional ones (the USB shield stakes and the exposed pads)", "drill/solder-land audit"),
    ("Mechanical and mounting", "8 copper layers in a 76.2 mm envelope; all four M3 holes keep their 8 mm "
     "reserve clear of pads and courtyards on both faces", "mechanical audit"),
    ("USB ground coverage", "the sampled ground projection under all four USB data routes had no uncovered "
     "sample points", "mechanical audit"),
    ("Antenna keepout", "no tracks, vias or copper pours under the module's antenna on any of the eight layers",
     "mechanical audit"),
    ("Silkscreen variants", "the eight silk-adapted footprints keep electrically identical lands, within 2 nm",
     "silk variant audit"),
    ("Parts list", "269 component instances, 248 purchased, 74 exact part-and-footprint rows, 21 excluded PCB "
     "features; no missing footprints or unassigned pads", "BOM audit"),
    ("Copper resistance", "43 power and return nets solved across 7 load states. At a modelled 4 A input the "
     "input copper drop is 59.68 mV nominal and 85.66 mV in the thin/hot sensitivity case; distribution copper "
     "loss is 0.2972 W and 0.4265 W. This excludes components, connector contacts and the spotlight lead "
     "models, and it is not a thermal result", "DC solver on this layout"),
]

VALIDATION_NOT_DONE = [
    "No board has been powered. There is no measurement of any kind on this revision.",
    "No firmware has been built or flashed. The channel map is an integration contract, not code.",
    "The factory stack-up, finished thickness, copper weight and plating are not accepted yet.",
    "The 90 Ohm USB differential geometry is a request to the factory. Thirteen modelled cases on the native "
    "geometry spread from 71 to 114 Ohm.",
    "No USB certification, enumeration test or electrostatic-discharge test.",
    "The coupled startup of the two switching converters was never qualified; the vendor model would not run.",
    "Real falling-edge timing, reset recovery and inhibit behaviour are hardware observations not yet made.",
    "No EMC, radio or in-enclosure antenna measurement.",
    "Motor regeneration has no qualified path. Nothing on this board is a brake.",
    "No enclosed-temperature measurement, and no completed mesh-convergence study behind the copper solve.",
    "Actual strip and motor currents are unmeasured; the load model is conditional arithmetic.",
    "Iron-only solderability has not been established, and no assembly process has been approved.",
]

FORBIDDEN_EVERYWHERE = [
    (r"[A-Za-z]:[\\/]Users[\\/]", "a Windows user path"),
    (r"/Users/", "a home directory path"),
    (r"Marcelo", "the author's name"),
    (r"W1144574AS7C1", "a vendor message id"),
    (r"ParentId", "a vendor message id"),
    (r"website_quote_quantity", "quote quantities"),
    (r"purchased_quantity", "quote quantities"),
]
FORBIDDEN_IN_ASSETS = [
    (r"assembles locally", "superseded assembly wording"),
    (r"iron-only", "superseded assembly wording"),
]

MARK = "<!-- el-pcb:generated %s %s -->"


# --------------------------------------------------------------------------- helpers
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def write_bytes(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data)


def write_json(path, obj):
    text = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    write_bytes(path, text.encode("utf-8"))


def write_text(path, text):
    write_bytes(path, text.encode("utf-8"))


def read_json(path):
    with open(path, "rb") as fh:
        return json.loads(fh.read().decode("utf-8"))


def header(extra=None):
    h = {"schema": SCHEMA, "pcb_sha256": PCB_SHA, "revision": REVISION, "generated": GENERATED}
    if extra:
        h.update(extra)
    return h


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def human_bytes(n):
    if n >= 1024 * 1024:
        return "%.1f MB" % (n / 1048576.0)
    if n >= 1024:
        return "%.0f kB" % (n / 1024.0)
    return "%d bytes" % n


def ref_key(ref):
    m = re.match(r"^([A-Za-z]+)(\d+)$", ref)
    return (m.group(1), int(m.group(2))) if m else (ref, 0)


# Pad outlines are drawn as translate(cx cy) rotate(-rot) around the pad centre.
# A pad's axis-aligned box is the rotated *inner* rectangle grown by the corner
# radius, which is why a rotated rounded pad is smaller than a sharp one.
def pad_extent(pad):
    w, h = pad["size"]
    t = math.radians(pad["rot"])
    shape = pad["shape"]
    if shape == 0:
        return w, h
    if shape == 2:
        r = min(w, h) / 2.0
    elif shape in (4, 5):
        r = pad.get("r") or 0.0
    else:
        r = 0.0
    iw, ih = max(w - 2 * r, 0.0), max(h - 2 * r, 0.0)
    return (abs(iw * math.cos(t)) + abs(ih * math.sin(t)) + 2 * r,
            abs(iw * math.sin(t)) + abs(ih * math.cos(t)) + 2 * r)


def check_pad_geometry(components):
    """Every pad's drawn outline must reproduce the exported bounding box, and
    the rotation sign must be the one that puts J12/J13's pad rows square to
    their pad axes. Custom-shaped pads are drawn from their box and excluded."""
    custom = []
    for c in components:
        for pad in c["pads"]:
            if pad["shape"] == 6:
                custom.append("%s.%s" % (c["ref"], pad["n"]))
                continue
            ew, eh = pad_extent(pad)
            if abs(ew - pad["bbox"][2]) > 1e-3 or abs(eh - pad["bbox"][3]) > 1e-3:
                sys.exit("pad %s.%s does not reproduce its exported box" % (c["ref"], pad["n"]))
    by_ref = {c["ref"]: c for c in components}
    for ref in ("J12", "J13"):
        pads = {p["n"]: p for p in by_ref[ref]["pads"]}
        p1, p3 = pads["1"]["xy"], pads["3"]["xy"]
        row = (p3[0] - p1[0], p3[1] - p1[1])
        length = math.hypot(*row)
        row = (row[0] / length, row[1] / length)
        t = math.radians(-by_ref[ref]["rot"])
        axis = (-math.sin(t), math.cos(t))
        if abs(axis[0] * row[0] + axis[1] * row[1]) > 0.02:
            sys.exit("%s: rotate(-rot) does not put the pad row square to the pad axis -- "
                     "the rotation sign is wrong" % ref)
    return sorted(custom)


# --------------------------------------------------------------------------- build
def build(handoff):
    H = Path(handoff)
    if not H.is_dir():
        sys.exit("handoff folder not found: %s" % H)

    src_pcb = H / "hardware-current/hardware/rev-a/engineered-lighting-rev-a.kicad_pcb"
    src_zip = H / "downloads/LIGHT-v0.1-c046202e-KiCad-project.zip"
    src_csv = H / "hardware-current/manufacturing/quote_bom.csv"
    for path, want, what in ((src_pcb, PCB_SHA, "governing PCB"),
                             (src_zip, ZIP_SHA, "KiCad project ZIP"),
                             (src_csv, CSV_SHA, "BOM CSV")):
        got = sha256(path)
        if got != want:
            sys.exit("%s hash mismatch\n  expected %s\n  got      %s" % (what, want, got))
    print("hash chain verified: PCB, project ZIP and BOM CSV all match the governing revision")

    board_src = read_json(H / "viewer-data/board.json")
    bom_src = read_json(H / "viewer-data/bom.json")
    sch_src = read_json(H / "schematic-view/index.json")
    zip_src = read_json(H / "downloads/index.json")
    for name, obj in (("board.json", board_src), ("bom.json", bom_src), ("schematic index", sch_src)):
        if obj.get("pcb_sha256") != PCB_SHA:
            sys.exit("%s does not carry the governing hash" % name)

    if ASSETS.exists():
        shutil.rmtree(ASSETS)
    ASSETS.mkdir(parents=True)

    provenance = {"sources": {}, "layers": {}, "schematic": {}, "census": {}, "notes": []}
    provenance["sources"] = {
        "engineered-lighting-rev-a.kicad_pcb": {"sha256": PCB_SHA, "bytes": src_pcb.stat().st_size},
        "LIGHT-v0.1-c046202e-KiCad-project.zip": {"sha256": ZIP_SHA, "bytes": src_zip.stat().st_size},
        "quote_bom.csv": {"sha256": CSV_SHA, "bytes": src_csv.stat().st_size,
                          "encoding": "UTF-8 with byte-order mark"},
        "handoff_folder": H.name,
    }

    # ---- layers -----------------------------------------------------------
    by_side = {"F": set(), "B": set()}
    for c in board_src["components"]:
        by_side[c["side"]].add(c["ref"])

    layer_meta = []
    for lid, kicad, kind, side, z, label, plain in LAYERS:
        src = H / "viewer-data/layers" / ("%s.svg" % lid)
        text = src.read_text(encoding="utf-8")
        refs = by_side[side] if kind == "fab" and side else set()
        out, stats = svgprep.prepare(
            text, refs=refs, recolour=True, normalise_mask=(kind == "mask"),
            extra_attrs={"data-layer": lid})
        counts = svgprep.verify(text, out)
        dest = ASSETS / "layers" / ("%s.svg" % lid)
        write_text(dest, out)
        layer_meta.append({
            "id": lid, "kicad": kicad, "kind": kind, "side": side, "z": z,
            "file": "layers/%s.svg" % lid, "label": label, "plain": plain,
            "bytes": dest.stat().st_size, "sha256": sha256(dest),
        })
        provenance["layers"][lid] = {
            "source_sha256": sha256(src), "source_bytes": src.stat().st_size,
            "published_sha256": sha256(dest), "published_bytes": dest.stat().st_size,
            "paths": counts["paths"], "circles": counts["circles"],
            "groups_before": counts["groups_before"], "groups_after": counts["groups_after"],
            "text_removed": counts["text_before"], "text_after": stats["text_after"],
            "hex_colors_after": stats["hex_colors_after"],
            "data_ref_tags": stats["data_ref_tags"], "data_ref_unique": stats["data_ref_unique"],
        }
        if kind == "fab" and side:
            missing = by_side[side] - set(stats["tagged_refs"])
            if missing:
                sys.exit("%s is missing reference labels for %s" % (lid, sorted(missing)[:8]))
    print("17 layer plots prepared (colours neutralised, invisible text removed, Fab labels tagged)")

    # ---- silhouette -------------------------------------------------------
    edge = (H / "viewer-data/layers/Edge_Cuts.svg").read_text(encoding="utf-8")
    arc = re.search(r'd="(M([\d.]+) ([\d.]+) A([\d.]+) ([\d.]+) ([\d.]+) (\d) (\d) ([\d.]+) ([\d.]+))"', edge)
    if not arc:
        sys.exit("could not find the outline arc in Edge_Cuts.svg")
    sx, sy, rx, ry, rot, large, sweep, ex, ey = (float(arc.group(i)) if i not in (7, 8) else int(arc.group(i))
                                                 for i in range(2, 11))
    silhouette = "%s Z" % arc.group(1)
    cx, cy = board_src["center_mm"]
    r = board_src["nominal_radius_mm"]
    chord = float(board_src["antenna_chord_y_mm"])
    computed = [cx - r, chord, 2 * r, cy + r - chord]
    outline = board_src["outline_bounds_mm"]
    if max(abs(a - b) for a, b in zip(computed, outline)) > 1e-6:
        sys.exit("silhouette bbox %s does not match the outline %s" % (computed, outline))
    if abs(sx - (cx - (r ** 2 - (cy - chord) ** 2) ** 0.5)) > 1e-3 or abs(sy - chord) > 1e-6:
        sys.exit("outline arc does not start on the antenna chord")

    # ---- components -------------------------------------------------------
    ref_to_sheet = {k: int(v) for k, v in sch_src["component_to_sheet"].items()}
    sheet_title = {s["number"]: s["title"] for s in sch_src["sheets"]}
    bom_rows_src = bom_src["rows"]
    row_by_item = {r["Item"]: r for r in bom_rows_src}

    components = []
    nets = {}
    features = []
    xs0, ys0, xs1, ys1 = [], [], [], []
    through_set, thermal = [], {}
    for c in sorted(board_src["components"], key=lambda c: ref_key(c["ref"])):
        ref = c["ref"]
        pkg = teaching.PACKAGES.get(c["footprint"])
        if not pkg:
            sys.exit("no plain-language package description for %s (%s)" % (ref, c["footprint"]))
        if ref not in ref_to_sheet:
            sys.exit("%s has no schematic sheet" % ref)
        row = row_by_item.get(c["bom_item"]) if c["bom_item"] else None
        pads = []
        n_thermal = 0
        is_through = False
        paste_only = 0
        for i, p in enumerate(c["pads"]):
            entry = {
                "i": i, "n": p["number"], "net": p["net"], "xy": p["xy_mm"], "size": p["size_mm"],
                "rot": p["rotation_deg_native"], "bbox": p["bbox_mm"], "shape": p["shape"],
                "r": p["roundrect_radius_mm"], "attr": p["attribute"],
            }
            drill = max(p["drill_mm"]) if p["drill_mm"] else 0.0
            if drill > 0:
                entry["drill"] = p["drill_mm"]
            if not p["copper_layers"]:
                entry["paste"] = True
                paste_only += 1
            if p["attribute"] == 3 or (p["attribute"] == 0 and drill >= 0.5):
                is_through = True
                entry["through"] = True
            elif p["attribute"] == 0 and 0 < drill < 0.5:
                n_thermal += 1
            pads.append(entry)
        if is_through:
            through_set.append(ref)
        if n_thermal:
            thermal[ref] = n_thermal
        for pin, net in c["pins"].items():
            if net and not net.startswith("unconnected-"):
                nets.setdefault(net, []).append([ref, pin])
        if not c["purchased_component"]:
            features.append(ref)
        b = c["bbox_without_text_mm"]
        xs0.append(b[0]); ys0.append(b[1]); xs1.append(b[0] + b[2]); ys1.append(b[1] + b[3])
        components.append({
            "ref": ref, "side": c["side"], "xy": c["xy_mm"], "rot": c["rotation_deg_native"],
            "bbox": b, "value": c["value"], "mpn": c["mpn"], "fp": c["footprint"], "pkg": pkg,
            "mfr": (row["Manufacturer"] if row else c["manufacturer"]),
            "sheet": ref_to_sheet[ref], "sheet_title": sheet_title[ref_to_sheet[ref]],
            "bom": int(c["bom_item"]) if c["bom_item"] else None,
            "feature": not c["purchased_component"],
            "through": is_through, "thermal_vias": n_thermal, "paste_only_pads": paste_only,
            "pins": c["pins"], "pads": pads,
            "uuid": {"fp": c["footprint_uuid"], "sch": c["schematic_uuid"]},
            "assembly_note": c["assembly_note"],
            "primary_source": c["primary_source"], "source_context": c["source_context"],
        })

    if sorted(through_set) != ["H1", "H2", "H3", "H4", "J14"]:
        sys.exit("unexpected through-feature set: %s" % sorted(through_set))
    custom_pads = check_pad_geometry(components)
    print("pad geometry verified: 887 outlines reproduce their exported boxes, "
          "rotation sign confirmed against J12 and J13")
    union = [min(xs0), min(ys0), max(xs1) - min(xs0), max(ys1) - min(ys0)]
    fit_x0 = min(union[0], 200 - (union[0] + union[2]), outline[0])
    fit_x1 = max(union[0] + union[2], 200 - union[0], outline[0] + outline[2])
    fit_y0 = min(union[1], outline[1])
    fit_y1 = max(union[1] + union[3], outline[1] + outline[3])
    fit = [round(fit_x0, 6), round(fit_y0, 6), round(fit_x1 - fit_x0, 6), round(fit_y1 - fit_y0, 6)]

    board = header()
    board.update({
        "frame": {
            "viewBox": [0, 0, 297.0022, 210.0072],
            "center": board_src["center_mm"], "outline": outline,
            "radius": r, "chord_y": chord,
            "components_union": [round(v, 6) for v in union], "fit": fit,
            "silhouette_path": silhouette,
            "mirror": "x' = 200 - x, applied once to the whole geometry group",
        },
        "layers": layer_meta,
        "synthetic_layers": [
            {"id": "Lands", "label": "Lands",
             "plain": "the exposed copper each component solders to, drawn from the board's own pad data"},
            {"id": "Holes", "label": "Holes",
             "plain": "component and mounting holes from the pad data -- the board's vias are not listed here"},
        ],
        "sides": {"F": len(by_side["F"]), "B": len(by_side["B"])},
        "components": components,
        "nets": nets,
        "features": features,
        "notes": [
            "Coordinates are absolute KiCad millimetres, x right and y down, in the shared unmirrored top view.",
            "Pad positions are already world-positioned: never rotate them again by the footprint angle.",
            "Footprint boxes exclude text but include graphics and pads. They are conservative hit candidates, "
            "not exact silhouettes.",
        ],
    })
    write_json(ASSETS / "board.json", board)

    # ---- enums ------------------------------------------------------------
    enums = header()
    enums.update({
        "shape": {"0": "circle", "1": "rect", "2": "oval", "3": "trapezoid", "4": "roundrect",
                  "5": "chamfered rect", "6": "custom"},
        "attribute": {"0": "plated through-hole", "1": "surface mount", "2": "edge connector",
                      "3": "unplated hole"},
    })
    write_json(ASSETS / "enums.json", enums)

    # ---- BOM --------------------------------------------------------------
    rows = []
    ref_to_item = {}
    total = 0
    for r_ in sorted(bom_rows_src, key=lambda r: int(r["Item"])):
        refs = [x.strip() for x in r_["Designators"].split(",") if x.strip()]
        qty = int(r_["Quantity per board"])
        if len(refs) != qty:
            sys.exit("BOM row %s lists %d references for a quantity of %d" % (r_["Item"], len(refs), qty))
        for ref in refs:
            if ref in ref_to_item:
                sys.exit("%s appears in more than one BOM row" % ref)
            ref_to_item[ref] = int(r_["Item"])
        total += qty
        sides = {"F": 0, "B": 0}
        for ref in refs:
            sides[[c for c in components if c["ref"] == ref][0]["side"]] += 1
        rows.append({
            "item": int(r_["Item"]), "refs": refs, "qty": qty,
            "qty2": int(r_["Quantity for 2 prototypes (no attrition)"]),
            "value": r_["Value / description"], "mfr": r_["Manufacturer"],
            "mpn": r_["Manufacturer part number"], "fp": r_["KiCad footprint"],
            "pkg": teaching.PACKAGES.get(r_["KiCad footprint"], ""),
            "note": r_["Assembly / engineering note"],
            "source": r_["Primary source"], "source_context": r_["Source revision / context"],
            "evidence_url": r_["Sourcing evidence URL"], "sides": sides,
        })
    if total != 248 or len(rows) != 74:
        sys.exit("BOM totals wrong: %d rows, %d packages" % (len(rows), total))

    note_updates = [
        {"refs": ["C3", "C512"],
         "text": "The row's note still asks for DC-bias characterisation. For these two references that work was "
                 "completed: both were changed to a 22 uF 25 V X7R in a 1210 package after a capacitance review, "
                 "and the screens passed on characterised sample data plus an engineering reserve. The other "
                 "references on this row were not part of that screen.",
         "basis": "engineering-history/rev_a_capacitor_correction.md"},
        {"refs": ["J1"],
         "text": "This terminal takes stripped wire directly; there is no mating plug to order.",
         "basis": "hardware-current/manufacturing/enclosure_assembly_notes.md"},
    ]
    bom = header()
    bom.update({
        "csv_sha256": CSV_SHA,
        "csv_file": "downloads/LIGHT-v0.1-%s-bom.csv" % SHORT,
        "totals": {"rows": 74, "per_board": 248, "two_boards": 496, "features": len(features)},
        "status": SCOPE + " This is the exact part selection that matches the c046202e layout. No stock or "
                          "price is claimed here.",
        "order_status_note": "Every row of the source CSV carries the same order status: "
                             "\"QUOTE ONLY - exact source/quantity/process not confirmed\".",
        "rows": rows, "ref_to_item": ref_to_item, "note_updates": note_updates,
        "features": [{"ref": f, "why_not_purchased":
                      "Made with the PCB itself -- copper, a hole or bare pads -- so it is not a purchased package."}
                     for f in sorted(features, key=ref_key)],
    })
    write_json(ASSETS / "bom.json", bom)

    # ---- teaching ---------------------------------------------------------
    teach = header()
    entries = {}
    fam_refs = {}
    src_by_ref = {c["ref"]: c for c in board_src["components"]}
    for c in components:
        ref = c["ref"]
        e = teaching.build_entry(ref, src_by_ref[ref])
        e["sheet"] = c["sheet"]
        e["bom"] = c["bom"]
        e["nets"] = [{"pin": p, "net": n, "role": ("no connect (intentional)" if n is None else "")}
                     for p, n in sorted(c["pins"].items(), key=lambda kv: (len(kv[0]), kv[0]))]
        sources = []
        if c["primary_source"]:
            sources.append({"label": "Primary source", "url": c["primary_source"],
                            "context": c["source_context"] or ""})
        row = next((r for r in rows if r["item"] == c["bom"]), None)
        if row and row["evidence_url"] and row["evidence_url"] != c["primary_source"]:
            sources.append({"label": "Sourcing evidence", "url": row["evidence_url"], "context": ""})
        e["sources"] = sources
        if not e["related"]:
            # Nothing hand-picked: offer the neighbours on this part's most
            # specific net, which is what a reader would look for next.
            own = [n for n in set(c["pins"].values()) if n and n in nets]
            own.sort(key=lambda n: len(nets[n]))
            for net in own:
                if len(nets[net]) > 12:
                    continue
                for other, _pin in nets[net]:
                    if other != ref and other not in e["related"]:
                        e["related"].append(other)
                if len(e["related"]) >= 3:
                    break
            e["related"] = sorted(set(e["related"]), key=ref_key)[:6]
        if not e["related"]:
            e["related"] = [r for r in ("U1", "U12") if r != ref][:1]
        for rel in e["related"]:
            if rel not in ref_to_sheet:
                sys.exit("%s lists a related reference that does not exist: %s" % (ref, rel))
        fam_refs.setdefault(e["family"], []).append(ref)
        entries[ref] = e
    teach.update({
        "vocab": teaching.VOCAB, "legend": teaching.LEGEND, "circuits": teaching.CIRCUITS,
        "families": {f: {"label": teaching.FAMILIES[f][0], "refs": sorted(r, key=ref_key)}
                     for f, r in fam_refs.items()},
        "components": entries,
        "sheets": {str(n): {"plain": SHEET_PLAIN[n][0], "start_with": SHEET_PLAIN[n][1]}
                   for n in sorted(SHEET_PLAIN)},
    })
    write_json(ASSETS / "teaching.json", teach)
    print("teaching content built for %d references across %d families" % (len(entries), len(fam_refs)))

    # ---- schematic --------------------------------------------------------
    sheets = []
    for s in sch_src["sheets"]:
        n = s["number"]
        src = H / "schematic-view" / s["svg"]
        text = src.read_text(encoding="utf-8")
        refs = set(s["component_refs"])
        out, stats = svgprep.prepare(text, refs=refs, recolour=False,
                                     extra_attrs={"data-sheet": str(n)})
        svgprep.verify(text, out)
        if set(stats["tagged_refs"]) != refs:
            sys.exit("sheet %d tagged %d of %d references" % (n, stats["data_ref_unique"], len(refs)))
        dest = ASSETS / "schematic" / s["svg"]
        write_text(dest, out)
        sheets.append({
            "n": n, "path": s["sheet_path"], "title": s["title"], "native": s["native_source"],
            "file": "schematic/%s" % s["svg"], "bytes": dest.stat().st_size, "sha256": sha256(dest),
            "refs": sorted(refs, key=ref_key), "pdf_page": n,
            "plain": SHEET_PLAIN[n][0], "start_with": SHEET_PLAIN[n][1],
        })
        provenance["schematic"][str(n)] = {"source_sha256": s["svg_sha256"],
                                           "published_sha256": sha256(dest),
                                           "data_ref_tags": stats["data_ref_tags"]}
    index = header()
    index.update({"frame": {"viewBox": [0, 0, 419.9890, 297.0022]}, "sheets": sheets,
                  "ref_to_sheet": ref_to_sheet})
    write_json(ASSETS / "schematic/index.json", index)
    print("19 schematic sheets prepared and indexed")

    # ---- native sources ---------------------------------------------------
    zip_members = {}
    with zipfile.ZipFile(src_zip) as zf:
        names = zf.namelist()
        for name in names:
            zip_members[name] = sha256_bytes(zf.read(name))
    if any(n.endswith(".kicad_prl") for n in zip_members):
        sys.exit("the project ZIP contains a .kicad_prl")
    rev = H / "hardware-current/hardware/rev-a"
    native = ["engineered-lighting-rev-a.kicad_pro", "engineered-lighting-rev-a.kicad_pcb",
              "engineered-lighting-rev-a.kicad_sch"]
    native += sorted(p.name for p in rev.glob("*.kicad_sch")
                     if p.name != "engineered-lighting-rev-a.kicad_sch")
    for name in native:
        src = rev / name
        data = src.read_bytes()
        digest = sha256_bytes(data)
        if zip_members.get(name) != digest:
            sys.exit("%s does not match its member inside the project ZIP" % name)
        write_bytes(ASSETS / "kicad" / name, data)
    for sub in ("downloads", "assembly", "fabrication"):
        (ASSETS / sub).mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src_zip, ASSETS / "downloads" / src_zip.name)
    shutil.copyfile(src_csv, ASSETS / "downloads" / ("LIGHT-v0.1-%s-bom.csv" % SHORT))
    for rel in ("light-v0.1-review.pdf", "schematic.pdf"):
        shutil.copyfile(H / "hardware-current/reports" / rel, ASSETS / "downloads" / rel)
    for rel in ("assembly-top.svg", "assembly-bottom.svg"):
        shutil.copyfile(H / "hardware-current/reports" / rel, ASSETS / "assembly" / rel)
    fabdir = H / "fabrication-reference"
    for rel in ("engineered-lighting-rev-a-NPTH-drl_map.svg", "engineered-lighting-rev-a-PTH-drl_map.svg",
                "outline-mm.svg", "drill-report.txt"):
        shutil.copyfile(fabdir / "drawings" / rel, ASSETS / "fabrication" / rel)

    fab_zip = ASSETS / "fabrication" / ("LIGHT-v0.1-%s-fabrication-reference.zip" % SHORT)
    fab_zip.parent.mkdir(parents=True, exist_ok=True)
    readme = (
        "LIGHT v0.1 fabrication reference (revision %s)\n"
        "PCB SHA-256: %s\n\n"
        "These are manufacturing outputs generated from the same design source published beside them:\n"
        "Gerber artwork, Excellon drill files, the job file, an IPC-D-356 netlist and the drill drawings.\n\n"
        "They are a reference for reading the board, not a fabrication release. No quote, price, quantity or\n"
        "vendor correspondence is included. The .gbrjob finish and revision fields are KiCad defaults.\n"
        "Nothing here has been ordered or approved for production.\n" % (SHORT, PCB_SHA)
    )
    members = []
    for p in sorted((fabdir / "gerbers").glob("*")):
        members.append(("gerbers/" + p.name, p.read_bytes()))
    members.append(("engineered-lighting-rev-a.d356", (fabdir / "engineered-lighting-rev-a.d356").read_bytes()))
    for rel in ("drill-report.txt", "engineered-lighting-rev-a-NPTH-drl_map.svg",
                "engineered-lighting-rev-a-PTH-drl_map.svg", "outline-mm.svg"):
        members.append(("drawings/" + rel, (fabdir / "drawings" / rel).read_bytes()))
    members.append(("README.txt", readme.encode("utf-8")))
    with zipfile.ZipFile(fab_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in sorted(members):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, data)

    # ---- downloads manifest ----------------------------------------------
    def item(idx, label, rel, fmt, group, view, note, member=None, predates=False):
        path = ASSETS / rel
        entry = {"id": idx, "label": label, "file": rel, "format": fmt,
                 "bytes": path.stat().st_size, "sha256": sha256(path),
                 "group": group, "view": view, "note": note}
        if member:
            entry["zip_member_sha256"] = zip_members[member]
        if predates:
            entry["predates_scope"] = True
        return entry

    manifest = header({"source_csv_sha256": CSV_SHA})
    items = [
        item("project-zip", "Complete KiCad project (everything below, plus libraries)",
             "downloads/%s" % src_zip.name, "ZIP archive", "kicad", None,
             "Extract the whole archive together and open the project file. The root schematic depends on the "
             "18 child sheets, and the custom symbol and footprint libraries only exist inside this archive."),
        item("kicad-pro", "KiCad project settings", "kicad/engineered-lighting-rev-a.kicad_pro",
             "KiCad project", "kicad", None, "Opens the project in KiCad.",
             member="engineered-lighting-rev-a.kicad_pro"),
        item("kicad-pcb", "PCB layout (the board itself)", "kicad/engineered-lighting-rev-a.kicad_pcb",
             "KiCad board", "kicad", "viewer",
             "The physical layout this page's board viewer is generated from.",
             member="engineered-lighting-rev-a.kicad_pcb"),
        item("kicad-sch", "Root schematic sheet", "kicad/engineered-lighting-rev-a.kicad_sch",
             "KiCad schematic", "schematic", "schematic",
             "The root sheet on its own is not the whole design: it links to 18 child sheets, and without them "
             "it will not open completely.",
             member="engineered-lighting-rev-a.kicad_sch"),
        item("bom-csv", "Parts list (BOM)", "downloads/LIGHT-v0.1-%s-bom.csv" % SHORT,
             "CSV (UTF-8 with byte-order mark)", "bom", "bom",
             "The exact part selection for this layout: 74 rows, 248 packages per board."),
        item("review-pdf", "Four-page design review", "downloads/light-v0.1-review.pdf", "PDF", "review",
             "assembly", "An engineering review of this revision. Its own scope line says it is not a "
                         "fabrication release.", predates=True),
        item("schematic-pdf", "Complete schematic (19 pages)", "downloads/schematic.pdf", "PDF", "schematic",
             "schematic", "One page per sheet, in the same order as the sheet chooser above.", predates=True),
        item("assembly-top", "Assembly drawing, front", "assembly/assembly-top.svg", "SVG drawing", "assembly",
             "assembly", "Component outlines and reference labels for the front face."),
        item("assembly-bottom", "Assembly drawing, back", "assembly/assembly-bottom.svg", "SVG drawing",
             "assembly", "assembly", "Component outlines and reference labels for the back face. KiCad plots "
                                     "this one mirrored, as you would see it looking at the back of the board."),
        item("fab-zip", "Fabrication reference (Gerbers, drills, IPC-D-356)",
             "fabrication/LIGHT-v0.1-%s-fabrication-reference.zip" % SHORT, "ZIP archive", "fabrication", None,
             "Manufacturing outputs of the same source. Not a fabrication release, and not where a beginner "
             "edits the design."),
        item("drill-pth", "Drill map, plated holes", "fabrication/engineered-lighting-rev-a-PTH-drl_map.svg",
             "SVG drawing", "fabrication", "fabrication", "Every plated hole, by size."),
        item("drill-npth", "Drill map, unplated holes", "fabrication/engineered-lighting-rev-a-NPTH-drl_map.svg",
             "SVG drawing", "fabrication", "fabrication",
             "The unplated holes: the four M3 mounts and the two USB locating pegs."),
        item("outline", "Board outline drawing", "fabrication/outline-mm.svg", "SVG drawing", "fabrication",
             "fabrication", "The cut line with dimensions, in millimetres."),
        item("drill-report", "Drill report", "fabrication/drill-report.txt", "Text", "fabrication", None,
             "Hole counts by diameter: 789 plated and 6 unplated."),
    ]
    for n, sheet in enumerate(sheets):
        if sheet["n"] == 1:
            continue
        items.append(item("sch-%d" % sheet["n"], "Schematic sheet %d: %s" % (sheet["n"], sheet["title"]),
                          "kicad/%s" % sheet["native"], "KiCad schematic", "schematic", "schematic",
                          "One child sheet. Single sheet files do not carry the project's symbol and footprint "
                          "libraries -- only the complete archive does.",
                          member=sheet["native"]))
    manifest["items"] = items
    write_json(ASSETS / "downloads/manifest.json", manifest)

    # ---- provenance -------------------------------------------------------
    provenance["census"] = {
        "components": len(components), "front": len(by_side["F"]), "back": len(by_side["B"]),
        "purchased": 248, "features": len(features), "bom_rows": 74,
        "assigned_nets": len(nets), "explicit_no_connect_pins":
            sum(1 for c in board_src["components"] for v in c["pins"].values() if v is None),
        "pads": sum(len(c["pads"]) for c in components),
        "paste_only_pads": sum(c["paste_only_pads"] for c in components),
        "schematic_sheets": 19,
    }
    provenance["through_features"] = sorted(through_set)
    provenance["pad_geometry_rule"] = (
        "Pads are drawn as translate(cx cy) rotate(-rot) about the pad centre. The axis-aligned box of a "
        "rotated pad is the rotated inner rectangle grown by the corner radius; every pad here reproduces "
        "its exported box under that rule, and the rotation sign is confirmed against the non-orthogonal "
        "connectors J12 and J13.")
    provenance["custom_shape_pads"] = custom_pads
    provenance["thermal_via_pads"] = thermal
    provenance["overhang"] = sorted(
        c["ref"] for c in components
        if c["bbox"][0] < outline[0] or c["bbox"][1] < outline[1]
        or c["bbox"][0] + c["bbox"][2] > outline[0] + outline[2]
        or c["bbox"][1] + c["bbox"][3] > outline[1] + outline[3])
    provenance["notes"] = [
        "Layer plots keep their geometry exactly: only the XML prolog, title, description, invisible text and "
        "one empty group are removed, and colours are replaced with currentColor so the page can theme them.",
        "Datasheet and sourcing links are reproduced as recorded in the BOM CSV on 2026-09-06. They were not "
        "re-checked when this page was built.",
        "Historical simulations keep their own board hashes and are never relabelled as current.",
    ]
    prov = header()
    prov.update(provenance)
    write_json(ASSETS / "provenance.json", prov)

    scan(verbose=True)
    render()
    print("build complete: %s" % ASSETS)


# --------------------------------------------------------------------------- scanner
def scan(verbose=False):
    problems = []
    checked = 0
    for path in sorted(ASSETS.rglob("*")):
        if not path.is_file():
            continue
        checked += 1
        data = path.read_bytes()
        blobs = [(path.name, data)]
        if path.suffix == ".zip":
            with zipfile.ZipFile(path) as zf:
                for name in zf.namelist():
                    blobs.append(("%s!%s" % (path.name, name), zf.read(name)))
        for name, blob in blobs:
            text = blob.decode("latin-1")
            for pattern, what in FORBIDDEN_EVERYWHERE + FORBIDDEN_IN_ASSETS:
                if re.search(pattern, text):
                    problems.append("%s contains %s (/%s/)" % (name, what, pattern))
    page = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""
    for pattern, what in FORBIDDEN_EVERYWHERE:
        if re.search(pattern, page):
            problems.append("the chapter contains %s (/%s/)" % (what, pattern))
    if problems:
        for p in problems:
            print("FORBIDDEN: %s" % p, file=sys.stderr)
        sys.exit("scanner found %d problem(s)" % len(problems))
    if verbose:
        print("scanner clean across %d published files (and every archive member)" % checked)
    return checked


# --------------------------------------------------------------------------- render
def _table(headers, rows, cls="el-pcb-table", extra=""):
    out = ['<div class="el-pcb-scroll">', '<table class="%s"%s>' % (cls, extra), "<thead><tr>"]
    out.append("".join("<th>%s</th>" % h for h in headers))
    out.append("</tr></thead>")
    out.append("<tbody>")
    for row in rows:
        attrs = ""
        if isinstance(row, tuple):
            row, attrs = row
        out.append("<tr%s>%s</tr>" % (attrs, "".join("<td>%s</td>" % c for c in row)))
    out.append("</tbody></table></div>")
    return "\n".join(out)


def _ref(ref):
    return '<span class="el-pcb-ref" data-pcb-ref="%s">%s</span>' % (esc(ref), esc(ref))


def blocks():
    board = read_json(ASSETS / "board.json")
    bom = read_json(ASSETS / "bom.json")
    teach = read_json(ASSETS / "teaching.json")
    index = read_json(ASSETS / "schematic/index.json")
    manifest = read_json(ASSETS / "downloads/manifest.json")
    comp = {c["ref"]: c for c in board["components"]}
    out = {}

    # connectors
    rows = []
    for ref in sorted(teaching.CONNECTORS, key=ref_key):
        c = comp[ref]
        face, direction, function, mating = teaching.CONNECTORS[ref]
        if ref == "J14":
            contacts = ("A1, A12, B1, B12 and the shell = GND; A4, A9, B4, B9 = USB_VBUS; A5 = USB_CC1; "
                        "B5 = USB_CC2; A6, B6 = USB_DP_HOST; A7, B7 = USB_DM_HOST; A8, B8 unused")
        else:
            contacts = ", ".join("%s = %s" % (k, v) for k, v in
                                 sorted(c["pins"].items(), key=lambda kv: int(kv[0])))
        rows.append(([_ref(ref), esc(function), esc(face), esc(direction), esc(contacts), esc(mating)],
                     ' data-pcb-row="%s"' % ref))
    out["connectors"] = _table(
        ["Port", "What plugs in", "Face", "How it mates", "Contacts in numeric order", "Mating hardware"], rows)

    # channel map
    rows = []
    for n in range(1, 22):
        dev, led, pin = teaching.CHANNELS[n]
        z = teaching.zone_of(n)
        cname, cletter = teaching.colour_of(n)
        conn = teaching.ZONE_CONN[z]
        contact = (n - 1) % 3 + 2
        mark = " (remapped)" if n in teaching.REMAPPED else ""
        rows.append([str(n), "Zone %d %s" % (z, cname), "%s output %d%s" % (dev, led, mark), str(pin),
                     _ref("R1%02d" % n), _ref("Q1%02d" % n),
                     "%s contact %d" % (_ref(conn), contact), _ref(teaching.ZONE_FUSE[z])])
    out["channels"] = _table(
        ["Logical channel", "Zone and colour", "Expander output", "Package pin", "Gate resistor",
         "Switch", "Leaves at", "Fused by"], rows)

    # BOM
    rows = []
    for r in bom["rows"]:
        refs = " ".join(_ref(x) for x in r["refs"])
        note = esc(r["note"])
        for upd in bom["note_updates"]:
            if set(upd["refs"]) & set(r["refs"]):
                note += ' <span class="el-pcb-note-update">Update: %s</span>' % esc(upd["text"])
        link = ('<a href="%s">datasheet</a>' % esc(r["source"])) if r["source"] else ""
        rows.append(([str(r["item"]), refs, str(r["qty"]), str(r["qty2"]), esc(r["value"]),
                      esc(r["mpn"]), esc(r["pkg"] or r["fp"]), note, link],
                     ' data-item="%d"' % r["item"]))
    out["bom"] = _table(
        ["Row", "References", "Per board", "For two boards", "Value / description", "Part number",
         "Package", "Notes", "Source"], rows)

    rows = [[_ref(f["ref"]), esc(comp[f["ref"]]["pkg"]), esc(f["why_not_purchased"])]
            for f in bom["features"]]
    out["features"] = _table(["Feature", "What it is", "Why it is not in the parts list"], rows)

    # parts index by family
    parts = ['<div class="el-pcb-index">']
    order = sorted(teach["families"], key=lambda f: (teaching.FAMILIES.get(f, ("", ""))[0] or f))
    for fam in order:
        info = teach["families"][fam]
        refs = info["refs"]
        parts.append("<details>")
        parts.append("<summary>%s <span class=\"el-pcb-count\">%d</span></summary>" %
                     (esc(info["label"] or fam), len(refs)))
        rows = []
        for ref in refs:
            c = comp[ref]
            e = teach["components"][ref]
            rows.append([_ref(ref), esc(e["name"]),
                         esc(c["value"] or ""), esc(c["mpn"] or ""),
                         "front" if c["side"] == "F" else "back",
                         "%d" % c["sheet"],
                         ("row %d" % c["bom"]) if c["bom"] else "PCB feature"])
        parts.append(_table(["Reference", "What it is", "Value", "Part number", "Face", "Sheet", "Parts list"],
                            rows))
        parts.append("</details>")
    parts.append("</div>")
    out["parts-index"] = "\n".join(parts)

    # schematic sheets
    rows = []
    for s in index["sheets"]:
        rows.append([str(s["n"]), esc(s["title"]),
                     "%d" % len(s["refs"]),
                     '<a href="../assets/pcb/light-v0.1/%s">open the drawing</a>' % s["file"],
                     '<a href="../assets/pcb/light-v0.1/kicad/%s">%s</a>' % (esc(s["native"]), esc(s["native"])),
                     esc(s["plain"])])
    out["sheets"] = _table(["Sheet", "Title", "Parts", "View", "Native file", "What is on it"], rows)

    # downloads
    rows = []
    for it in manifest["items"]:
        note = esc(it["note"])
        if it.get("predates_scope"):
            note += (' <span class="el-pcb-note-update">This document was written before the 7 September 2026 '
                     'quote scope and describes two assembled prototypes.</span>')
        view = ""
        if it["view"] == "viewer":
            view = '<a href="#the-board">open in the board viewer</a>'
        elif it["view"] == "schematic":
            view = '<a href="#schematic">open in the sheet browser</a>'
        elif it["view"] == "bom":
            view = '<a href="#bom">read the table above</a>'
        elif it["view"] == "assembly":
            view = '<a href="#assembly-references">see the drawings below</a>'
        elif it["view"] == "fabrication":
            view = '<a href="#fabrication">see the advanced section</a>'
        rows.append([esc(it["label"]), esc(it["format"]), SHORT, human_bytes(it["bytes"]),
                     '<code>%s</code>' % it["sha256"][:12], view,
                     '<a href="../assets/pcb/light-v0.1/%s">download</a>' % it["file"], note])
    out["downloads"] = _table(
        ["File", "Format", "Revision", "Size", "SHA-256 (first 12)", "View in browser", "Download", "Notes"],
        rows)

    # validation
    rows = [[esc(a), esc(b), esc(c)] for a, b, c in VALIDATION_PASSED]
    out["validation-passed"] = _table(["Check", "Result on this revision", "What ran it"], rows)
    out["validation-open"] = ("<ul class=\"el-pcb-open\">\n" +
                              "\n".join("<li>%s</li>" % esc(x) for x in VALIDATION_NOT_DONE) +
                              "\n</ul>")
    return out


def render(check_only=False):
    if not PAGE.exists():
        print("chapter not written yet; skipping block render")
        return True
    page = PAGE.read_text(encoding="utf-8")
    generated = blocks()
    updated = page
    for name, body in sorted(generated.items()):
        start, end = MARK % (name, "start"), MARK % (name, "end")
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
        if not pattern.search(updated):
            sys.exit("chapter is missing the %s block markers" % name)
        updated = pattern.sub(lambda _m, s=start, b=body, e=end: "%s\n\n%s\n\n%s" % (s, b, e), updated)
    if check_only:
        if updated != page:
            sys.exit("generated blocks in the chapter are out of date -- run: "
                     "python tools/pcb/build_pcb_assets.py render")
        print("generated page blocks match the published data")
        return True
    if updated != page:
        write_text(PAGE, updated)
        print("chapter blocks regenerated (%d)" % len(generated))
    else:
        print("chapter blocks already up to date (%d)" % len(generated))
    return True


# --------------------------------------------------------------------------- check
def check():
    if not (ASSETS / "board.json").exists():
        sys.exit("no published assets -- run build first")
    board = read_json(ASSETS / "board.json")
    bom = read_json(ASSETS / "bom.json")
    teach = read_json(ASSETS / "teaching.json")
    index = read_json(ASSETS / "schematic/index.json")
    manifest = read_json(ASSETS / "downloads/manifest.json")
    prov = read_json(ASSETS / "provenance.json")

    for name, obj in (("board", board), ("bom", bom), ("teaching", teach), ("schematic index", index),
                      ("manifest", manifest), ("provenance", prov)):
        if obj.get("pcb_sha256") != PCB_SHA:
            sys.exit("%s does not carry the governing hash" % name)

    pcb = ASSETS / "kicad/engineered-lighting-rev-a.kicad_pcb"
    if sha256(pcb) != PCB_SHA:
        sys.exit("the published .kicad_pcb no longer hashes to the governing revision "
                 "(line-ending normalisation is the usual cause -- check docs/assets/pcb/.gitattributes)")
    zpath = ASSETS / "downloads/LIGHT-v0.1-c046202e-KiCad-project.zip"
    if sha256(zpath) != ZIP_SHA:
        sys.exit("the published project ZIP has changed")
    csv_path = ASSETS / bom["csv_file"]
    if sha256(csv_path) != CSV_SHA:
        sys.exit("the published BOM CSV has changed")
    if csv_path.read_bytes()[:3] != b"\xef\xbb\xbf":
        sys.exit("the published BOM CSV lost its byte-order mark")

    for it in manifest["items"]:
        p = ASSETS / it["file"]
        if not p.exists():
            sys.exit("manifest lists a missing file: %s" % it["file"])
        if p.stat().st_size != it["bytes"] or sha256(p) != it["sha256"]:
            sys.exit("manifest entry does not match the file on disk: %s" % it["file"])
    for layer in board["layers"]:
        p = ASSETS / layer["file"]
        if not p.exists() or sha256(p) != layer["sha256"]:
            sys.exit("layer file missing or changed: %s" % layer["file"])
    for s in index["sheets"]:
        p = ASSETS / s["file"]
        if not p.exists() or sha256(p) != s["sha256"]:
            sys.exit("schematic sheet missing or changed: %s" % s["file"])
    if list(ASSETS.rglob("*.kicad_prl")):
        sys.exit("a .kicad_prl was published")

    census = prov["census"]
    if len(board["components"]) != 269 or census["components"] != 269:
        sys.exit("component census is not 269")
    if sum(bom["totals"][k] for k in ("per_board",)) != 248 or bom["totals"]["rows"] != 74:
        sys.exit("BOM totals drifted")
    if len(teach["components"]) != 269:
        sys.exit("teaching content does not cover all 269 references")
    for ref, e in teach["components"].items():
        for c in e["claims"]:
            if c["evidence"] == "measured":
                sys.exit("%s carries a 'measured' claim" % ref)
    if sorted(prov["through_features"]) != ["H1", "H2", "H3", "H4", "J14"]:
        sys.exit("through-feature set drifted")

    scan()
    render(check_only=True)
    print("check passed: hashes, counts, manifest, scanner and generated blocks all agree")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", choices=("build", "render", "check"))
    ap.add_argument("--handoff", help="path to the handoff folder (build only)")
    args = ap.parse_args()
    if args.mode == "build":
        if not args.handoff:
            sys.exit("build needs --handoff")
        build(args.handoff)
    elif args.mode == "render":
        render()
    else:
        check()


if __name__ == "__main__":
    main()
