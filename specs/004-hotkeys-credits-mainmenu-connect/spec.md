# Feature Specification: Standardized F1-F5 Hotkeys, Studio Credits, Server-Only News & Single-Connect Main Menu

**Feature Branch**: `004-hotkeys-credits-mainmenu-connect`
**Created**: 2026-11-19
**Status**: Approved by User
**Input**: User request:
- Standardize F1-F5 hotkeys: F1 who is online, F2 server uptime, F3 ping check, F4 read Message of the Day, F5 social menu; add complementary template features (`nvgt-dev` / `online-audio-game-dev` conventions) such as Who Is Near (`P`), Toggle Beacons (`F6`), Context Help (`F11` / `Shift+F1`), and Copy Last Spoken (`F12`).
- Add a detailed, studio-grade Credits section in the Main Menu crediting **LC Boy** (never full real name) with the developer template note.
- Remove Main Menu News & Changelog (Option B) and remove client-side local reading of `server/data/motd.txt` and `changelog.txt` so News & Changelog is strictly server-fed inside the in-game Pause Menu.
- Simplify Main Menu to a single `Connect` button (no custom server form/buttons); for uncompiled dev runs (`!SCRIPT_COMPILED`), pressing `F1` selects and speaks `"Main server"` and pressing `F2` selects and speaks `"Localhost"`; provide clear instructions for editing `MAIN_SERVER_HOST`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Standardized In-Game Hotkeys F1-F5 & Template Utilities (Priority: P1)
Players entering the game expect standard audio-game function keys:
- `F1`: Who is online (count + player list with rank/friend/location).
- `F2`: Server uptime (requested live from server, spoken in natural units).
- `F3`: Ping check (audible start cue + RTT in milliseconds and quality verdict).
- `F4`: Message of the Day (requested live from server, ignoring Alt+F4).
- `F5`: Social Menu (online players, friends, private messages, blocks, duels, leaderboard, profile).
Plus complementary utilities inspired by `nvgt-dev` templates:
- `P`: Who is near (players in earshot/same map with relative direction and step distance).
- `F6`: Toggle Beacon sounds on/off (persisted in `ClientProfile`).
- `F11` / `Shift+F1`: Context controls help (since `F1` is now Who Is Online).
- `F12`: Copy last spoken line to clipboard.
All new/updated actions are registered in `ClientProfile.keybinds` with a `keybind_schema_version = 2` migration so existing `settings.ini` files adopt the standardized bindings automatically.

### User Story 2 - Studio Credits & Server-Only News (Priority: P2)
1. **Credits**: Main Menu includes a detailed, studio-style `Credits` menu crediting **LC Boy** as Creator, Lead Developer, and Designer, along with architecture/audio/accessibility/tooling credits and the developer note explaining that while the game may not open as an official public server, it is built as a useful foundation template for survival online audio games.
2. **Server-Only News & Changelog**: Main Menu removes `News and Changelog` (Option B). `run_news_menu(NetClient@ nc)` never reads local `server/data/motd.txt` or `server/data/changelog.txt`; it displays only live `MOTD` and `CHANGELOG` received from the connected server (and refreshes via `NEWS` when opened in-game from the Pause Menu).

### User Story 3 - Single Connect Main Menu & Dev F1/F2 Server Switch (Priority: P3)
Main Menu contains **only one connection item**: `Connect` (no custom server input box or multiple connect entries).
- When compiled (`SCRIPT_COMPILED == true`), `Connect` always targets `MAIN_SERVER_HOST` on `DEFAULT_PORT`, and `F1`/`F2` in Main Menu do not switch targets.
- When running uncompiled from `.nvgt` source (`SCRIPT_COMPILED == false`), `Connect` defaults to `MAIN_SERVER_HOST`, pressing `F1` switches target to `MAIN_SERVER_HOST` and speaks `"Main server"`, and pressing `F2` switches target to `LOCAL_SERVER_HOST` (`127.0.0.1`) and speaks `"Localhost"`.

## Functional Requirements
- **FR-001**: Server MUST handle `UPTIME` -> `UPTIME_RES|<uptime_sec>`, `MOTD_REQ` -> `MOTD_RES|<escaped_motd>`, and `WHO_NEAR` -> `WHO_NEAR_RES|<cnt>|<entries>` for authenticated sessions.
- **FR-002**: Client MUST bind default actions `who=KEY_F1`, `uptime=KEY_F2`, `ping=KEY_F3`, `motd=KEY_F4`, `social=KEY_F5`, `toggle_beacons=KEY_F6`, `help=KEY_F11`, `copy_last=KEY_F12`, `who_near=KEY_P` with `KEYBIND_SCHEMA_VERSION = 2` migration in `ClientProfile`.
- **FR-003**: `F4` MUST NOT trigger MOTD when `Alt` is held (`KEY_LMENU`/`KEY_RMENU`).
- **FR-004**: `run_credits_menu()` MUST be reachable from Main Menu, credit **LC Boy** exclusively (zero occurrences of real name), and include the template developer note.
- **FR-005**: Main Menu MUST NOT include `News and Changelog` or custom server entry; `run_news_menu()` MUST NOT read local `server/data/` files.
- **FR-006**: Main Menu MUST have a single `Connect` item and `!SCRIPT_COMPILED` `F1`/`F2` switching between `MAIN_SERVER_HOST` and `LOCAL_SERVER_HOST` with spoken confirmation.
- **FR-007**: `common/constants.nvgt` MUST remain the single source of truth for `MAIN_SERVER_HOST`, `LOCAL_SERVER_HOST`, and `DEFAULT_PORT`.
