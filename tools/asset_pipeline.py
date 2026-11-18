#!/usr/bin/env python3
"""
Wildlands Online — Real Verified Audio Asset Pipeline.
Downloads CC0 / open-licensed recordings from verified public sources,
validates genuine audio magic headers, deduplicates by MD5, trims silence
and normalizes loudness via ffmpeg into client/sounds/*.ogg, and emits
client/sounds/manifest.txt and client/sounds/CREDITS.md.

Strictly NO synthesized placeholder tones.
"""

import hashlib
import os
import shutil
import subprocess
import sys
import urllib.parse
import zipfile
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(ROOT, "tools", "_audio_cache")
OUT_DIR = os.path.join(ROOT, "client", "sounds")
MANIFEST_PATH = os.path.join(OUT_DIR, "manifest.txt")
CREDITS_PATH = os.path.join(OUT_DIR, "CREDITS.md")

FFMPEG = shutil.which("ffmpeg") or (
    r"C:\Users\LCBoy\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.EXE"
)

AUDIO_MAGIC_BYTES = (b"RIFF", b"OggS", b"fLaC", b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")

KENNEY_IF_BASE = "https://raw.githubusercontent.com/Calinou/kenney-interface-sounds/master/addons/kenney_interface_sounds/"
KENNEY_UI_BASE = "https://raw.githubusercontent.com/Calinou/kenney-ui-audio/master/addons/kenney_ui_audio/"
KENNEY_RPG_BASE = "https://raw.githubusercontent.com/Boyquotes/kenney-rpg-audio-for-godot/main/addons/kenney%20rpg%20audio/"
KENNEY_IMP_BASE = "https://raw.githubusercontent.com/Boyquotes/kenney-impact-sounds-for-godot/main/addons/kenney%20impact%20sounds/"

OGA_ZIPS = {
    "rpg_sound_pack": "https://opengameart.org/sites/default/files/rpg_sound_pack.zip",
    "100_cc0_sfx": "https://opengameart.org/sites/default/files/100-CC0-SFX_0.zip",
    "water_sfx": "https://opengameart.org/sites/default/files/water-splash-slime-sfx.zip",
    "creature_sfx": "https://opengameart.org/sites/default/files/80-CC0-creature-SFX_0.zip",
    "swishes": "https://opengameart.org/sites/default/files/swishes.zip",
}

WIKI_URLS = {
    "campfire_sound_ambience.ogg": "https://upload.wikimedia.org/wikipedia/commons/b/b1/Campfire_sound_ambience.ogg",
    "river_stony.ogg": "https://upload.wikimedia.org/wikipedia/commons/2/21/Shallow_small_river_with_stony_riverbed.ogg",
    "bear_growl.ogg": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Bear_growl.ogg",
    "wolf_howls.ogg": "https://upload.wikimedia.org/wikipedia/commons/8/87/Wolf_howls.ogg",
    "barking_deer.ogg": "https://upload.wikimedia.org/wikipedia/commons/3/36/Barking_deer.ogg",
    "field_cricket.ogg": "https://upload.wikimedia.org/wikipedia/commons/0/0d/Field_cricket_unedited.ogg",
    "gentle_breeze.ogg": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Gentle_breeze_and_birds_singing.ogg",
    "heartbeat_speedsup.wav": "https://upload.wikimedia.org/wikipedia/commons/9/9b/Heartbeat_speedsup.wav",
    "just_as_soon.mp3": "https://upload.wikimedia.org/wikipedia/commons/7/73/Just_As_Soon_%28ISRC_USUAN1100185%29.mp3",
}

# Tuple: (target_rel_path, source_spec, channels, lufs, trim_silence, loop_max_sec, credit_note)
ASSETS = [
    # UI (stereo, crisp, -16 LUFS)
    ("ui/menu_move.ogg", ("url", KENNEY_IF_BASE + "tick_001.wav"), 2, -16, True, 0, "Kenney Interface Sounds (CC0)"),
    ("ui/menu_select.ogg", ("url", KENNEY_IF_BASE + "confirmation_001.wav"), 2, -15, True, 0, "Kenney Interface Sounds (CC0)"),
    ("ui/menu_back.ogg", ("url", KENNEY_IF_BASE + "back_001.wav"), 2, -16, True, 0, "Kenney Interface Sounds (CC0)"),
    ("ui/menu_wrap.ogg", ("url", KENNEY_IF_BASE + "switch_004.wav"), 2, -16, True, 0, "Kenney Interface Sounds (CC0)"),
    ("ui/menu_edge.ogg", ("url", KENNEY_IF_BASE + "drop_002.wav"), 2, -16, True, 0, "Kenney Interface Sounds (CC0)"),
    ("ui/menu_open.ogg", ("url", KENNEY_IF_BASE + "open_002.wav"), 2, -16, True, 0, "Kenney Interface Sounds (CC0)"),
    ("ui/slider_tick.ogg", ("url", KENNEY_IF_BASE + "click_003.wav"), 2, -16, True, 0, "Kenney Interface Sounds (CC0)"),
    ("ui/error.ogg", ("url", KENNEY_IF_BASE + "error_004.wav"), 2, -15, True, 0, "Kenney Interface Sounds (CC0)"),
    ("ui/key_click.ogg", ("url", KENNEY_UI_BASE + "click1.wav"), 2, -19, True, 0, "Kenney UI Audio (CC0)"),
    ("ui/key_backspace.ogg", ("url", KENNEY_UI_BASE + "click4.wav"), 2, -19, True, 0, "Kenney UI Audio (CC0)"),
    ("ui/chat_open.ogg", ("url", KENNEY_IF_BASE + "maximize_004.wav"), 2, -16, True, 0, "Kenney Interface Sounds (CC0)"),
    ("ui/chat_close.ogg", ("url", KENNEY_IF_BASE + "minimize_004.wav"), 2, -16, True, 0, "Kenney Interface Sounds (CC0)"),
    ("ui/chat_send.ogg", ("url", KENNEY_IF_BASE + "select_004.wav"), 2, -16, True, 0, "Kenney Interface Sounds (CC0)"),
    ("ui/msg_chat.ogg", ("url", KENNEY_IF_BASE + "pluck_001.wav"), 2, -16, True, 0, "Kenney Interface Sounds (CC0)"),
    ("ui/msg_pm.ogg", ("zip", "100_cc0_sfx/bell_01.ogg"), 2, -15, True, 0, "100 CC0 SFX by rubberduck (CC0)"),
    ("ui/msg_social.ogg", ("url", KENNEY_IF_BASE + "confirmation_003.wav"), 2, -15, True, 0, "Kenney Interface Sounds (CC0)"),
    ("ui/notify_friend.ogg", ("url", KENNEY_IF_BASE + "bong_001.wav"), 2, -15, True, 0, "Kenney Interface Sounds (CC0)"),
    ("ui/sonar_ping.ogg", ("url", KENNEY_IF_BASE + "glass_001.wav"), 1, -15, True, 0, "Kenney Interface Sounds (CC0)"),

    # Footsteps & Movement (mono for pure 3D spatialization, zero leading silence)
    ("steps/grass_1.ogg", ("url", KENNEY_IMP_BASE + "footstep_grass_000.ogg"), 1, -16, True, 0, "Kenney Impact Sounds (CC0)"),
    ("steps/grass_2.ogg", ("url", KENNEY_IMP_BASE + "footstep_grass_001.ogg"), 1, -16, True, 0, "Kenney Impact Sounds (CC0)"),
    ("steps/grass_3.ogg", ("url", KENNEY_IMP_BASE + "footstep_grass_002.ogg"), 1, -16, True, 0, "Kenney Impact Sounds (CC0)"),
    ("steps/dirt_1.ogg", ("url", KENNEY_RPG_BASE + "footstep_0.ogg"), 1, -16, True, 0, "Kenney RPG Audio (CC0)"),
    ("steps/dirt_2.ogg", ("url", KENNEY_RPG_BASE + "footstep_1.ogg"), 1, -16, True, 0, "Kenney RPG Audio (CC0)"),
    ("steps/dirt_3.ogg", ("url", KENNEY_RPG_BASE + "footstep_2.ogg"), 1, -16, True, 0, "Kenney RPG Audio (CC0)"),
    ("steps/stone_1.ogg", ("url", KENNEY_IMP_BASE + "footstep_concrete_000.ogg"), 1, -16, True, 0, "Kenney Impact Sounds (CC0)"),
    ("steps/stone_2.ogg", ("url", KENNEY_IMP_BASE + "footstep_concrete_001.ogg"), 1, -16, True, 0, "Kenney Impact Sounds (CC0)"),
    ("steps/stone_3.ogg", ("url", KENNEY_IMP_BASE + "footstep_concrete_002.ogg"), 1, -16, True, 0, "Kenney Impact Sounds (CC0)"),
    ("steps/wood_1.ogg", ("url", KENNEY_IMP_BASE + "footstep_wood_000.ogg"), 1, -16, True, 0, "Kenney Impact Sounds (CC0)"),
    ("steps/wood_2.ogg", ("url", KENNEY_IMP_BASE + "footstep_wood_001.ogg"), 1, -16, True, 0, "Kenney Impact Sounds (CC0)"),
    ("steps/wood_3.ogg", ("url", KENNEY_IMP_BASE + "footstep_wood_002.ogg"), 1, -16, True, 0, "Kenney Impact Sounds (CC0)"),
    ("steps/sand_1.ogg", ("url", KENNEY_IMP_BASE + "footstep_snow_000.ogg"), 1, -16, True, 0, "Kenney Impact Sounds (CC0)"),
    ("steps/sand_2.ogg", ("url", KENNEY_IMP_BASE + "footstep_snow_001.ogg"), 1, -16, True, 0, "Kenney Impact Sounds (CC0)"),
    ("steps/sand_3.ogg", ("url", KENNEY_IMP_BASE + "footstep_snow_002.ogg"), 1, -16, True, 0, "Kenney Impact Sounds (CC0)"),
    ("steps/water_1.ogg", ("zip", "water_sfx/splash_01.ogg"), 1, -16, True, 0, "40 CC0 Water Splash SFX by rubberduck (CC0)"),
    ("steps/water_2.ogg", ("zip", "water_sfx/splash_02.ogg"), 1, -16, True, 0, "40 CC0 Water Splash SFX by rubberduck (CC0)"),
    ("steps/water_3.ogg", ("zip", "water_sfx/splash_03.ogg"), 1, -16, True, 0, "40 CC0 Water Splash SFX by rubberduck (CC0)"),
    ("steps/jump.ogg", ("zip", "rpg_sound_pack/RPG Sound Pack/inventory/cloth.wav"), 1, -16, True, 0, "RPG Sound Pack by artisticdude (CC0)"),
    ("steps/land_soft.ogg", ("url", KENNEY_IMP_BASE + "impact_soft_medium_000.ogg"), 1, -15, True, 0, "Kenney Impact Sounds (CC0)"),
    ("steps/land_hard.ogg", ("url", KENNEY_IMP_BASE + "impact_soft_heavy_001.ogg"), 1, -14, True, 0, "Kenney Impact Sounds (CC0)"),
    ("steps/wall_bump_wood.ogg", ("url", KENNEY_IMP_BASE + "impact_wood_heavy_000.ogg"), 1, -15, True, 0, "Kenney Impact Sounds (CC0)"),
    ("steps/wall_bump_stone.ogg", ("url", KENNEY_IMP_BASE + "impact_punch_heavy_002.ogg"), 1, -15, True, 0, "Kenney Impact Sounds (CC0)"),

    # Survival & Gathering (mono 3D except self cues)
    ("survival/chop_wood.ogg", ("url", KENNEY_RPG_BASE + "chop.ogg"), 1, -14, True, 0, "Kenney RPG Audio (CC0)"),
    ("survival/tree_fall.ogg", ("zip", "100_cc0_sfx/slam_05.ogg"), 1, -14, True, 0, "100 CC0 SFX by rubberduck (CC0)"),
    ("survival/mine_stone.ogg", ("url", KENNEY_IMP_BASE + "impact_mining_000.ogg"), 1, -14, True, 0, "Kenney Impact Sounds (CC0)"),
    ("survival/forage_berry.ogg", ("zip", "rpg_sound_pack/RPG Sound Pack/inventory/cloth-heavy.wav"), 1, -15, True, 0, "RPG Sound Pack (CC0)"),
    ("survival/water_scoop.ogg", ("zip", "water_sfx/splash_07.ogg"), 1, -15, True, 0, "40 CC0 Water Splash SFX by rubberduck (CC0)"),
    ("survival/drink.ogg", ("zip", "rpg_sound_pack/RPG Sound Pack/inventory/bubble2.wav"), 1, -15, True, 0, "RPG Sound Pack (CC0)"),
    ("survival/eat.ogg", ("zip", "creature_sfx/eat_01.ogg"), 1, -15, True, 0, "80 CC0 Creature SFX by rubberduck (CC0)"),
    ("survival/bandage.ogg", ("url", KENNEY_RPG_BASE + "cloth_2.ogg"), 1, -15, True, 0, "Kenney RPG Audio (CC0)"),
    ("survival/craft_ok.ogg", ("zip", "100_cc0_sfx/tools_02.ogg"), 1, -15, True, 0, "100 CC0 SFX by rubberduck (CC0)"),
    ("survival/campfire_ignite.ogg", ("zip", "100_cc0_sfx/tools_04.ogg"), 1, -15, True, 0, "100 CC0 SFX by rubberduck (CC0)"),
    ("survival/campfire_loop.ogg", ("url", "https://opengameart.org/sites/default/files/fire.wav"), 1, -18, False, 12, "Fireplace Sound Loop by PagDev (CC0)"),
    ("survival/heartbeat.ogg", ("wiki", "heartbeat_speedsup.wav"), 1, -15, True, 1.4, "Wikimedia Commons Heartbeat (CC BY 4.0)"),
    ("survival/shiver.ogg", ("zip", "creature_sfx/breath.ogg"), 1, -16, True, 0, "80 CC0 Creature SFX by rubberduck (CC0)"),

    # Builder & World Structures (mono 3D)
    ("builder/build_place.ogg", ("zip", "100_cc0_sfx/wooden_02.ogg"), 1, -14, True, 0, "100 CC0 SFX by rubberduck (CC0)"),
    ("builder/build_repair.ogg", ("zip", "100_cc0_sfx/tools_01.ogg"), 1, -14, True, 0, "100 CC0 SFX by rubberduck (CC0)"),
    ("builder/build_break.ogg", ("url", KENNEY_IMP_BASE + "impact_plank_medium_001.ogg"), 1, -14, True, 0, "Kenney Impact Sounds (CC0)"),
    ("builder/door_open.ogg", ("url", KENNEY_RPG_BASE + "door_open_1.ogg"), 1, -15, True, 0, "Kenney RPG Audio (CC0)"),
    ("builder/door_close.ogg", ("url", KENNEY_RPG_BASE + "door_close_1.ogg"), 1, -15, True, 0, "Kenney RPG Audio (CC0)"),
    ("builder/door_locked.ogg", ("url", KENNEY_RPG_BASE + "metal_latch.ogg"), 1, -15, True, 0, "Kenney RPG Audio (CC0)"),
    ("builder/chest_open.ogg", ("zip", "100_cc0_sfx/wooded_box_open.ogg"), 1, -15, True, 0, "100 CC0 SFX by rubberduck (CC0)"),
    ("builder/chest_close.ogg", ("zip", "100_cc0_sfx/wooden_01.ogg"), 1, -15, True, 0, "100 CC0 SFX by rubberduck (CC0)"),
    ("builder/beacon_ping.ogg", ("zip", "100_cc0_sfx/bell_02.ogg"), 1, -16, True, 0, "100 CC0 SFX by rubberduck (CC0)"),

    # Combat (mono 3D)
    ("combat/swing_melee.ogg", ("zip", "swishes/swishes/swish-3.wav"), 1, -14, True, 0, "Swishes Sound Pack by artisticdude (CC0)"),
    ("combat/hit_flesh.ogg", ("zip", "100_cc0_sfx/hit_02.ogg"), 1, -14, True, 0, "100 CC0 SFX by rubberduck (CC0)"),
    ("combat/hit_block.ogg", ("url", KENNEY_IMP_BASE + "impact_metal_heavy_001.ogg"), 1, -14, True, 0, "Kenney Impact Sounds (CC0)"),
    ("combat/whiff.ogg", ("zip", "swishes/swishes/swish-7.wav"), 1, -15, True, 0, "Swishes Sound Pack by artisticdude (CC0)"),
    ("combat/bow_draw.ogg", ("url", KENNEY_RPG_BASE + "creak_1.ogg"), 1, -15, True, 0, "Kenney RPG Audio (CC0)"),
    ("combat/bow_release.ogg", ("url", "https://opengameart.org/sites/default/files/shoot.ogg"), 1, -14, True, 0, "Bow Arrow Shot OGA (CC-BY-SA)"),
    ("combat/arrow_fly.ogg", ("zip", "swishes/swishes/swish-11.wav"), 1, -15, True, 0, "Swishes Sound Pack by artisticdude (CC0)"),
    ("combat/hurt.ogg", ("zip", "creature_sfx/hurt_01.ogg"), 1, -14, True, 0, "80 CC0 Creature SFX by rubberduck (CC0)"),
    ("combat/death.ogg", ("zip", "creature_sfx/hurt_05.ogg"), 1, -14, True, 0, "80 CC0 Creature SFX by rubberduck (CC0)"),
    ("combat/respawn.ogg", ("zip", "rpg_sound_pack/RPG Sound Pack/battle/magic1.wav"), 1, -15, True, 0, "RPG Sound Pack (CC0)"),
    ("combat/duel_start.ogg", ("zip", "100_cc0_sfx/gong_01.ogg"), 1, -14, True, 0, "100 CC0 SFX by rubberduck (CC0)"),

    # Wildlife (mono 3D)
    ("wildlife/wolf_growl.ogg", ("zip", "rpg_sound_pack/RPG Sound Pack/NPC/misc/wolfman.wav"), 1, -15, True, 0, "RPG Sound Pack (CC0)"),
    ("wildlife/wolf_howl.ogg", ("wiki", "wolf_howls.ogg"), 1, -16, True, 3.0, "Wikimedia Commons Wolf Howls (Public Domain)"),
    ("wildlife/wolf_attack.ogg", ("zip", "creature_sfx/barking_01.ogg"), 1, -14, True, 0, "80 CC0 Creature SFX by rubberduck (CC0)"),
    ("wildlife/wolf_hurt.ogg", ("zip", "creature_sfx/hurt_02.ogg"), 1, -15, True, 0, "80 CC0 Creature SFX by rubberduck (CC0)"),
    ("wildlife/bear_roar.ogg", ("wiki", "bear_growl.ogg"), 1, -14, True, 3.0, "Wikimedia Commons Bear Growl (CC BY 3.0)"),
    ("wildlife/deer_call.ogg", ("wiki", "barking_deer.ogg"), 1, -16, True, 2.5, "Wikimedia Commons Barking Deer (CC BY-SA 2.5)"),
    ("wildlife/rabbit_rustle.ogg", ("zip", "creature_sfx/cute_03.ogg"), 1, -16, True, 0, "80 CC0 Creature SFX by rubberduck (CC0)"),

    # Ambience (looping environmental beds)
    ("ambience/forest_day.ogg", ("url", "https://opengameart.org/sites/default/files/Forest_Ambience.mp3"), 2, -20, False, 20, "Forest Ambience by TinyWorlds (CC0)"),
    ("ambience/forest_night.ogg", ("wiki", "field_cricket.ogg"), 2, -20, False, 15, "Wikimedia Commons Field Cricket (CC BY-SA 3.0)"),
    ("ambience/river_loop.ogg", ("wiki", "river_stony.ogg"), 1, -19, False, 15, "Wikimedia Commons Stony River (Public Domain)"),
    ("ambience/rain_loop.ogg", ("zip", "water_sfx/loop_rain.ogg"), 2, -20, False, 12, "40 CC0 Water Splash SFX by rubberduck (CC0)"),
    ("ambience/settlement_hearth.ogg", ("wiki", "campfire_sound_ambience.ogg"), 1, -19, False, 15, "Wikimedia Commons Campfire Ambience (CC BY 3.0)"),
    ("ambience/wind_gust.ogg", ("wiki", "gentle_breeze.ogg"), 2, -20, False, 15, "Wikimedia Commons Gentle Breeze (Public Domain)"),

    # Multiplayer Notifications (stereo UI/world cues)
    ("multi/player_join.ogg", ("zip", "100_cc0_sfx/bell_03.ogg"), 2, -16, True, 0, "100 CC0 SFX by rubberduck (CC0)"),
    ("multi/player_leave.ogg", ("url", KENNEY_IF_BASE + "close_004.wav"), 2, -16, True, 0, "Kenney Interface Sounds (CC0)"),
    ("multi/connect_ok.ogg", ("url", KENNEY_IF_BASE + "confirmation_002.wav"), 2, -15, True, 0, "Kenney Interface Sounds (CC0)"),
    ("multi/disconnect.ogg", ("url", KENNEY_IF_BASE + "error_002.wav"), 2, -15, True, 0, "Kenney Interface Sounds (CC0)"),
    ("multi/level_up.ogg", ("zip", "100_cc0_sfx/gong_02.ogg"), 2, -15, True, 0, "100 CC0 SFX by rubberduck (CC0)"),
    ("multi/countdown_tick.ogg", ("url", KENNEY_IF_BASE + "tick_002.wav"), 2, -16, True, 0, "Kenney Interface Sounds (CC0)"),

    # Music (calm acoustic theme, gently mastered)
    ("music/menu_theme.ogg", ("wiki", "just_as_soon.mp3"), 2, -21, False, 45, "Just As Soon by Kevin MacLeod / Incompetech (CC BY 3.0)"),
]


def verify_audio_magic(path: str) -> bool:
    with open(path, "rb") as f:
        head = f.read(16)
    return any(head.startswith(m) for m in AUDIO_MAGIC_BYTES)


def file_md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def ensure_download(session: requests.Session, url: str, dest: str) -> None:
    if os.path.exists(dest) and os.path.getsize(dest) > 128:
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    r = session.get(url, timeout=60)
    r.raise_for_status()
    ct = r.headers.get("Content-Type", "").lower()
    if "text/html" in ct:
        raise RuntimeError(f"URL returned HTML instead of media: {url}")
    with open(dest, "wb") as f:
        f.write(r.content)


def ensure_archives(session: requests.Session) -> None:
    for key, url in OGA_ZIPS.items():
        zpath = os.path.join(CACHE_DIR, f"{key}.zip")
        edir = os.path.join(CACHE_DIR, key)
        ensure_download(session, url, zpath)
        if not os.path.exists(edir):
            with zipfile.ZipFile(zpath, "r") as z:
                z.extractall(edir)


def resolve_source(session: requests.Session, spec: tuple) -> str:
    kind, val = spec
    if kind == "zip":
        src = os.path.join(CACHE_DIR, *val.split("/"))
        if not os.path.exists(src):
            raise FileNotFoundError(f"Missing extracted zip entry: {src}")
        return src
    if kind == "wiki":
        dst = os.path.join(CACHE_DIR, "wiki", val)
        ensure_download(session, WIKI_URLS[val], dst)
        return dst
    if kind == "url":
        parsed = urllib.parse.urlparse(val)
        safe_name = hashlib.sha1(val.encode("utf-8")).hexdigest()[:10] + "_" + os.path.basename(urllib.parse.unquote(parsed.path))
        dst = os.path.join(CACHE_DIR, "direct", safe_name)
        ensure_download(session, val, dst)
        return dst
    raise ValueError(f"Unknown source kind: {kind}")


def transcode_ogg(src: str, dst: str, channels: int, lufs: float, trim: bool, max_sec: float) -> None:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    filters = []
    if trim:
        filters.append("silenceremove=start_periods=1:start_duration=0:start_threshold=-46dB")
    filters.append(f"loudnorm=I={lufs}:TP=-1.5:LRA=11")
    cmd = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", src]
    if max_sec > 0:
        cmd += ["-t", str(max_sec)]
    cmd += ["-ac", str(channels), "-ar", "44100", "-af", ",".join(filters), "-c:a", "libvorbis", "-q:a", "5", dst]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"ffmpeg failed for {src} -> {dst}: {res.stderr}")


def main() -> int:
    if not os.path.exists(FFMPEG):
        print(f"ERROR: ffmpeg not found at {FFMPEG}")
        return 1

    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": "WildlandsOnlineAssetPipeline/1.0 (+https://example.org)"})

    print("1. Ensuring OpenGameArt CC0 archives...")
    ensure_archives(session)

    seen_hashes = {}
    manifest_lines = []
    credit_lines = [
        "# Wildlands Online — Audio Asset Credits & Licenses",
        "",
        "All audio assets are real recordings from verified open-license sources, byte-verified, deduplicated, and normalized with ffmpeg.",
        "",
        "| Asset | License & Source |",
        "|---|---|",
    ]

    print(f"2. Processing {len(ASSETS)} audio assets...")
    for rel_path, spec, chans, lufs, trim, max_sec, credit in ASSETS:
        src = resolve_source(session, spec)
        if not verify_audio_magic(src):
            raise RuntimeError(f"Source failed magic-byte audio check: {src}")
        dst = os.path.join(OUT_DIR, *rel_path.split("/"))
        transcode_ogg(src, dst, chans, lufs, trim, max_sec)
        if not verify_audio_magic(dst):
            raise RuntimeError(f"Output failed magic-byte OggS check: {dst}")
        md5 = file_md5(dst)
        if md5 in seen_hashes:
            raise RuntimeError(f"Duplicate audio output detected: {rel_path} == {seen_hashes[md5]}")
        seen_hashes[md5] = rel_path
        manifest_lines.append(rel_path)
        credit_lines.append(f"| `{rel_path}` | {credit} |")
        print(f"  ok  {rel_path} ({os.path.getsize(dst)} bytes)")

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(manifest_lines) + "\n")
    with open(CREDITS_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(credit_lines) + "\n")

    print(f"DONE: {len(manifest_lines)} unique verified OGG assets written to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
