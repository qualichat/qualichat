---
name: checkpoint
description: Salva um milestone/marco da sessao atual no Obsidian vault do qualichat como nota permanente. Use quando o usuario disser "checkpoint", "salva isso", "marca esse momento", "registra no vault", ou apos resolver bug importante, decidir arquitetura, descobrir gap teoria-codigo, fechar uma sprint. Nao use para pedidos triviais.
---

# Skill /checkpoint — Salvar milestone no vault qualichat

## Quando usar
- Usuario disse "checkpoint", "salva no vault", "marca esse momento"
- Acabamos de resolver um bug nao-trivial (o raciocinio seria caro de reconstruir)
- Fechamos uma decisao de arquitetura (sprint scope, escolha de chart, refator)
- Descobrimos comportamento novo do qualichat / chat-miner / spaCy / Streamlit
- Fechamos uma sprint da web UI (final de um conjunto de PRs)
- Mapeamos um gap PDF↔codigo relevante

## NAO usar
- Para perguntas triviais ("lista arquivos", "qual comando")
- Quando o conhecimento ja esta em outra nota (prefira editar existente)
- Para commit de codigo (isso ja fica no git log)
- Para aprendizado acionavel pontual (use /insight)

## Dependencias

Esta skill segue a sintaxe do **`obsidian-markdown`** (oficial do kepano/Obsidian)
para wikilinks, callouts, properties YAML. Especificamente:
- Wikilinks: `[[Nome da Nota]]`, `[[Nota#Heading]]`, `[[Nota|display]]`
- Callouts: `> [!note]`, `> [!warning]`, `> [!info]`, `> [!success]`
- Properties YAML no frontmatter (tags como array, nao string)
- Embeds: `![[imagem.png]]`, `![[nota#Heading]]`

## Passo a passo

1. **Verificar duplicata primeiro:**
   ```
   Grep("<palavra-chave>", path="d:/SITES/VSCODE/OUTROS/qualichat/obsidian_vault")
   ```
   Se ja existe nota relacionada, ATUALIZAR ela em vez de criar nova. Exception: se o
   que temos agora invalida a antiga, criar uma nova e adicionar `[[nota-antiga-superada]]`
   com data.

2. **Escolher pasta certa:**
   - `Tese/` — conceitos teoricos primarios (Goffman, Cavalcante, frames, ancoragens, laminacao, maquinacao)
   - `Conceitos/` — conceitos secundarios ou subsidiarios (sub-periodos, sorter cascade, etc)
   - `Codigo/` — arquitetura interna do qualichat (pipeline, frames.py, runtime, sorters)
   - `Gaps/` — discrepancias entre tese/PDF e codigo (ex: Intervalo de Interacao nao implementado)
   - `Insights/` — usar `/insight` em vez de `/checkpoint` para isso
   - `Referencias/` — fontes externas (papers, repos, posts)
   - `Checkpoints/` — marcos de progresso transversais (fim de sprint, deploy, decisao estrategica)

3. **Nome do arquivo** deve conter a data entre parenteses, ex:
   `qualichat - Sprint 3 wrapper-only fechada (2026-05-25).md`

4. **Frontmatter obrigatorio:**
   ```yaml
   ---
   date: 2026-05-25
   type: observation | decision | bug | fix | sprint-close | gap
   tags: [qualichat, sprint, ui, ...]
   sprint: opcional — 1, 2, 3...
   ---
   ```

5. **Estrutura do conteudo (adaptar conforme tipo):**
   ```markdown
   # Titulo descritivo

   ## Contexto
   Uma linha: qual era a situacao.

   ## Descoberta / Decisao / Diagnostico
   O que foi observado/decidido, com evidencia concreta (commits, paths, linhas,
   outputs reais).

   ## Causa raiz (se bug/fix)
   Por que acontecia.

   ## Solucao / Comportamento / Caminho escolhido
   O que foi feito OU como se comporta OU qual rota foi tomada.

   ## Evidencia
   Dados reais: paths, commits, file:line, counts, URLs de deploy.
   Nao inventar.

   ## Implicacao
   O que muda daqui pra frente. Em que casos aplicar.

   ## Relacionados
   - [[outra-nota]]
   - [[outra-nota-2]]
   ```

6. **Escrever com Write tool** no path do vault.

7. **Regenerar MOC** apos escrever (idealmente o Stop hook faz isso, mas em
   caso de checkpoint manual fora de sessao):
   ```
   Bash: python d:/SITES/VSCODE/OUTROS/qualichat/scripts/vault_moc.py
   ```

8. **Responder ao usuario** em 1-2 linhas: caminho da nota criada e links
   relacionados adicionados.

## Principios

- **Honestidade total**: nunca inventar dados. Se nao sei, escrevo "investigar".
- **Evidencia concreta**: file:line, commits (sha7), counts, outputs — nao generalidade.
- **Conectar**: usar [[wikilinks]] para linkar notas existentes.
- **Sem duplicar**: preferir atualizar nota existente.
- **Sem ruido**: nao documentar fatos triviais ja derivaveis do codigo ou ja
  em outra nota.

## Exemplos de nomes

- `qualichat - Sprint 3 wrapper-only fechada (2026-05-25).md`
- `qualichat - Bug latente Machinations vs Fabrications em frames.py667 (2026-05-25).md`
- `qualichat - Decisao surfacear charts CLI vs inventar (2026-04-30).md`
- `tese - Laminacao operacionalizada como links+emails+chamadas+emojis (2026-05-25).md`
- `tese - Maquinacao em portugues = Fabrication em ingles (2026-05-25).md`
- `gap - Intervalo de Interacao 5 charts nao implementados (2026-04-30).md`
