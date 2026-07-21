---
title: 5 · Teach It to Aim
description: "The perception stack: cameras, ground-plane tracking, beam self-calibration, coordination, safety, and the phased roadmap."
---

# Doc 5 · Teach It to Aim — Spatial Intelligence for Coordinated Spotlights

**Engineered Lighting prototype series · July 2026**
Your V-JEPA model answers *what is happening* (reading, cooking, movie). This document answers *where it's happening and what pan/tilt angles put light there* — for multiple fixtures, coordinating. Constraints held: all video local; central RTX 6000 box runs perception; one camera per room; assisted room scan OK; HA/MQTT ecosystem; fixture form factor deprioritized (floor lamps fine).

> **Hardware assumption, stated plainly:** the phases here run on the already-owned RTX 6000 Blackwell workstation. That card matters for the *full* vision (many rooms + V-JEPA); Phase 0's single-camera tracking runs fine on any recent CUDA GPU with ~12 GB+, so the first demo doesn't wait on big hardware.

## Bill of Materials — per room + one-time, ~$120–320/room

| # | Part | Qty | Est. | Where | Notes |
|---|---|---|---|---|---|
| 1 | **PoE camera** — standard rooms: Amcrest IP5M-T1179EW-AI-V3 (5 MP, 133° lens) | 1/room | $80 | amcrest.com | The room's eyes: a wide fixed lens covering the whole room from a corner, streaming standard RTSP video the GPU box ingests directly. PoE = one cable carries power and data, and wired video is what keeps a many-camera home stable and lets the camera network run fully internet-isolated |
| 1b | — priority rooms: Loryta/Dahua IPC-T549M-ALED-S3 (full-color night vision) | opt. | $185 | empiretech01.com | Night matters: IR cameras output grayscale, which degrades RGB-trained models |
| 2 | PoE switch (8–16 port) + Cat6 runs | 1/home | $150–400 | Amazon | Put cameras on their own VLAN with **no internet route** — privacy by construction |
| 3 | ChArUco calibration board (print + mount on rigid backing) | 1 | ~$10 | print it (calib.io generator) | For registering each camera to the room scan. Rigid and flat matters |
| 4 | iPhone/iPad Pro with LiDAR (borrow one) + Polycam or Scaniverse app | 1 | free–$ | App Store | One-time room scan, ~1–3 cm accuracy. Use **Space Mode (LiDAR)**, not the auto-floorplan mode |
| 5 | *Optional, later:* one stereo depth camera — Orbbec Gemini 335L ($359) or Luxonis OAK-D Pro PoE ($579) | 0–1 | — | store.orbbec.com, shop.luxonis.com | True per-pixel 3D for the specific rooms where ground-plane geometry runs out (reclined people, heavy clutter) — buy after Tier-0 tracking measurably misses, not before (see "the depth question") |
| — | Already owned | — | — | — | RTX 6000 Blackwell box (runs all perception), the Doc [3](03-build-the-gimbal.md)/[4](04-full-fixture-bench.md) bench rig (the actuator being aimed), Home Assistant + MQTT (the message plumbing) |

## Concepts (plain English)

- **Frames & transforms:** every position lives in some coordinate system ("frame") — the room, a camera, a fixture. A *transform* converts between them. The whole aiming stack is: target in room frame → transform to fixture frame → two angles.
- **Intrinsics / extrinsics:** a camera's *intrinsics* describe its lens (how pixels map to directions); *extrinsics* are where it sits in the room. Calibrate both once, then every pixel becomes a 3D ray.
- **Ground-plane trick (homography):** a person's feet touch the floor, and we know where the floor is. So one ordinary camera gives their 3D position: pixel → ray → intersect floor. This is the finding that deletes depth sensors from the plan.
- **Keypoints / pose:** models that find body joints (ankles, wrists, head) in an image. Body-scale keypoints work across a room; *finger*-scale does not (hands are 20–40 pixels at 4–8 m — too small, verified 2026 research).
- **Tracking ID:** detection says "a person is here *this frame*"; tracking says "it's the *same* person as last frame." Needed so beams follow individuals, not flicker between people.
- **Open-vocabulary detection:** models you query with words ("book") instead of fixed class lists. Used to *confirm* a book is present, not to measure it precisely.
- **Latency vs. update rate:** latency = how stale each measurement is; update rate = how often they arrive. Smooth following needs ~15–30 updates/second *and* prediction to cover the staleness (below).
- **One Euro filter:** the standard smoothing trick for noisy tracking — heavy smoothing when still (kills jitter), light smoothing when moving (kills lag). Cheap, three lines of code.
- **Fast path / slow path:** two loops sharing the cameras. Fast: person tracking at 15–30 Hz → aim. Slow: video clips → V-JEPA → "they're reading" (arrives seconds later, changes *policy*, not coordinates). The fast path never waits for the slow one.
- **No-go cone:** a computed exclusion zone around each tracked head that beams must never enter — borrowed from automotive adaptive headlights, which mask glare zones around oncoming drivers in exactly this way.
- **Named tools, one line each:** *YOLO26* — the current fast, standard "find the people in this frame" model. *ByteTrack* — the standard "it's the same person as last frame" ID-keeper. *Frigate* — an open-source camera recorder/reviewer that runs on the GPU box (used for recording and clips, never in the aiming loop). *DeepStream* — NVIDIA's toolkit for running vision models over many camera streams at once (an optional productized shortcut). *go2rtc* — a small program that re-serves camera streams with minimal delay.

---

## 1. What we're building (the six findings)

1. **No stereo needed to start.** Ground-plane localization delivers **4–19 cm** accuracy in room-scale tests (4–13 cm standing, 16–19 cm walking) — comfortably inside the real beam, which the optics research pinned down: the tightest off-the-shelf 3-up optic (Carclo 10507, ~16°) throws a **0.42 m spot at 1.5 m, growing to ~0.85 m at 3 m**. NVIDIA productized this pattern (DeepStream SV3DT/MV3DT, auto-calibration, 645–1,225 FPS aggregate on this GPU class). Seated people (feet unusable): the room model supplies the couch height, torso keypoints supply the rest. Stereo is a targeted later upgrade.
2. **Beam self-calibration is the differentiator.** No commercial system — including $30k zactrack/BlackTrax — auto-calibrates fixtures; all use a manual jog onto known points. But the recipe exists (a 2025 patent describes it; telescope pointing models supply the math with ~170× margin over our 1° need): sweep the beam, let the camera watch where it lands, fit the model. A fixture that calibrates itself in ~2 minutes beats the industry's shipped state of the art. (Patent flag: US 12,190,542.)
3. **The follow-me loop is real but unforgiving.** 100–300 ms end-to-end is achievable only on a bespoke path (camera → own tracker → fixture → CAN; the fixture link is MQTT on the bench, graduating to a direct ESPHome native-API action called via aioesphomeapi in production — one hop, typed floats, spec in [Doc 6](06-message-contract.md) §1). Convenience shortcuts cost *seconds* (Frigate events: 6–10 s; HA automations: documented 4–20 s traps). And **prediction is structural, not polish**: at 300 ms latency a walker moves 42 cm — comparable to the beam's half-width — so the aim point must *lead* the track by the measured latency. Geometry helps too, and for free: the fixed 10507 optic naturally widens with throw (~0.85 m at 3 m), so the beam is at its most forgiving exactly where tracking error and lag are largest; the tight-spot regime only exists at short throw, where tracking is at its best. (No variable-beam hardware needed — if beam-width experimentation matters later, the Carclo optics snap-swap in seconds, and a motorized-zoom path exists: Khatod's 45 mm slide-zoom, 11–45°, at the cost of redesigning to a single-die emitter.)
4. **Fixture speed requirement (computed):** a person passing 1–1.5 m from a fixture's plumb line needs **54–80°/s** pan. [Doc 3](03-build-the-gimbal.md)'s stage 5 measures whether the motors stay silent at those speeds; if not, the coordinator caps indoor slew and lets the beam lag through close passes.
5. **Hands don't work at range — design around them.** The book story: anchor the person from feet/torso, offset to the wrist (body keypoints work at range), confirm "book" with open-vocabulary detection. Same evidence reshapes gestures: **v1 gestures are arm-scale** (raise, wave, hold-out — from body keypoints); finger gestures (pinch, palm shapes) are not feasible from a corner camera. Naive pointing rays err ~28° — fine for "which zone," not for precision (a trained pointing model reaches <2° if ever needed).
6. **The failure modes are about feelings:** never sweep eyes (predictive no-go cones + soft-edged dimming + a hard interlock — tracking loss parks the beam within a deadline); move *legibly* (a small anticipatory "glance" before the main move reads as intentional — HRI-validated); and **suppress motion during movie/settled-reading** — lights that move when people are trying to be still is the documented trust-killer.

## 2. User stories (the problem space)

| ID | Story | Note |
|---|---|---|
| **A — Follow & task** | | |
| A1 | Follow me across the room | The canonical hard story: tracking + smoothing + handoff |
| A2 | Light the surface I'm using (table/board/desk) | Validated demand — $600 task lamps that don't even move |
| A3 | Spotlight the book in my hands | White space: every current solution is worn on the body |
| A4 | Cooking-step lighting (board → stove as activity shifts) | Context-driven; bridges to the DLP recipe story later |
| A5 | Light my face on video calls | Adjacent shipped demand (ring lights, Apple Edge Light) |
| **B — Ambient & idle** | | |
| B1 | Point at wall art when idle | Static target — trivial once calibrated |
| B2 | Plant/decor accents on schedule | Zero live perception needed |
| B3 | Gallery rotation with dwell times | Motion styling matters most here |
| **C — Media & social** | | |
| C1 | Movie mode = *stillness* | Suppression is a feature; movement here is the trust-killer |
| C2 | Light the board-game table when we gather | Group context from the activity model |
| C3 | Party sweeps | The one home for stage-light behavior |
| **D — Utility** | | |
| D1 | 3am path light | Ankle-height, dim, never near eyes |
| D2 | Find-my-keys by pointing light at them | No shipped product does this — needs object memory |
| D3 | Closet/pantry assist | Beam into the space you just opened |
| D4 | Pet play/follow | $20 auto laser toys validate the appetite |
| **E — Interaction** | | |
| E1 | Arm-scale gestures (raise/wave/hold-out), context-armed | Gating evidence: 5.5× fewer false positives; V-JEPA-gated version is novel |
| E2 | Point at a spot to send light there | Coarse zone-selection in v1; precision needs a trained model |
| E3 | Summon / banish the beam | Beckon it over; wave it away |
| **F — Multi-person & multi-fixture** | | |
| F1 | Each person gets their own beam | Research favors this "spatial multiplexing" over preference arbitration |
| F2 | Seamless fixture handoffs while walking | Hysteresis so beams don't ping-pong |
| F3 | Second fixture covers occlusions | Redundancy when line-of-sight breaks |
| F4 | My preferences follow me | Identity via trajectory re-ID; feeds the roadmap's identity layer |
| **G — Trust (gates everything)** | | |
| G1 | Never sweep a beam across eyes | Hard constraint: predictive no-go cones |
| G2 | Fail calm | Tracking loss → park/dim, never hunt |
| G3 | Legible motion | Anticipation micro-moves, context speed caps |
| G4 | Visible "perception off" state | The being-watched objection is the adoption risk |

## 3. The architecture in one picture

```
 PoE cams ──► RTX 6000 box:  go2rtc (low-latency restream)
                              ├─ FAST 15–30 Hz: detect (YOLO26) → track IDs →
                              │   ground-plane 3D → keypoints → One-Euro+prediction
                              │   → TARGET RESOLVER → ASSIGNMENT → SAFETY LAYER
                              └─ SLOW (event clips, 2–8 fps): V-JEPA → activity state
             Frigate: recording/review only — NOT in the control path
                              │ direct MQTT {fixture, pan, tilt, rate, dim}
             ESPHome C6 nodes (batch_delay: 0) ──► CAN ──► RMD actuators
             Home Assistant: observes, overrides — never in the loop
```

Annotations on each block:

- **Target resolver:** static targets (art, table) are *label lookups* in the room model — zero runtime perception. Dynamic targets come from tracks, led by velocity. Book = wrist offset from the person anchor.
- **Assignment** (which fixture takes which target): bipartite matching (Hungarian) with costs = incidence-angle badness (light the task from beside/behind the person, not their face) + travel + a hysteresis bonus for the incumbent. Run assignment at 1–5 Hz (sticky), aiming at 15–30 Hz — per-frame reassignment invites beam flapping. Handoffs cross-fade. Honest status: no published algorithm exists for lights; this is greenfield.
- **Safety layer (runs last, overrides all):** predictive no-go cones around heads (extrapolate by angular velocity — static per-frame checks demonstrably fail on fast motion), soft-edge dimming at cone borders, UGR ≤ 19 as a computable glare budget, and the interlock: tracking-confidence loss → park/dim within a deadline.
- **The camera sees the beam — design for it:** a bright moving spot shifts auto-exposure and casts moving shadows. Lock camera exposure, test the tracker with beams active, mask the commanded spot region if needed. (The same fact becomes an asset in calibration.)
- **Aiming math:** closed-form angles per fixture from the calibrated model, with the dual-solution constraint (every target has a mirrored pan+180° twin — pick one and don't flip).

## 4. Step-by-step execution plan

### Phase 0 — "The lamp follows me" (a weekend; needs only the Doc 3/4 rig + any RTSP camera)

1. Mount the camera high in a corner and get its stream working — budget an hour if you've never set up an IP camera: on first boot it forces an admin password (via its app or web page at the camera's IP); **enable RTSP/ONVIF in its settings** (often off by default); then confirm the stream plays in VLC (Media → Open Network Stream). Amcrest/Dahua URL pattern: `rtsp://user:pass@CAMERA_IP:554/cam/realmonitor?channel=1&subtype=0` — the camera's web UI or manual confirms the exact path. While in settings, set **fixed exposure** (the beam-in-view rule from §3).

!!! agent-prompt "🤖 Give this to your agent"

    ```text
    You're my bench agent for the Engineered Lighting perception stack
    (chapter: engineering.engineered.lighting/05-teach-it-to-aim/, Phase 0
    steps 2-6). The corner camera is mounted and streaming RTSP with fixed
    exposure, and the Doc 3/4 gimbal rig is on the bench with its ESPHome
    node subscribed to the spotlight/target MQTT topic, forwarding to CAN.

    Start by proposing a plan and wait for my approval before executing
    anything.

    Task: build the follow-me tracker on the GPU box, in a git repo, and
    iterate on it while I watch the beam. (a) pip install ultralytics and
    run YOLO26 person detection on the stream with ByteTrack IDs via
    model.track(); read frames through OpenCV with buffering disabled —
    grab-and-discard so we always process the newest frame. (b) Floor
    calibration: I tape 4 marks in a big rectangle and tape-measure their
    true room-frame positions; take my clicked pixel positions from one
    saved frame and compute the pixel-to-floor homography with
    cv2.getPerspectiveTransform. (c) For each tracked person, map the
    bottom-center of the box (the feet) through the homography to (x, y)
    on the floor; smooth with a One Euro filter, estimate velocity, and
    compute the led aim point (position + velocity × measured loop
    latency). (d) Fixture pose: I tape-measure the gimbal's (x, y, z);
    compute pan = atan2 and tilt = atan toward a chest-height point above
    the aim point. (e) Publish {"v":1, "ts":..., "pan":..., "tilt":...,
    "rate":60} — the Doc 6 envelope fields — to the spotlight/target
    topic at ~10-15 Hz, and use mosquitto_sub on that topic to verify
    what the fixture is actually being told; the 0xA4 speed field keeps
    motion continuous between updates.

    SAFETY — non-negotiable: never command motor motion unless I confirm
    I'm watching with a hand near the supply switch. The bench current
    limit stays as set. Announce each motion command before sending it
    and wait for my explicit go.

    Done when: the beam follows you smoothly across the room and you have
    latency + noise numbers.

    Report back: end-to-end latency (wave-to-beam from slow-mo video),
    beam lag at walking speed, tracking noise while standing still, a
    mosquitto_sub capture of spotlight/target, and the diff of every
    script added to the repo.
    ```

    *[How to run this prompt →](00b-ai-native-workflow.md)*

2. On the GPU box: `pip install ultralytics` + run YOLO26 person detection on the stream; add ByteTrack IDs (built into Ultralytics' `model.track()`); read frames via OpenCV with buffering disabled (grab-and-discard so you always process the *newest* frame — the classic seconds-of-lag trap). This script — and every GPU-box script in this doc — is ideal Claude Code territory: run it in a git repo on the box and have it scaffold, run, and iterate on the tracker while you watch the beam; it can also `mosquitto_sub` the output topic to verify what the fixture is actually being told.
3. **Floor calibration (15 min):** tape 4 marks on the floor in a big rectangle; measure their true positions with a tape measure (room frame = one corner of the room, x/y along walls); click their pixel positions in one saved frame; `cv2.getPerspectiveTransform` gives the pixel→floor homography.
4. For each tracked person: bottom-center of the box (≈ feet) → homography → (x, y) on the floor. Smooth with a One Euro filter; estimate velocity; compute the *led* aim point (position + velocity × measured loop latency).
5. Fixture pose: measure the gimbal's (x, y, z) with a tape measure; `pan = atan2`, `tilt = atan` toward a chest-height point above the aim point.
6. Publish `{"v":1, "ts":…, "pan":…, "tilt":…, "rate":60}` (envelope fields per [Doc 6](06-message-contract.md)) to the MQTT topic **`spotlight/target`** at ~10–15 Hz (the name [Doc 3](03-build-the-gimbal.md) stage 9 and [Doc 4](04-full-fixture-bench.md)'s stage-6 look-ahead both use); the [Doc 4](04-full-fixture-bench.md) ESPHome node subscribed to that topic forwards to CAN. The 0xA4 speed field makes motion continuous between updates.
7. Walk the room. Measure: end-to-end latency (wave-to-beam on slow-mo video), beam lag at walking speed, noise during tracking.

**Done when:** the beam follows you smoothly across the room and you have latency + noise numbers. *This single demo validates the entire stack's riskiest loop.*

### Phase 1 — Surfaces & suppression (the room model arrives)

!!! agent-prompt "🤖 Give this to your agent"

    ```text
    You're my bench agent for the Engineered Lighting perception stack
    (chapter: engineering.engineered.lighting/05-teach-it-to-aim/, Phase 1
    — surfaces & suppression). The follow-me loop from Phase 0 works off
    a 4-point floor homography, and I have a LiDAR room scan (Polycam
    Space Mode, rescaled against one tape-measured distance) exported as
    a mesh/point cloud.

    Start by proposing a plan and wait for my approval before executing
    anything.

    Task: be my calibration helper for registering the camera to the room
    scan and wiring in the room model. (a) Help me label ~10-20 surfaces
    from the scan into named JSON entries {name, centroid, normal,
    extent} — I do the lasso clicking in CloudCompare or SuperSplat, you
    build and validate the JSON. (b) Register the camera to the scan: I
    photograph the ChArUco board at a spot picked from the scan; you run
    solvePnP and invert for the camera pose, with sanity checks —
    reprojection under 1 px plus a few clicked non-coplanar points.
    (c) Replace the Phase 0 4-point floor homography with the registered
    camera + the scan's floor (better everywhere in the room). (d) Wire
    activity context in: subscribe the states the existing model
    publishes over MQTT and map them in the resolver — reading@couch to
    wall-art idle, cooking to the cutting-board target, movie to
    suppression (no spontaneous motion).

    SAFETY — non-negotiable: never command motor motion unless I confirm
    I'm watching with a hand near the supply switch. The bench current
    limit stays as set. Announce each motion command before sending it
    and wait for my explicit go.

    Done when: "light the table," "point at the art," and movie-stillness
    all work from label lookups.

    Report back: the solvePnP reprojection error and non-coplanar check
    results, before/after floor-position accuracy at a few tape-measured
    spots, the labeled-surfaces JSON, a mosquitto_sub capture showing a
    context state switching the target, and the diff.
    ```

    *[How to run this prompt →](00b-ai-native-workflow.md)*

1. Scan the room (Polycam **Space Mode**, LiDAR); tape-measure one known distance; rescale if off. Export mesh/point cloud.
2. Label ~10–20 surfaces once, manually (CloudCompare or SuperSplat lasso → named JSON `{name, centroid, normal, extent}`). Fifteen minutes of clicking beats a research project — auto-labeling (open-vocab 3D) is still unreliable on loose language like "cutting board."
3. Register the camera to the scan: ChArUco board at a spot picked *from the scan* → one photo → `solvePnP` → camera pose (invert!). Sanity: reprojection <1 px, plus a few clicked non-coplanar points. (Marker-based beats automatic matching indoors — the leading auto tool's own maintainers report >80% indoor failure.)
4. Replace Phase 0's 4-point floor homography with the registered camera + scan floor (better everywhere in the room).
5. Wire activity context in: your existing model publishes states over MQTT; the resolver maps `reading@couch` → wall-art idle vs. `cooking` → cutting-board target; `movie` → **suppression** (no spontaneous motion).

**Done when:** "light the table," "point at the art," and movie-stillness all work from label lookups.

### Phase 2 — Self-calibration (the crown jewel)

1. Sweep each fixture through a coarse pan/tilt grid **spanning its full range** but constrained to camera-visible landings (spots outside the FoV or occluded teach nothing; if the visible region is small, densify there or add a second camera pose).
2. At each grid point: beam on/off, frame-difference, centroid of the spot; ray-cast that pixel onto the scan mesh for the 3D landing point. **Lock exposure; run at dimmed ambient** — the system controls the room's other lights, so calibrate at night automatically for maximum contrast.
3. Fit fixture pose + encoder zero-offsets + axis non-orthogonality by least squares (Levenberg–Marquardt; the telescope-pointing term structure). Error budget: scan ~2 cm + registration ~2 cm + centroid ~2 cm → RSS ≈ 3.5 cm ≈ **0.67° at 3 m** — inside the ~1° budget, not by miles; *measure* residuals rather than assuming them.
4. Verify: command the beam to 10 labeled targets, measure landing error with the camera. Keep the manual 4-point jog as bootstrap/fallback. Re-fit automatically if drift is detected (the camera checks every landing forever — the system notices its own miscalibration).

**Done when:** a fixture placed anywhere self-calibrates in ~2 minutes and lands within ~1° on demand. This is also when fixture #2 arrives.

### Phase 3 — Book & gestures v1

1. Book: person anchor + wrist keypoint offset → aim; open-vocab confirm ("book" via YOLOE/SAM-3-class model on a wrist-region crop) to *arm* the behavior.
2. Gestures: arm-scale only (raise/wave/hold-out from body keypoints), armed by context state; coarse point-to-zone (ray from shoulder→wrist, snapped to the nearest labeled surface).

**Done when:** the beam lands on a held book within one beam-width; a raised-arm gesture reliably toggles it; and a normal evening passes with zero false gesture triggers.

### Phase 4 — Coordination & safety hardening

Two fixtures, two people: Hungarian assignment @ 1–5 Hz with hysteresis; cross-fade handoffs; predictive no-go cones + soft-edge dimming + tracking-loss interlock; motion styling (anticipation micro-move, context speed caps). **Done when:** two people walk crossing paths and the beams hand off without flapping or ever crossing a face.

### Phase 5 — Precision & identity

Trained pointing model (<2°) only if coarse pointing earns it; geometric/trajectory re-ID → per-person preferences (feeds the roadmap's identity layer).

**Done when:** a pointed arm selects the intended zone ≥9 times in 10, and two household members each get their saved warmth/brightness without asking.

## 5. The depth question, answered directly

| Tier | Hardware | Covers | When |
|---|---|---|---|
| **0 — ground plane + room model** | none new | follow-me, all static targets, couch-seated (model priors), book (wrist offset), heads for safety | **Start here** |
| 1 — better software | none | multi-camera fusion (halves jitter), occlusion-robust tracking, object memory | as stories demand |
| 2 — one stereo camera in a hard room | $359–579 | true 3D for reclined/floor-sitting, heavy clutter, tight multi-person; sharper self-cal | only when Tier 0 measurably misses |
| ✗ monocular depth networks | GPU only | — | skip — jittery, 18–40 cm @ 4 m, worse than free geometry |

Fisheye note: a 180°+ lens covers big rooms from one corner but needs a fisheye calibration model + dewarp before any of the geometry above — prefer two normal cameras when a room demands more coverage.

## 6. Risk register (honest)

- **Novel, no precedent:** the V-JEPA + real-time-tracker dual path and world-model-gated gestures are unpublished combinations — analogs de-risk the pattern; the integration is ours to prove.
- **Coordination policy is greenfield** — expect tuning cycles on costs/hysteresis; no literature will save us.
- **Slow-path latency is seconds-to-tens-of-seconds** (clips → V-JEPA): context-driven target switches lag activity changes; stories must tolerate it, and anything sub-second belongs on the fast path by design.
- **Hands at range stay unsolved (2026)** — stories are designed to wrist-level precision, which the beam width forgives.
- **No public benchmarks for this GPU** on Frigate/DeepStream/V-JEPA — benchmark early; margins on adjacent hardware suggest ample headroom.
- **Edge-migration debt (strategic):** the prototype is deliberately central-GPU, but the commercial product runs on a home-hub NPU. Cheap to migrate: YOLO-class detection, tracking, all the ground-plane/calibration/aiming math (it's just algebra). Expensive to migrate: SAM-3-class open-vocab segmentation, DeepStream-specific pipelines (NVIDIA-locked), full-size V-JEPA. Prefer the portable primitive wherever two options tie; treat every DeepStream convenience as prototype-only.
- **Product-kit camera transport must be reconciled:** if the commercial kit's per-room cameras stream continuous WiFi video, a 5–10 room home lands exactly in the documented WiFi-collapse regime. The edge hierarchy in the Engineered Lighting strategy roadmap (an internal doc outside this series) is the answer — tier-1 vision on-device, ship metadata/clips, not video — the prototype's stream-everything pattern is a lab convenience the product must not inherit. Wired/PoE is the alternative at installation-friction cost.
- **Camera brand watch item:** FCC Covered-List expansion (July 2026) targets Dahua/Hikvision procurement — residential unaffected, but firmware/inventory longevity is worth watching for Dahua-lineage brands.
- **Patents for counsel:** US 12,190,542 (beam self-calibration), US 11,956,873 (multi-fixture follow-spot control), Forma (motorized recessed fixtures).
- **Trust is the real adoption risk:** the same research validating demand documents the "being watched" objection — suppression states, legible motion, and a visible perception-off affordance are requirements, not polish.

## Further reading (most load-bearing)

Ground-plane localization accuracy — arxiv.org/abs/2606.13509 · DeepStream 9.1 MV3DT + AutoMagicCalib — developer.nvidia.com/blog (July 2026) + DS_Performance docs · One Euro filter — CHI 2012, direction.bordeaux.inria.fr/~roussel · REACH (hands at room range) — arxiv.org/abs/2605.22231 · SAM 3 — ai.meta.com/blog/segment-anything-model-3 · YOLO26 — docs.ultralytics.com · Beam self-cal patent — patents.google.com/patent/US12190542B2 · Beamatron (steerable-projector math, MSR UIST 2012) — hbenko.com · Pan-tilt kinematic calibration — arxiv.org/pdf/1812.00232 · TPOINT pointing models — bisque.com · OpenCV solvePnP/ChArUco — docs.opencv.org · hloc indoor-failure admission — github.com/cvg/Hierarchical-Localization/issues/325 · Polycam — learn.poly.cam · zactrack/BlackTrax/Follow-Me (manual-calibration prior art) — vendor sites · LuminAR (MIT robotic lamp precedent) — spectrum.ieee.org · Frigate autotracking + smoothing lessons — docs.frigate.video, github issue #20903 · PointingNet — arxiv.org/abs/2307.02949 · Animation principles for robots (HRI 2011) — leilatakayama.org · ADB glare masking — NHTSA DOT HS 812 174 · ILDA audience-scanning safety — ilda.com · go2rtc — github.com/AlexxIT/go2rtc · WiFi multi-camera collapse — ipcamtalk thread 77100 · ESPHome batch_delay — esphome.io/components/api · V-JEPA 2 — github.com/facebookresearch/vjepa2
