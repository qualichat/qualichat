"""Captura automatica de pesquisas web (WebSearch / WebFetch) no vault.

Uso como hook PostToolUse:
    Claude Code envia JSON via stdin apos executar WebSearch/WebFetch.
    Este script extrai query + achados e anexa em Pesquisas/YYYY-MM-DD.md.

Detecta o vault via:
    1. $CLAUDE_VAULT_DIR (env)
    2. $CLAUDE_PROJECT_DIR/obsidian_vault (convencao)
    3. Hardcoded fallback (qualichat)

Input JSON esperado (do Claude Code):
    {
      "tool_name": "WebSearch" | "WebFetch",
      "tool_input": {"query": "..."} OU {"url": "...", "prompt": "..."},
      "tool_response": "..." (string ou dict)
    }
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_VAULT_FALLBACK = Path(r"d:/SITES/VSCODE/OUTROS/qualichat/obsidian_vault")
MAX_RESPONSE_CHARS = 2000
MAX_URL_IN_PREVIEW = 120


def resolve_vault() -> Path | None:
    env_vault = os.environ.get("CLAUDE_VAULT_DIR")
    if env_vault:
        p = Path(env_vault)
        if p.is_dir():
            return p
    project = os.environ.get("CLAUDE_PROJECT_DIR")
    if project:
        p = Path(project) / "obsidian_vault"
        if p.is_dir():
            return p
    if DEFAULT_VAULT_FALLBACK.is_dir():
        return DEFAULT_VAULT_FALLBACK
    return None


def extract_snippet(response, limit: int = MAX_RESPONSE_CHARS) -> str:
    if response is None:
        return ""
    if isinstance(response, str):
        text = response
    else:
        try:
            text = json.dumps(response, ensure_ascii=False, default=str)
        except Exception:
            text = str(response)
    text = text.strip()
    if len(text) > limit:
        text = text[:limit] + "\n...[truncated]"
    return text


def extract_urls(text: str, limit: int = 10) -> list[str]:
    urls = re.findall(r"https?://[^\s\)\]\"'<>]+", text)
    seen = []
    for u in urls:
        u = u.rstrip(".,;:")
        if u not in seen:
            seen.append(u)
        if len(seen) >= limit:
            break
    return seen


def format_entry(tool_name: str, tool_input: dict, tool_response) -> str:
    now = datetime.now()
    ts = now.strftime("%H:%M:%S")

    header = f"## {ts} - {tool_name}"
    lines = [header, ""]

    if tool_name == "WebSearch":
        query = (tool_input or {}).get("query", "?")
        lines.append(f"**Query:** `{query}`")
    elif tool_name == "WebFetch":
        url = (tool_input or {}).get("url", "?")
        prompt = (tool_input or {}).get("prompt", "")
        display_url = url if len(url) <= MAX_URL_IN_PREVIEW else url[:MAX_URL_IN_PREVIEW] + "..."
        lines.append(f"**URL:** {display_url}")
        if prompt:
            prompt_short = prompt[:200] + ("..." if len(prompt) > 200 else "")
            lines.append(f"**Pergunta:** {prompt_short}")
    else:
        lines.append(f"**Input:** `{json.dumps(tool_input, default=str)[:200]}`")
    lines.append("")

    snippet = extract_snippet(tool_response)
    urls = extract_urls(snippet)

    if urls:
        lines.append("**Links encontrados:**")
        for u in urls[:10]:
            lines.append(f"- {u}")
        lines.append("")

    if snippet:
        lines.append("**Resumo da resposta:**")
        lines.append("")
        lines.append("```")
        lines.append(snippet)
        lines.append("```")
        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def ensure_daily_note(vault: Path, today: datetime) -> Path:
    folder = vault / "Pesquisas"
    folder.mkdir(parents=True, exist_ok=True)
    note = folder / f"Pesquisas-{today.strftime('%Y-%m-%d')}.md"
    if not note.exists():
        header = (
            f"---\n"
            f"title: Pesquisas {today.strftime('%Y-%m-%d')}\n"
            f"date: {today.strftime('%Y-%m-%d')}\n"
            f"type: pesquisa-log\n"
            f"tags: [pesquisa, auto, daily]\n"
            f"---\n\n"
            f"# Pesquisas de {today.strftime('%Y-%m-%d')}\n\n"
            f"> [!info] Log automatico\n"
            f"> Capturado pelo hook PostToolUse WebSearch/WebFetch.\n\n"
        )
        note.write_text(header, encoding="utf-8")
    return note


def main() -> int:
    raw = sys.stdin.read().strip()
    if not raw:
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    tool_name = payload.get("tool_name")
    if tool_name not in ("WebSearch", "WebFetch"):
        return 0

    vault = resolve_vault()
    if vault is None:
        return 0

    tool_input = payload.get("tool_input") or {}
    tool_response = payload.get("tool_response")

    entry = format_entry(tool_name, tool_input, tool_response)

    today = datetime.now()
    note = ensure_daily_note(vault, today)
    with note.open("a", encoding="utf-8") as f:
        f.write(entry)

    print(f"[research] capturada: {note.name}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
