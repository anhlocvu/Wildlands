# Implementation Plan: STW-Style Tracking, 3D Verticality, Multi-Map Builder & Staff Operations

**Branch**: `002-staff-multimap-builder-tracking-verticality` | **Date**: 2026-11-18 | **Spec**: [spec.md](file:///C:/Users/LCBoy/Desktop/data/stw/specs/002-staff-multimap-builder-tracking-verticality/spec.md)
**Input**: Approved feature specification and user clarifications (English in-game language, `<= 30` tile tracker list scan, staircase climbing plays builder-selected surface footsteps).

## Summary

Upgrade **Wildlands Online** to full STW-style spatial gameplay and server administration:
1. **Tracker Rebuild**: Replace legacy `T` radar with 6-category STW tracker (`All`, `Objects`, `Items`, `Animals`, `Structures`, `Players`) capped at `<= 30` tiles, navigated by `Ctrl+=`/`Ctrl+-` and `=`/`-`, locked with `Backspace` (live 3D radar beacon via `sound_pool`), read on demand with `O`, and stopped with `Shift+Backspace`.
2. **3D Verticality & Physics**: Box-based `min_x..max_z` map geometry (`Z` in `[-50..100]`), true Air/Void detection when no floor supports the player, `PageUp`/`PageDown` staircase climbing playing the staircase's configured `surface` footsteps, falling wind cues, height-scaled fall damage, fracture debuff curable via bandage/splint, deep-water cushioning, and void death.
3. **Multi-Map Server**: Concurrent `MapInstance` worlds loaded from `maps/*.map`, map-scoped snapshots/audio/chat/objects, Map Travel Portals (`D`), and a second interconnected multi-story/cavern map (`skywatch_citadel.map`).
4. **STW F8 Map Builder**: Multi-category Builder Hub Menu (`F8`), Create New Map form, Switch Map, 6-axis box forms for all elements, Line Manager (browse, filter, form-edit, raw-edit, duplicate, insert, reorder, teleport-to, delete), Undo stack, and atomic save + hot-reload.
5. **Professional Staff Panel (`F9`)**: Categorized Staff Menu with full Account Directory (`Online (<Map>, <Zone>)` vs `Last seen: <relative + timestamp>`), direct target action pickers (no typed item IDs/command syntax required), safe `Shutdown` & `Restart` countdown lifecycle, maintenance lock, live MOTD/Changelog edits, telemetry, audit log viewer, player `/report`, and `/sc` staff chat.
6. **Verified Audio & Manuals**: Expand `tools/asset_pipeline.py` for new CC0/open recordings + write `docs/BUILDER_GUIDE.md` and `docs/STAFF_GUIDE.md` + in-game guide reader.

## Technical Context

**Language/Version**: NVGT `0.90.0-dev` (AngelScript) + Python `3.11.9` + `ffmpeg 8.1`
**Primary Dependencies**: NVGT built-ins (`network`, `sound`, `mixer`, `audio_low_pass_filter`, `form`, `menu`, `rotation`, `calendar`, `run`), `common/` shared modules (`constants.nvgt`, `wire.nvgt`, `compass.nvgt`, `protocol.nvgt`, `map.nvgt`, `items.nvgt`)
**Storage**: Atomic `.dat`/`.bak` flat files (`accounts.dat` v2 with v1 upgrade, `world_objects.dat`, `reports.dat`, `maps/*.map` + `.bak`); Client AppData INI (`settings.ini`, `wallet.ini`)
**Testing**: `#pragma console` check suite in `tools/` (`common_check.nvgt`, `map_check.nvgt`, `auth_check.nvgt`, `asset_check.nvgt`, `client_profile_check.nvgt`, `net_integration_check.nvgt`, `client_ui_e2e_check.nvgt`) + `nvgt -c` clean EXE builds
**Target Platform**: Windows x64 (`server/server.exe` & `client/client.exe`), 100% English screen-reader-first UI & audio
**Performance Goals**: 30 Hz server tick (`<15ms`), 15 Hz earshot/map-scoped snapshots (`<= 1350` UDP bytes), immediate local footstep/climb feedback
**Constraints**: Zero synthetic audio placeholders, NEVER use pitch for elevation/distance, strict rank hierarchy (`nobody moderates sideways or upwards`), strict no-window/no-sound automated tests

## Constitution Check

- **I. Dedicated-Server Authority**: PASS — Server owns map instances, air/gravity/fall damage, stair clamping, portals, line manager mutations, moderation, shutdown/restart. Client owns only tracker selection/local radar beacon, UI menus/forms, and input state.
- **II. Screen-Reader-First Spatial Audio**: PASS — English-only clean speech, non-graphical arrow menus & `audio_form` inputs, real 3D XYZ coordinates, surface footsteps on stairs, no pitch-for-elevation.
- **III. Real Verified Audio Assets Only**: PASS — All new `.ogg` files fetched via `tools/asset_pipeline.py` from verified CC0/open sources, header-verified, MD5-deduplicated, LUFS-normalized.
- **IV. Wire, Security & Persistence Safety**: PASS — `PROTO_VERSION` bumped to `2`, escaping/clamping preserved, `DEV` strictly gated by server `data/devs.txt`, atomic `.tmp`/`.bak` saves before shutdown/restart/map overwrite.
- **V. SpecKit & Non-Disruptive Verification Gates**: PASS — Full SpecKit 002 workflow (`spec -> plan -> tasks -> implement`), console-only checks in `tools/`, `nvgt -c` gate on both executables, engineering logs updated in `GEMINI.md`.

## Project Structure

### Documentation (this feature)

```text
specs/002-staff-multimap-builder-tracking-verticality/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── checklists/requirements.md
├── contracts/
│   ├── protocol.md
│   ├── map-format.md
│   └── persistence-format.md
└── tasks.md
```

### Updated & New Source Files

```text
common/
├── constants.nvgt         # PROTO_VERSION=2, TRACKER_MAX_DIST=30.0, IN_CLIMB_UP/DOWN, Z bounds [-50..100]
├── items.nvgt             # Add splint item & recipe (fracture cure) + builder surface helpers
├── protocol.nvgt          # Multi-part packet helpers for Staff/Builder lists & epoch formatting helper
└── map.nvgt               # 6-axis box platforms/stairs/zones/waters/walls, Portals (D), Hazards (H), Air/Support check, raw_lines Line Manager engine

server/
├── server.nvgt            # Multi-map startup loader, --bind-delay-ms, lifecycle shutdown/restart countdown, map-scoped snapshots, extended input mask
├── maps/
│   ├── wildlands_valley.map   # Ground floor box 0..120 z=0..0, stairs, hazards, portal to skywatch_citadel
│   └── skywatch_citadel.map   # New interconnected multi-story & underground (-10..20) map with air drops & stairs
└── includes/
    ├── logger.nvgt        # Ring buffer of recent audit lines for Staff Panel viewer
    ├── accounts.nvgt      # v2 fields (last_seen_epoch, created_at_epoch, current_map, last_ip) + v1 compat + reports store
    ├── state.nvgt         # MapInstance class, multi-map lookup, player fracture & climb state, lifecycle state
    ├── world.nvgt         # Air/gravity/fall damage/fracture, PageUp/PageDown stairs surface steps, hazards, portals, map-scoped nodes/drops
    ├── wildlife.nvgt      # Map-scoped AI simulation per MapInstance
    ├── combat.nvgt        # Map-scoped combat, respawn on current/default map, fall/void deaths
    ├── chat_social.nvgt   # Map-scoped local chat, /sc staff chat, /report incident filing, map info in WHO
    ├── builder_srv.nvgt   # Create map, switch map, box forms add/edit, Line Manager CRUD + raw edit + undo + backup + hot reload
    └── admin_dev.nvgt     # Categorized Staff Panel handlers (Account Directory, target actions, Lifecycle Shutdown/Restart, Telemetry, Logs, Reports)

client/
├── client.nvgt            # Retire T scanner, wire tracker keys (Ctrl+=/Ctrl+-, =/-, Backspace, Shift+Backspace, O), unbind PageUp/PgDn from buffers, F8 Builder Menu, F9 Staff Panel
└── includes/
    ├── profile.nvgt       # Add tracker/staff keybinds in reset_keybinds()
    ├── net_client.nvgt    # Multi-map transfer handling, Staff Panel state caches, Builder Line Manager caches, Tracker state integration
    ├── audio_engine.nvgt  # Roof/indoor rain low-pass muffling, new tracker/fall/portal cues
    ├── tracker.nvgt       # NEW: STW-style 6-category <=30 tile scanner, live 3D radar beacon loop, O readout
    ├── radar_hud.nvgt     # Clean vitals/coords/compass & sonar V (legacy scanner removed)
    ├── builder_ui.nvgt    # STW-style F8 Builder Hub, Create Map form, 6-axis Box Forms, Line Manager UI, Sound Picker with Preview
    ├── staff_ui.nvgt      # NEW: Multi-category Staff Panel UI (Accounts w/ Online vs Last seen, Target Actions, Lifecycle, World, Entities, Teleport, Logs/Reports, Guides)
    └── menus.nvgt         # Pause/Social menu links to Staff Panel & Builder Hub + In-Game Guide reader

docs/
├── BUILDER_GUIDE.md       # NEW: Complete STW Audio Map Builder & 3D Verticality Manual
├── STAFF_GUIDE.md         # NEW: Complete Staff Operations, Moderation & Server Lifecycle Manual
├── CONTROLS.md            # Updated keybindings (Tracker, Stairs, F8 Builder Hub, F9 Staff Panel)
├── PROTOCOL.md            # Synced with v2 wire packets
└── ARCHITECTURE.md        # Updated with Multi-Map, Air Physics & Restart lifecycle
```
