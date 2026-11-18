---
description: "Actionable dependency-ordered tasks for Feature 003 (STW Maps System)"
---

# Tasks: STW Maps System

**Input**: Design documents from `/specs/003-stw-maps-system/`
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`

## Phase 1: Foundational Schema & Core Data Structures (`common/`)

- [x] T001 Update `common/constants.nvgt`: bump `PROTO_VERSION = 3`, `GAME_VERSION = "3.0.0"`, add reverb preset constants/limits
- [x] T002 Update `common/map.nvgt`:
  - Add `MapAnimalSpawn` (`E`) parser, serializer `make_e_line`, validation (require non-empty species list), Line Manager summary & anchor support, and filter support
  - Extend `M` header (`allow_build`, `weather_enabled`, `time_mode`) with backward-compatible v1/v2 parsing and `"none"` silent ambience support
  - Extend `Z` zone (`reverb_preset`: `none|room|hall|cave`) with backward-compatible parsing
  - Add map template generator helper for `flat`, `void`, `arena`, `cave`
- [x] T003 [P] Add unit tests in `tools/map_check.nvgt` and `tools/common_check.nvgt` for `E` Animal Spawn Zones, `M` v3 flags, `Z` reverb presets, `"none"` silent ambience, and Line Manager CRUD on `E` (TDD RED)

---

## Phase 2: User Story 1 — Dynamic Map-Scoped Animal Spawn Zones (Priority: P1)

**Goal**: Eliminate global wildlife auto-spawning; drive all wildlife purely from per-map `E` zones with Approach A shared `ms` timer and dynamic server-synced species checkbox picker in F8 Builder.

### Tests (Write First)
- [x] T004 [US1] Extend `tools/net_integration_check.nvgt` to verify: blank/test maps spawn 0 wildlife, `BUILDMAP|hub_sync` emits `BM_SPECIES` dynamically matching `g_species`, creating an `E` spawn line (`interval_ms = 1200`, `count = 3`) waits 1200ms before spawning 3 randomized species, and Approach A refills 1200ms after killing 1 mob

### Implementation
- [x] T005 [US1] Update `server/includes/state.nvgt`: add `spawn_zone_idx` + leash bounds on `WildlifeMob`, and runtime `animal_spawn_next_ms[]` / `animal_spawn_waiting[]` on `MapInstance`; remove unused `target_wildlife` global default dependency
- [x] T006 [US1] Rewrite `server/includes/wildlife.nvgt`: remove `wildlife_set_target_count` auto-spawner; implement `wildlife_sync_map_spawns()` and Approach A shared `ms` countdown per `MapAnimalSpawn` (`E`) zone, random selection across zone's checked species, safe-floor/wall-free box placement, leash bounds enforcement + safe-zone exclusion, and `day|night|always` schedule
- [x] T007 [US1] Update `server/server.nvgt` & `server/includes/admin_dev.nvgt`: remove startup global wildlife call and remove `STAFF|spawn_mob`, `STAFF|world|wildlife`, and `DEV|set_wildlife`
- [x] T008 [US1] Update `server/maps/wildlands_valley.map`: author balanced `E` Animal Spawn Zones across non-safe zones (`Southern Meadow`, `Quarry Ridge`, `Whispering Woods`, `Riverside Crossing`), keeping `Settlement Clearing` safe zone and test maps (`skywatch_citadel.map`, `anhloc.map`) free of `E` spawns
- [x] T009 [US1] Update `server/includes/builder_srv.nvgt`: emit dynamic `BM_SPECIES` list from `g_species` during `hub_sync`, support `add_box|animal_spawn` & `lm_replace_box` for `E`, reconcile `wildlife_sync_map_spawns()` on live reload/edit
- [x] T010 [US1] Update `client/includes/net_client.nvgt`, `client/includes/staff_ui.nvgt`, `client/includes/menus.nvgt`, and `client/includes/builder_ui.nvgt`:
  - Remove `"Spawn Wildlife or Practice Bots"` and `"Set Target Wildlife Count"` from `staff_ui.nvgt` and `menus.nvgt`
  - Parse `BM_SPECIES` dynamically in `net_client.nvgt`
  - Add `"Animal Spawn Zone"` (`E`) form to `builder_ui.nvgt` with `Label`, `Min X`, `Max X`, `Min Y`, `Max Y`, `Min Z`, `Max Z`, `Spawn Delay (ms)`, `Spawn Quantity`, `Leash to Zone` checkbox, `Active Time`, **multi-select checkbox `create_list(..., true)` populated dynamically from server species**, and `"Create Animal Spawn Zone"` button + Line Manager edit/filter (`E`)

---

## Phase 3: User Story 2 — `/maps`, Staff "View All Maps", & Builder Teleport Removal (Priority: P2)

**Goal**: Remove map teleportation from Builder and provide unified `/maps` (Builder+) and Staff Panel `View All Maps` server map browser & instant teleport.

### Tests (Write First)
- [x] T011 [US2] Extend `tools/net_integration_check.nvgt` to verify: `BUILDMAP|select_map` never teleports player, `/maps` (`MAPS|list` & `MAPS|tp`) denies rank `0` players and teleports `RANK_BUILDER+` cleanly to target map spawn

### Implementation
- [x] T012 [US2] Update `server/includes/builder_srv.nvgt` & `client/includes/builder_ui.nvgt`: strip teleport option from `bm_switch_map_menu` and `select_map` (edit-only switching); restrict `lm_tp` to the map the builder is currently standing on
- [x] T013 [US2] Update `server/includes/admin_dev.nvgt` & `server/server.nvgt`: implement `MAPS|list` -> `MAPS_LIST` and `MAPS|tp|<slug>` restricted to `ps.rank >= RANK_BUILDER` (also syncing `builder_edit_map = dest.slug`)
- [x] T014 [US2] Update `client/includes/net_client.nvgt`, `client/includes/chat_input.nvgt`, `client/includes/staff_ui.nvgt`, and `client/client.nvgt`:
  - Parse `MAPS_LIST`, add shared `run_server_maps_menu(NetClient@ nc)` menu (Enter teleports to map spawn)
  - Wire `/maps` (and `/map`) for `RANK_BUILDER+` in `chat_input.nvgt` and `client.nvgt`
  - Add `"View All Maps (/maps)"` in `staff_ui.nvgt` calling `run_server_maps_menu(nc)`

---

## Phase 4: User Story 3 — Silent Create-Map Default & Complete STW Maps System (Priority: P3)

**Goal**: Remove ambience loop selection on Create New Map (silent `"none"` default), enforce map rules (`allow_build`, `weather_enabled`, `time_mode`), integrate NVGT `audio_freeverb_node` zone acoustics, 2-Corner Coordinate Clipboard & Line Manager Bounds Ping, Create Map Templates & Clone Map, and clean internal same-map portals.

### Tests (Write First)
- [x] T015 [US3] Extend `tools/net_integration_check.nvgt` & `tools/client_ui_e2e_check.nvgt` to test: `create_map` with template defaults `ambience_default = "none"`, `allow_build = 0` rejects non-admin survival placement, `weather_enabled = 0` & `time_mode = night` apply in snapshots, `clone_map` duplicates map cleanly, same-map portal teleports smoothly, and `AudioEngine` handles `"none"` ambience + `audio_freeverb_node` presets without error

### Implementation
- [x] T016 [US3] Update `server/includes/world.nvgt`, `server/includes/builder_srv.nvgt`, and `server/server.nvgt`:
  - Enforce `allow_build` in `builder_place_structure`, per-map `weather_enabled` and `time_mode` in `world_step_vitals_and_env` & `send_scoped_snapshots`
  - Support `create_map` without ambience (sets `"none"` + builds chosen template `flat|void|arena|cave`), `edit_header` v3 rules, `clone_map`, and clean same-map portal speech/cue
- [x] T017 [US3] Update `client/includes/audio_engine.nvgt` & `client/includes/net_client.nvgt`:
  - Stop/fade out `amb_curr` when desired ambience is `"none"` or `""` (never fall back to forest)
  - Add dedicated `mix_steps` under `LAYER_SELF` volume and attach NVGT `audio_freeverb_node` reverb presets (`none|room|hall|cave`) across `mix_steps`, `mix_world`, `mix_actors`, `mix_threat` based on player's active `MapZone` (keeping UI cues, speech, ambience, and music dry)
- [x] T018 [US3] Update `client/includes/builder_ui.nvgt` & `client/client.nvgt`:
  - Remove ambience list from `bm_create_map_form`; add Map Template selector (`flat|void|arena|cave`)
  - Add `allow_build`, `weather_enabled`, `time_mode` controls to `bm_edit_header_form` and `reverb_preset` selector + `"None (Silent)"` ambience option to `zone` form
  - Add `Clone Active Map` menu/form in Builder Hub
  - Add 2-Corner Coordinate Clipboard (`Set Corner 1 Here`, `Set Corner 2 Here`, `Clear Corners`, plus cursor `M` / `Shift+M` support) auto-filling `Min X..Max Z` on new 6-axis box forms
  - Add `Ping Element Bounds (3D Audio)` inside Line Manager actions menu

---

## Phase 5: Verification, Code Review, Documentation & Logs (ECC Gate)

- [x] T019 Update [docs/BUILDER_GUIDE.md](file:///C:/Users/LCBoy/Desktop/data/stw/docs/BUILDER_GUIDE.md), [docs/STAFF_GUIDE.md](file:///C:/Users/LCBoy/Desktop/data/stw/docs/STAFF_GUIDE.md), [docs/CONTROLS.md](file:///C:/Users/LCBoy/Desktop/data/stw/docs/CONTROLS.md), and [docs/PROTOCOL.md](file:///C:/Users/LCBoy/Desktop/data/stw/docs/PROTOCOL.md)
- [x] T020 Run `nvgt -c server/server.nvgt` & `nvgt -c client/client.nvgt` and execute full `tools/run_checks.ps1` suite (100% PASS)
- [x] T021 Perform code quality & security review across all touched files, then update `GEMINI.md` engineering log
