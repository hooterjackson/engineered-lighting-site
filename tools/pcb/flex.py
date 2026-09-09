"""Build the published assets for Doc 10, the upper v0.3 and unchanged lower/arm v0.2 circuits.

The flex review package has the same shape as the main board's: per-design
KiCad sources, CAM renderings of each manufacturing layer, a connection table,
design intent and verification records. The CAM renderings are the useful ones
here -- they carry no drawing sheet, they share one frame per design, and their
own group transform is undone so every layer lands in native KiCad millimetres,
the same convention the board viewer already uses.

Read-only against the review folder. Nothing under it is written.
"""

import csv
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

import svgprep

# design id -> (title, short name, what it is, how many copper layers)
DESIGNS = [
    ("gimbal-static-v0.2", "Arm ribbon", "gimbal",
     "Carries motor power, the CAN pair and three spotlight pairs along the arm. "
     "Static: it does not flex in service, and ordinary wires cross the moving joints.", 1),
    ("led-upper-v0.3", "Upper cylinder band", "upper",
     "Connects main J2 directly through a 30-contact insertion tail to six separately fused zones; 96 lands solder to strip ends.", 2),
    ("led-lower-v0.2", "Lower cylinder band", "lower",
     "The mirrored lower band, feeding the same six zones from the other side.", 2),
]

LAYER_LABELS = {
    "F_Cu": ("Front copper", "the conductors on the front face"),
    "B_Cu": ("Back copper", "the conductors on the back face"),
    "F_Mask": ("Front coverlay openings", "where the insulating film is left open so copper is exposed"),
    "B_Mask": ("Back coverlay openings", "where the insulating film is left open so copper is exposed"),
    "F_Silkscreen": ("Front legend", "printed labels, not conductors"),
    "Edge_Cuts": ("Outline", "the profile the circuit is cut to"),
}
LAYER_ORDER = ["Edge_Cuts", "B_Cu", "F_Cu", "B_Mask", "F_Mask", "F_Silkscreen"]

RE_TRANSFORM = re.compile(
    r'transform="translate\(([-\d.]+) ([-\d.]+)\) scale\(1 -1\) translate\(([-\d.]+) ([-\d.]+)\)"')

# Files that must never be published: the fabrication reviews carry the vendor
# correspondence id, and the netlists carry a machine path.
NEVER_PUBLISH = ("FABRICATION-REVIEW.txt", "netlist.xml")


def _sha(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _frame(cam_path):
    """(viewBox in native mm, the y shift that gets us there)."""
    text = cam_path.read_text(encoding="utf-8")
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', text).group(1).split()]
    m = RE_TRANSFORM.search(text)
    if not m:
        sys.exit("%s does not carry the expected CAM transform" % cam_path.name)
    a, b, c, d = (float(m.group(i)) for i in (1, 2, 3, 4))
    if abs(a + c) > 1e-9:
        sys.exit("%s has an unexpected x offset" % cam_path.name)
    shift = d - b
    # the CAM frame is y-up; in native millimetres it becomes y-down
    native = [vb[0], vb[1] + shift, vb[2], vb[3]]
    return native, shift


def build(review, assets, write_json, write_text, write_bytes, header):
    """Derive docs/assets/pcb/flex-v0.2/** from the review folder."""
    review = Path(review)
    if not review.is_dir():
        sys.exit("flex review folder not found: %s" % review)
    if assets.exists():
        shutil.rmtree(assets)
    assets.mkdir(parents=True)

    summary = json.loads((review / "verification-summary.json").read_text(encoding="utf-8"))
    electrical = json.loads((review / "electrical-analysis.json").read_text(encoding="utf-8"))
    mechanical = json.loads((review / "mechanical-analysis.json").read_text(encoding="utf-8"))
    if summary.get("status") != "PASS":
        sys.exit("the flex review does not report PASS")

    boards = []
    provenance = {"designs": {}, "excluded": list(NEVER_PUBLISH)}

    for design, title, short, what, copper in DESIGNS:
        src = review / design
        if not src.is_dir():
            sys.exit("missing design folder: %s" % design)
        intent = json.loads((src / "design-intent.json").read_text(encoding="utf-8"))
        verify = json.loads((src / "verification.json").read_text(encoding="utf-8"))
        pcb_sha = verify["pcb_sha256"]
        if _sha(src / ("%s.kicad_pcb" % design)) != pcb_sha:
            sys.exit("%s: the board file does not match its recorded hash" % design)

        out = assets / short
        (out / "layers").mkdir(parents=True, exist_ok=True)

        cam = sorted((src / "view").glob("*-CAM.svg"))
        frame, shift = _frame(cam[0])
        layers = []
        for path in cam:
            lid = path.name[len(design) + 1:-len("-CAM.svg")]
            if lid not in LAYER_LABELS:
                continue
            this_frame, this_shift = _frame(path)
            if abs(this_shift - shift) > 1e-9:
                sys.exit("%s: %s does not share the design's frame" % (design, lid))
            text = path.read_text(encoding="utf-8")
            svg, stats = svgprep.prepare(
                text, recolour=True,
                wrap_transform="translate(0 %g)" % shift,
                view_box=" ".join("%g" % v for v in frame),
                extra_attrs={"data-layer": lid})
            svgprep.verify(text, svg, added_groups=1)
            if stats["hex_colors_after"]:
                sys.exit("%s: %s kept baked colours" % (design, lid))
            dest = out / "layers" / ("%s.svg" % lid)
            write_text(dest, svg)
            label, plain = LAYER_LABELS[lid]
            layers.append({
                "id": lid, "file": "%s/layers/%s.svg" % (short, lid),
                "label": label, "plain": plain,
                "z": LAYER_ORDER.index(lid),
                "bytes": dest.stat().st_size, "sha256": _sha(dest),
            })
        layers.sort(key=lambda l: l["z"])

        pads = _pads(src / "connection-table.csv", design)
        native = _native_sources(src, out, design, write_bytes)
        fab = _fabrication_zip(src, out, design, short, pcb_sha, write_bytes)

        boards.append({
            "id": short, "design": design, "title": title, "what": what,
            "pcb_sha256": pcb_sha, "copper_layers": copper,
            "size_mm": _size(intent, frame),
            "frame": {"viewBox": frame},
            "layers": layers, "pads": pads,
            "checks": {
                "erc": verify["ERC_violations"], "drc": verify["DRC_violations"],
                "unconnected": verify["unconnected_items"],
                "parity": verify["schematic_parity_issues"],
                "pin_oracle": verify["independent_pin_oracle"],
                "pads": verify["pads"], "cam_pad_flashes": verify["CAM_pad_flashes"],
                "cam_tracks": verify["CAM_native_tracks"], "cam_drills": verify["CAM_drills"],
                "outline_gap_mm": verify["CAM_outline_max_endpoint_gap_mm"],
            },
            "intent": _intent(intent, design),
            "files": native, "fabrication": fab,
        })
        provenance["designs"][short] = {
            "design": design, "pcb_sha256": pcb_sha,
            "layers": {l["id"]: l["sha256"] for l in layers},
            "pads": len(pads), "frame": frame, "y_shift_applied": shift,
        }

    index = header()
    index.update({
        "revision": "Upper v0.3; lower and gimbal v0.2",
        "status": ("Three routed passive circuits. Native ERC, DRC, schematic parity, an independent pin "
                   "oracle and CAM comparisons pass within their recorded scope. The boards have not been "
                   "physically qualified. All three were submitted to JLCPCB for engineering quotation and now have PCBWay inquiries. Supplier stack, copper, contact finish and stiffener requirements remain under review. No payment or production release."),
        "boards": boards,
        "totals": {
            "designs": 3,
            "pads": sum(len(b["pads"]) for b in boards),
            "installed_rail_components": summary["installed_rail_components"],
            "strip_end_pads": 192,
        },
        "electrical": _electrical(electrical),
        "mechanical": {
            "neutral_radius_mm": mechanical["neutral_radius_mm"],
            "developed_length_mm": mechanical["developed_length_mm"],
            "strip_pitch_mm": mechanical["24_strip_pitch_mm"],
            "adhesive_nominal_mm": mechanical["adhesive_thickness_nominal_mm"],
            "adhesive_tolerance_mm": mechanical["adhesive_datasheet_typical_tolerance_mm"],
            "worst_alignment_shift_mm": mechanical["max_circumferential_alignment_shift_adhesive_only_half_turn_mm"],
            "lateral_margin_mm": mechanical["pad_to_strip_nominal_lateral_margin_each_mm"],
            "axial_overlap_mm": mechanical["nominal_axial_copper_overlap_mm"],
            "exposed_toe_mm": mechanical["remaining_exposed_strip_toe_mm"],
            "why": mechanical["reason"],
        },
    })
    write_json(assets / "index.json", index)
    prov = header()
    prov.update(provenance)
    write_json(assets / "provenance.json", prov)

    # Shared references. The engineering notes are Markdown, and anything ending
    # .md under docs/ becomes a page MkDocs renders and awesome-pages appends to
    # the nav after the last chapter. Published with a .txt extension the bytes
    # are copied verbatim instead, so the file downloads and its hash still
    # matches the review folder's original.
    for name, published in (("fit-templates-A3.pdf", "fit-templates-A3.pdf"),
                            ("ENGINEERING-NOTES.md", "ENGINEERING-NOTES.txt"),
                            ("tail-resistance-screen.json", "tail-resistance-screen.json")):
        shutil.copyfile(review / name, assets / published)
    index["shared_files"] = [
        {"file": name, "sha256": _sha(assets / name), "bytes": (assets / name).stat().st_size}
        for name in ("fit-templates-A3.pdf", "ENGINEERING-NOTES.txt", "tail-resistance-screen.json")
    ]
    write_json(assets / "index.json", index)
    return index


def _size(intent, frame):
    if "length_mm" in intent:
        return [intent["length_mm"], intent.get("overall_y_mm", intent.get("width_mm", frame[3]))]
    return [round(frame[2], 3), round(frame[3], 3)]


def _intent(intent, design):
    """The facts worth teaching, per design."""
    out = {
        "status": intent.get("status", ""),
        "copper_layers": intent.get("physical_copper_layers"),
        "finished_thickness_mm": intent.get("finished_flex_thickness_target_mm", intent.get("finished_flex_target_mm")),
        "copper_um": intent.get("nominal_copper_um"),
    }
    for key in ("empty_editor_layer", "cut_lengths_mm", "retained_input_reference",
                "pad_length_mm", "edge_margin_mm", "lane_gap_mm"):
        if key in intent:
            out[key] = intent[key]
    if "lanes" in intent:
        out["lanes"] = intent["lanes"]
    if "termination_banks" in intent:
        out["termination_banks"] = [
            {"reference": b[0], "start_mm": b[1], "cut_at_mm": b[2]} for b in intent["termination_banks"]]
    return out


def _pads(table, design):
    """Pad positions in native millimetres, with whatever the design calls them."""
    rows = list(csv.DictReader(open(table, encoding="utf-8-sig")))
    pads = []
    for r in rows:
        x = r.get("X_native_mm") or r.get("native_x_mm")
        y = r.get("Y_native_mm") or r.get("native_y_mm")
        if x is None or y is None:
            sys.exit("%s: connection table has no native coordinates" % design)
        pads.append({
            "ref": r["reference"], "pin": r["pin"],
            "net": (r.get("net") or "").strip(),
            "rail": (r.get("rail") or "").strip(),
            "role": (r.get("role") or "").strip(),
            "copper_layer": "B_Cu" if r["reference"] == "J100" else "F_Cu",
            "xy": [round(float(x), 4), round(float(y), 4)],
        })
    return pads


def _electrical(analysis):
    cases = []
    for case in analysis["cases"]:
        row = {"name": case.get("case") or case.get("name") or "case"}
        for key, value in case.items():
            if key in ("case", "name"):
                continue
            if isinstance(value, (int, float)):
                row[key] = value
        cases.append(row)
    return {"cases": cases, "assumptions": analysis["assumptions"]}


def _native_sources(src, out, design, write_bytes):
    """Publish the editable sources: board, schematic, project, footprints."""
    files = []
    (out / "kicad").mkdir(parents=True, exist_ok=True)
    for name in ("%s.kicad_pcb" % design, "%s.kicad_sch" % design, "%s.kicad_pro" % design,
                 "fp-lib-table"):
        path = src / name
        if not path.exists():
            continue
        write_bytes(out / "kicad" / name, path.read_bytes())
        files.append({"file": "kicad/%s" % name, "bytes": path.stat().st_size,
                      "sha256": _sha(out / "kicad" / name)})
    for name in ("connection-table.csv", "stiffener-regions.csv", "design-intent.json",
                 "verification.json", "construction.svg", "overview.svg", "insertion-drawing.svg",
                 "template-1-to-1.svg", "J100-pin-map.csv"):
        path = src / name
        if not path.exists():
            path = src / "view" / name
        if not path.exists():
            continue
        write_bytes(out / name, path.read_bytes())
        files.append({"file": name, "bytes": path.stat().st_size, "sha256": _sha(out / name)})
    if design == "led-upper-v0.3":
        # The new insertion footprint is local to this project; the native board
        # embeds geometry, but editing needs its library too.
        for path in sorted((src / "ELFlex.pretty").glob("*.kicad_mod")):
            rel = "kicad/ELFlex.pretty/" + path.name
            write_bytes(out / rel, path.read_bytes())
            files.append({"file": rel, "bytes": path.stat().st_size, "sha256": _sha(path)})
        dest = out / "FLEX-v0.3-upper-KiCad-project.zip"
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted((out / "kicad").rglob("*")):
                if not path.is_file():
                    continue
                info = zipfile.ZipInfo(path.relative_to(out / "kicad").as_posix(), (1980,1,1,0,0,0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                archive.writestr(info, path.read_bytes())
        files.append({"file": dest.name, "bytes": dest.stat().st_size, "sha256": _sha(dest)})
    return files


def _fabrication_zip(src, out, design, short, pcb_sha, write_bytes):
    """One deterministic archive of the manufacturing outputs, minus the
    fabrication review, which carries vendor correspondence."""
    members = []
    fab = src / "fabrication"
    if fab.is_dir():
        for path in sorted(fab.iterdir()):
            if path.is_file() and path.name not in NEVER_PUBLISH:
                members.append((path.name, path.read_bytes()))
    if not members:
        return None
    readme = (
        "Engineered Lighting FLEX v0.2 / %s\n"
        "Board SHA-256: %s\n\n"
        "Manufacturing outputs generated from the design published beside them: Gerber artwork,\n"
        "drill data where the design has holes, and the drill maps. F.Mask and B.Mask designate\n"
        "COVERLAY OPENINGS on a flex circuit, not liquid solder mask.\n\n"
        "This is a reference for reading the circuit, not a fabrication release. Nothing here has\n"
        "been ordered, and no price, quantity or vendor correspondence is included.\n" % (design, pcb_sha)
    )
    if short == "upper":
        readme = readme.replace("FLEX v0.2", "Upper flex v0.3")
    members.append(("README.txt", readme.encode("utf-8")))
    dest = out / ("FLEX-%s-%s-fabrication.zip" % ("v0.3" if short == "upper" else "v0.2", short))
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in sorted(members):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, data)
    return {"file": "%s/FLEX-%s-%s-fabrication.zip" % (short, "v0.3" if short == "upper" else "v0.2", short),
            "bytes": dest.stat().st_size, "sha256": _sha(dest)}
