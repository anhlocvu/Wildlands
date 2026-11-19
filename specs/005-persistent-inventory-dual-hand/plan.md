# Implementation Plan: Persistent Server Inventory, Dual-Hand System & Backpack Audio

**Branch**: `005-persistent-inventory-dual-hand` | **Date**: 2026-11-19 | **Spec**: [spec.md](file:///C:/Users/LCBoy/Desktop/data/stw/specs/005-persistent-inventory-dual-hand/spec.md)

## Summary
1. **Shared Constants & Helpers (`common/constants.nvgt`, `common/items.nvgt`)**:
   - Bump `KEYBIND_SCHEMA_VERSION = 3`.
   - Remove `BELT_SLOTS` dependency; add shared item-stack serialization helpers `encode_item_stacks()` / `decode_item_stacks()` in `common/items.nvgt` so both `accounts.nvgt`, `world.nvgt`, and `state.nvgt` share one canonical encoder/decoder.
2. **Account Persistence (`server/includes/accounts.nvgt`, `server/includes/state.nvgt`, `server/server.nvgt`, `server/includes/admin_dev.nvgt`)**:
   - Upgrade `AccountStore` to `ACCOUNTS_V3` with backward-compatible parsing for `ACCOUNTS_V1` & `ACCOUNTS_V2`.
   - Store `has_saved_inv`, `saved_inv`, `left_hand_id`, `right_hand_id`, `equipped_armor_id`, `active_hand`.
   - Add `PlayerSession` dual-hand methods: `assign_hand(int hand, const string&in item_id)`, `toggle_hand(int hand)`, `reconcile_hands()`, `active_item()`, and `sync_session_to_account()`.
3. **Server Gameplay & Packet Handlers (`server/server.nvgt`, `server/includes/world.nvgt`, `server/includes/builder_srv.nvgt`)**:
   - Update `send_inv()` to emit `INV|<active_hand>|<left_hand_id>|<right_hand_id>|<equipped_armor_id>|<items>`.
   - Add `ACT|assign_hand|<left|right>|<idx>`, `ACT|hand|<1|2>`, `ACT|use_hand` (equipping `weapon`/`tool`/`armor`, consuming `food`/`drink`/`med`, placing `kit`).
   - Reconcile hands & mark `accounts.dirty = true` on all inventory mutations.
4. **Client Profile, Net, Menus & World Input (`client/includes/profile.nvgt`, `client/includes/net_client.nvgt`, `client/includes/menus.nvgt`, `client/client.nvgt`)**:
   - Bind `use_hand` to `KEY_SPACE` and `jump` to `KEY_SPACE` (Shift+Space when shared), migrate schema `< 3`.
   - Update `NetClient` to parse `INV` v2 format (`active_hand`, `left_hand_id`, `right_hand_id`, `equipped_armor_id`).
   - Update `run_inventory_menu()` with `Left Arrow` / `Right Arrow` hand assignment, live label updates without closing, and `inv_open.ogg` / `inv_close.ogg` cues.
   - Update `run_world_session()` & `speak_context_help()` for `1`/`2` hands, `Space` use/equip, `Shift+Space` jump.
5. **Audio Assets, Tests & Docs (`tools/asset_pipeline.py`, `tools/*.nvgt`, `docs/`, `GEMINI.md`)**:
   - Add `ui/inv_open.ogg` and `ui/inv_close.ogg` in `tools/asset_pipeline.py` from verified CC0 recordings and regenerate manifest/credits.
   - Update & run `common_check`, `auth_check`, `asset_check`, `client_profile_check`, `net_integration_check`, `client_ui_e2e_check`, compile `server.exe` & `client.exe`, and run `tools/run_checks.ps1`.
