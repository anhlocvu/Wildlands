# Quickstart & Verification Guide: Feature 002

## 1. Update Real Audio Assets
```powershell
python tools/asset_pipeline.py
```

## 2. Run Full Non-Interactive Console Checks
```powershell
powershell -ExecutionPolicy Bypass -File tools/run_checks.ps1
```
Validates:
- `common_check.nvgt`: Wire, compass, 6-axis box map parser, Line Manager ops, `ACCOUNTS_V2` + `last_seen` timestamp formatting.
- `map_check.nvgt`: Multi-map loading (`wildlands_valley.map` + `skywatch_citadel.map`), Air/Void checks, staircase `PageUp`/`PageDown` Z clamping + chosen surface lookup, portal & hazard checks, negative Z bounds.
- `auth_check.nvgt`: `ACCOUNTS_V1` migration + `ACCOUNTS_V2` roundtrip, `last_seen_epoch`, `current_map`, rank hierarchy checks.
- `asset_check.nvgt`: All manifest OGG files valid & unique.
- `client_profile_check.nvgt`: New tracker & staff keybinds persisted in INI.
- `net_integration_check.nvgt`: Live multi-map portal transfer, staircase climbing footsteps & fall damage in air, `<= 30` tile tracker validation, F8 create-map & Line Manager edits, Staff Panel account status (`Online` vs `Last seen`), safe shutdown countdown.
- `client_ui_e2e_check.nvgt`: Client connects cleanly under production server rules.

## 3. Compile Final Executables
```powershell
nvgt -c server/server.nvgt
nvgt -c client/client.nvgt
```
