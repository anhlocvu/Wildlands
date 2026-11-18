# Data Model: Feature 003 — STW Maps System

## 1. Map Schema Extensions (`common/map.nvgt`)

### `WorldMap` Header (`M`)
- Existing fields: `slug`, `name`, `width`, `height`, `min_z`, `max_z`, `default_surface`, `ambience_default` (supports `"none"` for silent default), `pvp_enabled`
- New STW Maps System fields (with backward-compatible defaults when absent):
  - `bool allow_build = true` — allows survival structure placement (`B`) by regular players
  - `bool weather_enabled = true` — enables rain audio & rain warmth drain on this map
  - `string time_mode = "auto"` — `"auto"`, `"day"`, or `"night"`

### `MapZone` (`Z`)
- Existing fields: `name`, `min_x..max_z`, `surface`, `ambience_loop` (supports `"none"`), `is_safe_zone`
- New field:
  - `string reverb_preset = "none"` — `"none"`, `"room"`, `"hall"`, `"cave"`

### `MapAnimalSpawn` (`E`) — NEW
- `string label` — readable zone name for Line Manager
- `double min_x, min_y, max_x, max_y, min_z, max_z` — 6-axis spawn box
- `int interval_ms = 5000` — shared spawn/respawn delay in milliseconds (`[250..3600000]`)
- `int count = 3` — target concurrent alive count (`[1..50]`)
- `string[] species` — one or more registered species `kind` strings (serialized as `species_csv`)
- `bool leash = true` — keep spawned creatures anchored to spawn box + outside safe zones
- `string active_time = "always"` — `"always"`, `"day"`, or `"night"`

## 2. Server Runtime Extensions (`server/includes/state.nvgt` & `wildlife.nvgt`)

### `MapInstance`
- `uint64[] animal_spawn_next_ms` — parallel to `map.animal_spawns`; target tick timestamp (`now_ms + interval_ms`) for next spawn wave
- `bool[] animal_spawn_waiting` — `true` while Approach A countdown is active (`alive < count`)

### `WildlifeMob`
- `int spawn_zone_idx = -1` — index into `MapInstance.map.animal_spawns` (`-1` for practice bots)
- `bool leash_to_zone = false`
- `double leash_min_x, leash_min_y, leash_max_x, leash_max_y`

## 3. Client Caches & Clipboard (`client/includes/net_client.nvgt`)

### `SpeciesCatalogItem`
- `string kind`, `string name`, `bool hostile` (populated dynamically from `BM_SPECIES` packet)

### `ServerMapItem`
- `string slug`, `string name`, `int width, height, min_z, max_z`, `int players`, `int lines` (populated from `MAPS_LIST`)

### `BuilderCornerClipboard` (on `NetClient`)
- `bool c1_set, c2_set`
- `int c1_x, c1_y, c1_z`, `int c2_x, c2_y, c2_z`
