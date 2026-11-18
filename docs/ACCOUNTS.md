# Accounts, Security & Persistence — Wildlands Online

## 1. Core UX Principle
**Sign in once, never asked again** unless the user explicitly signs out or switches to a different server address. Password fields never speak characters aloud by default (audible click per keypress, optional echo toggle, length readout, `Ctrl+V` paste supported).

## 2. Client AppData Storage
- Location: `DIRECTORY_PREFERENCES("WildlandsStudio", "WildlandsOnline")` (`%APPDATA%\WildlandsStudio\WildlandsOnline\player.ini`).
- Never stored beside the `.exe` (safe when installed in Program Files or read-only media).
- All numbers serialized as strings (`"0"`..`"100"`) to avoid double-precision parsing bugs.
- Settings save immediately on change.
- **Credential Wallet (`[wallet]`)**:
  - 8 LRU slots (`slot_0..slot_7`), each storing `host:port|username|token_hex`.
  - All 8 slots are overwritten every save (including empty `""` slots) so signed-out credentials cannot reappear.
  - Tokens are strictly scoped to `host:port` so local testing against `localhost:7100` never leaks or overwrites a live server session token.
  - Plaintext passwords are NEVER written to disk.

## 3. Server Password & Token Cryptography
- **Username Rules**: `3..20` characters `[A-Za-z0-9_-]`, case-insensitive uniqueness enforced server-side (`Hero` and `hero` cannot both exist). Rules spoken clearly before entering text.
- **Password Hashing**:
  - Per-account 16-byte CSPRNG salt (`random_bytes(16)` hex).
  - `5000` rounds of salted stretched SHA-256 (`h = string_hash_sha256(salt + ":" + h)`), verified with a constant-time comparison function.
  - *Transparency Note*: NVGT `0.90` exposes SHA-256/SHA-512 rather than Argon2/bcrypt; 5,000-round salted stretching protects offline hashes substantially while remaining responsive at login, though it is not memory-hard like Argon2.
- **Session Tokens**:
  - Issued on login/registration using `random_bytes(32)` hex-encoded (never non-crypto game RNG).
  - Server stores only `string_hash_sha256(token)` so a leaked account file cannot be used to hijack active sessions.
  - New login rotates and invalidates any previous token; `LOGOUT` clears it.
- **Rate Limiting**: Per-IP authentication/registration throttling prevents brute-force and account spam (configurable/lifted under `--test-mode`).

## 4. Atomic Server Store & Ranks
- `data/accounts.dat` and `data/world_objects.dat` use atomic writes (`.tmp` -> `.bak` -> rename).
- **Fatal Corrupt Store Rule**: If `data/accounts.dat` exists and fails validation, the server shows a modal `alert()`, logs the error, and refuses to start so existing accounts are never overwritten.
- **Ranks**: `Player (0)` < `Builder (1)` < `Moderator (2)` < `Admin (3)` < `Developer (4)`.
  - Nobody moderates sideways or upwards (`actor.rank > target.rank` strictly enforced).
  - `Developer` rank CANNOT be granted via network commands; it requires the account to appear in server-owned `data/devs.txt` AND pass server verification.
- **Guest Mode**: Disabled by default (`ALLOW_GUESTS = false`); enabled only when operator passes `--allow-guests` or `--test-mode` (logged loudly at startup).
