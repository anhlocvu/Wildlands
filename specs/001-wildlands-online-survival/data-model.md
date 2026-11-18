# Data Model: Wildlands Online

**Feature**: `001-wildlands-online-survival`
**Date**: 2026-11-18

---

## 1. Account (`Server: data/accounts.dat`)

| Field | Type | Constraints / Validation | Notes |
|---|---|---|---|
| `id` | `uint64` | Unique monotonic integer >= 1 | Internal primary key |
| `name` | `string` | `3..20` chars `[A-Za-z0-9_-]`, unique case-insensitive | Displayed canonical casing |
| `name_lower` | `string` | `name.lower()` | Lookup key |
| `salt` | `string` | 32-char hex (`16` random bytes) | Per-account CSPRNG salt |
| `pw_hash` | `string` | 64-char hex SHA-256 stretched `5000` rounds | Never stored plaintext |
| `token_hash` | `string` | 64-char hex SHA-256 of active bearer token, or `""` | Cleared on sign-out, rotated on login |
| `rank` | `uint8` | `0=Player, 1=Builder, 2=Mod, 3=Admin, 4=Developer` | Developer rank requires server `devs.txt` allowlist |
| `banned_until` | `int64` | Unix epoch seconds (`0`=none, `-1`=permanent) | Checked before spawn |
| `ban_reason` | `string` | `<= 160` chars, escaped via `wire_escape` | Spoken on refused connection |
| `muted_until` | `int64` | Unix epoch seconds (`0`=none) | Blocks Global/Local/PM chat |
| `friends` | `string[]` | Lowercase account names (`<= 50` entries) | Bidirectional/accepted friend list |
| `blocked` | `string[]` | Lowercase account names (`<= 50` entries) | Drops chat, PM, duel invites |
| `kills_pvp` | `uint32` | `>= 0` | Lifetime stats |
| `kills_pve` | `uint32` | `>= 0` | Lifetime wildlife hunts |
| `deaths` | `uint32` | `>= 0` | Lifetime deaths |
| `built_count` | `uint32` | `>= 0` | Structures placed |
| `gathered_count` | `uint32` | `>= 0` | Resource harvests |
| `playtime_sec` | `uint64` | `>= 0` | Accumulated online seconds |
| `last_x, last_y, last_z` | `double` | Clamped to active map bounds | Restored spawn position |

---

## 2. Client Profile & Credential Wallet (`Client AppData: player.ini`)

| Field | Type (stored as string) | Default | Constraints |
|---|---|---|---|
| `schema_ver` | `string` | `"1"` | Must match supported migration |
| `server_host` | `string` | `MAIN_SERVER_HOST` | Active target host |
| `server_port` | `string` | `"7100"` | `1..65535` |
| `vol_master` .. `vol_music` | `string` (`0..100`) | Layer defaults (`100,100,85,80,65,60,30,35`) | Converted to `0.0..1.0` linear, then dB at boundary |
| `speech_mode` | `string` | `"sr"` | `"sr"` (screen reader) or `"tts"` |
| `tts_rate` | `string` | `"0"` | `-10..10` |
| `tts_voice` | `string` | `""` | Saved voice name |
| `turn_snap_deg` | `string` | `"45"` | `45` or `90` |
| `tutorial_done` | `string` | `"0"` | `"0"` or `"1"` |
| `wallet_slot_0..7` | `string` | `""` | `host:port|account|token`, LRU ordered, always writes all 8 slots |
| `bind_<action>` | `string` | Action defaults | Key code integers validated on load |

---

## 3. WorldMap & Map Elements (`maps/<name>.map`)

### Map Metadata
- `name`: `string` (`3..40` chars)
- `version`: `uint`
- `width`, `height`: `int` (`40..500`, default starter map `160 x 160`, `Z: 0..20`)
- `default_surface`: `string` (`grass`)
- `spawn`: `(x, y, z, facing)`

### Sub-Entities
- **Zone (`Z`)**: `id, name, min_x, min_y, max_x, max_y, surface, ambience_loop, is_safe_zone(0|1)`
- **Platform / Elevation (`P`)**: `min_x, min_y, max_x, max_y, z_level, surface, is_ramp(0|1), ramp_axis(x|y), ramp_dir(+1|-1)`
- **Wall / Solid Obstacle (`W`)**: `id, min_x, min_y, max_x, max_y, min_z, max_z, material(wood|stone|metal|hedge), destructible(0|1)`
- **Water Body (`L`)**: `min_x, min_y, max_x, max_y, z_level, depth(shallow|deep), sound_loop`
- **Resource Spawner (`R`)**: `id, type(tree|rock|iron_vein|berry_bush|herb_patch), x, y, z, max_charges, respawn_sec`
- **Ambient Emitter (`A`)**: `id, label, sound_file, x, y, z, range, volume`
- **Door / Static Gate (`D`)**: `id, label, x, y, z, axis, is_open`

---

## 4. Live PlayerSession (`Server Memory`)

| Field | Type | Bounds | Notes |
|---|---|---|---|
| `peer_id` | `uint64` | ENet peer ID | `0` during grace window |
| `account_name` | `string` | Validated account | `"Guest_N"` if `--allow-guests` |
| `x, y, z` | `double` | `[0..map.w], [0..map.h], [0..20]` | Server authoritative |
| `vx, vy, vz` | `double` | Derived from move speed + surface | Sent in snapshots |
| `facing` | `int` | `0..359` | Whole degrees clockwise from North |
| `hp` | `int` | `0..100` | Death at `0` |
| `hunger` | `int` | `0..100` | Decays over time |
| `thirst` | `int` | `0..100` | Decays over time |
| `stamina` | `int` | `0..100` | Consumed by sprint/jump/melee, regens |
| `warmth` | `int` | `0..100` | Affected by night/weather vs campfire/torch |
| `inventory` | `ItemStack[]` | Max 24 slots | `{item_id, qty, durability}` |
| `belt_slot` | `int` | `0..8` | Active hotbar slot |
| `builder_mode` | `bool` | `false` default | True only when authorized Builder+ toggles map cursor |
| `duel_target` | `string` | `""` or opponent | Consensual duel outside PvP zones |
| `grace_until_ms` | `uint64` | `0` or `+15000 ms` | Protects body during transient drop |

---

## 5. Buildable Structure (`Server: data/world_objects.dat`)

| Field | Type | Validation | Notes |
|---|---|---|---|
| `id` | `uint64` | Unique monotonic | Referenced in packets |
| `type` | `string` | `wood_wall|wood_door|wood_floor|wood_stairs|campfire|chest|craft_bench|beacon` | Defined in shared `recipes.nvgt` |
| `owner` | `string` | Canonical account name | Controls lock/demolish rights |
| `x, y, z` | `int` | Snapped integer tile coordinates | Checked for overlap |
| `facing` | `int` | `0|90|180|270` | Orientation of door/stairs |
| `hp, max_hp` | `int` | `1..500` | Repairable with wood/stone |
| `locked` | `bool` | Doors & chests | Owner + friends may open locked objects |
| `is_open` | `bool` | Doors only | Controls movement blocking & sound occlusion |
| `fuel_sec` | `int` | Campfire burn timer (`0..600`) | Emits warmth + cooking + 3D crackle |
| `chest_items` | `ItemStack[]` | `<= 12` slots (chests only) | Persisted atomically |

---

## 6. Wildlife & Bot Entity (`Server Memory`)

| Field | Type | Values | Notes |
|---|---|---|---|
| `id` | `uint64` | Unique runtime ID | Sent in scoped snapshots |
| `kind` | `string` | `rabbit|deer|wolf|bear|bandit|bot_survivor` | Determines stats, speed, sound profile |
| `ai_state` | `uint8` | `idle|roam|flee|stalk|windup|attack` | Windup plays 3D telegraph sound before hit |
| `x, y, z, facing` | `double / int` | Map-clamped | Spatialized to nearby clients |
| `hp, max_hp` | `int` | Species-configured | Drops meat/hide/arrows/ore on death |
| `home_x, home_y` | `double` | Spawn anchor | Prevents leash drift |
| `aggro_peer` | `uint64` | Current target | Cleared if target enters safe zone or dies |

---

## 7. Inventory Items & Crafting Recipes (`src/common/items.nvgt`)

- **Raw Materials**: `wood`, `stone`, `iron_ore`, `berries`, `herbs`, `raw_meat`, `hide`, `water_flask_empty`, `water_flask_full`, `feathers`.
- **Crafted Consumables & Tools**: `cooked_meat`, `bandage`, `torch`, `stone_axe`, `stone_pickaxe`, `iron_axe`, `spear`, `wooden_bow`, `arrow`, `wood_wall_kit`, `wood_door_kit`, `wood_floor_kit`, `wood_stairs_kit`, `campfire_kit`, `chest_kit`, `craft_bench_kit`, `beacon_kit`.
- **Shared Definitions**: Both server (authoritative validation) and client (readable craft menu & tooltips) include `src/common/items.nvgt` so costs, tool tiers, and stats never disagree.
