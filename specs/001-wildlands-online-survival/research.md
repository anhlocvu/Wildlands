# Research Findings: Wildlands Online (NVGT 0.90.0-dev)

**Feature**: `001-wildlands-online-survival`
**Date**: 2026-11-18
**Purpose**: Resolve technical choices and verify NVGT `0.90.0-dev` engine behavior against local headers (`C:\nvgt\include\`) and C++ source (`nvgt_src/src/`) prior to implementation.

---

## 1. Audio Engine Volume, Pan, Pitch & `sound_pool.nvgt` Behavior

### Findings from `nvgt_src/src/sound.cpp` and `C:\nvgt\include\sound_pool.nvgt`
- **Default Audio Engine Flags**: In `sound.cpp` line 104, `init_sound()` initializes `g_audio_engine` with `audio_engine::PERCENTAGE_ATTRIBUTES | audio_engine::NO_CLIP`.
- **Volume Parameter Semantics**: Because `PERCENTAGE_ATTRIBUTES` is active on the default engine, `sound::set_volume(float v)` and `mixer::set_volume(float v)` expect **decibels** (`ma_volume_db_to_linear(v)`): `0.0` = unity (100% gain), `-6.0` ≈ 50% gain, `-100.0` = silent. Passing a linear `0.5` directly to `sound.volume` would actually amplify by `+0.5 dB` instead of halving volume!
- **Pan & Pitch Semantics**: With `PERCENTAGE_ATTRIBUTES`, `sound.pan` expects `-100.0` to `+100.0` (`pan_db_to_linear`), and `sound.pitch` expects percentage (`100.0` = normal playback speed, `97.0` = 3% lower).
- **`sound_pool.nvgt` Rough Edges Inspected**:
  1. `sound_pool_item::get_total_distance` (lines 165–212) casts coordinates (`listener_x`, `x`, ranges) to `int`, causing boundary/earshot distance checks to snap coarsely.
  2. `sound_pool_item::update_listener_position` (lines 155–158) applies `behind_pitch_decrease` to BOTH `true_pos.y < 0` (behind) AND `true_pos.z < 0` (below)! Applying pitch reduction to `z < 0` violates the modern rule forbidding pitch for elevation. Also, near-axis sources (`true_pos.y` close to `0.0`) can warble when crossing `0.0`.
  3. `sound_pool::play_extended` (line 321) only calls `handle.set_volume(start_volume)` when `start_volume < 0.0`.

### Decision & Rationale
- **Decision**: Vendor `C:\nvgt\include\sound_pool.nvgt` into `src/client/includes/sound_pool.nvgt` and patch it surgically:
  1. Preserve `float` precision in `get_total_distance` and `update_sound_3d(int slot, float x, float y, float z)` / `update_sounds_3d(string owner, float x, float y, float z)`.
  2. Apply `behind_pitch_decrease` (`3.0f` = 3% half-semitone) ONLY when `true_pos.y < -0.35f` (behind listener with axis deadzone), and NEVER on `true_pos.z < 0`.
  3. Design the entire client mix in intuitive linear gain `[0.0 .. 1.0]` across 7 `mixer@` layer objects (`Speech`, `Self`, `Threat`, `Actors`, `World`, `Ambience`, `Music`), converting once at the NVGT boundary via `linear_to_db(float gain)` (`gain <= 0.0001f ? -100.0f : clampf(20.0f * log10(gain), -100.0f, 0.0f)`).
  4. Enable `set_sound_global_hrtf(true)` for authentic binaural 3D spatialization, plus per-source `audio_low_pass_filter` on occluded world/player sounds behind walls or closed doors.
- **Alternatives Considered**: Writing a custom sound pool from scratch (rejected: `sound_pool.nvgt` already integrates `rotation.nvgt`, AABB ranges, persistence, and `sound` slot reuse) or switching to `king_audio_engine` (rejected: introduces external FMOD DLL redistribution/licensing dependencies when NVGT's built-in miniaudio + Steam Audio phonon HRTF + `audio_low_pass_filter` natively covers everything cleanly).

---

## 2. Rotation, Facing, & Relative Direction (`rotation.nvgt` + `compass.nvgt`)

### Findings
- `C:\nvgt\include\rotation.nvgt` uses `0° = North (+Y)`, increasing clockwise (`90° = East (+X)`), matching `sound_pool.nvgt`'s `rotation` parameter directly.
- `online-audio-game-dev/library/compass.nvgt` builds on `rotation.nvgt` and fixes `snapleft()`'s counterclockwise edge case (`snap_deg(3, 45, -1) == 0` instead of `315`), provides smooth turning `turn_smooth()`, and implements `describe_target(name, my_facing, mx, my, mz, tx, ty, tz, "steps")` with deliberate asymmetric relative buckets (`ahead`, `ahead and to your left/right`, `to your left/right`, `behind and to your left/right`, `behind you`).

### Decision & Rationale
- **Decision**: Copy `compass.nvgt` into `src/common/compass.nvgt` so server and client share identical degree rounding, unit vectors, and bearing math.
- **Alternatives Considered**: Rolling custom `atan2` math (rejected: risks 1-degree drift between client listener and server facing/hitboxes).

---

## 3. Networking, Channels, & Wire Safety (`network` + `wire.nvgt`)

### Findings from `nvgt_src/src/network.cpp`
- `network` wraps ENet natively: `setup_server(port, max_channels, max_peers)`, `setup_client(max_channels, max_peers)`, `connect(host, port)`, `send(peer_id, message, channel, reliable)`, `send_unreliable(peer_id, message, channel)`, `get_peer_average_round_trip_time(peer_id)`, `get_peer_address(peer_id)`, `receive_timeout_event = true`, `send_immediately = true`.
- ENet disconnects/timeouts emit `event_disconnect` / `event_disconnect_timeout` cleanly when `receive_timeout_event = true`.
- `wire.nvgt` provides single-pass `wire_escape()`, `wire_unescape()`, `split_keep_empty()`, `field()`, `safe_int()`, `safe_double()`, `sanitize_name()`, `name_is_valid()`, `names_match()`.

### Decision & Rationale
- **Decision**: Copy `wire.nvgt` into `src/common/wire.nvgt`. Use 6 ENet channels (`CH_SPEECH=0`, `CH_AUDIO=1`, `CH_CONTROL=2`, `CH_CHAT=3`, `CH_SNAPSHOT=4`, `CH_INPUT=5`). Scope unreliable `CH_SNAPSHOT` packets to within `EARSHOT_RADIUS` (35 tiles) + brief hysteresis so clients cannot inspect distant enemies/players. Enforce strict `MAX_UDP_PAYLOAD = 1350` bytes on all snapshots and map-sync chunks (splitting large map transfers into ordered reliable chunks on `CH_CONTROL`).
- **Alternatives Considered**: Binary packet serialization everywhere (rejected for v1: text pipe-delimited protocol with 2-decimal floats and compact opcodes keeps `CH_SNAPSHOT` well under 1,350 bytes for 15–30 nearby entities while making console packet tests inspectable).

---

## 4. Cryptography, Passwords, Tokens, & AppData Persistence

### Findings from `nvgt_src/src/hash.cpp`, `crypto.cpp`, `filesystem.cpp`, and `C:\nvgt\include\settings.nvgt`
- `string_hash_sha256(data, binary)` wraps Poco `SHA2Engine(SHA_256)`.
- `random_bytes(32)` calls OS CSPRNG (`rng_get_bytes`).
- `get_preferences_path(org, app)` / `DIRECTORY_PREFERENCES(org, app)` wraps `SDL_GetPrefPath()`, returning a guaranteed writable per-user directory (`%APPDATA%\WildlandsStudio\WildlandsOnline\`).
- `settings.nvgt` supports INI storage under AppData when `local_path = false`; storing values as strings avoids float-formatting corruption (`"100.000000"`).

### Decision & Rationale
- **Decision**:
  - Server hashes passwords with a per-account 16-byte random hex salt (`random_bytes(16)` hex-encoded) and `PBKDF_ROUNDS = 5000` stretched SHA-256 (`h = string_hash_sha256(salt + ":" + h)`), compared using a constant-time equality helper. Note honestly in `ACCOUNTS.md` that NVGT lacks native Argon2/bcrypt, so stretched salted SHA-256 is used.
  - Session tokens are generated with `random_bytes(32)` hex-encoded (64 chars), returned once to client, and stored as `string_hash_sha256(token)` on the server.
  - Client stores profile + keybinds + 8-slot LRU credential wallet in `DIRECTORY_PREFERENCES("WildlandsStudio", "WildlandsOnline") + "player.ini"`, saving immediately on every change and writing all 8 wallet slots on every save so signed-out entries cannot resurrect.
  - Server stores accounts (`data/accounts.dat` + `.bak`) and world structures (`data/world_objects.dat` + `.bak`) using atomic write-temp + backup + rename; corrupt account store at startup triggers `alert()` + fatal exit.

---

## 5. Forms, Menus, Buffers, Speech & Server Window

### Findings from `C:\nvgt\include\form.nvgt`, `menu.nvgt`, `speech.nvgt`, `UI.cpp`
- `audio_form` has built-in `create_input_box(..., password_mask)` which suppresses character/clipboard speech when `password_mask != ""`, plus `create_slider`, `create_checkbox`, `create_button`, `create_list`.
- `menu` supports wrap/edge/move/select/back/open sounds, first-letter nav, Ctrl+G index jump, Ctrl+F search, `background_callback` (vital so client continues pumping ENet while in pause/settings menus!).
- `buffers.nvgt` implements `BUF_ALL`, `BUF_CHAT`, `BUF_PM`, `BUF_SOCIAL`, `BUF_GAME`, `BUF_SYSTEM`.
- `screen_reader_speak()` + `tts_voice` handle screen-reader-first output with SAPI fallback.
- Server uses `show_window("Wildlands Online Server - Port " + port)` by default (with `--headless` optional), `get_COMMAND_LINE()` for `--port`, `--map`, `--bots`, `--test-mode`, `--allow-guests`, `--headless`, and `alert()` on fatal startup errors.

### Decision & Rationale
- **Decision**: Copy `buffers.nvgt` into `src/client/includes/buffers.nvgt`. Use `audio_form` for Registration, Login, Server Config, and Builder Property dialogs (never sequential `input_box()` prompts), and pump network keepalives in menu/form `background_callback` so players do not timeout while adjusting settings or browsing menus.

---

## 6. Real Verified Audio Asset Sourcing & Normalization

### Findings
- Python 3.11.9 (`requests`) and `ffmpeg 8.1` are installed and verified on this machine.
- OpenGameArt, Wikimedia Commons, and Kenney CC0 sound libraries provide high-quality real recordings (footsteps on grass/stone/wood/dirt/sand/water, campfire crackle, forest wind, river/water ambient, sword/axe/bow/arrow/impact sounds, animal calls/growls/pain, wooden door creaks/locks, hammer/saw building SFX, UI clicks).

### Decision & Rationale
- **Decision**: Build `tools/asset_pipeline.py` (using `nvgt-dev`'s byte verification + MD5 deduplication logic) to fetch verified CC0/open recordings into `sounds_raw/`, verify magic headers (`RIFF`/`OggS`/`fLaC`/`ID3`), deduplicate by MD5, transcode & loudness-normalize via `ffmpeg` (`44.1kHz`, `-16 LUFS` target / layer-balanced `.ogg` mono for 3D spatial sources, stereo for UI/ambience/music, silence-trimmed on one-shots so impacts trigger with zero latency!), write `sounds/manifest.txt` and `sounds/CREDITS.md`, and run `tools/asset_check.nvgt` to confirm 100% manifest coverage before shipping.
- **Note**: `sounds_raw/` stays excluded from final release / packed cleanly if desired while `sounds/` ships normalized `.ogg` assets.
