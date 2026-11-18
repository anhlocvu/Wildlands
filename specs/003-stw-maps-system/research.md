# Research: Feature 003 — STW Maps System

## 1. Root Cause of Uncontrolled Wildlife Spawns & Forced Ambience
- **Decision**: Remove `wildlife_set_target_count` auto-population from server startup and tick loop; replace with map-authored `E` (`MapAnimalSpawn`) box records evaluated per `MapInstance`. Remove `"ambience/forest_day.ogg"` fallback in `audio_engine.nvgt` and `net_client.nvgt` when `"none"` or `""` is selected.
- **Rationale**: Previously `server/includes/wildlife.nvgt` populated 12 mobs on default map and 6 on every other map every 5 seconds regardless of map purpose, attacking builders inside `anhloc.map`. Likewise `audio_engine.nvgt:310` forced `forest_day.ogg` whenever ambience was empty.
- **Alternatives Considered**: A server-level map blacklist flag. Rejected because per-map `E` spawner lines are declarative, builder-editable, and match STW map architecture.

## 2. Dynamic Species Catalog & NVGT Multi-Select Checkbox List (`audio_form`)
- **Decision**: Server dynamically serializes every entry in `g_species` (`BM_SPECIES|kind~name~hostile;...`) when syncing Builder Hub (`BUILDMAP|hub_sync`), and `builder_ui.nvgt` renders them inside `audio_form::create_list(caption, 0, true, false)`.
- **Rationale**: Reading `C:\nvgt\include\form.nvgt` revealed two critical engine facts:
  1. `create_list(..., multiselect = true)` sets `list_multiselect = true` on the newly created control and makes `Up/Down` browse items, `Space` toggle `Checked`/`Unchecked`, `Ctrl+A` select all, and `get_checked_list_items(ctrl)` return all checked indices.
  2. `set_list_properties()` in NVGT's `form.nvgt` has a bug referencing `control_counter` instead of `control_index` (line 1073), so passing `multiselect = true` directly to `create_list()` is mandatory and verified safe.
- **Alternatives Considered**: Multiple standalone `create_checkbox()` controls per species. Rejected because the user specifically requested a list box with checkbox items and dynamic server species scaling (`create_checkbox` stops scaling if many species are added and reaches the 50-control form limit).

## 3. Approach A Shared Millisecond Respawn Timer
- **Decision**: Each `MapAnimalSpawn` (`E`) maintains runtime state `(waiting, next_spawn_ms)` on `MapInstance`, and each `WildlifeMob` tracks `spawn_zone_idx`. Whenever `alive_count < sp.count` (including `0` at map load/zone edit or `< count` after any mob dies), if `!waiting`, schedule `next_spawn_ms = now_ms + sp.interval_ms`. When `now_ms >= next_spawn_ms`, spawn random checked species up to `sp.count` and clear `waiting`.
- **Rationale**: Matches user's explicit selection of Approach A and handles single or partial kills cleanly with exact millisecond delay without instant pop-in.
- **Alternatives Considered**: Per-mob independent respawn timers or Approach B (wait for full wipe). Rejected per user decision.

## 4. NVGT Acoustic Reverb Zones (`audio_freeverb_node`)
- **Decision**: Use NVGT's native `audio_freeverb_node` (`nvgt_src/src/sound.cpp:2481`) attached dynamically to `mix_world`, `mix_actors`, `mix_threat`, and a dedicated `mix_steps` (separating footsteps from dry `mix_self` UI cues, `mix_ambience`, and `mix_music`).
- **Rationale**: Verified exact property signatures in `sound_nodes.cpp`: `room_size`, `damping`, `width`, `wet`, `dry` (`float`, `[0..1]`). Clearing `effects_chain` in `"none"` zones keeps dry audio crisp with zero CPU overhead.
- **Alternatives Considered**: `reverb3d` emitter attachment. Rejected for zone-wide acoustics because `mixer.effects_chain` smoothly affects all spatial audio while inside the zone box without needing per-emitter point distance curves.
