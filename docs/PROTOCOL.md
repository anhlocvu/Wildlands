# Protocol — Wildlands Online (`PROTO_VERSION = 3`, `GAME_VERSION = "3.0.0"`)

See the full v3 contracts in [specs/003-stw-maps-system/contracts/protocol.md](file:///C:/Users/LCBoy/Desktop/data/stw/specs/003-stw-maps-system/contracts/protocol.md) and [specs/002-staff-multimap-builder-tracking-verticality/contracts/protocol.md](file:///C:/Users/LCBoy/Desktop/data/stw/specs/002-staff-multimap-builder-tracking-verticality/contracts/protocol.md).

## Wire Rules
1. **Delimiter & Escaping**: Pipe-delimited UTF-8 (`|`). Free-text fields (chat, names, reasons, map labels, raw map lines, announcements) pass through `wire_escape()` (`\` -> `\\`, `|` -> `\p`, `\n` -> `\n`, `\r` dropped) and single-pass `wire_unescape()`.
2. **Empty-Safe Parsing**: Always split via `split_keep_empty()` and read via `field(parts, idx, fallback)`.
3. **Versioned Handshake (`PROTO_VERSION = 3`)**: Client sends `HELLO|3|<client_ver>`. Server rejects mismatched versions with `REFUSE|ver_mismatch|...`.
4. **Fixed Precision & Hard Clamps**: Floats format to 2 decimals (`fmt2`). All coordinates (`[0..width/height]`, Z `[MAP_MIN_Z=-50 .. MAP_MAX_Z=100]`), bitmasks (`0..1023`), and IDs are server-validated and clamped.
5. **Packet Budget**: Every packet stays `<= 1350` bytes (`MAX_UDP_PAYLOAD`); large maps, Line Manager lists, Account Directory pages, logs, and reports chunk automatically on `CH_CONTROL`.

## Core v2 & v3 Protocol
- **`INPUT|mask|facing`**: `mask` includes `IN_CLIMB_UP (1<<7)` and `IN_CLIMB_DOWN (1<<8)`; `ACT|climb|up|down` triggers single-step stair climbing on the staircase's builder-selected surface.
- **`MAP_HDR|slug|name|w|h|min_z|max_z|default_surface|chunks`** & **`MAP_CHK|idx|esc_chunk`** & **`MAP_TRANSFER|slug|name|x|y|z|facing`**: Full multi-map synchronization (supporting `.map` v3 `M` rules, `Z` reverb presets, `"none"` silent ambience, and `E` Animal Spawn Zones).
- **`MAPS|list`** -> **`MAPS_LIST|rows`** & **`MAPS|tp|slug`** (`RANK_BUILDER+`): Unified `/maps` and Staff `View All Maps` browser & teleportation.
- **`SNAP|tick|x|y|z|fac|hp|hung|thir|stam|warm|night|rain|zone|fractured|ents`**: Earshot-scoped (`<= 35` steps) same-map snapshot including per-map overridden `night`, `rain`, and `fractured (0/1)`.
- **`BUILDMAP|...` -> `BM_SPECIES` / `BM_MAPS` / `BM_LM_HDR` / `BM_LM_CHK` / `BM_RES`**: Dynamic creature catalog (`BM_SPECIES`), STW Builder Hub map management (`create_map` with silent default + templates, edit-only `select_map`, `clone_map`, `edit_header`, `delete_map`, `add_box` including `animal_spawn` `E` & `zone` reverb, `noclip`), full Line Manager CRUD (`lm_tp` restricted to current map), `undo`, `validate`, `save`, `reload`.
- **`STAFF|...` -> `ST_OVERVIEW` / `ST_ACC_HDR` / `ST_ACC_CHK` / `ST_DETAIL` / `ST_LOGS` / `ST_REPORTS`**: Categorized Staff Panel, `Online` vs `Last seen` timestamps, Target Action pickers, Developer Lifecycle (`shutdown`, `restart`, `cancel`, `maintenance`, `guests`, `motd`, `changelog_add`), World Controls (practice bots), Coordinate Teleport, Audit Logs, and `/report` + `/sc`.
- **`INV|<active_hand>|<left_hand_id>|<right_hand_id>|<equipped_armor_id>|<items>`**: Server-authoritative backpack & dual-hand state (`ACCOUNTS_V3` persisted across offline/online sessions; `active_hand` is `0=none, 1=left, 2=right`).
- **`ACT|assign_hand|<left|right>|<inv_idx>`**, **`ACT|hand|<1|2>`**, **`ACT|use_hand`**: Assign item to Left/Right Hand (dual-holding allowed only when quantity >= 2), select or stow a hand (`1`/`2`), and equip (`weapon`/`tool`/`armor`) or use (`food`/`drink`/`med`/`kit`) the active hand item.
- **Standardized Status & News Queries**:
  - `WHO` -> `WHO_RES|count|entries` (`F1` / `/who`)
  - `WHO_NEAR` -> `WHO_NEAR_RES|count|name~x~y~z~rank~friend;...` (`P` / `/near`)
  - `UPTIME` -> `UPTIME_RES|uptime_sec` (`F2` / `/uptime`)
  - `PING|client_ts` -> `PONG|client_ts` (`F3` / `/ping`)
  - `MOTD_REQ` -> `MOTD_RES|escaped_motd` (`F4` / `/motd`)
  - `NEWS` -> `MOTD|...` + `CHANGELOG|idx|...` (Pause Menu `News and Changelog`; client reads live server data only).
