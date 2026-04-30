# Session Handoff — Qualichat web UI

> **Para quem está pegando o trabalho:** este documento captura o estado
> do projeto ao fim da sessão de **2026-04-30**, com tudo que precisa
> pra continuar sem perder contexto. Memória persistente em
> `~/.claude/projects/d--SITES-VSCODE-OUTROS-qualichat/memory/` é
> automaticamente carregada.

---

## TL;DR — onde estamos

- **App live em produção:** https://qualichat.streamlit.app/ ✅
- **Branch:** `feat/web-ui` (10 commits ahead of `chore/modern-tooling`)
- **Sprints concluídas:** 1 (foundation) + 2 (Frame: Keys com 8 charts)
- **Sprints pendentes:** 3 (Participação + Op. Pública + insights da análise dos 4 PDFs)
- **Análise importante recém-feita:** `docs/graficos-analysis.md` mapeia os 4 PDFs em `docs/graficos/` contra o código

## Tarefa imediata na próxima sessão

**Continuar análise visual das páginas que ficaram sem ser olhadas:**
`docs/graficos/YLAI_V2_Usuario.pdf` páginas **6, 7, 8, 9, 10, 11**.

PNGs já renderizados em **1867×1065 (sob 2000px)** em
`C:/temp/qc-graficos/YLAI_V2_Usuario_p{6,7,8,9,10,11}.png` —
basta chamar `Read` neles. Conteúdo provável (já confirmado por
extração de texto): treemaps Usuário × Dia/Período/Sub-Período +
cross-tabs de QTD_Simbolo/Riso por dimensão.

Atualizar `docs/graficos-analysis.md` com observações específicas das
páginas 6-11 quando confirmar visualmente.

---

## Estado do código

### Branch e commits

```
local + remoto: feat/web-ui
de6306e... + 4 commits posteriores
9c89df5  chore(deploy): touch requirements.txt to force fresh build
7fb4448  chore(ui): expose env versions on Setup page when spaCy import fails
de6306e  fix(deploy): bump spaCy 3.7→3.8 + drop numpy<2 pin
d8cb39b  chore: ignore docs/logo/ source assets
547e290  feat(ui): apply project logo to header + favicon
8816450  feat(ui): read google_api_key from Streamlit Cloud Secrets
7cc1259  fix(deploy): install qualichat package itself in Streamlit Cloud
3c78708  feat(ui): web UI sprints 1+2 — Streamlit interface with Frame: Keys
37e6fe9  docs: web UI wireframe + thesis blueprint + test corpus analysis
640ad7d  fix(parser): tolerate iOS U+202F NBSP and chat-miner false-positives
```

(de6306e foi o que finalmente desbloqueou o deploy. O usuário fez
"Reboot" no Streamlit Cloud Manage app pra forçar pegar o commit
após dois builds intermediários terem ficado em cache.)

### Ambiente local

- venv: `d:/SITES/VSCODE/OUTROS/qualichat/.venv/`
- Python 3.10.0
- numpy 2.2.6 · spacy 3.8.14 · polars 1.40.1 · pandas 2.3.3
- spaCy models pt_core_news_sm + en_core_web_sm carregados ✅
- Streamlit 1.57.0 + playwright + pymupdf instalados

### Streamlit Cloud config

- App URL: `qualichat.streamlit.app`
- Branch: `feat/web-ui`
- Main file: `qualichat/ui/app.py`
- Python: 3.11
- Secrets: `google_api_key` configurado pelo usuário
- Quando deploy stuck → user clica "Reboot" no Manage app

---

## Arquitetura UI (já implementada)

```
qualichat/ui/
├── __init__.py              entry point (launch())
├── app.py                   Home/Upload page
├── runtime.py               monkey-patch select/checkbox/input + capture fig
├── styling.py               CSS tokens + injection
├── state.py                 session_state wrappers
├── pipeline.py              cached parse @st.cache_resource
├── assets/
│   ├── qualichat-logo-icon.png  (36×36 no header + favicon)
│   └── qualichat-logo-full.png  (não usado ainda)
├── components/
│   ├── chrome.py            header + sidebar + bootstrap
│   ├── empty_state.py       "nenhum chat carregado"
│   ├── summary.py           Resumo: lede + def-list + stack-bar + heatmap
│   └── chart_runner.py      KEYS_CHARTS spec + build_answers (Sprint 2)
└── pages/
    ├── 1_Resumo.py          ✓ funcional com chat real
    ├── 2_Keys.py            ✓ 8 charts via runtime.run_chart()
    ├── 3_Participacao.py    🔴 stub (Sprint 3)
    ├── 4_Opiniao_Publica.py 🔴 stub (Sprint 3)
    ├── 5_Exportar.py        🔴 stub (Sprint 5)
    └── 9_Setup.py           ✓ detecta spaCy models + API key + env diagnostic
```

### Charts funcionais em produção

- **Resumo:** lede em PT, def-list (incluindo sub-período de pico),
  stack-bar de tipos de mensagem, heatmap Plotly Dia × Período
- **Frame: Keys** (8 sub-charts via radio):
  - Lamination, Links, Calls, Emails, Textual symbols (bar+line)
  - Messages, Keyword (wordcloud com NLP spaCy)
  - Ratings (tabela YouTube — precisa API key)
- **Setup:** detecta spaCy models, configura Google API key, mostra
  versões instaladas se algo quebrar

---

## Bugs corrigidos durante esta sessão

1. **U+202F NBSP no parser** ([qualichat/chat.py](qualichat/chat.py))
   — iOS US 12h tinha narrow no-break space que chat-miner não
   processava. Adicionado ao `_IMPURITIES`.
2. **ValueError tolerance no parser** — encaminhamentos de notícias
   com data tipo "16.09.2024 12:55" eram interpretados como nova
   mensagem por chat-miner e quebravam. `_CapturingWhatsAppParser` agora
   tolera.
3. **numpy 2.x ABI mismatch no deploy** — primeiro errei pinando
   `numpy<2`, depois descobri que polars/pandas vêm compilados pra
   numpy 2.x. Solução final: `spacy>=3.8` (que suporta numpy 2.x).
4. **CSS contrast nos sidebar/widget labels** — Streamlit emotion-CSS
   sobrescrevia minhas cores com `rgb(49,51,63)` claro contra
   pergaminho. Resolvido com regras `!important` aninhadas em
   `[data-testid="stSidebar"]` e `[data-testid="stMainBlockContainer"]`.
5. **`.replace(',', '.')` global** estragava vírgulas narrativas em
   "anonimizadas, por padrão" → "anonimizadas. por padrão". Substituído
   por função `_fmt_int()` localizada.
6. **`st.page_link(icon='◇')`** rejeitado (Streamlit só aceita emoji).
   CSS injeta `◇` via `::before` agora.
7. **Auto-nav do Streamlit aparecendo redundante** com a nav decorativa
   — escondido via CSS, navegação real via `st.page_link`.

---

## Fixtures de teste

### Fixtures sintéticas (para testes públicos / CI / Streamlit Cloud)

`tests/fixtures/*.txt` — 7 arquivos, 5-20 linhas cada, sem dados reais.
Usei `ios_old_pt.txt` para o E2E test em produção (privacy-safe).

### Corpus real (privado, gitignored)

`docs/chats/` — 11 chats reais do usuário (38.031 mensagens, 671 atores).
**NUNCA committar.** Já está em `.gitignore`.

Ver análise em `docs/chat-test-corpus-analysis.md` (privacy-safe).

---

## Análise dos 4 PDFs em docs/graficos/ (recém-concluída)

> **Localização:** `docs/graficos/` (gitignored — dados privados)
> **PNGs renderizados:** `C:/temp/qc-graficos/*.png` em 1867×1065
> **Análise documentada:** `docs/graficos-analysis.md`

### Páginas analisadas visualmente nesta sessão

✅ Vistas:
- `YLAI_V2_Tempo_p{1,2,3,4,5}.png` (todas)
- `YLAI_V2_Emojis_p{1,2,3}.png` (todas)
- `YLAI_V2_Usuario_p{1,2,3,4,5}.png`

❌ Por ler na próxima sessão:
- `YLAI_V2_Usuario_p{6,7,8,9,10,11}.png` — 6 páginas pendentes
- (Texto extraído já mostra: treemaps + bars de QTD_Simbolo/Riso × dia/período. Mas vale confirmar visual.)

### Descoberta principal: Intervalo de Interação

`YLAI_V2_Tempo.pdf` inteiro (5 páginas) descreve uma família de charts
**que não existe no código atual** — gap temporal entre mensagens
consecutivas, em 16 buckets finos ou 6 grupos coarse.

**Detalhes em** `docs/graficos-analysis.md` seção "YLAI_V2_Tempo.pdf".

---

## Decisões pendentes (não resolvidas — preciso do usuário)

1. **Faixas exatas dos 6 grupos de Intervalo de Interação** — bucket
   fino → grupo, mapping não está escrito no PDF.
2. **Gap entre mensagens GLOBAIS ou DO MESMO ATOR?** — semantica
   diferente.
3. **Drill-down PC_X individual** — `connector.csv` precisa estender ou
   já tem a info?
4. **Composição visual dos treemaps Usuário × Tempo** — labels
   específicos sugerem rótulos custom no nível folha.

Documento essas perguntas em `docs/graficos-analysis.md` seção "Decisões
pendentes" também.

---

## Priorização sugerida (ainda aguardando aprovação do usuário)

### Tier 1 — alto valor, baixo custo

- [ ] Heatmap Sub-Período no Resumo
- [ ] Ranking global de emojis (chart novo em Keys)
- [ ] Drill-down PC_X individual (estender `linkage`)

### Tier 2 — alto valor, médio custo

- [ ] **Frame: Tempo** — novo frame com 5 charts de Intervalo de Interação
- [ ] Treemap Usuário × Dia/Período/Sub-Período
- [ ] Cross-tab Categoria × Sub-Categoria × Usuário

### Tier 3 — alto custo, depende de decisões

- [ ] Utilidade tagging (manual coding)
- [ ] Idioma detection
- [ ] Generalizar Médias/Desvio/Mediana pra todas métricas

---

## Comandos para retomar

### Local dev (Streamlit)

```bash
cd "d:/SITES/VSCODE/OUTROS/qualichat"
.venv/Scripts/python.exe -m streamlit run qualichat/ui/app.py \
    --server.port 8501 --server.headless true \
    --browser.gatherUsageStats false
```

### Re-renderizar PDFs com tamanho seguro

```python
import pymupdf
from pathlib import Path
OUT = Path(r'C:/temp/qc-graficos')
OUT.mkdir(parents=True, exist_ok=True)
for fn in ['YLAI_V2_Emojis.pdf', 'YLAI_V2_Tempo.pdf', 'YLAI_V2_Usuario.pdf']:
    src = Path(r'd:/SITES/VSCODE/OUTROS/qualichat/docs/graficos') / fn
    doc = pymupdf.open(str(src))
    for i, page in enumerate(doc, 1):
        # dpi=70 → 1867×1065 (sob 2000px)
        pix = page.get_pixmap(dpi=70)
        pix.save(str(OUT / f'{fn[:-4]}_p{i}.png'))
    doc.close()
```

### Test E2E em produção

```bash
.venv/Scripts/python.exe C:/temp/qc_prod_test.py
```

(O script existe em `C:/temp/qc_prod_test.py` da última sessão. Faz
upload + navega + tenta gerar Lamination.)

### Re-deploy stuck

Usuário precisa clicar **Reboot** no Manage app de share.streamlit.io.
Não tem CLI para forçar.

---

## Arquivos novos criados nesta sessão

```
docs/
├── graficos/                    🔒 gitignored (privacy)
│   ├── YLAI_V2.pdf
│   ├── YLAI_V2_Emojis.pdf
│   ├── YLAI_V2_Tempo.pdf
│   └── YLAI_V2_Usuario.pdf
├── graficos-analysis.md         ← análise detalhada dos PDFs (commitável)
└── SESSION_HANDOFF.md           ← este arquivo
```

**Decisão:** committar `graficos-analysis.md` e `SESSION_HANDOFF.md`?
São derivados (não contêm dados privados — só estrutura analítica e
mapping para o código). **Sim, devem ser committados.**
