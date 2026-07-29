# Build Brief · engineering.engineered.lighting

*Paste this into Claude Code (plan mode) from the folder containing the 7 series docs + wiring SVGs/PNGs. It contains everything needed to plan and build the site.*

## Goal

Turn the Engineered Lighting prototype series (7 markdown docs + 4 wiring diagrams, in this folder) into a static instruction-manual website hosted at **engineering.engineered.lighting**. It should read like a book: landing page → chapters → next/prev, with search. Adding a future doc must be as simple as dropping a markdown file in a folder.

## Stack (decided — don't relitigate unless something breaks)

- **MkDocs + Material theme** (`pip install mkdocs-material`). Python-only toolchain, one `mkdocs.yml`.
- Auto page discovery: use filename-prefix ordering (`01-…` … `07-…`) with either explicit `nav:` or the `mkdocs-awesome-pages` plugin so a new `08-whatever.md` becomes a page without editing config.
- Deploy: **GitHub Pages** via the standard `mkdocs gh-deploy` GitHub Action (or Cloudflare Pages if the domain's DNS is on Cloudflare — builder's choice, prefer whichever matches where `engineered.lighting`'s DNS lives).
- Custom domain: `CNAME` file containing `engineering.engineered.lighting` + a DNS CNAME record `engineering` → the pages host. HTTPS via the host's cert automation.

## Site structure

```
docs/
  index.md                  ← LANDING PAGE (see spec below)
  bom-checklist.md          ← INTERACTIVE CHECKLIST (see spec below)
  01-how-we-got-here.md     ← from robotic-spotlight-gimbal-research.md
  02-choosing-the-motors.md ← from robotic-spotlight-micro-gimbal-research.md
  03-build-the-gimbal.md    ← from gimbal-breadboard-prototype-plan.md
  04-full-fixture-bench.md  ← from combined-bench-prototype-plan.md
  05-teach-it-to-aim.md     ← from spatial-intelligence-architecture.md
  06-message-contract.md    ← from system-message-contract.md
  07-building-the-software.md ← from software-build-plan.md
  assets/                   ← the 4 wiring-*.svg (+ .png fallbacks)
mkdocs.yml
```

Porting rules: keep doc content byte-faithful except (a) fix image paths to `assets/`, (b) convert each doc's "The series:" nav blockquote into nothing (the site sidebar replaces it), (c) the per-doc BoM tables STAY in the docs *and* feed the checklist page. Material's right-hand TOC turns each doc's `##` stages into chapter navigation automatically — do not split docs into multiple pages in v1.

## Landing page spec (index.md)

1. Hero: "Engineered Lighting · Engineering Notebook" + one-paragraph vision (source: Doc 1's "The project, in one paragraph" — reuse verbatim).
2. "What we're building toward" — 3 short cards: the silent robotic spotlight (Docs 1–4), the aiming intelligence (Doc 5), the system architecture (Docs 6–7).
3. Prominent link card → **BoM checklist**.
4. The document map table from Doc 1 (7 rows, with budget column), each row linking to its page.
5. Status line: total prototype budget ~$475–850/room; current phase: parts ordering / bench build.

## Interactive BoM checklist spec (bom-checklist.md)

- One page, three collapsible sections mirroring the three BoMs: **Doc 3 · Gimbal (~$185–290)**, **Doc 4 · LED bench (~$170–240)**, **Doc 5 · Per-room perception (~$120–320)**. Source the item rows from each doc's BoM table — item name, qty, est. price, source, and the one-line purpose note.
- Each item = a real checkbox. Persist state in `localStorage` (key: `el-bom-v1`, per-item stable IDs like `d3-motors`). Survives reload; no backend.
- Progress indicators: per-section "6/12 · ~$142 checked" and a global progress bar. A "reset section" and "copy unchecked as shopping list" button (copies plain text to clipboard).
- Implementation: plain HTML/JS inside the markdown page (Material allows raw HTML; put the ~80 lines of JS in `docs/js/checklist.js` via `extra_javascript`). No framework.
- Honest note at top: prices were verified July 2026 — re-check live prices when ordering (this rule is *in the docs* — surface it here).

## Acceptance checklist

- [ ] `mkdocs serve` renders all 7 chapters with diagrams visible, sidebar ordered 01→07, search working
- [ ] Landing page reads as a coherent front door; every link resolves
- [ ] Checklist: check 3 items → reload → still checked; reset works; progress math correct
- [ ] New-doc test: add `08-test.md` with a title → appears in nav without touching `mkdocs.yml`
- [ ] Deployed to the pages host; `engineering.engineered.lighting` resolves with HTTPS (DNS step may be manual — print the exact record to add)
- [ ] Mobile: chapters and checklist usable on a phone at the workbench

## Nice-to-haves (only after acceptance passes)

Dark mode toggle (Material built-in — just enable), a "print chapter" CSS tweak for bench printouts, per-chapter "Done when" checkboxes using the same localStorage pattern, and an RSS-less "changelog" page appended per session of edits.
