# Wire Protocol Contract: Wildlands Online (`PROTO_VERSION = 1`)

All packets are UTF-8 strings delimited by `|` (`FIELD_SEP`).
Free-text fields MUST be escaped with `wire_escape()` and unescaped with `wire_unescape()`.
Optional trailing fields MAY use `-` when empty so no mid-packet empty field shifts indices.
All floating-point coordinates are formatted to **2 decimal places** (`%.2f` equivalent).
Max UDP packet size MUST stay strictly `<= 1350` bytes.

---

## ENet Channels (`MAX_CHANNELS = 6`)

| Channel | Constant | Reliability | Purpose |
|---|---|---|---|
| `0` | `CH_SPEECH` | Reliable | Urgent spoken alerts, combat logs, death/kill, system notices, server refusals |
| `1` | `CH_AUDIO` | Reliable | 3D spatial world sound triggers (hits, footsteps of others, doors, building, wildlife calls) |
| `2` | `CH_CONTROL` | Reliable | Handshake, Auth, Map sync chunks, Inventory/Craft/Build commands, Ping/Pong, Who, News, Dev/Mod |
| `3` | `CH_CHAT` | Reliable | Global chat, Local/Area chat, Team/Party chat, Private Messages, Emotes |
| `4` | `CH_SNAPSHOT` | Unreliable | Earshot-scoped entity positions (`<= 35` tiles), vitals deltas, weather/time |
| `5` | `CH_INPUT` | Unreliable | Client key bitmask, facing `0..359`, active belt slot |

---

## Client -> Server Messages

| Opcode | Channel | Format | Validation / Rules |
|---|---|---|---|
| `HELLO` | `CH_CONTROL` | `HELLO\|proto_ver\|client_ver\|is_source_flag` | Reject immediately on `proto_ver != PROTO_VERSION` |
| `REG` | `CH_CONTROL` | `REG\|username\|password` | Sanitized `3..20` chars, password `6..64` chars, IP rate-limited |
| `LOGIN` | `CH_CONTROL` | `LOGIN\|username\|password` | Returns `AUTH_OK` + new bearer token or `AUTH_ERR\|reason` |
| `TOKEN` | `CH_CONTROL` | `TOKEN\|username\|token_hex` | Constant-time compare on hashed token; clears invalid token |
| `GUEST` | `CH_CONTROL` | `GUEST\|desired_name` | Allowed ONLY if `--allow-guests` or `--test-mode` is active |
| `LOGOUT` | `CH_CONTROL` | `LOGOUT` | Invalidates active token server-side |
| `PING` | `CH_CONTROL` | `PING\|client_ms` | Echoed back immediately as `PONG\|client_ms` |
| `NEWS` | `CH_CONTROL` | `NEWS` | Requests MOTD + changelog lines |
| `WHO` | `CH_CONTROL` | `WHO` | Requests online count + per-player name/zone/rank |
| `INPUT` | `CH_INPUT` | `INPUT\|seq\|keys_mask\|facing` | `facing` clamped `0..359`; keys: fwd/back/left/right/sprint/jump/block |
| `ACT` | `CH_CONTROL` | `ACT\|action\|arg1\|arg2` | `gather`, `attack`, `use_belt`, `equip:<slot>`, `craft:<recipe_id>`, `eat`, `drink`, `build:<type>`, `interact`, `lock`, `repair`, `demolish`, `loot` |
| `CHAT` | `CH_CHAT` | `CHAT\|scope\|target\|text` | `scope`: `global\|local\|team\|pm\|emote`; escaped, max 220 chars, rate-limited (`1 msg / 800ms`) |
| `SOCIAL` | `CH_CONTROL` | `SOCIAL\|op\|target` | `friend_add\|friend_rem\|block\|unblock\|duel_ask\|duel_acc\|profile\|leaderboard` |
| `CHEST` | `CH_CONTROL` | `CHEST\|op\|obj_id\|slot\|qty` | `open\|put\|take` with distance + lock verification |
| `BUILDMAP` | `CH_CONTROL` | `BUILDMAP\|cmd\|...` | Rank >= `Builder`: `toggle\|zone\|surface\|wall\|water\|platform\|resource\|emitter\|spawn\|validate\|save\|reload` |
| `DEV` | `CH_CONTROL` | `DEV\|cmd\|arg1\|arg2` | Rank == `Developer` + allowlisted: `set_bots\|set_wildlife\|weather\|time\|announce\|reload_all\|tp\|spawn_item` |
| `MOD` | `CH_CONTROL` | `MOD\|cmd\|target\|duration_min\|reason` | Rank >= `Mod`; enforces `actor.rank > target.rank`; logs every action & refusal |

---

## Server -> Client Messages

| Opcode | Channel | Format | Behavior |
|---|---|---|---|
| `WELCOME` | `CH_CONTROL` | `WELCOME\|proto_ver\|server_name\|motd\|guests_flag` | Confirms protocol match; speaks welcome/motd summary |
| `REFUSE` | `CH_CONTROL` | `REFUSE\|code\|spoken_reason` | Sent before disconnect (`ver_mismatch`, `full`, `banned_reason_duration`) |
| `AUTH_OK` | `CH_CONTROL` | `AUTH_OK\|username\|rank\|token_or_dash` | Client saves token in AppData wallet for `host:port` |
| `AUTH_ERR` | `CH_CONTROL` | `AUTH_ERR\|spoken_reason` | Clears stale token if `bad_token` |
| `MOTD` | `CH_CONTROL` | `MOTD\|line_escaped` | Followed by `CHANGELOG\|idx\|line_escaped` |
| `MAP_HDR` | `CH_CONTROL` | `MAP_HDR\|name\|w\|h\|max_z\|default_surface\|chunk_total` | Resets client map cache |
| `MAP_CHK` | `CH_CONTROL` | `MAP_CHK\|idx\|payload_escaped` | `<= 1200` bytes/chunk; on last chunk client confirms ready |
| `MAP_OBJ` | `CH_CONTROL` | `MAP_OBJ\|op\|id\|type\|x\|y\|z\|facing\|hp\|max_hp\|locked\|is_open\|owner` | `add\|upd\|del` for persistent player structures & resource state |
| `SNAP` | `CH_SNAPSHOT` | `SNAP\|srv_tick\|my_x\|my_y\|my_z\|my_fac\|hp\|hung\|thir\|stam\|warm\|zone\|ent_list` | `ent_list`: `id,kind,name,x,y,z,fac,state;...` strictly within `EARSHOT_RADIUS` (`<= 35`), batched if > 1300 bytes |
| `INV` | `CH_CONTROL` | `INV\|belt_slot\|slot0_id:qty;...` | Full authoritative inventory sync |
| `SFX` | `CH_AUDIO` | `SFX\|layer\|sound_key\|x\|y\|z\|vol_scale\|occlude_hint` | Triggers spatialized 3D audio on `sound_pool` (or stationary if `layer == self`) |
| `SPEAK` | `CH_SPEECH` | `SPEAK\|buf_channel\|interrupt\|text_escaped` | Files into `buffers.nvgt` AND speaks if buffer not muted |
| `CHAT_MSG` | `CH_CHAT` | `CHAT_MSG\|scope\|sender\|rank_tag\|text_escaped` | Client checks local blocklist, formats scope phrase, files into `BUF_CHAT`/`BUF_PM`, speaks if unmuted |
| `WHO_RES` | `CH_CONTROL` | `WHO_RES\|count\|name:zone:rank;...` | Count first, then players |
| `PONG` | `CH_CONTROL` | `PONG\|client_ms` | Client computes RTT ms + verdict |
| `CHEST_DATA` | `CH_CONTROL` | `CHEST_DATA\|obj_id\|item0:qty;...` | Opens chest interaction menu |
| `BUILDER_POS` | `CH_CONTROL` | `BUILDER_POS\|x\|y\|z\|surface\|zone\|wall_here` | Spoken + audio preview when moving Map Builder cursor |
