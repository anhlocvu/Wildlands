# Map File Format Contract (`maps/*.map`)

Maps are line-oriented plain UTF-8 text files shared by the Server and the Interactive Audio Map Builder. Blank lines and `#` comment lines are ignored. Every line begins with a record tag followed by `|` (`FIELD_SEP`) fields.

---

## Record Schema

### Header (`M`) — Required (exactly once)
```text
M|map_name|width|height|max_z|default_surface|ambience_default
```
- `width`, `height`: `40..500` tiles (`int`)
- `max_z`: `5..50` (`int`)
- `default_surface`: `grass|dirt|stone|wood|sand|snow`

### Spawn Point (`S`) — Required (at least 1)
```text
S|label|x|y|z|facing
```

### Zone (`Z`)
```text
Z|name|min_x|min_y|max_x|max_y|surface|ambience_loop|is_safe_zone
```
- `is_safe_zone`: `1` disables PvP and hostile wildlife entry; `0` allows combat.

### Wall / Solid Obstacle (`W`)
```text
W|label|min_x|min_y|max_x|max_y|min_z|max_z|material
```
- `material`: `wood|stone|metal|hedge|cliff` (determines bump sound + acoustic occlusion attenuation).

### Elevation Platform / Ramp (`P`)
```text
P|label|min_x|min_y|max_x|max_y|z_level|surface|is_ramp|ramp_axis|ramp_dir
```
- Supports elevated watchtowers, hills, bridges, and stair ramps connecting Z-levels.

### Water Body (`L`)
```text
L|label|min_x|min_y|max_x|max_y|z_level|depth|sound_loop
```
- `depth`: `shallow` (walkable with splash footsteps) or `deep` (requires swim/stamina or blocks entry).

### Resource Spawner (`R`)
```text
R|type|x|y|z|max_charges|respawn_sec
```
- `type`: `tree|rock|iron_vein|berry_bush|herb_patch`

### Ambient Landmark Emitter (`A`)
```text
A|label|sound_file|x|y|z|range|volume
```
- Persistent 3D audio beacon (e.g., `camp_hearth`, `waterfall`, `wind_mill`, `beacon_hum`) used by blind players as spatial anchors.

---

## Validation Rules (Enforced by `tools/map_check.nvgt` & Server Startup)
1. Header `M` must exist with valid positive bounds.
2. At least one `S` spawn point inside bounds and NOT overlapping any solid `W` wall.
3. Every `Z`, `W`, `P`, `L`, `R`, `A` coordinate clamped/verified within `[0..width, 0..height, 0..max_z]`.
4. Every referenced `sound_file` / `ambience_loop` must exist in `sounds/manifest.txt`.
5. Serialized handshake map chunks must fit cleanly under chunk limits and reload identically on round-trip (`load -> serialize -> load`).
