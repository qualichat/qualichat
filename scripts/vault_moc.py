"""Gera/atualiza MOC (Map of Content) do vault Obsidian do Qualichat.

MOC = indice navegavel que Claude le no inicio de cada sessao.
Varre vault, extrai frontmatter + primeira heading, agrupa por pasta e tags,
identifica notas recentes e orfas.

DEPENDENCIAS (NAO MOVER ESTE ARQUIVO sem atualizar):
- .claude/settings.local.json hooks:
    - Stop: regenera _MOC.md apos cada sessao
    - SessionStart: injeta contexto compacto via --stdout

Uso:
    python vault_moc.py                   # gera _MOC.md no vault
    python vault_moc.py --dry-run         # imprime sem escrever
    python vault_moc.py --stdout          # so imprime (para SessionStart hook)
    python vault_moc.py --recent 20       # N notas recentes (default 15)
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_VAULT = Path(
    os.environ.get("CLAUDE_VAULT_DIR",
                   r"d:/SITES/VSCODE/OUTROS/qualichat/obsidian_vault"))
EXCLUDE_DIRS = {".obsidian", "templates"}

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_WIKILINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:\|[^\]]*)?(?:#[^\]]*)?\]\]")
_HEADING_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    raw = m.group(1)
    data: dict = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        k = k.strip()
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            data[k] = [s.strip().strip('"\'') for s in v[1:-1].split(",") if s.strip()]
        else:
            data[k] = v.strip('"\'')
    return data, text[m.end():]


def extract_title(text: str, fallback: str) -> str:
    m = _HEADING_RE.search(text)
    return m.group(1).strip() if m else fallback


def extract_first_paragraph(text: str, max_len: int = 180) -> str:
    for chunk in text.split("\n\n"):
        chunk = chunk.strip()
        if not chunk:
            continue
        if chunk.startswith("#") or chunk.startswith("---"):
            continue
        cleaned = re.sub(r"\s+", " ", chunk)
        if len(cleaned) > max_len:
            cleaned = cleaned[:max_len - 1] + "..."
        return cleaned
    return ""


def scan_vault(vault: Path) -> list[dict]:
    notes: list[dict] = []
    for md in vault.rglob("*.md"):
        rel = md.relative_to(vault)
        if rel.parts and rel.parts[0] in EXCLUDE_DIRS:
            continue
        if md.name.startswith("_"):
            continue
        try:
            text = md.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        fm, body = parse_frontmatter(text)
        title = extract_title(body, md.stem)
        links = _WIKILINK_RE.findall(body)
        tags = fm.get("tags", []) if isinstance(fm.get("tags"), list) else []
        try:
            mtime = datetime.fromtimestamp(md.stat().st_mtime)
        except OSError:
            mtime = datetime.min
        notes.append({
            "path": md,
            "rel": rel,
            "folder": str(rel.parent) if rel.parent.parts else "/",
            "name": md.stem,
            "title": title,
            "summary": extract_first_paragraph(body),
            "tags": tags,
            "links": links,
            "mtime": mtime,
            "size": md.stat().st_size if md.exists() else 0,
        })
    return notes


def render_moc(notes: list[dict], recent_n: int) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines: list[str] = []
    lines.append("---")
    lines.append("type: moc")
    lines.append("tags: [moc, index, auto]")
    lines.append(f"updated: {now}")
    lines.append(f"notas_totais: {len(notes)}")
    lines.append("---")
    lines.append("")
    lines.append("# Map of Content - Vault Qualichat")
    lines.append("")
    lines.append("> Indice mestre auto-gerado por `scripts/vault_moc.py`. "
                 "NAO editar manualmente - use slash commands ou edite as notas diretamente.")
    lines.append("")
    lines.append(f"**{len(notes)} notas** em {len({n['folder'] for n in notes})} pastas.")
    lines.append("")

    recent = sorted(notes, key=lambda n: n["mtime"], reverse=True)[:recent_n]
    lines.append(f"## Ultimas {len(recent)} notas modificadas")
    lines.append("")
    for n in recent:
        when = n["mtime"].strftime("%Y-%m-%d")
        lines.append(f"- `{when}` [[{n['name']}]] - {n['title']}")
    lines.append("")

    by_folder: dict[str, list[dict]] = defaultdict(list)
    for n in notes:
        by_folder[n["folder"]].append(n)
    lines.append("## Por pasta")
    lines.append("")
    for folder in sorted(by_folder.keys()):
        folder_notes = sorted(by_folder[folder], key=lambda n: n["title"].lower())
        lines.append(f"### `{folder}/` ({len(folder_notes)} notas)")
        lines.append("")
        for n in folder_notes:
            summary = f" - {n['summary']}" if n["summary"] else ""
            lines.append(f"- [[{n['name']}]]{summary}")
        lines.append("")

    tag_counts: Counter = Counter()
    for n in notes:
        for t in n["tags"]:
            tag_counts[t] += 1
    if tag_counts:
        lines.append("## Tags mais frequentes")
        lines.append("")
        for tag, count in tag_counts.most_common(25):
            lines.append(f"- `#{tag}` ({count})")
        lines.append("")

    incoming: Counter = Counter()
    for n in notes:
        for link in n["links"]:
            incoming[link] += 1
    orphans = [n for n in notes
               if not n["links"] and incoming.get(n["name"], 0) == 0]
    if orphans:
        lines.append(f"## Notas orfas ({len(orphans)})")
        lines.append("")
        lines.append("> Sem [[wikilinks]] entrando nem saindo - candidatas a conectar.")
        lines.append("")
        for n in sorted(orphans, key=lambda n: n["mtime"], reverse=True)[:15]:
            lines.append(f"- [[{n['name']}]] (`{n['folder']}/`)")
        if len(orphans) > 15:
            lines.append(f"- ... (+{len(orphans)-15} orfas adicionais)")
        lines.append("")

    lines.append("---")
    lines.append(f"*Gerado em {now} por `scripts/vault_moc.py`.*")
    return "\n".join(lines) + "\n"


def render_session_start_context(notes: list[dict], vault: Path, recent_n: int = 10) -> str:
    """Versao compacta para injetar no SessionStart hook."""
    lines = [f"# Contexto do Vault - {vault.name}", ""]
    lines.append(f"Vault em `{vault}` com **{len(notes)} notas** curadas.")
    lines.append("")
    lines.append(f"## Ultimas {recent_n} notas modificadas")
    lines.append("")
    recent = sorted(notes, key=lambda n: n["mtime"], reverse=True)[:recent_n]
    for n in recent:
        when = n["mtime"].strftime("%Y-%m-%d")
        lines.append(f"- `{when}` **{n['title']}** - `{n['rel']}`")
    lines.append("")
    by_folder: dict[str, int] = defaultdict(int)
    for n in notes:
        by_folder[n["folder"]] += 1
    lines.append("## Estrutura")
    lines.append("")
    for folder, count in sorted(by_folder.items(), key=lambda kv: -kv[1]):
        lines.append(f"- `{folder}/` ({count})")
    lines.append("")
    lines.append(f"**Indice completo:** ler `_MOC.md` no vault.")
    lines.append("")
    lines.append("Ao documentar nova observacao, seguir regras do `CLAUDE.md`: "
                 "escolher pasta certa, checar duplicatas, usar frontmatter, criar [[wikilinks]].")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", type=Path, default=DEFAULT_VAULT,
                    help="Path do vault (default: CLAUDE_VAULT_DIR env ou hardcoded)")
    ap.add_argument("--recent", type=int, default=15)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--stdout", action="store_true",
                    help="Imprime versao compacta (para SessionStart hook)")
    args = ap.parse_args()

    if not args.vault.exists():
        print(f"[moc] vault nao encontrado: {args.vault}", file=sys.stderr)
        return 1

    notes = scan_vault(args.vault)
    if not notes:
        print("[moc] nenhuma nota encontrada", file=sys.stderr)
        return 1

    if args.stdout:
        sys.stdout.write(render_session_start_context(notes, args.vault))
        return 0

    md = render_moc(notes, args.recent)
    if args.dry_run:
        sys.stdout.write(md)
        return 0

    moc_path = args.vault / "_MOC.md"
    moc_path.write_text(md, encoding="utf-8")
    print(f"[moc] gerado: {moc_path} ({len(notes)} notas)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
