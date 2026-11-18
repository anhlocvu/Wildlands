# Architecture — Wildlands Online v2

## 1. Two-Program Model
Wildlands Online cleanly separates **Server (`server/`)** and **Client (`client/`)** while sharing `common/`:
- **`server/` (`server/server.nvgt` -> `server/server.exe`)**: Dedicated authoritative server loading all `maps/*.map`, persistent `data/accounts.dat` (`ACCOUNTS_V2`), `data/world_objects.dat`, `data/reports.dat`, `data/motd.txt`, `data/changelog.txt`, and `data/devs.txt`.
- **`client/` (`client/client.nvgt` -> `client/client.exe`)**: Pure player client with Steam Audio HRTF `sound_pool`, 7-layer mixer, low-pass occlusion + overhead rain muffling, STW 6-category tracker (`<= 30` tile list scan), 6-channel navigable message buffers, `F8` STW Builder Hub, and `F9` Staff Panel.

## 2. Authority & World Simulation
- **Multi-Map Simulation (`30 Hz` Tick, `15 Hz` Snapshots)**:
  - Each `server/maps/*.map` file runs as an independent `MapInstance` with its own resources, wildlife, bots, ground drops, portal links, and per-map undo history.
  - Snapshots (`CH_SNAPSHOT`), local chat, and 3D `SFX` filter strictly by `MapInstance.slug` and `EARSHOT_RADIUS = 35.0`.
- **3D Verticality & Air / Void Law**:
  - `WorldMap::find_support_at()` distinguishes supported slabs/ramps/stairs from empty air (`[-50 .. +100]` Z range).
  - Gravity accelerates unsupported players (`FALL_GRAVITY = 22.0`), triggering falling air audio (`steps/fall_air.ogg`), distance-scaled impact damage, curable Bone Fracture on severe falls (`>= 8.0` units), deep-water fall cushioning, or Void Death below `min_z - 6.0`.
  - Staircases climb via `PageUp`/`PageDown` (`ACT|climb` + held mask) and emit footsteps matching the staircase's builder-selected surface (`grass`, `dirt`, `stone`, `wood`, `sand`, `water`, `carpet`).

## 3. ENet Channel Separation (`MAX_CHANNELS = 6`)
- `CH_SPEECH (0)` Reliable: Urgent HUD/combat/staff speech
- `CH_AUDIO (1)` Reliable: 3D spatial sound cues
- `CH_CONTROL (2)` Reliable: Auth, chunked multi-map transfers, inventory/building/chests, `BUILDMAP`/`BM_*`, `STAFF`/`ST_*`, `REPORT`
- `CH_CHAT (3)` Reliable: Global, Local, Team, PM, Emote, and Staff (`/sc`) chat
- `CH_SNAPSHOT (4)` Unreliable: Earshot-scoped entities + `fractured` vitals
- `CH_INPUT (5)` Unreliable: Client input mask (`IN_FWD..IN_CLIMB_DOWN`) + facing

## 4. Lifecycle, Restart & Persistence Guarantees
- Atomic file writes (`.tmp` -> `.bak` -> target) for accounts, world objects, player reports, and `.map` saves.
- Fatal refusal on corrupt primary databases (never silently wipes data).
- Graceful Shutdown / Restart countdown: broadcasts timed warnings, flushes all stores, closes ENet socket cleanly (`--bind-delay-ms` on restart relaunch), and invokes `run()` when restarting.
