# Audio Map Builder Guide (`F8`) — Wildlands Online v3 (STW Maps System)

Welcome to the **STW Maps System & Multi-Map Audio Map Builder**. Authorized staff (`Builder`, `Admin`, or allowlisted `Developer`) can author 3D maps with vertical architecture, staircases, silent or zoned acoustics (`audio_freeverb_node` reverb presets), map-scoped Animal Spawn Zones (`E`), map starter templates, map cloning, and 2-corner coordinate clipboards — all screen-reader accessible.

---

## 1. Opening the Builder Hub (`F8`) & Navigating Maps (`/maps`)

Press **`F8`** in-game (or open **Pause Menu -> Audio Map Builder Hub (F8)**) to manage map authoring:

1. **Add Element or Animal Spawn Zone**: Opens 6-axis `audio_form` dialogs (`Minimum X`, `Maximum X`, `Minimum Y`, `Maximum Y`, `Minimum Z`, `Maximum Z`). If both Corner 1 and Corner 2 are set in the **Coordinate Clipboard**, bounds auto-fill automatically!
2. **Line Manager (`Browse, Edit, Ping Bounds, Move, Duplicate, Delete`)**: Inspect, filter (`E`, `M`, `FLOOR`, `STAIRS`, `P`, `W`, `Z`, `L`, `H`, `D`, `R`, `A`, `S`), reorder, or **Ping Element Bounds in 3D Audio** (plays a 3D chime at SW -> SE -> NE -> NW corners around you).
3. **Coordinate Clipboard**: Mark **Corner 1** (`M` in cursor mode or hub menu) and **Corner 2** (`Shift+M` in cursor mode or hub menu) from your player or cursor position to pre-fill 6-axis box forms quickly.
4. **Create New Map (Silent by Default + Templates)**: Creates a new `.map` starting with `ambience_default = "none"` (no forced ambience audio until you add a Zone or edit the header). Choose a starter template:
   - **`flat`**: Full ground slab at Spawn Z.
   - **`void`**: Floating 6x6 starter pad at Spawn Z.
   - **`arena`**: Floor slab enclosed by stone perimeter walls + `hall` acoustic reverb.
   - **`cave`**: Enclosed stone floor & overhead ceiling roof + `cave` acoustic reverb.
5. **Clone Active Map**: Duplicates the active builder map (geometry, zones, portals, animal spawns) to a new map slug and display name.
6. **Switch Active Builder Map (Edit Only)**: Changes which map your F8 Builder Hub and Line Manager edit **without teleporting your character**.
   - **To travel/teleport to another map**, type **`/maps`** (or `/map`, available to `Builder` rank and higher) or open **`F9 -> View All Maps (/maps)`**, highlight any map on the server, and press **`Enter`**.
7. **Edit Active Map Properties (`M` Header)**: Configure Display Name, X/Y bounds, Z min/max, default surface, default ambience (including **`None (Silent)`**), **PvP duels**, **Allow Survival Building (`allow_build`)**, **Enable Weather/Rain (`weather_enabled`)**, and **Time of Day Rule (`auto` / `day` / `night`)**.
8. **Undo / Noclip / Cursor Mode / Validate / Save / Reload / Delete**:
   - **Undo**: Reverts the last edit (up to 25 steps per map).
   - **Builder Noclip Flight**: Bypasses wall collision & gravity while flying through builds.
   - **Validate / Save / Reload / Delete**: Validates integrity, atomically saves `.tmp` -> `.bak` -> `.map`, reloads live (also syncing live animal spawn zones), or archives non-default maps to `.deleted.bak`.

---

## 2. Dynamic Animal Spawn Zones (`E`) — Map-Scoped Wildlife

There is NO global random wildlife spawning across maps. Blank or custom test maps remain completely peaceful until you explicitly place **Animal Spawn Zones (`E`)**:
- Open **`F8 -> Add Element or Animal Spawn Zone -> Animal Spawn Zone`**.
- Fill in: **Label**, **Minimum X**, **Maximum X**, **Minimum Y**, **Maximum Y**, **Minimum Z**, **Maximum Z**, **Spawn / Respawn Delay (ms)** (e.g. `5000` ms), **Spawn Quantity** (max living creatures maintained by this line), **Animal Species multi-select checkbox list** (`Up`/`Down` to browse dynamically synced server species, **`Space`** to check one or multiple species), **Leash to Zone**, and **Active Time (`always` / `day` / `night`)**, then press **Create Animal Spawn Zone**.
- **Shared Respawn Timer**: When a zone has fewer living animals than **Quantity** (on startup, after zone creation, or when a creature is slain), it waits **Delay (ms)** once (additional kills during the wait share that timer) and then spawns randomized species from your checked selection up to **Quantity**. Multiple independent `E` zones with different coordinates can live on the same map.

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

## 6. STW 6-Axis Element Catalog (`.map` v3 Syntax)

| Tag | Element | Format & Coordinate Semantics |
|---|---|---|
| `M` | Map Header | `M\|name\|w\|h\|min_z\|max_z\|default_surface\|ambience(or none)\|pvp\|allow_build\|weather\|time_mode(auto/day/night)` |
| `S` | Spawn Point | `S\|label\|x\|y\|z\|facing` |
| `Z` | Audio Zone | `Z\|name\|x1\|y1\|x2\|y2\|z1\|z2\|surface\|ambience(or none)\|safe_zone\|reverb(none/room/hall/cave)` |
| `W` | Solid Wall | `W\|label\|x1\|y1\|x2\|y2\|z1\|z2\|material(wood/stone)\|occlude(0/1)` |
| `P` | Platform / Stairs / Ramp | `P\|label\|x1\|y1\|x2\|y2\|z1\|z2\|surface\|kind(floor/stairs/ramp)\|is_roof(0/1)\|axis(x/y)\|dir(-1/1)` |
| `L` | Water Body | `L\|label\|x1\|y1\|x2\|y2\|z1\|z2\|depth(shallow/deep)\|loop_sound` |
| `H` | Hazard Box | `H\|label\|x1\|y1\|x2\|y2\|z1\|z2\|damage\|interval_ms\|hit_sound` |
| `D` | Map Portal | `D\|label\|x1\|y1\|x2\|y2\|z1\|z2\|target_slug(or same map)\|dest_x\|dest_y\|dest_z\|dest_fac\|auto_step(0/1)\|travel_sound` |
| `R` | Resource Node | `R\|type(tree/rock/iron_vein/berry_bush/herb_patch)\|x\|y\|z\|charges\|respawn_sec` |
| `A` | 3D Emitter | `A\|label\|sound_file\|x\|y\|z\|range\|volume` |
| `E` | Animal Spawn Zone | `E\|label\|x1\|y1\|x2\|y2\|z1\|z2\|interval_ms\|count\|species_csv\|leash(0/1)\|active_time(always/day/night)` |

Older v1 and v2 `.map` files load automatically with safe defaults (`allow_build=1`, `weather=1`, `time_mode=auto`, `reverb=none`). Use Zone **`reverb_preset`** (`room`, `hall`, `cave`) to apply real-time NVGT Freeverb acoustics on footsteps and world SFX inside chambers and dungeons!

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
