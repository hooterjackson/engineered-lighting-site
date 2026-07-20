# DESIGN — engineering.engineered.lighting

Visual identity for the Engineered Lighting engineering notebook (MkDocs Material).
One idea drives everything: **a dark workshop where exactly the right things are lit.**
The interface is the room; the content is what the light falls on.

Files: `mkdocs.yml` (palette/font/logo config) · `docs/stylesheets/extra.css` (tokens
at the top, everything else consumes them) · `docs/assets/el-logo.svg` + `el-favicon.svg`
· hero markup in `docs/index.md`. No theme fork, no JS, no build-chain additions.

---

## 1 · Color tokens

All ratios are WCAG contrast, computed against the surfaces actually used. Everything
interactive or textual meets AA (4.5:1); most of it clears AAA.

### Ground — black ramp

| Token | Hex | Role |
|---|---|---|
| `--el-bg-0` | `#000000` | Page ground, header, drawer |
| `--el-bg-1` | `#0F0D0B` | Raised: admonitions, BoM panels, progress housing |
| `--el-bg-2` | `#17140F` | Highest: kbd, focused search |
| `--el-bg-deep` | `#0B0A08` | Code blocks: a whisper above black |

True black, per the company's darkness-first principle: light is an additive
medium and only exists because of the dark behind it. The warmth lives entirely
in what's *lit* — the ink and the amber — while surface raises keep a faint warm
cast (R > G > B) so panels read as tungsten-touched, never blue-gray slate.
Panels raise by 1–2% lightness with a hairline — no drop-shadows anywhere,
because a shadow implies a light source above the interface, and here light
comes from within.

**Do:** raise a surface with `--el-bg-1` + `--el-line`. **Don't:** `box-shadow`,
blue-tinted grays, or a lifted "app background" — the page itself stays `#000`.

### Ink — warm off-whites

| Token | Hex | Role | On bg-0 |
|---|---|---|---|
| `--el-ink` | `#F2EEE6` | Headings, primary text | 18.1:1 |
| `--el-ink-2` | `#C9C1B2` | Body secondary, nav items | 11.8:1 |
| `--el-ink-3` | `#9C937F` | Captions, table headers, meta | 6.9:1 (6.3 on bg-1) |
| `--el-ink-4` | `#6E6759` | Faint: ¶ marks, footer legal — decorative/large only | 3.8:1 |

Text is 2700 K paper-white, not `#FFFFFF` — full white is reserved for nothing, so
the brightest thing on any page is always an intentional emphasis, never a default.
Hierarchy comes from this ramp plus weight; headings are never colored.

**Do:** dim to de-emphasize. **Don't:** use `--el-ink-4` for any text that must be read
(it's below AA at body sizes — it exists for glyphs and decoration).

### Accent — the tunable-white range, nothing else

| Token | Hex | Role | Contrast |
|---|---|---|---|
| `--el-amber` | `#E2A24C` | Links, active nav, progress, checks (~1800 K) | 9.5:1 bg-0 · 8.9:1 bg-1 |
| `--el-amber-hi` | `#EFBC77` | Hover state | 12.1:1 |
| `--el-amber-soft` | `rgba(226,162,76,.14)` | Tints, checked-box fill | — |
| `--el-ice` | `#D6E5F4` | Emphasis only: focus rings, selection, `mark`, live state (~6500 K) | 16.4:1 |

The site's only two colors are the two ends of the product's tunable-white spectrum.
Amber is *interactive* — if it glows warm, you can act on it. Ice is *attention* —
focus rings, selection, highlights; it never marks a link, so the two channels stay
unambiguous. Charcoal text on an amber button: 8.5:1. No red, no green, no brand blue;
cautionary states (traps) use amber + iconography, informational states use ice.

**Do:** amber = clickable, ice = look-here. **Don't:** amber behind body text, colored
headings, any saturated hue.

### The one light surface

| Token | Hex | Role |
|---|---|---|
| `--el-paper` | `#FFFFFF` | Wiring-diagram sheets |

The wiring SVGs have hardcoded white backgrounds and color-coded wires (+12 V red,
CAN-H orange…) that must not be inverted or hue-rotated — the colors are electrical
semantics. Decision: **keep them white and frame them as lit sheets** — full-bleed
white card, hairline frame, generous padding, a faint halo, mono caption below. A
schematic pinned under a downlight is exactly this brand; a CSS-inverted schematic is
a wiring hazard. (Print drops the framing and runs them full-width.)

## 2 · Typography

One hosted family: **IBM Plex Sans, weights 400 + 600** (the company's brand face;
`font: false` in mkdocs.yml stops Roboto, extra.css imports the two weights). Code and
all "chrome" labels use the **system mono stack** (`ui-monospace, SF Mono, Menlo…`) —
zero extra font weight on a workbench phone connection.

Scale (Material's base: 1rem = 20px; body = 0.8rem = 16px):

| Style | Spec | Use |
|---|---|---|
| Display | clamp(34–47px) / 600 / −0.02em / 1.08 | Landing hero only |
| H1 | 1.7em / 600 / −0.015em / 1.15 | Page titles |
| H2 | 1.3em / 600 / −0.01em | Sections (2.4em space above) |
| H3 | 1.08em / 600 | Sub-sections |
| Body | 16px / 400 / 1.65 line-height | Prose, max-width 42em ≈ 70ch |
| Chrome | mono 10–11px / 0.12em tracking / UPPERCASE | Table headers, admonition titles, captions, meta chips, prev/next labels |

Prose is capped at ~70ch; **tables, code blocks, and diagrams deliberately escape the
measure** and run the full column — BoMs are dense and diagrams want width. The mono
uppercase "chrome" voice is how the product labels itself (telemetry style); on this
site it marks *apparatus* (labels, captions, controls) as distinct from *writing*.
Headings differ by size/weight only — never color.

**Do:** mono-uppercase for labels ≤ a few words. **Don't:** uppercase whole sentences,
a third weight, Title Case.

## 3 · Spacing, radius, borders, motion

- **Spacing:** 4px grid (`--el-sp-*`). Section headings carry 2.4em of air above —
  rhythm comes from space, not rules.
- **Radius:** `0` for every panel, table, code block, button (architectural), `999px`
  only for small floating chips (meta pills, "optional" badges, back-to-top). Nothing
  in between — no 8px "app" corners.
- **Borders:** hairlines `rgba(242,238,230,.10)` and `.20` strong. Depth = border
  + surface step, never shadow. The only glows: the hero source point and the
  faint halo behind diagram sheets.
- **Motion:** 120ms hovers, 220ms fades, `cubic-bezier(.65,0,.35,1)` — damped, no
  bounce, and `prefers-reduced-motion` collapses all of it.

## 4 · The cone-of-light motif

A single radial gradient — `radial-gradient(58% 46% at 50% 0%, warm 15% → transparent)`
— with a 3px source point at its apex. It appears on the **landing hero only** (plus a
"cooling filament" gradient for `hr` dividers). It is never placed behind body text,
never repeated per-section, never animated. One room, one downlight.

## 5 · Component decisions

- **Header:** same color as the page, hairline underline — "no chrome." Search is a
  hairline slot, not a tinted pill.
- **Sidebar:** the repeated site title is hidden on desktop (the header carries it);
  chapter numbers in the existing "3 · Title" form render with tabular numerals; the
  active page is amber @ 600. (Splitting numbers into styled boxes would need template
  or JS changes — see §7.)
- **Admonitions:** quiet panels — hairline border, `--el-bg-1` fill, mono-uppercase
  title, small tinted icon. Informational family = ice; cautionary = amber. Two custom
  types ship in CSS: `!!! trap "…"` (hazard triangle) and `!!! rules "…"`
  (8-point light burst, for the golden rules). No fat left accent bars.
- **BoM checklist:** sections are panels; per-section progress is a mono amber label
  right-aligned in the summary row; the global bar's fill runs **amber → warm white as
  it completes** (the tunable range as a progress metaphor); checkboxes are custom
  15px squares — amber check, ice focus ring, fully keyboard-operable (native inputs,
  visible `:focus-visible`). Buttons are quiet mono-uppercase hairline buttons; the
  one filled (amber) button on the site is the landing CTA.
- **Tables:** hairline horizontal rules only — no zebra, no verticals, no outer box;
  mono-uppercase headers; tabular numerals; a 3%-alpha row hover for tracking dense
  BoM rows.
- **Code:** recessed `--el-bg-deep` + hairline; restrained warm/ice syntax palette
  (strings amber-family, keywords ice-family, comments 5.1:1 — all AA).
- **Footer prev/next:** mono PREVIOUS/NEXT eyebrow + plain title; amber on hover.
- **Print = the light mode:** white ground, warm-black ink, dark-amber links (5.9:1),
  nav/header/hero hidden, diagrams full-width and unframed, page-break guards on
  tables/code/admonitions.

## 6 · Logo

A downlight in section: source point, widening beam, amber pool on the ground —
the product's whole promise in three shapes. `el-logo.svg` (transparent, for the dark
header) and `el-favicon.svg` (on a charcoal tile, bolder geometry for 16px). Both pure
SVG, no text; the wordmark stays typographic.

## 7 · Verified constraints & flagged conflicts

**Verified:** 21 token pairs contrast-checked programmatically — every text/interactive
pair ≥ AA on its real surface (amber on ground 9.5:1; table above; script in review notes). Focus visible
everywhere (2px ice ring, 2px offset). Checklist keyboard-operable. One hosted family,
two weights; no decoration images — gradients only. Mobile: drawer, 44px+ targets on
nav/summary rows, tables scroll within their panels.

**Conflicts with Material's system, and the calls made:**

1. **Light mode:** not shipped. Rationale: print styles already deliver the "paper"
   context; a second screen scheme doubles QA surface and dilutes the identity. The
   tokens are scheme-scoped, so a `paper` scheme can be added later as a second
   `palette:` entry without touching components.
2. **Custom 404** would require a template override (`overrides/404.html`) — that's a
   theme fork by this brief's rules, so it's out of scope; the motif CSS (`.el-hero`)
   is 404-ready if you later allow a one-file override.
3. **Chapter numbers as separate styled elements** in the sidebar can't be done in
   CSS alone (nav labels are plain text); done typographically instead.
4. **`trap`/`rules` callouts** are styled in CSS, but the *content* currently writes
   traps as bold "If stuck:" paragraphs — adopting them means small authoring edits
   (`!!! trap "If stuck — no reply"`). The after-preview of Doc 3 shows one converted
   as a demonstration; no chapter content was otherwise touched.
5. **Scheme base:** built on `scheme: slate` with every visible color overridden,
   rather than a named custom scheme — a custom scheme name drops Material's derived
   defaults and risks unthemed corners (search modal, tooltips). Slate-as-base keeps
   those sane if a Material update adds new surfaces.
