# Protocol — Wildlands Online (`PROTO_VERSION = 2`, `GAME_VERSION = "2.0.0"`)

See the full v2 contract in [specs/002-staff-multimap-builder-tracking-verticality/contracts/protocol.md](file:///C:/Users/LCBoy/Desktop/data/stw/specs/002-staff-multimap-builder-tracking-verticality/contracts/protocol.md).

## Wire Rules
1. **Delimiter & Escaping**: Pipe-delimited UTF-8 (`|`). Free-text fields (chat, names, reasons, map labels, raw map lines, announcements) pass through `wire_escape()` (`\` -> `\\`, `|` -> `\p`, `\n` -> `\n`, `\r` dropped) and single-pass `wire_unescape()`.
2. **Empty-Safe Parsing**: Always split via `split_keep_empty()` and read via `field(parts, idx, fallback)`.
3. **Versioned Handshake (`PROTO_VERSION = 2`)**: Client sends `HELLO|2|<client_ver>`. Server rejects mismatched versions with `REFUSE|ver_mismatch|...`.
4. **Fixed Precision & Hard Clamps**: Floats format to 2 decimals (`fmt2`). All coordinates (`[0..width/height]`, Z `[MAP_MIN_Z=-50 .. MAP_MAX_Z=100]`), bitmasks (`0..1023`), and IDs are server-validated and clamped.
5. **Packet Budget**: Every packet stays `<= 1350` bytes (`MAX_UDP_PAYLOAD`); large maps, Line Manager lists, Account Directory pages, logs, and reports chunk automatically on `CH_CONTROL`.

## Core v2 Additions
- **`INPUT|mask|facing`**: `mask` includes `IN_CLIMB_UP (1<<7)` and `IN_CLIMB_DOWN (1<<8)`; `ACT|climb|up|down` triggers single-step stair climbing on the staircase's builder-selected surface.
- **`MAP_HDR|slug|name|w|h|min_z|max_z|default_surface|chunks`** & **`MAP_CHK|idx|esc_chunk`** & **`MAP_TRANSFER|slug|name|x|y|z|facing`**: Full multi-map synchronization and cross-map portal travel.
- **`SNAP|tick|x|y|z|fac|hp|hung|thir|stam|warm|night|rain|zone|fractured|ents`**: Earshot-scoped (`<= 35` steps) same-map snapshot including `fractured (0/1)`.
- **`BUILDMAP|...` -> `BM_MAPS` / `BM_LM_HDR` / `BM_LM_CHK` / `BM_RES`**: STW Builder Hub map management (`create_map`, `select_map`, `edit_header`, `delete_map`, `add_box`, `noclip`), full Line Manager CRUD (`lm_list`, `lm_raw_edit`, `lm_replace_box`, `lm_insert`, `lm_dup`, `lm_move`, `lm_del`, `lm_tp`), `undo`, `validate`, `save`, `reload`.
- **`STAFF|...` -> `ST_OVERVIEW` / `ST_ACC_HDR` / `ST_ACC_CHK` / `ST_DETAIL` / `ST_LOGS` / `ST_REPORTS`**: Categorized Staff Panel, `Online` vs `Last seen` timestamps, Target Action pickers, Developer Lifecycle (`shutdown`, `restart`, `cancel`, `maintenance`, `guests`, `motd`, `changelog_add`), World/Spawner/Teleport, Audit Logs, and `/report` + `/sc`.
