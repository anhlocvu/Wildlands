# Feature Specification: STW Maps System, Dynamic Map-Scoped Animal Spawners & Map Navigation

**Feature Branch**: `003-stw-maps-system`
**Created**: 2026-11-18
**Status**: Approved by User
**Input**: User decisions: "Implement according to plan; Approach A respawn timer (start shared ms countdown whenever alive count drops below spawn quantity or starts empty, refilling up to max quantity with random picks from checked species); /maps (and /map) restricted to Builder rank and above; dynamic species list driven entirely by whatever creatures exist on the server (no hardcoding); remove Staff Panel animal spawner and Builder map-teleport; remove forced ambience when creating maps; populate Animal Spawn Zones across wildlands_valley excluding safe zones while leaving test maps empty; implement all 6 STW Maps System enhancements (Map Rules/Weather/Time flags, Acoustic Reverb Zones, 2-Corner Coordinate Clipboard & Bounds Ping, Map Templates & Clone Map, Animal Spawn Leash & Day/Night schedule, Internal Map Portals)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Dynamic Map-Scoped Animal Spawn Zones in F8 Builder (Priority: P1)

A Builder or Developer wants wildlife and enemies to appear strictly where each map defines them—and nowhere on blank test maps—without being attacked while building. In the F8 Map Builder, they select **Animal Spawn Zone** and enter a zone label, 6-axis bounds (`Minimum X`, `Maximum X`, `Minimum Y`, `Maximum Y`, `Minimum Z`, `Maximum Z`), a shared respawn timer in milliseconds (for example `5000` ms), a maximum spawn quantity (for example `5`), optional zone behavior (leash to zone, active day/night/always), and check one or more creature species in a multi-select checkbox list populated dynamically from all creatures registered on the server. When a map loads or a spawn zone is created with zero active creatures (or whenever any creature from that zone is killed so alive count falls below the target quantity), the shared timer waits the configured milliseconds and then spawns random creatures from the checked list until the zone reaches its target quantity. Multiple independent spawn zones with different coordinates and settings coexist per map, while the legacy global Staff Panel creature spawner and server-wide auto-spawner are removed.

**Why this priority**: Global uncontrolled animal spawning killed builders on newly created maps (`anhloc`); isolating creature life to map-authored spawn records directly unblocks safe building and unlocks proper RPG zone balancing.

**Independent Test**: Load a new map with zero animal spawn lines and verify zero wildlife appear over 10 seconds. Add an Animal Spawn Zone (`min_x..max_z`, `interval_ms = 5000`, `count = 3`, two checked species) via Builder; confirm zero creatures appear before 5000 ms, then 3 creatures drawn randomly from the checked species spawn after 5000 ms. Kill 1 creature (2/3 alive); confirm no instant respawn occurs before 5000 ms, then after 5000 ms the zone refills back to 3/3. Verify `wildlands_valley` contains authored spawn zones outside its Safe Zone while `skywatch_citadel` and `anhloc` remain creature-free.

**Acceptance Scenarios**:

1. **Given** a Staff member opens the Staff Panel, **When** viewing Staff Panel categories, **Then** the old `"Spawn Wildlife or Practice Bots"` and global wildlife population controls are absent, and maps without Animal Spawn Zone records remain completely free of auto-spawned wildlife.
2. **Given** a Builder opens `F8 -> Add Element -> Animal Spawn Zone`, **When** the form renders, **Then** the species list displays all creature species currently registered on the server as checkable items navigable with Up/Down arrows and toggled with Space, with zero hardcoded species subset.
3. **Given** an Animal Spawn Zone specifies `interval_ms = 5000` and `count = 5` with multiple checked species, **When** the zone has fewer than `5` living creatures (initially `0/5` or after any creature dies), **Then** the shared timer counts `5000` ms and spawns random creatures from the checked set until alive count reaches `5`.
4. **Given** multiple Animal Spawn Zones exist on the same map, **When** edited, duplicated, reordered, or deleted in the Line Manager, **Then** each zone maintains independent coordinates, timers, leashes, and populations without disturbing other zones.

---

### User Story 2 - `/maps` Command, Staff "View All Maps", and Builder Teleport Removal (Priority: P2)

A Builder or Staff member wants a single, predictable way to inspect all maps running on the server and travel between them to test or edit, without accidental teleports inside the Builder menu. In the F8 Builder Hub, **Switch Active Builder Map** strictly changes which map is targeted for editing without moving the player's avatar. Whenever a Builder (`rank >= Builder`) wants to move to another map, they either type `/maps` (or `/map`) in chat or select **View All Maps (`/maps`)** in the Staff Panel; both open an identical menu listing every map hosted on the server, and pressing Enter on any map immediately teleports them to that map's spawn point (and aligns their active Builder edit map).

**Why this priority**: Separating "select which map I am editing" from "travel my character to a map" eliminates Builder confusion and provides a fast, consistent multi-map navigation workflow.

**Independent Test**: Sign in as a regular Player (`rank = 0`) and run `/maps`; verify permission denial. Sign in as a Builder (`rank = 1`), use F8 Switch Active Map to target a second map and verify the player stays on the first map. Type `/maps`, select the second map and press Enter; verify map transfer completes. Open Staff Panel (`Mod+`), choose **View All Maps (`/maps`)**, and verify it opens the exact same server maps menu and teleports upon Enter.

**Acceptance Scenarios**:

1. **Given** a Builder selects a different map in `F8 -> Switch Active Builder Map`, **When** confirming the selection, **Then** only the active editing target changes while the player remains at their current map and coordinates.
2. **Given** a Builder or Staff member types `/maps` (or chooses **View All Maps** in Staff Panel), **When** the menu opens, **Then** every map loaded on the server is listed with name, dimensions, elevation bounds, and online player count, and pressing Enter on an entry teleports the player to that map's spawn.
3. **Given** a standard Player (`rank = 0`) enters `/maps`, **When** the server processes the request, **Then** access is refused politely because `/maps` is restricted to Builder rank and above.

---

### User Story 3 - Silent Ambience Default on Map Creation & STW Maps System (Priority: P3)

A Builder creating a fresh map wants to choose only the map's ground surface without being forced to pick a background ambience loop (or having forest ambience forced on empty maps). Later, they add exact audio zones or 3D emitters where desired. Furthermore, builders and players experience the full **STW Maps System**: per-map environment rules (build permission, outdoor weather immunity, locked day/night time), distinct acoustic reverb presets per audio zone (dry outdoors, small room, stone hall, deep cave), a 2-corner coordinate clipboard that auto-fills 6-axis Box Forms plus 3D bounds pinging in Line Manager, starter map templates and one-step Map Cloning, and internal same-map travel portals.

**Why this priority**: Clean silent map creation prevents unwanted background noise on custom maps, while per-map rules, acoustic reverb, corner auto-fill, templates, and bounds pinging dramatically boost map quality and screen-reader builder speed.

**Independent Test**: Create a new map in F8 without selecting any ambience loop (choosing ground surface `stone` and template `Underground Cave` with weather off and time `night`). Visit it via `/maps`: confirm zero ambient background loop plays and rain never sounds or chills the player. Add an Audio Zone with `cave` reverb and `ambience/cave_loop.ogg`, step inside to confirm audible reverb + cave ambience, step outside to confirm silence resumes. Mark two corners in the world, open Wall or Animal Spawn form, confirm bounds auto-fill; use `Ping Bounds` in Line Manager and verify 3D bounds cues play; clone the map and verify the clone appears in `/maps`.

**Acceptance Scenarios**:

1. **Given** a Builder opens `F8 -> Create New Map`, **When** filling out the form, **Then** no ambient sound selection is presented; only surface, dimensions, elevation bounds, template, and spawn point are chosen, and the created map plays zero ambient background loop until zones or emitters are added.
2. **Given** a map disables weather (`weather_enabled = 0`) or locks time (`day`/`night`), **When** global weather turns rainy or server time shifts, **Then** players on that map experience no rain ambience/chill and observe the map's locked time of day.
3. **Given** a Builder marks Corner 1 and Corner 2, **When** opening any 6-axis box creation form (`Floor`, `Wall`, `Stairs`, `Zone`, `Animal Spawn`, etc.), **Then** `Min X..Max Z` fields are pre-populated from those corners, and Line Manager offers **Ping Element Bounds** to preview element dimensions spatially.
4. **Given** an Audio Zone specifies an acoustic reverb preset (`room`, `hall`, `cave`), **When** a player walks inside that zone, **Then** world, actor, threat, and footstep audio smoothly adopt the zone's acoustic reverb, returning to dry outdoors upon leaving.

---

### Edge Cases

- What happens if an Animal Spawn Zone lists a creature ID that is later removed or unrecognized, or has an empty species list? Server validation rejects empty species lists cleanly, ignores unknown species IDs safely without crashing, and only spawns valid registered species.
- What happens if an Animal Spawn Zone's 3D box has no valid walkable floor inside its `[min_z..max_z]` (or is entirely covered by a wall or safe zone)? Spawn placement samples candidate positions and avoids walls/safe zones; if no valid supported ground exists inside the box, it avoids spawning stuck mobs inside solid walls.
- What happens if a Builder creates a map with `"none"` ambience and later adds an Audio Zone with `"none"` vs `"ambience/cave_loop.ogg"`? Zones set to `"none"` (or silent) produce silence when no map default ambience exists, and smoothly crossfade to silence when exiting an audible zone into a silent zone.
- What happens if an `E` Animal Spawn Zone is edited or deleted while 4 mobs from it are alive on the map? Reloading/reconciling the map's spawn zones cleanly removes/rebinds orphaned zone mobs so populations match the edited `.map` lines with zero stale references.
- What happens if a Map Travel Portal (`D`) points to the same map slug it sits on (internal elevator/door)? Transfer moves the player smoothly to the destination `(X, Y, Z, Facing)` within the same map without disconnecting or re-downloading the whole map unnecessarily.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Server MUST NOT auto-spawn global wildlife across maps indiscriminately; non-bot wildlife MUST spawn exclusively from per-map **Animal Spawn Zone (`E`)** lines defined in each map file.
- **FR-002**: Staff Panel MUST remove the legacy `"Spawn Wildlife or Practice Bots"` menu and `"Set Target Wildlife Count"` world option.
- **FR-003**: Map schema and Builder (`F8`) MUST support multiple **Animal Spawn Zone (`E`)** entries per map with fields: Label, `Min X`, `Max X`, `Min Y`, `Max Y`, `Min Z`, `Max Z`, shared spawn/respawn delay in milliseconds (`interval_ms`), maximum alive quantity (`count`), multi-select creature list (`species_csv`), leash toggle (`leash`), and time schedule (`always|day|night`).
- **FR-004**: Builder's Animal Spawn Zone form MUST present `Min X`, `Max X`, `Min Y`, `Max Y`, `Min Z`, `Max Z`, `interval_ms`, `count`, a multi-select checkbox list populated dynamically from all creatures currently registered on the server (no hardcoded client/server list), and a **Create Animal Spawn Zone** submit button.
- **FR-005**: Server MUST implement Approach A shared respawn timing per Animal Spawn Zone: whenever living creature count for a zone is less than its configured `count` (including `0` at map load/zone creation or `< count` after any creature dies), the zone's timer waits `interval_ms` milliseconds and then spawns random selections from its checked species until living count reaches `count`.
- **FR-006**: `wildlands_valley.map` MUST define realistic Animal Spawn Zones outside its Settlement Safe Zone, while `skywatch_citadel.map` and `anhloc.map` MUST contain zero Animal Spawn Zones.
- **FR-007**: Builder (`F8`) **Switch Active Builder Map** MUST only change the active editing target without teleporting the player, and Line Manager `Teleport to Element` MUST require already standing on that map (directing builders to `/maps` otherwise).
- **FR-008**: System MUST implement `/maps` (and `/map` alias) restricted to `rank >= RANK_BUILDER`, plus a **View All Maps (`/maps`)** option in the Staff Panel (`F9`) opening the identical server map list menu where pressing Enter on any map teleports the player to that map's spawn.
- **FR-009**: `Create New Map` form in F8 Builder MUST omit ambient loop selection entirely (requiring ground surface, bounds, template, and spawn), defaulting map ambience to silent (`"none"`); clients MUST silence ambient loops when a map/zone specifies `"none"` rather than forcing forest audio.
- **FR-010**: System MUST implement the full **STW Maps System** features:
  1. Per-map header rules (`allow_build`, `weather_enabled`, `time_mode`: `auto|day|night`).
  2. Acoustic Reverb Zones on `Z` records (`none`, `room`, `hall`, `cave`) driven by real engine reverb nodes on world/actor/threat/self mixers (keeping UI/speech dry).
  3. Builder 2-Corner Coordinate Clipboard (mark Corner 1 & Corner 2 from cursor or player position to auto-fill 6-axis Box Forms) and Line Manager **Ping Bounds** 3D audio preview.
  4. Map Templates in `Create New Map` (`Flat Ground`, `Void Sky`, `Enclosed Arena`, `Underground Cave`) and **Clone Map** in F8 Builder Hub.
  5. Animal Spawn Zone leash bounds (keeping zone mobs within their area + safe-zone exclusion) and active time-of-day filter (`always`, `day`, `night`).
  6. Same-map internal Portal (`D`) support with smooth spatial cueing.

### Key Entities

- **MapAnimalSpawn (`E`)**: Map-scoped 3D bounding box spawner `(label, min_x..max_z, interval_ms, count, species[], leash, active_time)`.
- **SpeciesCatalogEntry**: Server-authoritative creature descriptor `(kind, name, hostile)` synced dynamically to authorized builders.
- **MapRules (`M` extension)**: Per-map simulation flags `(allow_build, weather_enabled, time_mode)` controlling building, weather exposure/audio, and lighting cycle.
- **AcousticReverbPreset (`Z` extension)**: Per-zone reverb classification (`none`, `room`, `hall`, `cave`) controlling spatial audio ambience reflections.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: New maps created without Animal Spawn Zones spawn `0` wildlife over continuous server uptime; maps with an `E` zone (`interval_ms = 5000, count = 5`) spawn `0` mobs before `5000` ms, spawn `5` randomized mobs from the checked species once `5000` ms elapses, and refill cleanly `5000` ms after any mob death.
- **SC-002**: Adding a new creature definition to the server's creature catalog immediately causes it to appear inside the Builder Animal Spawn Zone checkbox list with zero UI code edits.
- **SC-003**: Builders (`rank >= 1`) open the unified Server Maps menu via `/maps` or Staff Panel -> View All Maps and teleport to any loaded map on Enter in under 1 second, while regular Players (`rank = 0`) are cleanly denied `/maps`.
- **SC-004**: Newly created maps without added Audio Zones or Emitters emit zero forced background forest loop audio, while zones with `cave`/`hall`/`room` reverb audibly apply reflections and weather-disabled maps suppress rain.
- **SC-005**: All offline unit checks, live E2E integration checks (`tools/run_checks.ps1`), and `nvgt -c` builds for both `server/server.exe` and `client/client.exe` pass with exit code `0`.

## Assumptions

- `bot_survivor` remains registered in the dynamic creature catalog (`g_species`), so the server dynamically includes all `g_species` entries in the Builder's species list; `server.exe --bots N` continues to support automated test/practice bots separately when explicitly launched with `--bots > 0`.
- Existing `.map` v1/v2 files without trailing `M`/`Z` STW v3 columns (`allow_build`, `weather_enabled`, `time_mode`, `reverb_preset`) default seamlessly to `allow_build=1`, `weather_enabled=1`, `time_mode=auto`, and `reverb_preset=none`.
