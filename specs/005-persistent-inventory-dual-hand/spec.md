# Feature Specification: Persistent Server Inventory, Dual-Hand System & Backpack Audio

**Feature Branch**: `005-persistent-inventory-dual-hand`
**Created**: 2026-11-19
**Status**: Approved by User
**Input**: User request:
1. Persist each player's inventory and hand/equipment state on the server across disconnect/offline/online sessions instead of resetting to starter inventory on every login.
2. Replace the legacy 1-9 belt slot system:
   - In the Inventory menu (`I`), browsing items and pressing `Left Arrow` holds/assigns the focused item in the **Left Hand**; `Right Arrow` holds/assigns it in the **Right Hand**.
   - An item may be assigned to **both hands simultaneously only if its quantity in inventory is `>= 2`**. If quantity is `1`, assigning it to the other hand transfers it from the opposite hand.
   - Outside the menu in the world, pressing `1` interacts with the Left Hand and pressing `2` interacts with the Right Hand:
     - First press on a non-empty hand selects/readies that hand and speaks the held item name (and quantity).
     - Pressing the same hand key (`1` or `2`) a second time while that hand is already selected stows the item back into the backpack and leaves that hand empty (inventory quantity unchanged).
     - Pressing the opposite hand key switches directly to that hand without stowing the first.
   - Pressing **`Space`** (`use_hand`, moved from `Q`) equips weapons/tools/armor or uses consumable items/kits in the currently selected hand.
   - Bind **Jump** to **`Shift + Space`**.
3. Source real CC0 backpack open and close sounds and play them when the Inventory menu opens and closes.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Persistent Server-Side Inventory & Hand State (Priority: P1)
A player registers or signs in, gathers wood, crafts items, consumes food, or arranges items in their left/right hands, then disconnects and reconnects (or the server restarts). Upon signing back in, their exact inventory stacks, empty slots, and left/right/armor selections are restored rather than reset to the 4 starter items.
- **First-login behavior**: New accounts (and legacy `ACCOUNTS_V1`/`ACCOUNTS_V2` accounts with `has_saved_inv == false`) receive starter items once and immediately mark `has_saved_inv = true`.
- **Empty inventory preservation**: If a player empties their pack completely (e.g., deposits everything into a chest or consumes all items), reconnecting keeps their pack empty rather than re-granting starter items.
- **Guest accounts**: Guest sessions remain ephemeral and receive starter inventory without disk persistence.

### User Story 2 - Dual-Hand Inventory Assignment (`I` + Left/Right) & World Keys (`1`, `2`, `Space`, `Shift+Space`) (Priority: P1)
- Inside the Inventory menu (`I`):
  - `Up` / `Down`: Browse items in backpack.
  - `Left Arrow`: Assign focused item to Left Hand (allowed on both hands simultaneously only when `count_item(id) >= 2`; if `count == 1` and already in Right Hand, moves from Right Hand to Left Hand).
  - `Right Arrow`: Assign focused item to Right Hand (same `>= 2` rule).
  - Menu labels update immediately (`[Left Hand]`, `[Right Hand]`, `[Both Hands]`) without closing the menu.
- Outside in the world:
  - `1`: Select Left Hand (speaks item) if not currently active; if already active, stow Left Hand back into backpack (`left_hand_id = ""`, `active_hand = 0`). Speaks `"Left hand is empty."` if unassigned.
  - `2`: Same toggle/select/stow behavior for Right Hand.
  - Keys `3`..`9` no longer select belt slots.
  - `Space` (without `Shift`): Equip (`weapon`, `tool`, `armor`) or Use (`food`, `drink`, `med`, `kit`) the item in the currently selected hand (`active_hand == 1` or `2`). Consuming the last unit of an item clears it from the hand(s); dropping from `>= 2` to `1` while held in both hands clears the non-active hand automatically.
  - `Shift + Space`: Jump (`IN_JUMP`) without triggering `use_hand`.

### User Story 3 - Authentic Backpack Open/Close Audio Cues (Priority: P2)
Real verified CC0 `.ogg` audio files `ui/inv_open.ogg` and `ui/inv_close.ogg` play when opening and closing the Inventory menu (`I` or Pause -> Inventory).

## Functional Requirements
- **FR-001**: `AccountStore` MUST support `ACCOUNTS_V3` persistence for `has_saved_inv`, `saved_inv`, `left_hand_id`, `right_hand_id`, `equipped_armor_id`, and `active_hand`, while remaining 100% backward-compatible with `ACCOUNTS_V1` and `ACCOUNTS_V2` files.
- **FR-002**: Server MUST sync session inventory & hand state into `AccountRecord` on autosave, logout, disconnect, grace expiry, and shutdown/restart, and restore it on `complete_login()`.
- **FR-003**: Server MUST enforce the `count_item(id) >= 2` rule for dual-hand holding on assignment and whenever item quantities decrease (consume, drop, craft, chest deposit, clear_inv).
- **FR-004**: Server MUST handle `ACT|assign_hand|<left|right>|<idx>`, `ACT|hand|<1|2>`, and `ACT|use_hand` authoritatively; `ps.active_item()` MUST resolve to the active hand's item (or `null` when `active_hand == 0`).
- **FR-005**: Client MUST default `use_hand` to `KEY_SPACE` and `jump` to `KEY_SPACE` (requiring `Shift` when both share `KEY_SPACE`), migrating `KEYBIND_SCHEMA_VERSION = 3` cleanly in `ClientProfile`.
- **FR-006**: `client/sounds/ui/inv_open.ogg` and `client/sounds/ui/inv_close.ogg` MUST be sourced via `tools/asset_pipeline.py` from real CC0 recordings, pass `OggS` + MD5 uniqueness checks, and play on Inventory menu open/close.
