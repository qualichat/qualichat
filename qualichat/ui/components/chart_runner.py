"""
qualichat.ui.components.chart_runner
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bridge between Streamlit widgets and the prompt-driven CLI charts of
:mod:`qualichat.frames`. Collects answers from the UI, builds the queue
in the exact order the chart will pop them, then drives the chart via
:func:`qualichat.ui.runtime.run_chart`.

Each chart variant is described by a :class:`ChartSpec`. The spec
declares which extra prompts the chart asks (keyword text, morphological
class) and whether external services are required (Google API key for
Ratings).

For Sprint 2 we assume **single-chat** sessions; multi-chat scenarios
need a per-chat answer cascade and arrive in Sprint 3.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Sequence


__all__ = (
    'ChartSpec',
    'KEYS_CHARTS',
    'build_answers',
    'enumerate_months',
    'enumerate_actors',
)


@dataclass(frozen=True)
class ChartSpec:
    """Static description of a chart variant in :class:`KeysFrame`."""

    label: str
    """Human-readable label shown in the picker (e.g. 'Lamination')."""

    method: str
    """Method name on the frame (e.g. 'laminations')."""

    chart_key: str
    """Title-cased key used by ``frame.charts[...]`` (e.g. 'Laminations')."""

    description: str
    """One-paragraph description shown above the chart controls."""

    has_keyword: bool = False
    """Whether the chart asks ``input('Enter the keyword:')``."""

    has_morph: bool = False
    """Whether the chart asks ``select('Choose a morphological class:')``."""

    needs_api: bool = False
    """Whether the chart requires ``config['google_api_key']``."""

    is_wordcloud: bool = False
    """Renders a wordcloud (different layout). Informational."""


KEYS_CHARTS: Sequence[ChartSpec] = (
    ChartSpec(
        label='Lamination',
        method='laminations',
        chart_key='Laminations',
        description=(
            'Camadas de sentido que se acoplam à mensagem-base — links, '
            'emails, chamadas e emojis — agregadas por época ou ator.'
        ),
    ),
    ChartSpec(
        label='Links',
        method='links',
        chart_key='Links',
        description='URLs como única série de laminação, contra a frequência de mensagens.',
    ),
    ChartSpec(
        label='Calls',
        method='calls',
        chart_key='Calls',
        description='Menções (@nome) como série única de laminação.',
    ),
    ChartSpec(
        label='Emails',
        method='emails',
        chart_key='Emails',
        description='Endereços de e-mail como série única de laminação.',
    ),
    ChartSpec(
        label='Textual symbols',
        method='textual_symbols',
        chart_key='Textual Symbols',
        description='Marcas de pontuação e emojis combinados — fabricação textual.',
    ),
    ChartSpec(
        label='Messages',
        method='messages',
        chart_key='Messages',
        description=(
            'Wordcloud de tokens (verbos / substantivos / adjetivos) extraídos '
            'de todas as mensagens de texto via spaCy.'
        ),
        has_morph=True,
        is_wordcloud=True,
    ),
    ChartSpec(
        label='Keyword',
        method='keyword',
        chart_key='Keyword',
        description=(
            'Wordcloud restrita a mensagens que contêm uma palavra-chave informada. '
            'Útil para responder “quando falam de X, falam de quem/o quê/qualificando como?”.'
        ),
        has_keyword=True,
        has_morph=True,
        is_wordcloud=True,
    ),
    ChartSpec(
        label='Ratings',
        method='ratings',
        chart_key='Ratings',
        description=(
            'Tabela de vídeos do YouTube linkados no chat, com views/likes/comments '
            'puxados via API. Requer Google API key configurada no Setup.'
        ),
        needs_api=True,
    ),
)


# ──────────────────────────────────────────────────────────────────────
# Helpers — domain extracted from a Chat
# ──────────────────────────────────────────────────────────────────────


def enumerate_months(chat: Any) -> List[str]:
    """Sorted list of unique ``'%B %Y'`` keys present in ``chat.messages``.

    Order matches what :func:`qualichat.sorters._sort_by_time` will emit
    when the user picks 'Choose an epoch', so the multiselect labels
    line up with the chart's expectations.
    """
    months = sorted({m.created_at.strftime('%B %Y') for m in chat.messages})
    return months


def enumerate_actors(chat: Any) -> List[str]:
    """Anonymised display names of every actor in the chat."""
    return [a.display_name for a in chat.actors]


# ──────────────────────────────────────────────────────────────────────
# Answer-queue builder
# ──────────────────────────────────────────────────────────────────────


def build_answers(
    spec: ChartSpec,
    *,
    mode: str,                       # 'time' | 'actor'
    period_filter: str = 'all',      # 'all' | 'specific'
    months: Sequence[str] = (),
    actor_filter: str = 'all',       # 'all' | 'specific'
    actors: Sequence[str] = (),
    keyword: str = '',
    morph: str = 'Nouns',
) -> List[Any]:
    """Materialise the prompt-replay queue for a single-chat run.

    Order is the order in which :class:`qualichat.frames.KeysFrame`
    methods (and their decorators) call the questionary prompts:

    1. ``select('Choose your mode:', ['By Time', 'By Actor'])``
    2. (per chat) ``select('Which messages|actors should be selected?',
       ['All', 'Choose ...'])``
    3. (if specific) ``checkbox(months_or_actors)``
    4. (if has_keyword) ``input('Enter the keyword:')``
    5. (if has_morph) ``select('Choose a morphological class:',
       ['Verbs', 'Nouns', 'Adjectives'])``

    Multi-chat extends step 2-3 per chat. Out of scope for Sprint 2.
    """
    answers: List[Any] = []

    # 1. mode
    answers.append('By Time' if mode == 'time' else 'By Actor')

    # 2. + 3. per-chat sort cascade
    if mode == 'time':
        if period_filter == 'specific' and months:
            answers.append('Choose an epoch')
            answers.append(list(months))
        else:
            answers.append('All')
    else:
        if actor_filter == 'specific' and actors:
            answers.append('Choose a specific actor')
            answers.append(list(actors))
        else:
            answers.append('All')

    # 4. keyword text input
    if spec.has_keyword:
        answers.append(keyword)

    # 5. morphological class
    if spec.has_morph:
        answers.append(morph)

    return answers
