# Wire Protocol Contract v2 (`PROTO_VERSION = 2`)

Extends Feature 001 protocol while maintaining `|` field separation, `wire_escape()`/`wire_unescape()`, `<= 1350` UDP packet ceiling, and 6 dedicated ENet channels.

## Updated Input (`CH_INPUT`)
- `INPUT|mask|facing`: `mask` is now `0..1023` adding:
  - `IN_CLIMB_UP = 1 << 7` (`PageUp`)
  - `IN_CLIMB_DOWN = 1 << 8` (`PageDown`)
- Optional immediate action `ACT|climb|up` / `ACT|climb|down` on `CH_CONTROL` for single-tap precision alongside held `CH_INPUT` climbing.

## Multi-Map & Travel (`CH_CONTROL`)
- **Server -> Client**:
  - `MAP_HDR|slug|name|w|h|min_z|max_z|default_surface|chunk_total`
  - `MAP_CHK|idx|payload_escaped`
  - `MAP_TRANSFER|slug|name|x|y|z|facing` (notifies client of map switch before new `MAP_HDR`/`MAP_CHK`)
  - `SNAP|...` includes `fractured` flag (`0|1`) inside vitals/status or `ENT` state so client can announce leg fracture status in `H` vitals HUD.
- **Client -> Server**:
  - `ACT|portal` (triggered on `E`/`Enter` near a `MapPortal` if not `auto_step`, or automatic server-side on step-in).

## STW Builder & Line Manager (`CH_CONTROL`, Rank >= `RANK_BUILDER`)
- **Client -> Server (`BUILDMAP|cmd|...`)**:
  - `BUILDMAP|hub_sync` -> requests map list + active builder map metadata
  - `BUILDMAP|create_map|slug|name|w|h|min_z|max_z|surf|amb|sx|sy|sz`
  - `BUILDMAP|select_map|slug`
  - `BUILDMAP|edit_header|name|w|h|min_z|max_z|surf|amb|pvp`
  - `BUILDMAP|clone_map|src_slug|new_slug|new_name`
  - `BUILDMAP|delete_map|slug`
  - `BUILDMAP|noclip|0_or_1`
  - `BUILDMAP|add_box|kind|...` (`floor`, `wall`, `stairs`, `ramp`, `zone`, `water`, `hazard`, `portal`, `resource`, `emitter`, `spawn`) accepting explicit `min_x|max_x|min_y|max_y|min_z|max_z` parameters!
  - `BUILDMAP|lm_list|filter` -> requests formatted lines of `builder_edit_map`
  - `BUILDMAP|lm_raw_edit|line_idx|escaped_line`
  - `BUILDMAP|lm_replace_box|line_idx|...`
  - `BUILDMAP|lm_insert|after_idx|escaped_line`
  - `BUILDMAP|lm_dup|line_idx`
  - `BUILDMAP|lm_move|line_idx|-1_or_1`
  - `BUILDMAP|lm_del|line_idx`
  - `BUILDMAP|lm_tp|line_idx`
  - `BUILDMAP|undo`
  - `BUILDMAP|validate`
  - `BUILDMAP|save`
  - `BUILDMAP|reload`
- **Server -> Client**:
  - `BM_MAPS|active_slug|slug1:name1:w:h:players;...`
  - `BM_LM_HDR|map_slug|total_lines|chunk_count`
  - `BM_LM_CHK|idx|payload` (`line_idx~tag~summary~raw_escaped\n...`)
  - `BM_RES|ok_or_err|spoken_msg_escaped`

## Staff Panel & Lifecycle (`CH_CONTROL`, Rank >= `RANK_MOD`, Lifecycle `RANK_DEV`)
- **Client -> Server (`STAFF|cmd|...`)**:
  - `STAFF|overview` -> telemetry, maps, reports count, server flags (`maintenance`, `guests`, `shutdown_sec`)
  - `STAFF|accounts|filter` (`all|online|staff|punished`) -> paginated chunks
  - `STAFF|acc_detail|username`
  - `STAFF|act|op|target|arg1|arg2|arg3` (`tp_to`, `bring`, `move_map`, `heal`, `give_item`, `clear_inv`, `rescue`, `kick`, `mute`, `unmute`, `ban`, `unban`, `set_rank`, `clear_token`)
  - `STAFF|maps_list`
  - `STAFF|world|op|arg1|arg2` (`weather`, `time`, `bots`, `wildlife`, `clear_drops`, `announce`, `reload`, `save_now`)
  - `STAFF|spawn_mob|kind|map_slug|x|y|z`
  - `STAFF|tp_loc|map_slug|x|y|z`
  - `STAFF|lifecycle|op|seconds|reason_escaped` (`shutdown`, `restart`, `cancel`, `maintenance`, `guests`, `motd`, `changelog_add`)
  - `STAFF|logs|limit`
  - `STAFF|reports_list`
  - `STAFF|report_resolve|report_id`
- **Client -> Server (Reports & Staff Chat)**:
  - `CHAT|staff|-|text` (`/sc ...`)
  - `REPORT|target_or_dash|text_escaped` (`/report ...`)
- **Server -> Client**:
  - `ST_OVERVIEW|uptime_sec|worst_tick_ms|online|total_acc|maps_cnt|objs_cnt|mobs_cnt|reports_open|maint|guests|shutdown_rem_sec|maps_csv`
  - `ST_ACC_HDR|total|chunk_count`
  - `ST_ACC_CHK|idx|rows_payload` (row: `name,rank,online_01,map,zone,last_seen_epoch,ban_rem,mute_rem,playtime_sec,ip_or_dash`)
  - `ST_DETAIL|escaped_summary`
  - `ST_LOGS|chunk_idx|chunk_total|escaped_lines`
  - `ST_REPORTS|chunk_idx|chunk_total|rows_payload`
