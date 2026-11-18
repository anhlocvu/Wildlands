# Architecture — Wildlands Online

## 1. Two-Program Model
Wildlands Online consists of two cleanly separated directories (`server/` and `client/`) sharing one `common/` include directory at compile time:
- **`server/` (`server/server.nvgt` -> `server/server.exe`)**: Self-contained dedicated server directory (`maps/`, `data/`, `logs/`). Runs in a readable GUI window by default (`show_window()`) with live event log, timestamped file rotation, and modal `alert()` on fatal startup errors (`--headless` supported as an optional flag for service hosting).
- **`client/` (`client/client.nvgt` -> `client/client.exe`)**: Self-contained player client directory (`includes/`, `sounds/`). Never hosts a game directly; single-player testing launches `server` and connects via `localhost`.

## 2. Authority Table

| State | Owner | Rationale |
|---|---|---|
| Player `(x, y, z)`, velocity, facing | **Server** | Prevents teleportation and speed hacks |
| Health, hunger, thirst, stamina, warmth | **Server** | Prevents godmode and client desync |
| Inventory, tool durability, recipes, chest contents | **Server** | Prevents item duplication |
| Resource node charges & respawn timers | **Server** | Atomic multi-player harvesting |
| Placed structures, locks, door open/close, HP | **Server** | Single source of world collision/occlusion |
| Wildlife AI, aggro, attack windups, damage, death | **Server** | Fair hit resolution for all clients |
| Accounts, ranks, mutes, bans, friends | **Server** | Secure persistence & moderation enforcement |
| Which keys are down & local turn snap input | **Client** | Only client knows raw keyboard state |
| Listener orientation, 7-layer mix, occlusion DSP | **Client** | Immediate audio responsiveness |
| Menus, forms, 6-channel message buffers, local INI/wallet | **Client** | Personal UX & accessibility preferences |

## 3. Server Tick & Snapshot Loop
- **Simulation Tick (`TICK_HZ = 30`, ~33.33 ms budget)**:
  1. Drain all ENet events (`connect`, `disconnect`, `timeout`, `receive`); store latest `INPUT` per player.
  2. Consume inputs (or repeat last valid key mask if unreliable input packet dropped; step bots/wildlife inputs identically).
  3. Step physics, movement speeds by surface, Z-ramps/platforms, wall/door collision, vitals, campfires, cooldowns, combat hitboxes, and AI state machines.
  4. Broadcast immediate reliable one-shot events (`SFX` on `CH_AUDIO`, `SPEAK` on `CH_SPEECH`, `MAP_OBJ` on `CH_CONTROL`).
  5. Every 2nd tick (`SNAPSHOT_HZ = 15`), send earshot-scoped `SNAP` packets on `CH_SNAPSHOT`.
  6. Sleep remaining frame time (`max(5, budget - elapsed)` ms) so CPU yields cleanly.

## 4. Client Interpolation & Immediate Local Feel
- Client retains the last two `SNAP` frames (~66 ms interpolation buffer) and smoothly interpolates remote players/wildlife positions so attached 3D sounds glide without stepping at 15 Hz.
- Discrete states (HP, block stance, door open/closed, equipment) snap immediately on event arrival.
- Local player key presses trigger immediate local UI/turning speech feedback while authoritative position updates flow cleanly at 15–30 Hz.

## 5. ENet Channel Separation (`MAX_CHANNELS = 6`)

| Channel | Constant | Mode | Traffic |
|---|---|---|---|
| `0` | `CH_SPEECH` | Reliable | Urgent spoken combat/system/moderation lines |
| `1` | `CH_AUDIO` | Reliable | 3D sound event triggers |
| `2` | `CH_CONTROL` | Reliable | Handshake, Auth, Map chunks, Inventory, Build, Who, Ping, News, Dev/Mod |
| `3` | `CH_CHAT` | Reliable | Global/Local/Team/PM/Emote chat messages |
| `4` | `CH_SNAPSHOT` | Unreliable | Earshot-scoped entity positions & vitals (`<= 35` tiles) |
| `5` | `CH_INPUT` | Unreliable | Client input bitmask + facing |

**Why**: Urgent warnings (`CH_SPEECH`) and combat cues (`CH_AUDIO`) are never queued behind rapid chat (`CH_CHAT`) or map transfers (`CH_CONTROL`).

## 6. Earshot Scoping (Anti-ESP) & Packet Bounds
- **Earshot Rule**: Server only serializes players, wildlife, and temporary loot drops within `EARSHOT_RADIUS = 35.0` tiles into a client's `SNAP` packet. Modified clients cannot inspect players across the map.
- **Packet Ceiling**: Every outgoing packet is verified `<= 1350` bytes (`< 1400` MTU practical UDP limit). Large map transfers split into `<= 1200`-byte reliable chunks on `CH_CONTROL`; `SNAP` batches entities if a crowded hub ever approaches `1300` bytes.

## 7. Startup Order & Fatal Conditions
1. Parse CLI arguments (`--port`, `--map`, `--bots`, `--test-mode`, `--allow-guests`, `--headless`; unknown flags warn and continue).
2. Load shared item/recipe tables (`items.nvgt`).
3. Load & validate `.map` file (bounds, spawns, sound manifest refs) — **fatal with `alert()` if invalid**.
4. Verify initial handshake/map chunk sizes fit under `1350` bytes — **fatal with `alert()` if exceeded**.
5. Load `data/accounts.dat` & `data/world_objects.dat` — **fatal with `alert()` if existing file is corrupt/unreadable** (never wipe accounts with an empty fallback).
6. Load soft data (`data/motd.txt`, `data/changelog.txt`, `data/devs.txt`) — warn if missing, continue.
7. Bind ENet server port and log readiness.
