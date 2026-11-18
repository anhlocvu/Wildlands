# Wildlands Online (STW-Style Audio Survival) Constitution

## Core Principles

### I. Dedicated-Server Authority
Every gameplay system that can affect another player MUST execute authoritatively on the dedicated server (`server.exe`). The server owns world geometry, player coordinates and facing, vitals (health, hunger, thirst, stamina, warmth), inventory, crafting, resource node respawns, player-built structures, wildlife AI, combat hit detection, cooldowns, accounts, and moderation state. The client (`client.exe`) owns only local key state, menus, message buffers, audio mix layers, and listener orientation. Single-player mode MUST run by launching and connecting to the dedicated server on `localhost` so there is only one network code path.

### II. Screen-Reader-First Spatial Audio & Accessibility
All gameplay and interface interactions MUST be 100% playable without sight or graphical output. Speech MUST default to the player's active screen reader (`screen_reader_speak()`) with built-in engine TTS fallback, explicit interruption priorities, a repeat-last-line key, and persistent multi-channel message buffers (`All`, `Chat`, `Messages`, `Social`, `Game`, `System`). Positional audio MUST use real 3D coordinates `(X, Y, Z)` via a patched float-precision `sound_pool` and `rotation.nvgt`; using pitch shifting to represent elevation or distance is strictly prohibited (behind-only subtle pitch cue of ~3% is permitted solely to resolve front/back confusion). Turning defaults to compass snapping (`45°` / `90°` configurable) with smooth turning on a modifier key, while world targets and hazards are always described relative to the player's facing.

### III. Real Verified Audio Assets Only
Synthesized placeholder tones or generated Python sine-wave beeps are strictly prohibited. Every interface, movement, survival, building, combat, wildlife, ambient, and multiplayer sound MUST be sourced from real recorded audio (CC0 or permissive open licenses with attribution recorded), byte-verified for genuine audio container/codec headers and deduplicated by hash, loudness-normalized across a prioritized 7-layer mix (`Speech > Self > Threat > Actors > World > Ambience > Music`), and validated at client startup via a sound manifest.

### IV. Wire, Security & Persistence Safety
Network traffic MUST be separated across six ENet channels (`CH_SPEECH`, `CH_AUDIO`, `CH_CONTROL`, `CH_CHAT`, `CH_SNAPSHOT`, `CH_INPUT`) so urgent speech and sound events are never blocked behind chat or bulk state. Every delimited protocol message and stored record MUST use `wire_escape()` / `wire_unescape()`, `split_keep_empty()`, range-clamped numeric parsing (`safe_int`, `safe_double`), strict name sanitization (`sanitize_name`), protocol version negotiation on handshake, and earshot-scoped snapshots (anti-ESP). Client profiles, settings, bindings, and per-server credential wallets MUST live in the per-user application data directory (`DIRECTORY_PREFERENCES`) and NEVER store plaintext passwords. Server account stores MUST use salted stretched SHA-256 password hashes, `random_bytes(32)` bearer tokens hashed server-side, constant-time comparison, rate limiting, and atomic temp + `.bak` saves where a corrupt account file fails fatally at startup with an `alert()` rather than overwriting player data.

### V. SpecKit & Non-Disruptive Verification Gates
All development MUST strictly follow the SpecKit workflow (`constitution -> specify -> plan -> tasks -> implement`) and maintain living engineering logs in `GEMINI.md` and `docs/`. Every NVGT program MUST compile cleanly with `nvgt -c` before handoff. Automated checks in `tools/` MUST use `#pragma console`, MUST NOT call `show_window()` or steal focus, MUST NOT play sound unless explicitly flagged, MUST poll conditions with hard deadlines rather than fixed sleeps, MUST clean up any spawned server processes in failure paths, and MUST return a non-zero exit code on any assertion failure.

## Technical & Architectural Constraints

- **Engine & Language**: NVGT (NonVisual Gaming Toolkit) `0.90.0-dev` (AngelScript) for Windows x64 (`nvgt.exe` / `nvgtw.exe`).
- **Repository Layout**: Shared protocol, math, map schema, constants, and recipes under `src/common/`; dedicated server under `src/server/`; client under `src/client/`; offline and multi-client console checks under `tools/`; design specifications under `docs/` and `specs/`; verified `.ogg` audio assets and manifest under `sounds/`; data-driven world maps and server configs under `maps/` and `data/`.
- **Data-Driven World & Maps**: Maps MUST reside in external `.map` text files shared by server and builder tools so geometry never diverges between simulation and audio presentation.
- **No Unverified Engine Calls**: Any NVGT API signature MUST be verified against `C:\nvgt\include\` or local engine C++ source (`nvgt_src`) before use.

## Development Workflow & Quality Gates

- Before writing implementation code for any new system or feature, specification (`spec.md`), design (`plan.md`, `contracts/`, `data-model.md`, `docs/`), and breakdown (`tasks.md`) MUST be reviewed and approved.
- Large features MUST be implemented incrementally by prioritized user story (`P1` through `P6`), verifying compilation (`nvgt -c`) and console checks (`nvgt tools/...`) after each phase.
- All moderation actions MUST enforce rank hierarchy (`nobody moderates sideways or upwards`), and developer rank MUST require server-owned authorization rather than runtime promotion or client-only flags.

## Governance

This Constitution supersedes ad-hoc design choices across `Wildlands Online`. Amendments require updating this document, bumping the semantic version (`MAJOR.MINOR.PATCH`), updating affected design documents in `docs/` and `specs/`, and noting the change in `GEMINI.md`. Every code review, task checklist, and pre-delivery verification pass MUST confirm adherence to Principles I–V.

**Version**: 1.0.0 | **Ratified**: 2026-11-18 | **Last Amended**: 2026-11-18
