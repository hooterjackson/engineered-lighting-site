"""Data and browser checks for Doc 10, the three FLEX v0.2 circuits.

The thing that can silently go wrong here is registration: the published layer
renderings are rewritten out of their CAM frame into native millimetres so the
connection table's pad coordinates can be drawn on top of them. If that
transform drifts, the pads sit somewhere plausible but wrong, so these tests
check the pads land on the copper rather than merely that something rendered.
"""

import json
import pathlib
import re
import zipfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
ASSETS = REPO / "docs" / "assets" / "pcb" / "flex-v0.2"
PAGE_FILE = REPO / "docs" / "10-the-flex-circuits.md"
PAGE = "/10-the-flex-circuits/"
READY = '#el-flex[data-state="ready"]'

BOARD_SHA = {
    "gimbal": "7136c5c343da3194c0ada81330edd99336b3078152bb8f1ce47f5da158f2287d",
    "upper": "0af25f8f72fb999db1bad16a8d59541a02c4eb95f838ada6dd6abadba8fe058d",
    "lower": "21db9dba94c6b4fd992e7c361f79d360b84270ea8c3a89099156e5972f7d6379",
}
PAD_COUNT = {"gimbal": 70, "upper": 126, "lower": 96}


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def index():
    with open(ASSETS / "index.json", "rb") as fh:
        return json.loads(fh.read().decode("utf-8"))


def test_three_designs_with_their_own_hashes(index):
    assert len(index["boards"]) == 3
    assert index["totals"]["pads"] == 292
    for board in index["boards"]:
        assert board["pcb_sha256"] == BOARD_SHA[board["id"]], board["id"]
        assert len(board["pads"]) == PAD_COUNT[board["id"]], board["id"]
        native = ASSETS / board["id"] / "kicad" / ("%s.kicad_pcb" % board["design"])
        assert sha256(native) == board["pcb_sha256"], board["id"]
    assert index["boards"][0]["copper_layers"] == 1, "the arm ribbon has one copper layer"
    assert all(b["copper_layers"] == 2 for b in index["boards"][1:])


def test_every_pad_sits_inside_its_frame(index):
    """The transform out of the CAM frame is what makes the overlay meaningful."""
    for board in index["boards"]:
        x0, y0, w, h = board["frame"]["viewBox"]
        for pad in board["pads"]:
            x, y = pad["xy"]
            assert x0 <= x <= x0 + w, (board["id"], pad["ref"], pad["pin"])
            assert y0 <= y <= y0 + h, (board["id"], pad["ref"], pad["pin"])


def test_layers_are_themeable_and_share_one_frame(index):
    for board in index["boards"]:
        frame = " ".join("%g" % v for v in board["frame"]["viewBox"])
        for layer in board["layers"]:
            path = ASSETS / layer["file"]
            assert path.exists() and sha256(path) == layer["sha256"], layer["file"]
            text = path.read_text(encoding="utf-8")
            assert 'viewBox="%s"' % frame in text, layer["file"]
            assert not re.search(r"#[0-9A-Fa-f]{6}", text), layer["file"] + " kept baked colours"
            assert "<text" not in text, layer["file"]
        ids = [l["id"] for l in board["layers"]]
        assert "Edge_Cuts" in ids and "F_Cu" in ids
        if board["copper_layers"] == 2:
            assert "B_Cu" in ids, board["id"]


def test_vendor_correspondence_is_not_published():
    """The per-design fabrication reviews carry a vendor message id, and the
    netlists carry a machine path. Neither may reach the site."""
    forbidden = [r"W1144574AS7C1", r"ParentId", r"[A-Za-z]:[\\/]Users[\\/]", r"Marcelo"]
    for path in sorted(ASSETS.rglob("*")):
        if not path.is_file():
            continue
        blobs = [(path.name, path.read_bytes())]
        if path.suffix == ".zip":
            with zipfile.ZipFile(path) as zf:
                blobs.extend((path.name + "!" + n, zf.read(n)) for n in zf.namelist())
        for name, blob in blobs:
            text = blob.decode("latin-1")
            for pattern in forbidden:
                assert not re.search(pattern, text), "%s matches /%s/" % (name, pattern)
    assert not list(ASSETS.rglob("FABRICATION-REVIEW.txt"))
    assert not list(ASSETS.rglob("netlist.xml"))
    page = PAGE_FILE.read_text(encoding="utf-8")
    for pattern in forbidden:
        assert not re.search(pattern, page), pattern


def test_generated_blocks_cover_every_pad(index):
    page = PAGE_FILE.read_text(encoding="utf-8")
    for name in ("flex-boards", "flex-connections", "flex-electrical",
                 "flex-validation", "flex-downloads"):
        assert page.count("<!-- el-pcb:generated %s start -->" % name) == 1, name
        assert page.count("<!-- el-pcb:generated %s end -->" % name) == 1, name
    rows = re.findall(r'data-flex-row="([^"]+)"', page)
    assert len(rows) == 292
    for board in index["boards"]:
        for pad in board["pads"]:
            key = "%s:%s:%s" % (board["id"], pad["ref"], pad["pin"])
            assert key in rows, key
    # the honest numbers have to actually appear
    assert "0.346" in page and "0.30 mm" in page, "the alignment hold must state its numbers"
    # normalise wrapping and emphasis before looking for the honest statements
    flat = re.sub(r"[*\s]+", " ", page).lower()
    assert "submitted to jlcpcb for engineering quotation" in flat
    assert "no payment or production release" in flat
    assert "no physical qualification of any kind" in flat
    assert "not a passed physical test" in flat

    docs = REPO / "docs"
    page_dir = docs / "10-the-flex-circuits"
    for attr in ("href", "src", "data-base"):
        for value in re.findall(attr + r'="([^"#][^"]*)"', page):
            if value.startswith(("http", "#", "mailto:")):
                continue
            assert (page_dir / value).resolve().exists(), "%s=%s" % (attr, value)


# --------------------------------------------------------------------- browser
def ready(page):
    errors = []
    failures = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("requestfailed", lambda r: failures.append(r.url))
    page.goto(PAGE)
    page.wait_for_selector(READY, timeout=30000)
    page.locator(".el-flex-canvas").scroll_into_view_if_needed()
    page.wait_for_timeout(80)
    return errors, failures


def state(page):
    return page.evaluate("window.elFlex.getState()")


def test_viewer_loads_and_switches_between_circuits(page):
    errors, failures = ready(page)
    s = state(page)
    assert s["board"] == "gimbal" and s["pads"] == 70
    assert page.locator(".el-flex-pad").count() == 70
    assert set(s["layers"]) == {"Edge_Cuts", "F_Cu", "F_Silkscreen"}

    for board, pads in (("upper", 126), ("lower", 96)):
        page.evaluate("b => window.elFlex.setBoard(b)", board)
        page.wait_for_function("n => window.elFlex.getState().pads === n", arg=pads, timeout=15000)
        assert page.locator(".el-flex-pad").count() == pads
        page.evaluate("window.elFlex.toggleLayer('B_Cu', true)")
        page.wait_for_function("window.elFlex.getState().layers.includes('B_Cu')", timeout=15000)
    assert not errors, errors
    assert not failures, failures


def test_pads_are_drawn_on_the_copper(page):
    """If the CAM-to-native transform drifts, pads land somewhere plausible but
    wrong. Compare every marker against the rendered copper's own bounding box."""
    ready(page)
    for board in ("gimbal", "upper", "lower"):
        page.evaluate("b => window.elFlex.setBoard(b)", board)
        page.wait_for_function("b => window.elFlex.getState().board === b", arg=board, timeout=15000)
        if board == "upper":
            page.evaluate("window.elFlex.toggleLayer('B_Cu', true)")
        page.wait_for_timeout(700)
        result = page.evaluate("""() => {
            const cu = document.querySelector('.el-pcb-layer[data-layer="F_Cu"]');
            if (!cu || !cu.getBBox) return null;
            const bb = cu.getBBox();
            if (!bb.width) return null;
            const pads = Array.from(document.querySelectorAll('.el-flex-pad'));
            let inside = 0;
            for (const p of pads) {
                const x = +p.getAttribute('cx'), y = +p.getAttribute('cy');
                const isTail = p.getAttribute('data-ref') === 'J100';
                const box = isTail ? document.querySelector('.el-pcb-layer[data-layer="B_Cu"]').getBBox() : bb;
                if (x >= box.x - 0.5 && x <= box.x + box.width + 0.5 &&
                    y >= box.y - 0.5 && y <= box.y + box.height + 0.5) inside++;
            }
            return {total: pads.length, inside: inside};
        }""")
        assert result, board
        assert result["inside"] == result["total"], (board, result)


def test_pad_summary_pins_and_jumps_to_its_row(page):
    ready(page)
    # The default view fills the frame with the circuit's height, so most of a
    # 152 mm ribbon is off to the side. Click a pad that is genuinely on screen.
    point = page.evaluate("""() => {
        const box = document.querySelector('.el-flex-canvas').getBoundingClientRect();
        for (const p of document.querySelectorAll('.el-flex-pad')) {
            const s = window.elFlex.toScreen(+p.getAttribute('cx'), +p.getAttribute('cy'));
            if (s.x > box.left + 8 && s.x < box.right - 8 &&
                s.y > box.top + 8 && s.y < box.bottom - 8) return s;
        }
        return null;
    }""")
    assert point, "no pad is visible in the default view"
    before = page.evaluate("window.scrollY")
    page.mouse.click(point["x"], point["y"])
    tip = page.locator("#el-flex-tip")
    tip.wait_for(state="visible", timeout=5000)
    assert "is-pinned" in tip.get_attribute("class")
    assert "pin" in tip.text_content()
    assert abs(page.evaluate("window.scrollY") - before) < 4, \
        "selecting a pad must not scroll the page"

    marked = page.locator("[data-flex-row][aria-current='true']")
    assert marked.count() == 1

    tip.locator("button.el-flex-tip-table").click()
    page.wait_for_timeout(700)
    assert page.evaluate("window.scrollY") > before + 100
    assert "connection table row" in page.locator("#el-flex .el-pcb-status").text_content()


def test_pad_search_highlights_matches(page):
    ready(page)
    page.fill("#el-flex-search", "CAN_H")
    page.wait_for_timeout(200)
    results = page.locator(".el-flex-results").text_content()
    assert "matching pad" in results, results
    assert page.locator(".el-pcb-ring.group").count() >= 6, "CAN_H reaches every termination bank"
    page.fill("#el-flex-search", "zzzznope")
    page.wait_for_timeout(200)
    assert "No pad matches" in page.locator(".el-flex-results").text_content()


def test_flex_page_has_no_horizontal_scroll(page):
    for width, height in ((390, 844), (1280, 800)):
        page.set_viewport_size({"width": width, "height": height})
        ready(page)
        assert page.evaluate(
            "document.documentElement.scrollWidth <= window.innerWidth + 1"), width


def test_flex_page_works_without_javascript(context, base_url):
    ctx = context.browser.new_context(java_script_enabled=False, base_url=base_url)
    p = ctx.new_page()
    p.goto(PAGE)
    assert p.locator(".el-flex-fallback").is_visible()
    assert p.locator("[data-flex-row]").count() == 292
    ctx.close()


def test_flex_screenshots(page):
    screens = REPO / "test-artifacts" / "screens"
    screens.mkdir(parents=True, exist_ok=True)
    page.set_viewport_size({"width": 1400, "height": 1000})
    ready(page)
    page.evaluate("""() => { const h = document.querySelector('.md-header'); if (h) h.style.display='none'; }""")
    page.evaluate("window.elFlex.setBoard('upper')")
    page.wait_for_timeout(1500)
    page.evaluate("window.elFlex.toggleLayer('F_Mask', true)")
    page.wait_for_timeout(800)
    page.locator("#el-flex").screenshot(path=str(screens / "flex-upper-1400.png"))

    page.evaluate("window.elFlex.setBoard('gimbal')")
    page.wait_for_timeout(1200)
    page.evaluate("window.elFlex.select(0)")
    page.wait_for_timeout(500)
    page.locator("#el-flex").screenshot(path=str(screens / "flex-gimbal-1400.png"))


def test_upper_defaults_to_visible_insertion_tail(page):
    ready(page)
    page.evaluate("window.elFlex.setBoard('upper')")
    page.wait_for_timeout(500)
    assert "B_Cu" in state(page)["layers"]
    assert page.evaluate("""() => {
        const canvas = document.querySelector('.el-flex-canvas').getBoundingClientRect();
        const pads = [...document.querySelectorAll('.el-flex-pad[data-ref="J100"]')];
        return pads.length === 30 && pads.every(p => {
            const b = p.getBoundingClientRect();
            return b.left >= canvas.left && b.right <= canvas.right &&
                   b.top >= canvas.top && b.bottom <= canvas.bottom;
        });
    }""")
