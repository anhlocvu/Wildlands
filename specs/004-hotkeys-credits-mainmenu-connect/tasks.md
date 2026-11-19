---
description: "Tasks for Feature 004 (F1-F5 Hotkeys, Credits, Server-Only News, Single-Connect Main Menu)"
---

# Tasks: Feature 004

## Phase 1: Shared Helpers & Tests Setup (TDD)
- [x] T001 Add `KEYBIND_SCHEMA_VERSION = 2` to `common/constants.nvgt` and `format_uptime_words(uint64 sec)` to `common/protocol.nvgt`
- [x] T002 Extend `tools/client_profile_check.nvgt`, `tools/net_integration_check.nvgt`, and `tools/client_ui_e2e_check.nvgt` for F1-F5 keybinds, `schema_version` migration, `beacons_enabled`, `UPTIME`, `MOTD_REQ`, and `WHO_NEAR`

## Phase 2: Server Endpoints
- [x] T003 Add `social_send_who_near` in `server/includes/chat_social.nvgt`
- [x] T004 Handle `UPTIME`, `MOTD_REQ`, and `WHO_NEAR` in `server/server.nvgt`

## Phase 3: Client Keybinds, Net Handlers, Main Menu & Credits
- [x] T005 Update `client/includes/profile.nvgt` with standardized F1-F5 + P/F6/F11/F12 keybinds, `beacons_enabled`, and v2 schema migration
- [x] T006 Update `client/includes/net_client.nvgt` and `client/includes/chat_input.nvgt` with `request_uptime`, `request_motd`, `request_who_near`, `UPTIME_RES`/`MOTD_RES`/`WHO_NEAR_RES`, beacon toggle gating, and `/uptime`, `/motd`, `/near`
- [x] T007 Update `client/includes/menus.nvgt`: add studio `run_credits_menu()`, remove local file fallback from `run_news_menu()`, update Pause Menu label `Social and Online Players (F5)`
- [x] T008 Update `client/client.nvgt`: wire standardized hotkeys in `run_world_session()`, simplify Main Menu to single `Connect` + `Credits` (no custom server / no Main Menu News), and add `!SCRIPT_COMPILED` `F1`/`F2` server switcher

## Phase 4: Docs, Compilation & Full Verification (ECC Gate)
- [x] T009 Update `docs/CONTROLS.md` and `docs/PROTOCOL.md`
- [x] T010 Compile `server/server.exe` & `client/client.exe` with `nvgt -c` and run `tools/run_checks.ps1` until 100% PASS
- [x] T011 Review diff & record engineering log in `GEMINI.md`
