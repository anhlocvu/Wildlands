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
