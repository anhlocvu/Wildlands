---
description: "Tasks for Feature 005 (Persistent Inventory, Dual-Hand System, Shift+Space Jump, Backpack Audio)"
---

# Tasks: Feature 005

## Phase 1: Audio Assets & Shared Contracts
- [x] T001 Source real CC0 `ui/inv_open.ogg` and `ui/inv_close.ogg` in `tools/asset_pipeline.py`, run pipeline, and verify with `tools/asset_check.nvgt`
- [x] T002 Add `KEYBIND_SCHEMA_VERSION = 3` in `common/constants.nvgt` and shared `encode_item_stacks` / `decode_item_stacks` in `common/items.nvgt`

## Phase 2: TDD Checks Update (Tests First)
- [x] T003 Extend `tools/auth_check.nvgt` for `ACCOUNTS_V3` persistence (`saved_inv`, `has_saved_inv`, `left_hand_id`, `right_hand_id`, `equipped_armor_id`, `active_hand`) and backward-compatible V1/V2 migration
- [x] T004 Extend `tools/client_profile_check.nvgt` for `KEYBIND_SCHEMA_VERSION = 3` (`use_hand = KEY_SPACE`, `jump = KEY_SPACE` Shift+Space default)
- [x] T005 Update `tools/net_integration_check.nvgt` for persistent inventory across reconnect, dual-hand assignment (`>= 2` vs `1`), `1`/`2` select & stow, `Space` use/equip, and `IN_JUMP`

## Phase 3: Server Persistence & Dual-Hand Gameplay
- [x] T006 Upgrade `AccountRecord` / `AccountStore` to `ACCOUNTS_V3` in `server/includes/accounts.nvgt`
- [x] T007 Replace `belt_slot` with dual-hand + armor state and `reconcile_hands()` / `assign_hand()` / `toggle_hand()` in `server/includes/state.nvgt`
- [x] T008 Wire `complete_login()`, `sync_session_to_account()`, `ACT|assign_hand`, `ACT|hand`, `ACT|use_hand`, and inventory-dirty marking across `server/server.nvgt`, `server/includes/world.nvgt`, `server/includes/combat.nvgt`, `server/includes/builder_srv.nvgt`, `server/includes/admin_dev.nvgt`

## Phase 4: Client Dual-Hand UI, Controls & Backpack Audio
- [x] T009 Update `client/includes/profile.nvgt` keybinds (`use_hand`, `jump` Shift+Space) and v3 schema migration
- [x] T010 Update `client/includes/net_client.nvgt` to parse and store `active_hand`, `left_hand_id`, `right_hand_id`, `equipped_armor_id`
- [x] T011 Update `client/includes/menus.nvgt` (`run_inventory_menu` with Left/Right hand assignment, live labels, `inv_open.ogg` / `inv_close.ogg`)
- [x] T012 Update `client/client.nvgt` (`1`/`2` hand keys, `Space` `use_hand`, `Shift+Space` `jump`, context help)

## Phase 5: Compile, Full Verification, Review & Docs (ECC Gate)
- [x] T013 Compile `server/server.exe` & `client/client.exe` via `nvgt -c` and run full `tools/run_checks.ps1` until `=== ALL CHECKS PASSED ===`
- [x] T014 Update `docs/CONTROLS.md`, `docs/PROTOCOL.md`, `docs/ACCOUNTS.md` (if present), run code/security review, and log summary in `GEMINI.md`
