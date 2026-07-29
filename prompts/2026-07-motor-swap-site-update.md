# Prompt · Motor swap (RMD-L-4005 → 5005) + outstanding review fixes

*Paste into Claude Code in plan mode from this repo.*

Read this entire brief, then propose a plan and wait for approval before
editing. This update has one big change (motor part swap) plus a sweep of
outstanding review fixes. Work idempotently: several fixes from a previous
feedback round may already be applied — verify each, apply only what's
missing.

════════════════════════════════════════════════════════════════════
PART A — MOTOR CHANGE: RMD-L-4005 → RMD-L-5005 (sitewide)
════════════════════════════════════════════════════════════════════

CONTEXT: The RMD-L-4005-100-C is sold out at all retail channels
(temporarily — active product line, not discontinued). Its in-stock,
same-family sibling RMD-L-5005 is now the build's motor. Same protocol,
same wiring, same everything in the build instructions — this is a part
number + price + dimensions change, not an engineering change.

SOURCE-OF-TRUTH FACTS (use these exactly; don't re-derive):
- Part: MyActuator RMD-L-5005 (order as RMD-L-5005-100-C — CAN variant;
  the -R twin is RS485). Confirmed in stock at Dings Motion USA
  (https://www.dingsmotionusa.com/rmd-l-5005), $107.50 each,
  "Contact us for quantity pricing."
- Specs: Ø49 mm × ~24 mm body (flag the ~ — exact drawing from
  myactuator.com L-series downloads), 92 g, 42 N·cm peak torque
  (= 4.8× the 8.83 N·cm unbalanced worst case; the balanced case is
  ~28× covered). Identical to the 4005 in: 18-bit absolute single-turn
  encoder, 12–24 V, CAN @ 1 Mbps, Motion Protocol V4.2, direct drive,
  0xA4/0x92/0x79/0x63-64 command set, 4-pin port (VCC/GND/CANL/CANH).
- Quantity: 2 required (pan + tilt). Recommend ordering 3 — the third is
  a spare/permanent bench-dev unit, justified by this exact stockout
  episode and by Phase 4's future second fixture. Purchase notes to keep:
  explicitly request the -C variant, ask for mating cables (one per motor
  + spare), keep the protocol PDF that ships in the box.

THE HISTORY-VS-FORWARD RULE (important editorial principle):
- FORWARD-LOOKING content (BoMs, build steps, checklist, purchase links,
  diagrams, budgets) → becomes 5005 everywhere.
- HISTORICAL content (Doc 2's decision journey, its comparison tables,
  "why the 4005 won") → STAYS as written; the 4005 was the decision and
  the record shouldn't be rewritten. The bridge between them is a new
  addendum (below). Doc 1's lessons don't mention the part number — leave.

EDITS:
A1. Doc 3 BoM row 1: part → RMD-L-5005-100-C; qty "2 (+1 spare
    recommended — see note)"; Est. "$215 for 2 / $322.50 for 3";
    Where → Dings Motion USA (link the URL); rewrite the note: keep the
    -C-variant instruction, mating-cable ask, protocol-PDF-authority
    line; replace "65 g puck" with "92 g, Ø49 mm puck"; add one line on
    why 3 ("this motor family sells out episodically; the third unit is
    the permanent bench unit and feeds the future second fixture").
A2. Doc 3 header + BoM title: recompute the total (non-motor items are
    unchanged; motors went from $60–120 to $215 fixed for qty 2). Compute
    the new range yourself from the table, state it, and PROPAGATE the
    same number to: Home's doc-map row 3, Doc 1's doc-map row 3, the BoM
    checklist Doc-3 section header, and the sitewide "$475–850 end to
    end" total (Home hero, Home footer line, Doc 1 reading-paths line,
    anywhere else grep finds it). All instances must match to the dollar.
A3. Doc 3 stage 7: "design against the L-4005 STEP files" → L-5005; the
    OpenSCAD note's example dimensions reference the flange drawing —
    make it point at the L-5005 drawing.
A4. Doc 2: add an "Availability addendum (July 2026)" box directly under
    its purchase table: the 4005 sold out at retail; the build moved to
    the in-stock sibling RMD-L-5005 ($107.50, Dings) — a zero-code swap.
    Include this sibling table (keep the starred-estimate flags and the
    4015 caveat verbatim):

    | | L-4005 | L-4010 | L-4015 | L-5005 |
    |---|---|---|---|---|
    | Diameter | 39.6 mm | 39.6 mm | 39.6 mm | ~49 mm |
    | Body length | 23 mm | ~28 mm* | ~33 mm* | ~24 mm |
    | Mass | 65 g | ~85 g* | ~105 g* | 92 g |
    | Peak torque | 25 N·cm | 33 N·cm | ~45–50 N·cm* | 42 N·cm |
    | Everything else | identical — same encoder, voltage, CAN/RS485, V4.2 protocol, direct drive | | | |

    *Estimates — the 4015's spec sheet is published only as an image;
    confirm exact figures with Dings.*

    Explain the naming (L-DDSS: diameter class + stator stack height) and
    the pick logic in two sentences: torque doesn't differentiate (all
    ≥2.8× margin); geometry does — the 5005 keeps the slim ~24 mm pancake
    profile and pays 9 mm of diameter, which the fixture bay absorbs,
    while 4010/4015 grow in body length, the dimension the yoke and
    fixture depth care about. Preference order 5005 ≥ 4010 > 4015.
    Update Doc 2's purchase-table price cell to $107.50/axis (Dings) and
    fix any remaining "$25–60/axis" or "$30–60/axis" instances.
A5. Permanent alternates note (keep even though stock resolved — it's
    insurance): in Doc 3's BoM row-1 note or directly under the BoM, one
    line: "Family sold out again? CubeMars GL40 II ($134, DigiKey,
    direct-drive, CAN) is the buy-today alternative at the cost of a
    protocol port; M5Stack RollerCAN ($44) is the recommended dev bridge
    while waiting." Link both.
A6. Diagrams (SVG text edits in docs/assets/): in wiring-gimbal-can.svg,
    both motor box titles "RMD-L-4005 · Motor A/B" → "RMD-L-5005"; in
    wiring-full-bench-overview.svg, "2× RMD-L-4005 smart servos" →
    "2× RMD-L-5005 smart servos". Change ONLY the text nodes — no
    geometry edits. Render/screenshot both after editing and eyeball that
    the labels didn't overflow their boxes.
A7. BoM checklist page: update the motor item (name, qty note, price,
    Dings link), recompute the Doc-3 section total and the page's grand
    total, and confirm the localStorage item ID for that row is UNCHANGED
    (users' checked state must survive the rename — if the ID was derived
    from the part name, pin it to the old ID explicitly).
A8. Sweep: grep the whole docs tree for "4005" after all edits. Every
    remaining hit must be in Doc 2's historical sections or the addendum
    table — list the final hits in your report so I can confirm.

════════════════════════════════════════════════════════════════════
PART B — OUTSTANDING REVIEW FIXES (verify-then-apply; may be partially done)
════════════════════════════════════════════════════════════════════

B1. Valent X sourcing (Doc 4 BoM + checklist): the one non-click-to-buy
    item. Check Diode LED's dealer locator for 1–2 US online dealers that
    sell single Valent X spools retail and name them with links; if none
    sell online, add a pre-vetted Amazon-buyable high-CRI tunable-white
    substitute row (24 V, 3-channel W/N/C, ≥90 CRI) clearly marked
    "substitute — spec-check before committing the fixture design".
B2. Optional posture line on Home hero: "This is our internal engineering
    notebook, published openly — hardware assumptions (a CUDA GPU box for
    Docs 5–7, an existing Home Assistant install) are ours."
B3. Doc 1 document map: replace with Home's version (linked titles, no
    .md filenames, no "(this file)"). Hyperlink every bare digit in the
    Reading-paths line; copy that line to Home if not already there.
B4. Doc 5: tag each BoM row with the phase it serves (PoE switch + night
    camera are NOT Phase 0); add agent-prompt blocks to Phases 2–5 or an
    explicit "greenfield — no recipe yet; work it with your agent from
    the chapter text" marker.
B5. Doc 3 template parity: add Further Reading (isaac879 Pan-Tilt-Mount,
    Visaging ESP32-Gimbal, RMD protocol PDF, myactuator downloads) and a
    short risk register (hold-whine at sealed loop, protocol version
    drift, single-turn encoder needs hard stops, supply volatility).
    VERIFY Doc 3's software stages carry the same 🤖 prompt blocks as
    Docs 4/5/7 and that the AI-agent page is in nav everywhere (a prior
    reviewer saw it missing; likely a fetch artifact — confirm in source).
B6. Link pass: BoM checklist section headers → their chapters; deep-link
    "Doc 6 §1" (Doc 3), "Doc 5 Phase 0" (Docs 4, 7), "Doc 5 Phase 1"
    (Doc 6); make purchase sources and Further-Reading citations real
    hyperlinks sitewide; prev/next chain symmetric around the AI page.
B7. Hygiene: Doc 6 — delete "since 'sliders' caused confusion in review"
    (keep the clarification); Doc 4 Concepts — add "(external design doc,
    not on this site)" to the unqualified "fixture brief" mention; Home —
    add the "July 2026" dateline; Doc 5 FCC item — rephrase "As of July
    2026…"; Doc 5 stereo row — move $359/$579 into the Est. column.
B8. Mobile: collapse ASCII wiring blocks into <details> ("plain-text
    version") with the SVGs primary; check the Doc 4 channel table
    doesn't force horizontal scroll on phones.

════════════════════════════════════════════════════════════════════
PART C — VERIFICATION (before calling it done)
════════════════════════════════════════════════════════════════════
C1. Budget-sum audit: every occurrence of the Doc-3 total and the
    end-to-end total across Home, Doc 1, Doc 3, checklist — identical
    values; show me the grep proving it.
C2. The "4005" grep report from A8.
C3. mkdocs build clean; existing CI (link/persistence/add-a-doc tests)
    green; checklist localStorage state survives the motor rename (test
    it in headless: pre-seed the old key, load, assert still checked).
C4. Screenshot the two edited SVGs, the updated Doc 3 BoM, the checklist
    motor row, and Home's updated numbers — attach to your report.
C5. Report format: per-item DONE / ALREADY-DONE / SKIPPED-because, plus
    the two grep outputs and screenshots.
