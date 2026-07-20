"""Acceptance tests from site-build-brief.md, automated.

Each test gets a fresh browser context (and thus empty localStorage).
"""
import pathlib

SCREENS = pathlib.Path(__file__).resolve().parents[2] / "test-artifacts" / "screens"

CHECK_IDS = ("d3-motors", "d3-multimeter", "d5-poe-switch")


def test_checklist_persists_across_reload(page):
    page.goto("/bom-checklist/")
    for cid in CHECK_IDS:
        page.check(f"#{cid}")
    assert page.locator(".bom-progress").first.inner_text().startswith("2/13")
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
    assert page.locator("#bom-global-text").inner_text() == "0/30 items"
    page.check("#d3-motors")
    assert page.locator("#bom-global-text").inner_text() == "1/30 items"
    assert page.locator(".bom-progress").first.inner_text() == "1/13 · ~$90 checked"


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
