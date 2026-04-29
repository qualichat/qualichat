# Wireframe — qualichat web UI

Esta pasta contém o wireframe HTML da interface web proposta para o qualichat
(branch `feat/web-ui`). É um documento de design, **não uma especificação
de feature** — alguns elementos refletem o código atual, outros propõem
funcionalidades novas. Esta legenda existe para que ninguém (incluindo o
próprio futuro mantenedor) confunda visão com realidade implementada.

## Como abrir

```bash
# do root do repositório
start docs/wireframes/index.html        # Windows
open  docs/wireframes/index.html        # macOS
xdg-open docs/wireframes/index.html     # Linux
```

Arquivo é self-contained — sem build step, sem dependências locais. Fontes
(EB Garamond, Source Sans 3, JetBrains Mono) são carregadas do Google
Fonts CDN. Navegação por tabs no topo.

## Lineage — origem da nomenclatura métrica

Antes de qualquer coisa, registrar de onde vem o vocabulário do qualichat:

1. **Cavalcante & Hanke (2020)** — `Ancoragens de interação em grupos
   midiatizados: proposta quantiqualitativa` (Comunicação Mídia e Consumo
   v.17, n.50, DOI 10.18568/cmc.v17i49.2227). Define os conceitos
   teóricos: ancoragem, frame, key, lamination, fabrication.

2. **YLAI_V2.pdf** (`docs/YLAI_V2.pdf`) — relatório Power BI de tese,
   15 páginas, set/2018 a abr/2019. **É o blueprint operacional do
   qualichat.** Quase todas as variáveis `Qty_char_X` em `models.py`
   correspondem a `QTD_X` neste relatório:

   | Tese (PDF) | Código (`qualichat/models.py`) |
   |---|---|
   | QTD_Liquidos | `Qty_char_net` |
   | QTD_Texto | `Qty_char_text` |
   | QTD_Mensagens | `Qty_messages` |
   | QTD_Riso | `Qty_char_laughs` |
   | QTD_Pontuacao | `Qty_char_marks` |
   | QTD_Emoji/Simbolo | `Qty_char_emoji` |
   | QTD_Numeros | `Qty_char_numbers` |
   | QTD_Email, QTD_Chamada, QTD_Link | `Qty_char_emails`, `Qty_char_calls`, `Qty_char_links` |
   | Sub-períodos: Descanso, Acordar/Transporte, Trabalho(Manhã), Almoço, Trabalho(Tarde), Transporte, Segundo Expediente | `enums.py:SubPeriod` (mesmos labels) |

   O wireframe inclui uma visualização canônica do relatório de tese: o
   **heatmap "Dia × Período"** na tela de Resumo (PDF página 6 e 8). É
   100% derivável dos dados existentes em `chat.messages` + `SubPeriod`.

   **Análise completa do PDF:** ver [`docs/YLAI_V2-analysis.md`](../YLAI_V2-analysis.md)
   — registro do que foi extraído com confiança, o que foi deduzido e
   quais perguntas permanecem abertas (Utilidade era tagging manual ou
   regra? Idioma é detecção automática? etc).

## Legenda

Cada elemento abaixo recebe uma de três etiquetas:

| Símbolo | Significado |
|--------|-------------|
| 🟢 **Real** | A feature existe em `qualichat/` hoje. O wireframe apenas a visualiza. |
| 🟡 **Derivado** | Visualizável a partir de dados/estruturas que já existem, mas a UI específica não existe. Implementação é "expor o que está lá", sem nova lógica de domínio. |
| 🔴 **Inventado** | Feature nova. Não existe no código. Requer implementação genuína (modelos, persistência, lógica). |

---

## Tela 1 — Setup (primeira execução)

| Elemento | Categoria | Origem |
|----------|-----------|--------|
| Botão "Baixar modelos do spaCy" | 🟢 | `qualichat setup` no CLI faz `download('pt_core_news_md', ...)` e `download('en_core_web_sm', ...)` ([`__main__.py:114-118`](../../qualichat/__main__.py#L114-L118)) |
| Input "Google API key" (opcional) | 🟢 | `setup()` pede `password('Enter your Google API key:')` e salva em `~/.qualichat/config.json` ([`__main__.py:108-112`](../../qualichat/__main__.py#L108-L112)) |
| Pasta de dados `~/.qualichat/` | 🟢 | `utils.py:Config.load()` cria a pasta automaticamente ([`utils.py:57-72`](../../qualichat/utils.py#L57-L72)) |
| Step 03 "Pasta editável" | 🔴 | Hoje a pasta é hardcoded; oferecer override é nova feature |
| Notice de privacidade | 🟡 | Texto novo, alinhado com comportamento real |

**Quando aparece:** primeira execução (quando `~/.qualichat/` não existe)
ou via menu Configurações depois.

---

## Tela 2 — Início (Upload)

| Elemento | Categoria | Origem |
|----------|-----------|--------|
| Drag-drop de `.txt` ou `.zip` | 🟢 | `Chat(path)` aceita ambos via `_extract_txt_from_zip` ([`chat.py:76-93`](../../qualichat/chat.py#L76-L93)) |
| Hint "iOS antigo · iOS novo · Android · pt-BR · en · es · de · it · fr · auto-detectado" | 🟢 | chat-miner faz auto-detect; é factual |
| Checkbox "Anonimizar atores" | 🟢 | `get_random_name()` + fallback `Actor #N` ([`utils.py:95-111`](../../qualichat/utils.py#L95-L111)) |
| Pool de 767 nomes | 🟢 | `books.txt` bundled com Tolstói + Machado de Assis |
| Checkbox "Múltiplos chats" | 🟢 | `load_chats(*paths)` aceita múltiplos paths ([`core.py:69-78`](../../qualichat/core.py#L69-L78)) |
| Bloco "Caderno de campo" (preview da marginália) | 🔴 | Preview do diferencial — a feature em si é inventada |
| Bloco "Sobre o que é isto" | 🟡 | Texto descritivo, alinhado com `README.md` e `docs/methodology.rst` |
| Sidebar "Citar este trabalho → BibTeX / CITATION.cff" | 🟢 | `CITATION.cff` existe (PR #15) |

**Removido em v2:** o radio "Locale forçado" — chat-miner não suporta
override de locale, então oferecer essa opção mentia sobre a capacidade
da ferramenta.

---

## Tela 3 — Resumo (chat carregado)

| Elemento | Categoria | Origem |
|----------|-----------|--------|
| Lede com totais | 🟡 | Derivado de `chat.messages`, `chat.actors`, `chat.system_messages`, min/max de `created_at` |
| Definition list (formato, período, mensagens, system events, atores, densidade) | 🟡 | Tudo derivado de `Chat` instance |
| Linha "Sub-período de pico" no def-list | 🟡 | Derivado de `Message['Day_sub_period']` (já existe em `models.py`) — apenas agrega e mostra o top |
| **Distribuição por tipo de mensagem** (barra horizontal segmentada) | 🟡 | Derivado de `MessageType` enum aplicado a `chat.messages`. Substitui o mini-chart vertical (v1) que ficava dominado pela barra de "texto" 92% |
| **Heatmap "Dia × Período"** | 🟡 | Visualização canônica do relatório de tese (YLAI_V2.pdf p.6). Derivado de `chat.messages` + `Day_period` enum + dia da semana |
| Fórmula ribbon `Qtd_liq_car = total − (...)` | 🟡 | Fórmula está em `docs/methodology.rst` e operacionalizada em `models.py:Message['Qty_char_net']`. Ribbon é UI nova |
| Marginália (textarea + lista de notas datadas) | 🔴 | **Feature nova.** Persistência em `~/.qualichat/notes/<chat>/_resumo.md` |
| Botão "Ir para Frame: Keys" | 🟢 | Roteamento entre frames |

---

## Tela 4 — Resumo (empty state)

| Elemento | Categoria | Origem |
|----------|-----------|--------|
| Mensagem "Nenhum chat carregado" + botão "Ir para Início" | 🟡 | Apenas defesa de UX — sem chat carregado, qualquer tela exceto Início/Setup mostra esse estado |

---

## Tela 5 — Frame: Keys → Lamination

| Elemento | Categoria | Origem |
|----------|-----------|--------|
| Sidebar "Menu Keys" como tree-nav | 🟡 | Os charts existem; a navegação como árvore é convenção UX (inspirada no fluxograma de Cavalcante 2021) |
| **Sidebar Keys completa**: Lamination, Links, Calls, Emails, Textual symbols, Messages, Keyword, Ratings | 🟢 | Todos os 8 métodos de `KeysFrame` em `frames.py` |
| Badge `api` em "Ratings" | 🟢 | `KeysFrame.ratings` requer `config['google_api_key']` ([`frames.py:401`](../../qualichat/frames.py#L401)) |
| **Sidebar Participação completa**: Mensagens por ator, Mensagens por semana, Bots, Repertório de mídia, Estatísticas, Lam. por atores, Fab. por atores | 🟢 | Todos os 7 métodos de `ParticipationStatusFrame` |
| Sidebar Opinião pública: Matriz de polaridade, Linkage temático | 🟢 | Os 2 métodos de `PublicOpinionFrame` |
| Fórmula ribbon `Lamination = links + emails + chamadas + emojis` | 🟡 | Componentes vêm de `KeysFrame.laminations.bars`; ribbon é UI |
| Radio "Sorter: Por época / Por ator" | 🟢 | `@sorters.keys` decorator: `select('Choose your mode:', ['By Time', 'By Actor'])` ([`sorters.py:357-378`](../../qualichat/sorters.py#L357-L378)) |
| Annotation `@sorters.keys` ao lado do label | 🟡 | UI honesta sobre origem — facilita debug |
| Radio "Período: todos / escolher meses" | 🟢 | `_sort_by_time`: `select('Which messages should be selected?', ['All', 'Choose an epoch'])` ([`sorters.py:173-199`](../../qualichat/sorters.py#L173-L199)) |
| Help text sobre multi-select de meses | 🟢 | Quando "Choose an epoch", abre `checkbox('Choose an epoch:', meses)` |
| Chart bar+line | 🟢 | `KeysFrame.laminations` ([`frames.py:227-265`](../../qualichat/frames.py#L227-L265)) |
| Botões "Baixar PNG / HTML interativo" | 🟡 | `Plotly.Figure` tem `to_html()` e `to_image()` nativos |
| Botão "Copiar BibTeX da figura" | 🔴 | Geração automática de BibTeX `@figure{...}` é nova |
| Bloco "Como ler isto" em prosa serif | 🟡 | Texto novo, baseado em `docs/methodology.rst` |
| Notice de divergência D1 inline | 🔴 | `docs/divergences.rst` existe (PR #15), surfaceá-la é nova UI |
| Marginália à direita | 🔴 | Mesma feature inventada da Tela 3 |

---

## Tela 6 — Frame: Keys → Keyword

| Elemento | Categoria | Origem |
|----------|-----------|--------|
| Input "Palavra-chave a buscar" | 🟢 | `KeysFrame.keyword`: `input('Enter the keyword:').ask()` ([`frames.py:182`](../../qualichat/frames.py#L182)) |
| Radio "Classe morfológica: Verbos / Substantivos / Adjetivos" | 🟢 | `_parse_nlp_messages`: `select('Choose a morphological class:', ['Verbs', 'Nouns', 'Adjectives'])` ([`frames.py:104`](../../qualichat/frames.py#L104)) |
| Annotation `spaCy POS` | 🟡 | UI honesta — informa que VERB/NOUN/ADJ são tags POS do spaCy |
| Sorter + Período (mesmos da Lamination) | 🟢 | Decorator `@sorters.keys` aplicado também aqui |
| Wordcloud rendering | 🟢 | `_generate_wordcloud(data)` retorna `WordCloud` com fonte Roboto bundled ([`frames.py:113-125`](../../qualichat/frames.py#L113-L125)) |
| Botão "Exportar tokens (CSV)" | 🔴 | Hoje só renderiza; exportar a lista de tokens NLP é nova |
| Bloco "Como ler isto" | 🟡 | Texto novo |

---

## Tela 7 — Opinião pública → Matriz de polaridade

| Elemento | Categoria | Origem |
|----------|-----------|--------|
| **Notice "Serviço externo · Google Translate"** | 🟢 | `PublicOpinionFrame.matrix_polarity` chama `GoogleTranslator(target='en').translate(...)` ([`frames.py:998`](../../qualichat/frames.py#L998)). Estilo padronizado com a notice de divergência (uma só treatment) |
| Radio "Filtro: apenas acima da média / todos" | 🟢 | Código filtra `if not (len(actor.messages) > average_messages): continue` ([`frames.py:987`](../../qualichat/frames.py#L987)) |
| Input "Limite por ator" | 🔴 | Hoje hardcoded em `actor.messages[:5]` ([`frames.py:991`](../../qualichat/frames.py#L991)). Tornar configurável é nova |
| Chart scatter | 🟢 | `px.scatter(dataframe, x='Actor', y='Figure Polarity', ...)` ([`frames.py:1006`](../../qualichat/frames.py#L1006)) |
| Bloco "Como ler isto" + nota sobre TextBlob | 🟡 | Texto novo, calibragem honesta sobre limitação real |

**Não desenhada:** a tela do `linkage` chart (também em `PublicOpinionFrame`)
que usa `connector.csv` para mapear themes pré-definidos. Sub-item existe
na sidebar; tela em si fica para Sprint 3.

---

## Tela 8 — Exportar

| Elemento | Categoria | Origem |
|----------|-----------|--------|
| Contact sheet de figuras geradas na sessão | 🔴 | **Histórico de figuras geradas não existe** no código. CLI hoje abre cada `fig.show()` como tab nova e esquece. UI precisaria capturar via `runtime.py:capture_figures()` |
| Botão "Baixar todas (.zip)" | 🔴 | Depende do contact sheet existir |
| Citação canônica (BibTeX) | 🟢 | `CITATION.cff` (PR #15) tem o paper-mãe como `preferred-citation` |
| Bloco BibTeX renderizado | 🟡 | Pode ser gerado a partir de `CITATION.cff` via `cffconvert` |
| Archive de marginália da sessão | 🔴 | Depende da feature marginália |
| Botões "Exportar marginália .md / .json" | 🔴 | Mesmo |

---

## Decisões UX que merecem discussão

### Marginália inline (signature element)

Não existe no código. Implementá-la implica:

- Persistência em `~/.qualichat/notes/<chat_basename>/<chart_id>.md`
- Append-only com timestamp ISO
- Editor inline com auto-save
- Indexação para busca cross-chart
- Export agregado da sessão

Custo estimado: 1 sprint inteiro. Benefício: a interface deixa de ser
"ferramenta de visualização" e passa a ser "caderno de campo digital",
diferenciando-a de qualquer dashboard genérico de chat analytics.

**Decisão registrada (2026-04-28):** o usuário (owner pradosystems)
confirmou que quer manter marginália no design e implementar como feature
nova.

### Divergence note inline no chart

D1-D6 estão documentadas em `docs/divergences.rst` (PR #15) por decisão do
usuário em 2026-04-26 ("documentar o que aprendemos com o fluxograma e as
divergencias encontradas! Manter o que temos hoje!").

Mostrar a nota inline no próprio chart afetado é UX nova. Tradeoff:

- **A favor:** honestidade científica máxima
- **Contra:** ruído visual em todos os charts afetados (D1, D2, D3 → 4
  charts no mínimo)

**Recomendação:** manter inline mas com peso visual baixo (já é como está
no wireframe — `notice` com border-left vermelha discreta, sem ícones).

### Sub-período de pico no Resumo

Inspirado no relatório de tese (YLAI_V2.pdf), que faz extensivo uso da
quebra por sub-período. O def-list do Resumo agora inclui "Sub-período de
pico" (ex.: *"Trabalho (Tarde) · 28% do tráfego"*). Os labels são os
mesmos de `enums.py:SubPeriod`, garantindo continuidade com a metodologia
da tese.

### Heatmap Dia × Período

Visualização canônica do relatório de tese (PDF p.6 e p.8). Replicada no
Resumo como bloco padrão. Dados são 100% derivados de `chat.messages` +
`Day_period` enum (já existem). Implementação: agregar mensagens (ou
qualquer métrica) por `(weekday, period)` e renderizar como tabela com
gradient ocre.

---

## Mapa de implementação por sprint

### Sprint 1 — Foundation (1 semana)

Apenas 🟢 e 🟡 — porta CLI pra web sem mudar lógica de domínio.

- Streamlit skeleton + roteamento
- Tela Setup (wrappear `qualichat setup` com botões)
- Upload + parse via `Chat(path)` existente
- Cached parse com `@st.cache_resource`
- Sidebar com nav (lista plana → estilizar como tree em sprint 2)
- Página Resumo com def-list + stack-bar + heatmap
- Empty state em todas as telas que precisam de chat
- Patch de prompts (já implementado em `qualichat/ui/runtime.py`)

### Sprint 2 — Frames principais (1 semana)

- Keys Frame: 8 charts (lamination, links, calls, emails, textual_symbols,
  messages, keyword, ratings) com prompts mapeados pra widgets Streamlit
- Sidebar fluxograma estilizada (tree com `◇`/`└`)
- Botões de export (PNG, HTML) usando Plotly nativo
- Tela Keyword com keyword input + morph class

### Sprint 3 — Frames secundários (1 semana)

- Participation Status (7 charts)
- Public Opinion (matrix_polarity + linkage)
- Treemap mode em participation_status
- Notice de serviço externo (Google Translate)
- Tela Linkage com `connector.csv`

### Sprint 4 — Marginália (1 semana) 🔴

Sprint inteiro pra signature element. Pode ser pulado/adiado.

- Modelo de persistência em `~/.qualichat/notes/`
- Editor inline + auto-save
- Lista de notas anteriores na sidebar
- Export agregado

### Sprint 5 — Polish (1 semana)

- Citação BibTeX (lê `CITATION.cff` via `cffconvert`)
- Contact sheet 🔴 — depende de session history (capturado via `runtime.py`)
- Divergence notes inline (lê `docs/divergences.rst` e mapeia)
- README + screenshots

---

## Stack visual definido

Salvo aqui para futuras iterações — mantém consistência se outro agente
ou contribuidor pegar o trabalho.

| Token | Valor | Uso |
|-------|-------|-----|
| `--pergaminho` | `#F4EFE6` | canvas / surface base |
| `--pergaminho-claro` | `#FAF7F1` | cards / inputs (inset) |
| `--tinta-impressao` | `#1A1814` | texto primário |
| `--sepia-fieldnote` | `#7A6B5A` | texto secundário, metadata |
| `--ocre-encadernacao` | `#B8860B` | emphasis, lamination series, heatmap |
| `--musgo-biblioteca` | `#3B5249` | success, fabrication series |
| `--marginalia-vermelha` | `#922B21` | warnings, divergences (notice padrão) |
| `--toga-academica` | `#1F3A5F` | accent primário, links, nav ativo |

| Tipografia | Família | Peso/Estilo | Uso |
|------------|---------|-------------|-----|
| Headlines | EB Garamond | 500, 24-32px | h1, h2 |
| Body prose | EB Garamond | 400, 17px | parágrafos longos, "como ler isto" |
| Lede / cite | EB Garamond italic | 400, 19px | introduções, fórmula |
| UI labels | Source Sans 3 | 600, 12px uppercase | tabs, field labels |
| Form inputs | Source Sans 3 | 400, 14px | radios, checkboxes |
| Data / mono | JetBrains Mono | 400, 11-15px | números, IDs, timestamps, BibTeX, heatmap cells |

| Espaçamento | Valor | Uso |
|-------------|-------|-----|
| `--s1` | 8px | gap mínimo |
| `--s2` | 16px | gap padrão entre elementos |
| `--s3` | 24px | padding de card |
| `--s4` | 32px | gap entre seções |
| `--s5` | 48px | padding de página |
| `--s6` | 64px | separação maior |

**Depth strategy:** apenas bordas, sem shadows. `1px solid rgba(26,24,20,N)`
com N variando de `0.08` (padrão) a `0.32` (focus).

**Radius:** `0` em cards, `2px` em inputs/badges. Cantos quase retos —
manuscrito não tem rounded corners.

**Notice (warnings) — tratamento padronizado:**
Bloco com `border-left: 3px solid var(--marginalia-vermelha)` + fundo
levemente avermelhado + título uppercase. Variante `notice-info` muda
para ocre. Mesmo treatment para Divergences D1-D6 e para o aviso de
serviço externo (Google Translate).
