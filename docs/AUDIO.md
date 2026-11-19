# Audio Design & Mix Specification — Wildlands Online

## 1. Hard Rules (Engine-Verified for NVGT `0.90.0-dev`)
1. **Never use pitch for elevation or distance**: Height uses real `Z` passed to 3D positioning (`sound.set_position_3d`).
2. **NVGT Volume Boundary**: NVGT's default `g_audio_engine` uses `PERCENTAGE_ATTRIBUTES` (`sound.volume` and `mixer.volume` expect decibels `0.0..-100.0`, `sound.pitch` expects percentage `100.0`). All game code & settings operate in intuitive linear gain `[0.0 .. 1.0]` and convert once at the boundary via `linear_to_db(gain)`.
3. **Patched Float-Precision `sound_pool.nvgt`**: Vendored in `src/client/includes/sound_pool.nvgt` with float distance calculations (eliminating near-field pan stepping) and **behind-only** `behind_pitch_decrease = 3.0` (`true_pos.y < -0.35`, never `z < 0`).
4. **Listener First, Then Sources**: Every client frame updates listener `(x, y, z, facing)` before updating spatialized pool/entity slots.
5. **Wall Occlusion**: When line-of-sight between listener and a world/actor sound crosses a closed wall or closed door, apply an `audio_low_pass_filter` (cutoff ~`750 Hz`) and `-6 dB` attenuation.
6. **Real Recordings Only**: Zero synthesized sine-wave/beep placeholders. Every sound is sourced from real CC0/permissive audio, byte-verified, deduplicated, loudness-normalized via `ffmpeg`, and checked at startup against `sounds/manifest.txt`.

## 2. Seven-Layer Priority Mix & Ducking

| Priority | Layer | Mixer Gain Default | Contents | Ducking Behavior |
|---|---|---|---|---|
| 1 | **Speech** | `1.0` | Screen reader / TTS announcements | Ducks Threat/World/Ambience/Music lightly (`-3 dB`) while speaking if enabled |
| 2 | **Self** | `0.85` | Own footsteps, heartbeat, shiver, stomach, inventory clicks, UI cues | Never occluded |
| 3 | **Threat** | `0.80` | Predator growls, attack windups, incoming arrows, combat hits | Cuts through World/Ambience |
| 4 | **Actors** | `0.65` | Other players' footsteps, swings, building, chatter cues | 3D spatial + occluded |
| 5 | **World** | `0.60` | Doors, wood chopping, mining, campfires, chests, falling trees | 3D spatial + occluded |
| 6 | **Ambience** | `0.30` | Zone forest wind, river flow, rain, night crickets | Looping, smooth crossfade |
| 7 | **Music** | `0.35` | Optional menu/wilderness theme (off-able) | Ducks lowest |

## 3. Required Asset Catalog (`sounds/`)
- **ui/**: `menu_move`, `menu_select`, `menu_back`, `menu_wrap`, `menu_edge`, `menu_open`, `inv_open`, `inv_close`, `slider_tick`, `error`, `key_click`, `key_backspace`, `chat_open`, `chat_close`, `chat_send`, `msg_chat`, `msg_pm`, `msg_social`, `notify_friend`
- **steps/**: `grass_1..3`, `dirt_1..3`, `stone_1..3`, `wood_1..3`, `sand_1..3`, `water_1..3`, `jump`, `land_soft`, `land_hard`, `wall_bump_wood`, `wall_bump_stone`
- **survival/**: `chop_wood`, `tree_fall`, `mine_stone`, `forage_berry`, `water_scoop`, `drink`, `eat`, `bandage`, `craft_ok`, `campfire_ignite`, `campfire_loop`, `heartbeat`, `shiver`
- **builder/**: `build_place`, `build_repair`, `build_break`, `door_open`, `door_close`, `door_locked`, `chest_open`, `chest_close`, `beacon_ping`
- **combat/**: `swing_melee`, `hit_flesh`, `hit_block`, `whiff`, `bow_draw`, `bow_release`, `arrow_fly`, `hurt`, `death`, `respawn`, `duel_start`
- **wildlife/**: `wolf_growl`, `wolf_attack`, `wolf_hurt`, `bear_roar`, `deer_call`, `rabbit_rustle`
- **ambience/**: `forest_day`, `forest_night`, `river_loop`, `rain_loop`, `settlement_hearth`, `wind_gust`
- **multi/**: `player_join`, `player_leave`, `connect_ok`, `disconnect`, `level_up`, `countdown_tick`
- **music/**: `menu_theme` (calm acoustic ambient loop, CC0)
