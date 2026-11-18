# Data Model: Feature 002

## 1. Map Geometry & Triggers (`common/map.nvgt`)

### `WorldMap`
- `string slug` — file stem (e.g. `wildlands_valley`)
- `string name` — display name
- `int width, height` — `[40..500]`
- `int min_z, max_z` — `min_z [-50..0]`, `max_z [5..100]`
- `string default_surface` — `grass|dirt|stone|wood|sand|water`
- `string ambience_default` — OGG asset path
- `bool pvp_enabled` — map-wide PvP policy
- `string[] raw_lines` — canonical ordered `.map` lines used by Line Manager & `serialize()`

### `MapPlatform` (Floors, Elevated Decks, Stairs, Ramps, Roofs)
- `string label`
- `double min_x, min_y, max_x, max_y`
- `double min_z, max_z` — ground plates e.g. `0..0`; stairs e.g. `0..20`
- `string surface` — `grass|dirt|stone|wood|sand|water` (also used for staircase footstep sounds!)
- `string kind` — `"floor"`, `"stairs"`, `"ramp"`
- `bool is_roof` — muffles outdoor rain ambience & slows warmth loss underneath
- `string ramp_axis` — `"x"` or `"y"` (for `"ramp"`)
- `int ramp_dir` — `+1` or `-1`

### `MapZone`
- `string name`, `min_x..max_y`, `min_z..max_z` (`[-50..100]`), `surface`, `ambience_loop`, `is_safe_zone`

### `MapWall`
- `string label`, `min_x..max_z`, `material`, `bool occlude_sound`

### `MapWater`
- `string label`, `min_x..max_z`, `depth ("shallow"|"deep")`, `sound_loop`

### `MapPortal` (`D` record)
- `string label`, `min_x..max_z`
- `string target_map` (slug or name)
- `double dest_x, dest_y, dest_z`, `int dest_facing`
- `bool auto_step` (step-in vs `E`/`Enter` interact)
- `string sound_file`

### `MapHazard` (`H` record)
- `string label`, `min_x..max_z`
- `int damage`, `int interval_ms`, `string sound_file`

## 2. Multi-Map Server Runtime (`server/includes/state.nvgt`)

### `MapInstance`
- `string slug`, `string file_path`
- `WorldMap map`
- `ResourceNode@[] nodes`, `WildlifeMob@[] mobs`, `LootDrop@[] drops`, `ArrowProjectile@[] arrows`
- `string[][] undo_history` (capped at 15 line snapshots)

### `PlayerSession` additions
- `string current_map`
- `uint64 last_climb_ms`
- `bool fall_air_sfx_sent`
- `uint64 fracture_until_ms`
- `uint64 last_hazard_ms`
- `string builder_edit_map` (which map the builder is currently editing in Builder Menu/Line Manager)
- `bool builder_noclip`

### `ServerCtx` additions
- `MapInstance@[] maps`
- `string default_map_slug`
- `bool maintenance_mode`
- `bool shutdown_pending`
- `bool restart_pending`
- `uint64 shutdown_at_ms`
- `uint64 next_countdown_announce_ms`
- `string shutdown_reason`
- `string[] saved_cli_flags`
- `StaffReport@[] reports`

## 3. Persistence Extensions (`server/includes/accounts.nvgt`)

### `AccountRecord` additions
- `int64 created_at_epoch`
- `int64 last_seen_epoch` (updated on login, autosave while online, and disconnect)
- `string current_map`
- `string last_ip`

### `StaffReport` (`data/reports.dat`)
- `uint64 id`
- `string reporter`, `string target`, `string map_slug`
- `double x, y, z`
- `string message`
- `int64 created_epoch`
- `bool resolved`
- `string resolved_by`

## 4. Client Tracker (`client/includes/tracker.nvgt`)

### `TrackerCategory` Enum
- `0`: `All`
- `1`: `Objects` (Map resources, emitters, stairs, portals, water sources)
- `2`: `Items` (Ground `LootDrop` entities)
- `3`: `Animals` (Wildlife mobs & practice bots)
- `4`: `Structures` (Player-built structures)
- `5`: `Players` (Other online players on same map)

### `TrackerTarget`
- `string stable_id` (`"ent:m12"`, `"ent:p4"`, `"ent:d9"`, `"obj:18"`, `"res:4"`, `"prt:1"`, `"str:0"`, `"emt:2"`)
- `int category`
- `string label`
- `double x, y, z, dist`

### `TrackerState`
- `int current_category = 0`
- `string focused_id = ""`
- `string active_track_id = ""`
- `string active_track_label = ""`
- `double active_x, active_y, active_z`
- `uint64 next_ping_ms`
