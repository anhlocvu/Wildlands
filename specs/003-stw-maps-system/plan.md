# Implementation Plan: STW Maps System

**Branch**: `003-stw-maps-system` | **Date**: 2026-11-18 | **Spec**: [spec.md](file:///C:/Users/LCBoy/Desktop/data/stw/specs/003-stw-maps-system/spec.md)
**Input**: Approved feature specification and user confirmations (Approach A ms respawn timer, `/maps` for Builder+, 100% dynamic species list from server, `wildlands_valley.map` spawn zones outside safe zone, all 6 STW Maps System enhancements).

## Summary

Deliver the **STW Maps System** across `Wildlands Online`:
1. **Dynamic Map-Scoped Animal Spawn Zones (`E`)**: Remove global server wildlife auto-spawning and Staff Panel spawner menus; add `E` 6-axis box spawn lines in `.map` with shared `ms` respawn timer (Approach A), target quantity, dynamic server-synced creature checkbox list (`audio_form::create_list(..., true)`), leash-to-zone option, and day/night schedule; author initial zones on `wildlands_valley.map` outside safe zones while keeping `skywatch_citadel.map` and `anhloc.map` spawn-free.
2. **Unified `/maps` Navigation & Builder Teleport Removal**: Remove map teleportation from `F8 -> Switch Active Builder Map` (edit-only switching) and cross-map `lm_tp`; add `/maps` (and `/map`) restricted to `RANK_BUILDER+` plus **View All Maps (`/maps`)** inside `F9 Staff Panel`, opening one shared server map list menu that teleports to the chosen map's spawn on `Enter`.
3. **Silent Ambience Default & Full STW Maps System**: Remove ambient loop selection from `Create New Map` (default `"none"` with zero forced forest fallback); add `M` map rules (`allow_build`, `weather_enabled`, `time_mode`), `Z` acoustic reverb presets via NVGT `audio_freeverb_node`, Builder 2-Corner Coordinate Clipboard (auto-filling 6-axis Box Forms) & Line Manager `Ping Bounds`, Create Map Templates (`Flat Ground`, `Void Sky`, `Enclosed Arena`, `Underground Cave`) + `Clone Map`, and clean same-map internal portals (`D`).

## Technical Context

**Language/Version**: NVGT `0.90.0-dev` (AngelScript) + PowerShell / `tools/run_checks.ps1`
**Primary Dependencies**: NVGT `audio_form` (`create_list` multiselect), `menu`, `audio_freeverb_node`, `sound_pool`, `rotation`, `network`, shared `common/` modules
**Storage**: `.map` v3 text files (backward-compatible v1/v2 parsing) with atomic `.tmp`/`.bak` saves under `server/maps/`
**Testing**: `#pragma console` test suite (`tools/common_check.nvgt`, `tools/map_check.nvgt`, `tools/asset_check.nvgt`, `tools/net_integration_check.nvgt`, `tools/client_ui_e2e_check.nvgt`) + `nvgt -c` clean EXE builds
**Target Platform**: Windows x64 (`server/server.exe` & `client/client.exe`)
**Performance Goals**: 30 Hz tick loop (`<15ms` worst tick), 15 Hz earshot/map-scoped snapshots (`<= 1350` UDP bytes), clean zero-CPU bypass when zone reverb is `"none"`
**Constraints**: Zero hardcoded species lists, zero synthetic audio cues, strict `RANK_BUILDER+` enforcement on `/maps` and `BUILDMAP`, clean console-only tests (no `show_window()` or audio in `tools/`)

## Constitution Check

- **I. Dedicated-Server Authority**: PASS — Server owns `E` animal spawn timers, species validation, leash bounds, `allow_build`/`weather`/`time_mode` map rules, `/maps` permission & transfer, and map mutations.
- **II. Screen-Reader-First Spatial Audio**: PASS — English-only UI/speech, `audio_form` multiselect checkbox list (`Space` toggles, `Up/Down` reads state), `audio_freeverb_node` acoustic reverb without pitch-elevation hacks, 3D `Ping Bounds` preview in Line Manager.
- **III. Real Verified Audio Assets Only**: PASS — Reuses verified `.ogg` sounds from `client/sounds/manifest.txt`; silent `"none"` mode cleanly fades/stops ambient loops.
- **IV. Wire, Security & Persistence Safety**: PASS — `PROTO_VERSION = 3` (or clean protocol sync for updated `BUILDMAP`/`MAPS` packets), `wire_escape`/`safe_int`/`safe_double`, atomic `.tmp`/`.bak` map writes, rank checks on `/maps` & `BUILDMAP`.
- **V. SpecKit & Non-Disruptive Verification Gates**: PASS — Full SpecKit `003` artifacts, TDD console tests, clean `nvgt -c` builds, `run_checks.ps1` exit `0`, updated `docs/` & `GEMINI.md`.

## Project Structure

### Documentation (this feature)

```text
specs/003-stw-maps-system/
├── spec.md
├── checklists/requirements.md
├── research.md
├── plan.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── map-format.md
│   └── protocol.md
└── tasks.md
```

### Modified Source Files

```text
common/
├── constants.nvgt         # PROTO_VERSION = 3, spawn/reverb/template constants
├── items.nvgt             # Dynamic SpeciesDef registry helpers (no UI hardcoding)
└── map.nvgt               # MapAnimalSpawn (E), MapRules (M v3 fields), Zone reverb_preset, templates & clone helpers

server/
├── server.nvgt            # Remove global target_wildlife spawning, wire MAPS packet, per-map time/weather snapshot flags
├── maps/
│   └── wildlands_valley.map # Author E animal spawn zones outside Safe Zone (skywatch_citadel & anhloc untouched)
└── includes/
    ├── state.nvgt         # WildlifeMob spawn_zone_idx + leash bounds; MapInstance runtime spawn timer arrays
    ├── wildlife.nvgt      # Dynamic E-zone Approach A ms respawn loop, leash/safe-zone bounds, day/night schedule
    ├── world.nvgt         # Enforce allow_build, weather_enabled, time_mode; clean same-map portal messaging
    ├── builder_srv.nvgt   # Dynamic BM_SPECIES sync, create_map w/o ambience + templates, clone_map, edit_only select_map, E add/edit box, same-map lm_tp guard
    └── admin_dev.nvgt     # Remove spawner & set_wildlife; implement MAPS|list & MAPS|tp (RANK_BUILDER+)

client/
├── client.nvgt            # Wire g_net.maps_menu_pending handler + 2-corner clipboard hotkeys in builder cursor
└── includes/
    ├── net_client.nvgt    # SpeciesEntry[] dynamic cache, ServerMapEntry[] /maps cache, 2-corner clipboard state, MAPS_LIST & BM_SPECIES handlers, silent ambience handling
    ├── audio_engine.nvgt  # Silent "none" ambience stop/fade, dedicated mix_steps, NVGT audio_freeverb_node zone reverb presets
    ├── chat_input.nvgt    # /maps & /map command (RANK_BUILDER+)
    ├── builder_ui.nvgt    # Animal Spawn Zone form (dynamic checkbox list!), create_map w/o ambience + template, clone_map, edit-only switch_map, 2-corner auto-fill, Ping Bounds, reverb/map-rule fields
    ├── staff_ui.nvgt      # Remove spawner & wildlife count; add "View All Maps (/maps)" calling shared run_server_maps_menu()
    └── tracker.nvgt       # Include E zones or keep live spawned mobs in Animals (existing live ents handles Animals!)

docs/
├── BUILDER_GUIDE.md
├── STAFF_GUIDE.md
├── CONTROLS.md
└── PROTOCOL.md

tools/
├── map_check.nvgt
├── net_integration_check.nvgt
└── client_ui_e2e_check.nvgt
```
