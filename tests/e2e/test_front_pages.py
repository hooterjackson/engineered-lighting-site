"""The four-page front: Home, Vision, Hardware and Software (docs/index.html,
docs/{vision,hardware,software}/index.html, shared assets in docs/assets/site/).

These are standalone static pages, so the checks here are the ones Material
used to give for free: they load cleanly at every width, with and without
reduced motion, and they keep their honesty and privacy rules.
"""
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
SITE = ROOT / "site"
SITE_ASSETS = DOCS / "assets" / "site"
SCREENS = ROOT / "test-artifacts" / "screens"

WIDTHS = (390, 768, 1440, 1920)
NAV = ["Vision", "Hardware", "Software"]
MARKS = {"Works today", "Partly built", "Not built yet"}
# (name, path, current nav tab, how to tell the page has finished building)
PAGES = (
    ("home", "/", None, "home"),
    ("vision", "/vision/", "Vision", None),
    ("hardware", "/hardware/", "Hardware", '#el-pcb[data-state="ready"]'),
    ("software", "/software/", "Software", None),
)


def _collect_errors(page):
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    return errors


def _wait_built(page, ready):
    if ready == "home":
        # With the opening on, its hint reads "Scroll" once the room scan is in;
        # Skip intro then lands on the den. The den scene only runs while it is
        # on screen, and its HUD shows the loop clock once its scan has loaded.
        if page.evaluate("document.documentElement.dataset.intro === 'on'"):
            page.wait_for_function(
                "document.querySelector('.opening__hint').textContent === 'Scroll'", timeout=60000)
            page.locator(".skip-pill").click()
            page.wait_for_function("Math.abs(document.getElementById('den').getBoundingClientRect().top) < 2")
        page.wait_for_function(
            "/^\\d\\d:\\d\\d$/.test(document.querySelector('.hud__clock').textContent)", timeout=30000)
    elif ready:
        page.wait_for_selector(ready, timeout=20000)


@pytest.mark.parametrize("motion", ["no-preference", "reduce"])
@pytest.mark.parametrize("name,path,current,ready", PAGES, ids=[p[0] for p in PAGES])
def test_front_page_loads_cleanly_at_every_width(page, name, path, current, ready, motion):
    SCREENS.mkdir(parents=True, exist_ok=True)
    page.emulate_media(reduced_motion=motion)
    errors = _collect_errors(page)
    for width in WIDTHS:
        page.set_viewport_size({"width": width, "height": 900 if width > 400 else 844})
        page.goto(path)
        _wait_built(page, ready)
        assert page.locator("h1").count() == 1, f"{path}: one h1 per page"
        nav = page.locator('nav[aria-label="Site"] a')
        assert nav.all_text_contents() == NAV, f"{path}: nav order"
        on = page.locator('nav[aria-label="Site"] a[aria-current="page"]')
        assert on.all_text_contents() == ([current] if current else []), f"{path}: current tab"
        overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
        assert overflow <= 1, f"{path} at {width}px: page scrolls sideways by {overflow}px"
        page.wait_for_timeout(250)
        page.screenshot(path=str(SCREENS / f"front-{name}-{width}-{motion}.png"))
    assert errors == [], f"{path} ({motion}): console errors {errors}"


def test_notebook_chapter_urls_are_intact(page):
    chapters = sorted(p.stem for p in DOCS.glob("*.md"))
    assert "index" not in chapters, "docs/index.md would collide with the front page"
    for slug in chapters:
        res = page.request.get(f"/{slug}/")
        assert res.status == 200, f"/{slug}/ is gone"
        assert 'class="md-content"' in res.text(), f"/{slug}/ is no longer a Material page"
    notebook = page.request.get("/notebook/").text()
    for slug in chapters:
        if slug != "notebook":
            assert f'href="../{slug}/"' in notebook, f"/notebook/ no longer lists {slug}"


# ---------------------------------------------------------------- Home

def test_home_skips_the_opening_for_intro_0_and_reduced_motion(page):
    page.goto("/?intro=0")
    assert page.evaluate("document.documentElement.dataset.intro") == "off"
    assert not page.locator("#opening").is_visible()
    page.emulate_media(reduced_motion="reduce")
    page.goto("/")
    assert page.evaluate("document.documentElement.dataset.intro") == "off"
    assert not page.locator("#opening").is_visible()


def test_home_deep_link_lands_on_the_den(page):
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto("/#den")
    page.wait_for_function("Math.abs(document.getElementById('den').getBoundingClientRect().top) < 2",
                           timeout=20000)


def test_home_doors(page):
    page.goto("/?intro=0")
    doors = page.locator("#doors > a.door")
    assert doors.count() == 3
    assert [doors.nth(i).get_attribute("href") for i in range(3)] == ["vision/", "hardware/", "software/"]
    assert page.locator("#doors .door__label").all_text_contents() == NAV


def test_home_shows_the_load_error_copy_when_scans_are_unpublished(page):
    manifest = json.loads((SITE_ASSETS / "large-assets.json").read_text(encoding="utf-8"))
    for c in manifest["clouds"].values():
        c["present"] = False
    manifest["den"]["present"] = False
    page.route("**/assets/site/large-assets.json",
               lambda route: route.fulfill(status=200, content_type="application/json", body=json.dumps(manifest)))
    requested = []
    page.on("request", lambda r: requested.append(r.url) if r.url.endswith(".bin") else None)
    errors = _collect_errors(page)
    page.goto("/")
    page.wait_for_function(
        "document.querySelector('.opening__hint').textContent === 'Scan unavailable · scroll for the overview'",
        timeout=20000)
    page.wait_for_function("document.querySelector('.hud__clock').textContent === 'Scan unavailable'",
                           timeout=20000)
    assert requested == [], f"unpublished scans were requested: {requested}"
    assert errors == []


# ---------------------------------------------------------------- Vision

def test_vision_films_load_lazily(page):
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto("/vision/")
    films = page.locator("video[data-film]")
    assert films.count() == 4
    assert all(films.nth(i).get_attribute("preload") in ("none", "auto") for i in range(4))
    page.wait_for_function("document.querySelector('video[data-film=carpet]').getAttribute('src')")
    assert page.locator('video[data-film="wood"]').get_attribute("src") is None, "far film loaded early"
    page.locator("#film-wood").scroll_into_view_if_needed()
    page.wait_for_function("document.querySelector('video[data-film=wood]').getAttribute('src')")


def test_vision_reduced_motion_never_autoplays(page):
    page.emulate_media(reduced_motion="reduce")
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto("/vision/")
    page.wait_for_timeout(1200)
    assert page.evaluate("[...document.querySelectorAll('video[data-film]')].every(v => v.paused)")


def test_vision_sweep_flips_text_on_lit_fields(page):
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto("/vision/")
    page.evaluate("window.scrollTo(0, document.getElementById('flows').getBoundingClientRect().top + scrollY - 60)")
    page.wait_for_function("document.querySelectorAll('[data-lit]').length > 0", timeout=5000)
    nested = page.evaluate("[...document.querySelectorAll('[data-lit]')].filter(el => el.parentElement.closest('[data-lit]')).length")
    assert nested == 0, "an element and its ancestor were both inverted"
    pre = page.evaluate("[...document.querySelectorAll('[data-lit] pre')].map(p => p.style.filter)")
    assert all("invert" in f for f in pre), "code blocks must cancel the flip and stay dark"


# ---------------------------------------------------------------- Hardware

def test_hardware_board_controls(page):
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto("/hardware/")
    page.wait_for_selector('#el-pcb[data-state="ready"]', timeout=20000)
    flip = page.locator('[data-board="flip"]')
    assert flip.text_content() == "Show back"
    flip.click()
    assert page.evaluate("window.elPcb.getState().face") == "B"
    assert flip.text_content() == "Show front"
    refs = page.locator(".hw-list__refs .el-pcb-ref")
    assert refs.all_text_contents() == ["U1", "J2", "J8", "J9", "J12", "J13"]


def test_hardware_runbook_links_resolve(page):
    page.goto("/hardware/")
    hrefs = page.eval_on_selector_all(".runbook", "els => els.map(a => a.href)")
    assert len(hrefs) == 12
    for href in hrefs:
        assert page.request.get(href).status == 200, href


# ---------------------------------------------------------------- Software

REPOS = [
    "https://github.com/hooterjackson/HomeApp",
    "https://github.com/hooterjackson/engineered-lighting-card",
    "https://github.com/hooterjackson/gimbal-bench",
    "https://github.com/hooterjackson/engineered-lighting-site",
]


def test_software_keeps_its_honesty_rules(page):
    page.goto("/software/")
    assert page.locator("main section.sw-sec").first.get_attribute("id") == "today", \
        "Running today must come first after the introduction"
    assert page.eval_on_selector_all(".repos a", "els => els.map(a => a.href)") == REPOS
    assert "Private" in page.locator(".repos li").nth(2).text_content()
    marks = set(page.locator(".mark").all_text_contents())
    assert marks <= MARKS, f"unexpected status words: {marks - MARKS}"
    assert page.locator(".step .mark").all_text_contents() == [
        "Works today"] + ["Partly built"] * 5 + ["Not built yet", "Partly built"]
    assert page.locator('[data-privacy="private"] img').count() == 0, "private drawing published"
    assert page.locator('a[href*="/software/architecture"]').count() == 0, "architecture page is not hosted"
    drawings = page.locator(".diagram img")
    assert drawings.count() >= 1
    for i in range(drawings.count()):
        drawings.nth(i).scroll_into_view_if_needed()
        drawings.nth(i).evaluate("img => img.complete || new Promise(r => img.onload = img.onerror = r)")
        assert drawings.nth(i).evaluate("img => img.naturalWidth") > 0, "a published drawing is missing"


# ---------------------------------------------------------------- guards

def test_no_prototype_files_or_private_links_ship():
    assert SITE.is_dir()
    shipped = [p for p in SITE.rglob("*") if p.is_file()]
    bad = [p for p in shipped if p.name.endswith(".dc.html") or p.name in ("support.js", "image-slot.js")]
    assert bad == [], f"design prototypes in the build: {bad}"
    front = [SITE / "index.html"] + [SITE / d / "index.html" for d in ("vision", "hardware", "software")]
    front += [p for p in (SITE / "assets" / "site").rglob("*") if p.suffix in (".html", ".js", ".css", ".json")]
    for p in front:
        text = p.read_text(encoding="utf-8", errors="ignore")
        assert "claude.ai" not in text, f"{p} links claude.ai"
        # The owner's rule: the apartment's place name never appears on the site.
        for place in ("Echo Park", "Los Angeles"):
            assert place not in text, f"{p} names {place}"


def test_large_asset_manifest_matches_the_files():
    manifest = json.loads((SITE_ASSETS / "large-assets.json").read_text(encoding="utf-8"))
    entries = [(c["present"], part["path"], part["bytes"])
               for c in manifest["clouds"].values() for part in c["parts"]]
    entries.append((manifest["den"]["present"], manifest["den"]["path"], manifest["den"]["bytes"]))
    for film in manifest["films"]:
        entries += [(film["present"], film["video"], None), (film["present"], film["poster"], None)]
    for present, rel, size in entries:
        f = SITE_ASSETS / rel
        assert f.exists() == present, f"{rel}: manifest says present={present}"
        if present and size is not None:
            assert f.stat().st_size == size, f"{rel}: {f.stat().st_size} bytes, manifest says {size}"
    vision = (DOCS / "vision" / "index.html").read_text(encoding="utf-8")
    for film in manifest["films"]:
        assert f'"../assets/site/{film["video"]}"' in vision
