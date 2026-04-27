Divergences between specification and implementation
====================================================

This page documents where the current code departs from the analytical
specification published in 2021, with a frank assessment of severity
and the maintainers' standing decision for each item.

The point of the page is **not** to call out bugs. The current
behaviour has been in production since approximately v1.3 and is
familiar to existing users; correcting any individual divergence would
be a behaviour change that affects ongoing research workflows. The
maintainers' default is therefore *preserve current behaviour, document
the gap*. Each item below records that decision so it can be revisited
deliberately by a future maintainer (or by the project's creator) when
appropriate.

For the analytical foundation against which these are compared, see
:doc:`methodology`.


Source of truth
---------------

The specification is the **Keys frame flowchart** included as the
opening figure of *Como instalar o Qualichat* (Medium, 2021), and
republished as a one-page document on Academia.edu under the title
*Qualichat Menu-Keys Framing Flowchart* (2021). The flowchart is the
only published map of the menu hierarchy and its expected outputs.

No equivalent published flowcharts have been located for the
*Participation Status* or *Public Opinion* frames. The divergences
listed below are therefore restricted to the *Keys* frame; the other
two frames cannot be audited the same way without consulting the
project's creator or recovering the missing diagrams.


Summary table
-------------

============== =========================================== ==================== ===============================
Severity       Item                                        Code reference       Decision
============== =========================================== ==================== ===============================
🔴 Critical    `laminations` chart shows components,       ``frames.py:227-265`` Keep current behaviour
               not the net-character residue
🔴 Critical    `messages` chart only renders a wordcloud,  ``frames.py:204-225`` Keep current behaviour
               not the character-count panels
🔴 Critical    `keyword` chart produces a single wordcloud ``frames.py:174-201`` Keep current behaviour
               for the chosen morphological class, not                          (Open issue for review)
               the three simultaneous wordclouds the
               flowchart specifies
🟡 Medium      Sorting modes: only "By Time" / "By Actor"  ``sorters.py:362-378`` Keep current behaviour
               are offered; the flowchart's "By Group"
               mode is absent
🟡 Cosmetic    The flowchart's terminal label "Gráfico de  multiple              No action needed
               Relevância" is not used in the UI
🟢 Addition    `ratings` chart exists in code but not in   ``frames.py:395-480`` Keep — added 2022 with
               the 2021 flowchart                                                ``qualichat-qualitube``
============== =========================================== ==================== ===============================


Detailed analysis
-----------------

D1 — `laminations` chart shows the components, not the residue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Specification.** The flowchart specifies that the *Laminações* node
yields *Quantidade líquida de caracteres* — the net-character residue
that remains after the laminating elements are subtracted. The formula
is stated explicitly:

.. code-block:: text

    Qtd._liq._car. = Qtd._car._msg.
                     − ( Qtd._car._chamadas
                       + Qtd._car._links
                       + Qtd._car._emails
                       + Qtd._car._emojis/símbolos )

**Current implementation** (``KeysFrame.laminations``,
``frames.py:227-265``). The chart plots **the laminations themselves**
as four bar series — links, e-mails, calls, emojis — with the message
count overlaid as a line. The net-character figure is computed
upstream (``Qty_char_net`` in :py:mod:`qualichat.models`) but never
appears in this chart's output.

**Severity: critical (semantic).** The chart produces information that
is *related* to the spec (showing the components instead of the
residue is the same conceptual surface viewed from the inverse
direction), but a researcher reading the chart and following the
flowchart's promise would be expecting a different number on the
y-axis. The discrepancy is masked because the chart's title says
"*Laminations*", which is technically what is plotted.

**Decision.** Preserve current behaviour. Restoring the spec would
mean changing what *every existing user* of this chart sees — and
several drill-down charts (``links``, ``calls``, ``emails``) re-use the
component pattern, so consistency matters.

A future PR could add a *new* chart called ``net_text`` (or rename
the current ``laminations`` to ``laminating_components`` and add
``laminations_net``) without breaking existing flows.


D2 — `messages` chart skips the character-count panels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Specification.** The flowchart's *Mensagens* node has four downstream
outputs:

1. *Total de caracteres da mensagem* (total character count)
2. *Total de caracteres da mensagem por lexical* (character count per
   morphological class)
3. *Quantidade de verbos* / *substantivos* / *adjetivos* (word counts
   per morphological class)
4. (Implicit) the wordcloud is treated as a fourth, separate output.

**Current implementation** (``KeysFrame.messages``, ``frames.py:204-225``).
The chart prompts for a single morphological class and produces a
single wordcloud for it. Outputs 1, 2 and 3 from the spec are absent.

**Severity: critical (analytical).** The four spec outputs together
let a researcher compare *which class carries the message* — does
this group's discourse anchor in nouns (referents) or verbs (action)
or adjectives (judgement)? The wordcloud alone does not surface that
contrast.

**Decision.** Preserve current behaviour. Adding the three count
panels is a chart redesign, not a bug fix; it changes the rendering
flow significantly.


D3 — `keyword` chart yields one wordcloud, not three
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Specification.** The flowchart's *Pal.-chave* sub-flow shows three
parallel wordclouds — *Nuv. pal. de verbos por palavra-chave*, *Nuv.
pal. de substantivos por palavra-chave*, *Nuv. pal. de adjetivos por
palavra-chave* — produced **simultaneously**, not as user-selectable
alternatives.

**Current implementation** (``KeysFrame.keyword``, ``frames.py:174-201``).
The chart prompts the user to pick **one** morphological class, then
generates a single wordcloud filtered to that class.

**Severity: critical (analytical).** The same logic as D2: comparing
the three classes side by side is the analytical move; offering them
as a one-of-three choice forces the researcher to do three runs and
hold the comparison in memory, which is fragile.

**Decision.** Preserve current behaviour. This is the most defensible
*candidate for a future fix*, because:

- The change is a UX rearrangement (run the inner loop three times
  and emit three wordclouds) without changing any data or formula.
- The performance cost is bounded (3× tokenisation per chat).
- It restores fidelity to the spec without any architectural impact.

A maintenance PR that adds an opt-in ``All classes`` option to the
existing prompt would deliver the spec behaviour without breaking the
existing ``one class at a time`` workflow.


D4 — Missing "By Group" sorting mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Specification.** The flowchart's bottom panel shows three
*Preparação por quadros* modes — *Quadros por tempo*, *Quadros por
ator*, *Quadros por grupo* — each with its own *Seleção específica*
prompt feeding into the final relevance chart.

**Current implementation** (``sorters.keys`` decorator,
``sorters.py:362-378``). Only two modes are offered: ``By Time`` and
``By Actor``.

**Severity: medium.** *Quadros por grupo* would only matter when
multiple chats are loaded — and even then, the existing dropdown on
the rendered Plotly figure (``All Chats / chat_a / chat_b``) provides
inter-chat navigation post-hoc.

**Decision.** Preserve current behaviour. The existing dropdown
covers the practical need; adding a third sorting branch would
require a new sorter helper (``_sort_by_group``) without obvious
analytical gain.


D5 — `ratings` chart exists in code but not in the flowchart
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Specification.** The 2021 flowchart contains no *Ratings* node.

**Current implementation** (``KeysFrame.ratings``, ``frames.py:395-480``).
The chart fetches YouTube view / like / comment counts for every
shared YouTube link in the chat, using
:py:mod:`qualichat-qualitube` (an add-on by Vitor Mussa, UFBA).

**Severity: addition (not a regression).** Cavalcante mentions the
qualitube integration explicitly in the 2022 webinar as a *new*
collaboration with UFBA, post-dating the 2021 flowchart. The chart is
therefore a deliberate extension, not an undocumented drift.

**Decision.** No action needed. Ensure the methodology page records
this as an addition (it does — see :doc:`methodology`).


Items still to be audited
-------------------------

The following audits are pending because the corresponding published
specifications have not been located:

- The complete flowchart for the *Participation Status* frame.
- The complete flowchart for the *Public Opinion* frame.
- The exact list of expected outputs for each chart in those frames.

Anyone with access to those documents (or to the creator) is
encouraged to open an issue or PR that completes this page.
