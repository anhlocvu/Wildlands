# Audio Map Builder Guide (`F8`) — Wildlands Online v2

Welcome to the **STW-Style Multi-Map Audio Map Builder**. Authorized staff (`Builder`, `Admin`, or allowlisted `Developer`) can author entire worlds with 3D vertical geometry, underground caverns (`min_z .. max_z`), staircases, audio zones, deep/shallow water pools, hazards, ambient landmarks, and cross-map portals — all screen-reader accessible with zero external text editors required.

---

## 1. Opening the Builder Hub (`F8`)

Press **`F8`** in-game (or open **Pause Menu -> Audio Map Builder Hub (F8)**) to launch the main hub for the currently active builder map:

1. **Add Element by 6-Axis Box Coordinates (`Min X .. Max Z`)**: Opens dedicated `audio_form` dialogs so you enter bounds (`Minimum X`, `Maximum X`, `Minimum Y`, `Maximum Y`, `Minimum Z`, `Maximum Z`) directly rather than walking every corner tile-by-tile.
2. **Line Manager (`Browse, Edit, Move, Duplicate, Delete`)**: Inspect and manipulate every line of the `.map` file live on the server.
3. **Create New Map**: Spawns a brand new `.map` inside `server/maps/` with custom dimensions, elevation range, default surface, default ambience, spawn point, and optional base floor slab.
4. **Switch Active Map**: Select any loaded map on the server to edit in place or teleport directly to its primary spawn point.
5. **Edit Active Map Properties**: Change the display name, X/Y dimensions, Z elevation range, default ground surface, default ambience loop, or PvP rules on the `M|` header line.
6. **Undo Last Map Change**: Reverts the last box addition, line edit, reorder, or deletion on the active map (up to 25 undo snapshots per map in memory).
7. **Builder Noclip Flight**: Toggles wall/gravity bypass so you can walk through walls and hover smoothly across heights without fall damage while testing builds.
8. **Free-Roam Cursor Mode & Palette**: Walk a discrete `(X, Y, Z)` cursor tile-by-tile with `Arrow` keys and `PageUp` / `PageDown`, press `M` to mark a corner, and `Enter` / `B` to drop quick shapes.
9. **Validate / Save / Reload / Delete**:
   - **Validate**: Runs `WorldMap::validate()` across bounds, spawns, surfaces, and audio references.
   - **Save**: Atomically writes `.map` via `.tmp` -> `.bak` -> `.map`.
   - **Reload**: Reloads the saved `.map` from disk onto the live server and re-syncs all players on that map.
   - **Delete Map**: Archives non-default maps to `<slug>.map.deleted.bak` and evacuates players cleanly to default spawn.

---

## 2. Multi-Map System

The server scans `server/maps/*.map` on startup and keeps every valid map running simultaneously:
- Snapshots (`EARSHOT_RADIUS = 35.0`), wildlife AI, gathering nodes, player structures, local chat, and 3D sound events are scoped per map (`MapInstance`).
- Players travel between maps using **Map Travel Portals (`D`)** with `E` / `Enter` or automatic trigger when `auto_step = 1`.
- Map filenames follow lowercase `slug` IDs (`a-z`, `0-9`, `_`, `-`), e.g. `wildlands_valley.map` and `skywatch_citadel.map`.

---

## 3. 3D Coordinate Space & Air / Void Law

Every map operates in true 3D space (`X` East-West, `Y` South-North, `Z` Elevation inside `[MAP_MIN_Z=-50 .. MAP_MAX_Z=100]`):

- **Supported Ground (`P` platforms, `stairs`, `ramp`)**: A player standing within supported `(X, Y)` bounds rests securely on `Z`. Flat platforms support thin slabs (`z1 == z2`, e.g., `0..0` base floor or `10..10` upper deck) or solid blocks (`z1..z2`).
- **Mid-Air & Gravity**: Unlike flat 2D tilemaps, empty air above or below has **no solid ground**. Stepping past the edge of a high platform (`z1 > current_ground`) puts the player in mid-air:
  - Client suppresses ground footsteps; server applies gravity (`FALL_GRAVITY = 22.0` units/sec^2).
  - Air rushing sound (`steps/fall_air.ogg`) plays when dropping fast through air.
  - **Safe Drop (`<= 3.5` blocks)**: Soft landing (`steps/land_soft.ogg`), no damage.
  - **Damaging Fall (`> 3.5` blocks)**: Scales up with drop distance above 3.5 (10 HP per extra block), plus hard impact sound (`steps/land_hard.ogg`).
  - **Bone Fracture (`>= 8.0` blocks)**: Plays `combat/bone_break.ogg`, inflicts a 90-second leg fracture (movement slowed to 65% and sprinting disabled). Cure immediately with a crafted **Wooden Splint** (`splint`) or **Bandage** (`bandage`).
  - **Deep Water Cushion**: Landing inside a `water` box marked **`deep`** plays `steps/water_splash_big.ogg` and reduces fall damage by 70% while preventing bone fracture.
  - **Void Fall**: Dropping below `map.min_z - 6.0` kills the player immediately with void warning speech and respawns them cleanly at spawn.
- **Overhead Roof (`is_roof = 1`)**: Standing under an overhead `floor` platform above player height automatically muffles outdoor rain (`audio_engine.nvgt`).

---

## 4. Staircases (`PageUp` / `PageDown`) & Surface Footsteps

Staircases span a vertical volume `(min_x..max_x, min_y..max_y, min_z..max_z)` and allow vertical climbing with **`PageUp`** (ascend +1 Z step) and **`PageDown`** (descend -1 Z step):
- **Builder-Chosen Surface Footstep**: When you choose a surface for the staircase (`grass`, `dirt`, `stone`, `wood`, `sand`, `water`, or `carpet`), climbing or descending that staircase plays that exact surface's footsteps (`steps/<surface>_1..3.ogg`), NOT a generic staircase sound.
- This lets builders author stone dungeon spiral steps, creaking wooden watchtower stairs, soft indoor carpeted staircases, or mossy earth ledges simply by picking the surface on the staircase form.

---

## 5. STW 6-Axis Element Catalog (`.map` v2 Syntax)

| Tag | Element | Format & Coordinate Semantics |
|---|---|---|
| `M` | Map Header | `M\|name\|width\|height\|min_z\|max_z\|default_surface\|ambience\|pvp_enabled(0/1)` |
| `S` | Spawn Point | `S\|label\|x\|y\|z\|facing` |
| `Z` | Audio Zone | `Z\|name\|x1\|y1\|x2\|y2\|z1\|z2\|surface\|ambience\|safe_zone(0/1)` |
| `W` | Solid Wall | `W\|label\|x1\|y1\|x2\|y2\|z1\|z2\|material(wood/stone)\|occlude(0/1)` |
| `P` | Platform / Stairs / Ramp | `P\|label\|x1\|y1\|x2\|y2\|z1\|z2\|surface\|kind(floor/stairs/ramp)\|is_roof(0/1)\|axis(x/y)\|dir(-1/1)` |
| `L` | Water Body | `L\|label\|x1\|y1\|x2\|y2\|z1\|z2\|depth(shallow/deep)\|loop_sound` |
| `H` | Hazard Box | `H\|label\|x1\|y1\|x2\|y2\|z1\|z2\|damage\|interval_ms\|hit_sound` |
| `D` | Map Portal | `D\|label\|x1\|y1\|x2\|y2\|z1\|z2\|target_slug\|dest_x\|dest_y\|dest_z\|dest_fac\|auto_step(0/1)\|travel_sound` |
| `R` | Resource Node | `R\|type(tree/rock/iron_vein/berry_bush/herb_patch)\|x\|y\|z\|charges\|respawn_sec` |
| `A` | 3D Emitter | `A\|label\|sound_file\|x\|y\|z\|range\|volume` |

Note: Older `NAME=..` v1 files load automatically with an automatic base ground slab at `Z = 0` so existing maps remain valid.

---

## 6. Using the Line Manager (`F8 -> Line Manager`)

Line Manager mirrors STW's line-indexed map list:
1. Open **Line Manager** and choose **Change Line Filter** (`ALL`, `M`, `FLOOR`, `STAIRS`, `P`, `W`, `Z`, `L`, `H`, `D`, `R`, `A`, `S`).
2. Highlight any line (`Line 14: stairs Tower Steps: 54..58, 54..58, Z 0..10 (wood)`) and press **`Enter`**:
   - **Edit Using 6-Axis Coordinate Form**: Opens the element's form pre-filled with its exact bounds and surface/flags.
   - **Edit Raw Map Line Text**: Direct pipe-delimited string editing for power users.
   - **Teleport to Element Center**: Instantly warps your character there to test collision, acoustics, or sightlines by ear.
   - **Insert New Raw Line After This Line**: Inserts custom geometry immediately below the selected line.
   - **Duplicate This Line**: Clones the line right below itself (fast way to mirror bridge spans or walls).
   - **Move Line Up / Down**: Adjusts overlap priority (useful when two Zones or Floors overlap, as later lines take priority in `zone_at` / support tiebreaks).
   - **Delete This Line**: Removes the line after confirmation.
3. Remember to press **Save Active Map to Disk** before exiting if you want edits persisted permanently (while still on the undo stack inside the session).

---

## 7. Builder Sound Assets Quick Reference

Available ground & stair surfaces: `grass`, `dirt`, `stone`, `wood`, `sand`, `water`, `carpet`.
Available ambience loops under `client/sounds/`:
- `ambience/forest_day.ogg`
- `ambience/forest_night.ogg`
- `ambience/rain_loop.ogg`
- `ambience/river_loop.ogg`
- `ambience/settlement_hearth.ogg`
- `ambience/wind_gust.ogg`
- `ambience/cave_loop.ogg`
- `ambience/indoor_room.ogg`

Use **Preview Selected Sound** inside the Ambient Emitter form to hear any emitter sound before saving.
