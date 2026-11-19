# Controls Specification — Wildlands Online v2

All in-game controls support full remapping in **Settings -> Key Remapping** (with conflict confirmation and Reset to Defaults).

## 1. Main Menu, Menus & Forms
- **Connect** *(Main Menu)*: Connects to `MAIN_SERVER_HOST` on `DEFAULT_PORT`. When running uncompiled from `client.nvgt` (`!SCRIPT_COMPILED`), developers can press **`F1`** to switch to `Main server` or **`F2`** to switch to `Localhost` (`127.0.0.1`) with spoken confirmation.
- **Credits** *(Main Menu)*: Studio credits and developer note (`LC Boy`).
- **Up / Down**: Move between menu items or list options (speaks item & position; wraps cleanly)
- **First Letter / Ctrl+F / Ctrl+G**: Jump by initial letter, text search, or item index
- **Home / End**: First / last item
- **Enter / Space**: Select / activate / toggle checkbox
- **Tab / Shift+Tab** (in Forms): Next / previous field
- **Left / Right** (on Sliders): Adjust value with live audio sample preview
- **Escape**: Cancel / back

## 2. In-Game Movement, 3D Orientation & Stair Climbing
- **W / Up Arrow**: Walk forward (relative to facing)
- **S / Down Arrow**: Walk backward
- **A / D**: Strafe left / right
- **Left / Right Arrow**: Snap-turn left / right (`45°` default, `90°` configurable in Settings) and speak compass heading
- **Shift + Left / Right Arrow**: Smooth turn continuously (for bisecting 3D sounds by ear)
- **Shift (held while walking)**: Sprint (consumes Stamina; disabled when fractured)
- **Shift + Space**: Jump (horizontal clearance and obstacle hop)
- **`PageUp` / `PageDown`**: Climb up / descend down staircases (`P|...|stairs`) — footsteps play on the builder-selected staircase surface

## 3. STW-Style 6-Category Tracker & Acoustic Sonar
Tracker categories: **All**, **Objects**, **Items**, **Animals**, **Structures**, **Players**.
The browsable tracker list strictly includes targets within **`30` steps** (`TRACKER_MAX_DIST = 30.0`); an active lock holds out to **`35` steps** (`EARSHOT_RADIUS`) before announcing lost track.
- **`Ctrl + Equals (=)` / `Ctrl + Minus (-)`**: Switch tracker category forward / backward
- **`Equals (=)` / `Minus (-)`**: Step next / previous target inside the current category (plays directional sonar-free radar preview ping + speaks relative direction, step count, elevation, and index)
- **`Backspace`**: Start live 3D radar beacon tracking on the focused or nearest target
- **`Shift + Backspace`**: Stop active radar tracking
- **`O`**: Speak live relative direction, step distance, and height of the tracked or focused target (`"<Target>, behind and to your left, 12 steps"`)
- **`V`**: Acoustic Sonar Sweep (directional wall/object reflection sweep)

## 4. Actions, Combat & Survival
- **`E` / `Enter`**: Context Interact (use Map Portal `D`, drink at water, gather node, open/close Door, open Chest)
- **`F`**: Primary Attack / Swing equipped weapon or shoot Bow
- **`G`**: Block / Guard (reduces incoming melee damage)
- **`Space`**: Use or equip the item in the currently selected hand (equips weapon/tool/armor, consumes food/drink/med, or places kit)
- **`1` / `2`**: Select & announce **Left Hand (`1`)** or **Right Hand (`2`)**; press the same hand key a second time while selected to stow the item back into the backpack and empty that hand
- **`I`**: Open Inventory & Backpack menu (plays backpack open/close audio; **`Up` / `Down`** browse items, **`Left Arrow`** holds item in Left Hand, **`Right Arrow`** holds item in Right Hand — holding the same item in both hands requires quantity >= 2)
- **`C`**: Open Crafting menu
- **`B`**: Open Survival Building menu (place wall/door/floor/stairs/campfire/chest/bench/beacon)
- **`L`**: Lock / Unlock targeted Door or Chest; **`R`**: Repair targeted Structure; **`Ctrl+Delete`**: Demolish owned Structure

## 5. Audio Map Builder (`F8`), `/maps` Navigation & Staff Panel (`F9`)
- **`/maps`** (or `/map`, **`Builder`+** via `/` modal chat): Open the **Server Maps Directory**; press **`Enter`** on any map to teleport to its spawn and select it for editing.
- **`F8`** (`Builder`+): Open the **STW Audio Map Builder Hub** (Add Elements & Animal Spawn Zones, Line Manager + 3D Bounds Ping, Coordinate Clipboard, Create New Map Templates, Clone Map, Switch Active Map Edit-Only, Map Header Rules/Reverb, Undo, Noclip, Validate, Save, Hot-Reload).
  - In **Free-Roam Cursor Mode**: **Arrows / PageUp / PageDown** step cursor `(X, Y, Z)`, **`M`** marks Corner 1, **`Shift+M`** marks Corner 2, **`B` / `Enter`** opens Cursor Palette, **`Ctrl+S`** saves & reloads, **`F8`** exits cursor mode.
- **`F9`** (`Moderator`+): Open the **Categorized Staff Panel** (Account Directory with `Online` & `Last seen` timestamps, View All Maps `/maps`, Target Actions, Developer Server Lifecycle Shutdown/Restart, World Controls, Coordinate Teleport, Telemetry, Audit Logs & Player Reports).

## 6. Chat, Buffers & Standardized Online Status Keys (`F1`–`F6`, `F11`–`F12`, `P`)
- **`/`**: Open Modal Chat input (`Enter` sends, `Escape` cancels; supports `/pm <user> <msg>`, `/r <msg>`, `/local <msg>`, `/global <msg>`, `/team <msg>`, `/emote <text>`, `/report <msg>`, `/sc <msg>`, `/maps` for Builder+, `/who`, `/near`, `/uptime`, `/ping`, `/motd`)
- **`,` / `.`** *(Comma / Period ONLY; PageUp/PageDown reserved for stairs)*: Switch Message Buffer channel (`All`, `Chat`, `Messages`, `Social`, `Game`, `System`)
- **`[` / `]`**: Browse buffer history (older / newer line); **Home / End** in buffer mode or **Shift+[ / ]**: Oldest / newest line
- **`` ` `` (Backtick) or `Ctrl+R`**: Repeat last spoken line
- **`Ctrl+M`**: Mute/unmute focused buffer channel
- **`Ctrl+C`**: Copy focused buffer line to clipboard
- **`H`**: Read Health, Hunger, Thirst, Stamina, Warmth, Fracture status, Time & Weather
- **`X`**: Read Map Name, Zone Name, `(X, Y, Z)` Coordinates, and Surface (or `in mid-air`)
- **`K`**: Read Compass Facing
- **`F1`**: Who Is Online (player count, ranks, friends, locations)
- **`F2`**: Server Uptime
- **`F3`**: Measure Ping (ms + quality verdict)
- **`F4`**: Read live server Message of the Day (ignored when `Alt` is held)
- **`F5`**: Social Menu (Online Players, Friends, Block, Duels, Leaderboard, Profile, Staff shortcuts)
- **`F6`**: Toggle periodic Beacon 3D audio cues on/off (saved to profile)
- **`P`**: Who Is Near (players within earshot on current map with relative direction & steps)
- **`F11` / `Shift+F1`**: Context Help
- **`F12`**: Copy last spoken line to clipboard
- **`F10` / `Escape`**: In-Game Pause Menu (includes server-only News & Changelog)
