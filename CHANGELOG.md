# Changelog

## 1.5.0

### Highlights

Qualichat now reads **WhatsApp exports from any platform and locale**: iOS
(old format with space, current format with comma), Android, US 12-hour
clock, German, and so on. Previously, only iOS exports in Brazilian
Portuguese with the legacy timestamp format `[dd/mm/yyyy hh:mm:ss]` were
parsed; everything else silently produced an empty chat.

### Changes

- **Parser rewritten** as a thin adapter over
  [`chat-miner`](https://github.com/joweich/chat-miner). The brittle in-house
  regex was removed. `chat-miner` infers brackets, separators and date
  ordering automatically.
- **`.zip` exports are now accepted directly.** `Chat(path)` extracts
  `_chat.txt` (or the first `.txt`) from the archive in a temp directory.
- **Useful error on parse failure.** A garbage or unsupported file now raises
  `ValueError("No messages parsed from …")` instead of silently loading
  zero messages.
- **`Message` accepts `datetime.datetime` directly** for `created_at`
  (string is still accepted for backwards compatibility).
- **Version aligned**: `__version__` and `version_info` were out of sync
  (`1.4.3` vs `1.4.2`). Both are now `1.5.0`.
- **System events recovered.** Group lifecycle messages ("Bob added you",
  "Jimbo left", "Loris created group X", end-to-end notice, …) are
  reintroduced via a thin `WhatsAppParser` subclass that captures what the
  upstream parser drops. They now populate `chat.system_messages` again, so
  the `messages_per_actors_per_weekday` chart's "System Messages" option
  works as before. Self-destroying messages (`Author:.`) remain skipped —
  they carry no useful body.

### Removed

- `qualichat.regex.CHAT_FORMAT_RE` and `qualichat.regex.USER_MESSAGE_RE`
  (obsolete; their job is now `chat-miner`'s).

### Dependencies

- Added: `chat-miner>=0.6,<1`
- Pinned (to prevent silent breakage on upgrade):
  - `spacy>=3.7,<4`
  - `pandas>=2,<3`
  - `plotly>=5,<7`
  - `emojis>=0.7,<1`
  - `wordcloud>=1.9,<2`
  - `matplotlib>=3.7,<4`
  - `tldextract>=5,<6`
  - `questionary>=2,<3`
  - `rich>=13,<15`
  - `deep-translator>=1.11,<2`
  - `spacytextblob>=4,<5`
