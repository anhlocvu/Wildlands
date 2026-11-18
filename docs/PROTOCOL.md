# Protocol — Wildlands Online (`PROTO_VERSION = 1`)

See the full field-by-field contract in [contracts/protocol.md](file:///C:/Users/LCBoy/Desktop/data/stw/specs/001-wildlands-online-survival/contracts/protocol.md).

## Wire Rules (Non-Negotiable)
1. **Delimiter & Escaping**: Pipe-delimited UTF-8 (`|`). Every free-text field (chat, names, reasons, announcements, map labels) MUST pass through `wire_escape()` (`\` -> `\\`, `|` -> `\p`, `\n` -> `\n`, `\r` dropped) and single-pass `wire_unescape()`.
2. **Empty-Safe Parsing**: Always split with `split_keep_empty()` and access via `field(parts, idx, fallback)`. Optional fields belong at the end or carry `-` as an explicit placeholder.
3. **Versioned Handshake**: Client sends `HELLO|1|<client_ver>|<is_source>`. Server refuses mismatched versions with `REFUSE|ver_mismatch|<spoken message explaining which side is behind>`.
4. **Fixed Float Precision**: Coordinates and velocities serialize to 2 decimal places (`%.2f`).
5. **Hostile Input Assumption**: Server validates, sanitizes (`sanitize_name()`), and range-clamps (`safe_int()`, `safe_double()`) every incoming field, rejecting unknown opcodes and logging refused auth/dev/mod requests.
6. **Packet Budget**: Every packet MUST stay `<= 1350` bytes before `network.send()`.
