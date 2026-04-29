# Análise de corpus de teste real

> **Privacidade:** os arquivos `.zip` em `docs/chats/` **não estão e nunca
> serão commitados** — são exports reais com nomes e conteúdos de pessoas
> reais. A pasta está em `.gitignore`. Este documento descreve apenas
> métricas agregadas e padrões estruturais — nenhuma mensagem é citada
> textualmente, nenhum nome real é exposto.

## Contexto

O usuário forneceu **11 exports `.zip`** do WhatsApp para validar a
ferramenta com dados reais. O objetivo: confirmar que a v1.5.0 do
qualichat (com o parser refeito sobre `chat-miner`, PRs #9/#10/#13)
processa corretamente o que pesquisadores realmente recebem em campo,
não apenas as fixtures sintéticas.

**Resultado final:** 11 / 11 chats processados, **38.031 mensagens**,
**671 atores anonimizados**, **2.923.036 caracteres totais**, **242
eventos de sistema**. **Dois bugs reais foram encontrados e corrigidos**
durante o teste.

## Corpus

| # | Identificador (nome do grupo) | Tipo (inferido) | Mensagens | Atores | Período (dias) |
|---|-------------------------------|----------------|-----------|--------|----------------|
| 1 | C7S - Amigos Eternos          | Social, amigos | 8.707     | 15     | 3.743          |
| 2 | Clube Positivista Brasileiro: Estudos Sociocráticos | Acadêmico | 181 | 13 | 877      |
| 3 | Dever da Esperança            | Religioso/movimento | 10.940 | 63   | 1.303         |
| 4 | Grupo 25 horas e outros membros | Social, pequeno | 680     | 42     | 991            |
| 5 | Lula 13 ✨Lulaverso ✨ 64       | Político       | 1.456     | 25     | 1.304          |
| 6 | Networking & Parcerias         | Profissional   | 471       | 255    | 445            |
| 7 | O Positivista - Célula Gestora | Governança, mín. | 14      | 8      | 1.090          |
| 8 | ODONTOLOGIA UNIFOR T56         | Acadêmico (turma) | 1.222   | 103    | 1.341         |
| 9 | REDENÇÃO                       | Religioso/movimento | 11.539 | 75    | 1.564         |
| 10 | Sociedade Brasileira de Palestrantes e Oradores I | Profissional | 2.723 | 57 | 315 |
| 11 | Turma Esp. Itaú Cultural       | Acadêmico (turma esporádica) | 98 | 15 | 3.016 |

Todos em **iOS US 12-hour clock** (`[m/d/yy, h:mm:ss AM/PM]`) com locale
inglês — formato moderno do app, gerado via "Exportar conversa" do
WhatsApp iOS recente.

## Bug 1 — U+202F NARROW NO-BREAK SPACE no timestamp

### Sintoma

`Chat()` falhava com `ValueError: No messages parsed from ...` em
**Dever da Esperança** apesar de chat-miner reportar 11.003 linhas
processadas.

### Causa raiz

O iOS atual injeta **U+202F NARROW NO-BREAK SPACE** entre o número de
horas/minutos/segundos e o marcador AM/PM no timestamp. O export tem:

```
[9/12/24, 10:14:22 PM] Author: ...
              ^^^^^
              U+202F (NARROW NBSP), não ASCII space
```

A regex de detecção de "nova mensagem" do chat-miner usa `\s`, que
combina com U+202F. Mas o `_infer_date_author_sep` da chat-miner depende
de o primeiro caractere após `[date]` ser um `]` direto, e várias outras
inferências assumem ASCII space. Com U+202F intercalado, o
`date_author_sep` é detectado mas o downstream falha de modos sutis em
mensagens individuais.

A tabela `_IMPURITIES` em `qualichat/chat.py` já cobria 6 caracteres
invisíveis (LRM, en-space, PDF, LRE, NBSP, non-breaking hyphen) mas
**não U+202F**.

### Fix aplicado

Adicionada uma entrada à tupla `_IMPURITIES`:

```python
(' ', ' '),   # Narrow No-Break Space → space (U+202F, iOS US 12h)
```

Antes do parse, o `_clean_text` substitui U+202F por espaço ASCII normal,
o que desbloqueia o reconhecimento.

### Impacto

Sem o fix, qualquer chat exportado de iOS com locale inglês US (e
provavelmente também outros locales 12h) **não parseia**. Como
pesquisadores usam mistura de devices, esse bug afetaria silenciosamente
todo um subconjunto da base de usuários potenciais.

## Bug 2 — Tolerância a falsos positivos da regex de "nova mensagem"

### Sintoma

Mesmo com o Bug 1 corrigido, **Dever da Esperança** ainda falhava com
`ValueError: not enough values to unpack (expected 2, got 1)` durante o
parse de mensagens individuais.

### Causa raiz

A regex de chat-miner para detectar uma nova mensagem é permissiva:

```python
r"^[‎]?\[?(\d{1,4})([./,-])\d{1,2}\2\d{2,4}(?:\s|,\s)(0?\d|1\d|2[0-4]):([0-5]?\d)"
```

Repare:
- O bracket de abertura `\[?` é **opcional**
- A regex aceita separadores `.`, `/`, `,`, `-`

**Mensagem real do corpus** (parafraseada por privacidade): um membro
encaminhou um trecho de notícia que começava com `16.09.2024 12:55`
(timestamp da agência alemã de notícias). chat-miner viu esse trecho
como uma "nova mensagem", separou o conteúdo em uma raw_message
distinta — sem `[`, sem `]`, sem `author:`. Quando a chat-miner depois
tentou `mess.split(']', 1)` para separar timestamp de autor, retornou
1 elemento e `ValueError`.

Em outras palavras: **uma única mensagem de notícia encaminhada bastou
para envenenar todo o parse.**

### Fix aplicado

Em `_CapturingWhatsAppParser._parse_message` (subclass do qualichat),
envolver a chamada `super()._parse_message(mess)` em `try/except
ValueError` e retornar `None` se o super levantar — tratando como
"não-é-uma-mensagem" silenciosamente.

```python
def _parse_message(self, mess: str):
    try:
        result = super()._parse_message(mess)
    except ValueError:
        # Falso positivo da regex de chat-miner. Treat as not-a-message.
        return None
    if result is not None:
        return result
    # ... continue handling system events
```

### Impacto

Qualquer chat com mensagens encaminhadas que contenham timestamps
embutidos (notícias, calendários, logs colados) seria afetado. Em
corpus de pesquisa real isso é **comum** — pesquisadores estudam
exatamente o tipo de grupo onde notícias são encaminhadas constantemente.

### Recomendação upstream

Os dois fixes acima são contornos no qualichat. **O ideal seria também
abrir um PR no chat-miner** apertando a regex de "nova mensagem":

- Tornar o bracket de abertura **obrigatório** quando `has_brackets` foi
  inferido como `True`
- Validar que a linha contém o `date_author_sep` antes de classificar
  como nova mensagem

Por ora, os fixes ficam locais ao qualichat, garantindo robustez sem
depender de release do chat-miner.

## Padrões estruturais observados

Analisar 11 grupos diversos revela **três "formas" claramente distintas**
que a UI deveria ajudar o pesquisador a identificar:

### 1. Broadcast (top-1 ator > 60% das mensagens)

Um único ator domina o canal; outros são audiência passiva.

| Grupo | Atores | Mensagens | Top-1 share |
|-------|--------|-----------|-------------|
| Lula 13 ✨Lulaverso ✨ 64 | 25 | 1.456 | **86,3%** |
| Grupo 25 horas e outros membros | 42 | 680 | **68,8%** |

Estes parecem **canais de difusão** (campanha política, notícias de
horário fixo) mais do que grupos conversacionais. Charts de "Mensagens
por ator" devem destacar essa concentração — provavelmente com **índice
de Gini** ou similar.

### 2. Conversacional balanceado (top-1 entre ~15% e ~40%)

Grupos onde múltiplos atores participam ativamente. A maior parte do
corpus.

| Grupo | Atores | Top-1 share |
|-------|--------|-------------|
| C7S - Amigos Eternos | 15 | 28,1% |
| Clube Positivista Brasileiro | 13 | 38,7% |
| Dever da Esperança | 63 | 24,0% |
| O Positivista - Célula Gestora | 8 | 28,6% |
| REDENÇÃO | 75 | 17,4% |
| Sociedade Brasileira de Palestrantes I | 57 | 30,8% |
| Turma Itaú Cultural | 15 | 19,4% |

Top-1 entre 17% e 40% sugere distribuição "log-normal" típica de
grupos sociais reais (Goffman seria feliz).

### 3. Distribuído com cauda longa (top-1 < 10%)

Muitos atores, poucas mensagens — predominam **lurkers** (membros que
entram mas raramente postam).

| Grupo | Atores | Mensagens | Top-1 share |
|-------|--------|-----------|-------------|
| Networking & Parcerias | 255 | 471 | **5,1%** |
| ODONTOLOGIA UNIFOR T56 | 103 | 1.222 | **7,4%** |

Networking tem **mais atores que mensagens em 50%** — um profissional
broadcast group com baixa interação. A UI deveria sinalizar isso ao
pesquisador (por exemplo, "78% dos atores nunca enviaram mensagem").

### Picos de período por tipo de grupo

| Tipo de grupo | Pico de período | Pico de sub-período |
|---------------|-----------------|---------------------|
| Social (C7S) | Tarde | Almoço |
| Acadêmico (Estudos Sociocráticos) | Tarde | Trabalho (Tarde) |
| Religioso/movimento (Dever da Esperança) | Tarde | Trabalho (Tarde) |
| Social pequeno (25 horas) | Noite | Transporte (volta) |
| Político (Lulaverso) | Tarde | Almoço |
| Profissional (Networking) | Manhã | Trabalho (Manhã) |
| Governança (Célula Gestora) | Manhã | Acordar/Transporte |
| Acadêmico turma (Odontologia) | Manhã | Trabalho (Manhã) |
| Religioso/movimento (REDENÇÃO) | Manhã | Transporte (volta) |
| Profissional (Palestrantes) | Manhã | Acordar/Transporte |
| Acadêmico esporádico (Itaú Cultural) | Tarde | Almoço |

**Padrão emergente:** grupos profissionais e acadêmicos picam pela manhã
(`work_morning` ou `transport_morning`), grupos sociais e políticos
picam tarde/almoço, grupos religiosos picam em pontos de
transição (tarde/transporte de volta — "depois do trabalho"). Isso
**valida** os labels de sub-período herdados da tese (YLAI_V2.pdf):
eles capturam dimensões reais de uso.

## Implicações para o wireframe v2 e próximos sprints

1. **Heatmap "Dia × Período" no Resumo** — confirmado pelos dados que
   essa visualização SEPARA grupos profissionais de sociais com clareza.
   Mantida no wireframe.

2. **Indicador "shape do grupo" (broadcast / conversacional /
   distribuído)** — é uma feature derivável do índice de Gini ou
   simplesmente do `top_1_share_pct` que pode entrar no Resumo. Não
   estava no wireframe v2 — vou considerar adicionar como Sprint 2.

3. **Alerta "X% dos atores nunca enviaram"** — relevante para grupos
   distribuídos. Derivável de `chat.actors` com filtro `len(messages) ==
   0`. Não estava previsto, fácil de implementar.

4. **Multi-chat support** já é importante** — o pesquisador típico vai
   querer comparar lado a lado dois grupos (ex.: Networking vs Sociedade
   Palestrantes — ambos profissionais mas formatos opostos). O
   wireframe v2 já mostra checkbox de multi-chat na Home; sprint 1
   precisa garantir que a infra (`load_chats(*paths)`) é exposta.

5. **Caso degenerado (apenas 14 mensagens em 1.090 dias)** — Célula
   Gestora é um chat quase inativo. UI precisa lidar gracefully com
   chats minúsculos: alguns charts vão ficar quase vazios, alguns
   testes estatísticos perdem significância. Talvez exibir um aviso
   "amostra pequena, charts podem ser pouco informativos quando n < 50".

6. **Multi-locale ativo na prática** — todos os 11 chats são iOS US
   12h em inglês, mas com nomes/conteúdo em pt-BR. Confirma que
   `enums.py` precisa **mesmo** suportar mistura de timestamp en + body
   pt (já suporta após PR #13).

## Status dos fixes

Os dois fixes foram aplicados na branch `feat/web-ui` (em
`qualichat/chat.py`). **Eles deveriam ser portados para
`feat/parser-chatminer` (PR #9)** quando essa stack for retomada,
porque ali é o lugar conceitual correto. Por enquanto vivem no
feat/web-ui para desbloquear teste local da UI com dados reais.

## O que ainda está aberto

- ❓ **PR upstream no chat-miner** com regex mais estrita — depende de
  decisão sua sobre prioridade
- ❓ **Test fixture com `forwarded_news.txt`** — replicar o padrão do
  Bug 2 em fixture sintética para regression test (sem usar dados
  reais privados)
- ❓ **Test fixture com `narrow_nbsp_us.txt`** — idem para Bug 1
- ❓ **Adicionar índice de Gini** ou métrica de concentração na sidebar
  do Resumo — depende de você sinalizar valor

Posso encaminhar qualquer um desses como próxima micro-tarefa, ou
priorizar Sprint 1 (foundation Streamlit) e voltar a esses depois.
