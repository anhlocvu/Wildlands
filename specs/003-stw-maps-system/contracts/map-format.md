# Map Format Contract v3 (`server/maps/*.map`)

Backward-compatible extension of Map Format v2 adding per-map environment/build rules, silent `"none"` ambience support, zone acoustic reverb presets, and dynamic Animal Spawn Zones (`E`).

## Updated & New Record Tags

1. **`M` Header (Required once, Line 0)**:
   - v3: `M|name|width|height|min_z|max_z|default_surface|ambience_default|pvp_enabled|allow_build|weather_enabled|time_mode`
     - `ambience_default`: audio asset path or `"none"` (silent; client must not force forest ambience).
     - `allow_build`: `1` (players can build kits) or `0` (disabled for non-admin players).
     - `weather_enabled`: `1` (follows server rain) or `0` (weather/rain disabled on map).
     - `time_mode`: `"auto"`, `"day"`, or `"night"`.
   - v2 fallback (9 fields): defaults `allow_build = 1`, `weather_enabled = 1`, `time_mode = "auto"`.
   - v1 fallback (7 fields): also defaults `min_z = -20`, `pvp_enabled = 1`.

2. **`Z` Audio Zone**:
   - v3: `Z|name|min_x|min_y|max_x|max_y|min_z|max_z|surface|ambience_loop|is_safe_zone|reverb_preset`
     - `ambience_loop`: audio asset path, `"none"` (silent), or `""`.
     - `reverb_preset`: `"none"`, `"room"`, `"hall"`, `"cave"`.
   - v2 fallback (11 fields): defaults `reverb_preset = "none"`.

3. **`E` Animal Spawn Zone (NEW — 0 or more lines per map)**:
   - `E|label|min_x|min_y|max_x|max_y|min_z|max_z|interval_ms|count|species_csv|leash|active_time`
     - `label`: wire-escaped spawn zone name.
     - `min_x..max_z`: 3D spawn volume bounds.
     - `interval_ms`: shared spawn/respawn timer in milliseconds (`[250..3600000]`).
     - `count`: max concurrent living creatures owned by this line (`[1..50]`).
     - `species_csv`: comma-separated creature `kind` IDs from the server's dynamic creature catalog (`g_species`).
     - `leash`: `1` (keep creatures anchored near zone + out of safe zones) or `0`.
     - `active_time`: `"always"`, `"day"`, or `"night"`.

4. **`S`, `W`, `P`, `L`, `H`, `D`, `R`, `A`**:
   - Unchanged from v2 (`D` also supports `target_map == current_map.slug` for internal elevators/doors).
