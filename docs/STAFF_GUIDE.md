# Staff Operations Guide (`F9`) — Wildlands Online v2

This guide covers the **Categorized Staff & Developer Control Panel (`F9`)**, rank permissions, live account inspection (`Online` vs `Last seen`), player moderation, multi-map management, world controls, audit logging, and safe server lifecycle management (`Shutdown` / `Restart`).

---

## 1. Rank Hierarchy & Trust Boundaries

| Rank ID | Role | Primary Permissions |
|---|---|---|
| `0` | **Player** | Standard gameplay, `/report`, social/chat/building |
| `1` | **Builder** | STW Audio Map Builder (`F8`), multi-map editing, Line Manager, Staff Chat (`/sc`) |
| `2` | **Moderator (`RANK_MOD`)** | Staff Panel (`F9`), Account Directory (Online / Last Seen), Rescue, Teleport To, Bring lower ranks, Kick, Timed Mute/Ban (`<= RANK_MOD` targets), Unmute, Audit Logs & Report Resolution |
| `3` | **Admin (`RANK_ADMIN`)** | All Moderator powers + View Account Last IP, Move Player Between Maps, Heal & Cure Fracture, Give Item Catalog, Clear Inventory, Set Rank (up to Moderator), Invalidate Session Token, World Time/Weather/Drops/Announcements, Creature/Bot Spawner |
| `4` | **Developer (`RANK_DEV`)** | All Admin powers + Allowlisted Lifecycle Operations (`server/data/devs.txt`): Countdown Shutdown, Clean Server Restart, Cancel Countdown, Maintenance Lock, Guest Toggle, Live MOTD & Changelog Edit, Wildlife/Bot Population Scaling, Live Full Reload |

> **Security Rule**: Lifecycle controls (`shutdown`, `restart`, `maintenance`, `guests`, `motd`, `changelog_add`) require **both** `RANK_DEV` **and** presence in `server/data/devs.txt`. Every denied attempt logs a `REFUSED` audit entry.

---

## 2. Opening the Staff Panel (`F9`)

Press **`F9`** in-game (or open **Pause Menu -> Staff Panel (F9)**). All actions work through categorized menus and pickers — **you do not need to memorize console commands**.

### Category 1: Account Directory (Online & Last Seen)
- Displays all accounts registered on the server, sorted with **Online players first** and offline accounts ordered by **most recent activity**.
- **Online entry format**:
  `Alice [Player] - Online (Wildlands Valley, Hearth Clearing)`
- **Offline entry format**:
  `Bob [Player] - Last seen: 2 hours ago (2026-11-18 17:12 UTC+07:00)`
- Includes filters (`All`, `Online Players Only`, `Staff Members Only`, `Muted or Banned Only`) and status badges (`[BANNED]`, `[MUTED]`).
- Selecting any account fetches the full record (`ST_DETAIL`: account ID, rank, status/last-seen, current or saved `(map, X, Y, Z)`, total playtime in minutes, PvE hunts, PvP duels, deaths, structures built, active ban/mute countdown, and last IP for Admin+) and provides direct action pickers:
  - **Teleport to Player** / **Bring Player to Me** / **Move Player to Another Map**
  - **Restore Vitals & Cure Fracture**
  - **Give Item from Catalog** (menu picker for every `ItemDef` + quantity selector)
  - **Clear Inventory** (with confirmation)
  - **Rescue to Safe Spawn** (works even when the player is offline by resetting saved coordinates!)
  - **Mute / Unmute** (`5m`, `15m`, `1h`, `24h`, `7d`)
  - **Ban / Unban** (`5m .. 7d` or `Permanent`, disconnected immediately if online)
  - **Set Account Rank** & **Invalidate Saved Session Token** (forces password login on next connect)

### Category 2: Server Lifecycle (`Developer Allowlist Only`)
- **Schedule Graceful Shutdown**: Choose delay (`5s`, `10s`, `30s`, `60s`) + reason. Plays `multi/server_shutdown.ogg`, broadcasts spoken countdown warnings, atomically flushes `accounts.dat`, `world_objects.dat`, `reports.dat`, updates every online account's `last_seen_epoch`, disconnects peers cleanly, and exits.
- **Schedule Clean Server Restart**: Executes the exact same countdown and atomic flush, tears down the ENet socket completely so the UDP port releases cleanly, and spawns the new server instance with `--bind-delay-ms 1200` using NVGT's `run()` before exiting.
- **Cancel Scheduled Shutdown / Restart**: Aborts an active countdown and notifies players.
- **Maintenance Mode (`ON / OFF`)**: Blocks non-staff logins with a polite maintenance message while letting Staff remain connected to inspect or build.
- **Guest Logins (`ON / OFF`)**: Dynamically opens or closes `Guest_*` temporary access without editing CLI flags.
- **Live MOTD & Changelog Editors**: Updates `motd.txt` / `changelog.txt` and pushes fresh `MOTD` / `CHANGELOG` packets immediately to all connected players.

### Category 3: World, Weather, Saves & Broadcasts (`Admin+`)
- Force immediate disk persistence (`Save Now`).
- Broadcast high-priority `Server Announcement:` speech to every player across all maps.
- Override weather (`Clear` / `Rain`) and time-of-day (`Day` / `Night`).
- Clear ground drops across all maps to tidy loot clutter.
- Tune live server wildlife population and practice bot count (`Developer`), or reload config/maps live.

### Category 4: Spawner & Multi-Map Teleport
- **Spawn Wildlife or Practice Bots**: Choose `deer`, `rabbit`, `boar`, `wolf`, `bear`, or `bot_survivor` to spawn right near you on your current map.
- **Teleport to Any Map or Coordinates**: Pick any loaded map and enter `(X, Y, Z)` coordinates directly.

### Category 5: Telemetry, Audit Logs & Player Reports
- Live telemetry overview: Server uptime, worst simulation tick time (ms), online count, total registered accounts, loaded maps + per-map player distribution, persistent structure count, active wildlife/bot count, and open report badge count.
- **Audit Logs**: Streams the most recent lines from `server/logs/server.log` into a browsable screen-reader menu.
- **Player Reports**: Players submit reports using `/report <message>` or `/report @Player <message>`. Staff receive an immediate `MBUF_SYSTEM` speech alert. From **F9 -> Telemetry, Audit Logs & Player Reports -> View Player Reports**, staff can **Teleport to Report Location** or **Mark Report Resolved**.

---

## 3. Staff Chat (`/sc`)

Use **`/`** -> `/sc <message>` (or **F9 -> Send Staff Chat Message**) to communicate privately across all maps with every online player of `Builder` rank and above. Messages chime with `ui/staff_alert.ogg`.

---

## 4. Operational Checklists

### Before Planned Maintenance or Restart
1. Check **Account Directory -> Online** and announce in `/sc` or **Broadcast Announcement**.
2. Toggle **Maintenance Mode ON** if you do not want new players joining mid-work.
3. Click **Save All Accounts, Objects & Reports Now** (or use **Schedule Shutdown / Restart**, which saves atomically on final tick).
4. After restart reconnects, confirm **worst tick <= 16ms**, `open reports`, and check **Audit Logs** for clean startup without `ERROR`/`WARN` lines.
