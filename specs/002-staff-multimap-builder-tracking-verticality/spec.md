# Feature Specification: STW-Style Tracking, 3D Verticality, Multi-Map Builder & Staff Operations

**Feature Branch**: `002-staff-multimap-builder-tracking-verticality`
**Created**: 2026-11-18
**Status**: Approved by User
**Input**: User request: "Professional Staff Panel with multi-category menus, full account list with Online or Last Seen timestamps, server shutdown/restart/moderation/world controls; multi-map architecture with STW-style F8 Map Builder, create-new-map form, min/max 6-axis box inputs, Line Manager, Staff & Builder documentation; completely rebuilt STW-style Tracker (categories, <= 30 tile list range, Ctrl+=/Ctrl+- category navigation, =/- item navigation, Backspace start tracking with 3D radar, Shift+Backspace stop, O relative readout); PageUp/PageDown staircase climbing playing the chosen surface footstep sound, air/void law when no floor supports the player, falling sound and height-based fall damage / fracture; additional verified sound assets; English in-game text consistency."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - STW-Style Category Radar & Live 3D Target Tracking (Priority: P1)

A player wants to locate nearby wildlife, dropped items, player-built structures, world resource objects, or other players purely by ear using the classic STW tracking workflow instead of the old single-list scanner. Using `Ctrl+Equals` and `Ctrl+Minus`, they cycle between six tracking categories (`All`, `Objects`, `Items`, `Animals`, `Structures`, `Players`), hearing each category name and count of targets within 30 tiles (`<= 30`). Using `Equals` and `Minus`, they step forward and backward through targets in that category, hearing each target's relative direction, distance, and index. Pressing `Backspace` starts active tracking on the selected target, emitting a 3D radar beacon positioned continuously at the target's live coordinates. Pressing `O` at any time announces the tracked (or focused) target's relative direction, step distance, and elevation (`"Wolf, behind and to your left, 12 steps"`). Pressing `Shift+Backspace` stops active tracking.

**Why this priority**: Blind players rely constantly on fast target scanning and directional radar homing to navigate, forage, hunt, and find teammates; replacing the broken old scanner directly unlocks playable spatial orientation.

**Independent Test**: Spawn a player near a wolf, a resource tree, a wood campfire, a dropped item, and another player within 30 tiles, plus one object 40 tiles away. Cycle categories with `Ctrl+=` / `Ctrl+-`, confirm the 40-tile object is excluded while `<= 30` targets appear, step with `=` / `-`, press `Backspace` to start 3D radar homing, move the wolf and press `O` to verify updated relative direction/steps, move beyond range or kill the wolf to verify automatic lost-track alert, and press `Shift+Backspace` to cancel tracking.

**Acceptance Scenarios**:

1. **Given** targets exist within 30 tiles and beyond 30 tiles, **When** the player cycles categories (`Ctrl+=` / `Ctrl+-`) and steps targets (`=` / `-`), **Then** only targets at distance `<= 30.0` tiles on the player's current map appear in the active category sorted nearest-first, and the old `T` scanner is retired.
2. **Given** the player highlights a target with `=` / `-`, **When** they press `Backspace`, **Then** the client announces `"Started tracking <Target>"`, plays `ui/track_start.ogg`, and emits periodic 3D radar pings (`ui/track_ping.ogg`) at the target's live `(X, Y, Z)` coordinates with cadence tightening as distance closes.
3. **Given** a target is actively tracked, **When** the player presses `O`, **Then** the client speaks the target's live relative direction, step distance, and elevation difference (e.g., `"Wolf, behind and to your left, 14 steps, above"`).
4. **Given** a target is actively tracked, **When** the player presses `Shift+Backspace` (or the target dies, is collected, changes map, or moves out of range), **Then** tracking stops immediately with an audible cue (`ui/track_stop.ogg` or `ui/track_lost.ogg`) and clear spoken confirmation.

---

### User Story 2 - 3D Verticality, Stair Climbing, Air/Void Law & Fall Trauma (Priority: P2)

A player explores multi-story structures, watchtowers, caves with negative Z basements, and bridges over empty air. Floors exist only where map tile/platform boxes (`min_x..max_x, min_y..max_y, min_z..max_z`) or water/structures provide solid support; areas without supporting ground below the player are open **Air**. When standing in a Staircase/Ladder region (`min_z..max_z`, e.g., `0..20`), pressing `PageUp` climbs up 1 Z unit and `PageDown` climbs down 1 Z unit, playing the **chosen surface footstep sound** configured on that staircase (e.g., wood or stone footsteps) rather than a generic ladder sound. Stepping off an elevated edge or off a mid-air staircase into Air causes the player to fall under gravity with a 3D falling wind sound (`steps/fall_air.ogg`), taking height-scaled impact damage (and possible leg fracture treatable with bandages/splints) upon landing on lower terrain, mitigated by deep water, or dying if falling into bottomless void.

**Why this priority**: Vertical architecture, stair traversal, and real fall physics define STW-style 3D exploration and make `min_z`/`max_z` map building meaningful.

**Independent Test**: Walk onto a floor at `z=0`, step onto a wooden staircase spanning `z=0..20`, climb up with `PageUp` (verifying wood footstep audio plays and Z increases without falling), climb back down with `PageDown` (never switching message buffers), then climb up to `z=12` and walk off the side over empty Air with ground at `z=0` below; verify falling sound, fall damage proportionate to 12 units of drop, bone-break cue/fracture on severe drops, and void death when stepping outside all floor plates.

**Acceptance Scenarios**:

1. **Given** the player stands inside a staircase volume (`z=0..20`) configured with surface `wood`, **When** they press `PageUp` or `PageDown`, **Then** the server steps player Z up or down within `[min_z, max_z]` and broadcasts/plays `wood` footstep audio without switching message buffer channels (buffers remain on `,` / `.`).
2. **Given** a map defines a floor at `x: 0..50, y: 0..50, z: 0..0` and an upper floor at `x: 10..20, y: 10..20, z: 10..10`, **When** the player stands outside any floor box (or steps off an upper ledge with no bridge underneath), **Then** the server treats unsupported space as Air and accelerates the player downward under gravity while emitting `steps/fall_air.ogg` once drop velocity/height exceeds threshold.
3. **Given** a player falls from height `H` onto a lower surface, **When** `H > 2.5`, **Then** landing deals height-scaled fall damage, plays `steps/land_hard.ogg` and `combat/bone_break.ogg` on high falls (`H > 5.5`), applies a curable leg fracture debuff for severe falls (`H > 6.5`), or grants deep-water cushioning (`steps/water_splash_big.ogg`).
4. **Given** a map includes negative Z areas (`min_z >= -50`), **When** a staircase leads down to `z = -10`, **Then** players descend smoothly to `z = -10` and hear spatial audio at true negative Z coordinates.

---

### User Story 3 - Multi-Map World Architecture & Map Travel Portals (Priority: P3)

The server hosts multiple `.map` files simultaneously from `maps/` rather than a single static map. Each player session, resource node, wildlife mob, loot drop, arrow projectile, and built structure belongs to a specific `map_name`. Players move seamlessly between connected maps using **Map Travel Portals / Doors** placed in maps (either auto-stepping or pressing `Enter`/`E`), or via Staff teleportation, receiving only snapshots, spatial audio, and local chat for their current map.

**Why this priority**: Multi-map worlds are essential for an expanding online RPG/survival game and are the prerequisite for creating and visiting new maps directly in the F8 Builder.

**Independent Test**: Load a server hosting `wildlands_valley.map` and a second connected map (`skywatch_citadel.map`). Place Player A on Map 1 and Player B on Map 2; verify neither receives snapshots or local chat from the other. Walk Player A through the portal onto Map 2; verify `world/portal_travel.ogg` plays, new map geometry/objects sync cleanly, and Players A and B now see and hear each other.

**Acceptance Scenarios**:

1. **Given** multiple `.map` files exist in `maps/`, **When** the server starts, **Then** it validates and instantiates every map into an independent simulation world (`MapInstance`) and persists each player's `current_map` in `accounts.dat`.
2. **Given** a map contains a Portal/Link (`LNK` / `PORTAL`) pointing to another loaded map and target `(X, Y, Z, Facing)`, **When** a player enters or interacts with it, **Then** the server transfers the player to the destination map, syncs `MAP_HDR`/`MAP_CHK`/`MAP_OBJ` for that map, and leaves other maps unaffected.

---

### User Story 4 - STW-Style F8 Map Builder, Box Forms & Line Manager (Priority: P4)

Authorized Builders, Admins, and Developers press `F8` to open a full, screen-reader-optimized **STW-Style Audio Map Builder Menu** instead of being forced to walk around marking corners tile by tile. From this menu they can **create new maps** (specifying slug, display name, X/Y bounds, Min/Max Z, default surface, default ambience, initial spawn), switch the active map, add any element (Floors, Walls, Stairs/Ladders/Ramps, Zones, Water, Roofs/Indoor Areas, Hazard Zones, Map Portals, Resource Spawners, Ambient Emitters, Spawn Points) via multi-field **6-axis box input forms (`Min X, Max X, Min Y, Max Y, Min Z, Max Z`)**, open a **Line Manager** to browse, filter, edit (both field-by-field form and raw line text), duplicate, insert, reorder, teleport to, or delete individual `.map` lines with Undo support, and validate/save/hot-reload changes live to all clients on that map.

**Why this priority**: Constructing large 3D multi-map environments by stepping corner-to-corner does not scale; box forms and a Line Manager are the signature productivity tools of STW builders.

**Independent Test**: Sign in as a Builder/Dev, press `F8`, create a new map `"outpost"` (`60x60`, `min_z=-10`, `max_z=30`), add a ground floor `0..60, 0..60, z 0..0`, an upper floor `10..20, 10..20, z 10..10`, and stairs `10..12, 8..10, z 0..10` using box input forms, open **Line Manager** to edit the upper floor's Z to `12`, duplicate a wall line, delete a test line, undo/save, teleport to the new map, and climb the new stairs with `PageUp`.

**Acceptance Scenarios**:

1. **Given** an authorized Builder (`rank >= RANK_BUILDER`) presses `F8`, **When** the Builder Hub Menu opens, **Then** they can choose **Create New Map**, **Switch Builder Map**, **Add Element (Box Form)**, **Line Manager**, **Toggle Free-Roam Noclip Builder Cursor**, **Undo**, **Validate**, or **Save & Hot-Reload**, without needing raw text-editor access to the server filesystem.
2. **Given** a builder adds or edits any box-shaped map element (Floor, Wall, Stairs, Zone, Water, Hazard, Portal), **When** the form opens, **Then** it presents clear labeled fields for `Min X`, `Max X`, `Min Y`, `Max Y`, `Min Z`, `Max Z` (pre-filled sensibly around current position or existing record) and validates `min <= max` before applying on the server.
3. **Given** a builder opens **Line Manager**, **When** they browse or filter the map lines, **Then** each entry speaks its line index, record type, name, and dimensions; selecting it lets them edit via Form, edit raw `.map` text, duplicate, insert above/below, move up/down, teleport to its location, or delete it.

---

### User Story 5 - Multi-Category Professional Staff Panel & Safe Server Lifecycle (Priority: P5)

Staff members (`Moderator`, `Admin`, `Developer`) access a unified, categorized **Staff Panel** (`F9` or via Pause/Social menus) that presents organized menus and target pickers instead of memorizing typed commands or item IDs. It includes an **Account Directory** listing all registered server accounts showing `"Online (<Map>, <Zone>)"` for connected users and `"Last seen: <relative & formatted timestamp>"` for offline users, plus one-click target action menus (teleport, summon, move to map, heal, give item from picker, inspect inventory, kick, timed mute/ban, unban, set rank, rescue position, clear session token). Developers gain **Server Lifecycle** controls to safely **Shutdown** or **Restart** the server with configurable countdowns, spoken/audio warnings, atomic saves, maintenance mode, MOTD/Changelog editing, live telemetry, audit log viewing, player report handling, and Staff Chat (`/sc`).

**Why this priority**: Running a live multiplayer server requires non-destructive, screen-reader-friendly administration tools that prevent operator typos and protect persistence during shutdowns or restarts.

**Independent Test**: Connect a Developer and a regular Player; log the Player out to record `last_seen`, then reconnect Player 2. Open Staff Panel -> Account Directory as Developer; verify Player 2 reads `"Online"` while offline Player reads `"Last seen: ..."` with timestamp. Select Player 2 from the directory and execute Give Item (from menu picker), Teleport, Kick; verify rank hierarchy blocks lower ranks from moderating equal/higher ranks; trigger a timed Shutdown and a Restart command verifying clean atomic save and server relaunch/termination.

**Acceptance Scenarios**:

1. **Given** a Staff member opens **Account Directory** in the Staff Panel, **When** the server responds with the account list, **Then** currently connected accounts show `Online (<Map>, <Zone>)` instead of last-seen time, while offline accounts show `Last seen: <time ago / YYYY-MM-DD HH:MM>` computed from server timestamps.
2. **Given** a Staff member selects an account in the directory, **When** they choose an action (Teleport, Summon, Move Map, Heal, Give Item, Kick, Mute, Ban, Unban, Set Rank, Rescue Spawn), **Then** the server enforces strict rank hierarchy (`actor.rank > target.rank`, `DEV` immutable over network), executes the action, announces changes to affected players, and writes an audit log entry.
3. **Given** a Developer triggers **Shutdown Server** or **Restart Server**, **When** the countdown completes (or immediately if 0s), **Then** the server broadcasts `SPEAK` and `multi/server_shutdown.ogg` / `multi/countdown_tick.ogg`, flushes all dirty accounts, world objects, reports, and maps atomically to disk, cleanly closes network sockets, and either exits or relaunches the server executable with preserved CLI flags.

---

### User Story 6 - Expanded Verified Audio Library & Staff/Builder Manuals (Priority: P6)

Every newly introduced gameplay and administrative event (tracker start/stop/ping/lost/arrived/category switch, air fall wind, bone break, big water splash, hazard hit, portal travel, indoor ambience, builder line edits/map creation, staff alert, server shutdown) uses verified real CC0/open-license audio recordings downloaded, deduplicated, loudness-normalized, and checked against `client/sounds/manifest.txt`. Complete, screen-reader-friendly manuals (`docs/BUILDER_GUIDE.md` and `docs/STAFF_GUIDE.md`) document every workflow and shortcut, and summaries are readable directly inside the game menus.

**Why this priority**: In an audio game, silent features feel broken and complex builder/staff tools require authoritative documentation alongside in-game discovery.

**Independent Test**: Run `tools/asset_pipeline.py` and `tools/asset_check.nvgt` to confirm all new `.ogg` assets pass magic-byte, uniqueness, and manifest verification; open both `docs/BUILDER_GUIDE.md` and `docs/STAFF_GUIDE.md` and verify in-game Help/Guide menus read all sections cleanly.

**Acceptance Scenarios**:

1. **Given** the updated asset pipeline runs, **When** `asset_check.nvgt` validates `client/sounds/manifest.txt`, **Then** 100% of required sounds exist on disk with valid `OggS` headers, unique MD5 hashes, and zero synthetic tones.
2. **Given** a Builder or Staff member opens the documentation in `docs/` or via the in-game guide menu, **When** reading through instructions, **Then** every Staff Panel category, Builder box-form rule, Line Manager action, tracking key, and Z/stair/air rule is accurately documented with English UI parity.

---

### Edge Cases

- What happens if a player is tracking a target (`Backspace`) and the target moves slightly from 29 tiles to 31 tiles away? List scanning strictly enforces `<= 30.0` tiles when enumerating targets, while an actively tracked target remains locked up to `35.0` (`EARSHOT_RADIUS`) before triggering `"Lost track"` so edge jitter does not constantly break active homing.
- What happens if a staircase has `min_z = 0, max_z = 20` and a player tries pressing `PageUp` while already at `z = 20` or `PageDown` at `z = 0`? Climbing clamps cleanly at `max_z` / `min_z` and plays a subtle edge/thud cue without teleporting or passing through a solid ceiling wall.
- What happens if a builder sets `min_x > max_x` or `min_z > max_z` in a box form or edits a raw `.map` line into invalid syntax? Server-side validation rejects or swaps bounds safely only with explicit feedback, rejects malformed raw lines before committing, preserves an undo snapshot and `.map.bak` backup, and prevents deleting the last `S` spawn point or deleting a map while players stand inside it (or automatically moves players safely to default map first).
- What happens if a Developer runs `Restart Server` while still bound to UDP port `7100`? The shutting-down server must close its ENet socket (`net.destroy(true)`) before spawning (or pass a `--bind-delay-ms 1000` flag to the child process) so the restarted server never hits a port-in-use bind failure.
- What happens when reading legacy `accounts.dat` (`ACCOUNTS_V1`) or `wildlands_valley.map` after upgrading? Account and map parsers MUST seamlessly migrate `ACCOUNTS_V1` records (defaulting `last_seen = 0`, `current_map = default_map`) and ensure starter maps have base ground plates covering walkable `z = 0` terrain so existing worlds do not turn into accidental void pits.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST keep all in-game client/server speech, menus, buffer lines, and tracker readouts strictly in **English**.
- **FR-002**: Client MUST replace the legacy `T` / `Shift+T` scanner with an STW-style category tracker featuring `All`, `Objects`, `Items`, `Animals`, `Structures`, and `Players`, filtering list entries to distance `<= 30.0` tiles on the player's current map.
- **FR-003**: Tracker MUST support `Ctrl+Equals` / `Ctrl+Minus` (next/previous category), `Equals` / `Minus` (next/previous item in category), `Backspace` (start live 3D radar tracking), `Shift+Backspace` (stop tracking), and `O` (speak relative direction, steps, and elevation of tracked/focused target), with all bindings remappable in Settings.
- **FR-004**: Server and shared map schema MUST represent terrain floors, elevated decks, roofs, walls, water bodies, hazard zones, map portals, and staircases using 3D boxes (`min_x, max_x, min_y, max_y, min_z, max_z`) supporting `Z` in `[-50 .. 100]`.
- **FR-005**: Server MUST implement the Air/Void physics law: space without a supporting floor, water, or structure beneath `(x, y, z)` provides no floor support, triggering gravity fall, `steps/fall_air.ogg`, height-scaled fall damage, fracture debuff on high drops (curable by bandage/splint), deep-water fall mitigation, and void death below map minimum Z.
- **FR-006**: Server MUST process `PageUp` (`IN_CLIMB_UP`) and `PageDown` (`IN_CLIMB_DOWN`) when inside a staircase volume, moving player Z between `min_z` and `max_z` while preventing mid-stair gravity drop and playing footstep audio matching the staircase's configured `surface` (never a separate generic stair sound), and client MUST unbind `PageUp`/`PageDown` from message buffer channel switching.
- **FR-007**: Server MUST load and simulate multiple `.map` worlds concurrently from `maps/`, scoping snapshots, audio broadcasts, local chat, structures, resource nodes, drops, and wildlife strictly by `map_name`, and supporting map-to-map transfer via Map Portals and Staff Teleport.
- **FR-008**: Map Builder (`F8`) MUST present a full multi-category Builder Hub menu supporting Create New Map (name, slug, X/Y/minZ/maxZ bounds, default surface/ambience, initial spawn), Switch Active Map, 6-axis box input forms for all map element types, Noclip Builder Cursor toggle, Line Manager (list, filter, form edit, raw line edit, duplicate, insert, move up/down, teleport-to, delete), Undo stack, Map Validation, and Atomic Save + Hot-Reload.
- **FR-009**: Accounts store MUST persist `last_seen_epoch`, `created_at_epoch`, `current_map`, and `last_ip` backward-compatibly with `ACCOUNTS_V1`, updating `last_seen_epoch` on login, heartbeat/save, and disconnect.
- **FR-010**: Staff Panel MUST provide categorized navigation (`Account Directory`, `Server Lifecycle`, `Multi-Map & World`, `Entities & Sandbox`, `Teleport & Waypoints`, `Logs, Reports & Telemetry`, `Guides`) gated by rank (`Mod`, `Admin`, `Developer`), displaying `Online (<Map>, <Zone>)` for live players and `Last seen: ...` for offline accounts in Account Directory, with direct target action submenus (including item/map/duration pickers).
- **FR-011**: Server Lifecycle controls (Developer-only) MUST support configurable-countdown `Shutdown Server` and `Restart Server`, cancelling pending shutdown/restart, maintenance lock, guest toggle, live MOTD/Changelog editing, atomic saves before exit, and clean port release + process relaunch on restart.
- **FR-012**: System MUST add verified CC0/open-license `.ogg` recordings via `tools/asset_pipeline.py` for all new features and provide comprehensive `docs/BUILDER_GUIDE.md` and `docs/STAFF_GUIDE.md` guides.

### Key Entities

- **MapInstance**: Server runtime container for a single loaded world (`id/slug`, `WorldMap`, `ResourceNode[]`, `WildlifeMob[]`, `LootDrop[]`, `ArrowProjectile[]`, dirty/undo stack).
- **MapPlatform / BoxVolume**: 3D box entity `(label, min_x, max_x, min_y, max_y, min_z, max_z, surface, kind[floor|stairs|ramp], roof_flag, ramp_axis, ramp_dir)` unifying ground plates, elevated platforms, roofs, and climbable staircases.
- **MapPortal / MapHazard**: 3D trigger volumes connecting maps (`target_map, dest_x, dest_y, dest_z, dest_facing, auto_step`) or dealing periodic environmental damage.
- **TrackableTarget**: Client-side resolved radar item `(stable_id, category, label, x, y, z, dist, map_name)` scanned within 30 tiles.
- **AccountRecord (v2)**: Extended persistent account record adding `last_seen_epoch`, `created_at_epoch`, `last_ip`, `current_map` while preserving `ACCOUNTS_V1` compatibility.
- **StaffReport**: Player-submitted incident report (`id, reporter, target, map, x, y, z, message, created_epoch, status`) managed in the Staff Panel.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Tracker category filtering strictly returns 0 targets beyond `30.0` tiles and updates live coordinates at 15 Hz snapshot cadence when actively tracking moving targets with `Backspace` and `O`.
- **SC-002**: Players climb a `z=0..20` staircase via `PageUp`/`PageDown` while hearing surface-matching footsteps (`wood`/`stone`), fall through unsupported Air with audible wind and accurate height-scaled damage, and survive zero accidental buffer switches on `PageUp`/`PageDown`.
- **SC-003**: Server hosts >= 2 concurrent `.map` worlds with complete entity/snapshot isolation and transitions players between maps via Portals or Staff Teleport in under 1 second.
- **SC-004**: Authorized Builders create a brand new map, add boxed terrain/walls/stairs, and add/edit/duplicate/reorder/delete entries via Line Manager purely through `F8` audio menus/forms without manual file editing.
- **SC-005**: Developers view all accounts with accurate `Online` vs `Last seen` status, execute target moderation/item-give/map-transfer actions via menus, and execute clean `Shutdown` and `Restart` cycles with zero lost account/world data.
- **SC-006**: All `tools/*.nvgt` console checks (including new tracking, verticality/air/fall, multi-map, builder line manager, and staff/account tests) exit with code `0`, `client/sounds/manifest.txt` passes 100% magic-byte/hash validation, and both `server/server.exe` and `client/client.exe` compile cleanly via `nvgt -c`.

## Assumptions

- Default in-game language remains English across all new features, while developer communication and documentation summaries remain clear for screen-reader users.
- Existing `wildlands_valley.map` will be updated with a base ground floor box covering `0..120 x 0..120` at `z: 0..0` (with deliberate elevated platforms/stairs and cliff gaps) so legacy coordinates remain safely grounded while supporting true Air physics elsewhere.
- `server/server.exe` restart spawns a new server instance with `--bind-delay-ms` and exits cleanly after saving all data and destroying its ENet socket.
