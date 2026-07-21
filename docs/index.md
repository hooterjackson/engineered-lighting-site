---
title: Home
description: "The Engineered Lighting prototype series — a silent robotic spotlight taken from research through bench build to perception and software."
hide:
  - toc
---

<div class="el-hero" markdown>

<p class="el-hero__kicker">Engineered Lighting · Engineering notebook</p>

# Building the robotic spotlight

We're building the robotic spotlight for the Engineered Lighting fixture: a silent pan/tilt head (smart CAN servo motors, absolute encoders, no homing dance) carrying a high-CRI 3-up LED spot, living alongside the fixture's tunable-white ambient zones, exposed to Home Assistant as ordinary entities *and* aimed autonomously by a camera-driven perception stack — following people, lighting task surfaces and books, pointing at art when idle, never sweeping across eyes.

This seven-document series takes it from research through a working bench prototype to the system architecture, with everything adversarially reviewed and every purchase specified.

*This is our internal engineering notebook, published openly — hardware assumptions (a CUDA GPU box for Docs [5](05-teach-it-to-aim.md)–[7](07-building-the-software.md), an existing Home Assistant install) are ours.*

<p class="el-hero__meta"><span>July 2026</span><span>7 documents</span><span>$630–945 end to end</span><span>Current phase · parts ordering</span></p>

</div>

## What we're building toward

<div class="grid cards" markdown>

-   :material-robot:{ .lg .middle } **The silent robotic spotlight**

    ---

    A pan/tilt head you can't hear: smart CAN actuators, absolute encoders, a balanced high-CRI LED payload — researched, chosen, and bench-built step by step.

    [:octicons-arrow-right-24: Docs 1–4](01-how-we-got-here.md)

-   :material-eye:{ .lg .middle } **The aiming intelligence**

    ---

    Cameras, ground-plane tracking, and beam self-calibration that follow people, light task surfaces, and never sweep across eyes.

    [:octicons-arrow-right-24: Doc 5](05-teach-it-to-aim.md)

-   :material-lan:{ .lg .middle } **The system architecture**

    ---

    The message contract every component obeys, and the software stack that runs it — testable without a living room.

    [:octicons-arrow-right-24: Docs 6–7](06-message-contract.md)

</div>

## Buying parts?

Everything the series tells you to buy, in one interactive list — check items off as you order, progress and totals persist in your browser.

[:material-format-list-checks: Open the BoM checklist](bom-checklist.md){ .md-button .md-button--primary }

## The document map

| # | Doc | What it is | You buy |
|---|---|---|---|
| 1 | [How We Got Here](01-how-we-got-here.md) | Round-1 research digest: the physics, vocabulary, and five lessons under every later decision. Archive — read for understanding | nothing |
| 2 | [Choosing the Motors](02-choosing-the-motors.md) | The decision journey to the RMD-L-4005 smart CAN actuators — what was evaluated, why integrated actuators won | (decision feeds Doc 3) |
| 3 | [Build the Gimbal](03-build-the-gimbal.md) | 10-stage bench build: motors answering on CAN by stage 4, a balanced aimed head by stage 8. Full BoM, wiring, code, AI-partner workflow | ~$340–385 |
| 4 | [Build the Full Fixture Bench](04-full-fixture-bench.md) | One ESP32-C6 running the whole fixture: 21 tunable-white channels + CC spotlight + gimbal, in ESPHome/Home Assistant | ~$170–240 |
| 5 | [Teach It to Aim](05-teach-it-to-aim.md) | The perception stack: cameras, ground-plane tracking, beam self-calibration, coordination, safety, user stories, phased roadmap (Phase 0 = a weekend) | ~$120–320 per room |
| 6 | [The Message Contract](06-message-contract.md) | The one page every component obeys: topics, schemas, units, watchdogs, and the dual-control architecture (HA entities + autonomy without fights). *When docs disagree, Doc 6 wins* | nothing |
| 7 | [Building the Software](07-building-the-software.md) | The code: pinned stack, repo layout, hardware-free testing (replay cameras, simulated fixtures), deployment, firmware growth path, licensing gates | nothing |

**Reading paths:** *Building this weekend?* → [Doc 3](03-build-the-gimbal.md), then [4](04-full-fixture-bench.md) (skim their concepts sections; Docs [1](01-how-we-got-here.md)–[2](02-choosing-the-motors.md) optional background). *Understanding the choices?* → [1](01-how-we-got-here.md) → [2](02-choosing-the-motors.md), then skim [5](05-teach-it-to-aim.md). *Writing the software?* → [6](06-message-contract.md) → [7](07-building-the-software.md), with [5](05-teach-it-to-aim.md) as the spec.

---

**Total prototype budget, all hardware:** roughly **$630–945** for one room end-to-end · **Current phase:** parts ordering / bench build
