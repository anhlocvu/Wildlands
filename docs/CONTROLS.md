# Controls Specification — Wildlands Online

All in-game controls support full remapping in **Settings -> Key Remapping** (with conflict confirmation and Reset to Defaults).

## 1. Menus & Forms
- **Up / Down**: Move between menu items (speaks item & position; wraps cleanly with wrap sound)
- **First Letter / Ctrl+F / Ctrl+G**: Jump by initial letter, text search, or item index
- **Home / End**: First / last item
- **Enter / Space**: Select / activate / toggle checkbox
- **Tab / Shift+Tab** (in Forms): Next / previous field
- **Left / Right** (on Sliders): Adjust value with live audio sample preview
- **Escape**: Cancel / back

## 2. In-Game Movement & Orientation
- **W / Up Arrow**: Walk forward (relative to facing)
- **S / Down Arrow**: Walk backward
- **A / D**: Strafe left / right
- **Left / Right Arrow**: Snap-turn left / right (`45°` default, `90°` configurable in Settings) and speak compass heading
- **Shift + Left / Right Arrow**: Smooth turn continuously (for bisecting 3D sounds by ear)
- **Shift (held while walking)**: Sprint (consumes Stamina)
- **Space**: Jump / climb onto elevated step

## 3. Actions, Combat & Survival
- **E / Enter**: Context Interact / Gather nearby node / Open-Close Door / Open Chest
- **F**: Primary Attack / Swing equipped weapon or shoot Bow
- **G**: Block / Guard (reduces incoming melee damage)
- **1 – 9**: Select & announce quick-belt item slot
- **I**: Open Inventory & Equipment menu
- **C**: Open Crafting menu
- **B**: Open Survival Builder menu (place wall/door/floor/stairs/campfire/chest/bench/beacon)
- **L**: Lock / Unlock targeted Door or Chest; **R**: Repair targeted Structure; **Ctrl+Delete**: Demolish owned Structure

## 4. Interactive Audio Map Builder (Builder / Admin / Dev Rank)
- **F8**: Toggle Map Builder Cursor Mode
- **Arrows / PgUp / PgDn**: Step builder cursor `(X, Y, Z)` 1 tile with spoken coords, zone, surface & surface preview sound
- **M**: Cycle brush/tool (`Zone`, `Surface`, `Wall`, `Platform/Ramp`, `Water`, `Resource`, `Ambient Emitter`, `Spawn`, `Erase`)
- **Enter**: Mark corner 1 / Apply corner 2 or place object at cursor
- **Ctrl+S**: Validate & export `.map` file + request live server reload

## 5. Chat, Buffers & Online Status Keys
- **`/`**: Open Modal Chat input (`Enter` sends, `Escape` cancels; supports `/pm <user> <msg>`, `/r <msg>`, `/local <msg>`, `/global <msg>`, `/team <msg>`, `/emote <text>`)
- **`,` / `.`** (or **PageUp / PageDown**): Switch Message Buffer channel (`All`, `Chat`, `Messages`, `Social`, `Game`, `System`)
- **`[` / `]`**: Browse buffer history (older / newer line); **Home / End** in buffer mode or **Shift+[ / ]**: Oldest / newest line
- **`\`` (Backtick) or `Ctrl+R`**: Repeat last spoken line
- **`M` (in buffer mode) / `Ctrl+M`**: Mute/unmute focused buffer channel
- **`Ctrl+C` (in buffer mode)**: Copy focused buffer line to clipboard
- **`H`**: Read Health, Hunger, Thirst, Stamina, Warmth
- **`X`**: Read Zone name, Coordinates `(X, Y, Z)`, and current Surface
- **`K`**: Read Compass Facing
- **`T`**: Target / Landmark Radar Scanner (cycles nearest Wildlife, Player, Resource, Landmark, Structure — speaks relative direction + steps)
- **`V`**: Acoustic Sonar Sweep (directional pings around player)
- **`P`**: Measure Ping (ms + verdict)
- **`U`**: Who is Online (count first, then names/zones/ranks)
- **`F2`**: Social Menu (Friends, Block/Mute, Duels, Leaderboard, Profile)
- **`F1`**: Context Help (keys for current mode)
- **`F10` / `Escape`**: In-Game Pause Menu (Settings, Tutorial, News, Dev Panel, Mod Panel, Sign Out, Disconnect)
