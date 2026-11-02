# Engineered Lighting · Engineering Notebook

The prototype series for the Engineered Lighting robotic spotlight — research,
bench builds, perception stack, and software — published as a book-style site.

**Live site:** <https://hooterjackson.github.io/engineered-lighting-site/>
(moving to <https://engineering.engineered.lighting> once DNS cuts over)

## Working on the site

```bash
pip install -r requirements-site.txt
mkdocs serve
```

Every push to `main` builds with `--strict` and deploys to GitHub Pages via
[`.github/workflows/publish.yml`](.github/workflows/publish.yml).

Adding a chapter: drop `09-whatever.md` (numeric prefix, H1 title, optional
`title:` front matter for the sidebar) into `docs/` — the nav picks it up
automatically; no config edits needed. A chapter that belongs in a titled
sidebar group is listed explicitly in `docs/.pages` above its `...` catch-all;
anything unlisted lands after the last group.

## The front pages

The site root and `/vision/`, `/hardware/` and `/software/` are standalone static
pages (`docs/index.html`, `docs/<page>/index.html`) built from the owner's Claude
Design handoff. MkDocs copies them through untouched, so Material's CSS and JS
never load on them. The notebook landing that used to be `/` is now `/notebook/`.

Their shared assets live in `docs/assets/site/`: `site.css` (tokens, nav, footer),
one stylesheet per page, `js/`, self-hosted IBM Plex and three.js r160, and the
large binaries listed in `large-assets.json` (apartment point clouds, the den
scan, the Vision films). A binary marked `"present": false` is never requested;
the page shows its load-error copy instead. `tools/site/den_scan.py` rebuilds the
den scan from its source pack. Images the owner has yet to supply are marked in
the HTML with `data-slot` (diagram slots also carry `data-privacy`); replace a slot
with an `<img>` once the image is approved for publication.

Chapter `- [ ]` checklists are interactive on the site (state in the
reader's browser, keyed by page slug + item position) — reordering or
inserting checklist items in a doc shifts readers' saved checkmarks.
