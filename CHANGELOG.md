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
- **`MessageType` detection is now multi-locale.** `enums.get_message_type`
  used to recognise eight hard-coded pt-BR strings; all other locales fell
  back to `MessageType.default`, so non-pt-BR exports flagged every media
  line as a regular text message and skewed every chart that filtered on
  type. Now recognises pt-BR, en, es, de, it and fr tokens (case-insensitive,
  whitespace-tolerant) plus the Android `<Media omitted>` / `<Mídia oculta>`
  generic. iOS document lines are still detected by suffix match.
- **`get_random_name()` no longer raises `IndexError`** when the bundled
  `books.txt` pool of 767 names is exhausted. Falls back to sequential
  `Actor #N` placeholders so chats with > 767 distinct actors load cleanly.
- **`setup.py` author typo fixed**: `Erneist Manhein` → `Ernest Manheim`
  (matches `__author__` in `qualichat/__init__.py`).
- **Modern packaging**. Project metadata, dependencies and tool
  configuration moved to `pyproject.toml` (PEP 621). The legacy
  `setup.py` is now a one-line stub kept only for older `pip` versions.
  Dynamic version reading from `qualichat/__init__.py` eliminates the
  duplicate-version-string class of bug.
- **Tooling configuration**: `pyproject.toml` carries `ruff` (linter
  and formatter, conservative ruleset), `mypy` (per-module strictness
  ramping up), `pytest` config, and `coverage` config. Local
  development uses `pip install -e ".[dev]"`; documentation builds use
  `pip install -e ".[docs]"`.
- **Pre-commit hooks** (`.pre-commit-config.yaml`) — trailing
  whitespace, end-of-file-fixer, large-file guard, ruff lint and ruff
  format on every commit.
- **Dependabot** (`.github/dependabot.yml`) — weekly pip dependency
  updates and monthly GitHub Actions updates, with conventional commit
  prefixes and automatic labelling.
- **CI overhaul**. The `Test` workflow now adds a third Python version
  (3.12), uses `pip install -e .` to exercise the package install,
  emits coverage reports (`pytest-cov` + `coverage.xml` artifact) and
  adds a separate non-blocking `lint` job (`ruff check`,
  `ruff format --check`). The `Publish to PyPI` workflow uses
  `python -m build` (PEP 517) plus `twine check` for distribution
  verification before upload.
- **Repository hygiene**: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`
  (Contributor Covenant 2.1, with a research-specific addendum on
  privacy and ongoing-research respect) and CI/PyPI/license/Python
  badges in the README.

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
