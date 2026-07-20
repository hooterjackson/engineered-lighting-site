---
title: 7 · Building the Software
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

`libs/roommodel` is where Doc 6 stops being prose: every schema becomes a pydantic model, and both publisher and subscriber import the same class — the contract enforced by the type checker instead of by discipline.

## 3. Testing without a living room (the part that makes AI-partner development fly)

- **Replay cameras:** mediamtx loops an mp4 as a real RTSP source (`runOnInit: ffmpeg -re -stream_loop -1 …`, or its native `alwaysAvailableFile:`); go2rtc's `exec:` source does the same. Record 2 minutes of walking through the room once; the tracker develops against it forever.
- **Golden tracks:** capture `(ts, id, x, y, vx, vy)` jsonl from a session; replay at wall-clock pace into the resolver in CI; assert pan/tilt outputs within tolerance. Geometry (homography, aim inverse, cone checks) gets plain `pytest` + `numpy.testing.assert_allclose`.
- **Simulated fixture — the big one:** an `esphome` config with `host:` + `api:` + template outputs compiles to a native binary exposing the *real* API server. The resolver's integration test spins it up as a subprocess, connects with real `aioesphomeapi`, calls `fixture_aim`, and asserts state — the identical pattern ESPHome's own `tests/integration/` uses in its CI. End-to-end resolver→firmware-logic testing, zero hardware, runs in GitHub Actions. (Host caveats: no MQTT component, no real GPIO — template stand-ins only, which is exactly what you want.)
- **Why this matters doubly:** every one of these loops is text-in/text-out, which means Claude Code can run the full suite, read failures, and iterate — the Docs 3/4 lab-partner workflow extended to the whole system.

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

- **When lambdas graduate:** the Doc 4 lambdas are right for the bench. The moment the CAN logic grows (telemetry parsing, two-stage failsafe, calibration hooks), it becomes `components/fixture_control/` — the official skeleton is ~3 files (`__init__.py` schema + `.h/.cpp`), and `mrk-its/esphome-canopen` is the structural reference for a component that rides the built-in `canbus:`. **Verified negative: no RMD/CyberGear/ODrive ESPHome component exists anywhere — ours is greenfield**, and a candidate for open-sourcing (community moat, exactly the Made-for-ESPHome ethos).
- **Fleet pattern:** one base package + thin per-device files that set only substitutions (the jesserockz/ESPHome-maintainer pattern); Jinja expressions in substitutions (2025.7+) derive per-fixture CAN IDs and offsets. Fleet updates: `esphome update-all`, Device Builder's bulk actions (2026.6+), or HA `update.*` entities.
- **Performance discipline on the single core (all source-verified):** the loop-block warning threshold is now **50 ms** (raised from the oft-cited 30 ms in mid-2025); CAN RX drains its whole queue inline per tick — fine at our tens of frames/sec, **but keep `logger:` at INFO once telemetry flows** (per-frame DEBUG logging is the documented crash cause on busy CAN nodes); structure the CAN component event-style (`disable_loop()` when idle) rather than polling.
- **The product licensing decision (flag for counsel, not resolvable here):** ESPHome's C++ core is **GPLv3** — a commercial fixture shipping ESPHome-based firmware ships a GPLv3 combined work: source availability plus the anti-lock-down clause (users must be able to install modified firmware) — in direct tension with signed OTA. Real precedents exist for embracing it (Apollo Automation and Athom ship ESPHome commercially; the free "Made for ESPHome" program formalizes it) — but every confirmed precedent is open-hardware prosumer gear, not a mass-market appliance. The alternatives: keep ESPHome for prototypes/dev-kits and write ESP-IDF firmware for the sealed product (the aim/CAN/failsafe logic ports cleanly — it's the smallest part of what ESPHome provides), or lean into openness as strategy (it *is* on-brand for the HA-first launch audience). Decide before the commercial firmware effort starts, not after.

## 5. Deployment (one GPU box, boring on purpose)

Single `docker-compose.yaml`: restreamer, tracker-per-room, context-bridge, resolver, Frigate — GPU services declare `deploy.resources.reservations.devices` (NVIDIA runtime via `nvidia-ctk runtime configure`). One systemd unit runs `docker compose up -d` at boot; compose owns restarts. Mosquitto and HA stay where they are (the HA box); everything meets on the LAN per Doc 5's VLAN plan.

## 6. Build order (the first two weeks of software)

1. Repo bootstrap: uv workspace, `libs/roommodel` encoding Doc 6's schemas, empty service skeletons, compose file. *(An afternoon, mostly Claude Code.)*
2. Replay rig before real cameras: mediamtx looping a recorded clip → tracker MVP against it → tracks on MQTT. **Done when** `mosquitto_sub` shows sane 15 Hz tracks from a looped clip.
3. Resolver MVP: consume tracks, aim math from `config/rooms/`, publish bench targets. **Done when** golden-track replay produces expected angles in pytest.
4. Simulated fixture: host-platform config + `fixture_aim` action; resolver integration test green in CI. **Done when** the whole loop passes with no hardware attached.
5. Point it at reality: swap the looped clip for the real camera, the simulated fixture for the bench rig — this is Doc 5 Phase 0, arrived at with every component already tested. The remaining unknowns are physics, not code.
6. Graduate the CAN lambdas into `fixture_control` when they exceed a screen; wire `hass-client` override detection when the coordinator starts making choices worth overriding.

## Risk register

- **`hass-client` is maintained by one adjacent project** (Music Assistant) — solid today; the fallback is ~200 lines of raw websocket client, so the exposure is bounded.
- **YOLO26/Ultralytics licensing is AGPL** for the library — fine for personal/prototype use; a commercial product needs an Ultralytics license or a differently-licensed detector. Same decision-gate timing as the ESPHome GPL question; bundle them for counsel.
- **No public benchmark exists** for this exact GPU on these exact loads (unchanged from Doc 5) — step 2's replay rig is also the benchmark harness.
- **Version drift:** everything above was verified July 2026; re-verify pins at build time (the pre-purchase-recheck rule from the hardware BoMs, applied to software).

## Further reading

Ultralytics track mode — docs.ultralytics.com/modes/track · aioesphomeapi — github.com/esphome/aioesphomeapi · ESPHome host platform — esphome.io/components/host · ESPHome external components — esphome.io/components/external_components + developers.esphome.io/architecture/components · esphome-canopen (structural reference) — github.com/mrk-its/esphome-canopen · build-action — github.com/esphome/build-action · packages/fleet pattern — esphome.io/components/packages + github.com/jesserockz/esphome-configs · mediamtx config (replay) — mediamtx.org/docs · Frigate architecture (process-per-camera precedent) — docs.frigate.video · hass-client — github.com/music-assistant/python-hass-client · aiomqtt — pypi.org/project/aiomqtt · uv workspaces — docs.astral.sh/uv · ESPHome LICENSE (GPL boundary) — github.com/esphome/esphome/blob/dev/LICENSE · Made for ESPHome — esphome.io/guides/made_for_esphome
