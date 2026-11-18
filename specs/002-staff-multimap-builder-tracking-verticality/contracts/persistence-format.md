# Persistence Format Contract v2

## 1. Accounts Store (`data/accounts.dat` + `.bak`)
- Header: `ACCOUNTS_V2` (also cleanly parses legacy `ACCOUNTS_V1` records!)
- Record (`ACCOUNTS_V2`, 26 fields):
  `ACC|v2|id|name|salt|pw_hash|token_hash|rank|banned_until|ban_reason|muted_until|friends|blocked|kills_pvp|kills_pve|deaths|built_count|gathered_count|playtime_sec|last_x|last_y|last_z|current_map|created_at_epoch|last_seen_epoch|last_ip`
- Atomic write rule unchanged: write `.tmp`, backup existing to `.bak`, move `.tmp` into place. Fatal `alert()` if file exists and is corrupt/unreadable.

## 2. Staff Reports Store (`data/reports.dat` + `.bak`)
- Header: `REPORTS_V1`
- Record: `REP|v1|id|reporter|target|map_slug|x|y|z|created_epoch|resolved_01|resolved_by|message_escaped`

## 3. World Objects Store (`data/world_objects.dat` + `.bak`)
- Unchanged `OBJECTS_V1`; `map_name` field matches `MapInstance.slug` (or `map.name` case-insensitively for existing `Wildlands Valley` structures).
