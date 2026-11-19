## quy tắc bắt buộc

luôn luôn tuân thủ quy trình specify trong mọi trường hợp phát triển

---

## Nhật ký kỹ thuật — Wildlands Online (Phiên 2026-11-18)

### 1. Kiến trúc & Phân tách thư mục
- **`common/`**: Mã dùng chung giữa server, client và công cụ kiểm tra:
  - `constants.nvgt`: Cấu hình cổng (`7100`), 6 kênh ENet (`CH_SPEECH..CH_INPUT`), 30 Hz simulation / 15 Hz snapshots, giới hạn UDP (`1350` bytes), phân cấp Rank (`Player..Developer`), 7 lớp âm thanh (`LAYER_SPEECH..LAYER_MUSIC`), 6 kênh buffer (`MBUF_*`).
  - `wire.nvgt` & `protocol.nvgt`: Escaping một lượt (`wire_escape`/`wire_unescape`), tách trường giữ rỗng (`split_keep_empty`), đọc trường an toàn (`field`), ép biên số (`safe_int`, `safe_double`, `fmt2`), lọc ký tự điều khiển (`strip_control_chars`).
  - `compass.nvgt`: Tọa độ 0° Bắc thuận chiều kim đồng hồ, `snap_deg` (45°/90°), `turn_smooth`, mô tả tương đối (`describe_target`), khoảng cách bước (`distance_words`).
  - `map.nvgt`: Parser/serializer `.map`, kiểm tra tính hợp lệ, lookup vùng/bề mặt (`grass`, `dirt`, `stone`, `wood`, `sand`, `water`), độ cao Z (platform/ramp), va chạm tường AABB và thuật toán ray-AABB occlusion (`segment_occluded`) cho tường tĩnh và cửa/tường người chơi xây (`dyn_occluders`).
  - `items.nvgt`: Bảng 26 vật phẩm, 18 công thức chế tạo, 8 loại công trình (`wood_wall`, `wood_door`, `wood_floor`, `wood_stairs`, `campfire`, `chest`, `craft_bench`, `beacon`), và 6 loài sinh vật/bot.
- **`server/`** (Máy chủ độc lập, đã biên dịch `server/server.exe`):
  - `server.nvgt`: Vòng lặp authoritative 30 Hz, CLI `--headless`, `--test-mode`, `--allow-guests`, `--port`, `--map`, `--bots`, `--wildlife`, `--data-dir`, tự động lưu theo chu kỳ, ân hạn reconnect 15 giây, snapshot giới hạn trong bán kính nghe (`EARSHOT_RADIUS=35.0`).
  - `includes/logger.nvgt`: Cửa sổ `audio_form` cho máy chủ có màn hình + xoay vòng file `logs/server.log`.
  - `includes/accounts.nvgt`: Xác thực SHA-256 5000 vòng có muối (`PBKDF_ROUNDS`), so sánh thời gian hằng (`constant_time_eq`), token CSPRNG 32 bytes, `devs.txt`, ghi file nguyên tử `.tmp` -> `.bak`.
  - `includes/world.nvgt`, `wildlife.nvgt`, `combat.nvgt`, `chat_social.nvgt`, `builder_srv.nvgt`, `admin_dev.nvgt`: Chu kỳ sinh tồn, thời tiết/ngày-đêm, AI động vật hoang dã & bot luyện tập, cận chiến/đỡ đòn/bắn cung, đấu tay đôi & khu vực an toàn, hệ thống Xây dựng Sinh tồn (cửa khóa được + cách âm, rương lưu trữ bền vững `world_objects.dat`) & Audio Map Builder (`F8`) lưu/reload `.map` nóng, bảng kiểm duyệt theo cấp bậc và bảng Dev điều khiển theo mục tiêu.
  - `maps/wildlands_valley.map`, `data/motd.txt`, `data/changelog.txt`, `data/devs.txt`.
- **`client/`** (Client độc lập, đã biên dịch `client/client.exe`):
  - `client.nvgt` & `includes/`:
    - `speech.nvgt`: Hỗ trợ `screen_reader_speak` + fallback `tts_voice`, lặp lại câu cuối (`repeat_last_spoken`), ducking khi phát thoại.
    - `profile.nvgt`: Lưu cài đặt dạng chuỗi trong AppData (`settings.ini`), danh sách chặn, phím tùy chỉnh (`keybinds`), ví lưu đăng nhập 8 slot LRU (`wallet.ini`) ghi đè nguyên tử.
    - `audio_engine.nvgt` & patched `sound_pool.nvgt`: 7 lớp mixer với quy đổi `linear_to_db`, Steam Audio HRTF, bộ lọc thông thấp `audio_low_pass_filter(750 Hz, order 2)` cho âm thanh bị che bởi tường/cửa đóng, crossfade môi trường ngày/đêm & mưa.
    - `buffers.nvgt`: 6 kênh lịch sử thông báo (`All`, `Chat`, `Messages`, `Social`, `Game`, `System`).
    - `ui_forms.nvgt`, `menus.nvgt`, `net_client.nvgt`, `chat_input.nvgt`, `radar_hud.nvgt`, `builder_ui.nvgt`, `tutorial.nvgt`: Đầy đủ UI đăng ký/đăng nhập/chọn server, Chat `/` đa chế độ, Radar quét `T` & Sonar `V`, Kho đồ/Chế tạo/Xây dựng/Rương đồ/Map Builder `F8`, Mixer 7 thanh trượt thử âm trực tiếp, Phím tắt tùy biến, Hướng dẫn tương tác có bước kiểm chứng thực tế, Mạng xã hội/Leaderboard/Kiểm duyệt/Dev.
- **`client/sounds/`**: 94 file âm thanh `.ogg` chuẩn (`OggS`) được `tools/asset_pipeline.py` tải từ nguồn mở CC0/permissive (Kenney, OpenGameArt, Wikimedia Commons, Kevin MacLeod), khử trùng lặp MD5, chuẩn hóa âm lượng và cắt khoảng lặng bằng `ffmpeg`, kèm `manifest.txt` và `CREDITS.md`.

### 2. Sửa lỗi thực tế phát hiện trong quá trình kiểm thử
- Sửa lỗi phân tích gói `INPUT` trong `server/server.nvgt` (đọc đúng `mask` và `facing` cho cả định dạng 2 và 3 tham số).
- Sửa lỗi `ClientProfile.save_settings`/`save_wallet` trong `client/includes/profile.nvgt`: gọi `create_section` trước `ini.set_string` (vì `ini.nvgt` không tự tạo section mới) và dùng dấu cách cho danh sách chặn.
- Sửa lỗi chỉ mục trường gói `MAP_HDR` trong `client/includes/net_client.nvgt` (lấy tổng số chunk ở trường thứ 6 thay vì nhầm sang `default_surface`).
- Đồng bộ tên `build_type` (VD `wood_door`) vs `_kit` ID (`wood_door_kit`) giữa client và server (`builder_srv.nvgt`, `builder_ui.nvgt`, `menus.nvgt`).
- Sửa thiếu ID rương trong gói `CHEST|put|oid|slot|qty` ở `client/includes/builder_ui.nvgt` và kiểm tra đúng `is_chest` trên server.
- Bổ sung hỗ trợ tham số mục tiêu cho `DEV|spawn_item` và `DEV|tp`, thêm `--data-dir` và tự động dò đường dẫn chạy từ `server/` hoặc thư mục gốc.
- Sửa lỗi `Null pointer access` lúc khởi động client (`ClientProfile::ClientProfile()` truy cập biến chuỗi toàn cục `LOCAL_SERVER_HOST` trước khi khởi tạo): đổi mặc định sang `"127.0.0.1"`, chuyển `g_profile` và `g_net` thành handle khởi tạo trong `main()`, đồng thời hỗ trợ tìm `../server/data/` khi xem News từ `client.exe` và thêm cờ `--smoke-test`.
- Sửa triệt để lỗi ENet timeout sau ~16 giây khi gõ lâu trong form Đăng ký/Đăng nhập (`ui_forms.nvgt` / `client.nvgt`): bổ sung `g_global_ui_pump` + `client_ui_pump()` giữ kết nối ENet (`PING|0` mỗi 2,5 giây), `ensure_auth_connection()` tự động kết nối lại nếu đứt + `net.flush()` tức thì, không để `menu.intro()` ngắt ngang lời thoại báo lỗi (`intro_interrupt = false`), và hỗ trợ phím `Enter` trên checkbox form.
- Sửa lỗi phân tích cấp bậc trong `WHO_RES` (`chat_social.nvgt` gửi `"" + other.rank` thay vì chuỗi chữ, `net_client.nvgt` hỗ trợ cả hai).
- Tạo thêm `tools/client_ui_e2e_check.nvgt` (test hồi quy 18 giây giữ form, auto-reconnect, token ví, buffers, radar/sonar, chat) và mở rộng `tools/net_integration_check.nvgt` kiểm tra đầy đủ vật lý nhảy/chạy nhanh/thể lực/dốc tháp canh, hái lượm, uống nước suối, chế tạo/nấu lửa trại, săn thú cận chiến/cung tên/nhặt chiến lợi phẩm, đỡ đòn/đấu tay đôi/hồi sinh, khóa cửa/sửa/phá hủy/rương đồ, chat phạm vi gần, bạn bè, chặn/bỏ chặn, kiểm duyệt và lưu bền vững qua khởi động lại.

### 3. Kết quả kiểm thử đã xác nhận (tất cả qua `tools/run_checks.ps1`)
- `common_check.nvgt`: PASS
- `map_check.nvgt`: PASS (map khởi đầu, ramp độ cao, va chạm, occlusion, chia chunk <= 1350B)
- `auth_check.nvgt`: PASS (băm SHA-256 5000 vòng, token rotation, phân cấp kiểm duyệt, khôi phục `.bak`, từ chối file hỏng)
- `asset_check.nvgt`: PASS (94 file `.ogg` hợp lệ, khớp đầy đủ với map & sinh vật)
- `client_profile_check.nvgt`: PASS (INI, keybind, blocklist, ví 8 slot LRU & xóa triệt để)
- Biên dịch `server/server.exe` và `client/client.exe`: Thành công, exit code 0
- `net_integration_check.nvgt` (Pha 1 & Pha 2 toàn bộ cơ chế gameplay qua server chạy thật ở cổng 7199): PASS toàn bộ
- `client/client.exe --smoke-test` (chạy thật E2E kết nối `server.exe` ở cổng 7199 + chế độ cửa sổ & audio engine): PASS toàn bộ
- `client_ui_e2e_check.nvgt` (trên server chế độ production ở cổng 7198, không `--test-mode`, test giữ kết nối 18 giây lúc gõ form, ví token, chat rate-limit, radar/buffers): PASS toàn bộ.


---

## Nhật ký kỹ thuật — Wildlands Online v2 (`002-staff-multimap-builder-tracking-verticality`, 2026-11-18)

### 1. Hệ thống Theo dõi STW 6 danh mục (`client/includes/tracker.nvgt`, `radar_hud.nvgt`, `profile.nvgt`)
- Loại bỏ hoàn toàn cơ chế quét `T` cũ (`collect_radar_targets` / `announce_radar_step`) và phím bind `"scanner"`.
- Xây dựng `StwTracker` với 6 danh mục: `All`, `Objects`, `Items`, `Animals`, `Structures`, `Players`.
- Danh sách duyệt chỉ hiển thị mục tiêu trong phạm vi **`<= 30` bước** (`TRACKER_MAX_DIST = 30.0`); khóa theo dõi giữ bán kính tối đa tới `EARSHOT_RADIUS = 35.0` trước khi báo mất dấu (`ui/track_lost.ogg`).
- Phím điều khiển mặc định (có thể map lại trong Settings): `Ctrl+=` / `Ctrl+-` chuyển danh mục, `=` / `-` duyệt mục kế tiếp/trước đó, `Backspace` bắt đầu theo dõi kèm radar 3D qua `sound_pool` (nhịp lặp 360ms/640ms/1050ms theo khoảng cách, không dùng pitch cho độ cao/khoảng cách), `Shift+Backspace` dừng theo dõi, `O` đọc hướng tương đối + số bước + chênh lệch độ cao.

### 2. Vật lý 3D Thực, Leo Cầu thang theo Âm bề mặt & Định luật Không khí / Vực thẳm
- Tách phím `PageUp` / `PageDown` khỏi hệ thống Buffer (Buffer chỉ còn dùng `,` / `.`), gán sang leo lên / xuống cầu thang (`IN_CLIMB_UP = 1 << 7`, `IN_CLIMB_DOWN = 1 << 8`, và `ACT|climb|up|down`).
- **Âm thanh cầu thang**: Khi leo hoặc xuống `MapPlatform` loại `"stairs"`, phát âm thanh bước chân đúng theo bề mặt mà builder đã chọn (`steps/<stair.surface>_1..3.ogg`: `grass`, `dirt`, `stone`, `wood`, `sand`, `water`, `carpet`) chứ không dùng âm thanh cầu thang riêng lẻ.
- **Định luật Không khí (`find_support_at`)**: Ngoài vùng có sàn/dốc/cầu thang đỡ (`Z` hỗ trợ `[MAP_MIN_Z=-50 .. MAP_MAX_Z=100]`) là Không khí rỗng. Trọng lực (`FALL_GRAVITY = 22.0`) kéo rơi kèm âm gió rơi (`steps/fall_air.ogg`); rơi `> 3.5` ô gây sát thương theo độ cao; rơi `>= 8.0` ô phát `combat/bone_break.ogg` và gây gãy xương 90 giây (chậm bước, cấm chạy nhanh — chữa bằng `bandage` hoặc `splint` Wooden Splint chế tạo từ 2 gỗ + 1 thảo mộc); rơi xuống nước sâu (`deep`) giảm 70% sát thương & chặn gãy xương kèm `steps/water_splash_big.ogg`; rơi xuống dưới `min_z - 6` chết vực và hồi sinh tại spawn; đứng dưới mái (`is_roof = 1`) tự làm dịu tiếng mưa.

### 3. Hệ thống Đa bản đồ & STW Map Builder `F8` (`common/map.nvgt`, `builder_srv.nvgt`, `builder_ui.nvgt`)
- Máy chủ (`PROTO_VERSION = 2`) quét và chạy đồng thời tất cả `server/maps/*.map` (`wildlands_valley.map` và `skywatch_citadel.map`) với snapshot, local chat, node tài nguyên, AI và âm thanh tách riêng theo `MapInstance`, liên thông qua **Cổng dịch chuyển (`D`)**.
- Menu Builder **`F8`** (`run_map_builder_hub`):
  - **Create New Map**: Form đa trường tạo map mới (`slug`, tên hiển thị, chiều rộng/dài, `min_z..max_z`, bề mặt mặc định, nhạc nền, điểm spawn, tùy chọn tạo sàn nền).
  - **Switch / Edit Header / Delete Map**: Chuyển map chỉnh sửa hoặc dịch chuyển tới spawn, sửa header `M`, xóa map có sao lưu `.deleted.bak`.
  - **6-Axis Box Coordinate Forms**: Nhập trực tiếp `Minimum X, Maximum X, Minimum Y, Maximum Y, Minimum Z, Maximum Z` cho `floor/roof`, `stairs`, `ramp`, `wall`, `zone`, `water`, `hazard`, `portal`, `resource`, `emitter` (có nút nghe thử âm), `spawn`.
  - **Line Manager**: Lọc theo loại (`ALL`, `M`, `FLOOR`, `STAIRS`, `P`, `W`, `Z`, `L`, `H`, `D`, `R`, `A`, `S`), sửa bằng form 6 trục hoặc sửa dòng thô, chèn mới, nhân bản, đổi thứ tự lên/xuống, dịch chuyển tới tâm phần tử, xóa, kèm **Undo** 25 bước/map, **Validate**, **Save** (`.bak`) và **Hot-Reload**.

### 4. Staff Panel Phân danh mục `F9` & Vòng đời Server (`accounts.nvgt`, `admin_dev.nvgt`, `staff_ui.nvgt`)
- Nâng cấp `ACCOUNTS_V2` (`current_map`, `created_at_epoch`, `last_seen_epoch`, `last_ip`) tương thích ngược `ACCOUNTS_V1`, kèm kho lưu báo cáo `reports.dat` + `.bak`.
- **`F9` Staff Panel** không cần gõ lệnh thô:
  - **Account Directory**: Sắp xếp Online trước, hiển thị **`Online (<Map>, <Zone>)`** cho người đang chơi và **`Last seen: <relative> (<YYYY-MM-DD HH:MM UTC+07:00>)`** cho tài khoản offline; menu hành động trực tiếp từng mục tiêu (`tp_to`, `bring`, `move_map`, `heal`, `give_item`, `clear_inv`, `rescue`, `kick`, `mute`, `ban`, `unban`, `set_rank`, `clear_token`).
  - **Developer Lifecycle** (`RANK_DEV` + `devs.txt`): Đếm ngược **Shutdown** / **Restart** (`--bind-delay-ms` đóng ENet rồi khởi chạy lại bằng `run()`), hủy đếm ngược, khóa **Maintenance Mode**, bật/tắt **Guest**, sửa nóng `motd.txt` & `changelog.txt`.
  - **World / Spawner / Telemetry / Logs / Reports**: Điều khiển thời tiết/ngày đêm/thả quái & bot, xem log từ bộ đệm vòng nhớ, đọc & xử lý `/report` và chat nội bộ `/sc`.

### 5. Âm thanh, Tài liệu & Kết quả Kiểm thử Xác thực (`tools/run_checks.ps1`)
- Bổ sung 22 file `.ogg` CC0 thật qua `tools/asset_pipeline.py` (tổng **116** file hợp lệ, tất cả đều có header `OggS`).
- Bổ sung [BUILDER_GUIDE.md](file:///C:/Users/LCBoy/Desktop/data/stw/docs/BUILDER_GUIDE.md) và [STAFF_GUIDE.md](file:///C:/Users/LCBoy/Desktop/data/stw/docs/STAFF_GUIDE.md) (đọc được trực tiếp trong Pause Menu), cùng cập nhật `CONTROLS.md`, `PROTOCOL.md`, `ARCHITECTURE.md`, `PLAN.md`.
- Biên dịch sạch `server/server.exe` và `client/client.exe` bằng `nvgt -c` và xác nhận **`=== ALL CHECKS PASSED ===`** qua `tools/run_checks.ps1` (exit code 0 across offline unit tests, build, Phase 1/2 E2E integration gồm leo cầu thang âm gỗ, rơi từ Z=12 gãy xương chữa bằng Wooden Splint, cổng đa bản đồ sang `skywatch_citadel`, Builder `F8` + Line Manager, Staff `Online`/`Last seen` + `/report` + `/sc` + graceful shutdown, `client.exe --smoke-test`, và `client_ui_e2e_check.nvgt` với STW Tracker `<= 30`).


---

## Nhật ký kỹ thuật — Wildlands Online v3 (`003-stw-maps-system`, 2026-11-18)

### 1. Hệ thống Spawn Động vật theo từng Bản đồ (`E` Animal Spawn Zone — Phương án A)
- **Gỡ bỏ hoàn toàn Spawner toàn cục**: Xóa `wildlife_set_target_count` tự động thả quái trên mọi map trong `server/includes/wildlife.nvgt`, xóa mục spawn & đặt số lượng động vật khỏi Staff Panel (`client/includes/staff_ui.nvgt`, `STAFF|spawn_mob`, `STAFF|world|wildlife`) và Dev Console (`client/includes/menus.nvgt`, `DEV|set_wildlife`), giữ `wildlife_set_bot_count` riêng cho practice bots. Các map test (`skywatch_citadel.map`, `anhloc.map`, map tạo mới) hoàn toàn yên bình (0 động vật) trừ khi được thêm dòng `E`.
- **Cơ chế Timer `ms` dùng chung (Approach A)** & Danh sách loài **100% động** từ `g_species`:
  - `common/map.nvgt` thêm lớp `MapAnimalSpawn` (`E|label|min_x|min_y|max_x|max_y|min_z|max_z|interval_ms|count|species_csv|leash|active_time`), validator từ chối dòng `E` rỗng loài, cùng `make_e_line`, `parse_species_csv`, `join_species_csv`.
  - Server gửi động toàn bộ catalog sinh vật từ `g_species` qua gói `BM_SPECIES` mỗi lần mở `F8` (`builder_send_hub_sync`).
  - Client (`client/includes/builder_ui.nvgt`) xây dựng form **Create Animal Spawn Zone** đúng thứ tự: `Label`, `Min X`, `Max X`, `Min Y`, `Max Y`, `Min Z`, `Max Z`, `Spawn / Respawn Time (ms)`, `Spawn Quantity`, **List Box Checkbox đa chọn** (`audio_form::create_list(..., 0, true, false)` cho phép Up/Down & Space chọn 1 hoặc nhiều loài — tránh bug `set_list_properties` của NVGT), `Leash` checkbox, `Active Time (always|day|night)`, nút `Create Animal Spawn Zone`. Hỗ trợ sửa/lọc `E` trong Line Manager và đồng bộ nóng `wildlife_sync_map_spawns()`.
  - Tác giả hóa 6 vùng `E` cân bằng trên [wildlands_valley.map](file:///C:/Users/LCBoy/Desktop/data/stw/server/maps/wildlands_valley.map) **ngoài** vùng an toàn `Settlement Clearing` (`35..65 x 35..65`).

### 2. Gỡ dịch chuyển khỏi Builder & Thêm `/maps` + Staff "View All Maps"
- Tách bạch chỉnh sửa với di chuyển: `F8 -> Switch Active Builder Map` (`bm_switch_map_menu`, `BUILDMAP|select_map`) chỉ đổi bản đồ đang sửa (`edit-only`); `BUILDMAP|lm_tp` chỉ cho phép dịch chuyển trong map người chơi đang đứng.
- Triển khai `MAPS|list` -> `MAPS_LIST` và `MAPS|tp|<slug>` (`PROTO_VERSION = 3`, `GAME_VERSION = "3.0.0"`) giới hạn từ **`RANK_BUILDER` trở lên** (`server/includes/admin_dev.nvgt`, `server/server.nvgt`).
- Hợp nhất UI `run_server_maps_menu` (`client/includes/staff_ui.nvgt`, `chat_input.nvgt`, `client.nvgt`) dùng chung cho cả lệnh **`/maps`** (hoặc `/map`) và mục **`View All Maps (/maps)`** trong `F9 Staff Panel` — Enter vào bản đồ sẽ dịch chuyển tới spawn của map đó.

### 3. Tạo Map Im lặng Mặc định & Bộ Nâng cấp STW Maps System
- **Silent-by-default Create Map**: Bỏ chọn âm thanh môi trường trong `bm_create_map_form`, mặc định `ambience_default = "none"`. Sửa `client/includes/audio_engine.nvgt` & `net_client.nvgt` dừng/fade-out êm `amb_curr` khi ambience là `"none"` thay vì ép bật `forest_day.ogg`; `collect_sound_refs()` bỏ qua `"none"`/`"inherit"`. Bổ sung lựa chọn `None (Silent)` và `Inherit Map Default` ở Edit Header & Zone.
- **Map Header v3 Rules (`M`)**: Hỗ trợ `allow_build (0/1)`, `weather_enabled (0/1)`, `time_mode (auto|day|night)` tương thích ngược v1/v2; server thực thi trong `builder_place_structure`, `send_scoped_snapshots`, `world_step_vitals_and_env`, `wildlife_step_spawn_zones`.
- **Zone Acoustic Reverb (`Z` + NVGT `audio_freeverb_node`)**: Thêm `reverb_preset` (`none|room|hall|cave`) gắn `audio_freeverb_node` trên `mix_steps`, `mix_world`, `mix_actors`, `mix_threat` khi người chơi đi vào vùng có reverb (giữ thoại, UI cue, ambience, nhạc nền sạch/dry).
- **Templates, Clone, 2-Corner Clipboard, Bounds Ping & Internal Portals**:
  - `generate_map_template_raw` hỗ trợ `flat`, `void`, `arena`, `cave` khi tạo map mới; `BUILDMAP|clone_map` nhân bản map đang mở.
  - Clipboard 2 góc (`Corner 1` / `Corner 2` qua `M` / `Shift+M` hoặc menu Hub) tự điền `Min X..Max Z` vào mọi form hộp 6 trục mới; Line Manager thêm `Ping Element Bounds in 3D Audio`.
  - Cổng dịch chuyển cùng map (`D` với `target_map == current_map`) phát âm thanh và đọc vùng/độ cao mới gọn nhẹ không nạp lại bản đồ.

### 4. Kiểm thử & Tài liệu (`tools/run_checks.ps1`)
- Cập nhật [BUILDER_GUIDE.md](file:///C:/Users/LCBoy/Desktop/data/stw/docs/BUILDER_GUIDE.md), [STAFF_GUIDE.md](file:///C:/Users/LCBoy/Desktop/data/stw/docs/STAFF_GUIDE.md), [CONTROLS.md](file:///C:/Users/LCBoy/Desktop/data/stw/docs/CONTROLS.md), [PROTOCOL.md](file:///C:/Users/LCBoy/Desktop/data/stw/docs/PROTOCOL.md).
- Biên dịch `server/server.exe` và `client/client.exe` bằng `nvgt -c` và xác nhận **`=== ALL CHECKS PASSED ===`** qua `tools/run_checks.ps1` (exit code 0 across `common_check`, `map_check` v3/E/reverb/templates, `auth_check`, `asset_check`, `client_profile_check`, E2E Phase 1/2 gồm Approach A 1200ms spawn & respawn, `/maps` RBAC & teleport, `select_map` edit-only, `allow_build=0`, `time_mode=night`, `clone_map`, same-map portal, `client.exe --smoke-test`, và `client_ui_e2e_check.nvgt`).

---

## Nhật ký kỹ thuật — Di chuyển Tọa độ Số Nguyên, Cầu thang 1x1 & Con dốc (2026-11-18)

### 1. Sửa lỗi Cầu thang & Con dốc (`common/constants.nvgt`, `common/protocol.nvgt`, `common/map.nvgt`)
- Bổ sung `round_coord(double)` trong `common/protocol.nvgt`, hằng số nhịp bước `WALK_STEP_MS = 220`, `SPRINT_STEP_MS = 140` và đệm ô lưới `TILE_CELL_PAD = 0.45` trong `common/constants.nvgt`.
- Cập nhật `find_stair_at`, `find_portal_at`, `find_hazard_at`, và `find_support_ex` / `find_support_at` trong `common/map.nvgt` dùng đệm `TILE_CELL_PAD` để mọi phần tử 1x1 (`min == max`, như `5..5, 5..5`) khớp chính xác với tọa độ ô nguyên.
- Sửa logic `ramp` trong `find_support_ex`: xử lý cả dốc `span <= 0.01`, tính ngưỡng bước lên dốc động `step_tol = clampd(1.05 + this_slope * 1.15, 1.05, 12.0)` khi nhân vật đứng trong tầm chân dốc (`z >= pl.min_z - 1.05`) để không hút người từ tầng dưới lên dốc tầng cao nhưng vẫn leo mượt cả dốc gắt, đồng thời trả về `on_ramp` và `ramp_slope`.

### 2. Chuyển Di chuyển Nhân vật sang Bước Số Nguyên & Bám Dốc (`server/includes/state.nvgt`, `server/includes/world.nvgt`, `server/server.nvgt`, `client/client.nvgt`)
- Thêm `last_move_ms`, `was_moving`, `step_rem_x`, `step_rem_y` vào `PlayerSession`; chuẩn hóa tọa độ X/Y thành số nguyên khi login, respawn, teleport và mỗi bước di chuyển (`5 -> 6`).
- Sử dụng chuẩn hóa Chebyshev + tích lũy phần dư Bresenham trong `world_step_player_move` để 8 hướng la bàn tiến thẳng `±1` ô nguyên và góc xoay mượt vẫn đi đúng hướng trên lưới số nguyên, tách trục va chạm tường và giữ nhân vật bám mượt mặt dốc khi đi xuống (`max_ramp_drop`) không bị rơi ảo.
- Cập nhật `client/client.nvgt` phát tiếng bước chân cục bộ ngay khi tap 1 bước và lặp đồng bộ theo `WALK_STEP_MS` / `SPRINT_STEP_MS`.

### 3. Kiểm thử & Biên dịch (`tools/map_check.nvgt`, `tools/net_integration_check.nvgt`, `tools/run_checks.ps1`)
- Bổ sung regression test cho cầu thang 1x1 (`5..5, 5..5, 0..20`), sàn 1x1, dốc gắt hẹp 1 ô Nam->Bắc (`Z 0..20`), dốc lơ lửng, bước đi số nguyên `20 -> 21`, leo cầu thang đá qua `ACT|climb|up` và đi lên/xuống dốc gắt không mất máu.
- Biên dịch `server/server.exe` và `client/client.exe` bằng `nvgt -c`, chạy toàn bộ `tools/run_checks.ps1` đạt **`=== ALL CHECKS PASSED ===`** (exit code 0).

---

## Nhật ký kỹ thuật — Chuẩn hóa phím tắt F1–F5, Credits, News từ Server & Main Menu Connect (`004-hotkeys-credits-mainmenu-connect`, 2026-11-19)

### 1. Chuẩn hóa hệ thống phím tắt trong game (`F1`–`F5` & tiện ích từ template `nvgt-dev`)
- **`common/constants.nvgt` & `common/protocol.nvgt`**: Thêm `KEYBIND_SCHEMA_VERSION = 2` và helper `format_uptime_words(uint64 sec)`.
- **`server/server.nvgt` & `server/includes/chat_social.nvgt`**: Bổ sung các gói điều khiển `UPTIME` -> `UPTIME_RES|<sec>`, `MOTD_REQ` -> `MOTD_RES|<escaped_motd>`, và `WHO_NEAR` -> `WHO_NEAR_RES|<cnt>|<entries>` (`social_send_who_near` lọc người chơi cùng map trong bán kính `EARSHOT_RADIUS`).
- **`client/includes/profile.nvgt`**, **`client/includes/net_client.nvgt`**, **`client/includes/chat_input.nvgt`**, **`client/client.nvgt`**:
  - Chuẩn hóa bộ phím tắt mặc định (hỗ trợ tự động migrate `settings.ini` cũ sang `schema_version = 2` mà vẫn giữ các phím tùy chỉnh không xung đột):
    - **`F1`**: Xem người chơi online (`who` / `/who`)
    - **`F2`**: Xem thời gian chạy của server (`uptime` / `/uptime`)
    - **`F3`**: Kiểm tra ping (`ping` / `/ping`, kèm cue `ui/track_ping.ogg`)
    - **`F4`**: Đọc Message of the Day trực tiếp từ server (`motd` / `/motd`, bỏ qua khi giữ `Alt` để không đụng `Alt+F4`)
    - **`F5`**: Mở Social Menu (`social`, đồng bộ nhãn `Social and Online Players (F5)` trong Pause Menu)
    - **`F6`**: Bật/tắt âm thanh Beacon (`toggle_beacons`, lưu vào `beacons_enabled`)
    - **`P`**: Xem người chơi ở gần kèm hướng tương đối & số bước (`who_near` / `/near`)
    - **`F11` / `Shift+F1`**: Đọc trợ giúp phím ngữ cảnh (`help`)
    - **`F12`**: Chép dòng thoại cuối cùng vừa đọc vào clipboard (`copy_last` qua `clipboard_set_text`)

### 2. Credits chuyên nghiệp, Sửa News & Main Menu một nút Connect (`client/includes/menus.nvgt`, `client/client.nvgt`)
- **`run_credits_menu()`**: Thêm mục **Credits** trong Main Menu với bố cục studio chuyên nghiệp, ghi tác giả là **LC Boy** và kèm ghi chú template phát triển game sinh tồn online từ đầu.
- **`run_news_menu(NetClient@ nc)`**: Gỡ bỏ hoàn toàn việc đọc lén file cục bộ `server/data/motd.txt` và `changelog.txt`; gỡ `News and Changelog` khỏi Main Menu (Phương án B), chỉ hiển thị dữ liệu thật từ server trong **Pause Menu** khi đã kết nối.
- **Main Menu tối giản + Phím tắt Dev (`!SCRIPT_COMPILED`)**:
  - Xóa các mục chọn nhiều server và hộp nhập Custom Server khỏi Main Menu; chỉ giữ đúng một nút **`Connect`** kết nối tới `MAIN_SERVER_HOST:DEFAULT_PORT` (`common/constants.nvgt`).
  - Khi chạy trực tiếp `client.nvgt` chưa biên dịch (`!SCRIPT_COMPILED`): nhấn **`F1`** chuyển sang `MAIN_SERVER_HOST` và đọc `"Main server"`, nhấn **`F2`** chuyển sang `LOCAL_SERVER_HOST` (`127.0.0.1`) và đọc `"Localhost"`. Khi chạy `client.exe` đã biên dịch, `F1`/`F2` bị khóa và luôn kết nối `MAIN_SERVER_HOST`.

### 3. Kiểm thử & Biên dịch (`tools/run_checks.ps1`)
- Bổ sung kiểm thử cho `format_uptime_words`, `beacons_enabled`, keybind `F1`–`F6`/`F11`/`F12`/`P`, migrate `settings.ini` v1 -> v2, `UPTIME`/`MOTD_REQ`/`WHO_NEAR`, và `/uptime`, `/motd`, `/near`.
- Cập nhật [docs/CONTROLS.md](file:///C:/Users/LCBoy/Desktop/data/stw/docs/CONTROLS.md) và [docs/PROTOCOL.md](file:///C:/Users/LCBoy/Desktop/data/stw/docs/PROTOCOL.md).
- Biên dịch `server/server.exe` & `client/client.exe` bằng `nvgt -c` và chạy toàn bộ `tools/run_checks.ps1` đạt **`=== ALL CHECKS PASSED ===`** (exit code 0).

---

## Nhật ký kỹ thuật — Lưu trữ Hàng tồn kho Server, Hệ thống Tay Trái/Phải & Âm thanh Ba lô (`005-persistent-inventory-dual-hand`, 2026-11-19)

### 1. Lưu trữ Hàng tồn kho & Trạng thái Tay Bền vững (`ACCOUNTS_V3`)
- **`common/items.nvgt`**: Bổ sung `encode_item_stacks` và `decode_item_stacks` dùng chung cho cả túi đồ tài khoản và rương đồ (`world.nvgt`).
- **`server/includes/accounts.nvgt`**: Nâng cấp định dạng `ACCOUNTS_V3` (tương thích ngược `ACCOUNTS_V1`/`ACCOUNTS_V2`), lưu `has_saved_inv`, `saved_inv`, `left_hand_id`, `right_hand_id`, `equipped_armor_id`, và `active_hand`. Nhờ cờ `has_saved_inv`, tài khoản mới chỉ nhận bộ đồ khởi đầu đúng 1 lần; tài khoản đã từng chơi (kể cả khi ba lô rỗng hoàn toàn) luôn giữ nguyên kho đồ thật qua offline/online và khởi động lại server.
- **`server/includes/state.nvgt` & `server/server.nvgt` & `server/includes/admin_dev.nvgt`**:
  - Thay `belt_slot` bằng `left_hand_id`, `right_hand_id`, `equipped_armor_id`, `active_hand` (`0=none`, `1=left`, `2=right`) trên `PlayerSession`.
  - Đồng bộ `sync_inv_to_account()` qua `send_inv()` và `ctx_sync_session_account()` khi `LOGOUT`, `disconnect`, hết grace period, autosave và `admin_save_all_state()`; nâng cấp `STAFF|act|clear_inv` gọi `clear_inv_and_hands()`.

### 2. Cơ chế Tay Trái/Phải (`I` + Trái/Phải, `1`/`2`, `Space` & `Shift+Space`)
- **`server/includes/world.nvgt` & `server/server.nvgt`**:
  - `ACT|assign_hand|<left|right>|<inv_idx>`: Gán vật phẩm trong ba lô vào tay trái hoặc tay phải; chỉ cho phép cầm cùng 1 vật phẩm ở **cả 2 tay** khi số lượng trong kho `>= 2` (nếu số lượng `== 1`, gán sang tay kia sẽ tự động chuyển tay). `reconcile_hands()` tự động giữ đúng bất biến này khi vật phẩm bị tiêu hao, cất rương hoặc xóa.
  - `ACT|hand|<1|2>`: Nhấn `1` (tay trái) hoặc `2` (tay phải) lần 1 chọn tay và đọc tên vật phẩm; nhấn lại đúng phím tay đó lần 2 khi đang chọn sẽ cất vật phẩm vào lại ba lô và làm tay trống (`active_hand = 0`); nhấn phím tay đối diện chuyển nhanh sang tay kia.
  - `ACT|use_hand` (`Space`): Trang bị `weapon`/`tool`/`armor` hoặc sử dụng ngay `food`/`drink`/`med`/`kit` ở tay đang chọn; `ps.active_item()` dùng cho tấn công (`F`), khai thác (`E`/`Enter`) và sưởi đuốc (`torch`).
- **`client/includes/profile.nvgt`, `net_client.nvgt`, `menus.nvgt`, `client.nvgt`**:
  - Gỡ bỏ hoàn toàn belt slot `1..9` và phím `Q`; nâng `KEYBIND_SCHEMA_VERSION = 3` (`common/constants.nvgt`) đặt `use_hand = KEY_SPACE` và `jump = KEY_SPACE` (kích hoạt bằng **`Shift + Space`** khi dùng chung `Space`).
  - `run_inventory_menu()` hỗ trợ **Mũi tên trái/phải** gán nhanh vào tay trái/phải và cập nhật nhãn tại chỗ (`Left Hand`, `Right Hand`, `Both Hands`, `Equipped Armor`) mà không đóng menu.

### 3. Âm thanh Ba lô & Kiểm thử (`tools/asset_pipeline.py`, `tools/run_checks.ps1`)
- Tải 2 file âm thanh CC0 thật (`Kenney RPG Audio`: `handle_small_leather.ogg` -> `ui/inv_open.ogg`, `handle_small_leather_2.ogg` -> `ui/inv_close.ogg`) qua `tools/asset_pipeline.py` (tổng **118** file `.ogg` hợp lệ trong `manifest.txt`).
- Phát `ui/inv_open.ogg` khi mở Inventory Menu (`I`) và `ui/inv_close.ogg` khi đóng (`Escape` hoặc `Back`).
- Cập nhật tài liệu [docs/CONTROLS.md](file:///C:/Users/LCBoy/Desktop/data/stw/docs/CONTROLS.md), [docs/PROTOCOL.md](file:///C:/Users/LCBoy/Desktop/data/stw/docs/PROTOCOL.md), [docs/ACCOUNTS.md](file:///C:/Users/LCBoy/Desktop/data/stw/docs/ACCOUNTS.md), [docs/AUDIO.md](file:///C:/Users/LCBoy/Desktop/data/stw/docs/AUDIO.md) và đặc tả [specs/005-persistent-inventory-dual-hand/](file:///C:/Users/LCBoy/Desktop/data/stw/specs/005-persistent-inventory-dual-hand/spec.md).
- Biên dịch `server/server.exe` và `client/client.exe` bằng `nvgt -c` và xác nhận **`=== ALL CHECKS PASSED ===`** qua `tools/run_checks.ps1` (exit code 0).

