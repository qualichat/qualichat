"""Captura de commits no vault.

Chamado por git hook post-commit (bash wrapper) OU manualmente.
Extrai SHA, mensagem, arquivos, diff stat do ultimo commit e anexa
em Commits/YYYY-MM-DD.md.

Uso:
    python capture_commit.py                    # ultimo commit no cwd
    python capture_commit.py --repo PATH        # repo especifico
    python capture_commit.py --vault PATH       # override vault

Detecta vault via:
    1. --vault arg
    2. $CLAUDE_VAULT_DIR env
    3. $REPO/obsidian_vault ou $REPO/../obsidian_vault
    4. Hardcoded fallback (qualichat)
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_VAULT_FALLBACK = Path(r"d:/SITES/VSCODE/OUTROS/qualichat/obsidian_vault")


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return result.stdout.strip()


def resolve_vault(explicit: Path | None, repo: Path) -> Path | None:
    if explicit:
        return explicit if explicit.is_dir() else None
    env_vault = os.environ.get("CLAUDE_VAULT_DIR")
    if env_vault and Path(env_vault).is_dir():
        return Path(env_vault)
    candidates = [
        repo / "obsidian_vault",
        repo.parent / "obsidian_vault",
        DEFAULT_VAULT_FALLBACK,
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return None


def ensure_daily_note(vault: Path, today: datetime) -> Path:
    folder = vault / "Commits"
    folder.mkdir(parents=True, exist_ok=True)
    note = folder / f"Commits-{today.strftime('%Y-%m-%d')}.md"
    if not note.exists():
        header = (
            f"---\n"
            f"title: Commits {today.strftime('%Y-%m-%d')}\n"
            f"date: {today.strftime('%Y-%m-%d')}\n"
            f"type: commit-log\n"
            f"tags: [commits, auto, daily]\n"
            f"---\n\n"
            f"# Commits de {today.strftime('%Y-%m-%d')}\n\n"
            f"> [!info] Log automatico\n"
            f"> Capturado pelo git hook post-commit.\n\n"
        )
        note.write_text(header, encoding="utf-8")
    return note


def format_commit_entry(repo: Path) -> str | None:
    sha = git(repo, "rev-parse", "HEAD")
    if not sha:
        return None
    sha_short = sha[:8]
    msg = git(repo, "log", "-1", "--format=%B")
    author = git(repo, "log", "-1", "--format=%an")
    ts = git(repo, "log", "-1", "--format=%ai")
    branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD") or "(detached)"
    stat = git(repo, "show", "--stat", "--format=", sha).strip()
    files_raw = git(repo, "show", "--name-only", "--format=", sha)
    files = [f for f in files_raw.splitlines() if f.strip()]

    hhmm = datetime.now().strftime("%H:%M")
    first_line = msg.splitlines()[0] if msg else "(sem mensagem)"

    lines = []
    lines.append(f"## {hhmm} - `{sha_short}` - {first_line}")
    lines.append("")
    lines.append(f"- **Repo:** `{repo.name}` (`{repo}`)")
    lines.append(f"- **Branch:** `{branch}`")
    lines.append(f"- **Autor:** {author}")
    lines.append(f"- **Timestamp:** {ts}")
    lines.append(f"- **SHA:** `{sha}`")
    lines.append("")
    if msg and msg.strip() != first_line:
        lines.append("**Mensagem completa:**")
        lines.append("")
        lines.append("```")
        lines.append(msg.strip())
        lines.append("```")
        lines.append("")
    if files:
        lines.append(f"**Arquivos alterados ({len(files)}):**")
        lines.append("")
        for f in files[:30]:
            lines.append(f"- `{f}`")
        if len(files) > 30:
            lines.append(f"- ... (+{len(files)-30} arquivos)")
        lines.append("")
    if stat:
        lines.append("**Diff stat:**")
        lines.append("")
        lines.append("```")
        lines.append(stat)
        lines.append("```")
        lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--vault", type=Path, default=None)
    args = ap.parse_args()

    repo = args.repo.resolve()
    if not (repo / ".git").exists():
        print(f"[commit] {repo} nao e repositorio git", file=sys.stderr)
        return 0

    vault = resolve_vault(args.vault, repo)
    if vault is None:
        print(f"[commit] vault nao encontrado (setar CLAUDE_VAULT_DIR ou --vault)",
              file=sys.stderr)
        return 0

    entry = format_commit_entry(repo)
    if entry is None:
        print("[commit] nenhum commit para capturar", file=sys.stderr)
        return 0

    note = ensure_daily_note(vault, datetime.now())
    with note.open("a", encoding="utf-8") as f:
        f.write(entry)
    print(f"[commit] capturado: {note.name}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
