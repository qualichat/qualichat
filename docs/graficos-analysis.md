# Análise de `docs/graficos/` — 4 PDFs de referência

> **Status:** análise sistemática dos 4 PDFs em `docs/graficos/` confrontados
> com a implementação atual em `qualichat/frames.py`. Identifica o que já
> existe, o que é derivável dos dados existentes, e o que precisa de
> nova lógica de domínio.
>
> Os PDFs em `docs/graficos/` são privados (citam dados reais da tese do
> usuário) — adicionados a `.gitignore` se ainda não estiverem.

## Inventário

| Arquivo | Páginas | Foco | Período |
|---------|---------|------|---------|
| `YLAI_V2.pdf` | 15 | Dashboard mãe — todas as métricas × Mês × Dia × Categoria | set/2018 → abr/2019 |
| `YLAI_V2_Tempo.pdf` | 5 | **Intervalo de Interação** (gap entre mensagens) | mesmo |
| `YLAI_V2_Emojis.pdf` | 3 | Emojis: ranking global, drill-down por emoji, cross-tab usuário×emoji | mesmo |
| `YLAI_V2_Usuario.pdf` | 11 | Tudo pivotado por usuário (cada página um corte de métrica) | mesmo |

`YLAI_V2.pdf` já está documentado em `docs/YLAI_V2-analysis.md`.
Esta análise cobre os 3 novos.

---

## YLAI_V2_Tempo.pdf — Intervalo de Interação

**Conceito central:** gap temporal entre mensagens consecutivas como
indicador de qualidade da interação. Operacionalizado em **dois níveis**:

### Buckets finos (16 categorias) — página 2

```
0..30s · 30s..1m · 1m..5m · 5m..10m · 10m..30m · 30m..1h · 1h..3h ·
3h..6h · 6h..12h · 12h..1d · 1d..3d · 3d..7d · 7d..30d · 30d..6m ·
6m..1y · 1y+
```

### Grupos (6 categorias) — página 1

```
1 · Interações Super Rápidas   (provavelmente 0..30s ∪ 30s..1m)
2 · Interações Rápidas         (provavelmente 1m..5m ∪ 5m..10m)
3 · Interações Regulares       (provavelmente 10m..30m ∪ 30m..1h)
4 · Interações Demoradas       (provavelmente 1h..3h ∪ 3h..6h ∪ 6h..12h)
5 · Intervalos Curtos          (provavelmente 12h..1d ∪ 1d..3d ∪ 3d..7d)
6 · Intervalos Longos          (provavelmente 7d..30d ∪ 30d..6m ∪ 6m..1y ∪ 1y+)
```

> ⚠️ **Faixas dos grupos não estão escritas explicitamente no PDF** —
> a inferência acima é dedução visual da ordem dos buckets dentro de
> cada grupo nos charts compostos. Antes de implementar, **confirmar
> com o usuário** ou com a documentação da tese.

### Cortes do PDF (5 páginas)

| Pág | Title | Cortes |
|-----|-------|--------|
| 1 | Intervalo de Interação (Grupos) × Tempo | Mês × Dia × Período × Sub-Período |
| 2 | Intervalo de Interação (Tempo fino) × Tempo | mesmo, com 16 buckets em vez de 6 grupos |
| 3 | Intervalo de Interação × Usuário | bars + composição por ator |
| 4 | Intervalo de Interação × Tipo de Mensagem | composição por categoria/sub-categoria |
| 5 | Intervalo de Interação × Composição das Mensagens | média/desvio/mediana de QTD_Caracteres por grupo |

### Status na implementação

🔴 **Inteiramente novo.** Nenhum chart em `qualichat/frames.py` mede
intervalos entre mensagens. Implementação requer:

1. Calcular `gaps[i] = messages[i].created_at - messages[i-1].created_at`
   por par consecutivo (ou por par consecutivo do mesmo ator, decisão
   pendente)
2. Categorizar cada gap em um dos 16 buckets ou 6 grupos
3. Cross-tabs com Mês/Dia/Período/Sub-Período/Usuário/Tipo já é trivial
   uma vez que cada gap esteja anotado com o `MessageType` da mensagem
   subsequente

**Custo estimado:** 1 sprint dedicado (Sprint 3.5 ou 4). Sem dependência
externa, só lógica nova.

---

## YLAI_V2_Emojis.pdf — Emojis

### Página 1 — ranking global

| Coluna | Conteúdo |
|--------|----------|
| Decimal | Codepoint Unicode (ex: `128514` = `0x1F602` = 😂) |
| Emoji | Glyph |
| QTD | Total de ocorrências no chat |

Top 10 do PDF: `😂 126 · ❤️ 120 · 👏 90 · 🤣 61 · 😍 57 · ☮ 34 · 😱 26 · 🙏 24 · 👍 ...`

Charts à direita:
- "Contagem de Índice por Usuário e Usuário" — bars de uso de emoji por
  ator (Duchamp domina visualmente)
- "Contagem de Índice por Ano, Mês e Usuário" — linha por ator ao
  longo dos meses
- "Contagem de Índice por Dia e Usuário" — bars por dia da semana
- "Contagem de Índice por Sub Período e Usuário" — bars por sub-período

### Página 2 — drill-down de emoji selecionado

Slider `QTD_Ocorrencia_Emoji: 1 — 267` filtra emojis pela frequência. Ao
selecionar um emoji específico (ex: 127877 = 🎅), os 4 charts da página
1 são re-renderizados restritos àquele emoji.

Filtro adicional à direita: emoticons textuais (`:( :'( :) :)) :* :/ :B :D :P ;)`)
— são patterns de **caractere** distintos dos emojis Unicode. Implica
que o sistema também precisa detectar emoticons textuais (já há uma
regex `EMOTICONS_RE` em `qualichat/regex.py`).

### Página 3 — cross-tab Usuário × Emoji

Duas barras horizontais lado a lado:
- "Contagem de Índice por Usuário e Emoji" — para cada usuário, quais
  emojis usa (composição)
- "Contagem de Índice por Decimal, Emoji e Usuário" — para cada emoji,
  quais usuários usam (composição)

### Status na implementação

🟡 **Derivável dos dados existentes.** O campo `Message['Qty_char_emoji']`
já retorna a lista de emojis encontrados (via lib `emojis`). Falta
apenas:

1. Agregar emojis em ranking global (chart novo)
2. Decompor por usuário/tempo (cross-tabs, mesmos sorters de Keys)
3. Drill-down por emoji específico (selectbox + filtro)
4. Detecção de emoticons textuais (`EMOTICONS_RE` já existe em `regex.py`,
   já usado em `Qty_char_emoticons`)

**Custo estimado:** 1 sub-sprint dentro de Sprint 3 ou 4. Não há novo
dado, só agregação.

---

## YLAI_V2_Usuario.pdf — Pivot por usuário

11 páginas com a mesma estrutura: dois charts por página (Quantidades /
Médias) cyclando pelas variáveis `QTD_X`. Equivale a `YLAI_V2.pdf` mas
**sempre pivotado por Usuário** em vez de Mês.

| Pág | Variáveis no chart top | Variáveis no chart médio |
|-----|------------------------|---------------------------|
| 1 | QTD_Liquidos · QTD_Texto · QTD_Mensagens | médias + desvio padrão + mediana |
| 2 | QTD_Riso · QTD_Pontuacao · QTD_Simbolo · QTD_Numero · QTD_Mensagens | médias correspondentes |
| 3 | QTD_! · QTD_? · QTD_Mensagens | médias |
| 4 | Conj_App_S · Conj_Comunicacao_Direta_S · Conj_Web_S · Conj_Rede_Social_S · Conj_Termos_R_S_S · Conj_Midia_S | PC_Email · PC_Whatsapp · PC_Skype · PC_Site · PC_Internet · PC_Link · PC_Facebook · PC_Instagram · PC_Linkedin · ... |
| 5 | QTD_Mensagens × Ano/Mês × Usuário (line) | mesma view com bars |
| 6 | QTD_Liquidos × Usuário × Dia (treemap) + QTD_Mensagens × Dia × Usuário | QTD_Mensagens × Usuário × Dia (treemap) |
| 7 | QTD_Liquidos × Usuário × Período (treemap) | Contagem × Usuário × Período (treemap) |
| 8 | QTD_Liquidos × Usuário × Sub-Período (treemap) | Contagem × Usuário × Sub-Período (treemap) |
| 9 | QTD_Mensagens × Usuário × Categoria (bars) | × Sub-Categoria (bars) |
| 10 | QTD_Simbolo × Usuário × Período | QTD_Riso × Usuário × Período |
| 11 | QTD_Simbolo × Usuário × Dia | QTD_Riso × Usuário × Dia |

### Status na implementação

🟡🟢 Mistura de coberturas:

| Conteúdo | Status |
|---------|--------|
| QTD_Liquidos/Texto/Mensagens × Usuário (pág 1) | 🟢 `messages_per_actors` cobre exatamente |
| Médias + desvio padrão + mediana × Usuário (pág 1) | 🟡 `message_statistics` faz para net/text — generalizar para todas as métricas |
| QTD_Riso/Pontuacao/Simbolo/Numero × Usuário (pág 2) | 🟡 dados existem (`fabrications_per_actors` cobre laughs+marks+numbers, mas falta breakdown por símbolo) |
| QTD_! e QTD_? × Usuário (pág 3) | 🟡 dados em `Qty_char_!` e `Qty_char_?` mas chart específico não existe |
| Conj_X e PC_X × Usuário (pág 4) | 🟡 `linkage` agrega via `connector.csv` mas não pivota por ator nem faz drill-down de PC individual |
| Treemaps Usuário × Dia/Período/Sub-Período (pág 6-8) | 🔴 **chart treemap é diferente do que existe** — temos `media_treemap` mas é por domínio de URL, não por matriz Usuário × Tempo |
| QTD_Mensagens × Usuário × Categoria/Sub-Categoria (pág 9) | 🟡 dados em `MessageType` enum + `Day_period` etc; pivot falta |
| QTD_Simbolo/Riso × Usuário × Período/Dia (pág 10-11) | 🟡 dados existem; pivot falta |

---

## Mapping consolidado: PDF → código

### Já coberto (🟢)

| Chart no PDF | Função em `qualichat/frames.py` |
|--------------|----------------------------------|
| Lamination (links + emails + chamadas + emojis × tempo/ator) | `KeysFrame.laminations` |
| Links/Calls/Emails individuais | `KeysFrame.{links,calls,emails}` |
| Textual symbols (marks + emojis) | `KeysFrame.textual_symbols` |
| Wordcloud por keyword/morph | `KeysFrame.{keyword,messages}` |
| YouTube ratings | `KeysFrame.ratings` |
| Mensagens por ator | `ParticipationStatusFrame.messages_per_actors` |
| Mensagens por dia da semana (User/System) | `ParticipationStatusFrame.messages_per_actors_per_weekday` |
| Estatísticas (avg/sd net/text) | `ParticipationStatusFrame.message_statistics` |
| Bots (Index/Components) | `ParticipationStatusFrame.bots` |
| Repertório de mídia | `ParticipationStatusFrame.media_repertoire` |
| Lam por ator (avg/total) | `ParticipationStatusFrame.laminations_per_actors` |
| Fab por ator (avg/total) | `ParticipationStatusFrame.fabrications_per_actors` |
| Polaridade scatter | `PublicOpinionFrame.matrix_polarity` |
| Linkage temático (Conj_X agregado) | `PublicOpinionFrame.linkage` |

### Derivável dos dados (🟡 — implementar como nova UI sem mudar `models.py`)

| Chart no PDF | O que falta |
|--------------|-------------|
| **Heatmap Dia × Período / Sub-Período** (canonical da tese) | Já no wireframe v2 do Resumo; precisa reproduzir em mais granularidades |
| **Treemap Usuário × Dia/Período/Sub-Período** (Usuario pág 6-8) | Plotly `treemap` com `(actor, period_axis)` como hierarquia |
| **Médias + Desvio + Mediana trio para QUALQUER métrica × Usuário** (Usuario pág 1-3) | Generalização do `message_statistics` |
| **Cross-tab Categoria × Sub-Categoria × Usuário** (Usuario pág 9) | Pivot novo, dados em `MessageType` |
| **Drill-down PC_X individual × Usuário** (Usuario pág 4) | `linkage` lê `connector.csv` mas só agrega por Conj_X; expor PC_X individuais é leitura adicional do mesmo CSV |
| **Ranking global de emojis** (Emojis pág 1) | Counter de `Qty_char_emoji` em todas as mensagens, ordenado |
| **Drill-down de emoji específico** (Emojis pág 2) | Selectbox + filter chain |
| **Cross-tab Usuário × Emoji composição** (Emojis pág 3) | Stacked bars de `(actor, emoji) → count` |
| **Filtro por emoticons textuais** (`:( :) :D :P :*`) | `EMOTICONS_RE` já existe em `regex.py`; expor o resultado como um chart paralelo aos emojis Unicode |

### Inteiramente novo (🔴 — exige nova lógica de domínio)

| Feature | Custo | Onde encaixaria |
|---------|-------|-----------------|
| **Intervalo de Interação** (Tempo.pdf inteiro) — gap entre mensagens consecutivas, categorizado em 16 buckets ou 6 grupos | 1 sprint | Novo frame `IntervalFrame` ou seção em `KeysFrame` |
| **Utilidade tagging** (mencionado em YLAI_V2.pdf, não nos novos 3) | 1 sprint | Já documentado em `docs/YLAI_V2-analysis.md` — seção 8.1 |
| **Idioma detection** (mencionado em YLAI_V2.pdf) | 1 sub-sprint | Já documentado em `docs/YLAI_V2-analysis.md` — seção 8.2 |

---

## Decisões pendentes (perguntas para o usuário)

Antes de implementar qualquer um destes, preciso confirmar:

1. **Faixas dos 6 grupos de Intervalo de Interação** (Super Rápidas, Rápidas,
   Regulares, Demoradas, Curtos, Longos) — que buckets finos pertencem
   a cada grupo? A inferência acima é dedução visual.

2. **Gap calculado entre mensagens consecutivas globais ou consecutivas do mesmo ator?**
   "Tempo de resposta de A para a mensagem anterior de B" é diferente de
   "tempo de A para a mensagem anterior de A".

3. **Composição visual dos treemaps Usuário × Tempo** (Usuario pág 6-8) —
   o PDF mostra labels de tempo dentro dos retângulos de cada ator.
   Plotly suporta hierarquia `(actor → period → value)` nativamente, mas
   os labels específicos (ex: "Trabalho(Tarde) 5 Mil") sugerem rótulos
   custom no nível folha.

4. **Drill-down de PC_X individual** — `connector.csv` define os mapeamentos
   `(palavra) → grupo`. Para drill-down precisamos preservar a palavra
   original, não só o grupo. Verificar se o CSV atual já tem essa info
   ou se precisa ser estendido.

5. **Privacidade dos PDFs** — `docs/graficos/*.pdf` deve ser adicionado
   ao `.gitignore`? Eles citam dados reais (nomes de atores anonimizados
   sim, mas o conjunto + métricas pode ser identificável).

---

## Priorização sugerida (input do usuário)

Em ordem de **impacto analítico vs custo de implementação**:

### Tier 1 (alta valor, baixo custo — Sprint 3)

- [ ] Heatmap Usuário × Sub-Período (variação do que já temos no Resumo)
- [ ] Ranking global de emojis (chart novo no Keys, derivável)
- [ ] Drill-down PC_X individual (estender `linkage`)

### Tier 2 (alto valor, custo médio — Sprint 4)

- [ ] **Intervalo de Interação** (Tempo.pdf inteiro)
- [ ] Treemap Usuário × Dia/Período (Usuario pág 6-8)
- [ ] Cross-tab Categoria × Sub-Categoria

### Tier 3 (alto custo, depende de decisões — Sprint 5+)

- [ ] Utilidade tagging (manual coding)
- [ ] Idioma detection
- [ ] Médias/Desvio/Mediana para CADA métrica × Usuário (generalização)

---

## Implicações para o wireframe v2

O wireframe atual foi desenhado **antes** desta análise. Algumas adições
naturais:

- Sidebar "Frame: Tempo" (novo) com os charts de Intervalo de Interação
- Sub-itens de Keys ganham "Emojis" (ranking + drill-down)
- Resumo ganha mais um heatmap (Sub-Período em vez/além de Período)
- Página de Usuário independente (centralizando os 11 cortes do
  Usuario.pdf) — opcional, alternativa: estes pivots ficam *dentro*
  de Participação como sub-charts cycláveis
