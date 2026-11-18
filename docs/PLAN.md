# Wildlands Online — Design & Milestone Plan (v2)

## 1. What the Game Is
**Wildlands Online** is a persistent, multiplayer, 3D spatial-audio survival sandbox inspired by *Survive the Wild (STW)* and engineered specifically for blind and screen-reader players using NVGT `0.90.0-dev`.

## 2. Milestones

### v1 Foundation (Completed)
- **M1 — Verified Audio & Common Core**: CC0 normalized `.ogg` asset pack + `sounds/manifest.txt`, wire escaping, 3D compass math, items/recipes, starter map.
- **M2 — Accounts, World Movement & Spatial Engine**: Salted 5000-round SHA-256 + tokens + 8-slot AppData wallet, 7-layer mixer, patched HRTF `sound_pool`.
- **M3 — Chat, Buffers & Online Social**: Modal `/` chat, 6-channel navigable buffers, Who, Ping, Friends, Block, Duels, Profiles, Leaderboard.
- **M4 — Survival, Crafting & 3D Combat**: Vitals, gathering, cooking, weather/day-night, wildlife AI, melee/block/bow combat.
- **M5 — Survival Building & Initial Map Builder**: Lockable doors with occlusion, persistent chests, survival kits, cursor palette.
- **M6 — Polish, Tests & E2E QA**: Key remapper, interactive tutorial, E2E test suite.

### v2 Architecture Expansion (`002-staff-multimap-builder-tracking-verticality`, Active)
- **Categorized Staff Panel (`F9`)**: Full Account Directory with `Online (<Map>, <Zone>)` vs exact `Last seen` formatting, direct target action pickers, Developer Shutdown/Restart countdown + Maintenance/Guests/MOTD/Changelog controls, World/Spawner/Teleport, Audit Logs, `/report`, and `/sc` Staff Chat.
- **Multi-Map & STW `F8` Map Builder + Line Manager**: Multiple concurrent `maps/*.map` with Map Portals (`D`), Create New Map form, 6-axis Box Coordinate forms (`Min X .. Max Z`), full Line Manager (filter, edit form/raw, insert, duplicate, move, teleport, delete), per-map Undo, Validate, Save (`.bak`), and Hot-Reload.
- **STW 6-Category Tracker**: Strict `<= 30`-step scan list (`All`, `Objects`, `Items`, `Animals`, `Structures`, `Players`), `Ctrl+=`/`Ctrl+-` category switch, `=`/`-` target browse, `Backspace` radar start, `Shift+Backspace` stop, `O` live direction/steps/elevation readout.
- **True 3D Verticality, Stair Climbing & Air/Void Law**: Unbound `PageUp`/`PageDown` from buffers to climb staircases playing the staircase's builder-selected surface footsteps; gravity falling through unsupported air, height-scaled fall damage, curable Bone Fracture (`Wooden Splint` / `Bandage`), deep-water cushioning, roof rain muffling, and void death.
- **22 Additional Real CC0 Audio Assets & Complete Documentation**: 116 verified `.ogg` files in `client/sounds/` plus `BUILDER_GUIDE.md` & `STAFF_GUIDE.md` readable in-game.
