# Wire Protocol Contract v3 (`PROTO_VERSION = 3`)

Extends Feature 002 protocol with dynamic creature catalog sync, `E` Animal Spawn Zone builder packets, unified `/maps` navigation, map cloning, and per-map rule headers.

## Unified `/maps` Navigation (`CH_CONTROL`, Rank >= `RANK_BUILDER`)
- **Client -> Server**:
  - `MAPS|list` -> requests full server map directory (`RANK_BUILDER+`).
  - `MAPS|tp|slug` -> teleports caller to `slug`'s primary spawn and syncs `builder_edit_map = slug` (`RANK_BUILDER+`).
- **Server -> Client**:
  - `MAPS_LIST|rows` (`slug~name~w~h~min_z~max_z~players~lines;...`)

## Updated STW Builder (`CH_CONTROL`, Rank >= `RANK_BUILDER`)
- **Server -> Client on `BUILDMAP|hub_sync`**:
  - `BM_SPECIES|rows` (`kind~name~hostile_01;...`) — dynamically built from `g_species` on server.
  - `BM_MAPS|active_slug|slug:name:w:h:min_z:max_z:surf:amb:pvp:players:lines:allow_build:weather_enabled:time_mode;...`
- **Client -> Server (`BUILDMAP|...`)**:
  - `BUILDMAP|create_map|slug|name|w|h|min_z|max_z|surf|template|sx|sy|sz` (no ambience field; server sets `ambience_default = "none"` and builds template geometry `flat|void|arena|cave`).
  - `BUILDMAP|select_map|slug` (switches `builder_edit_map` ONLY; never teleports).
  - `BUILDMAP|edit_header|name|w|h|min_z|max_z|surf|amb|pvp|allow_build|weather_enabled|time_mode`
  - `BUILDMAP|clone_map|src_slug|new_slug|new_name`
  - `BUILDMAP|add_box|animal_spawn|label|x1|x2|y1|y2|z1|z2|interval_ms|count|species_csv|leash|active_time`
  - `BUILDMAP|add_box|zone|label|x1|x2|y1|y2|z1|z2|surf|amb|safe|reverb_preset`
  - `BUILDMAP|lm_tp|line_idx` (teleports within current map ONLY if `builder_edit_map == current_map`; rejects cross-map teleport with `/maps` guidance).

## Removed Legacy Staff Spawner Packets
- Removed from Staff Panel UI & handlers: `STAFF|spawn_mob`, `STAFF|world|wildlife`, `DEV|set_wildlife`.
