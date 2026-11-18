# Quickstart & Verification Guide: Wildlands Online

**Feature**: `001-wildlands-online-survival`
**Target Toolchain**: NVGT `0.90.0-dev` (`C:\nvgt\nvgt.exe`) + Python `3.11+` + `ffmpeg 8.1`

---

## 1. Prerequisites

1. Verify NVGT compiler is available:
   ```powershell
   nvgt --version
   ```
2. Verify audio assets and manifest integrity (once `sounds/` is populated):
   ```powershell
   nvgt tools/asset_check.nvgt
   ```

---

## 2. Offline Verification Suite (No Window, No Sound, Fast)

Run all stateless unit & contract checks (exits `0` on `PASS`, non-zero on `FAIL`):
```powershell
nvgt tools/common_check.nvgt
nvgt tools/map_check.nvgt
nvgt tools/auth_check.nvgt
nvgt tools/asset_check.nvgt
```

---

## 3. Compilation Verification

Compile dedicated server and client executables cleanly:
```powershell
nvgt -c server/server.nvgt
nvgt -c client/client.nvgt
```

---

## 4. End-to-End Integration Check (Multi-Client Against Local Server)

Run automated 2-client integration suite on non-default port (`7199`, `--test-mode`, `--headless`):
```powershell
nvgt tools/net_integration_check.nvgt
```
Verifies:
- Account registration + token persistence login + duplicate name refusal
- Movement + server clamping + wall collision
- Global / Local / Private chat round-trip & block filtering
- Survival gathering + crafting + structure placement + door occlusion state + restart persistence
- Rank enforcement (Mod cannot ban Admin; Dev Panel sets target count)
- Clean process teardown (zero orphaned `nvgt.exe` processes)

---

## 5. Manual Playtest Launch

1. Start server (from `server/` directory, windowed with live log):
   ```powershell
   cd server
   .\server.exe
   ```
   (Or run `nvgt server/server.nvgt -- --allow-guests` for quick unauthenticated testing, or `--port 7100`).
2. Start client (from `client/` directory):
   ```powershell
   cd client
   .\client.exe
   ```
3. In client main menu, select **Connect to Localhost** (dev switch) or **Connect to Server**, register once, optionally run the **Interactive Tutorial**, and explore the world!
