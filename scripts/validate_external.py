"""Validate qualichat parser against external WhatsApp fixtures.

Downloads test fixtures on-demand from third-party WhatsApp parser projects
to a local temp directory and runs `qualichat.chat.Chat()` against each.

Useful as a real-world sanity check when modifying the parser.

Run:
    .venv/Scripts/python.exe scripts/validate_external.py

Requires `gh` CLI (authenticated) on PATH for content download.
Fixtures are cached under ``%TEMP%/qualichat-external-fixtures/``.
"""

from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CACHE = Path(tempfile.gettempdir()) / "qualichat-external-fixtures"


# (label, repo, branch, path-in-repo, license)
SOURCES: List[Tuple[str, str, str, str, str]] = [
    ("chat-miner: ddmmyy 24h",
     "joweich/chat-miner", "main", "test/whatsapp/test_ddmmyy_24hrs.txt", "MIT"),
    ("chat-miner: mmddyy 24h (US)",
     "joweich/chat-miner", "main", "test/whatsapp/test_mmddyy_24hrs.txt", "MIT"),
    ("chat-miner: mmddyyyy 12h (Spanish AM/PM)",
     "joweich/chat-miner", "main", "test/whatsapp/test_mmddyyyy_12hrs.txt", "MIT"),
    ("chat-miner: yyyymmdd 24h (ISO)",
     "joweich/chat-miner", "main", "test/whatsapp/test_yyyymmdd_24hrs.txt", "MIT"),
    ("chat-miner: brackets mmddyy 24h",
     "joweich/chat-miner", "main", "test/whatsapp/test_[mmddyy]_24hrs.txt", "MIT"),
    ("toneworm: iOS recent EN with LRM",
     "toneworm/whatsapp-text-to-json", "master", "example/_example_chat.txt", "no-license"),
    ("Pustur: example.zip (Android DE)",
     "Pustur/whatsapp-chat-parser-website", "master",
     "src/assets/whatsapp-chat-parser-example.zip", "MIT"),
]


def _gh_download(repo: str, branch: str, path: str, dest: Path) -> None:
    """Download a single file from a GitHub repo via gh api."""
    api_path = path.replace("[", "%5B").replace("]", "%5D")
    cmd = ["gh", "api", f"repos/{repo}/contents/{api_path}?ref={branch}"]
    out = subprocess.check_output(cmd, text=True)
    payload = json.loads(out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(base64.b64decode(payload["content"]))


def _ensure_fixture(repo: str, branch: str, path: str) -> Path:
    """Cached download. Returns local path."""
    name = repo.replace("/", "__") + "__" + Path(path).name
    local = CACHE / name
    if not local.is_file():
        _gh_download(repo, branch, path, local)
    return local


def main() -> int:
    print(f"Cache: {CACHE}")
    CACHE.mkdir(parents=True, exist_ok=True)

    from qualichat.chat import Chat

    rows = []
    failures = 0

    for label, repo, branch, path, lic in SOURCES:
        try:
            local = _ensure_fixture(repo, branch, path)
        except Exception as exc:
            rows.append(("DLERR", "-", "-", lic, label, str(exc)))
            failures += 1
            continue

        try:
            chat = Chat(local)
            n_msgs = len(chat.messages)
            n_actors = len(chat.actors)
            status = "OK" if n_msgs > 0 else "EMPTY"
            if n_msgs == 0:
                failures += 1
            rows.append((status, n_msgs, n_actors, lic, label, ""))
        except Exception as exc:
            rows.append(("FAIL", "-", "-", lic, label, f"{type(exc).__name__}: {exc}"))
            failures += 1

    # silence the noisy chat-miner logging in the report block
    print()
    print(f"{'STATUS':<8}{'#MSGS':>6}{'#ACTORS':>9}  {'LICENSE':<11}  FIXTURE")
    print("-" * 100)
    for status, n_msgs, n_actors, lic, label, err in rows:
        print(f"{status:<8}{str(n_msgs):>6}{str(n_actors):>9}  {lic:<11}  {label}")
        if err:
            print(f"{'':<35}↳ {err}")
    print("-" * 100)
    print(f"Total: {len(SOURCES)} fixtures, {failures} failures")

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
