# Quickstart & Verification Guide: Feature 003 — STW Maps System

## 1. Run Full Verification Suite
```powershell
powershell -ExecutionPolicy Bypass -File tools/run_checks.ps1
```
Verifies:
- `common_check.nvgt`: Wire helpers & dynamic `g_species` catalog integrity.
- `map_check.nvgt`: `E` Animal Spawn Zone serialization/roundtrip, `M` v3 rules (`allow_build`, `weather_enabled`, `time_mode`), `Z` `reverb_preset`, Line Manager CRUD on `E` lines, templates & clone.
- `asset_check.nvgt`: All sound assets valid `OggS`.
- `net_integration_check.nvgt`:
  - Blank/test maps (`skywatch_citadel` / newly created map) spawn 0 wildlife automatically.
  - Newly created map defaults to silent ambience (`"none"`).
  - Adding an `E` Animal Spawn Zone (`interval_ms = 1200`, `count = 3`, multiple species) spawns 0 mobs before `1200` ms, spawns 3 randomized mobs after `1200` ms, and Approach A refills 1200 ms after killing 1 mob.
  - `BUILDMAP|hub_sync` returns dynamic `BM_SPECIES` list matching `g_species`.
  - `/maps` (`MAPS|list` & `MAPS|tp`) denies rank `0` players and teleports `RANK_BUILDER+` to target map spawn while `BUILDMAP|select_map` never teleports.
  - Map rules (`allow_build = 0`, `weather_enabled = 0`, `time_mode = night`), `clone_map`, and same-map portals work cleanly.
- `client_ui_e2e_check.nvgt`: Verifies `audio_engine` handles `"none"` ambience & `audio_freeverb_node` zone reverb presets cleanly.

## 2. Clean Release Compiles
```powershell
nvgt -c server/server.nvgt
nvgt -c client/client.nvgt
```
