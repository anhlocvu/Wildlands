# Tasks: Wildlands Online — Multiplayer Survival Audio Game

**Input**: Design documents from `/specs/001-wildlands-online-survival/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`
**Directory Separation**: `common/` (shared), `server/` (standalone server), `client/` (standalone client), `tools/` (console checks & audio pipeline)

---

## Phase 1: Setup & Audio Asset Pipeline (US6 Foundation)

- [X] T001 Create separated folder layout (`common/`, `server/includes/`, `server/maps/`, `server/data/`, `server/logs/`, `client/includes/`, `client/sounds/`, `tools/`)
- [X] T002 [P] Copy and adapt drop-in libraries from `online-audio-game-dev`: `common/wire.nvgt` and `common/compass.nvgt`
- [X] T003 [P] Copy and adapt `online-audio-game-dev/library/buffers.nvgt` into `client/includes/buffers.nvgt`
- [X] T004 [P] Vendor and patch `C:\nvgt\include\sound_pool.nvgt` into `client/includes/sound_pool.nvgt` (float precision distance/update + behind-only 3% pitch cue, never Z elevation)
- [X] T005 Write `tools/asset_pipeline.py` to search/download real CC0/open recordings, verify magic audio headers, deduplicate by MD5, loudness-normalize & silence-trim via `ffmpeg` to `.ogg`, and output `client/sounds/manifest.txt` + `client/sounds/CREDITS.md`
- [X] T006 Execute `tools/asset_pipeline.py` and verify every sound category (`ui/`, `steps/`, `survival/`, `builder/`, `combat/`, `wildlife/`, `ambience/`, `multi/`, `music/`) is populated with real high-quality `.ogg` files

---

## Phase 2: Foundational Common Code & Offline Checks (Blocking Prerequisites)

- [X] T007 Implement shared constants (`MAIN_SERVER_HOST`, `LOCAL_SERVER_HOST`, `DEFAULT_PORT=7100`, `PROTO_VERSION=1`, `MAX_CHANNELS=6`, `CH_*`, `TICK_HZ=30`, `SNAPSHOT_HZ=15`, `EARSHOT_RADIUS=35.0`, `MAX_UDP_PAYLOAD=1350`, ranks, keys) in `common/constants.nvgt`
- [X] T008 [P] Implement protocol escaping/packet helpers and bounds validators in `common/protocol.nvgt`
- [X] T009 [P] Implement shared `.map` parser, serializer, bounds validator, surface/zone lookup, wall/door collision, and line-of-sight acoustic occlusion test in `common/map.nvgt`
- [X] T010 [P] Implement shared items, tools, crafting recipes, survival structures, and wildlife species tables in `common/items.nvgt`
- [X] T011 Author starter multi-zone wilderness + settlement map `server/maps/wildlands_valley.map` and server news/dev files (`server/data/motd.txt`, `server/data/changelog.txt`, `server/data/devs.txt`)
- [X] T012 [P] Write console verification tools `tools/common_check.nvgt`, `tools/map_check.nvgt`, and `tools/asset_check.nvgt` (no window, no sound, exit codes) and run all three to PASS

---

## Phase 3: User Story 1 — Account Onboarding, Spatial Navigation & Reconnect (Priority: P1)

**Goal**: Dedicated server + client boot, register/login once with AppData token wallet, sync map, walk/turn with 3D spatialized audio, status keys, and reconnect cleanly.
**Independent Test**: Register/login on Client A, relaunch for auto-token login, walk across zones/surfaces, collide with walls, test reconnect after server drop.

- [X] T013 [US1] Implement timestamped windowed/file rotating logger and fatal modal `alert()` helper in `server/includes/logger.nvgt`
- [X] T014 [US1] Implement salted stretched SHA-256 (`5000` rounds), constant-time compare, `random_bytes(32)` hashed tokens, IP rate limiting, and atomic `.dat`/`.bak` account store in `server/includes/accounts.nvgt`
- [X] T015 [US1] Write offline auth/security check `tools/auth_check.nvgt` and verify PASS
- [X] T016 [P] [US1] Implement client speech layer (`screen_reader_speak()` + `tts_voice` fallback + repeat-last-line) in `client/includes/speech.nvgt`
- [X] T017 [P] [US1] Implement 7-layer audio engine (`Speech..Music`), `linear_to_db` boundary, HRTF activation, `audio_low_pass_filter` occlusion, and `sound_pool` integration in `client/includes/audio_engine.nvgt`
- [X] T018 [P] [US1] Implement AppData INI settings + 8-slot LRU per-server credential wallet in `client/includes/profile.nvgt`
- [X] T019 [US1] Implement accessible `audio_form` dialogs (Registration, Sign-In with silent masked password + toggle echo + Ctrl+V paste, Server Entry) in `client/includes/ui_forms.nvgt`
- [X] T020 [US1] Implement core server entry, CLI args (`--port`, `--map`, `--bots`, `--test-mode`, `--allow-guests`, `--headless`), 30 Hz tick, 15 Hz earshot-scoped snapshots, handshake, movement, and reconnect grace window in `server/server.nvgt`
- [X] T021 [US1] Implement client network pump, state interpolation, chunked map loader, and reconnect prompt in `client/includes/net_client.nvgt`
- [X] T022 [US1] Implement client main loop, compass snap/smooth turning, immediate local movement/UI feedback, main/connect menus, status hotkeys (`H`, `X`, `K`, `F1`), and radar foundation in `client/client.nvgt` & `client/includes/menus.nvgt` & `client/includes/radar_hud.nvgt`

---

## Phase 4: User Story 2 — Multi-Channel Chat, Buffers & Online Social (Priority: P2)

**Goal**: Modal `/` chat (Global/Local/Team/PM/Reply/Emote), 6-channel navigable message buffers, `Who`, `Ping`, Friends, Mute/Block, Profiles & Leaderboard.
**Independent Test**: Two clients exchange area/global/PM chat via `/`, inspect/mute/copy buffer channels, check `Who` and `Ping` mid-game, and verify `Block` suppresses messages and duel requests.

- [X] T023 [US2] Implement server-side chat router, rate limiter, mute check, whisper routing, `WHO_RES`, `PONG`, friends, block list, player profile & leaderboard queries in `server/includes/chat_social.nvgt`
- [X] T024 [P] [US2] Implement modal `/` chat input box (open/close/click SFX, Escape cancel, Enter send, command parsing) in `client/includes/chat_input.nvgt`
- [X] T025 [US2] Wire 6-channel `buffers.nvgt` navigation/mute/copy/clear hotkeys, `Who` (`U`), `Ping` (`P`), and Social menu (`F2`: Friends, Block, Profile, Leaderboard) in `client/includes/menus.nvgt`, `client/includes/net_client.nvgt`, and `client/client.nvgt`

---

## Phase 5: User Story 3 — Survival Gathering, Vitals, Crafting & Wildlife Combat (Priority: P3)

**Goal**: 5 survival vitals, resource nodes with respawn, crafting, campfire cooking/warmth, 3D wildlife AI, melee/block/bow combat, duels & death/respawn.
**Independent Test**: Gather berries/wood/stone/water, craft campfire & axe, cook meat, track 3D wolf audio, defeat it in combat, loot & heal.

- [X] T026 [US3] Implement server resource nodes, item drops, vitals decay/warmth, crafting validation, campfire fuel/cooking, and day/night/weather simulation in `server/includes/world.nvgt`
- [X] T027 [US3] Implement passive & hostile wildlife AI (`rabbit`, `deer`, `wolf`, `bear`, `bandit`, `bot_survivor`) with 3D vocalizations and telegraphed attack windups in `server/includes/wildlife.nvgt`
- [X] T028 [US3] Implement server-authoritative melee swings, guard blocking, ranged bow projectile travel, safe-zone vs PvP/duel resolution, and death/respawn in `server/includes/combat.nvgt`
- [X] T029 [US3] Implement client Inventory/Belt (`1-9`, `I`), Crafting (`C`), Survival self-state cues (heartbeat, shiver, ambience transitions), and 3D threat/wildlife/combat audio + Target/Sonar scanner (`T`, `V`) in `client/includes/menus.nvgt`, `client/includes/audio_engine.nvgt`, and `client/includes/radar_hud.nvgt`

---

## Phase 6: User Story 4 — Dual Builder: Survival Base Building & Audio Map Builder (Priority: P4)

**Goal**: Persistent survival building (walls, lockable doors with acoustic occlusion, chests, floors/stairs, campfires, benches, beacons) + Interactive Audio Map Builder (`F8`) with live server reload.
**Independent Test**: Place cabin walls, locked door, and chest; confirm closed door muffles outside sound; restart server to verify persistence; open Map Builder (`F8`), create/edit a zone and wall, save `.map`, and live-reload.

- [X] T030 [US4] Implement server-authoritative Survival Builder (placement collision/bounds, lock/unlock, open/close door, chest storage, repair/demolish, atomic `world_objects.dat` persistence) and Map Builder live `.map` mutation/validation/reload in `server/includes/builder_srv.nvgt`
- [X] T031 [US4] Implement client Survival Builder menu (`B`, `L`, `R`, `Ctrl+Del`), Chest UI, dynamic wall/door low-pass occlusion hooks, and Interactive Audio Map Builder cursor UI (`F8`) in `client/includes/builder_ui.nvgt` and `client/includes/audio_engine.nvgt`

---

## Phase 7: User Story 5 — Professional Ops: Settings, Key Remap, Tutorial, Dev & Mod Panels (Priority: P5)

**Goal**: Instant-saving Settings with live slider samples & key remapping, Interactive Guided Tutorial, Developer Panel, Ranked Moderation, and E2E integration tests.
**Independent Test**: Adjust 7-layer sliders & remap a key across restart; complete/skip Tutorial; verify Dev Panel target commands and Mod hierarchy refusals; pass full multi-client integration suite.

- [X] T032 [US5] Implement server Developer Panel (`DEV` target commands) and Ranked Moderation (`MOD` kick/mute/ban/unban with strict rank hierarchy & startup ban messages) in `server/includes/admin_dev.nvgt`
- [X] T033 [P] [US5] Implement Settings menu (7-layer volume sliders with live audio preview, speech/TTS rate/voice, snap angle, localhost dev switch, key remapper with conflict prompt) in `client/includes/menus.nvgt` and `client/includes/ui_forms.nvgt`
- [X] T034 [P] [US5] Implement step-verified Interactive Audio Tutorial (skip/replayable) in `client/includes/tutorial.nvgt`
- [X] T035 [US5] Implement client Dev Panel & Moderation menus in `client/includes/menus.nvgt` and integrate News/MOTD/Changelog & Update Check hook

---

## Phase 8: Polish, Compilation, Full E2E Integration & Bug Fixes (US6 Completion)

- [X] T036 Write end-to-end multi-client integration test `tools/net_integration_check.nvgt` (spawns temp headless server on `:7199` with `--test-mode`, tests auth, movement, chat, block, survival craft/gather, building persistence, map reload, dev/mod hierarchy, cleans up process)
- [X] T037 Write master runner `tools/run_checks.ps1` running all offline checks, compilation (`nvgt -c server/server.nvgt`, `nvgt -c client/client.nvgt`), integration check, and stray `nvgt.exe` check
- [X] T038 Execute `tools/run_checks.ps1`, resolve every compile warning/error or runtime test failure until 100% PASS, review code quality across `common/`, `server/`, `client/`, and record final engineering log in `GEMINI.md`
