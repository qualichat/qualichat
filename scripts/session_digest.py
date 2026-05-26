"""Gera nota de sessao no Obsidian vault a partir de transcript JSONL do Claude Code.

Usado como hook Stop e via CLI. Nao depende de rede nem de Claude API.

CLI:
    python session_digest.py                       # ultimo transcript do projeto corrente
    python session_digest.py --transcript PATH     # transcript especifico
    python session_digest.py --session-id ID       # por id
    python session_digest.py --dry-run             # imprime sem escrever

Hook Stop:
    CLAUDE_PROJECT_DIR e CLAUDE_SESSION_ID sao definidos pelo harness.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_VAULT = Path(r"d:/SITES/VSCODE/OUTROS/qualichat/obsidian_vault")
DEFAULT_SLUG = "d--SITES-VSCODE-OUTROS-qualichat"
CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"


def derive_slug(project_dir: str | Path) -> str:
    """Claude Code sanitiza paths para slug: troca \\ / : . por -"""
    s = str(project_dir)
    for ch in ["\\", "/", ":", "."]:
        s = s.replace(ch, "-")
    return s.strip("-")


MAX_TEXT_SNIPPET = 600
MIN_TEXT_KEEP = 80


def find_latest_transcript(project_slug: str) -> Path | None:
    root = CLAUDE_PROJECTS_DIR / project_slug
    if not root.exists():
        return None
    candidates = sorted(root.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def find_by_session_id(project_slug: str, session_id: str) -> Path | None:
    path = CLAUDE_PROJECTS_DIR / project_slug / f"{session_id}.jsonl"
    return path if path.exists() else None


def iter_entries(transcript: Path):
    with transcript.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def parse_ts(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone()
    except Exception:
        return None


def filter_by_window(entries: list[dict], cutoff: datetime | None) -> list[dict]:
    if cutoff is None:
        return entries
    kept = []
    for e in entries:
        ts = parse_ts(e.get("timestamp"))
        if ts is None or ts >= cutoff:
            kept.append(e)
    return kept


def extract_text_blocks(message: dict) -> list[str]:
    content = message.get("content", [])
    if isinstance(content, str):
        return [content]
    if not isinstance(content, list):
        return []
    out = []
    for c in content:
        if isinstance(c, dict) and c.get("type") == "text":
            t = c.get("text", "").strip()
            if t:
                out.append(t)
    return out


def extract_tool_uses(message: dict) -> list[dict]:
    content = message.get("content", [])
    if not isinstance(content, list):
        return []
    return [c for c in content if isinstance(c, dict) and c.get("type") == "tool_use"]


def summarize_tool_use(tu: dict) -> str | None:
    name = tu.get("name", "")
    inp = tu.get("input", {}) or {}
    if name == "Bash":
        cmd = (inp.get("command") or "").strip().replace("\n", " \\ ")
        desc = inp.get("description") or ""
        if len(cmd) > 180:
            cmd = cmd[:177] + "..."
        return f"`bash` {desc} - `{cmd}`" if desc else f"`bash` `{cmd}`"
    if name in ("Edit", "Write"):
        p = inp.get("file_path", "?")
        return f"`{name.lower()}` [{Path(p).name}]({p})"
    if name == "Read":
        p = inp.get("file_path", "?")
        return f"`read` [{Path(p).name}]({p})"
    if name == "Glob":
        return f"`glob` `{inp.get('pattern','')}`"
    if name == "Grep":
        q = inp.get("pattern", "")
        if len(q) > 80:
            q = q[:77] + "..."
        return f"`grep` `{q}`"
    if name == "WebSearch":
        return f"`websearch` {inp.get('query','')[:120]}"
    if name == "WebFetch":
        return f"`webfetch` {inp.get('url','')[:120]}"
    if name == "TodoWrite":
        todos = inp.get("todos", [])
        if isinstance(todos, list):
            return f"`todos` atualizada ({len(todos)} itens)"
    if name == "Skill":
        return f"`skill` /{inp.get('skill','?')}"
    if name == "Agent":
        return f"`agent` {inp.get('subagent_type','general')}: {(inp.get('description') or '')[:80]}"
    if name.startswith("mcp__"):
        short = name.replace("mcp__", "").replace("__", ".")
        return f"`mcp` {short}"
    return f"`{name}`"


def collect_affected_files(tool_uses: list[dict]) -> list[str]:
    seen = OrderedDict()
    for tu in tool_uses:
        if tu.get("name") in ("Edit", "Write"):
            p = (tu.get("input") or {}).get("file_path")
            if p:
                seen[p] = True
    return list(seen.keys())


_WRAPPER_TAG_RE = re.compile(
    r"<(ide_opened_file|ide_selection|system-reminder|command-name|command-message|command-args|local-command-stdout|user-prompt-submit-hook)\b[^>]*>.*?</\1>",
    re.DOTALL,
)
_STRAY_TAG_RE = re.compile(r"</?(ide_opened_file|ide_selection|system-reminder|command-name|command-message|command-args|local-command-stdout|user-prompt-submit-hook)[^>]*>")


def clean_user_text(text: str) -> str:
    cleaned = _WRAPPER_TAG_RE.sub("", text)
    cleaned = _STRAY_TAG_RE.sub("", cleaned)
    return cleaned.strip()


def collect_user_prompts(entries: list[dict]) -> list[str]:
    out = []
    for e in entries:
        if e.get("type") != "user":
            continue
        msg = e.get("message") or {}
        if not isinstance(msg, dict) or msg.get("role") != "user":
            continue
        content = msg.get("content", [])
        texts: list[str] = []
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "text":
                    t = c.get("text", "")
                    if t and not t.startswith("Tool loaded"):
                        texts.append(t)
        elif isinstance(content, str):
            if content.strip():
                texts.append(content)
        if not texts:
            continue
        cleaned = clean_user_text("\n".join(texts))
        if cleaned:
            out.append(cleaned)
    return out


def collect_assistant_reasoning(entries: list[dict]) -> list[str]:
    out = []
    for e in entries:
        if e.get("type") != "assistant":
            continue
        msg = e.get("message") or {}
        for text in extract_text_blocks(msg):
            if len(text) >= MIN_TEXT_KEEP:
                out.append(text)
    return out


def collect_tool_uses(entries: list[dict]) -> list[dict]:
    out = []
    for e in entries:
        if e.get("type") != "assistant":
            continue
        msg = e.get("message") or {}
        out.extend(extract_tool_uses(msg))
    return out


def infer_title(prompts: list[str]) -> str:
    if not prompts:
        return "Sessao sem prompt inicial"
    first = prompts[0].strip().splitlines()[0]
    first = re.sub(r"[#*`>\[\]]", "", first).strip()
    if len(first) > 80:
        first = first[:77] + "..."
    return first or "Sessao"


def infer_tags(prompts: list[str], tool_uses: list[dict], affected: list[str]) -> list[str]:
    tags = {"sessao", "auto"}
    corpus = " ".join(prompts).lower() + " " + " ".join(affected).lower()
    keywords = {
        # Teoria
        "goffman": "goffman",
        "cavalcante": "cavalcante",
        "hanke": "hanke",
        "frame": "frame",
        "laminac": "laminacao",      # laminacao/laminacoes
        "maquinac": "maquinacao",    # maquinacao/maquinacoes
        "fabricac": "fabricacao",
        "ancoragem": "ancoragem",
        "tom": "tom",                # tonalizacao
        "tese": "tese",
        # Codigo qualichat
        "qualichat": "qualichat",
        "frames.py": "frames",
        "models.py": "models",
        "regex": "regex",
        "parser": "parser",
        "chat-miner": "chat-miner",
        "qty_char": "qty-char",
        "sub_period": "sub-period",
        # UI / deploy
        "streamlit": "streamlit",
        "plotly": "plotly",
        "sprint": "sprint",
        "deploy": "deploy",
        # Meta
        "vault": "vault",
        "obsidian": "obsidian",
        "pdf": "pdf",
    }
    for k, tag in keywords.items():
        if k in corpus:
            tags.add(tag)
    return sorted(tags)


def render_note(
    transcript: Path,
    session_id: str,
    started_at: str | None,
    ended_at: str,
    prompts: list[str],
    reasoning: list[str],
    tool_uses: list[dict],
    affected: list[str],
) -> str:
    title = infer_title(prompts)
    tags = infer_tags(prompts, tool_uses, affected)
    tool_lines = []
    for tu in tool_uses:
        s = summarize_tool_use(tu)
        if s:
            tool_lines.append(f"- {s}")

    lines = []
    lines.append("---")
    lines.append(f"date: {ended_at[:10]}")
    lines.append(f"time: {ended_at[11:19]}")
    lines.append("type: sessao")
    lines.append(f"session_id: {session_id}")
    lines.append(f"transcript: {transcript}")
    lines.append(f"tags: [{', '.join(tags)}]")
    lines.append("---")
    lines.append("")
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"**Inicio:** {started_at or '?'}  ")
    lines.append(f"**Fim:** {ended_at}  ")
    lines.append(f"**Prompts do usuario:** {len(prompts)}  ")
    lines.append(f"**Tool calls:** {len(tool_uses)}  ")
    lines.append(f"**Arquivos tocados:** {len(affected)}")
    lines.append("")

    if prompts:
        lines.append("## Objetivo")
        lines.append("")
        first = prompts[0].strip()
        if len(first) > MAX_TEXT_SNIPPET:
            first = first[:MAX_TEXT_SNIPPET] + "..."
        lines.append(f"> {first}")
        lines.append("")

    if affected:
        lines.append("## Arquivos tocados")
        lines.append("")
        for p in affected:
            lines.append(f"- [{Path(p).name}]({p})")
        lines.append("")

    if tool_lines:
        lines.append("## Atividade")
        lines.append("")
        lines.extend(tool_lines[:120])
        if len(tool_lines) > 120:
            lines.append(f"- ... (+{len(tool_lines)-120} tool calls omitidos)")
        lines.append("")

    if reasoning:
        lines.append("## Decisoes e achados")
        lines.append("")
        for i, r in enumerate(reasoning[-12:], 1):
            snippet = r.strip()
            if len(snippet) > MAX_TEXT_SNIPPET:
                snippet = snippet[:MAX_TEXT_SNIPPET] + "..."
            lines.append(f"### Bloco {i}")
            lines.append("")
            for ln in snippet.splitlines():
                lines.append(f"> {ln}" if ln else ">")
            lines.append("")

    if len(prompts) > 1:
        lines.append("## Conversa (prompts do usuario)")
        lines.append("")
        for i, p in enumerate(prompts[1:], 2):
            snippet = p.strip()
            if len(snippet) > 300:
                snippet = snippet[:297] + "..."
            lines.append(f"{i}. {snippet}")
        lines.append("")

    lines.append("---")
    lines.append("*Nota gerada automaticamente por `scripts/session_digest.py` (hook Stop).*")
    return "\n".join(lines) + "\n"


def write_note(markdown: str, session_id: str, ended_at: datetime,
               per_day: bool, sessions_dir: Path) -> Path:
    sessions_dir.mkdir(parents=True, exist_ok=True)
    if per_day:
        fname = f"Sessao-{ended_at.strftime('%Y-%m-%d')}.md"
    else:
        fname = f"Sessao-{ended_at.strftime('%Y-%m-%d-%H%M')}-{session_id[:8]}.md"
    path = sessions_dir / fname
    path.write_text(markdown, encoding="utf-8")
    return path


def update_index(note_path: Path, title: str, sessions_dir: Path) -> None:
    index = sessions_dir / "_index.md"
    entry = f"- [[{note_path.stem}]] - {title}\n"
    if index.exists():
        existing = index.read_text(encoding="utf-8")
        if note_path.stem not in existing:
            index.write_text(existing.rstrip() + "\n" + entry, encoding="utf-8")
    else:
        header = "---\ntype: index\ntags: [index, sessoes]\n---\n\n# Indice de Sessoes\n\n"
        index.write_text(header + entry, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript", type=Path, default=None)
    ap.add_argument("--session-id", default=os.environ.get("CLAUDE_SESSION_ID"))
    ap.add_argument("--vault", type=Path,
                    default=Path(os.environ.get("CLAUDE_VAULT_DIR", str(DEFAULT_VAULT))))
    ap.add_argument("--project-slug",
                    default=os.environ.get("CLAUDE_PROJECT_SLUG") or
                    (derive_slug(os.environ["CLAUDE_PROJECT_DIR"])
                     if os.environ.get("CLAUDE_PROJECT_DIR") else DEFAULT_SLUG))
    ap.add_argument("--sessions-subdir", default="Sessoes")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--min-turns", type=int, default=2,
                    help="Nao gera nota se menos que N prompts do usuario")
    ap.add_argument("--window-hours", type=float, default=24.0,
                    help="Processa apenas entradas das ultimas N horas (default 24). Use 0 para tudo.")
    ap.add_argument("--per-day", action="store_true", default=True,
                    help="Nome do arquivo por data (default). Um arquivo por dia, sobrescreve.")
    ap.add_argument("--per-session", action="store_true",
                    help="Nome por session_id+hora. Uma nota por execucao.")
    args = ap.parse_args()

    transcript = args.transcript
    if transcript is None and args.session_id:
        transcript = find_by_session_id(args.project_slug, args.session_id)
    if transcript is None:
        transcript = find_latest_transcript(args.project_slug)
    if transcript is None or not transcript.exists():
        print(f"[digest] nenhum transcript encontrado em {CLAUDE_PROJECTS_DIR}/{args.project_slug}",
              file=sys.stderr)
        return 1

    entries = list(iter_entries(transcript))
    if not entries:
        print("[digest] transcript vazio", file=sys.stderr)
        return 1

    if args.window_hours > 0:
        cutoff = datetime.now(tz=timezone.utc).astimezone() - timedelta(hours=args.window_hours)
        entries = filter_by_window(entries, cutoff)
        if not entries:
            print(f"[digest] nenhuma entrada nas ultimas {args.window_hours}h", file=sys.stderr)
            return 0

    prompts = collect_user_prompts(entries)
    if len(prompts) < args.min_turns:
        print(f"[digest] sessao muito curta ({len(prompts)} prompts), nao gerando nota",
              file=sys.stderr)
        return 0

    reasoning = collect_assistant_reasoning(entries)
    tool_uses = collect_tool_uses(entries)
    affected = collect_affected_files(tool_uses)

    session_id = transcript.stem
    started_at = None
    ended_at_dt = datetime.now()
    for e in entries:
        ts = e.get("timestamp")
        if ts and not started_at:
            started_at = ts
    if entries and entries[-1].get("timestamp"):
        try:
            ended_at_dt = datetime.fromisoformat(entries[-1]["timestamp"].replace("Z", "+00:00"))
            ended_at_dt = ended_at_dt.replace(tzinfo=None)
        except Exception:
            pass
    ended_at_str = ended_at_dt.strftime("%Y-%m-%d %H:%M:%S")

    md = render_note(transcript, session_id, started_at, ended_at_str,
                     prompts, reasoning, tool_uses, affected)

    if args.dry_run:
        sys.stdout.write(md)
        return 0

    per_day = args.per_day and not args.per_session
    sessions_dir = args.vault / args.sessions_subdir
    note_path = write_note(md, session_id, ended_at_dt, per_day=per_day,
                           sessions_dir=sessions_dir)
    update_index(note_path, infer_title(prompts), sessions_dir=sessions_dir)
    print(f"[digest] nota gerada: {note_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
