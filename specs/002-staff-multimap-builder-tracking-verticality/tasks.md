---

description: "Actionable dependency-ordered tasks for Feature 002 (STW Tracking, 3D Verticality, Multi-Map Builder, Staff Panel & Audio Assets)"
---

# Tasks: STW-Style Tracking, 3D Verticality, Multi-Map Builder & Staff Operations

**Input**: Design documents from `/specs/002-staff-multimap-builder-tracking-verticality/`
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`

## Phase 1: Setup & Real Verified Audio Assets (US6 prereq)

- [x] T001 Expand `tools/asset_pipeline.py` with new verified CC0/open-license audio recordings (`ui/track_start.ogg`, `ui/track_stop.ogg`, `ui/track_ping.ogg`, `ui/track_lost.ogg`, `ui/track_arrived.ogg`, `ui/cat_switch.ogg`, `steps/fall_air.ogg`, `combat/bone_break.ogg`, `steps/water_splash_big.ogg`, `builder/line_add.ogg`, `builder/line_edit.ogg`, `builder/line_delete.ogg`, `builder/map_create.ogg`, `world/portal_travel.ogg`, `world/hazard_hit.ogg`, `ambience/indoor_room.ogg`, `ui/staff_alert.ogg`, `multi/server_shutdown.ogg`, `steps/carpet_1..3.ogg`, etc.) and run pipeline to regenerate `client/sounds/manifest.txt` and `client/sounds/CREDITS.md` (116 unique `OggS` files)
- [x] T002 Run `nvgt tools/asset_check.nvgt` to verify 100% magic bytes and unique MD5 hashes

---

## Phase 2: Foundational Shared Core (`common/` & Persistence Schema)

- [x] T003 Update `common/constants.nvgt`: bump `PROTO_VERSION = 2`, add `TRACKER_MAX_DIST = 30.0`, `IN_CLIMB_UP = 1 << 7`, `IN_CLIMB_DOWN = 1 << 8`, `MAP_MIN_Z = -50`, `MAP_MAX_Z = 100`
- [x] T004 Update `common/items.nvgt`: add `splint` (Wooden Splint, medical fracture cure) item and crafting recipe (`r_splint`: `2 Wood + 1 Herbs`)
- [x] T005 Update `common/protocol.nvgt`: add `format_last_seen_en(int64 epoch_sec, int64 now_sec, int tz_offset)` helper and multi-field builders
- [x] T006 Upgrade `common/map.nvgt`: 6-axis box schema (`min_x..max_z`) for `MapPlatform` (`floor|stairs|ramp`, `is_roof`), `MapZone`, `MapWall`, `MapWater`, `MapPortal` (`D`), `MapHazard` (`H`); backward-compatible v1 parser; `raw_lines` preservation + Line Manager mutation/validation API; `find_stair_at`, `find_support_at` (true Air law!), `is_under_roof_at`, `find_portal_at`, `find_hazard_at`
- [x] T007 Upgrade `server/includes/accounts.nvgt`: `ACCOUNTS_V2` with `created_at_epoch`, `last_seen_epoch`, `current_map`, `last_ip` + seamless `ACCOUNTS_V1` upgrade loader + `StaffReportStore` (`data/reports.dat` + `.bak`)
- [x] T008 Write/extend offline unit assertions in `tools/common_check.nvgt`, `tools/map_check.nvgt`, `tools/auth_check.nvgt` for box Z, Air support, stair surface lookup, Line Manager ops, `ACCOUNTS_V1->V2` & `last_seen` formatting; verify PASS

---

## Phase 3: User Story 1 - STW-Style Category Tracker (Priority: P1)

**Goal**: Completely replace old `T`/`Shift+T` scanner with 6-category `<= 30` tile tracker + 3D radar beacon + `O` directional readout.

- [x] T009 [US1] Update `client/includes/profile.nvgt`: remove legacy `scanner` (`T`) default bind, add remappable `trk_next` (`KEY_EQUALS`), `trk_prev` (`KEY_MINUS`), `trk_track` (`KEY_BACK`), `trk_read` (`KEY_O`), `climb_up` (`KEY_PAGEUP`), `climb_down` (`KEY_PAGEDOWN`), `staff_panel` (`KEY_F9`)
- [x] T010 [US1] Create `client/includes/tracker.nvgt`: implement 6 categories (`All`, `Objects`, `Items`, `Animals`, `Structures`, `Players`), strict `<= 30.0` tile filter, stable ID live coordinate resolution, 3D radar ping loop via `sound_pool` with distance-adaptive cadence (zero pitch-elevation hacks), `Ctrl+=`/`Ctrl+-`, `=`/`-`, `Backspace`, `Shift+Backspace`, `O` readout, and lost-track detection
- [x] T011 [US1] Clean up `client/includes/radar_hud.nvgt` (remove legacy `collect_radar_targets` / `announce_radar_step`; keep vitals w/ fracture readout, coords, compass, sonar `V`)
- [x] T012 [US1] Wire tracker controls and unbind `PageUp`/`PageDown` from buffer switching in `client/client.nvgt`

---

## Phase 4: User Story 2 & 3 - 3D Verticality, Air Law, Stair Surface Footsteps & Multi-Map Architecture (Priority: P2 & P3)

**Goal**: True Air/gravity physics, `PageUp`/`PageDown` staircase climbing using builder-selected surface footsteps, height-based fall trauma/fracture, concurrent multi-map simulation, and Map Portals.

- [x] T013 [US2][US3] Refactor `server/includes/state.nvgt` to introduce `MapInstance` (`maps[]`, `find_map`, `default_map_slug`), player `current_map`, `last_climb_ms`, `fracture_until_ms`, `builder_edit_map`, `builder_noclip`, `maintenance_mode`, `shutdown_pending`, `restart_pending`, `StaffReport@[]`
- [x] T014 [US2][US3] Update `server/includes/logger.nvgt` to retain a rolling memory ring buffer of recent audit/log lines for Staff Panel retrieval
- [x] T015 [US2][US3] Update `server/includes/world.nvgt` & `server/includes/combat.nvgt` & `server/includes/wildlife.nvgt`:
  - Map-scoped world nodes, wildlife AI, drops, arrows, combat, respawns per `MapInstance`
  - Staircase climbing via `IN_CLIMB_UP` / `IN_CLIMB_DOWN` / `ACT|climb` (`PageUp`/`PageDown`) playing `steps/<stair.surface>_1..3.ogg` (never generic stair sound)
  - True Air support check (`find_support_at`), falling wind `steps/fall_air.ogg`, height-scaled fall damage, bone break `combat/bone_break.ogg`, curable fracture debuff (plus bandage/splint cure in `world_handle_use_item`), deep-water splash cushioning, void death below `map.min_z - 6`
  - Hazard zone periodic damage (`MapHazard`) and Map Travel Portal transfer (`world_transfer_player_map`)
- [x] T016 [US3] Update `server/includes/chat_social.nvgt`: map-scoped local/emote chat, `/sc` staff chat, `/report` filing, map+zone display in `WHO_RES`
- [x] T017 [US3] Update `server/server.nvgt`: load all `maps/*.map` on startup, accept `--bind-delay-ms` & `--maps-dir`, accept extended `input_mask` (`0..1023`), map-scoped `send_scoped_snapshots`, `ACT|climb|up/down`, `CHAT` staff routing, `REPORT`, `STAFF`, shutdown/restart tick countdown & clean port release + relaunch
- [x] T018 [US2][US3] Update `server/maps/wildlands_valley.map` (add explicit `0..120` ground plate at `z=0..0`, high lookout stairs `z=0..12` with `wood`, cliff drop zone, hazard firepit, and portal to second map) and create `server/maps/skywatch_citadel.map` (multi-story `z=0..20` stone stairs/deck + `-10..0` vault cavern + carpet bastion + air bridge + return portal)
- [x] T019 [US2][US3] Update `client/includes/net_client.nvgt` & `client/includes/audio_engine.nvgt`: handle `MAP_TRANSFER`, new `MAP_HDR`, fractured vital status, roof rain low-pass muffling, local immediate surface footsteps (suppressed mid-air), `BUILDMAP` / `STAFF` packets

---

## Phase 5: User Story 4 - STW-Style F8 Map Builder, Box Forms & Line Manager (Priority: P4)

**Goal**: Replace basic mark-point builder with full STW-style `F8` menu, Create New Map, 6-axis Box Forms, Line Manager, Undo, Validate & Hot-Reload.

- [x] T020 [US4] Rewrite `server/includes/builder_srv.nvgt`: implement `hub_sync`, `create_map`, `select_map`, `edit_header`, `delete_map`, `noclip`, `add_box` (all box/point record types with `min_x..max_z`), full Line Manager (`lm_list`, `lm_raw_edit`, `lm_replace_box`, `lm_insert`, `lm_dup`, `lm_move`, `lm_del`, `lm_tp`), `undo` (25-step per-map stack), `validate`, atomic `save` (with `.map.bak`), and live multi-client `reload`
- [x] T021 [US4] Rewrite `client/includes/builder_ui.nvgt`: STW-style `F8` Builder Hub menu, Create New Map `audio_form`, Switch/Edit Map forms, 6-axis `Min X..Max Z` input forms for Floors/Walls/Stairs/Ramps/Zones/Water/Hazards/Portals/Resources/Emitters/Spawns (pre-filled near player position with sound preview picker), complete Line Manager menu & edit workflows

---

## Phase 6: User Story 5 - Multi-Category Staff Panel & Lifecycle Operations (Priority: P5)

**Goal**: Full categorized Staff Panel (`F9`), Account Directory (`Online` vs `Last seen`), direct target pickers, safe `Shutdown`/`Restart`, world/entity controls, telemetry, audit logs, reports & `/sc`.

- [x] T022 [US5] Upgrade `server/includes/admin_dev.nvgt`: implement `STAFF` protocol handlers for overview telemetry, chunked Account Directory (online flag, map, zone, `last_seen_epoch`, ban/mute state, IP for Admin/Dev), target action pickers (`tp_to`, `bring`, `move_map`, `heal`, `give_item`, `clear_inv`, `rescue`, `kick`, `mute`, `unmute`, `ban`, `unban`, `set_rank`, `clear_token`), world/entity spawn controls, safe countdown `shutdown` & `restart` (launching child process cleanly with preserved CLI args after socket close), maintenance lock, live MOTD/changelog edit, audit log viewer, and reports resolution
- [x] T023 [US5] Create `client/includes/staff_ui.nvgt` and integrate with `client/includes/menus.nvgt` & `client/includes/chat_input.nvgt`: categorized Staff Panel (`Account Directory`, `Server Lifecycle`, `World/Saves/Broadcasts`, `Spawner`, `Teleport`, `Telemetry/Audit Logs/Reports`, `Staff & Builder Guides`), `/sc` & `/report` chat commands, `F9` shortcut

---

## Phase 7: Documentation, Full Verification Gates & Release Builds (US6 + Polish)

- [x] T024 [P] [US6] Author `docs/BUILDER_GUIDE.md` and `docs/STAFF_GUIDE.md`; update `docs/CONTROLS.md`, `docs/PROTOCOL.md`, `docs/ARCHITECTURE.md`, `docs/PLAN.md` and wire in-game guide reader menus
- [x] T025 Update `tools/asset_check.nvgt`, `tools/client_profile_check.nvgt`, `tools/net_integration_check.nvgt`, `tools/client_ui_e2e_check.nvgt`, and `tools/run_checks.ps1` to test Tracker (`<= 30` tiles), stair surface footsteps + air fall damage/splint, multi-map portal transfer, F8 create-map & Line Manager, Staff Panel `Online`/`Last seen` account directory, and shutdown countdown
- [x] T026 Run complete `tools/run_checks.ps1`, compile `server/server.exe` and `client/client.exe` via `nvgt -c`, inspect code quality/security review, and update `GEMINI.md` engineering log
