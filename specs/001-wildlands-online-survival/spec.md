# Feature Specification: Wildlands Online — Multiplayer Survival Audio Game

**Feature Branch**: `001-wildlands-online-survival`
**Created**: 2026-11-18
**Status**: Draft
**Input**: User description: "STW-like multiplayer online survival audio game with survival builder, interactive map builder, multi-channel chat, accounts, buffers, spatial 3D audio, wildlife combat, and professional online features"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Account Onboarding, Connection & Spatial World Navigation (Priority: P1)

A player launches the client, signs up once or reconnects seamlessly using remembered credentials for the selected server, reads the server's latest message of the day and changelog, and enters a persistent 3D wilderness world navigated purely through spatial audio and spoken feedback. They turn by compass heading (default 45-degree or 90-degree snaps, or smooth turning when holding a modifier), walk across distinct terrain surfaces (grass, dirt, stone, wood, sand, shallow water), hear walls and environmental landmarks in 3D space, check status hotkeys mid-action (coordinates, zone, compass heading, health/vitals, repeat last line, context help), and recover gracefully with one-keypress reconnect if disconnected.

**Why this priority**: Without reliable accounts, server-authoritative movement, spatialized hearing, accessible menus, and reconnect recovery, no multiplayer audio survival experience is playable.

**Independent Test**: Start a dedicated server and two clients; register a new account on Client A, close and relaunch Client A to verify automatic sign-in without retyping the password, walk across two named zones with distinct surface footsteps, collide with a wall, turn toward a humming landmark, read status hotkeys, drop and restore connection.

**Acceptance Scenarios**:

1. **Given** a new player opens the client, **When** they open the Registration form and submit a valid unique name (3–20 alphanumeric, underscore, or hyphen characters) and matching password, **Then** the server creates the account, issues a session credential saved per server on the client, announces account creation, and connects them into the world without echoing password characters aloud by default.
2. **Given** a returning player launches the client, **When** they select Connect to Server, **Then** the client signs in automatically using the saved server-scoped token without prompting for a password unless they explicitly signed out or the token expired.
3. **Given** a player is walking in the world, **When** they move across named zones and step onto different surfaces while turning left/right, **Then** they hear surface-accurate footsteps, immediate local step feedback, zone-entry announcements, 3D landmark sounds that rotate around the listener as they turn, and tactile wall-bump audio on obstacles.
4. **Given** a player's connection drops unexpectedly, **When** the transport disconnects or times out, **Then** the client announces the specific failure or disconnect reason, retains the player's body safely for a short grace window, and offers one-keypress reconnection using the saved token.

---

### User Story 2 - Multi-Channel Chat, Message Buffers & Social Online Systems (Priority: P2)

Players communicate across global, area/local, team/party, emote, and private whisper channels without losing urgent gameplay alerts. Every spoken message lands in a categorized message buffer (`All`, `Chat`, `Messages`, `Social`, `Game`, `System`) that players can browse, mute per channel, jump to top/bottom, and copy to clipboard. Players can check who is online (total count first, then names, zones, ranks, and friend indicators), measure connection ping in milliseconds with a plain-language verdict, manage friends (online/offline alerts), mute or block disruptive players, and inspect player profiles and leaderboards.

**Why this priority**: In a screenless multiplayer game, destructive single-voice speech causes players to miss messages unless buffered, and online survival games rely heavily on chat, whispers, ping checks, and social moderation.

**Independent Test**: Connect two players; exchange area chat, global chat, and private messages via `/`; verify messages echo back from the server, appear in the correct buffer channels and merged `All` view, survive channel muting, support blocking (blocking stops chat/PM/duel invites), and verify `Who` and `Ping` readouts work mid-game without opening a menu.

**Acceptance Scenarios**:

1. **Given** a player presses `/` in-game, **When** chat mode opens, **Then** movement keys are captured, a modal sound and "chat" prompt play, typing gives subtle non-speech click feedback, Escape cancels without sending, and Enter sends the message to the server which broadcasts it back with clear scope phrasing ("Player says", "Player tells you", "Player globally").
2. **Given** multiple chat messages, combat alerts, and friend notifications arrive while a player is busy, **When** the player navigates buffers using buffer channel and history keys, **Then** they can switch between `All` (with channel prefixes) and individual channels, read past lines, mute noisy channels without losing history, and copy any focused line to the clipboard.
3. **Given** a player blocks another user from the online player list or via command, **When** the blocked user sends area chat, global chat, private messages, or duel requests, **Then** the blocking player does not hear or receive them.
4. **Given** a player presses the `Who` or `Ping` hotkey mid-game, **When** the response arrives, **Then** the client speaks the online player count before listing names/zones/ranks, or reports round-trip latency in milliseconds with a clear quality label ("Good", "Fair", "Poor").

---

### User Story 3 - Survival Loop: Gathering, Vitals, Crafting & Wildlife Combat (Priority: P3)

Players survive in a living wilderness by managing five server-tracked vitals: Health, Hunger, Thirst, Stamina, and Warmth. Players gather raw resources from interactive world nodes (chopping trees for wood, mining rock outcrops for stone and iron ore, foraging berry bushes and herbs, scooping water from rivers/ponds), craft survival gear and consumables at campfires or crafting benches (axes, pickaxes, bows, arrows, spears, bandages, cooked meat, torches), light campfires for warmth and cooking, and hunt passive wildlife (rabbits, deer) or defend against hostile predators (wolves, bears, bandits) that emit 3D vocalizations, stalk, telegraph attacks, and drop loot. Consensual duels and marked PvP wilderness zones enable player-vs-player combat with melee swings, blocks, and ranged arrows.

**Why this priority**: Survival progression, resource loops, and dynamic 3D combat are the core gameplay heartbeat that gives the STW-inspired world depth and replayability.

**Independent Test**: A player gathers berries, wood, stone, and water; crafts a campfire and stone axe; cooks raw meat; tracks a 3D wolf growl by ear, dodges/blocks its telegraphed strike, defeats it with melee or bow, collects loot, and uses a bandage to restore health.

**Acceptance Scenarios**:

1. **Given** a player stands near a tree, rock, berry bush, or water source, **When** they press the interact/gather key, **Then** the server verifies proximity, tool requirement, and cooldown, plays spatial gathering audio to nearby players, grants resources into inventory, and depletes/schedules node respawn.
2. **Given** a player's hunger, thirst, or warmth drops below safe thresholds, **When** survival ticks advance, **Then** the client plays subtle self-state cues (heartbeat, shivering, stomach rumble) and warns through speech before health begins draining, and eating/drinking/standing near a lit campfire restores the corresponding vital.
3. **Given** a hostile predator or rival player is within earshot, **When** they move, vocalize, draw a bow, or wind up an attack, **Then** the client plays spatialized 3D threat and actor audio (with behind-only front/back differentiation and real Z elevation) and resolves hits, blocks, misses, and kills authoritatively on the server.
4. **Given** a player's health reaches zero, **When** death occurs, **Then** the server announces who/what killed them, drops a temporary lootable corpse container or applies configured respawn rules, plays the death cue, and respawns the player at a safe settlement spawn after a short countdown.

---

### User Story 4 - Dual Builder System: Player Base Building & Interactive Audio Map Builder (Priority: P4)

The game supports both **in-world survival base building** and an **interactive audio map builder**:
1. **Survival Base Building**: Players craft and place persistent structures onto the map (Wooden Walls, Lockable Doors/Gates, Wooden Floors/Platforms with Z-elevation, Stairs/Ramps, Campfires, Storage Chests, Craft Benches, Waypoint Beacons). Walls block movement and acoustically muffle (occlude) sounds passing through them; doors can be opened, closed, and locked/unlocked by owners/friends; storage chests hold shared or private items; structures persist across server restarts and can be repaired or broken down.
2. **Interactive Audio Map Builder**: Authorized builders/admins can enter a dedicated Map Builder mode (either in-game or via builder cursor) to navigate any coordinate on a grid/3D cursor, hear tile surface and elevation cues immediately, define named zones, paint surface regions, draw rectilinear walls/water/platforms, place resource spawners, landmarks, ambient sound emitters, and spawn points, validate map integrity (bounds, spawns, sound manifest coverage), save `.map` files, and live-reload maps on the server.

**Why this priority**: The user explicitly requested a builder and map system; providing both player-driven survival construction and a complete accessible map-authoring workflow makes the world expandable and endlessly replayable.

**Independent Test**: (a) Survival Builder: Player crafts walls, a door, and a storage chest, places an enclosed cabin, locks/opens the door, verifies a sound outside the wall plays muffled compared to when the door opens, and restarts the server to confirm persistence. (b) Map Builder: Authorized builder creates a new zone, paints grass/stone tiles, places a wall and an ambient campfire emitter, validates the map, saves `.map`, and reloads it on the server so players can immediately walk in it.

**Acceptance Scenarios**:

1. **Given** a player has building materials in inventory and faces an unobstructed build slot, **When** they select a structure (e.g., wall, door, chest, platform, campfire) and confirm placement, **Then** the server validates ownership/overlap/bounds, deducts materials, spawns the persistent structure, and broadcasts spatial construction audio.
2. **Given** a wall or closed door lies between a sound source and the listener, **When** the sound plays, **Then** the client applies acoustic occlusion (attenuation and high-frequency muffling) until the door opens or the player moves around the wall.
3. **Given** an authorized builder enters Map Builder mode, **When** they move the builder cursor across coordinates and inspect/edit tiles, zones, walls, water, resource nodes, ambient emitters, or spawns, **Then** every cursor move speaks coordinates, elevation, zone, and surface type with an audible terrain cue, and saving exports a valid `.map` data file loadable by the server without code edits.

---

### User Story 5 - Professional Online Operations: Settings, Key Remapping, Tutorial, Dev Panel & Moderation (Priority: P5)

The client and server provide the complete polish expected of top online audio games: instant-persisting Settings (7-layer volume sliders with live audio preview, screen reader vs built-in TTS fallback and speech rate, turn snap angle 45/90, key remapping with conflict checks and reset, developer localhost toggle), a skippable/replayable interactive tutorial that verifies each physical action (turn, walk, follow wall, gather, craft, build, chat), a windowed server console with structured rotating logs and command-line flags (`--port`, `--test-mode`, `--allow-guests`, `--map`), an in-game Developer Panel for target-based world control (set wildlife/bot counts, weather/time of day, reload maps/MOTD, server-wide announcements, debug coordinates), and a hierarchical Moderation suite (Kick, Timed Mute, Reasoned Timed Ban, Unban) strictly preventing sideways or upward moderation.

**Why this priority**: These operational, accessibility, and administrative systems turn a prototype into a maintainable, player-ready live online service.

**Independent Test**: Adjust a layer volume slider and restart client to verify instant persistence; complete or skip the interactive tutorial; log in as a preconfigured developer account, open the Dev Panel to set bot/wildlife count to 4 and broadcast an announcement; log in as a Moderator and verify they can mute/kick a regular player (with spoken reason) but are rejected when attempting to ban another Moderator or Admin.

**Acceptance Scenarios**:

1. **Given** a player adjusts any mix layer slider (Speech, Self, Threat, Actors, World, Ambience, Music) or remaps a key in Settings, **When** the value changes, **Then** a live sample sound plays at the new level and the setting persists immediately to the per-user application data folder.
2. **Given** a player starts the Interactive Tutorial, **When** they complete each guided task (turn north, step forward, locate wall, gather wood, craft campfire, send a message, browse buffers), **Then** each step detects real completion before advancing, and the player may skip or replay at any time.
3. **Given** a developer account connects, **When** they invoke a Developer Panel command (e.g., set wildlife count = 6, reload maps, change weather), **Then** the server verifies both server-owned developer authorization and rank, applies the idempotent target state, announces world changes to affected players, and logs the action.
4. **Given** a moderator attempts to kick, mute, or ban another user, **When** the target's rank is equal to or higher than the actor's rank, **Then** the server refuses and logs the attempt; if valid, the server disconnects/mutes the target with a spoken reason and duration that is also announced if a banned user tries to reconnect.

---

### User Story 6 - High-Fidelity Verified Spatial Audio Pipeline (Priority: P6)

Every UI cue, footstep surface, gathering action, building interaction, weapon/combat telegraph, wildlife call, zone ambience, weather loop, and multiplayer event uses genuine recorded audio assets (no synthetic beeps), normalized to a consistent loudness profile across the seven priority mix layers, deduplicated and verified for authentic audio container headers, and checked against a manifest at startup so missing files surface immediately rather than causing silent gameplay.

**Why this priority**: Audio *is* the display; high-craft, distinct, properly leveled sound design determines whether players can react accurately in combat and enjoy long survival sessions.

**Independent Test**: Run the offline asset/manifest verification check to confirm every sound referenced by maps, items, structures, wildlife, UI, and protocol events exists on disk as a valid, non-empty, header-verified audio file with zero duplicates and normalized peak/LUFS levels.

**Acceptance Scenarios**:

1. **Given** the game ships its complete `sounds/` catalog and manifest, **When** the client starts or the asset check runs, **Then** every required sound path is verified present and valid, and any missing asset produces a clear named startup error instead of silent gameplay.
2. **Given** overlapping combat threats, footsteps, ambience, and speech occur simultaneously, **When** speech or threat sounds trigger, **Then** lower-priority layers (ambience/music) duck cleanly so urgent audio cues remain intelligible.

---

### Edge Cases

- What happens when a player registers or sends chat containing delimiter characters (`|`), backslashes (`\`), newlines, or control characters? Names must reject invalid characters upfront with clear rules spoken before input; free text must escape/unescape losslessly on the wire without shifting fields or breaking storage records.
- What happens when a player creates an account named `Hero` and another tries `hero`? Case-insensitive uniqueness rejects duplicates so players cannot impersonate one another by ear.
- What happens if a player uses a saved credential token from `localhost` against the public server (or vice versa)? The credential wallet scopes tokens strictly by `host:port`, never sending one server's token to another.
- What happens when a client connects with an older or newer protocol version? The handshake immediately refuses connection with a clear spoken explanation telling the user which side is out of date.
- What happens when the server's account store exists on disk but is corrupted or unreadable? The server fails fatally at startup with an alert modal and log message rather than starting empty and overwriting accounts.
- What happens if two players chop the same tree or place a structure on the exact same tile simultaneously? Server-side atomic tick resolution awards the first valid action and gives the second player an immediate refusal cue without duplicating items or overlapping walls.
- What happens if a client leaves earshot of another player or enters an enclosed cabin? Out-of-earshot players are excluded from snapshots (preventing modified clients from snooping distant positions), and sounds inside/outside closed walls apply acoustic muffling.
- What happens if a client loses focus, connects without a running screen reader, or disconnects mid-combat? Built-in TTS takes over seamlessly when no screen reader is active, and a disconnected combatant enters a short safe-despawn/grace state rather than remaining an AFK pinata or vanishing instantaneously during transient 5-second packet drops.

## Requirements *(mandatory)*

### Functional Requirements

#### Networking, Accounts & Persistence
- **FR-001**: System MUST operate as a dedicated authoritative server and separate client sharing common protocol, math, map schema, and recipe definitions; single-player MUST connect to a local dedicated server.
- **FR-002**: System MUST separate network traffic across six distinct channels: Speech (reliable), Audio Events (reliable), Control/State (reliable), Chat/Social (reliable), Snapshots (unreliable), and Client Input (unreliable).
- **FR-003**: System MUST validate protocol version compatibility during handshake and speak a specific reason when connection fails or closes (DNS/unresolved, timeout, server full, version mismatch, invalid token, banned with reason and remaining duration).
- **FR-004**: System MUST require accounts by default (guest play disabled unless explicitly enabled by server operator flag), validate usernames (`3–20` chars `[A-Za-z0-9_-]`) case-insensitively, store salted stretched password hashes and hashed cryptographic session tokens server-side, rate-limit authentication attempts per IP, and persist account/world files atomically with backup copies.
- **FR-005**: Client MUST persist profile settings, key bindings, and a multi-server credential wallet (scoped by `host:port`, max 8 entries, never storing plaintext passwords) in the per-user application data directory, saving changes immediately.

#### Accessibility, UI, Chat & Buffers
- **FR-006**: Client MUST output speech through the player's active screen reader by default with built-in TTS fallback selectable in Settings, support explicit interrupt flags, and bind a single key to repeat the last spoken line.
- **FR-007**: Client MUST provide arrow-key accessible menus with wrap/move/select/back/error sounds, first-letter navigation, Home/End jumps, item position readouts, remembered cursor positions, and live value readouts, plus multi-field forms (Registration, Sign-In, Server Entry) that mask passwords by default (keypress clicks, toggle echo, read length, Ctrl+V paste).
- **FR-008**: Client MUST provide a 6-channel navigable message buffer system (`All`, `Chat`, `Messages`, `Social`, `Game`, `System`) with channel switching, history browsing, Home/End, per-channel mute (still collects), clipboard copy, and clear, where `All` prefixes each line with its source channel.
- **FR-009**: Client MUST provide modal text chat opened with `/`, supporting Global, Local/Area, Team/Party, Emote, and Private Whispers (`/pm`, `/r`), server-side rate limiting, length limits, text escaping, and server echo confirmation.
- **FR-010**: Client MUST provide mid-game status hotkeys (Health/Vitals, Zone & Coordinates, Compass Facing, Target/Landmark Scanner with relative directions and steps, Who is Online count-first, Ping in ms with quality verdict, Context Help) and social controls (Friends list with online alerts, Mute, Block, Player Profile, Leaderboard).

#### World, Survival, Combat & Builders
- **FR-011**: System MUST simulate a 3D coordinate world (`X` East, `Y` North, `Z` Elevation) loaded from external `.map` data files containing named zones, terrain surfaces, rectilinear walls/obstacles, water bodies, elevated platforms/stairs, resource nodes, ambient landmarks, and spawn points.
- **FR-012**: Client MUST spatialize world audio using floating-point coordinates around an immediately updated listener, applying real Z elevation, behind-only subtle pitch cues (~3%), wall occlusion muffling, distance attenuation culling, and a 7-layer priority mix (`Speech > Self > Threat > Actors > World > Ambience > Music`).
- **FR-013**: Server MUST simulate survival vitals (Health, Hunger, Thirst, Stamina, Warmth), gathering with tool tiers and node respawns, crafting recipes, campfire cooking/warmth, inventory & quick-belt slots, and day/night/weather cycles.
- **FR-014**: Server MUST simulate passive and hostile wildlife AI (roaming, fleeing, stalking, 3D vocal cues, telegraphed melee/lunge attacks, loot drops) alongside consensual duels and PvP zones with server-authoritative melee swings, blocks, and ranged projectile physics.
- **FR-015**: System MUST provide an in-world Survival Builder allowing players to craft, place, inspect, repair, demolish, lock/unlock (doors/chests), and interact with persistent world structures (walls, doors/gates, floors/platforms, stairs, chests, campfires, craft benches, beacons).
- **FR-016**: System MUST provide an Interactive Audio Map Builder allowing authorized builders/admins to navigate coordinates with spoken & spatialized cursor feedback, edit zones, surfaces, walls, elevation, water, resource spawners, ambient emitters, and spawns, validate integrity, export `.map` files, and live-reload maps on the server.

#### Operations, Moderation, Updates & Audio Assets
- **FR-017**: Server MUST display a readable log window with timestamped events (connections, refusals, dev actions, moderation, periodic health summary), rotate file logs, alert modally on fatal startup errors (bad map, packet limit overflow, unreadable account store), and accept runtime CLI flags (`--port`, `--map`, `--bots`, `--test-mode`, `--allow-guests`, `--headless`).
- **FR-018**: System MUST provide an in-game Developer Panel (restricted strictly to server-authorized developer accounts) for idempotent target-based world changes (bot/wildlife counts, weather/time, map reload, world broadcast, debug readout) and a hierarchical Moderation system (Kick, Timed Mute, Reasoned Timed Ban, Unban) enforcing no sideways or upward moderation.
- **FR-019**: Client MUST support dynamic server-sent MOTD/Changelog news, version/update notification check, instant-saving Settings (7-layer mix sliders with sample playback, speech options, turn snap size 45/90, key remapping with conflict checks, dev localhost switch), and a skippable/replayable Interactive Tutorial verifying player actions.
- **FR-020**: System MUST ship with real, verified, loudness-normalized audio recordings (zero synthetic placeholders) covering UI, footsteps per surface, survival actions, builder/doors, combat, wildlife, ambience/weather, and multiplayer notifications, verified at startup against a sound manifest.

### Key Entities

- **Account**: Persistent registered player identity with canonical name, case-insensitive lookup key, salted stretched password hash, hashed session token, rank (`Player`, `Builder`, `Moderator`, `Admin`, `Developer`), friend list, block list, ban/mute metadata, and server-side lifetime stats (playtime, kills, deaths, structures built, resources gathered).
- **WorldMap & Zone**: External map definition containing grid/3D bounds, named rectangular zones, surface polygons/regions, rectilinear wall/obstacle segments, water regions, Z-platforms/ramps, spawn points, resource spawners, and persistent ambient sound emitters.
- **PlayerSession**: Live connected entity linking peer transport ID, authenticated account, 3D position/velocity/facing, vitals, inventory slots, equipped belt item, active buffs/warmth, duel/party state, and last-heard timestamp/grace window.
- **BuildableStructure**: Persistent player-placed object on the map with unique ID, type (wall, door, chest, campfire, bench, platform, stairs, beacon), owner account, lock state, coordinates/bounds, elevation, hitpoints, and optional chest inventory or fuel timer.
- **ResourceNode & LootDrop**: World-placed harvestable node (tree, boulder, iron vein, berry bush, herb patch) with remaining charges and respawn timer, or temporary dropped item bundle with spatial audio beacon and expiry.
- **WildlifeEntity**: Server-driven non-player creature (rabbit, deer, wolf, bear, bandit) or test bot with AI state (`idle`, `roam`, `flee`, `stalk`, `windup`, `attack`), 3D position/facing, health, aggro target, and loot table.
- **MessageBuffer & ChatChannel**: Client-side ring-buffered history stores across six channels (`All`, `Chat`, `Messages`, `Social`, `Game`, `System`) plus server-side chat/PM routing and mute/block filters.
- **ClientProfile**: Per-user local settings stored in application data containing per-layer mix gains, speech mode/rate/voice, compass snap degree, custom key bindings, and per-server credential wallet entries.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A blind player relying solely on audio and a screen reader (or built-in TTS) can register an account, complete the interactive tutorial, gather wood/food/water, light a campfire, and place a wall + door in under 10 minutes without external visual guidance.
- **SC-002**: Returning players reconnect to a previously authenticated server in 1 keypress (under 2 seconds on LAN/localhost) without retyping credentials.
- **SC-003**: Dedicated server sustains a fixed 30 Hz simulation tick and 15 Hz scoped snapshot rate with at least 15 simultaneous players and 20 active wildlife/bot entities while keeping worst-case tick execution under 15 milliseconds and every UDP packet under 1,400 bytes.
- **SC-004**: Urgent speech alerts and spatial threat cues arrive and trigger audibly without waiting behind bursts of 20+ rapid chat messages.
- **SC-005**: 100% of audio files listed in the sound manifest exist on disk, pass authentic container/header verification, have zero duplicate hashes, and are free of synthetic tone placeholders.
- **SC-006**: Every server-authoritative rule (position clamping, melee/bow range, inventory/crafting costs, build overlap, rank hierarchy, protocol escaping) passes automated non-interactive console verification suites (`PASS` with exit code `0`, zero popped windows, zero stray audio, zero orphaned processes).
- **SC-007**: Maps created or modified in the Interactive Audio Map Builder export cleanly, pass validation checks, and reload onto a running server without restarting or recompiling executables.

## Assumptions

- **In-Game Speech Language**: Default in-game speech, commands (`/pm`, `/who`), and compass terminology (`north`, `ahead and to your left, 12 steps`) will use clear **English** to match standard NVGT `rotation.nvgt`, international STW player conventions, and screen-reader/SAPI pronunciation reliability, while user documentation and communication with the developer remain in Vietnamese (with a centralized string table so Vietnamese localization can be added cleanly if desired).
- **Primary Target Platform**: Windows x64 (`nvgt.exe` / `nvgtw.exe`, NVGT 0.90.0-dev), matching the installed toolchain and Windows screen reader ecosystem (NVDA/JAWS/Narrator via `screen_reader_speak()` + SAPI fallback).
- **Networking Scope**: Single dedicated server process designed for 1–50 concurrent players per shard (tuned for 10–30 typical audio-game sessions) using direct UDP/ENet connections (`localhost` default switch for testing, single configurable public host/port constant for live hosting).
- **Audio Sourcing**: Real CC0 / open-licensed recordings will be retrieved from verified public repositories (OpenGameArt, Freesound CC0, Wikimedia Commons, Kenney CC0, PolyHaven/Soniss CC0), inspected byte-wise, normalized with `ffmpeg`, and documented with full attribution/licenses in `sounds/CREDITS.md`.
