---
title: 7 · Building the Software
description: "The software: pinned stack, repo layout, hardware-free testing, deployment, and the firmware growth path."
---

# Doc 7 · Building the Software — Stack, Repos, Testing, Deployment

**Engineered Lighting prototype series · July 2026**
How the code actually gets built: the services on the GPU box, the fixture firmware's growth path, and — the part that usually gets skipped — how to test all of it without standing in front of a camera holding a book. Every package and pattern here was verified against official docs/source in July 2026.

## Nothing to buy

Everything here is open source. The costs are attention and discipline.

## Concepts (plain English)

- **Restreamer:** a small server (go2rtc / mediamtx) that connects to each camera *once* and re-serves the stream locally to any number of consumers — isolating flaky camera connections from your code, and doubling as the replay rig for testing.
- **uv workspace:** one Python repo containing several packages (tracker, resolver, context bridge) sharing a single lockfile — the current standard toolchain (uv won; even OpenAI acquired its maker in 2026 and kept it open source).
- **Golden test:** record a real session's tracks once, replay them into the resolver in CI forever — asserting the same inputs still produce the same aim outputs.
- **ESPHome `host` platform:** compiles your fixture config into a *native program* on your dev machine — real `api:` server, template outputs standing in for hardware — so the resolver can be integration-tested against a simulated fixture with zero hardware. ESPHome's own CI tests itself exactly this way.
- **External component:** the sanctioned way ESPHome lambdas grow up — a small Python+C++ package (`components/fixture_control/`) that YAML then imports. The old "custom component" hack is dead (removed 2025); this is its successor.
- **GPL boundary:** ESPHome's C++ core is GPLv3 (its Python tooling is MIT). Any C++ you compile into the firmware binary joins a GPLv3 combined work — fine for prototypes and open products, a real decision point for the commercial fixture (§6).

## 1. The services on the GPU box (what runs, in what process)

```
cameras ──► go2rtc/mediamtx restream (one local RTSP per room)
              │
              ├─► TRACKER  (one process per room)          ─┐
              │    ultralytics.track(stream=True,           │ MQTT (QoS 0)
              │    persist=True, tracker=bytetrack)         │ el/<room>/tracks @15Hz
              │    feet→ground-plane → One-Euro/prediction ─┘ + perception/status
              │
              ├─► CONTEXT BRIDGE (one process, GPU)
              │    event-triggered clips → V-JEPA → el/<room>/context (retained)
              │
              └─► Frigate (recording/review only — off the control path)

RESOLVER (one asyncio process, uvloop)
  subscribes tracks+context (aiomqtt) · watches HA state_changed w/ contexts (hass-client)
  computes per-fixture pan/tilt · safety cones · assignment
  → bench: publishes spotlight/target (MQTT)
  → production: calls fixture_aim() directly (aioesphomeapi + ReconnectLogic, one client per fixture)
```

Why process-per-camera (Frigate's pattern, not Ultralytics' threading example): isolation — one room's camera flaking can't stall the others, and each tracker restarts independently. The RTX 6000 has orders-of-magnitude more throughput than a home needs, so batching efficiency (DeepStream's win) buys nothing here.

**The stack, pinned (July 2026, all verified):**

| Role | Package | Version note |
|---|---|---|
| Detection + tracking | `ultralytics` | ≥8.4.63 (YOLO26 + current trackers; ByteTrack = cheapest for static cameras) |
| Camera restream + replay | go2rtc v1.9.14 or mediamtx v1.19.2 | either; go2rtc already ships inside Frigate |
| Async MQTT | `aiomqtt` | **==2.5.1** (3.0.0a1 exists — alpha, skip) |
| ESPHome native API client | `aioesphomeapi` | ≥45.6.0; use `ReconnectLogic` (backoff + instant mDNS reconnect) |
| HA observation | `hass-client` | ==1.2.3 — asyncio WebSocket client, production-proven by Music Assistant; subscribes `state_changed` *with context data* (the override detector's food) |
| Event loop | `uvloop` | latest |
| Config models | `pydantic` 2.x | per-room YAML loaded with `yaml.safe_load` + `model_validate` (pydantic-settings' YAML source can't do nested sections — known open issue — so keep it for process env only) |
| Env/build | `uv` | workspace mode |
| GPU containers | `nvidia-container-toolkit` + compose `deploy.resources.reservations.devices` | Frigate's own install pattern |

**Three ingest rules that prevent the classic seconds-of-lag bug:** always read through the local restream (never direct-to-camera); set `OPENCV_FFMPEG_CAPTURE_OPTIONS="rtsp_transport;tcp|fflags;nobuffer|flags;low_delay"` before opening; and know that Ultralytics' `stream=True` loader already keeps only the newest frame internally (verified in its source) — the env var still matters because it opens plain `cv2.VideoCapture` underneath.

**Calling the fixture (production lane), the whole pattern:**

```python
api = aioesphomeapi.APIClient("fixture-1.local", 6053, None, noise_psk=PSK)  # encryption mandatory ≥2026.1
entities, services = await api.list_entities_services()
aim = next(s for s in services if s.name == "fixture_aim")
await api.execute_service(aim, {"pan": 32.5, "tilt": -14.0})   # typed floats, fire-and-forget, ~12 Hz
```

## 2. Repo layout (one monorepo, uv workspace)

```
engineered-lighting/
  services/
    tracker/          # per-camera process; pyproject each; uv workspace members
    resolver/
    context_bridge/
  libs/roommodel/     # shared pydantic models: tracks, context, targets (Doc 6 schemas as code)
  firmware/           # the ESPHome tree (see §4)
  config/rooms/*.yaml # one file per room: camera URL+pose, fixture poses+calibration, labeled surfaces
  deploy/docker-compose.yaml
  tests/
    golden_tracks/    # recorded jsonl track sessions
    clips/            # short mp4s for RTSP replay
```

`libs/roommodel` is where [Doc 6](06-message-contract.md) stops being prose: every schema becomes a pydantic model, and both publisher and subscriber import the same class — the contract enforced by the type checker instead of by discipline.

## 3. Testing without a living room (the part that makes AI-partner development fly)

- **Replay cameras:** mediamtx loops an mp4 as a real RTSP source (`runOnInit: ffmpeg -re -stream_loop -1 …`, or its native `alwaysAvailableFile:`); go2rtc's `exec:` source does the same. Record 2 minutes of walking through the room once; the tracker develops against it forever.
- **Golden tracks:** capture `(ts, id, x, y, vx, vy)` jsonl from a session; replay at wall-clock pace into the resolver in CI; assert pan/tilt outputs within tolerance. Geometry (homography, aim inverse, cone checks) gets plain `pytest` + `numpy.testing.assert_allclose`.
- **Simulated fixture — the big one:** an `esphome` config with `host:` + `api:` + template outputs compiles to a native binary exposing the *real* API server. The resolver's integration test spins it up as a subprocess, connects with real `aioesphomeapi`, calls `fixture_aim`, and asserts state — the identical pattern ESPHome's own `tests/integration/` uses in its CI. End-to-end resolver→firmware-logic testing, zero hardware, runs in GitHub Actions. (Host caveats: no MQTT component, no real GPIO — template stand-ins only, which is exactly what you want.)
- **Why this matters doubly:** every one of these loops is text-in/text-out, which means Claude Code can run the full suite, read failures, and iterate — the Docs [3](03-build-the-gimbal.md)/[4](04-full-fixture-bench.md) lab-partner workflow extended to the whole system.

## 4. Firmware engineering (bench → fleet → product)

```
firmware/
  components/fixture_control/    # the graduated C++ external component (RMD CAN driver,
                                 #   aim gate, watchdog) — starts as type: local
  packages/
    base-fixture.yaml            # PCA9685, canbus, api+actions, ota, logger — shared
    network.yaml · mqtt.yaml     # mqtt: discovery: false
  devices/<room>/fixture-NN.yaml # thin per-fixture file: substitutions + package includes
  secrets.yaml                   # gitignored; remote packages can't use !secret — pass via substitutions
  tests/host/                    # the simulated-fixture configs from §3
  .github/workflows/             # esphome config validate + esphome/build-action@v8 matrix
```

- **When lambdas graduate:** the [Doc 4](04-full-fixture-bench.md) lambdas are right for the bench. The moment the CAN logic grows (telemetry parsing, two-stage failsafe, calibration hooks), it becomes `components/fixture_control/` — the official skeleton is ~3 files (`__init__.py` schema + `.h/.cpp`), and `mrk-its/esphome-canopen` is the structural reference for a component that rides the built-in `canbus:`. **Verified negative: no RMD/CyberGear/ODrive ESPHome component exists anywhere — ours is greenfield**, and a candidate for open-sourcing (community moat, exactly the Made-for-ESPHome ethos).
- **Fleet pattern:** one base package + thin per-device files that set only substitutions (the jesserockz/ESPHome-maintainer pattern); Jinja expressions in substitutions (2025.7+) derive per-fixture CAN IDs and offsets. Fleet updates: `esphome update-all`, Device Builder's bulk actions (2026.6+), or HA `update.*` entities.
- **Performance discipline on the single core (all source-verified):** the loop-block warning threshold is now **50 ms** (raised from the oft-cited 30 ms in mid-2025); CAN RX drains its whole queue inline per tick — fine at our tens of frames/sec, **but keep `logger:` at INFO once telemetry flows** (per-frame DEBUG logging is the documented crash cause on busy CAN nodes); structure the CAN component event-style (`disable_loop()` when idle) rather than polling.
- **The product licensing decision (flag for counsel, not resolvable here):** ESPHome's C++ core is **GPLv3** — a commercial fixture shipping ESPHome-based firmware ships a GPLv3 combined work: source availability plus the anti-lock-down clause (users must be able to install modified firmware) — in direct tension with signed OTA. Real precedents exist for embracing it (Apollo Automation and Athom ship ESPHome commercially; the free "Made for ESPHome" program formalizes it) — but every confirmed precedent is open-hardware prosumer gear, not a mass-market appliance. The alternatives: keep ESPHome for prototypes/dev-kits and write ESP-IDF firmware for the sealed product (the aim/CAN/failsafe logic ports cleanly — it's the smallest part of what ESPHome provides), or lean into openness as strategy (it *is* on-brand for the HA-first launch audience). Decide before the commercial firmware effort starts, not after.

## 5. Deployment (one GPU box, boring on purpose)

Single `docker-compose.yaml`: restreamer, tracker-per-room, context-bridge, resolver, Frigate — GPU services declare `deploy.resources.reservations.devices` (NVIDIA runtime via `nvidia-ctk runtime configure`). One systemd unit runs `docker compose up -d` at boot; compose owns restarts. Mosquitto and HA stay where they are (the HA box); everything meets on the LAN per [Doc 5](05-teach-it-to-aim.md)'s VLAN plan.

## 6. Build order (the first two weeks of software)

!!! agent-prompt "🤖 Give this to your agent"

    ```text
    You're my bench agent for the Engineered Lighting software build
    (chapter: engineering.engineered.lighting/07-building-the-software/,
    build-order step 1 — repo bootstrap). Everything in this step is
    hardware-free and runs on the GPU box; no camera, no fixture.

    Start by proposing a plan and wait for my approval before executing
    anything.

    Task: bootstrap the monorepo exactly per the chapter's repo layout: a
    uv workspace with services/tracker, services/resolver, and
    services/context_bridge (a pyproject each, one shared lockfile);
    libs/roommodel encoding the Doc 6 message schemas as pydantic 2.x
    models so publisher and subscriber import the same class;
    config/rooms/ with per-room YAML loaded via yaml.safe_load +
    model_validate; deploy/docker-compose.yaml; the firmware/ tree
    skeleton; and tests/golden_tracks + tests/clips directories. Pin the
    chapter's stack exactly — ultralytics >=8.4.63, aiomqtt ==2.5.1,
    aioesphomeapi >=45.6.0, hass-client ==1.2.3, uvloop, pydantic 2.x —
    but re-verify every pin at build time per the chapter's version-drift
    rule and flag anything that moved.

    Done when: uv sync succeeds across the whole workspace and the
    service skeletons, roommodel schemas, and compose file are committed.

    Report back: the repo tree, the uv sync output, any pin that drifted
    from the chapter's table, and the diff.
    ```

    *[How to run this prompt →](00b-ai-native-workflow.md)*

1. Repo bootstrap: uv workspace, `libs/roommodel` encoding [Doc 6](06-message-contract.md)'s schemas, empty service skeletons, compose file. *(An afternoon, mostly Claude Code.)*

!!! agent-prompt "🤖 Give this to your agent"

    ```text
    You're my bench agent for the Engineered Lighting software build
    (chapter: engineering.engineered.lighting/07-building-the-software/,
    build-order step 2 — replay rig before real cameras). The repo from
    step 1 exists; a 2-minute recorded clip of someone walking the room
    stands in for a live camera, so this step touches no hardware.

    Start by proposing a plan and wait for my approval before executing
    anything.

    Task: build the replay rig and the tracker MVP against it. Configure
    mediamtx to loop the mp4 as a real local RTSP source (runOnInit with
    ffmpeg -re -stream_loop -1, or its native alwaysAvailableFile). Then
    the tracker (one process per room): ultralytics track with
    stream=True, persist=True, tracker=bytetrack; feet to ground-plane
    position; One-Euro smoothing plus prediction; publish
    el/<room>/tracks at 15 Hz (MQTT QoS 0) plus perception/status. Obey
    the chapter's three ingest rules: always read through the local
    restream; set OPENCV_FFMPEG_CAPTURE_OPTIONS to
    "rtsp_transport;tcp|fflags;nobuffer|flags;low_delay" before opening;
    and rely on stream=True keeping only the newest frame. Use the
    chapter's pinned versions, re-verifying pins at build time per the
    version-drift rule.

    Done when: mosquitto_sub shows sane 15 Hz tracks from a looped clip.

    Report back: a mosquitto_sub capture of el/<room>/tracks with the
    measured publish rate, per-frame processing latency on the GPU box,
    and the diff.
    ```

    *[How to run this prompt →](00b-ai-native-workflow.md)*

2. Replay rig before real cameras: mediamtx looping a recorded clip → tracker MVP against it → tracks on MQTT. **Done when** `mosquitto_sub` shows sane 15 Hz tracks from a looped clip.

!!! agent-prompt "🤖 Give this to your agent"

    ```text
    You're my bench agent for the Engineered Lighting software build
    (chapter: engineering.engineered.lighting/07-building-the-software/,
    build-order step 3 — resolver MVP). The step-2 tracker is publishing
    el/<room>/tracks at 15 Hz from the looped clip; still no hardware
    anywhere.

    Start by proposing a plan and wait for my approval before executing
    anything.

    Task: build the resolver as one asyncio process on uvloop: subscribe
    tracks and context with aiomqtt (==2.5.1); compute per-fixture
    pan/tilt with the aim math driven by the fixture poses and
    calibration in config/rooms/; include the safety-cone checks and
    assignment; publish bench targets on spotlight/target using the Doc 6
    envelope fields. Testing: capture a golden-track session as (ts, id,
    x, y, vx, vy) jsonl into tests/golden_tracks/, replay it at
    wall-clock pace into the resolver in CI, and assert the pan/tilt
    outputs within tolerance; cover the pure geometry (homography, aim
    inverse, cone checks) with plain pytest +
    numpy.testing.assert_allclose. Follow the chapter's pins,
    re-verifying at build time per the version-drift rule.

    Done when: golden-track replay produces expected angles in pytest.

    Report back: the pytest output including the golden-track tolerances,
    a sample of the published spotlight/target messages, and the diff.
    ```

    *[How to run this prompt →](00b-ai-native-workflow.md)*

3. Resolver MVP: consume tracks, aim math from `config/rooms/`, publish bench targets. **Done when** golden-track replay produces expected angles in pytest.

!!! agent-prompt "🤖 Give this to your agent"

    ```text
    You're my bench agent for the Engineered Lighting software build
    (chapter: engineering.engineered.lighting/07-building-the-software/,
    build-order step 4 — the simulated fixture). The step-3 resolver
    passes its golden-track tests; this step stays entirely hardware-free
    — the fixture is a compiled host-platform binary.

    Start by proposing a plan and wait for my approval before executing
    anything.

    Task: create an esphome config in firmware/tests/host/ using the host
    platform with an api server and template outputs standing in for
    hardware, exposing the fixture_aim action. Then the integration test:
    spin the compiled binary up as a subprocess, connect with real
    aioesphomeapi (>=45.6.0, ReconnectLogic, noise encryption — mandatory
    since 2026.1), call fixture_aim with typed floats, and assert the
    resulting state — the same pattern ESPHome's own tests/integration/
    uses in its CI. Remember the host caveats: no MQTT component, no real
    GPIO — template stand-ins only, which is exactly what we want. Wire
    it into GitHub Actions alongside esphome config validate.

    Done when: the whole loop passes with no hardware attached.

    Report back: the integration-test pytest output, the CI run result,
    and the diff.
    ```

    *[How to run this prompt →](00b-ai-native-workflow.md)*

4. Simulated fixture: host-platform config + `fixture_aim` action; resolver integration test green in CI. **Done when** the whole loop passes with no hardware attached.

!!! agent-prompt "🤖 Give this to your agent"

    ```text
    You're my bench agent for the Engineered Lighting software build
    (chapter: engineering.engineered.lighting/07-building-the-software/,
    build-order step 5 — point it at reality). Steps 1-4 proved every
    component against the replay rig and the simulated fixture; this step
    prepares the swap to the real camera and the Doc 4 bench rig but
    stays hardware-free itself — anything that actually moves the fixture
    belongs to the Doc 5 Phase 0 session and its own prompt.

    Start by proposing a plan and wait for my approval before executing
    anything.

    Task: make the swap a pure configuration change. Point the restreamer
    at the real camera's RTSP URL (still reading only through the local
    restream, per the ingest rules), update config/rooms/ with the real
    camera pose and fixture pose, and switch the resolver's output to the
    bench lane — spotlight/target over MQTT, which the Doc 4 ESPHome node
    forwards to CAN. Verify the perception side only: the tracker
    consuming the live stream, sane 15 Hz tracks on el/<room>/tracks, the
    resolver publishing plausible angles — with the fixture's supply left
    off. Do not command or enable any fixture motion in this session.

    Done when: the tracker runs against the live camera and the resolver
    publishes plausible bench targets, with every component already
    tested before hardware enters — the remaining unknowns are physics,
    not code.

    Report back: a mosquitto_sub capture of el/<room>/tracks and of
    spotlight/target from the live stream, the measured track rate, and
    the config diff.
    ```

    *[How to run this prompt →](00b-ai-native-workflow.md)*

5. Point it at reality: swap the looped clip for the real camera, the simulated fixture for the bench rig — this is [Doc 5](05-teach-it-to-aim.md) Phase 0, arrived at with every component already tested. The remaining unknowns are physics, not code.

!!! agent-prompt "🤖 Give this to your agent"

    ```text
    You're my bench agent for the Engineered Lighting software build
    (chapter: engineering.engineered.lighting/07-building-the-software/,
    build-order step 6 — graduating the firmware and override detection).
    The full loop from steps 1-5 runs; the Doc 4 CAN lambdas have
    outgrown a screen. This step is code and host-platform tests only —
    no flashing, no hardware.

    Start by proposing a plan and wait for my approval before executing
    anything.

    Task: graduate the CAN lambdas into the external component
    firmware/components/fixture_control/ (starts as type: local) — the
    official ~3-file skeleton (__init__.py schema plus .h/.cpp), riding
    the built-in canbus, with mrk-its/esphome-canopen as the structural
    reference; ours is greenfield, since no RMD ESPHome component exists
    anywhere. Respect the chapter's single-core discipline: event-style
    structure with disable_loop() when idle, logger at INFO once
    telemetry flows, and the 50 ms loop-block threshold. Separately, wire
    hass-client (==1.2.3) into the resolver to subscribe state_changed
    with context data — the override detector's food — so the coordinator
    notices manual overrides. Validate with esphome config validate and
    the step-4 host-platform integration tests.

    Done when: the fixture_control component compiles, config validate
    and the host-platform integration tests pass, and a replayed
    state_changed event with context data is logged as a detected manual
    override.

    Report back: the esphome config validate output, the host-platform
    test results, the override-detection log line, and the diff.
    ```

    *[How to run this prompt →](00b-ai-native-workflow.md)*

6. Graduate the CAN lambdas into `fixture_control` when they exceed a screen; wire `hass-client` override detection when the coordinator starts making choices worth overriding.

## Risk register

- **`hass-client` is maintained by one adjacent project** (Music Assistant) — solid today; the fallback is ~200 lines of raw websocket client, so the exposure is bounded.
- **YOLO26/Ultralytics licensing is AGPL** for the library — fine for personal/prototype use; a commercial product needs an Ultralytics license or a differently-licensed detector. Same decision-gate timing as the ESPHome GPL question; bundle them for counsel.
- **No public benchmark exists** for this exact GPU on these exact loads (unchanged from [Doc 5](05-teach-it-to-aim.md)) — step 2's replay rig is also the benchmark harness.
- **Version drift:** everything above was verified July 2026; re-verify pins at build time (the pre-purchase-recheck rule from the hardware BoMs, applied to software).

## Further reading

Ultralytics track mode — docs.ultralytics.com/modes/track · aioesphomeapi — github.com/esphome/aioesphomeapi · ESPHome host platform — esphome.io/components/host · ESPHome external components — esphome.io/components/external_components + developers.esphome.io/architecture/components · esphome-canopen (structural reference) — github.com/mrk-its/esphome-canopen · build-action — github.com/esphome/build-action · packages/fleet pattern — esphome.io/components/packages + github.com/jesserockz/esphome-configs · mediamtx config (replay) — mediamtx.org/docs · Frigate architecture (process-per-camera precedent) — docs.frigate.video · hass-client — github.com/music-assistant/python-hass-client · aiomqtt — pypi.org/project/aiomqtt · uv workspaces — docs.astral.sh/uv · ESPHome LICENSE (GPL boundary) — github.com/esphome/esphome/blob/dev/LICENSE · Made for ESPHome — esphome.io/guides/made_for_esphome
