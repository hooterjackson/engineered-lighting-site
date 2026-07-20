---
title: 6 · The Message Contract
description: "The message contract every component obeys: topics, schemas, units, watchdogs, and the dual-control architecture."
---

# Doc 6 · The Message Contract — How Every Part of the System Talks

**Engineered Lighting prototype series · July 2026**
The single page that the tracker ([Doc 5](05-teach-it-to-aim.md)), the context model (your V-JEPA pipeline), the fixture firmware (Docs [3](03-build-the-gimbal.md)–[4](04-full-fixture-bench.md)), and the coordinator all agree on. Written *before* three codebases exist, because retrofitting a contract after they do is how systems rot. When any doc and this page disagree, **this page wins** — update the code, then the doc.

## Quick reference (the one-screen version)

| Lane | Name | Direction | Rate | Retained | Owner/writer |
|---|---|---|---|---|---|
| Aim stream (bench) | MQTT `spotlight/target` | resolver → fixture | ≤15 Hz | no, QoS 0 | resolver only |
| Aim stream (production) | native-API action `fixture_aim(pan, tilt)` | resolver → fixture (direct call via aioesphomeapi) | 5–15 Hz | n/a | resolver only |
| Fixture telemetry | MQTT `spotlight/state` | fixture → all | 1 Hz + on-change | yes | fixture |
| People tracks | MQTT `el/<room>/tracks` | tracker → resolver | 15–30 Hz | no, QoS 0 | tracker |
| Activity context | MQTT `el/<room>/context` | context model → all | on-change (lags seconds) | yes | V-JEPA pipeline |
| Assignments (observability) | MQTT `el/<room>/beam/assignments` | resolver → logs/dashboards | on-change | yes | resolver |
| Perception heartbeat | MQTT `el/<room>/perception/status` | tracker → fixtures | 1 Hz | yes | tracker |
| Brightness/CCT | HA `light.spot1` entity | everyone → HA → fixture | — | — | HA (single write path) |
| Mode / presets / jogs | HA `select` / `number` entities | humans + coordinator | — | — | HA |
| Failsafe | firmware-internal | — | 2 s target watchdog · 3 s heartbeat staleness · 1 s fade | — | fixture |

## Nothing to buy

The transport already exists: the **Mosquitto MQTT broker** (Home Assistant add-on, [Doc 4](04-full-fixture-bench.md)'s prerequisites box). Lights are the one exception — they ride ESPHome's native HA API as normal light entities and never touch MQTT directly; the coordinator drives them through HA scenes/services.

## Conventions (read once)

- **Payloads are JSON**, snake_case keys. Every message carries `"ts"` (unix milliseconds) and `"v": 1` (contract version — bump it when a schema changes shape).
- **Units, always:** angles in **degrees**, positions in **meters**, rates in **deg/s** or **m/s**, confidence **0–1**, dim levels **0–1**. Never radians, never centimeters, never percent.
- **Frames:** positions are in the **room frame** (right-handed, z-up, origin and axes fixed by the room scan — [Doc 5](05-teach-it-to-aim.md) Phase 1). Fixture pan/tilt angles are in the **fixture's own frame**: tilt 0° = straight down, positive toward horizontal; pan 0° = wherever stage-8 zeroing put it, recorded in that fixture's calibration file. Only the GPU box converts between frames — fixtures never do geometry.
- **Topic scheme:** `el/<room>/<subsystem>/<message>` (e.g., `el/living/beam/target`). The single-room bench uses the alias **`spotlight/target`** (as printed in Docs [3](03-build-the-gimbal.md)–[5](05-teach-it-to-aim.md)); it is the same schema — rename when a second room exists. (The topic scheme governs the MQTT lane only; the production aim lane is a named native-API action, not a topic — §1.)
- **Retained vs. not:** slow-changing *state* topics are published retained (a late subscriber immediately learns the current state); high-rate *stream* topics are not retained, QoS 0 (a lost frame doesn't matter; the next one arrives in ≤100 ms).

## The topics

### 1. `spotlight/target` — aim commands (GPU box → fixture) · stream, ≤15 Hz

```json
{"v":1, "ts":1784150000000, "pan":32.5, "tilt":-14.0, "rate":30}
```

`pan`/`tilt`: absolute fixture-frame degrees. `rate`: max slew in deg/s — the motors interpolate onboard (0xA4), which is why 5–15 Hz targets produce continuous motion. **Deliberately absent: brightness.** Photometrics have exactly one write path — the HA light entity (§ "Living inside Home Assistant") — so aim messages never carry `dim`; a coordinator that wants the beam dimmer calls `light.turn_on` like everyone else.

**Two transports for this one message, split by build phase:**

- **Bench / v0: the MQTT topic above.** Trivially debuggable (`mosquitto_sub`), zero resolver code beyond a publish call. This is what Docs [3](03-build-the-gimbal.md)–[5](05-teach-it-to-aim.md) wire up.
- **Production loop: an ESPHome native-API action, called directly.** The fixture declares `api: actions: → action: fixture_aim` with typed `float pan, float tilt` variables; the resolver calls it via **aioesphomeapi** — the same Python client HA itself uses — connected *directly* to the fixture alongside HA's connection (ESP32-family nodes accept 5 concurrent API clients by default; HA uses one, the resolver one). One network hop instead of two, typed floats instead of JSON parsing, fire-and-forget (`supports_response: none`), and reconnection is solved for free (aioesphomeapi's `ReconnectLogic`: exponential backoff + instant mDNS-triggered reconnect). Note: as of ESPHome 2026.1.0, **API encryption is mandatory** — the resolver holds the same `api: encryption: key:` HA does, via a shared secrets file.
- Either way, **the Auto-mode gate lives inside the firmware action/handler** — the fixture is the only place that can authoritatively arbitrate if two callers ever collide. MQTT stays configured regardless (`discovery: false`) as the observability tap. (It is *not* an automatic failover — if the native-API session dies, the resolver's ReconnectLogic restores it; re-pointing at MQTT is a manual/ops decision, not firmware behavior.)

**Firmware watchdog rule (the WLED pattern, adapted — same design, re-tuned constant):** the aim stream *bypasses* persistent state, never overwrites it — so there's nothing to "restore." A sliding 2 s window refreshes with every target (WLED ships 2.5 s for exactly this class of stream); when it lapses in Auto, the failsafe is **two-stage**: stage 1 (immediately) — hold position, fade the light toward a floor over 1 s (internal `light.turn_on` call, reported to HA as a normal state change); stage 2 (after a further 60 s with no recovery) — glide calmly to the fixture's configured idle preset (wall art / default surface). Never hunts, never parks with a snap (story G2). `Hold` mode is the receiver-side force-ignore (WLED's "live override"): the fixture keeps listening but discards targets — protection that doesn't depend on a possibly-hung resolver cooperating.

### 2. `spotlight/state` — fixture telemetry (fixture → anyone) · retained, 1 Hz + on-change

```json
{"v":1, "ts":..., "pan":32.4, "tilt":-13.9, "moving":false, "temp_c":41, "fault":null}
```

Read-back angles come from the motors' encoders (0x92), so this is ground truth, not an echo of commands. `fault`: null or a short string (`"can_timeout"`, `"overtemp"`, …) — the coordinator treats any non-null fault as "stop sending targets, alert."

### 3. `el/<room>/tracks` — live people (tracker → resolver/observers) · stream, 15–30 Hz

```json
{"v":1, "ts":..., "tracks":[
  {"id":7, "pos":[2.31,1.04,0.0], "vel":[0.9,-0.1], "head":[2.28,1.02,1.62],
   "posture":"walking", "conf":0.93}
]}
```

`pos` is the ground-plane anchor (z = 0 by construction); `head` feeds the safety cones; `vel` feeds prediction; `id` is stable for the life of the track (ByteTrack), not a person's identity. `posture`: `walking | standing | seated | unknown`. Consumers must tolerate tracks appearing/vanishing between messages.

### 4. `el/<room>/context` — activity state (context model → resolver/coordinator) · retained, on-change

```json
{"v":1, "ts":..., "activity":"reading", "zone":"couch", "conf":0.81,
 "phase":"sustained", "people":1}
```

`activity` enum (extend deliberately, never rename): `reading | cooking | tv | movie | gathered | working | transit | sleeping | away | unknown`. `phase`: `onset | sustained | winding_down` (straight from the perception stack's temporal trajectory). **Consumers must expect this topic to lag reality by seconds-to-tens-of-seconds** (slow path) — anything needing sub-second reaction belongs on `tracks`, not `context`.

### 5. `el/<room>/beam/assignments` — who's lighting what (resolver → observers) · retained, on-change

```json
{"v":1, "ts":..., "assignments":[{"fixture":"spot1", "target":"track:7", "story":"A1"}]}
```

Pure observability — nothing acts on it, but debugging multi-fixture behavior without it is misery, and it's the log that explains "why did the light move?" (the auditability promised by the Engineered Lighting strategy roadmap — an internal doc outside this series).

### 6. `el/<room>/perception/status` — the dead-man's switch (tracker → fixtures/coordinator) · retained, 1 Hz

```json
{"v":1, "ts":..., "ok":true, "cameras":1, "fps":22}
```

Heartbeat. Fixture firmware treats a stale (>3 s) or `"ok":false` status the same as the target watchdog firing: hold, fade toward the floor, wait. This is the interlock from story G2, implemented as one retained topic.

### 7. Lights & scenes — via Home Assistant, not MQTT

The 7 tunable zones and the spotlight's brightness/CCT are ESPHome **light entities**; the coordinator sets moods through HA scenes/services (Movie, Reading…). Rationale: HA already gives lights transitions, state history, dashboards, and manual override for free — MQTT is reserved for the two things HA's pipeline is too slow for (aim targets) or that HA doesn't model (tracks, context, interlocks).

## Living inside Home Assistant — the dual-control architecture

The spotlight must be an ordinary HA citizen *and* autonomous. Those coexist only with a strict ownership split: **one write path per concern.**

**The fixture's entity set in HA** (all via ESPHome's native API):

| Entity | Type | Who uses it |
|---|---|---|
| `light.spot1` | light (brightness + CCT) | Everyone — knobs, groups, scenes, voice, *and the coordinator* (via `light.turn_on` service calls) |
| `select.spot1_mode` | select: `Auto / Hold / Manual` | Humans and coordinator. Firmware obeys aim targets **only in Auto** — autonomy is a visible switch, not an invisible force (story G4). (Ecosystem idiom check: Frigate exposes exactly this as its `ptz_autotracker` switch; our select adds the Hold state) |
| `select.spot1_preset` | select: named aim presets (`Chair / Table / Art / …`) | One-shot recall of calibrated positions — the ONVIF `GotoPreset` / Frigate `return_preset` pattern. One preset is designated the *idle* preset: the stage-2 failsafe destination (§1 — hold-and-fade comes first, always) |
| `number.spot1_pan`, `number.spot1_tilt` | numbers (degrees) | Manual jog + calibration; writing one flips mode to Manual. (Deliberately *not* a repurposed `cover`-tilt entity — HA's developer docs explicitly warn against reusing cover for non-opening devices) |
| `sensor.spot1_*`, `event.spot1_tracking` | temp, fault; `target_acquired`/`target_lost` events | Dashboards, coordinator health checks; the event entity gives automations clean discrete hooks |

Housekeeping: ESPHome's **sub-devices** feature (2025.7.0+) lets this one physical node present as two HA devices — "Spot Ambient" (the light) and "Spot Gimbal" (mode/presets/numbers) — via `device_id:` on each entity. Worth adopting for dashboard hygiene; one caveat, spot-check `area_id` propagation on your firmware version (a 2025 bug left sub-device areas blank).

**The rules that make it work:**

1. **Photometrics: HA's light entity is the *only* brightness/CCT write path — for humans and machines alike.** The spotlight joins the room's HA light group, so scenes and absolute group commands include it for free. **One researched gotcha on knobs:** HA converts a *relative* step (`brightness_step_pct`) on a group into one **absolute** value (the members' average) before fanning out — repeated knob steps collapse all members toward the same level, destroying deliberate differences (e.g., zones at 40%, spotlight at 60% → both drift to 50%). Verified in HA core source and a worked Hue issue. Fixes, pick one: have the knob automation step **each member individually** (the community-blueprint consensus), use the `relative-brightness-light-group` community integration, or accept convergence as the desired "dim everything together" semantic. Decide per room; the architecture is agnostic.
2. **Aiming: the target lane (§1 — MQTT on the bench, direct native-API action in production) is the only pan/tilt path in Auto**; HA's automation pipeline never carries the 5–15 Hz stream (too slow, per [Doc 5](05-teach-it-to-aim.md)). Mode changes, presets, and manual jogs ride HA; the stream does not.
3. **Human-override detection is layered — context first, but never context alone** (the deep finding from Adaptive Lighting's source and HA maintainers). The mechanism, adopted from proven practice:
    - *Detector 1, always on:* the coordinator mints a recognizable `Context` for every service call it makes and listens to service-call events on its entities across all three domains — `light.turn_on`, `select.select_option`, `number.set_value` — any call whose context isn't the coordinator's own = manual override, unconditionally. No thresholds on explicit commands.
    - *Detector 2, optional:* poll actual state vs. last-commanded with **significance thresholds** (~10% brightness, ~3% CCT — Adaptive Lighting's tuned values) to catch changes that never produce an HA event (vendor apps, device-local behavior). Threshold the polling path only, never the command path.
    - *Known blind spots, guarded explicitly:* physical knobs, Zigbee-bridge restarts, and time/template-triggered automations can all present the **identical null/null context signature** (HA maintainer, verbatim: "You can't [distinguish]. Only way… is to monitor the switch itself"). Guards: ignore transitions from `unavailable/unknown` (kills restart-republish false positives), debounce briefly after own commands, and treat the knob's *own* event entity (ZHA/Z2M expose rotate events) as the authoritative "human is acting" signal where one exists.
    - *Override lifecycle (Adaptive Lighting's `autoreset` pattern):* overrides self-expire after a configurable window, the timer **restarts on continued manual activity**, remaining time is an observable attribute, and a service exists to clear it early. Every override is logged as training signal.
4. **ESPHome config gotcha, one line:** with both `api:` and `mqtt:` enabled, ESPHome also advertises entities over MQTT discovery — duplicate entities in HA. Set `mqtt: → discovery: false` (ESPHome's own docs endorse exactly this combination); the native API owns entities, MQTT stays the streaming/observability lane.
5. **Scenes may aim, sparingly:** a scene/script wanting a preset beam position selects `select.spot1_preset` (or fires one target message) and sets mode to Hold — one-shots, not streams.
6. **Local reflexes are allowed a shortcut:** ESPHome's `homeassistant:` import platform lets the fixture subscribe to an HA entity's state directly (e.g., mirror the room group's brightness as an internal sensor) — useful for purely local behaviors like ambient-proportional beam trim, without waking the resolver. Any such trim still applies itself via the fixture's own `light.turn_on` on the light entity (the §1 fade pattern), so rule 1's single write path holds and HA sees every change.
7. **Matter (product phase, one line):** Matter 1.5's pan/tilt support is scoped to *cameras only* — a Matter version of this fixture exposes a standard dimmable/CT light endpoint and keeps aiming on a vendor cluster or outside Matter entirely.

## Who publishes, who subscribes

| Topic | Publisher | Subscribers |
|---|---|---|
| `spotlight/target` | GPU box (resolver) — and *only* it, in follow mode | Fixture ESPHome node |
| *(production aim lane)* | *publisher/subscriber framing describes the MQTT bench lane; in production the resolver **calls** `fixture_aim` directly — one caller, one callee, no topic* | |
| `spotlight/state` | Fixture node | Coordinator, dashboards, calibration |
| `el/<room>/tracks` | Tracker process | Resolver, gesture layer, recorder (optional) |
| `el/<room>/context` | V-JEPA pipeline | Resolver, coordinator, HA (as sensor) |
| `el/<room>/beam/assignments` | Resolver | Dashboards, logs |
| `el/<room>/perception/status` | Tracker process | Fixture nodes, coordinator |

Manual override rule: when a human touches anything (knob, slider, scene, mode select), detected via HA's context mechanism (§ "Living inside Home Assistant"), the coordinator pauses automatic control of that entity for a cooldown — human wins, always, and the correction gets logged (it's training signal).

## Change discipline

Additive changes (new optional field, new enum value) don't bump `v`. Breaking changes (rename, unit change, semantic change) bump `v`, and publishers dual-publish `v` and `v+1` for one transition period. Every schema here has one owner process — no topic has two writers. (Clarification, since "sliders" caused confusion in review: the HA number entities **never** publish to `spotlight/target` — they ride HA per rule 2. The only second writer the topic ever sees is a human's manual test-publish from MQTT Explorer during bench debugging, and then only while the resolver is stopped.)
