Methodology
===========

This page documents the theoretical foundation, terminology and analytical
formulas behind Qualichat, drawing on the project's own published
materials (paper, doctoral thesis, official video, public webinar).

Maintainers should treat this as the source of truth for what the tool
*intends* to compute. For the gap between intent and the current
implementation, see :doc:`divergences`.


Origin and lineage
------------------

Qualichat is a research instrument built to support the ethnographic
study of mediatised groups, with a focus on Brazilian WhatsApp
communities and their political-cultural framings. The relevant lineage:

- **2019** — Fernando Luiz Nobre Cavalcante (also published as
  *Kochav Koren Nobre*) defends his doctoral thesis at UFRN:
  *"Vínculos de Ancoragens e Enquadramentos Temáticos: Olhares
  Itinerantes às Interações Midiatizadas em Grupo"*.
- **2020** — Cavalcante & Hanke publish the foundational paper
  *"Ancoragens de interação em grupos midiatizados: proposta
  quantiqualitativa"* in *Comunicação Mídia e Consumo* v.17 n.50,
  `DOI 10.18568/cmc.v17i49.2227 <https://doi.org/10.18568/cmc.v17i49.2227>`_.
- **2020-2022** — Cavalcante does his postdoc at UNICAMP IEL under
  Prof. Marcelo Buzato, in collaboration with the University of Bremen.
  The American Political Science Association (APSA) provides funding
  through the *Fund for Latino Scholarship* (2020).
- **2021** — Public release of the tool as a Python package, alongside
  two videos on the *Os Dedos* / *Ernest Manheim* channels and an
  installation guide on Medium.
- **2022** — Cavalcante presents the project on the *Escola de Dados*
  webinar `"Qualichat: conhecendo o projeto"
  <https://www.youtube.com/watch?v=drCPx4roX-U>`_ (28/06/2022).

The tool's namesake — *Ernest Manheim* — is a homage to the
Hungarian-American sociologist (1900–2002) whose habilitation thesis
*Die Träger der öffentlichen Meinung* (1933) pioneered the theory of
public opinion as a *social tie* rather than a poll aggregate.


Theoretical foundation
----------------------

Qualichat operationalises a chain of concepts from the sociology of
interaction:

- **Frame analysis** (Erving Goffman, 1974) — interactions are organised
  by interpretive *frames* that participants signal and recognise.
- **Anchorages** (*ancoragens*) — structural elements that ground a
  frame: temporal markers, participant signals, message-type indicators
  (Cavalcante & Hanke, 2020).
- **Symbolic interactionism** — meaning emerges in interaction, not in
  isolated utterances. The participant is read as an **actor** acting
  within a vincular network, not as an isolated user.
- **Public opinion as a tie** — opinion is the polarisation of
  group-level vincular ties under tension, not the sum of individual
  sentiments. This view derives from Manheim's communication theory and
  contrasts with the polling-institute view of public opinion.

A WhatsApp group export, in this framing, is a record of *anchored
interaction*: each line is annotated with timestamp (temporal anchor),
participant (vincular anchor), and message-type marker (formal anchor).
The tool extracts these anchorages and computes derived metrics that
support — but do not replace — qualitative ethnographic reading.


The three frames
----------------

Qualichat exposes three analytical *frames*, each grouping a set of
charts that answer related questions:

Keys
~~~~

The lexical frame. Answers *what is being said and how*.

Charts:

- **Keyword** — wordcloud of co-occurring words around a user-supplied
  term, grouped by morphological class (verbs, nouns, adjectives).
- **Messages** — wordcloud of all messages, grouped by morphological
  class.
- **Laminations** — counts of laminating elements (links, e-mails,
  mentions, emojis) per actor.
- **Links / Calls / E-mails / Textual symbols** — drill-downs of the
  *laminations* chart on a single dimension.
- **Ratings** — YouTube view / like / comment counts for every shared
  YouTube link, retrieved through the
  `qualichat-qualitube <https://github.com/qualichat/qualichat-qualitube>`_
  add-on (developed by Vitor Mussa, UFBA).

Participation Status
~~~~~~~~~~~~~~~~~~~~

The actor-behaviour frame. Answers *who participates, how much, and
when*.

Charts:

- **Messages per Actors / per Weekday** — temporal distribution of
  participation.
- **Message Statistics** — mean and standard deviation of message
  length per actor.
- **Media Repertoire** — domain breakdown of shared links per actor,
  rendered as a treemap or bar chart.
- **Laminations per Actors** — per-actor breakdown of the laminating
  elements (mirrors *Keys → Laminations* but pivoted on actor).
- **Fabrications per Actors** — per-actor breakdown of fabricating
  elements (laughs, punctuation, numbers).
- **Bots** — heuristic bot indicator (see :ref:`bot-heuristic`).

Public Opinion
~~~~~~~~~~~~~~

The framing frame. Answers *in what tone* and *on what theme*.

Charts:

- **Matrix Polarity** — per-actor sentiment polarity (translates each
  message PT→EN via ``deep-translator`` then runs the spaCyTextBlob
  pipeline). Cavalcante intentionally does **not** call this "sentiment
  analysis" — see his caveat in the 2022 webinar regarding the
  philosophical and methodological limits of sentiment quantification.
- **Linkage** — thematic linkage scoring against the bundled
  ``connector.csv`` lexicon. Each message is scored against 21
  pre-defined thematic groups (Friends, Political, Religious,
  Scientific, Family, Green, Health, Spiritual, etc.) and the chat's
  dominant frame is identified.


Defined terms
-------------

The following terms recur in code, charts and academic prose. They have
specific meanings in this project and should not be conflated with
their everyday senses.

Lamination
~~~~~~~~~~

The *laminating* elements of a message — markers that prepare or signal
the discursive move rather than carrying the propositional content.
Following Goffman's *lamination* (layered keying), Cavalcante reads
these as:

- **@-mentions** (calls) — invoking another actor into the frame.
- **Links** — anchoring an external referent.
- **E-mails** — addressing a third party.
- **Emojis / textual symbols** — non-verbal cues.

In the 2022 webinar Cavalcante explains the laminations as "*a
preparação para o jogo discursivo*" — the rhetorical scaffolding around
a message rather than its content.

Fabrication
~~~~~~~~~~~

The *fabricating* elements — markers that destabilise or dissimulate
the literal frame. In Goffman's terms, fabrications are false framings;
in WhatsApp practice they signal informality, irony, performative
distance:

- **Laughs** (``kkk``, ``hehe``, ``hahaha``, regional variants).
- **Punctuation marks** (``?``, ``!``, repeated for emphasis).
- **Numbers** in informal positions.

Net characters (``Qty_char_net``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The textual residue after laminations are stripped — the *unornamented*
referential content of the message.

The official formula, reproduced from the *Keys* flowchart published
with the 2021 installation guide:

.. code-block:: text

    Qtd._liq._car. = Qtd._car._msg.
                     − ( Qtd._car._chamadas
                       + Qtd._car._links
                       + Qtd._car._emails
                       + Qtd._car._emojis/símbolos )

Implemented in :py:mod:`qualichat.models` (see ``Message.__init__``).
The same formula expressed in code:

.. code-block:: python

    net_text = remove_all_incidences(
        self.content,
        message['Qty_char_calls'],
        message['Qty_char_links'],
        message['Qty_char_emails'],
        message['Qty_char_emoji'],
    )

Pure text (``Qty_char_text``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Net characters with fabrications also stripped. The remaining text is
what Cavalcante calls the actor's *pure speech* — the propositional
content with both laminations *and* fabrications removed.

.. code-block:: text

    Qtd._car._text = Qty_char_net
                     − ( Qty_char_laughs
                       + Qty_char_marks
                       + Qty_char_numbers )

Day periods and sub-periods
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each message is tagged with a coarse and a fine temporal anchor based
on the brazilian working-day rhythm:

============  =================  =====================
Period        Hours              Sub-period
============  =================  =====================
Dawn          00:00–05:59        Resting
Morning       06:00–08:59        Transport (morning)
Morning       09:00–11:59        Work (morning)
Evening       12:00–14:59        Lunch
Evening       15:00–17:59        Work (evening)
Night         18:00–20:59        Transport (evening)
Night         21:00–23:59        Second Office Hour
============  =================  =====================

This taxonomy is brazilian-context-specific and not meant to translate
universally.


.. _bot-heuristic:

Bot heuristic
-------------

The ``ParticipationStatusFrame.bots`` chart applies a weighted score to
detect non-human posting behaviour, as described by Cavalcante in the
2022 webinar:

.. code-block:: text

    score = ( chars_net  × 1
            + videos     × 2
            + stickers   × 3 ) / 6

The intuition: human participation produces text (low weight), occasional
media (medium weight), and rarely a stream of stickers (high weight).
Posting *only* high-weight media in tight intervals — Cavalcante cites
"*vídeo, vídeo, vídeo, vídeo*" sequences with sub-second gaps — produces
a high score and high standard deviation, flagging coordinated
inhuman activity.

The heuristic is **explicitly preliminary**. Cavalcante notes in the
webinar that bot detection is an aspiration of the project, not a solved
problem.


Thematic linkage and the ``connector.csv``
------------------------------------------

The ``Public Opinion → Linkage`` chart classifies a chat against 21
thematic groups defined in :file:`qualichat/connector.csv`. Each row of
the CSV is a thematic profile with five typed columns of trigger
keywords:

- **Action** (5 keywords) — verbs that the group performs.
- **Space** (5 keywords) — places the group occupies.
- **Time** (5 keywords) — temporal markers the group uses.
- **Object** (5 keywords) — material referents.
- **Person** (5 keywords) — addressees and protagonists.

The 21 groups currently encoded:

Friends, Political (×2 rows), Religious, Scientific, Scholar,
Co-workers, Family, Green, Innovation, Health care, Spiritual,
Mentoring, Wellness, plus a Brazilian-political bundle keyed on
``lula / bolsonaro / ciro / doria / alckmin``.

The vocabulary is **specific to Brazilian Portuguese politico-cultural
context** as of the 2018-2022 election cycle. Customising the file for
other locales or contexts is a known need (see :doc:`divergences`).


Ethics
------

Cavalcante is explicit about the ethical commitments of using
Qualichat in research:

1. **Prior notice to all group members.** Every actor in the analysed
   group must be informed that conversations will be analysed.
2. **Phone-number anonymisation.** The tool replaces every contact
   identifier with a fictitious display name drawn from
   :file:`qualichat/books.txt` (777 Brazilian-Portuguese public-domain
   literary characters). Even the researcher cannot tell from the
   output whether an actor is from DDD 85 (Ceará) or DDD 11 (São Paulo).
3. **Ethics committee registration.** For research with hidden or
   passive observation, registration with a university ethics committee
   is *necessary*, not optional. In Brazil, this is the
   `Plataforma Brasil <https://plataformabrasil.saude.gov.br/>`_ /
   CONEP system; equivalents apply elsewhere.
4. **No data collection by the tool itself.** Qualichat does not
   collect, transmit or store conversation data. All processing is
   local. The single configuration artefact at
   ``~/.qualichat/config.json`` (Google API key + name mapping) is the
   researcher's responsibility to handle.

These commitments align with the LGPD (Brazil) and the GDPR (EU).


References
----------

**Foundational paper**

.. parsed-literal::

   Cavalcante, F. L. N., & Hanke, M. M. (2020). *Ancoragens de
   interação em grupos midiatizados: proposta quantiqualitativa*.
   Comunicação Mídia e Consumo, 17(50), 536–558.
   https://doi.org/10.18568/cmc.v17i49.2227

**Doctoral thesis**

.. parsed-literal::

   Cavalcante, F. L. N. (2019). *Vínculos de Ancoragens e Enquadramentos
   Temáticos: Olhares Itinerantes às Interações Midiatizadas em Grupo*.
   PhD dissertation, UFRN.

**Methodology flowchart (2021)**

.. parsed-literal::

   Cavalcante, F. L. N. (2021). *Qualichat Menu-Keys Framing Flowchart*.
   https://www.academia.edu/87023706/

**Public-facing materials**

- `Como instalar o Qualichat (Medium, 2021) <https://medium.com/qualichat/como-instalar-o-qualichat-375bc1e35258>`_
- `Os Dedos – Download Qualichat (YouTube, 18/07/2021) <https://www.youtube.com/watch?v=OMHGg3OoaKw>`_
- `Qualichat – Combatendo Fakenews em Grupos de WhatsApp (YouTube, 24/07/2021) <https://www.youtube.com/watch?v=zFARp05xNjY>`_
- `Qualichat: conhecendo o projeto – Webinar Escola de Dados (YouTube, 28/06/2022) <https://www.youtube.com/watch?v=drCPx4roX-U>`_

**Foundational sociology**

- Goffman, E. (1974). *Frame Analysis: An Essay on the Organization of
  Experience.* Harvard University Press.
- Manheim, E. (1933). *Die Träger der öffentlichen Meinung.*
  Habilitationsschrift, Universität Leipzig.
