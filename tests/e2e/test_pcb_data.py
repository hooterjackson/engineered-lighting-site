"""Data and asset checks for Doc 9's published PCB material.

These run without a browser. They guard the things `mkdocs build --strict`
cannot see: the hash chain from the governing board file through to every
published byte, the counts the page states as fact, the joins between the
board, the parts list, the teaching content and the schematic, and the raw
HTML links the Markdown validator ignores.

They live in tests/e2e so the repo's single test command picks them up.
"""

import json
import math
import pathlib
import re
import subprocess
import sys
import zipfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
ASSETS = REPO / "docs" / "assets" / "pcb" / "light-v0.1"
PAGE = REPO / "docs" / "09-understand-the-pcb.md"
SITE = REPO / "site"

PCB_SHA = "c046202efa3896d59d12bf19f55ed48b3a6c77532aac199a3a1e9a993e449310"
ZIP_SHA = "029f02282a4500ad541a31513062dc8ef4b7426aef1c0547d51f07ee4b459d8d"
CSV_SHA = "d9308529a10ce194e19765466474dc2ceda12c8e35fa6eeddf06806462911756"

LANDMARKS = {
    "J1": ("F", [84.5, 126.5], -90.0, 16),
    "U1": ("F", [100.0, 72.6], 0.0, 2),
    "J14": ("F", [100.0, 134.425], 0.0, 5),
    "C504": ("B", [100.0, 114.0], 0.0, 15),
    "J12": ("B", [88.5, 130.0], 160.0, 4),
    "J13": ("B", [113.0, 129.5], -160.0, 4),
    "H1": ("F", [83.0, 70.5], 0.0, 19),
    "H2": ("F", [117.0, 70.5], 0.0, 19),
    "H3": ("F", [76.0, 124.0], 0.0, 19),
    "H4": ("F", [124.0, 124.0], 0.0, 19),
    "C512": ("B", [None, None], None, 16),
}

TP_NETS = {
    "TP1": "GND", "TP2": "VIN24_RAW", "TP3": "V24_BUS", "TP4": "+5V", "TP5": "+3V3",
    "TP6": "GATE_BIAS", "TP7": "LIGHT_ENABLE_SAFE", "TP8": "EFUSE_RESET_N",
    "TP9": "V24_SPOT", "TP10": "I2C_SDA", "TP11": "I2C_SCL", "TP12": "PCA_OE",
}


def load(name):
    with open(ASSETS / name, "rb") as fh:
        return json.loads(fh.read().decode("utf-8"))


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def board():
    return load("board.json")


@pytest.fixture(scope="module")
def bom():
    return load("bom.json")


@pytest.fixture(scope="module")
def teach():
    return load("teaching.json")


@pytest.fixture(scope="module")
def sch():
    return load("schematic/index.json")


def test_generator_check_passes():
    """The build tool's own drift check, which CI can run without the handoff."""
    result = subprocess.run(
        [sys.executable, str(REPO / "tools" / "pcb" / "build_pcb_assets.py"), "check"],
        capture_output=True, text=True, cwd=str(REPO))
    assert result.returncode == 0, result.stdout + result.stderr


def test_hash_chain(bom):
    assert sha256(ASSETS / "kicad/engineered-lighting-rev-a.kicad_pcb") == PCB_SHA, (
        "the published board file no longer hashes to the governing revision - if this fails after a "
        "fresh clone, docs/assets/pcb/.gitattributes is missing or wrong")
    zpath = ASSETS / "downloads/LIGHT-v0.1-c046202e-KiCad-project.zip"
    assert sha256(zpath) == ZIP_SHA
    csv = ASSETS / bom["csv_file"]
    assert sha256(csv) == CSV_SHA
    assert csv.read_bytes()[:3] == b"\xef\xbb\xbf", "the parts CSV lost its byte-order mark"
    for name in ("board.json", "bom.json", "teaching.json", "provenance.json",
                 "schematic/index.json", "downloads/manifest.json"):
        assert load(name)["pcb_sha256"] == PCB_SHA, name
    assert not list(ASSETS.rglob("*.kicad_prl")), "personal editor state must never be published"


def test_project_zip_contents():
    zpath = ASSETS / "downloads/LIGHT-v0.1-c046202e-KiCad-project.zip"
    with zipfile.ZipFile(zpath) as zf:
        names = zf.namelist()
    assert len(names) == 62, names
    assert sum(1 for n in names if n.endswith(".kicad_sch")) == 19
    assert sum(1 for n in names if n.endswith(".kicad_sym")) == 15
    for required in ("engineered-lighting-rev-a.kicad_pro", "engineered-lighting-rev-a.kicad_pcb",
                     "engineered-lighting-rev-a.kicad_dru", "fp-lib-table", "sym-lib-table",
                     "SOURCE-MANIFEST.json"):
        assert required in names, required
    assert any(n.startswith("EL.pretty/") for n in names)
    assert any(n.startswith("ELF.pretty/") for n in names)
    assert not any(n.endswith(".kicad_prl") for n in names)


def test_manifest_and_layers_resolve(board, sch):
    manifest = load("downloads/manifest.json")
    for item in manifest["items"]:
        path = ASSETS / item["file"]
        assert path.exists(), item["file"]
        assert path.stat().st_size == item["bytes"], item["file"]
        assert sha256(path) == item["sha256"], item["file"]
    assert len(board["layers"]) == 17
    for layer in board["layers"]:
        path = ASSETS / layer["file"]
        assert path.exists() and sha256(path) == layer["sha256"], layer["id"]
    assert len(sch["sheets"]) == 19
    for sheet in sch["sheets"]:
        path = ASSETS / sheet["file"]
        assert path.exists() and sha256(path) == sheet["sha256"], sheet["n"]


def test_board_census(board):
    comps = {c["ref"]: c for c in board["components"]}
    assert len(comps) == 269
    assert board["sides"] == {"F": 127, "B": 142}
    assert sum(1 for c in comps.values() if c["side"] == "F") == 127
    assert len(board["features"]) == 21
    assert sum(1 for c in comps.values() if not c["feature"]) == 248
    assert len(board["nets"]) == 163
    assert not [n for n in board["nets"] if n.startswith("unconnected-")]
    nc = sum(1 for c in comps.values() for v in c["pins"].values() if v is None)
    assert nc == 29
    pads = [p for c in comps.values() for p in c["pads"]]
    assert len(pads) == 887
    assert sum(1 for p in pads if p.get("paste")) == 18

    assert sorted(r for r, c in comps.items() if c["through"]) == ["H1", "H2", "H3", "H4", "J14"]
    thermal = {r: c["thermal_vias"] for r, c in comps.items() if c["thermal_vias"]}
    assert thermal == {"U10": 8, "U11": 2, "U12": 9, "U14": 6, "U500": 2, "U501": 2}

    outline = board["frame"]["outline"]
    overhang = sorted(r for r, c in comps.items()
                      if c["bbox"][0] < outline[0] or c["bbox"][1] < outline[1]
                      or c["bbox"][0] + c["bbox"][2] > outline[0] + outline[2]
                      or c["bbox"][1] + c["bbox"][3] > outline[1] + outline[3])
    assert overhang == ["J14", "J17", "U1"]
    assert board["frame"]["fit"] == [61.225, 56.49, 77.55, 82.14]

    for ref, (side, xy, rot, sheet) in LANDMARKS.items():
        c = comps[ref]
        assert c["side"] == side, ref
        assert c["sheet"] == sheet, (ref, c["sheet"])
        if xy[0] is not None:
            assert c["xy"] == xy, ref
            assert c["rot"] == rot, ref
    for ref in ("H1", "H2", "H3", "H4"):
        pad = comps[ref]["pads"][0]
        assert pad["attr"] == 3 and pad["drill"] == [3.2, 3.2], ref
    assert all(c["pkg"] for c in comps.values())


def test_pad_geometry(board):
    """Every pad's drawn outline reproduces its exported box, and the rotation
    sign is the one that squares J12/J13's pad rows to their pad axes."""
    comps = {c["ref"]: c for c in board["components"]}
    for c in comps.values():
        for pad in c["pads"]:
            if pad["shape"] == 6:
                continue
            w, h = pad["size"]
            t = math.radians(pad["rot"])
            if pad["shape"] == 0:
                ew, eh = w, h
            else:
                if pad["shape"] == 2:
                    r = min(w, h) / 2
                elif pad["shape"] in (4, 5):
                    r = pad.get("r") or 0.0
                else:
                    r = 0.0
                iw, ih = max(w - 2 * r, 0.0), max(h - 2 * r, 0.0)
                ew = abs(iw * math.cos(t)) + abs(ih * math.sin(t)) + 2 * r
                eh = abs(iw * math.sin(t)) + abs(ih * math.cos(t)) + 2 * r
            assert abs(ew - pad["bbox"][2]) < 1e-3, (c["ref"], pad["n"])
            assert abs(eh - pad["bbox"][3]) < 1e-3, (c["ref"], pad["n"])

    for ref in ("J12", "J13"):
        pads = {p["n"]: p for p in comps[ref]["pads"]}
        p1, p3 = pads["1"]["xy"], pads["3"]["xy"]
        row = (p3[0] - p1[0], p3[1] - p1[1])
        length = math.hypot(*row)
        row = (row[0] / length, row[1] / length)
        good = math.radians(-comps[ref]["rot"])
        bad = math.radians(comps[ref]["rot"])
        good_axis = (-math.sin(good), math.cos(good))
        bad_axis = (-math.sin(bad), math.cos(bad))
        assert abs(good_axis[0] * row[0] + good_axis[1] * row[1]) < 0.02, ref
        assert abs(bad_axis[0] * row[0] + bad_axis[1] * row[1]) > 0.5, (
            ref + ": the oracle cannot tell the two rotation signs apart")


def test_layers_are_themeable_and_labelled(board):
    front = {c["ref"] for c in board["components"] if c["side"] == "F"}
    back = {c["ref"] for c in board["components"] if c["side"] == "B"}
    for layer in board["layers"]:
        text = (ASSETS / layer["file"]).read_text(encoding="utf-8")
        assert 'viewBox="0.0000 0.0000 297.0022 210.0072"' in text, layer["id"]
        assert not re.search(r"#[0-9A-Fa-f]{6}", text), layer["id"] + " still has baked colours"
        assert "<text" not in text, layer["id"] + " still has invisible text"
        tagged = set(re.findall(r'data-ref="([^"]+)"', text))
        if layer["id"] == "F_Fab":
            assert tagged == front
        elif layer["id"] == "B_Fab":
            assert tagged == back
        else:
            assert not tagged, layer["id"] + " should carry no reference labels"
    edge = (ASSETS / "layers/Edge_Cuts.svg").read_text(encoding="utf-8")
    assert "M90.9110 63.0000" in edge and "A38.1000 38.1000" in edge
    frame = board["frame"]
    assert frame["silhouette_path"].startswith("M90.9110 63.0000 A38.1000 38.1000")
    assert frame["silhouette_path"].endswith("Z")


def test_bom_join(board, bom, teach):
    comps = {c["ref"]: c for c in board["components"]}
    assert bom["totals"] == {"rows": 74, "per_board": 248, "two_boards": 496, "features": 21}
    assert len(bom["rows"]) == 74
    assert sum(r["qty"] for r in bom["rows"]) == 248
    assert [r["item"] for r in bom["rows"]] == list(range(1, 75))
    purchased = {r for r, c in comps.items() if not c["feature"]}
    assert set(bom["ref_to_item"]) == purchased
    for row in bom["rows"]:
        assert len(row["refs"]) == row["qty"]
        assert row["qty2"] == row["qty"] * 2
        for ref in row["refs"]:
            assert not comps[ref]["feature"], ref
            assert comps[ref]["bom"] == row["item"], ref
    variants = {}
    for row in bom["rows"]:
        variants.setdefault((row["mpn"], row["fp"]), []).append(row["item"])
    assert all(len(v) == 1 for v in variants.values()), "a part+footprint pair spans two rows"
    same_mpn = {}
    for row in bom["rows"]:
        same_mpn.setdefault(row["mpn"], []).append(row["item"])
    assert sorted(same_mpn["SM04B-GHS-TB(LF)(SN)"]) == [23, 26, 27]
    assert sorted(same_mpn["BM02B-GHS-TBT(LF)(SN)"]) == [72, 73, 74]

    updated = {ref for u in bom["note_updates"] for ref in u["refs"]}
    assert {"C3", "C512"} <= updated
    assert "C510" not in updated, "the capacitor screen covered C3 and C512 only"


def test_teaching_is_complete_and_honest(board, teach):
    comps = {c["ref"]: c for c in board["components"]}
    assert set(teach["components"]) == set(comps)
    families = teach["families"]
    seen = []
    for info in families.values():
        seen.extend(info["refs"])
    assert sorted(seen) == sorted(comps), "families must partition every reference exactly once"

    for ref, e in teach["components"].items():
        nets = {v for v in comps[ref]["pins"].values() if v}
        assert 0 < len(e["name"]) <= 80, ref
        assert len(e["here"]) >= 120, ref
        assert len(e["how"]) >= 120, ref
        assert e["circuit"] in teach["circuits"], ref
        if nets:
            assert any(n in e["here"] or n in e["how"] for n in nets), ref
        assert e["related"] and all(r in comps for r in e["related"]), ref
        assert ref not in e["related"], ref
        assert e["claims"] or e["open"], ref
        assert len(e["nets"]) == len(comps[ref]["pins"]), ref
        for claim in e["claims"]:
            assert claim["kind"] in teach["vocab"]["claim_kinds"], ref
            assert claim["evidence"] in teach["vocab"]["evidence"], ref
            assert claim["evidence"] != "measured", ref + " claims a measurement"
            assert claim["basis"], ref
            if claim["evidence"] == "simulated-historical":
                assert claim.get("bound_to") and claim.get("source_file"), ref
                assert claim["bound_to"] not in PCB_SHA, ref

    for ref in ("U1", "U12", "U14", "U17", "U10", "U11", "J14", "C504", "F1", "J1"):
        assert teach["components"][ref]["open"], ref + " should carry at least one open question"


def test_channel_map_matches_the_board(board, teach):
    """The 21-row channel map is only useful if it agrees with the actual nets."""
    comps = {c["ref"]: c for c in board["components"]}
    expander_pin = {}
    for dev in ("U2", "U3"):
        for pin, net in comps[dev]["pins"].items():
            if net and net.startswith("PWM_"):
                expander_pin[net] = (dev, int(pin))
    assert expander_pin["PWM_18"] == ("U3", 20), "the PWM 18 remap is wrong"
    assert expander_pin["PWM_20"] == ("U3", 19), "the PWM 20 remap is wrong"

    for n in range(1, 22):
        net = "PWM_%02d" % n
        assert comps["R1%02d" % n]["pins"]["1"] == net
        gate = comps["R1%02d" % n]["pins"]["2"]
        assert gate == "GATE_%02d" % n
        assert comps["Q1%02d" % n]["pins"]["1"] == gate
        assert comps["Q1%02d" % n]["pins"]["2"] == "GND"
        assert comps["R2%02d" % n]["pins"]["1"] == gate
        assert comps["R3%02d" % n]["pins"]["2"] == net
        zone = (n - 1) // 3 + 1
        colour = ["W", "N", "C"][(n - 1) % 3]
        assert comps["Q1%02d" % n]["pins"]["3"] == "ZONE%d_%s" % (zone, colour)
        group = teach["components"]["Q1%02d" % n]["group"]
        assert group["zone"] == zone and group["channel"] == n

    assert comps["U1"]["pins"]["25"] == "UART_TX"
    assert comps["U1"]["pins"]["24"] == "UART_RX"
    for tp, net in TP_NETS.items():
        assert comps[tp]["value"] == net, tp


def test_schematic_index(board, sch):
    comps = {c["ref"]: c for c in board["components"]}
    assert len(sch["ref_to_sheet"]) == 269
    assert set(sch["ref_to_sheet"]) == set(comps)
    assert set(sch["ref_to_sheet"].values()) <= set(range(2, 20))
    counts = {}
    for sheet in sch["sheets"]:
        counts[sheet["n"]] = len(sheet["refs"])
        assert sheet["pdf_page"] == sheet["n"]
        text = (ASSETS / sheet["file"]).read_text(encoding="utf-8")
        tagged = set(re.findall(r'data-ref="([^"]+)"', text))
        assert tagged == set(sheet["refs"]), sheet["n"]
        for ref in sheet["refs"]:
            assert comps[ref]["sheet"] == sheet["n"], ref
    assert counts[1] == 0
    assert sum(counts.values()) == 269


def test_nothing_private_is_published():
    """No machine paths, no vendor correspondence, no superseded assembly wording."""
    forbidden = [r"[A-Za-z]:[\\/]Users[\\/]", r"/Users/", r"Marcelo",
                 r"W1144574AS7C1", r"ParentId", r"website_quote_quantity", r"purchased_quantity"]
    assets_only = [r"assembles locally", r"iron-only"]
    for path in sorted(ASSETS.rglob("*")):
        if not path.is_file():
            continue
        blobs = [(path.name, path.read_bytes())]
        if path.suffix == ".zip":
            with zipfile.ZipFile(path) as zf:
                blobs.extend((path.name + "!" + n, zf.read(n)) for n in zf.namelist())
        for name, blob in blobs:
            text = blob.decode("latin-1")
            for pattern in forbidden + assets_only:
                assert not re.search(pattern, text), "%s matches /%s/" % (name, pattern)
    page = PAGE.read_text(encoding="utf-8")
    for pattern in forbidden:
        assert not re.search(pattern, page), pattern
    # The chapter must still be free to explain the iron-only distinction.
    assert "iron-only" in page


def test_generated_blocks_and_raw_links(board, bom, sch):
    page = PAGE.read_text(encoding="utf-8")
    for name in ("connectors", "channels", "bom", "features", "parts-index", "sheets",
                 "downloads", "validation-passed", "validation-open"):
        assert page.count("<!-- el-pcb:generated %s start -->" % name) == 1, name
        assert page.count("<!-- el-pcb:generated %s end -->" % name) == 1, name
    assert len(re.findall(r'data-item="\d+"', page)) == 74
    assert len(re.findall(r'data-pcb-row="', page)) == 18
    channel_block = page.split("<!-- el-pcb:generated channels start -->")[1] \
                        .split("<!-- el-pcb:generated channels end -->")[0]
    assert channel_block.count("<tr") == 22, "21 channel rows plus one header row"
    manifest = load("downloads/manifest.json")
    downloads_block = page.split("<!-- el-pcb:generated downloads start -->")[1] \
                          .split("<!-- el-pcb:generated downloads end -->")[0]
    assert downloads_block.count("<tr") == len(manifest["items"]) + 1

    docs = REPO / "docs"
    page_dir = docs / "09-understand-the-pcb"
    for attr in ("href", "src", "data-src", "data-base"):
        for value in re.findall(attr + r'="([^"#][^"]*)"', page):
            if value.startswith(("http", "#", "mailto:")):
                continue
            target = (page_dir / value).resolve()
            assert target.exists(), "%s=%s does not resolve to a published file" % (attr, value)

    boxes = len(re.findall(r"^- \[ \] ", page, re.M))
    assert boxes >= 8, "the bring-up checklist lost its items"


@pytest.mark.skipif(not (SITE / "09-understand-the-pcb" / "index.html").exists(),
                    reason="run mkdocs build first")
def test_built_page_and_footer():
    page = (SITE / "09-understand-the-pcb" / "index.html").read_text(encoding="utf-8")
    assert 'id="el-pcb"' in page and 'data-state="nojs"' in page
    assert 'id="el-sch"' in page
    doc8 = (SITE / "08-build-the-fixture" / "index.html").read_text(encoding="utf-8")
    nxt = re.search(r'md-footer__link--next.*?md-ellipsis">([^<]+)<', doc8, re.S)
    assert nxt and "Understand the PCB" in nxt.group(1)
    prev = re.search(r'md-footer__link--prev.*?md-ellipsis">([^<]+)<', page, re.S)
    assert prev and "Build the Fixture" in prev.group(1)
    assert "md-footer__link--next" not in page, "Doc 9 must be the last page"
