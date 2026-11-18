# Phase 0 Research: STW-Style Tracking, 3D Verticality, Multi-Map Builder & Staff Operations

**Feature**: `002-staff-multimap-builder-tracking-verticality`
**Date**: 2026-11-18

## 1. NVGT 0.90.0-dev API Verification (from `nvgt_src` & `C:\nvgt\include`)

1. **Keyboard Constants (`nvgt_src/src/input.cpp`)**:
   - Verified exact enum names registered in AngelScript:
     - `KEY_EQUALS` (`SDL_SCANCODE_EQUALS`)
     - `KEY_MINUS` (`SDL_SCANCODE_MINUS`)
     - `KEY_BACK` (`SDL_SCANCODE_BACKSPACE`)
     - `KEY_O` (`SDL_SCANCODE_O`)
     - `KEY_PAGEUP` (`SDL_SCANCODE_PAGEUP`)
     - `KEY_PAGEDOWN` (`SDL_SCANCODE_PAGEDOWN`)
   - Finding in existing code: [client.nvgt](file:///C:/Users/LCBoy/Desktop/data/stw/client/client.nvgt#L205-L210) currently binds `KEY_PAGEUP` and `KEY_PAGEDOWN` directly to `buffer_left()` / `buffer_right()` when not in map builder mode. Removing those hardcoded aliases frees `PageUp`/`PageDown` for staircase climbing while leaving buffer channel switching cleanly on `buf_prev` (`,`) and `buf_next` (`.`).

2. **Process Launch for Safe Server Restart (`nvgt_src/src/misc_functions.cpp`, `scriptstuff.cpp`)**:
   - Verified signatures:
     - `bool run(const string&in filename, const string&in arguments, bool wait_for_completion, bool background)`
     - `bool get_SCRIPT_COMPILED() property`
     - `string get_SCRIPT_EXECUTABLE() property`
     - `string get_SCRIPT_MAIN_PATH() property`
     - `string get_COMMAND_LINE() property`
   - Decision for Server Restart: Before calling `run(...)`, save all dirty stores (`accounts.dat`, `world_objects.dat`, `reports.dat`, active edited maps), send final `REFUSE|restarting|Server is restarting...` notices to connected peers, call `g_srv.net.flush()`, and **destroy ENet host (`g_srv.net.destroy(true)`)** so UDP port is released. Launch the new instance passing `--bind-delay-ms 900` plus original CLI flags (`--port`, `--data-dir`, `--bots`, `--wildlife`, `--allow-guests`, `--test-mode`, `--headless`), then exit cleanly. When `SCRIPT_COMPILED` is false (running via `nvgt.exe server/server.nvgt`), spawn `SCRIPT_EXECUTABLE` with `SCRIPT_MAIN_PATH` + preserved args.

3. **Timestamps & Human-Readable `Last seen` Formatting (`nvgt_src/src/misc_functions.cpp`, `timestuff.cpp`)**:
   - `TIME_STAMP` returns `uint64` POSIX epoch seconds (`time(0)`).
   - `DATE_YEAR`, `DATE_MONTH`, `DATE_DAY`, `TIME_HOUR`, `TIME_MINUTE`, `TIME_SECOND`, `TIMEZONE_OFFSET` are built-in.
   - Decision: Store `last_seen_epoch` and `created_at_epoch` as `int64` epoch seconds in `accounts.dat` (`ACCOUNTS_V2`, backward-compatible reader for `ACCOUNTS_V1`). Format offline `Last seen` on server (or send `online_flag` + `last_seen_epoch` to client) as relative + calendar text, e.g. `"Last seen: 12 minutes ago (2026-11-18 19:02)"` using civil-from-days / epoch-to-UTC+offset conversion verified in `auth_check.nvgt`. Online accounts strictly display `"Online (<map>, <zone>)"`.

4. **Accessible Forms & Lists (`C:\nvgt\include\form.nvgt`)**:
   - Verified `audio_form` methods: `create_input_box`, `create_list`, `add_list_item(ctrl, option, id, position, selected, focus_if_first)`, `get_list_position`, `set_list_position`, `create_checkbox`, `create_slider`, `create_button`.
   - Decision: Use multi-field `audio_form` dialogs for all 6-axis Builder Box forms (`Label, Min X, Max X, Min Y, Max Y, Min Z, Max Z`, etc.) and Create New Map form, plus arrow-key `menu` for category/target navigation in Staff Panel & Line Manager (`focus_first_item = true`, remembered index on submenu return).

## 2. Architecture & Design Decisions

1. **Multi-Map Server Model**:
   - `ServerCtx` replaces single `WorldMap map` with `MapInstance@[] maps` plus `string default_map_slug` (resolved from `--map` or first valid map, default `"wildlands_valley"`).
   - Each `MapInstance` owns its `slug`, `file_path`, `WorldMap map`, `ResourceNode@[] nodes`, `WildlifeMob@[] mobs`, `LootDrop@[] drops`, `ArrowProjectile@[] arrows`, and `string[]@[] undo_stack` (last 15 raw-line snapshots).
   - `WorldStructure` already stores `map_name` (`wildlands_valley` -> matched against `MapInstance.slug` or `map.name` via normalized helper so legacy `world_objects.dat` stays valid!).
   - Helper `ctx.find_map(name_or_slug)` resolves maps consistently. When a player enters a `MapPortal` (`D` record) or is moved by Staff, `server_transfer_player_map()` updates `ps.current_map`, places `(ps.x, ps.y, ps.z, ps.facing)`, clears stale peer entity visibility on next snapshot, sends `MAP_HDR` + `MAP_CHK` + scoped `MAP_OBJ` for the destination map, and plays `world/portal_travel.ogg`.

2. **STW 3D Box Geometry, Air Law & Stair Surface Footsteps**:
   - Every `MapPlatform` holds `min_x, max_x, min_y, max_y, min_z, max_z, surface, kind ("floor" | "stairs" | "ramp"), is_roof, ramp_axis, ramp_dir`.
   - `WorldMap::find_support_at(x, y, z, out_has_support, out_z, out_surface, out_deep_water, out_under_roof)`:
     - Checks `"floor"` plates (`x in [min_x,max_x]`, `y in [min_y,max_y]`, `max_z <= z + 0.85`): picks highest `max_z`.
     - Checks `"ramp"` boxes: interpolates height between `min_z` and `max_z` along `ramp_axis`/`ramp_dir`.
     - Checks `"water"` (`L` boxes): `max_z <= z + 0.85` yields water support (`deep` softens/negates fall damage and triggers `water_splash_big.ogg`).
     - Checks solid player-built floor structures (`wood_floor`) if any.
     - If nothing supports `(x, y)` at or below `z`, `has_support = false` -> **Air / Void**.
   - **Staircases (`kind == "stairs"`)**:
     - Climbing does NOT play a single hardcoded stair sound; instead, server/client read `stair.surface` (`grass`, `dirt`, `stone`, `wood`, `sand`, `water`) and play `steps/<surface>_<1..3>.ogg` at the climber's 3D position (immediate self cue + spatialized `CH_AUDIO` broadcast to nearby players on the same map).
     - Pressing `PageUp` / `PageDown` steps Z by `+/- 1.0` clamped to `[stair.min_z, stair.max_z]` (with `200ms` repeat throttle while held, or instant on tap), checking head clearance against solid walls.
   - **Fall Damage & Fracture**:
     - If falling in Air with `fall_start_z - z > 2.2`, emit `steps/fall_air.ogg` once per fall.
     - Landing with `drop = fall_start_z - landed_z`:
       - `drop <= 2.5`: soft land (`land_soft.ogg`), 0 dmg.
       - `2.5 < drop <= 5.5`: hard land (`land_hard.ogg`), `int((drop - 2.0) * 5.0)` dmg.
       - `drop > 5.5`: trauma (`land_hard.ogg` + `combat/bone_break.ogg` + `combat/hurt.ogg`), `int((drop - 3.0) * 8.5)` dmg; if `drop > 6.5` and still alive, sets `ps.fracture_until_ms = now_ms + 25000` (35% slower walk, no sprint/jump until healed or treated with `bandage` / `splint`).
       - Falling below `map.min_z - 6.0` with no support triggers Void death & respawn at map's default spawn.

3. **Line-Authoritative Map Editing (Line Manager)**:
   - `WorldMap` tracks `string[] raw_lines` matching the exact `.map` file lines.
   - Line Manager operations (`LM_LIST`, `LM_EDIT_FIELDS`, `LM_EDIT_RAW`, `LM_INSERT`, `LM_DUP`, `LM_MOVE`, `LM_DEL`, `LM_UNDO`) operate deterministically on `raw_lines` and validate through `WorldMap candidate; candidate.load_from_lines(...)` before committing to the live `MapInstance`, guaranteeing zero divergence between memory, Line Manager indices, Undo snapshots, and `.map` disk serialization.

4. **STW-Style Tracker (`<= 30` Tiles)**:
   - Completely replaces `announce_radar_step` (`T` / `Shift+T`).
   - Categories: `All` (0), `Objects` (1), `Items` (2), `Animals` (3), `Structures` (4), `Players` (5).
   - Scan radius strictly `<= TRACKER_MAX_DIST` (`30.0` tiles) when enumerating items; active tracking holds lock up to `EARSHOT_RADIUS` (`35.0` tiles) so edge jitter does not flicker, then speaks `"Lost track of <Target>"` + `ui/track_lost.ogg` when lost/destroyed/map-changed.
   - Keys: `Ctrl+=` / `Ctrl+-` (category forward/back), `=` / `-` (item forward/back), `Backspace` (start tracking + 3D radar beacon), `Shift+Backspace` (stop tracking), `O` (speak live relative direction, step distance, and elevation).

5. **Sound Assets**:
   - Extend `tools/asset_pipeline.py` with verified CC0/open-license sources (Kenney, OpenGameArt CC0 packs) for all new cues (tracker cues, air fall, bone break, big splash, portal travel, hazard hit, indoor room ambience, builder line ops, staff alert, server shutdown). Zero Python-generated tones.
