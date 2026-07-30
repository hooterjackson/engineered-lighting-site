"""Acceptance tests from site-build-brief.md, automated.

Each test gets a fresh browser context (and thus empty localStorage).
"""
import pathlib

SCREENS = pathlib.Path(__file__).resolve().parents[2] / "test-artifacts" / "screens"

CHECK_IDS = ("d3-motors", "d3-multimeter", "d5-poe-switch", "d8-irm")


def _section_total(page, section="d3"):
    """How many items that section actually has, so adding one doesn't fail a test."""
    return page.locator(f'.bom-section[data-section="{section}"] .bom-box').count()


def test_checklist_persists_across_reload(page):
    page.goto("/bom-checklist/")
    for cid in CHECK_IDS:
        page.check(f"#{cid}")
    # totals come from the page, not from a literal: the BoM is allowed to grow
    assert page.locator(".bom-progress").first.text_content().startswith(
        f"2/{_section_total(page)}"
    )
    page.reload()
    for cid in CHECK_IDS:
        assert page.is_checked(f"#{cid}"), f"{cid} lost after reload"
    stored = page.evaluate("JSON.parse(localStorage.getItem('el-bom-v1'))")
    assert stored == {cid: 1 for cid in CHECK_IDS}


def test_reset_clears_only_its_section(page):
    page.goto("/bom-checklist/")
    page.check("#d3-motors")
    page.check("#d5-camera")
    page.click('.bom-section[data-section="d3"] [data-reset]')
    assert not page.is_checked("#d3-motors")
    assert page.is_checked("#d5-camera")


def test_copy_unchecked_shopping_list(page, context):
    context.grant_permissions(["clipboard-read", "clipboard-write"])
    page.goto("/bom-checklist/")
    page.check("#d5-camera")
    page.click('.bom-section[data-section="d5"] [data-copy]')
    text = page.evaluate("navigator.clipboard.readText()")
    assert text.startswith("Doc 5 · Per-room perception")
    assert "- [ ]" in text
    assert "PoE switch" in text, "unchecked item missing from list"
    assert "Amcrest" not in text, "checked item leaked into list"


def test_global_progress_math(page):
    page.goto("/bom-checklist/")
    total = page.locator(".bom-box").count()
    # text_content(), not inner_text(): the theme uppercases these via CSS
    assert page.locator("#bom-global-text").text_content() == f"0/{total} items"
    assert page.locator("#bom-bar").get_attribute("max") == str(total), (
        "the progress bar's max is hardcoded in the page and has drifted from the "
        "number of checkboxes actually on it"
    )
    page.check("#d3-motors")
    assert page.locator("#bom-global-text").text_content() == f"1/{total} items"
    assert page.locator(".bom-progress").first.text_content() == (
        f"1/{_section_total(page)} · ~$269 checked"
    )


def test_chapter_done_when_persists(page):
    page.goto("/03-build-the-gimbal/")
    first = page.locator(".task-list-item [type=checkbox]").first
    first.check(force=True)  # input is visually replaced by the indicator
    assert page.locator(".el-done-progress").first.text_content() == "1/7 done"
    page.reload()
    assert page.locator(".task-list-item [type=checkbox]").first.is_checked()
    stored = page.evaluate("JSON.parse(localStorage.getItem('el-done-v1'))")
    assert stored == {"03-build-the-gimbal:0": 1}


def test_checklist_uses_wide_viewports(page):
    page.set_viewport_size({"width": 1800, "height": 900})
    page.goto("/bom-checklist/")
    overflows = page.evaluate(
        "Array.from(document.querySelectorAll('.bom-scroll'))"
        ".map(s => s.scrollWidth - s.clientWidth)")
    assert all(o <= 1 for o in overflows), f"table crops on wide screens: {overflows}"
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto("/bom-checklist/")
    assert page.evaluate(
        "document.documentElement.scrollWidth <= window.innerWidth + 1"), \
        "page-level horizontal scroll on mobile"


def test_motor_state_survives_part_rename(page):
    # the 4005→5005 swap must not orphan saved state: id d3-motors is stable
    page.goto("/bom-checklist/")
    page.evaluate("localStorage.setItem('el-bom-v1', JSON.stringify({'d3-motors': 1}))")
    page.reload()
    assert page.locator("#d3-motors").is_checked(), "pre-rename state lost"


def test_agent_prompt_copy_button(page, context):
    context.grant_permissions(["clipboard-read", "clipboard-write"])
    page.goto("/03-build-the-gimbal/")
    page.locator(".admonition.agent-prompt .md-code__button").first.click()
    text = page.evaluate("navigator.clipboard.readText()")
    assert text.startswith("You're my bench agent"), text[:80]
    assert "wait for my approval" in text


def test_screenshots(page):
    SCREENS.mkdir(parents=True, exist_ok=True)
    pages = (("landing", "/"), ("doc3", "/03-build-the-gimbal/"),
             ("checklist", "/bom-checklist/"))
    for name, path in pages:
        for width, height in ((390, 844), (1280, 800)):
            page.set_viewport_size({"width": width, "height": height})
            page.goto(path)
            page.wait_for_timeout(250)
            page.screenshot(path=str(SCREENS / f"{name}-{width}.png"))
