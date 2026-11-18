# Wildlands Online — Design & Milestone Plan

## 1. What the Game Is
**Wildlands Online** is a persistent, multiplayer, 3D spatial-audio survival sandbox inspired by *Survive the Wild (STW)* and engineered specifically for blind and screen-reader players using NVGT `0.90.0-dev`.

Players enter an atmospheric wilderness featuring named zones, distinct footstep surfaces, elevated structures, rushing rivers, wildlife, campfires, player-built shelters, and a living multiplayer community — navigated 100% by ear and accessible speech.

## 2. Core Design Pillars
1. **Complete Screenless Playability**: Screen-reader-first output (`screen_reader_speak()` with SAPI fallback), audio menus, accessible multi-field forms, and a 6-channel navigable message buffer history.
2. **Spatial Audio as the Display**: Floating-point 3D HRTF audio around an immediately-updated listener, real Z elevation, behind-only subtle pitch differentiation, wall/door acoustic occlusion, and real normalized recordings (zero synthetic beeps).
3. **Server Authority**: One dedicated windowed server (`server.exe`) simulates the world at 30 Hz and validates every action, position, recipe, structure, hit, and moderation rule. Single-player runs by connecting to `localhost`.
4. **Dual Builders**:
   - **Survival Builder**: Players gather wood/stone/iron to craft and build persistent cabins, lockable doors, stairs/platforms, chests, campfires, craft benches, and beacons.
   - **Interactive Audio Map Builder**: Authorized builders/admins walk or move a builder cursor across the map by ear to author zones, surfaces, walls, water, resource nodes, ambient beacons, and spawns, saving directly to `.map` files and hot-reloading live.

## 3. Scope for v1

### In Scope
- Account registration/login, salted stretched SHA-256 hashes, `random_bytes(32)` bearer tokens, 8-slot per-server client credential wallet in AppData, one-keypress reconnect, optional `--allow-guests` / `--test-mode` server flags.
- 6-channel ENet wire protocol (`Speech`, `Audio`, `Control`, `Chat`, `Snapshot`, `Input`) with `wire.nvgt` escaping and earshot-scoped snapshots.
- Modal `/` chat (Global, Local, Team, Emote, Private Message, Reply), 6-channel `buffers.nvgt`, `Who`, `Ping`, MOTD/Changelog, Friends, Mute/Block, Profiles, Leaderboard.
- Five survival vitals (`Health`, `Hunger`, `Thirst`, `Stamina`, `Warmth`), resource gathering (`wood`, `stone`, `iron`, `berries`, `herbs`, `water`), crafting, cooking, day/night & weather, passive & hostile 3D wildlife, melee/block/bow combat, duels, safe zones vs wilds.
- Survival Building (walls, lockable doors with sound occlusion, chests, floors, stairs, campfires, craft benches, beacons) + Interactive Audio Map Builder.
- Settings menu (7-layer mix sliders with live sample playback, speech options, 45°/90° snap angle, key remapping, dev localhost switch), Interactive Guided Tutorial, Dev Panel, Ranked Moderation, and complete `tools/` console test suite.

### Out of Scope for v1
- Voice over IP (VoIP) streaming chat (text chat + spatial audio + screen reader remain primary).
- Client-side movement prediction (starts with honest "trust the server" + snapshot interpolation; prediction only added later if latency feedback requires it).
- Cross-server character transfers or SQL database backends (flat atomic `.dat` + `.bak` handles dozens of players cleanly).

## 4. Milestones
- **M1 — Verified Audio & Common Core**: Real normalized `.ogg` asset pack + `sounds/manifest.txt`, shared constants, `wire.nvgt`, `compass.nvgt`, `protocol.nvgt`, `map.nvgt`, `items.nvgt`, starter `wildlands_valley.map`, offline checks passing.
- **M2 — Accounts, World Movement & Spatial Engine**: Server startup/accounts/windowed logger + Client AppData wallet, forms, 7-layer mix, patched `sound_pool`, walking/turning/surfaces/walls/landmarks, reconnect.
- **M3 — Chat, Buffers & Online Social**: Modal `/` chat, 6-channel buffers, Who, Ping, MOTD/Changelog, Friends, Mute/Block, Profiles, Leaderboard.
- **M4 — Survival, Crafting & 3D Combat**: Gathering, vitals, campfires/cooking, recipes, wildlife AI, melee/bow/duel combat, death/respawn.
- **M5 — Survival Builder & Interactive Audio Map Builder**: Persistent player bases, lockable doors with low-pass occlusion, chests, plus full audio Map Builder mode and live server reload.
- **M6 — Polish, Ops & E2E QA**: Settings, key remapper, tutorial, Dev Panel, Moderation, `net_integration_check.nvgt`, final exe builds.
