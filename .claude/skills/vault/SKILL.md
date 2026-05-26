---
name: vault
description: Busca no Obsidian vault do projeto qualichat por um tema, conceito teorico (Goffman, Cavalcante, laminacao, maquinacao, ancoragem), aspecto de codigo (frames.py, models.py, regex, pipeline, sorters) ou aprendizado anterior. Use quando o usuario perguntar "o que a gente tem sobre X", "ja documentamos Y", "busca no vault", "procura no obsidian", ou antes de comecar qualquer investigacao/feature que possa ter sido feita antes.
---

# Skill /vault — Busca no vault qualichat

## Quando usar
- Usuario pergunta "o que temos sobre X", "ja investigamos Y", "tem nota sobre Z"
- Antes de escrever nova nota (checar duplicata — regra do CLAUDE.md do vault)
- Antes de implementar feature nova — conferir se ja foi investigada
- Quando o tema for relacionado a: tese, Goffman, Cavalcante & Hanke, ancoragens, laminacao, maquinacao, fabricacao, frames, sub-periodos, QTD_X, qualichat pipeline, charts, Streamlit UI, regex, parser, chat-miner, sprints

## NAO usar
- Para buscar codigo (use Grep direto em qualichat/*.py)
- Para buscar em memoria MEMORY.md (ja esta carregada)

## Passo a passo

1. **Ler MOC primeiro** (se ainda nao viu nesta sessao):
   ```
   Read("d:/SITES/VSCODE/OUTROS/qualichat/obsidian_vault/_MOC.md")
   ```
   Ele lista todas as notas agrupadas por pasta + recentes + tags.

2. **Buscar por palavra-chave** em conteudo:
   ```
   Grep(<termo>, path="d:/SITES/VSCODE/OUTROS/qualichat/obsidian_vault",
        glob="*.md", output_mode="files_with_matches", -i=true, head_limit=20)
   ```

3. **Ler notas mais relevantes** (top 3-5) em paralelo:
   ```
   Read(<path>)  # para cada um
   ```

4. **Reportar ao usuario** em estrutura clara:
   ```
   ## Encontrei no vault

   **[[titulo-mais-relevante]]** (`pasta/`)
   Resumo da nota em 2-3 linhas.
   Pontos-chave para responder a pergunta.

   **[[titulo-2]]**
   ...

   **Relacionadas (nao abertas):**
   - [[nota3]]
   - [[nota4]]
   ```

5. Se NADA encontrado: reportar explicitamente "vault nao tem nota sobre X".
   NAO inventar conteudo.

## Heuristica de busca

- Conceito teorico (laminacao, frame, ancoragem) — buscar em `Tese/` e `Conceitos/` primeiro
- Aspecto de codigo (frames.py, sorter, regex) — buscar em `Codigo/` primeiro
- Bug resolvido / aprendizado — buscar em `Insights/`
- Gap PDF↔codigo — buscar em `Gaps/`
- Sessoes Claude anteriores — buscar em `Sessoes/`
- Referencia externa (paper, artigo, repo) — buscar em `Referencias/`

Sinonimos teoricos comuns:
- "laminacao" → "layering" + "lamination" + "camadas" + "sobreposicao"
- "maquinacao" → "machination" + "fabrication" (em PT-BR a tese traduz fabrication como maquinacao!) + "manipulacao" + "assimetria"
- "tom" → "key" + "keying" + "tonalizacao" + "retonalizacao"
- "ancoragem" → "bracket" + "anchorage" + "parentese" + "marcador"
- "frame" → "quadro" + "enquadramento" + "frame analysis"

## Regras

- NUNCA inventar conteudo que nao leu.
- Citar a nota como [[wikilink]] para o usuario poder abrir.
- Resumir ao inves de colar tudo — usuario pede detalhes se quiser.
- Se encontrou nota "fix" ou "bug resolvido" — alertar que pode impactar decisao atual.
- Se encontrou nota teorica que contradiz uma assercao tua, REVISAR a propria assercao antes de responder.
