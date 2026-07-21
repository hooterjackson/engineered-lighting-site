---
title: Work With an AI Agent
description: "The AI-native lane: you do atoms, the agent does bits. Setup, how to run a stage prompt, and the one hard safety rule."
---

# Work With an AI Agent

**Engineered Lighting prototype series · July 2026**
Every software-touching stage in this series leads with a copy-paste prompt for a coding agent — Claude Code, Codex CLI, or any agent with shell access. This page is the one-time setup and the rules of engagement. The manual steps remain in every chapter as the understanding/fallback lane.

## The model

**You do atoms, the agent does bits.** Wiring, clamping, soldering, balancing, holding the payload — human hands. Toolchains, compiling, flashing, serial captures, YAML generation, log watching, test loops — agent work. The boundary runs through *plan mode*: the agent proposes, you approve, then it executes. Chapters mark the hands-on stages explicitly; everything else has an agent lane.

Each prompt block looks like this on the page — the copy button in its corner grabs the whole prompt:

!!! agent-prompt "🤖 Give this to your agent"

    ```text
    You're my bench agent. This block is an example — real ones live in the
    chapters, each one self-contained: context, plan-first, task, acceptance
    criteria, and what evidence to report back.
    ```

    *New here? You're already on the right page.*

## Setup, once

1. **Install an agent.** [Claude Code](https://claude.com/claude-code) (`npm install -g @anthropic-ai/claude-code` or the desktop app) or Codex CLI — the prompts are tool-agnostic.
2. **Make a bench repo.** Create an empty folder, `git init`, and run the agent inside it. Everything the agent writes (sketches, YAML, helper scripts) lands here, reviewable and versioned.
3. **Plug in the board** (USB-C data cable — the charge-only kind is the classic trap).
4. **Let the agent install its own toolchain.** That is literally the first prompt of [Doc 3, stage 2](03-build-the-gimbal.md#stage-2-hello-esp32-and-exactly-how-code-gets-onto-the-board) — `arduino-cli`, the ESP32 core, and whatever Python helpers it needs. Don't pre-install anything.

## How to run a stage prompt

**Claude Code:** enter plan mode (Shift+Tab or the mode picker), paste the prompt, read the plan it proposes, then approve. Plan mode is the gate — nothing executes until you've seen the plan.

**Codex (or any other agent):** the prompts carry the gate inside themselves — every one opens with *"start by proposing a plan; wait for my approval before executing."* Hold the agent to it.

Either way: give the agent this site (or the chapter URL in the prompt) as context. It reads the stage, the pins, the addresses, and the protocol notes the same way you do.

## The hard rule

Verbatim from [Doc 3](03-build-the-gimbal.md#ai-as-your-lab-partner), and repeated inside every motion-capable prompt:

!!! rules "One hard rule"
    The agent never commands motion unattended. Current limit stays set, your hand stays near the supply switch, and any agent-driven test that moves the motor happens while you watch. Agents are excellent at reading; keep the physical-safety authority human.

## What the agent reports back

Every prompt ends with a "report back" clause — serial captures, test output, a diff, a log summary. Insist on it. The evidence trail is what makes agent work reviewable, and it's what you'll paste into the *next* debugging conversation when something misbehaves. When a stage has a **Done when** line, that line is the agent's acceptance criteria too — same bar, both lanes.
