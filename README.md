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

Adding a chapter: drop `08-whatever.md` (numeric prefix, H1 title, optional
`title:` front matter for the sidebar) into `docs/` — the nav picks it up
automatically; no config edits needed.

Chapter `- [ ]` checklists are interactive on the site (state in the
reader's browser, keyed by page slug + item position) — reordering or
inserting checklist items in a doc shifts readers' saved checkmarks.
