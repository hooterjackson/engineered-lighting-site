"""Purchasing progress must survive reload without inheriting old bench orders."""
from playwright.sync_api import expect

PATH = "/09a-pcb-build-bom/"
KEY = "el-pcb-fixture-orders-v1"


def test_pcb_orders_persist_and_stay_separate(page):
    page.goto(PATH)
    page.evaluate("localStorage.setItem('el-bom-v1', JSON.stringify({'d3-motors': 1}))")
    assert not page.is_checked("#pcb-motors")
    page.check("#pcb-main")
    page.check("#pcb-gh6")
    page.reload()
    assert page.is_checked("#pcb-main") and page.is_checked("#pcb-gh6")
    assert not page.is_checked("#pcb-motors")
    assert page.evaluate("JSON.parse(localStorage.getItem('el-bom-v1'))") == {"d3-motors": 1}
    total = page.locator('.pcb-order-box[data-required="true"]').count()
    expect(page.locator("#pcb-order-total")).to_have_text(f"2 / {total} required purchase lines covered")
    # Optional/alternative records do not increase required procurement progress.
    page.check("#pcb-pa-diy")
    expect(page.locator("#pcb-order-total")).to_have_text(f"2 / {total} required purchase lines covered")


def test_pcb_copy_contains_quantities_and_open_decisions(page, context):
    context.grant_permissions(["clipboard-read", "clipboard-write"])
    page.goto(PATH)
    page.check("#pcb-main")
    page.check("#pcb-diffuser")  # Covered by owned Yupo or chosen diffuser alternative.
    page.click("#pcb-copy-remaining")
    expect(page.locator("#pcb-copy-message")).to_have_text("Remaining required purchases copied.")
    text = page.evaluate("navigator.clipboard.readText()")
    assert "2 housings" in text and "GHR-06V-S" in text
    assert "Select compatible SKU" in text and "26 AWG" in text
    assert "L21-YPT153WH1114" not in text
    assert "Roscolux" not in text  # optional alternatives are not mandatory buys
    assert "2 complete assemblies" not in text


def test_pcb_save_failure_preserves_session_checks(page):
    page.goto(PATH)
    page.evaluate(f"localStorage.setItem('{KEY}', JSON.stringify({{'pcb-main': false}}))")
    page.reload()
    page.evaluate("() => { Storage.prototype.setItem = function () { throw new Error('quota'); }; }")
    page.check("#pcb-main")
    page.check("#pcb-upper")
    assert page.is_checked("#pcb-main") and page.is_checked("#pcb-upper")
    expect(page.locator("#pcb-save-message")).to_contain_text("cannot save progress")


def test_pcb_checklist_small_viewport_and_unique_ids(page):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(PATH)
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")
    ids = page.locator(".pcb-order-box").evaluate_all("xs => xs.map(x => x.id)")
    assert len(ids) == len(set(ids))
    page.check("#pcb-gh4")
    assert page.is_checked("#pcb-gh4")
