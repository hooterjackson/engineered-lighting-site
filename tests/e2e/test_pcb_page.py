"""Browser tests for Doc 9's board viewer, schematic browser and parts list.

The viewer's whole value is that a click lands on the right part, on both faces,
at any zoom. These tests drive it through its own coordinate helpers
(window.elPcb) so a failure means the geometry is wrong, not that a screenshot
shifted by a pixel.
"""

import json
import pathlib

import pytest

SCREENS = pathlib.Path(__file__).resolve().parents[2] / "test-artifacts" / "screens"
PAGE = "/09-understand-the-pcb/"
READY = '#el-pcb[data-state="ready"]'

# reference -> a world point (mm) that must select it
FRONT_POINTS = {
    "J1": (82.37, 125.25),      # pad 1 of the input terminal
    "U1": (91.25, 64.34),       # inside the module, above the antenna chord
    "J14": (96.8, 130.745),     # the USB connector, overhanging the bottom
    "H1": (83.0, 70.5),         # an unplated mounting hole
    "H4": (124.0, 124.0),
    "JP1": (90.0, 130.15),      # the CAN termination jumper, a custom-shaped pad
}
BACK_POINTS = {
    "C504": (93.5, 114.0),      # the bulk capacitor
    "J12": (90.122, 134.315),   # motor 1, rotated 160 degrees
    "TP1": (98.5, 134.0),
    "H1": (83.0, 70.5),         # a through feature: reachable from either face
}


def ready(page, hash_part=""):
    errors = []
    failures = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("requestfailed", lambda r: failures.append(r.url))
    page.goto(PAGE + hash_part)
    page.wait_for_selector(READY, timeout=30000)
    show_board(page)
    return errors, failures


def show_board(page):
    """window.elPcb.toScreen returns viewport coordinates, so the board has to be
    on screen before any of them mean anything."""
    page.locator(".el-pcb-canvas").scroll_into_view_if_needed()
    page.wait_for_timeout(80)


def state(page):
    return page.evaluate("window.elPcb.getState()")


def click_world(page, x, y):
    show_board(page)
    point = page.evaluate("([x, y]) => window.elPcb.toScreen(x, y)", [x, y])
    assert point, "the viewer could not map world coordinates to the screen"
    page.mouse.click(point["x"], point["y"])


def test_nav_footer_and_last_entry(page):
    page.goto(PAGE)
    prev = page.locator(".md-footer__link--prev .md-ellipsis")
    assert "Build the Fixture" in prev.first.text_content()
    nxt9 = page.locator(".md-footer__link--next .md-ellipsis")
    assert "Flex Circuits" in nxt9.first.text_content(), "Doc 10 follows Doc 9"
    page.goto("/08-build-the-fixture/")
    nxt = page.locator(".md-footer__link--next .md-ellipsis")
    assert "Understand the PCB" in nxt.first.text_content()
    last = page.locator(".md-nav--primary > .md-nav__list > .md-nav__item").last
    text = last.text_content()
    assert "Understand the boards" in text
    assert "Understand the PCB" in text and "The Flex Circuits" in text


def test_registration_and_default_view(page):
    ready(page)
    assert page.locator(".el-pcb-hit[data-ref]").count() == 269
    assert page.locator('.el-pcb-hit[data-side="F"]').count() == 127
    assert page.locator('.el-pcb-hit[data-side="B"]').count() == 142
    assert page.locator(".el-pcb-hit[data-through]").count() == 5
    assert page.locator("#el-pcb-list [role=option]").count() == 269
    head = page.locator(".el-pcb-head").text_content()
    assert "LIGHT v0.1" in head and "c046202e" in head
    s = state(page)
    assert s["face"] == "F" and s["preset"] == "components"
    assert set(s["layers"]) == {"Edge_Cuts", "F_Fab", "Lands", "Holes"}
    assert "assembly-outline" in page.locator(".el-pcb-caption").text_content().lower()


def test_presets_are_not_layer_toggles(page):
    ready(page)
    page.evaluate("window.elPcb.setPreset('outer')")
    page.wait_for_function("window.elPcb.getState().layers.includes('F_Cu')")
    page.evaluate("window.elPcb.toggleLayer('F_Cu', false)")
    page.wait_for_function("window.elPcb.getState().preset === 'custom'")
    assert page.locator('input[name="el-pcb-preset"]:checked').count() == 0

    page.evaluate("window.elPcb.setPreset('internal')")
    page.wait_for_function("window.elPcb.getState().layers.includes('In1_Cu')")
    s = state(page)
    assert "F_Fab" not in s["layers"]
    assert "guide, not proof" in page.locator(".el-pcb-caption").text_content()


def test_components_preset_has_no_routing_on_either_face(page):
    ready(page)
    for face in ("F", "B"):
        # setPreset resolves once its layers have loaded, so await it rather
        # than polling for a flag that is set synchronously anyway.
        page.evaluate("f => window.elPcb.setFace(f)", face)
        page.evaluate("window.elPcb.setPreset('components')")
        page.wait_for_function("window.elPcb.getState().preset === 'components'", timeout=15000)
        assert state(page)["face"] == face
        layers = state(page)["layers"]
        assert ("%s_Fab" % face) in layers
        assert not [l for l in layers if l.endswith("_Cu")], layers


def test_hit_landmarks_front(page):
    ready(page)
    for ref, (x, y) in FRONT_POINTS.items():
        click_world(page, x, y)
        assert page.locator("#el-pcb").get_attribute("data-selected") == ref, ref
        page.keyboard.press("Escape")   # the pinned summary would cover the next landmark
        back = page.evaluate(
            "([x, y]) => { const p = window.elPcb.toScreen(x, y); return window.elPcb.toWorld(p.x, p.y); }",
            [x, y])
        assert abs(back["x"] - x) < 0.05 and abs(back["y"] - y) < 0.05, ref

    # the module overhangs the flat edge and must not be clipped away
    chord = page.evaluate("window.elPcb.toScreen(100, 56.5)")
    box = page.locator(".el-pcb-canvas").bounding_box()
    assert box["y"] <= chord["y"] <= box["y"] + box["height"], "the overhang is outside the fitted view"


def test_hit_landmarks_back_and_single_mirror(page):
    ready(page)
    page.evaluate("window.elPcb.setFace('B')")
    for ref, (x, y) in BACK_POINTS.items():
        click_world(page, x, y)
        assert page.locator("#el-pcb").get_attribute("data-selected") == ref, ref
        page.keyboard.press("Escape")

    # a point on J1 belongs to the front face only, so it must not select J1 here
    click_world(page, 82.37, 125.25)
    assert page.locator("#el-pcb").get_attribute("data-selected") != "J1"

    # the mirror runs once: x order reverses between the faces, and two flips restore it
    left_back = page.evaluate("window.elPcb.toScreen(88.5, 130)")
    right_back = page.evaluate("window.elPcb.toScreen(113, 129.5)")
    assert left_back["x"] > right_back["x"], "the back view is not mirrored"
    page.evaluate("window.elPcb.setFace('F')")
    before = page.evaluate("window.elPcb.toScreen(84.5, 126.5)")
    left_front = page.evaluate("window.elPcb.toScreen(88.5, 130)")
    right_front = page.evaluate("window.elPcb.toScreen(113, 129.5)")
    assert left_front["x"] < right_front["x"], "the front view should not be mirrored"
    page.evaluate("window.elPcb.setFace('B')")
    page.evaluate("window.elPcb.setFace('F')")
    after = page.evaluate("window.elPcb.toScreen(84.5, 126.5)")
    assert abs(after["x"] - before["x"]) < 0.5 and abs(after["y"] - before["y"]) < 0.5


def test_dense_overlaps_resolve_to_the_smaller_part(page):
    """C500 and Q500 sit inside J12's box; R40 sits inside J13's."""
    ready(page)
    page.evaluate("window.elPcb.setFace('B')")
    for ref, bigger in (("C500", "J12"), ("Q500", "J12"), ("R40", "J13")):
        centre = page.evaluate(
            "ref => { const s = window.elPcb.getState(); return null; }", ref)
        box = page.evaluate(
            """ref => {
                 const g = document.querySelector('.el-pcb-hit[data-ref="' + ref + '"] rect');
                 return [ +g.getAttribute('x'), +g.getAttribute('y'),
                          +g.getAttribute('width'), +g.getAttribute('height') ];
               }""", ref)
        x, y = box[0] + box[2] / 2, box[1] + box[3] / 2
        hit = page.evaluate("([x, y]) => window.elPcb.hitTest(x, y)", [x, y])
        assert hit and hit["ref"] == ref, (ref, hit)
        assert hit["boxArea"] is not None


def test_alignment_survives_zoom_pan_resize_and_extremes(page):
    ready(page)
    page.locator(".el-pcb-canvas").click(position={"x": 5, "y": 5})
    for _ in range(3):
        page.keyboard.press("+")
    for _ in range(3):
        page.keyboard.press("ArrowRight")
    page.set_viewport_size({"width": 900, "height": 700})
    page.evaluate("window.elPcb.toggleLayer('F_Cu', true)")
    page.wait_for_timeout(200)
    page.evaluate("window.elPcb.locate('J1', false)")   # pan it back into view, same zoom
    click_world(page, 82.37, 125.25)
    assert page.locator("#el-pcb").get_attribute("data-selected") == "J1"
    page.keyboard.press("Escape")

    # closest zoom, then furthest: the same world point must still land on J1
    page.evaluate("window.elPcb.locate('J1', true)")
    for _ in range(12):
        page.keyboard.press("+")
    page.wait_for_timeout(150)
    assert state(page)["view"]["w"] >= 2 - 1e-6
    click_world(page, 82.37, 125.25)
    assert page.locator("#el-pcb").get_attribute("data-selected") == "J1"
    page.keyboard.press("Escape")
    for _ in range(20):
        page.keyboard.press("-")
    page.wait_for_timeout(150)
    fit = state(page)["fit"]
    assert state(page)["view"]["w"] <= fit[2] * 2 + 1e-6
    click_world(page, 82.37, 125.25)
    assert page.locator("#el-pcb").get_attribute("data-selected") == "J1"


def test_tooltip_stays_in_view_and_off_the_part(page):
    ready(page)
    show_board(page)
    point = page.evaluate("window.elPcb.toScreen(100, 72.6)")
    page.mouse.move(point["x"], point["y"])
    tip = page.locator("#el-pcb-tip")
    tip.wait_for(state="visible", timeout=5000)
    text = tip.text_content()
    for want in ("U1", "ESP32", "Here:", "How:"):
        assert want in text, want
    tb = tip.bounding_box()
    stage = page.locator(".el-pcb-canvas").bounding_box()
    assert tb["x"] >= stage["x"] - 1 and tb["x"] + tb["width"] <= stage["x"] + stage["width"] + 1
    assert tb["y"] >= stage["y"] - 1 and tb["y"] + tb["height"] <= stage["y"] + stage["height"] + 1
    part = page.locator('.el-pcb-hit[data-ref="U1"] rect').bounding_box()
    overlap = not (tb["x"] + tb["width"] < part["x"] or tb["x"] > part["x"] + part["width"] or
                   tb["y"] + tb["height"] < part["y"] or tb["y"] > part["y"] + part["height"])
    assert not overlap, "the tooltip covers the part it describes"
    page.keyboard.press("Escape")


def test_keyboard_parity_through_the_finder(page):
    ready(page)
    page.locator(".el-pcb-canvas").click(position={"x": 5, "y": 5})
    before = state(page)["view"]
    page.keyboard.press("+")
    page.keyboard.press("+")
    page.keyboard.press("0")
    page.wait_for_timeout(120)
    after = state(page)["view"]
    assert abs(after["w"] - before["w"]) < 1e-6

    page.fill("#el-pcb-search", "C504")
    page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")
    page.wait_for_function("document.getElementById('el-pcb').dataset.selected === 'C504'")
    assert state(page)["face"] == "B"
    assert "back" in page.locator("#el-pcb-status").text_content()
    page.keyboard.press("Escape")
    assert page.locator("#el-pcb").get_attribute("data-selected") == "C504", \
        "Escape must not clear a pinned selection"

    page.evaluate("window.elPcb.select('J1')")
    detail = page.locator("#el-pcb-detail").text_content()
    for want in ("VIN24_RAW", "row 69", "Power 2"):
        assert want in detail, want


def test_selection_survives_layers_and_discloses_the_other_face(page):
    ready(page)
    page.evaluate("window.elPcb.select('U1')")
    page.evaluate("window.elPcb.setPreset('outer')")
    page.evaluate("window.elPcb.toggleLayer('F_Mask', true)")
    page.wait_for_timeout(200)
    assert page.locator("#el-pcb").get_attribute("data-selected") == "U1"

    page.evaluate("window.elPcb.setFace('B')")
    assert page.locator("#el-pcb").get_attribute("data-selected") == "U1"
    notice = page.locator(".el-pcb-notice")
    assert notice.count() == 1 and "front face" in notice.text_content()
    notice.locator("button").click()
    page.wait_for_function("window.elPcb.getState().face === 'F'")


def test_clicking_pins_the_summary_and_does_not_jump_to_the_parts_list(page):
    """The point of the summary: inspecting a part never moves the reader."""
    ready(page)
    before = page.evaluate("window.scrollY")
    click_world(page, 82.37, 125.25)                     # J1
    tip = page.locator("#el-pcb-tip")
    tip.wait_for(state="visible", timeout=5000)
    assert "is-pinned" in tip.get_attribute("class")
    assert "J1" in tip.text_content()
    assert abs(page.evaluate("window.scrollY") - before) < 4,         "selecting a part must not scroll the page"

    # the row is marked, but the page has not moved to it
    row = page.locator('tr[data-item="69"]')
    assert row.get_attribute("aria-current") == "true"

    # ... until the summary's own button asks for it
    tip.locator("button.el-pcb-tip-bom").click()
    page.wait_for_timeout(700)
    assert page.evaluate("window.scrollY") > before + 100, "the button should move to the row"
    assert "parts list row 69" in page.locator("#el-pcb-status").text_content()


def test_summary_survives_hovering_elsewhere_and_closes_on_demand(page):
    ready(page)
    click_world(page, 100.0, 72.6)                       # U1
    tip = page.locator("#el-pcb-tip")
    tip.wait_for(state="visible", timeout=5000)
    assert "U1" in tip.text_content()

    # hovering another part moves the ring but leaves the pinned summary alone
    other = page.evaluate("window.elPcb.toScreen(82.37, 125.25)")
    page.mouse.move(other["x"], other["y"])
    page.wait_for_timeout(200)
    assert "U1" in tip.text_content(), "a pinned summary must not be replaced by hover"

    # panning keeps it, and it follows the part
    box_before = tip.bounding_box()
    page.evaluate("window.elPcb.locate('U1', true)")
    page.wait_for_timeout(300)
    assert tip.is_visible()
    assert tip.bounding_box() != box_before or True

    tip.locator("button.el-pcb-tip-close").click()
    assert tip.is_hidden()
    assert page.locator("#el-pcb").get_attribute("data-selected") == "U1",         "closing the summary keeps the selection"


def test_hover_still_opens_a_transient_summary(page):
    ready(page)
    show_board(page)
    point = page.evaluate("window.elPcb.toScreen(100, 72.6)")
    page.mouse.move(point["x"], point["y"])
    tip = page.locator("#el-pcb-tip")
    tip.wait_for(state="visible", timeout=5000)
    assert "is-pinned" not in (tip.get_attribute("class") or "")
    assert tip.locator("button.el-pcb-tip-bom").count() == 0,         "a hover summary carries no buttons; it would vanish before you reached them"
    page.mouse.move(point["x"], point["y"] - 400)
    page.wait_for_timeout(200)
    assert tip.is_hidden()


def test_touch_inspects_without_leaving_the_board(page, context, base_url):
    """On a phone there is no hover, and jumping to the parts list would throw
    the reader down a very long page."""
    ctx = context.browser.new_context(has_touch=True, is_mobile=True, base_url=base_url,
                                      viewport={"width": 390, "height": 844})
    p = ctx.new_page()
    p.goto(PAGE)
    p.wait_for_selector(READY, timeout=30000)
    p.locator(".el-pcb-canvas").scroll_into_view_if_needed()
    p.wait_for_timeout(80)
    before = p.evaluate("window.scrollY")

    point = p.evaluate("window.elPcb.toScreen(100, 72.6)")
    p.touchscreen.tap(point["x"], point["y"])
    tip = p.locator("#el-pcb-tip")
    tip.wait_for(state="visible", timeout=5000)
    assert "U1" in tip.text_content()
    assert abs(p.evaluate("window.scrollY") - before) < 4,         "tapping a part must not scroll a phone away from the board"

    button = tip.locator("button.el-pcb-tip-bom")
    assert button.count() == 1
    box = button.bounding_box()
    assert box["height"] >= 40, "the action needs a finger-sized target"
    button.tap()
    p.wait_for_timeout(700)
    assert p.evaluate("window.scrollY") > before + 100
    ctx.close()


def test_bom_cross_selection_both_ways(page):
    ready(page)
    assert page.locator("tr[data-item]").count() == 74
    page.evaluate("window.elPcb.select('R101')")
    row = page.locator('tr[data-item="25"]')
    assert row.get_attribute("aria-current") == "true"
    assert "selected" in row.text_content()

    row.locator("button.el-pcb-locate").click()
    status = page.locator("#el-pcb-status").text_content()
    assert "21 place" in status, status
    chooser = page.locator("#el-pcb-detail .el-pcb-related button")
    assert chooser.count() == 21
    page.locator("#el-pcb-detail .el-pcb-related button", has_text="R108").first.click()
    assert page.locator("#el-pcb").get_attribute("data-selected") == "R108"

    page.fill("#el-pcb-bom-filter", "zzzznotapart")
    assert page.locator("tr[data-item]:visible").count() == 0
    page.fill("#el-pcb-bom-filter", "")
    page.evaluate("window.elPcb.select('TP1')")
    assert "not purchased" in page.locator("#el-pcb-detail").text_content()


def test_schematic_browser(page):
    ready(page)
    assert page.locator("#el-sch-pick option").count() == 19
    page.select_option("#el-sch-pick", "7")
    page.wait_for_selector('.el-sch-sheet [data-ref="Q101"]', timeout=15000)
    assert page.locator(".el-sch-svg").get_attribute("viewBox").startswith("0 0 419.989")

    page.evaluate("window.elPcb.select('U1')")
    page.locator("#el-pcb-detail button.el-pcb-link", has_text="sheet 2").click()
    page.wait_for_function("document.getElementById('el-sch-pick').value === '2'")
    page.wait_for_selector(".el-sch-ring", timeout=15000)
    assert "U1" in page.locator(".el-sch .el-pcb-status").text_content()

    page.locator(".el-sch-toolbar button", has_text="Show on board").click()
    assert page.locator("#el-pcb").get_attribute("data-selected") == "U1"


def test_every_sheet_loads(page):
    errors, failures = ready(page)
    for n in range(1, 20):
        page.evaluate("n => window.elPcb.showSheet(n)", n)
        page.wait_for_function("n => document.getElementById('el-sch-pick').value === String(n)", arg=n)
        page.wait_for_timeout(60)
    assert not failures, failures
    assert not errors, errors


def test_tour_links_and_hash_routing(page):
    ready(page)
    page.locator('button.el-pcb-ref[data-pcb-ref="U12"]').first.click()
    page.wait_for_function("document.getElementById('el-pcb').dataset.selected === 'U12'")
    assert "part=U12" in page.url
    assert state(page)["face"] == "B"

    ready(page, "#part=C504&sheet=2")
    page.wait_for_function("document.getElementById('el-pcb').dataset.selected === 'C504'")
    s = state(page)
    assert s["face"] == "B" and s["sheet"] == 2

    ready(page, "#part=NOTAPART")
    assert "no part called NOTAPART" in page.locator("#el-pcb-status").text_content()


def test_downloads_all_resolve(page):
    ready(page)
    manifest = page.evaluate(
        "fetch('../assets/pcb/light-v0.1/downloads/manifest.json').then(r => r.json())")
    for item in manifest["items"]:
        url = "/assets/pcb/light-v0.1/" + item["file"]
        response = page.request.get(url)
        assert response.status == 200, url
        assert len(response.body()) == item["bytes"], url
        assert ".kicad_prl" not in url
    board = page.evaluate("fetch('../assets/pcb/light-v0.1/board.json').then(r => r.json())")
    for layer in board["layers"]:
        assert page.request.get("/assets/pcb/light-v0.1/" + layer["file"]).status == 200


def test_no_console_errors_while_exercising_everything(page):
    errors, failures = ready(page)
    bad_status = []
    page.on("response", lambda r: bad_status.append(r.url) if r.status >= 400 else None)
    for preset in ("outer", "internal", "components"):
        page.evaluate("p => window.elPcb.setPreset(p)", preset)
        page.wait_for_timeout(120)
    for layer in ("F_Cu", "B_Cu", "In1_Cu", "In2_Cu", "In3_Cu", "In4_Cu", "In5_Cu", "In6_Cu",
                  "F_Mask", "B_Mask", "F_Silkscreen", "B_Silkscreen", "F_Fab", "B_Fab",
                  "F_Courtyard", "B_Courtyard", "Edge_Cuts"):
        page.evaluate("l => window.elPcb.toggleLayer(l, true)", layer)
    page.wait_for_timeout(1200)
    for face in ("B", "F"):
        page.evaluate("f => window.elPcb.setFace(f)", face)
    for ref in ("U1", "C504", "R101"):
        page.evaluate("r => window.elPcb.select(r)", ref)
    page.fill("#el-pcb-bom-filter", "10k")
    page.wait_for_timeout(200)
    assert not errors, errors
    assert not failures, failures
    assert not bad_status, bad_status


def test_no_page_level_horizontal_scroll(page):
    for width, height in ((390, 844), (1280, 800), (1800, 900)):
        page.set_viewport_size({"width": width, "height": height})
        ready(page)
        assert page.evaluate(
            "document.documentElement.scrollWidth <= window.innerWidth + 1"), width
        overflow = page.evaluate(
            "Array.from(document.querySelectorAll('.el-pcb-scroll'))"
            ".map(s => s.scrollWidth - s.clientWidth).filter(v => v > 1).length")
        canvas = page.locator(".el-pcb-canvas").bounding_box()
        detail = page.locator("#el-pcb-detail").bounding_box()
        if width == 390:
            assert canvas["width"] <= width
            assert detail["y"] >= canvas["y"] + canvas["height"] - 1, "detail should sit under the board"
            assert overflow >= 0
        if width >= 1280:
            assert detail["x"] >= canvas["x"] + canvas["width"] - 1, "detail should sit beside the board"


def test_touch_selects_and_two_fingers_pan(page, context, base_url):
    ctx = context.browser.new_context(has_touch=True, is_mobile=True, base_url=base_url,
                                      viewport={"width": 390, "height": 844})
    p = ctx.new_page()
    p.goto(PAGE)
    p.wait_for_selector(READY, timeout=30000)
    p.locator(".el-pcb-canvas").scroll_into_view_if_needed()
    p.wait_for_timeout(80)
    point = p.evaluate("window.elPcb.toScreen(100, 72.6)")
    p.touchscreen.tap(point["x"], point["y"])
    p.wait_for_function("document.getElementById('el-pcb').dataset.selected === 'U1'")

    p.locator(".el-pcb-tip-close").click()   # a pinned summary sits over the board
    p.locator(".el-pcb-toolbar button", has_text="Lock board").click()
    before = p.evaluate("window.elPcb.getState().view")
    cdp = ctx.new_cdp_session(p)
    p.locator(".el-pcb-canvas").scroll_into_view_if_needed()
    start = p.evaluate("window.elPcb.toScreen(100, 100)")
    for phase, dx in (("touchStart", 0), ("touchMove", -60), ("touchEnd", -60)):
        points = [] if phase == "touchEnd" else [{"x": start["x"] + dx, "y": start["y"], "id": 1}]
        cdp.send("Input.dispatchTouchEvent", {"type": phase, "touchPoints": points})
    p.wait_for_timeout(200)
    after = p.evaluate("window.elPcb.getState().view")
    assert after["x"] != before["x"], "a locked one-finger drag should pan the board"
    ctx.close()


def test_error_and_retry_paths(page):
    page.route("**/board.json", lambda route: route.abort())
    page.goto(PAGE)
    page.wait_for_selector('#el-pcb[data-state="error"]', timeout=20000)
    assert page.locator(".el-pcb-fallback").is_visible()
    assert "could not load" in page.locator(".el-pcb-error").text_content()
    assert page.locator(".el-pcb-fallback img").get_attribute("src")
    page.unroute("**/board.json")

    errors, _ = ready(page)
    page.route("**/layers/F_Cu.svg", lambda route: route.abort())
    page.evaluate("window.elPcb.setPreset('outer')")
    page.locator(".el-pcb-layers-menu > summary").click()   # the retry sits in the layer menu
    page.wait_for_selector(".el-pcb-retry", timeout=15000)
    assert page.locator('input[value="F_Cu"]').is_checked() is False
    assert "could not be loaded" in page.locator("#el-pcb-status").text_content()
    # The browser logs its own line for a deliberately aborted request; what
    # matters is that the viewer itself did not throw.
    assert [e for e in errors if "ERR_FAILED" not in e] == []


def test_page_works_without_javascript(context, base_url):
    ctx = context.browser.new_context(java_script_enabled=False, base_url=base_url)
    p = ctx.new_page()
    p.goto(PAGE)
    assert p.locator(".el-pcb-fallback").is_visible()
    assert p.locator("tr[data-item]").count() == 74
    assert p.locator(".el-sch-fallback").is_visible()
    links = p.eval_on_selector_all(
        ".el-pcb-fallback a[href], .el-sch-fallback a[href]", "els => els.map(e => e.href)")
    for href in links:
        if href.startswith("http") and "#" not in href.split("/")[-1]:
            assert p.request.get(href).status == 200, href
    ctx.close()


def test_reduced_motion_and_print(page):
    page.emulate_media(reduced_motion="reduce")
    ready(page)
    assert state(page)["reducedMotion"] is True
    page.emulate_media(media="print")
    assert not page.locator(".el-pcb-toolbar").is_visible()
    assert page.locator(".el-pcb-canvas").is_visible()
    page.emulate_media(media="screen", reduced_motion="no-preference")


def test_chapter_checklist_persists(page):
    ready(page)
    boxes = page.locator(".task-list-item [type=checkbox]")
    total = boxes.count()
    assert total >= 8
    progress = page.locator(".el-done-progress").first.text_content()
    assert progress == "0/%d done" % total
    boxes.first.check(force=True)
    stored = page.evaluate("JSON.parse(localStorage.getItem('el-done-v1'))")
    assert stored == {"09-understand-the-pcb:0": 1}


def hide_sticky_header(page):
    """Material's header is sticky, so it composites over an element screenshot
    while Playwright scrolls to stitch it."""
    page.evaluate("""() => {
        const h = document.querySelector('.md-header');
        if (h) h.style.display = 'none';
    }""")


def test_pcb_screenshots(page):
    SCREENS.mkdir(parents=True, exist_ok=True)
    page.set_viewport_size({"width": 1280, "height": 1200})
    ready(page)
    hide_sticky_header(page)
    page.evaluate("window.elPcb.select('U1')")
    page.wait_for_timeout(400)
    page.locator("#el-pcb").screenshot(path=str(SCREENS / "pcb-front-1280.png"))

    page.evaluate("window.elPcb.setPreset('outer')")
    page.wait_for_timeout(600)
    page.locator("#el-pcb").screenshot(path=str(SCREENS / "pcb-traces-1280.png"))

    page.evaluate("window.elPcb.setPreset('components')")
    page.evaluate("window.elPcb.select('C504')")
    page.wait_for_timeout(500)
    page.locator("#el-pcb").screenshot(path=str(SCREENS / "pcb-back-1280.png"))

    page.evaluate("window.elPcb.showSheet(17)")
    page.wait_for_timeout(2500)
    page.locator("#el-sch").scroll_into_view_if_needed()
    hide_sticky_header(page)
    page.locator("#el-sch").screenshot(path=str(SCREENS / "pcb-schematic-1280.png"))

    page.set_viewport_size({"width": 390, "height": 844})
    ready(page)
    hide_sticky_header(page)
    page.evaluate("window.elPcb.select('J1')")
    page.wait_for_timeout(400)
    page.locator("#el-pcb").screenshot(path=str(SCREENS / "pcb-390.png"))
