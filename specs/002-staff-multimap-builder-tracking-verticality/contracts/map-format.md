# Map Format Contract v2 (`server/maps/*.map`)

Backward-compatible line-oriented UTF-8 text schema supporting negative Z (`-50..100`), 3D box platforms/stairs/zones/waters, hazards, and multi-map portals.

## Record Tags

1. **`M` Header (Required once, Line 0)**:
   - v2: `M|name|width|height|min_z|max_z|default_surface|ambience_default|pvp_enabled`
   - v1 fallback: `M|name|width|height|max_z|default_surface|ambience_default` (defaults `min_z = -20`, `pvp_enabled = 1`)
2. **`S` Spawn Point (At least 1 required)**:
   - `S|label|x|y|z|facing`
3. **`Z` Audio Zone**:
   - v2: `Z|name|min_x|min_y|max_x|max_y|min_z|max_z|surface|ambience_loop|is_safe_zone`
   - v1 fallback: 9 fields (`min_z = -50`, `max_z = 100`)
4. **`W` Solid Wall**:
   - v2: `W|label|min_x|min_y|max_x|max_y|min_z|max_z|material|occlude_sound`
   - v1 fallback: 9 fields (`occlude_sound = 1`)
5. **`P` Platform / Floor / Stairs / Ramp**:
   - v2: `P|label|min_x|min_y|max_x|max_y|min_z|max_z|surface|kind|is_roof|ramp_axis|ramp_dir`
     - `kind`: `floor` (solid plate at `max_z`), `stairs` (climbable `[min_z..max_z]` via `PageUp`/`PageDown`, plays `surface` footsteps!), `ramp` (walk-up slope from `min_z` to `max_z`).
   - v1 fallback: 11 fields (`min_z = 0`, `max_z = z_level`, `kind = is_ramp ? "ramp" : "floor"`, `is_roof = 0`).
6. **`L` Water Body**:
   - v2: `L|label|min_x|min_y|max_x|max_y|min_z|max_z|depth|sound_loop`
   - v1 fallback: 9 fields (`min_z = z_level - 2`, `max_z = z_level`)
7. **`H` Hazard Zone**:
   - `H|label|min_x|min_y|max_x|max_y|min_z|max_z|damage|interval_ms|sound_file`
8. **`D` Map Travel Portal / Link**:
   - `D|label|min_x|min_y|max_x|max_y|min_z|max_z|target_map|dest_x|dest_y|dest_z|dest_facing|auto_step|sound_file`
9. **`R` Resource Spawner**:
   - `R|type|x|y|z|max_charges|respawn_sec`
10. **`A` Ambient Emitter**:
   - `A|label|sound_file|x|y|z|range|volume`

## Line Order & Line Manager Guarantee
- Lines are preserved in exact file order (`raw_lines`) so Line Manager edits, insertions, duplications, and priority moves (`Move Up` / `Move Down`) survive save/reload deterministically.
