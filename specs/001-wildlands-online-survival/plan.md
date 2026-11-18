# Implementation Plan: Wildlands Online (STW-Style Audio Survival)

**Branch**: `001-wildlands-online-survival` | **Date**: 2026-11-18 | **Spec**: [spec.md](file:///C:/Users/LCBoy/Desktop/data/stw/specs/001-wildlands-online-survival/spec.md)
**Input**: Feature specification from `/specs/001-wildlands-online-survival/spec.md`

## Summary

Build **Wildlands Online**, an STW-inspired multiplayer online 3D survival audio game in NVGT `0.90.0-dev` with a dedicated authoritative server and separate accessible client sharing common protocol, math, map format, and recipe definitions. The system delivers persistent accounts with token wallets, 6-channel ENet networking, screen-reader-first output with SAPI fallback, 6-channel message buffers, modal `/` multi-scope chat and social controls, real-time 3D HRTF spatial audio with wall occlusion and patched float-precision `sound_pool`, survival vitals/gathering/crafting/wildlife combat, **dual builder systems** (in-game survival base building + interactive audio map builder), developer/moderation panels, interactive tutorial, and a complete library of verified, loudness-normalized real `.ogg` audio recordings.

## Technical Context

**Language/Version**: NVGT `0.90.0-dev` (AngelScript) + Python `3.11.9` + `ffmpeg 8.1` (offline audio pipeline only)
**Primary Dependencies**: NVGT built-ins (`network`, `sound`, `mixer`, `audio_low_pass_filter`, `tts_voice`, `screen_reader_speak`, `string_hash_sha256`, `random_bytes`, `settings`, `ini`, `menu`, `form`, `rotation`), vendored/adapted `wire.nvgt`, `compass.nvgt`, `buffers.nvgt`, and patched `sound_pool.nvgt`
**Storage**: Server atomic flat files (`data/accounts.dat` + `.bak`, `data/world_objects.dat` + `.bak`, `maps/*.map`, `data/motd.txt`, `data/changelog.txt`, `data/devs.txt`); Client AppData INI (`DIRECTORY_PREFERENCES("WildlandsStudio", "WildlandsOnline") + "player.ini"`)
**Testing**: Non-interactive `#pragma console` NVGT check suite in `tools/` (`common_check.nvgt`, `map_check.nvgt`, `auth_check.nvgt`, `asset_check.nvgt`, `net_integration_check.nvgt`) + `nvgt -c` clean compilation gates
**Target Platform**: Windows x64 (`nvgt.exe` / `nvgtw.exe`) with Windows screen readers (NVDA/JAWS/Narrator) & SAPI fallback
**Project Type**: Dual-executable online game (`server` + `client` + shared `common/`) + offline console tools & audio pipeline
**Performance Goals**: Server 30 Hz fixed simulation tick (`<15ms` worst tick), 15 Hz earshot-scoped snapshot broadcast (`<=35` tiles), UDP payloads strictly `<= 1350` bytes, client frame loop with `wait(5)` and immediate local feedback
**Constraints**: Zero graphics required, zero synthetic tone audio placeholders, linear `[0.0..1.0]` mix design converted once to NVGT dB at boundary (`PERCENTAGE_ATTRIBUTES` active on `g_audio_engine`), behind-only pitch cue (`NEVER` pitch for elevation/distance), console checks strictly no-window / no-sound / auto-exit
**Scale/Scope**: Tuned for 10–30 concurrent players (hard ceiling 50 peers), 20+ active wildlife/bots, 160x160x20 initial multi-zone wilderness map + user-created `.map` worlds

## Constitution Check

*GATE: Passed before Phase 0 research and re-verified after Phase 1 design.*

- **I. Dedicated-Server Authority**: PASS — Server owns position, facing, vitals, inventory, crafting, node respawns, structures, wildlife AI, combat, moderation, and accounts. Client sends `INPUT` bitmasks and `ACT` intents only.
- **II. Screen-Reader-First Spatial Audio**: PASS — Uses `screen_reader_speak()` + `tts_voice` fallback, `buffers.nvgt`, `compass.nvgt`, real Z coordinates, behind-only 3% pitch cue in patched `sound_pool.nvgt`, and `audio_low_pass_filter` wall occlusion.
- **III. Real Verified Audio Assets Only**: PASS — Automated `tools/asset_pipeline.py` sources CC0/open recordings, checks magic bytes + MD5 deduplication, normalizes with `ffmpeg`, and verifies against `sounds/manifest.txt` + `tools/asset_check.nvgt`.
- **IV. Wire, Security & Persistence Safety**: PASS — 6 ENet channels (`CH_SPEECH=0..CH_INPUT=5`), `wire.nvgt` escaping/splitting/clamping, salted stretched SHA-256 (`5000` rounds), `random_bytes(32)` tokens hashed server-side, AppData wallet, atomic `.tmp`/`.bak` persistence, earshot-scoped snapshots.
- **V. SpecKit & Non-Disruptive Verification Gates**: PASS — SpecKit docs complete (`constitution.md`, `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`) + `docs/*.md` suite; all checks are `#pragma console`, windowless, silent, deadline-polled, and process-clean.

## Project Structure

### Documentation (this feature)

```text
specs/001-wildlands-online-survival/
├── spec.md              # Technology-agnostic requirements & user stories P1..P6
├── plan.md              # This file (architecture, structure, milestone plan)
├── research.md          # Verified NVGT 0.90.0-dev API & sound_pool findings
├── data-model.md        # Entities, constraints, bounds, schema
├── quickstart.md        # Build, check, integration & manual playtest guide
├── checklists/
│   └── requirements.md  # Spec quality validation checklist
├── contracts/
│   ├── protocol.md      # 6-channel ENet wire protocol & message tables
│   ├── map-format.md    # Shared .map text file specification
│   └── persistence-format.md # Server accounts/objects & client INI schema
└── tasks.md             # Generated by /speckit-tasks after plan approval

docs/                    # Online Audio Game Dev design documents
├── PLAN.md              # Game vision, v1 scope, and incremental milestones
├── ARCHITECTURE.md      # Authority table, 30Hz/15Hz tick, channels, scoping
├── PROTOCOL.md          # Complete wire specification & safety rules
├── AUDIO.md             # 7-layer mix, dB boundary, spatialization & asset list
├── CONTROLS.md          # Complete keybindings (game, builder, menus, buffers)
└── ACCOUNTS.md          # Salted SHA-256, tokens, AppData wallet, guest flags
```

### Source Code (repository root)

```text
common/                    # Shared code compiled into both server & client
├── constants.nvgt         # Hosts/port constants, channels, tick rates, limits
├── wire.nvgt              # Copied & tailored from online-audio-game-dev
├── compass.nvgt           # Copied from online-audio-game-dev (wraps rotation.nvgt)
├── protocol.nvgt          # Packet builders, parsers & bounds helpers
├── map.nvgt               # .map parser, serializer, collision, occlusion, zone lookup
└── items.nvgt             # Shared items, tools, recipes, structure & wildlife tables

server/                    # Standalone Server Directory (self-contained to deploy)
├── server.nvgt            # Entry point, CLI args, windowed log, 30 Hz fixed tick
├── server.exe             # Compiled release executable (nvgt -c)
├── includes/
│   ├── logger.nvgt        # Timestamped window + rotating file log + fatal alert()
│   ├── accounts.nvgt      # Salted stretched SHA-256, tokens, atomic .dat/.bak, ranks
│   ├── world.nvgt         # Resource nodes, persistent structures, campfires, chests
│   ├── wildlife.nvgt      # Roam/flee/stalk/windup/attack AI + test bots
│   ├── combat.nvgt        # Server-authoritative melee, block, bow arrows, duels, PvP
│   ├── chat_social.nvgt   # Scoped chat, whispers, rate limit, friends, mute/ban
│   ├── builder_srv.nvgt   # Authoritative Survival Builder & Map Builder mutations
│   └── admin_dev.nvgt     # Dev panel (target-based) + ranked moderation handlers
├── maps/
│   └── wildlands_valley.map # Starter multi-zone survival wilderness + settlement
├── data/
│   ├── motd.txt           # Server message of the day
│   ├── changelog.txt      # Recent update notes sent on connect/news
│   └── devs.txt           # Authorized developer usernames (server-owned)
└── logs/                  # Runtime rotating server logs

client/                    # Standalone Client Directory (self-contained for players)
├── client.nvgt            # Entry point, state machine, main loop, network pump
├── client.exe             # Compiled release executable (nvgt -c)
├── includes/
│   ├── sound_pool.nvgt    # Vendored & patched float-precision behind-only pool
│   ├── audio_engine.nvgt  # 7-layer mixers, linear->dB boundary, occlusion, ambience
│   ├── speech.nvgt        # Screen-reader-first + SAPI fallback + repeat-last-line
│   ├── buffers.nvgt       # Copied & tailored 6-channel navigable message buffers
│   ├── profile.nvgt       # AppData INI persistence + 8-slot LRU token wallet
│   ├── ui_forms.nvgt      # Registration, Login, Server Config, Key Remap forms
│   ├── menus.nvgt         # Main, Connect, News, Settings, Inventory, Craft, Social, Dev/Mod
│   ├── chat_input.nvgt    # Modal `/` chat box with click SFX, cancel, command hints
│   ├── radar_hud.nvgt     # Status hotkeys, sonar scan, relative target scanner
│   ├── builder_ui.nvgt    # Survival build menu + Interactive Audio Map Builder cursor
│   ├── tutorial.nvgt      # Interactive step-verified audio tutorial
│   └── net_client.nvgt    # ENet pump, interpolation, scoped entity sync, reconnect
└── sounds/
    ├── manifest.txt       # Authoritative asset list checked at startup
    ├── CREDITS.md         # CC0 / open-license source URLs & attributions
    └── ... (ui/, steps/, survival/, builder/, combat/, wildlife/, ambience/, music/, multi/)

tools/
├── asset_pipeline.py      # Download, header-verify, deduplicate & ffmpeg-normalize audio
├── run_checks.ps1         # Master offline test & compile runner
├── common_check.nvgt      # Wire, compass, protocol, item/recipe assertions
├── map_check.nvgt         # Map parser, bounds, spawn, roundtrip, packet-size checks
├── auth_check.nvgt        # Salted hash, constant-time compare, token & rank hierarchy checks
├── asset_check.nvgt       # Verifies every manifest & map sound exists and is valid audio
└── net_integration_check.nvgt # Spawns temp server on :7199, tests 2 clients E2E, tears down cleanly
```

**Structure Decision**: `server/` and `client/` live in cleanly separated root directories so each folder is independently runnable and distributable (`server/` holds `server.exe`, `maps/`, `data/`, `logs/`; `client/` holds `client.exe` and `sounds/`), while `common/` shares protocol, math, map schema, and recipe definitions compiled into both executables without duplication.

## Phased Delivery Roadmap (After Plan Approval)

1. **Audio Asset Pipeline (`US6` foundation)**: Source, byte-verify, deduplicate, and `ffmpeg`-normalize real CC0 recordings for every sound category in `docs/AUDIO.md`, generating `sounds/manifest.txt` and `sounds/CREDITS.md`.
2. **Core Common & Offline Checks**: Implement `constants.nvgt`, `wire.nvgt`, `compass.nvgt`, `protocol.nvgt`, `map.nvgt`, `items.nvgt`, starter `wildlands_valley.map`, and `common_check.nvgt` / `map_check.nvgt` / `asset_check.nvgt`.
3. **Auth, World Navigation & Reconnect (`US1`)**: Server accounts/tokens/windowed logger + Client AppData wallet, forms, 7-layer audio engine, patched `sound_pool`, movement/turning/wall-bump/zone announcements, reconnect flow.
4. **Chat, Buffers & Social (`US2`)**: Modal `/` chat, 6-channel `buffers.nvgt`, `Who`, `Ping`, friends, mute/block, profiles, leaderboard.
5. **Survival, Crafting & Wildlife Combat (`US3`)**: Vitals, gathering, crafting, campfires, passive & hostile 3D wildlife AI, melee/block/bow combat, duels & death/respawn.
6. **Dual Builder Systems (`US4`)**: In-world Survival Base Building (walls, lockable doors with acoustic occlusion, chests, floors/stairs, campfires, benches, beacons) + Interactive Audio Map Builder (cursor inspection, editing, validation, `.map` export, live server reload).
7. **Operations, Tutorial, Dev Panel, Moderation & Full E2E QA (`US5`)**: Settings with live previews & key remapping, interactive tutorial, Dev Panel, ranked moderation, `net_integration_check.nvgt`, final `nvgt -c` builds & bug fixes.

## Complexity Tracking

No Constitution violations require exceptions; complexity stays tightly modularized across `src/common/`, `src/server/includes/`, and `src/client/includes/`.
