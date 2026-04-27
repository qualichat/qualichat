Usage Guide
===========

A walkthrough of the Qualichat tool from a fresh machine to the first chart
on screen, plus a reference of every frame and chart you can run.

This guide describes the **interactive CLI** (``python -m qualichat load``)
which is the primary way to use Qualichat. For the programmatic API
(building your own pipelines from a notebook), see :doc:`api`.


Prerequisites
-------------

- **Python 3.7.1 or higher** (≤ 3.11 for the most stable experience).
- **Visual Studio C++ Build Tools** on Windows. Several dependencies
  (``wordcloud``, ``pandas``) compile native extensions during install.
- **A WhatsApp chat export** in ``.txt`` form (or ``.zip`` archive,
  starting with v1.5.0). To export, in WhatsApp open the conversation →
  menu → *Export Chat* → *Without Media* → send the file to yourself.
- **(Optional) A Google API key** with access to the *YouTube Data API v3*.
  Only required by the *Ratings* chart, which enriches shared YouTube
  links with view / like / comment counts.


Installation
------------

::

    $ pip install -U qualichat

Then run the one-time setup, which stores your Google API key and
downloads the required spaCy models:

::

    $ python -m qualichat setup

The setup command:

1. Prompts for your Google API key — saved to ``~/.qualichat/config.json``.
2. Downloads two spaCy language models:

   * ``pt_core_news_sm`` — Brazilian Portuguese, used for tokenisation
     and morphological tagging (verbs / nouns / adjectives).
   * ``en_core_web_sm`` — English, used for sentiment analysis after
     translating message bodies via ``deep-translator``.


Loading a chat
--------------

::

    $ python -m qualichat load _chat.txt

Multiple files at once:

::

    $ python -m qualichat load grupo_a.txt grupo_b.txt grupo_c.txt

``.zip`` archives produced by iOS' *Export Chat* feature (which contain
``_chat.txt`` plus media) are accepted directly:

::

    $ python -m qualichat load "Chat with Friends.zip"

Supported timestamp formats include (non-exhaustive):

================================== =====================================
Platform / locale                  Example
================================== =====================================
iOS (recent, with comma)           ``[01/01/2021, 07:52:45] Joel: Hi!``
iOS (legacy, with space)           ``[01/01/2021 07:52:45] Joel: Hi!``
iOS (US, 12-hour)                  ``[1/1/21, 7:52:45 AM] Joel: Hi!``
Android (most locales)             ``01/01/2021, 07:52 - Joel: Hi!``
Android (DE, ``.`` separator)      ``01.01.21, 07:52 - Hans: Hallo``
================================== =====================================

If the parser cannot recognise the file, it raises
``ValueError("No messages parsed from …")`` rather than silently
producing an empty chat.


The interactive REPL
--------------------

After loading, the tool prints an ASCII banner and enters an interactive
loop. Each iteration follows the same shape::

      ┌──────────────────────────┐
      │ Choose a frame:          │   ← KeysFrame /
      │   > Keys                 │     ParticipationStatusFrame /
      │     Participation Status │     PublicOpinionFrame
      │     Public Opinion       │
      └────────────┬─────────────┘
                   ▼
      ┌──────────────────────────┐
      │ Choose your charts:      │   (multi-select with space, Enter)
      │   ☐ links                │
      │   ☐ calls                │
      │   ☐ keyword              │
      │   ☐ ...                  │
      └────────────┬─────────────┘
                   ▼
      ┌──────────────────────────────┐
      │ Optional follow-up prompts:  │
      │  • By Time / By Actor        │
      │  • Choose epoch (Mar 2021…)  │
      │  • Choose media domain       │
      │  • Choose morphological      │
      │    class (Verbs / Nouns /    │
      │    Adjectives)               │
      │  • Enter keyword             │
      └────────────┬─────────────────┘
                   ▼
      ┌──────────────────────────┐
      │ fig.show() opens default │
      │ browser with the chart   │
      └────────────┬─────────────┘
                   ▼
              "Restarting menu..."

Press ``Ctrl-C`` (or pick *cancel* in any menu) to exit.


The three frames
----------------

A *frame* groups charts that answer related questions about the chat.

Keys frame
~~~~~~~~~~

Lexical analyses — what words and tokens appear, by whom and how often.

============================ =================================================
Chart                        Question it answers
============================ =================================================
``keyword``                  Words (verbs / nouns / adjectives) co-occurring
                             with a user-entered term — rendered as a
                             wordcloud.
``messages``                 Most prominent words across the whole chat —
                             wordcloud.
``laminations``              Per-actor counts of links, e-mails, mentions
                             and emojis (bars), with total messages on a
                             secondary line.
``links``                    Same view, but only links.
``calls``                    Only ``@number`` mentions.
``emails``                   Only e-mails.
``textual_symbols``          Punctuation emphasis (``?`` ``!``) plus emojis.
``ratings``                  YouTube view / like / comment counts for shared
                             video URLs (requires a Google API key) — table.
============================ =================================================

Participation Status frame
~~~~~~~~~~~~~~~~~~~~~~~~~~

Behavioural analyses — who speaks, how much, and when.

==================================== ===========================================
Chart                                Question it answers
==================================== ===========================================
``messages_per_actors``              Distribution of message counts per
                                     actor.
``message_statistics``               Mean and standard deviation of message
                                     length per actor.
``messages_per_actors_per_weekday``  Weekly seasonality (Mon–Sun) — split
                                     between user messages and system
                                     messages.
``media_repertoire``                 Which media domains (YouTube,
                                     Telegram, news outlets, …) each actor
                                     shares — bar / average / treemap views.
``laminations_per_actors``           Lamination = links + e-mails + calls +
                                     emojis per actor.
``fabrications_per_actors``          Fabrication = laughs + punctuation +
                                     numbers per actor.
``bots``                             Bot heuristic weighting characters,
                                     videos and stickers per actor.
==================================== ===========================================

Public Opinion frame
~~~~~~~~~~~~~~~~~~~~

Thematic and sentiment analyses — what is the conversation *about*.

================== =================================================================
Chart              Question it answers
================== =================================================================
``matrix_polarity`` Per-actor emotional polarity (translates each message
                    PT → EN, then runs the spaCyTextBlob sentiment pipeline).
``linkage``         Which of the 21 thematic groups in the bundled
                    ``connector.csv`` the conversation maps onto. The default
                    vocabulary is Brazilian-Portuguese political-cultural
                    (Friends, Political, Religious, Scientific, Family, Green,
                    Health, Spiritual, …).
================== =================================================================


Persistent state
----------------

Qualichat keeps a single configuration file across runs:

::

    ~/.qualichat/config.json

It stores:

- The Google API key entered during ``setup``.
- The mapping of real contact names → anonymising display names, keyed by
  the absolute path of the chat file. This means:

  - Loading the same path twice yields the same display names — useful for
    reproducible analyses.
  - Renaming or moving the chat file invalidates the mapping (a new set of
    pseudonyms is generated on next load).

Display names are drawn from a curated list of book characters bundled
with Qualichat. If a chat has more distinct actors than the pool of
names, sequential ``Actor #N`` placeholders are emitted so the load does
not crash.


Outputs
-------

Charts open in your default browser via Plotly's ``fig.show()``. Use
Plotly's built-in *Download as PNG* button to save figures, or take a
screenshot.

When multiple chats are loaded, each chart includes a dropdown to switch
between *All Chats* (aggregated) and each individual chat.

There is currently **no built-in PDF / CSV / batch export**. For headless
or scripted use cases, see the :doc:`api` for direct access to the
underlying ``pandas`` data structures.


End-to-end example
------------------

A minimal session, end to end:

1. Install and set up::

    $ pip install -U qualichat
    $ python -m qualichat setup            # enter API key, download models

2. Export a chat from WhatsApp on your phone (Without Media → send to
   yourself → save as ``_chat.txt``).

3. Load and explore::

    $ python -m qualichat load _chat.txt

4. In the REPL, choose ``Keys`` → ``links`` → *By Time* → *All*.
   A browser tab opens with a bar chart of link counts per month, with
   total messages overlaid on a secondary axis.

5. The menu loops back. Pick another frame / chart, or press ``Ctrl-C``
   to exit.


Where Qualichat does not (yet) shine
------------------------------------

Some friction points worth knowing about:

- **No batch / scripted output.** Every chart is interactive in the
  browser; there is no flag to render to PDF/PNG/CSV without the REPL.
- **Display-name mapping keyed by absolute path.** Moving or renaming
  the chat file generates new pseudonyms — keep paths stable for
  reproducibility.
- **Media treemap renders only the last chat** when several are loaded
  (the per-chat dataframe is overwritten in a tight loop). Use one chat
  at a time when running ``media_repertoire`` → *Treemap*.
- **`linkage` vocabulary is hard-coded in Brazilian Portuguese** for now
  (political-cultural framing). Other languages or contexts require
  editing ``qualichat/connector.csv`` manually.
