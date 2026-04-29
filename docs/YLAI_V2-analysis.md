# Análise de `YLAI_V2.pdf` — relatório Power BI

> **Status:** notas de leitura, work-in-progress.
>
> Este documento registra o que foi extraído do `YLAI_V2.pdf` (ver pasta
> `docs/`) durante a iteração do wireframe da web UI. Marcadores
> `✅ confirmado`, `🟡 deduzido` e `❓ pergunta aberta` separam o que é
> fato textual do que é inferência.
>
> O arquivo serve como referência permanente para quem for trabalhar na
> taxonomia do qualichat ou em features ainda não implementadas
> (Utilidade, Idioma, drill-down de keyword groups).

---

## 1. Identificação do arquivo `✅`

| Atributo | Valor |
|---|---|
| Caminho | `docs/YLAI_V2.pdf` |
| Páginas | 15 |
| Tamanho | ~1,1 MB |
| Criado em | 2021-05-19 01:42 UTC |
| Producer | PDFium |
| Title / Author | (não preenchidos no metadata) |

A geração via PDFium sugere export de browser (provavelmente Chrome
imprimindo pra PDF), o que é compatível com **Power BI Service** (o
relatório web do Microsoft Power BI). Não há texto narrativo: cada página
é um conjunto de gráficos, eixos e legendas, com painel de filtros
lateral.

---

## 2. Período coberto `✅`

`14/09/2018 → 08/04/2019` — 8 meses (rodapé "Data/Hora" das páginas 6, 7,
8, 9 e 14).

Os eixos de "Quantidades por Ano, Mês e Dia" listam consistentemente:
- 2018 setembro
- 2018 outubro
- 2018 novembro
- 2018 dezembro
- 2019 janeiro
- 2019 fevereiro
- 2019 março
- 2019 abril

---

## 3. Métricas (medidas) `✅`

Todas explicitamente nomeadas em legendas e eixos do PDF:

| Métrica no PDF | Provável significado |
|---|---|
| `QTD_Liquidos` | Qtde. de caracteres líquidos (após remover laminadores) |
| `QTD_Texto` | Qtde. de caracteres de texto puro (após remover laminadores e fabricadores) |
| `QTD_Mensagens` | Contagem de mensagens |
| `QTD_Riso` | Caracteres classificados como risada (kkk, hahaha, etc) |
| `QTD_Pontuacao` | Caracteres de pontuação |
| `QTD_Emoji/Simbolo` | Emojis e símbolos |
| `QTD_Numeros` | Caracteres numéricos |
| `QTD_!` | Pontos de exclamação |
| `QTD_?` | Pontos de interrogação |
| `QTD_Email` | E-mails encontrados |
| `QTD_Chamada` | Menções (`@nome`) |
| `QTD_Link` | URLs |

Todas têm também versões `Média de QTD_X`, `Desvio padrão de QTD_X` e
`Mediana de QTD_X` em diferentes páginas.

---

## 4. Dimensões / filtros `✅`

Painel lateral de filtros idêntico em quase todas as páginas:

### Tempo

- **Dia (da semana):** Domingo, Segunda, Terça, Quarta, Quinta, Sexta, Sábado
- **Período:** Madrugada, Manhã, Tarde, Noite
- **Sub Período:** Descanso, Acordar/Transporte, Trabalho(Manhã), Almoço,
  Trabalho(Tarde), Transporte, Segundo Expediente

### Conteúdo

- **Categoria:** (Em branco), Texto/Numero, Simbolos/Expressao, Midia,
  Link/Localizacao, Documento, Sistema
- **Sub Categoria:** (Em branco), Texto, Chamada, Hora/Numero, Hashtag,
  Mensagem Apagada, Mensagem Aguardando, Simbolo, Risada, Expressao,
  Pontuacao, Audio, Audio Ocultado, "I" *(rótulo aparece truncado em
  algumas páginas)*

### Qualitativos (provavelmente tagging manual)

- **Utilidade:** (Em branco), Mensagem Util, Mensagem NaoUtil, Mensagem
  Descartada/Omitida
- **Idioma:** Espanhol, Inglês *(citado apenas na página 10)*

---

## 5. Páginas — sumário das views `✅`

| Pág. | Conteúdo principal |
|------|-------------------|
| 1 | QTD_Liquidos, QTD_Texto, QTD_Mensagens × Ano/Mês — totais e médias/desvio padrão/mediana |
| 2 | QTD_Riso, QTD_Pontuacao, QTD_Emoji/Simbolo, QTD_Numeros × Ano/Mês — totais e médias |
| 3 | QTD_Liquidos × Dia da semana — totais e médias |
| 4 | QTD_Liquidos, QTD_Texto, QTD_Mensagens × Dia + variantes Riso/Pontuacao/Emoji/Numeros × Dia |
| 5 | QTD_Mensagens, QTD_Liquidos × Dia + Riso/Pontuacao/Emoji/Numeros — médias, desvios e medianas |
| 6 | QTD_Mensagens, QTD_Liquidos × Dia × **Período** (heatmap implícito) |
| 7 | Riso, Simbolo × Dia × Período (médias, desvios, medianas) |
| 8 | QTD_Liquidos, QTD_Mensagens × Dia × **Sub Período** (com IDs `1.1, 2.1, 2.2, 3.1, 3.2, 4.1, 4.2`) |
| 9 | Simbolo, Riso × Dia × Sub Período |
| 10 | Contagem por **Utilidade** × Ano/Mês + **Idioma** × Ano/Mês |
| 11 | QTD_!, QTD_? × Ano/Mês — totais, médias, desvios |
| 12 | **Grupos de Palavras-Chave** (Conj_X) e palavras-chave individuais (PC_X) × Ano/Mês |
| 13 | **Categoria** e **Sub Categoria** × Ano/Mês |
| 14 | QTD_Liquidos × QTD_Email/Chamada/Emoji/Link × Dia + QTD_Texto × QTD_Numeros/Pontuacao/Risos × Dia (cross-correlation) |
| 15 | Mesmas cross-correlations × Ano/Mês |

---

## 6. Página 12 — keyword groups (`Conj_X` e `PC_X`) `✅`

Lado esquerdo: barras agregadas por **Conjunto Semântico**:

- `Conj_App_S`
- `Conj_Comunicacao_Direta_S`
- `Conj_Web_S`
- `Conj_Rede_Social_S`
- `Conj_Termos_R_S_S`
- `Conj_Midia_S`

Lado direito: barras por **Palavra-Chave individual**:

- `PC_Email_S`
- `PC_WhatsApp_S`
- `PC_Skype_S`
- `PC_Site_S`
- `PC_Internet_S`
- `PC_Link_S`
- `PC_Facebook_S`
- `PC_Instagram_S`
- `PC_Linkedin_S`
- `PC_Twitter_S`
- `PC_Youtube_S`

> 🟡 **Dedução:** `Conj` = Conjunto, `PC` = Palavra-Chave, `_S` = sufixo
> de sigla/sufixo (origem desconhecida). A estrutura PC dentro de Conj
> sugere o mesmo modelo do `connector.csv` usado por
> `PublicOpinionFrame.linkage`.

---

## 7. Mapeamento PDF → código atual do qualichat `✅`

### Métricas

| PDF (`QTD_*`) | Código (`qualichat/models.py`) |
|---|---|
| QTD_Liquidos | `Qty_char_net` |
| QTD_Texto | `Qty_char_text` |
| QTD_Mensagens | `Qty_messages` (atributo derivado) |
| QTD_Riso | `Qty_char_laughs` |
| QTD_Pontuacao | `Qty_char_marks` |
| QTD_Emoji/Simbolo | `Qty_char_emoji` |
| QTD_Numeros | `Qty_char_numbers` |
| QTD_! | `Qty_char_!` |
| QTD_? | `Qty_char_?` |
| QTD_Email | `Qty_char_emails` |
| QTD_Chamada | `Qty_char_calls` |
| QTD_Link | `Qty_char_links` |

### Sub Período

| PDF | Código (`qualichat/enums.py:SubPeriod`) |
|---|---|
| Descanso | `resting` |
| Acordar/Transporte | `transport_morning` |
| Trabalho(Manhã) | `work_morning` |
| Almoço | `lunch` |
| Trabalho(Tarde) | `work_evening` |
| Transporte | `transport_evening` |
| Segundo Expediente | `second_office_hour` |

Os labels exibidos no CLI/UI seguem exatamente os strings do PDF.

### Período

| PDF | Código (`qualichat/enums.py:Period`) |
|---|---|
| Madrugada | `dawn` |
| Manhã | `morning` |
| Tarde | `evening` |
| Noite | `night` |

---

## 8. Dimensões do PDF que **não** existem no código `✅`

### 8.1 Utilidade

Categoria qualitativa de 3 níveis (`Mensagem Util`, `Mensagem NaoUtil`,
`Mensagem Descartada/Omitida`). **Não há equivalente no código atual.**

> 🟡 **Dedução:** se cada mensagem tem um valor de Utilidade, e o PDF
> mostra *contagens* por mês × utilidade (página 10), foi feito um
> tagging manual ou semi-manual do dataset. Pode ter sido pelo Power
> BI Editor de Consultas com regras (ex.: mensagens muito curtas →
> NaoUtil) ou por anotação direta.
>
> ❓ **Pergunta aberta:** foi tagging manual mensagem-a-mensagem ou
> regra automática? A resposta determina se a feature de Utilidade na
> UI futura precisa ser uma ferramenta de coding qualitativo (NVivo-like)
> ou apenas um conjunto de regras configuráveis.

### 8.2 Idioma

Detecção/tag de idioma (Espanhol, Inglês). Apenas valores baixos no
PDF (3, 89, 62 etc) — sugere uma fração pequena do total (chat
predominantemente em português, com mensagens ocasionais em outros
idiomas).

> 🟡 **Dedução:** poderia ser detecção automática (`langdetect` ou spaCy)
> ou tagging manual. Implementação automatizada é simples e seria nova
> feature útil.

### 8.3 Categoria × Sub Categoria como pivot

Os DADOS para reproduzir essa view existem (campos `Qty_char_X` em
`models.py` cobrem texto, calls, hashtags, símbolos, links etc), mas
**não há chart no qualichat hoje** que faça pivot Categoria × Sub
Categoria como tabela ou heatmap.

### 8.4 Heatmap Dia × Período / Dia × Sub Período

Visualização canônica das páginas 6 e 8. Não há chart equivalente no
qualichat. Dados são totalmente derivados de `chat.messages` +
`Day_period` / `Day_sub_period` que já estão em `models.py`.

### 8.5 Cross-correlação visual de métricas

Páginas 14 e 15 mostram **dois eixos Y simultâneos** com métricas
diferentes (ex.: QTD_Liquidos no eixo esquerdo vs QTD_Email/Chamada/Link
no eixo direito). Permite ler "quando QTD_Liquidos sobe, qual dos
laminadores acompanha?".

`KeysFrame.laminations` já faz algo parecido (eixo principal = barras
laminadoras, eixo secundário = QTD_Mensagens), mas a cross-correlação
do PDF é mais flexível — qualquer par de métricas pode ser cruzado.

---

## 9. O que ainda não entendi `❓`

### 9.1 Autoria e propriedade

> "Parte dos gráficos consideraram essa teoria em minha tese"
> — usuário, 2026-04-28

A frase sugere que o PDF é o relatório da tese **do usuário** (vitorprado).
Não há metadados no PDF que confirmem (Title e Author estão vazios). Se
de fato é a tese do usuário, isso explica por que ele:
- Tem domínio sobre a metodologia do qualichat (foi pesquisador-usuário
  antes de mantenedor)
- Herdou o projeto qualichat (passou a manter a ferramenta que usou
  para a própria tese)

### 9.2 Natureza do chat analisado

Não há nada no PDF que identifique o grupo: tema, contexto, número de
participantes, propósito. Pelo volume (≈ 4 mil mensagens em pico mensal,
≈ 100 mil caracteres líquidos em pico mensal), é um grupo de tamanho
médio-grande, com atividade contínua por 8 meses.

> 🟡 **Dedução prévia que retiro:** eu havia associado o pico de
> outubro/2018 à eleição presidencial brasileira (1º turno em 07/10).
> Isso pressupõe que o chat é político — não tenho evidência. O pico
> pode refletir qualquer outro fenômeno temporal (semestre acadêmico,
> sprint de trabalho, calendário religioso, etc).

### 9.3 IDs de Sub Período (página 8)

O eixo da página 8 lista `ID_Subperiodo 1.1, 2.1, 2.2, 3.1, 3.2, 4.1, 4.2`.

> 🟡 **Dedução plausível:** esquema hierárquico onde primeiro número =
> Período (1=Madrugada, 2=Manhã, 3=Tarde, 4=Noite) e segundo número =
> sub-divisão dentro do período. Ex.: 2.1=Acordar/Transporte (manhã
> cedo), 2.2=Trabalho(Manhã) (manhã produtiva); 3.1=Almoço (início da
> tarde), 3.2=Trabalho(Tarde); 4.1=Transporte (início da noite),
> 4.2=Segundo Expediente.
>
> Mas isso é encaixe lógico — não é confirmado por nenhum texto do PDF.

### 9.4 Sufixos `_S` e `Conj_Termos_R_S_S`

O sufixo `_S` aparece em todos os Conj e PC da página 12. Pode ser:
- Marcador de "Soma" (como o Power BI agrega medidas)
- Marcador de "Sigla" (categorias siglares)
- Algo específico do schema do dataset

`Conj_Termos_R_S_S` tem sufixo duplo `_S_S` o que reforça que é
sufixação de Power BI, não nomenclatura semântica.

### 9.5 Categoria "Sub Categoria — I"

Em algumas páginas o painel de Sub Categoria mostra um valor truncado
chamado `I` (página 1, linha 104; página 2, linha 236; etc). Pode ser:
- "Imagem" truncado pela renderização do PDF
- Valor literal de uma categoria
- Artefato de extração

Sem ver o PDF original renderizado, não dá pra confirmar.

---

## 10. Implicações para o wireframe e a UI futura

### 10.1 O que já foi aplicado no wireframe v2

- **Heatmap "Dia × Período"** na tela Resumo (replica páginas 6 e 8 do PDF)
- **"Sub-período de pico"** no def-list do Resumo (usa `enums.py:SubPeriod`,
  cuja taxonomia vem do PDF)
- Seção "Lineage" na README do wireframe documenta o mapeamento `QTD_X →
  Qty_char_X` e cita o PDF como blueprint operacional ao lado de
  Cavalcante & Hanke (2020)

### 10.2 O que pode entrar em sprints futuros

- **Utilidade** (Sprint 5+) — depende de decisão sobre tagging manual
  vs regra automática. Se manual, vira feature similar à marginália
  (persistência local, append-only, reversível). Se regra, é apenas um
  filtro configurável.
- **Idioma** (Sprint 3) — detecção automática via `langdetect`. Adiciona
  dimensão `Language` em `Message` e expõe filtro na sidebar.
- **Categoria × Sub Categoria pivot** (Sprint 3) — chart adicional em
  Participation Status, derivável dos campos atuais sem mudar `models.py`.
- **Cross-correlação flexível de métricas** (Sprint 5+) — UI permite
  selecionar dois `Qty_char_X` e plotar ambos com eixos secundários.

### 10.3 O que precisa de decisão antes de implementar

| Feature | Decisão pendente |
|---|---|
| Utilidade | Tagging manual ou regra? |
| Idioma | Detecção automática suficiente, ou também tagging manual? |
| Conj/PC drill-down | Reutilizar `connector.csv` existente ou nova estrutura? |
| Heatmap default | Métrica padrão do heatmap = QTD_Liquidos médio (como na tese), ou QTD_Mensagens? |

---

## 11. Resumo executivo

O PDF é uma fotografia do estado da metodologia do qualichat **antes** do
código atual existir como Python package. Os campos, métricas, períodos
e nomenclatura do código foram **importados quase 1:1** deste relatório
de Power BI.

Há, porém, **dimensões qualitativas no PDF (Utilidade, Idioma) que nunca
chegaram ao código** — provavelmente porque exigiam tagging manual ou
detecção que ainda não existia em 2021 quando o pacote foi escrito por
kyomi. Essas dimensões representam **gaps deliberados ou acidentais**
entre a metodologia da tese e a ferramenta que a opera.

A web UI proposta no wireframe v2 reduz alguns desses gaps ao surfaceá-los
(heatmap Dia × Período, sub-período de pico no Resumo) e abre caminho
para os outros (Utilidade e Idioma) serem implementados como sprints
futuros sem quebrar a metodologia herdada.
