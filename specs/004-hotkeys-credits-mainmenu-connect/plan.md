# Implementation Plan: Standardized F1-F5 Hotkeys, Studio Credits, Server-Only News & Single-Connect Main Menu

**Branch**: `004-hotkeys-credits-mainmenu-connect` | **Date**: 2026-11-19 | **Spec**: [spec.md](file:///C:/Users/LCBoy/Desktop/data/stw/specs/004-hotkeys-credits-mainmenu-connect/spec.md)

## Summary
1. **Protocol & Server (`common/`, `server/`)**: Keep `PROTO_VERSION = 3` (additive control packets). Add `format_uptime_words(uint64 sec)` in `common/protocol.nvgt`, `KEYBIND_SCHEMA_VERSION = 2` in `common/constants.nvgt`, and server handlers `UPTIME` (`UPTIME_RES`), `MOTD_REQ` (`MOTD_RES`), and `WHO_NEAR` (`WHO_NEAR_RES` via `social_send_who_near`).
2. **Client Profile & Keybinds (`client/includes/profile.nvgt`)**: Update default keybinds (`F1` who, `F2` uptime, `F3` ping, `F4` motd, `F5` social, `F6` toggle_beacons, `F11` help, `F12` copy_last, `P` who_near), add `beacons_enabled` persistence, and migrate `schema_version < 2` cleanly on load.
3. **Client Networking, Audio & Chat (`client/includes/net_client.nvgt`, `client/includes/chat_input.nvgt`)**: Add `request_uptime()`, `request_motd()`, `request_who_near()`, and handlers for `UPTIME_RES`, `MOTD_RES`, `WHO_NEAR_RES`; gate periodic beacon pings on `profile.beacons_enabled`; add `/uptime`, `/motd`, `/near` slash commands.
4. **Main Menu, Credits & News (`client/client.nvgt`, `client/includes/menus.nvgt`)**:
   - Main Menu: single `Connect` item, `!SCRIPT_COMPILED` `F1`/`F2` dev target switcher (`"Main server"` / `"Localhost"`), `Settings and Audio Mixer`, `Interactive Audio Tutorial`, `Learn Game Sounds`, `Credits`, `Exit Game`.
   - `run_credits_menu()`: detailed studio-style credits for **LC Boy** + template note.
   - `run_news_menu(NetClient@ nc)`: strictly server-sourced (`MOTD` & `CHANGELOG`), zero local `server/data/` reads, Pause Menu only.
5. **Verification & Docs (`tools/`, `docs/`, `GEMINI.md`)**: Update tests (`client_profile_check.nvgt`, `net_integration_check.nvgt`, `client_ui_e2e_check.nvgt`), update `docs/CONTROLS.md` & `docs/PROTOCOL.md`, compile `server/server.exe` & `client/client.exe` via `nvgt -c`, run `tools/run_checks.ps1`, review, and log in `GEMINI.md`.
