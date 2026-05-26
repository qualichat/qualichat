---
name: insight
description: Captura um aprendizado estruturado no vault do qualichat — problema, tentativas, solucao, licao acionavel. Use IMEDIATAMENTE apos resolver bug nao-trivial, validar comportamento inesperado, descobrir conexao teoria-codigo, ou quando usuario diz "insight", "aprendizado", "anota isso que aprendemos". Diferente de /checkpoint (que documenta estado), /insight documenta APRENDIZADO acionavel. Use PROATIVAMENTE — se voce acabou de resolver algo dificil, invoque sem esperar o usuario pedir.
---

# Skill /insight — Captura de aprendizado para qualichat

## Quando usar PROATIVAMENTE

Invoque esta skill SEM o usuario pedir quando:

- Voce acabou de resolver bug que demorou >3 tentativas
- Descobriu comportamento de biblioteca/API nao documentado (chat-miner, spaCy, Streamlit, Plotly)
- Pesquisou na web (ou leu PDF/artigo) e achou algo que muda como interpretamos o codigo
- Identificou gap entre tese (Cavalcante & Hanke) e implementacao no codigo
- Eliminou uma hipotese errada (aprendizado negativo tambem vale)
- Descobriu que sua propria compreensao anterior estava errada (CRITICO documentar)
- Usuario disse: "insight", "aprendemos", "anota isso", "registra o que aprendemos"

## Diferenca para /checkpoint

| Skill | O que documenta | Exemplo qualichat |
| --- | --- | --- |
| `/checkpoint` | **Estado** do sistema apos milestone | "Sprint 3 fechada com 7 charts ParticipationStatusFrame surfacados via run_chart" |
| `/insight` | **Aprendizado** acionavel para o futuro | "Maquinacao em PT (Cavalcante 2020) = Fabrication em EN (Goffman 1974). O codigo chama `fabrication` o que a teoria PT chama maquinacao." |

Insights viram fonte de decisao futura. Checkpoints viram historico de progresso.

## Estrutura obrigatoria da nota

```markdown
---
title: Insight — <frase curta>
date: YYYY-MM-DD
type: insight
tags:
  - insight
  - <area>           # tese, codigo, ui, deploy, parser
  - <subarea>        # frames, regex, plotly, chat-miner
severity: low | medium | high   # quanto custou aprender
confidence: speculative | likely | confirmed
---

# Insight — <titulo>

## Problema / Pergunta
Uma linha: o que estavamos tentando resolver ou entender.

## Tentativas (o que NAO funcionou)
- [x] Abordagem A — falhou porque X
- [x] Abordagem B — falhou porque Y

Documentar o que nao funcionou eh tao importante quanto o que funcionou.
Previne repetir o erro.

## O que funcionou
Descricao tecnica concreta com comando/codigo/path/valor real.
NAO generalidade. NAO "configurar direito".

## Por que funcionou (mecanismo)
Explicacao causal. Se voce nao sabe, ESCREVA "nao investigado".
Nao invente.

## Licao acionavel
Uma frase que voce vai aplicar no futuro:
"Daqui pra frente, quando <situacao>, fazer <acao>."

## Evidencia
- Comando/codigo que validou:
- Output real:
- Arquivo:linha:
- Commit / PDF pagina:
- Data/hora do teste:

## Escopo
- [x] Aplica-se a: <sistema/versao>
- [ ] NAO aplica-se a: <caso excluido>

## Relacionados
- [[insight anterior se houver]]
- [[nota que esse insight invalida, se houver]]
```

## Escolha de pasta

| Pasta | Quando |
| --- | --- |
| `Insights/` | Aprendizado generico cross-area (workflow, ferramenta, processo) |
| `Tese/` | Insight teorico sobre Cavalcante/Hanke/Goffman ou interpretacao do PDF |
| `Codigo/` | Insight sobre arquitetura interna ou bug de qualichat |
| `Gaps/` | Discrepancia recem-descoberta entre tese e codigo |
| `Referencias/` | Descoberta sobre fonte externa (paper, lib, repo) |

Se nao tem certeza, use `Insights/`.

## Nome do arquivo

`Insight - <topico curto> (YYYY-MM-DD).md`

Exemplo: `Insight - Maquinacao PT = Fabrication EN Goffman (2026-05-25).md`

## Passos da execucao

1. Verifique duplicata com Grep no vault:
   ```
   Grep("<palavra-chave>", path="d:/SITES/VSCODE/OUTROS/qualichat/obsidian_vault", glob="*.md")
   ```
   Se existe nota sobre o mesmo tema, ATUALIZE em vez de criar nova.
2. Escolha pasta (ver tabela acima).
3. Escreva arquivo com frontmatter completo (Write tool).
4. Use `> [!danger]`, `> [!warning]`, `> [!success]` callouts para destacar pontos
   criticos.
5. Conecte com `[[wikilinks]]` a notas relacionadas (especialmente `[[Cavalcante-Hanke-2020]]`
   ou `[[Goffman-1974]]` se for teorico).
6. Regenere MOC (o Stop hook faz isso, mas em caso manual):
   ```
   python d:/SITES/VSCODE/OUTROS/qualichat/scripts/vault_moc.py
   ```
7. Reporte ao usuario em 1-2 linhas com caminho da nota.

## Regras absolutas

- **NUNCA inventar** — se nao sabe o porque, escreve "nao investigado".
- **Evidencia concreta** — paths, comandos, outputs, file:line, paginas de PDF.
- **Licao acionavel** — se nao da pra aplicar no futuro, nao eh insight.
- **Preferir atualizar** a criar nova nota.
- **Aprendizado negativo conta** — "X nao funciona" tem valor.
- **Corrigir compreensao previa eh sagrado** — se voce mudou de ideia sobre algo,
  documentar EXATAMENTE o que pensava antes, o que faz mudar, e a evidencia. Isso
  protege voce (e quem vier depois) de regredir.

## Exemplo completo (caso qualichat real)

```markdown
---
title: Insight — Maquinacao em PT = Fabrication em EN, codigo confunde com 'resíduos texturais'
date: 2026-05-25
type: insight
tags: [insight, tese, codigo, frames, terminologia]
severity: high
confidence: confirmed
---

# Insight — Maquinacao PT = Fabrication EN (Goffman)

## Problema
Como o codigo `qualichat/frames.py:fabrications_per_actors` se relaciona com a
teoria? "Fabricacao" no codigo significa o mesmo que "fabrication" em Goffman?

## Tentativas
- [x] Inferir pelo nome do metodo — Levou a interpretar "fabricacao" como
      "residuos texturais que dao textura" (errado!)
- [x] Olhar so o codigo e a memoria-resumo — perdi a referencia teorica original

## O que funcionou
Ler Cavalcante & Hanke (2020) "Ancoragens de Interacao em Grupos Midiatizados"
direto do PDF (revistacmc.espm.br/revistacmc/article/view/2227). Paginas 8-9:

> "[...] desde os niveis onde os atores estao mais familiarizados com os codigos
> de interacao, intitulados de tons (keys), ate as maquinacoes (fabrications),
> as quais, por uma relacao assimetrica, pelo menos um dos atores desconhece as
> convencoes da interacao."

E pagina 17:
> "E a oportunidade de explicitar maquinacoes e tonalizacoes dos atores do grupo
> midiatizado."

## Por que funcionou
Goffman (1974) cunhou tres conceitos: Keys, Fabrications, Layerings.
Cavalcante & Hanke traduziram para PT-BR como: Tons, Maquinacoes, Laminacoes.
O codigo qualichat usa "Lamination" (OK) e "Fabrication" (mal traduzido — em
PT a tese chama Maquinacao). A string `'Machinations per Actors'` em
`frames.py:667` era a traducao correta que ficou esquecida no bug-condicional.

## Licao acionavel
Daqui pra frente, ao ler/escrever sobre qualichat:
- "Fabrication" no codigo = "Maquinacao" na tese = "Fabrication" em Goffman ENG
- Risos/marcas/numeros NAO sao "fabricacao" em si — sao MARCADORES para detectar
  maquinacoes e tons (pagina 17)
- O bug em frames.py:667 (`if result == 'Machinations per Actors'`) torna o ramo
  `_fabrications_per_actors` morto — fix pendente.

## Evidencia
- PDF: docs/Cavalcante-Hanke-2020.pdf (baixado de revistacmc.espm.br/.../2227/pdf/7920)
- Paginas: 8 (definicao maquinacao), 9 (laminacoes), 12 (Qntd_Caract_Total), 17 (operacionalizacao)
- Codigo: qualichat/frames.py:656-670 (bug latente confirmado)

## Escopo
- [x] Aplica-se a: toda interpretacao teorica do qualichat
- [x] Aplica-se a: artefato docs/qualichat-pipeline.html (precisa correcao)
- [ ] NAO aplica-se a: codigo de parsing (que e independente da teoria)

## Relacionados
- [[Cavalcante-Hanke-2020]]
- [[tese - Operacionalizacao das 4 ancoragens]]
- [[Codigo - Bug latente Machinations em frames.py667]]
```
