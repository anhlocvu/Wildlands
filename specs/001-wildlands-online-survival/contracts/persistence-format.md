# Persistence Format Contract: Accounts, World Objects, & Client Profile

---

## 1. Server Account Store (`data/accounts.dat` & `data/accounts.dat.bak`)

Line-based pipe-delimited records (`wire_escape()` / `split_keep_empty()`):
```text
ACC|v1|id|name|salt|pw_hash|token_hash|rank|banned_until|ban_reason|muted_until|friends_csv|blocked_csv|kills_pvp|kills_pve|deaths|built|gathered|playtime|last_x|last_y|last_z
```
- **Atomic Write**: Write to `data/accounts.dat.tmp`, flush/close, copy existing `data/accounts.dat` -> `data/accounts.dat.bak`, move `.tmp` -> `data/accounts.dat`.
- **Corrupt File Behavior**: If `data/accounts.dat` exists and fails header/parse validation, log error, show modal `alert()`, and terminate startup cleanly (never fall back to empty list).

---

## 2. Server Persistent Structures (`data/world_objects.dat` & `.bak`)

```text
OBJ|v1|id|map_name|type|owner|x|y|z|facing|hp|max_hp|locked|is_open|fuel_sec|chest_items_encoded
```
- `chest_items_encoded`: semicolon-separated `item_id:qty` pairs (e.g., `wood:10;cooked_meat:2` or `-` if empty).

---

## 3. Server Configuration & Text Lists

- `data/devs.txt`: One canonical lowercase username per line for authorized Developer accounts. (Must NEVER be modifiable at runtime over the network).
- `data/motd.txt`: First line is active MOTD; `data/changelog.txt` contains latest release bullet lines sent by `NEWS`.

---

## 4. Client Profile & Credential Wallet (`DIRECTORY_PREFERENCES("WildlandsStudio", "WildlandsOnline") + "player.ini"`)

All numeric settings stored explicitly as **strings** (`"0"`..`"100"`):
- `[profile]` `schema_ver`, `last_host`, `last_port`, `tutorial_done`
- `[audio]` `vol_master`, `vol_speech`, `vol_self`, `vol_threat`, `vol_actors`, `vol_world`, `vol_ambience`, `vol_music`, `speech_mode`, `tts_rate`, `tts_voice`
- `[controls]` `turn_snap_deg`, `bind_<action>`
- `[wallet]` `slot_0` through `slot_7`, always writing all 8 keys (`""` when empty) in LRU order (`host:port|username|token_hex`). Plaintext passwords are NEVER written anywhere on disk.
