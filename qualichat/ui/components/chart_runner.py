"""
qualichat.ui.components.chart_runner
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bridge between Streamlit widgets and the prompt-driven CLI charts of
:mod:`qualichat.frames`. Collects answers from the UI, builds the queue
in the exact order the chart will pop them, then drives the chart via
:func:`qualichat.ui.runtime.run_chart`.

Each chart variant is described by a :class:`ChartSpec`. The spec
declares which extra prompts the chart asks (keyword text, morphological
class, sub-action choices) and whether external services are required
(Google API key for Ratings; Google Translate + ``en_core_web_sm``
for Matrix Polarity).

Sprint 2 covered the eight :class:`KeysFrame` charts. Sprint 3 adds the
seven :class:`ParticipationStatusFrame` charts and the two
:class:`PublicOpinionFrame` charts, all driven through the same
prompt-replay machinery via :data:`PARTICIPATION_CHARTS` and
:data:`OPINION_CHARTS`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Sequence, Tuple


__all__ = (
    'ChartSpec',
    'KEYS_CHARTS',
    'PARTICIPATION_CHARTS',
    'OPINION_CHARTS',
    'build_answers',
    'build_answers_participation',
    'build_answers_opinion',
    'enumerate_months',
    'enumerate_actors',
    'enumerate_media_domains',
)


@dataclass(frozen=True)
class ChartSpec:
    """Static description of a chart variant across all frames.

    Most fields default to ``False``/empty so KeysFrame specs don't need
    the participation-specific knobs and vice-versa. Charts in
    :data:`KEYS_CHARTS` use ``has_keyword`` / ``has_morph`` /
    ``needs_api``; charts in :data:`PARTICIPATION_CHARTS` use
    ``has_pp_mode`` / ``action_choices`` / ``msg_type_choices`` /
    ``has_media_whitelist``; :data:`OPINION_CHARTS` mostly relies on
    ``needs_translator`` / ``needs_en_spacy``.
    """

    label: str
    """Human-readable label shown in the picker (e.g. 'Lamination')."""

    method: str
    """Method name on the frame (e.g. 'laminations')."""

    chart_key: str
    """Title-cased key used by ``frame.charts[...]`` (e.g. 'Laminations')."""

    description: str
    """One-paragraph description shown above the chart controls."""

    # ── KeysFrame-specific prompts ─────────────────────────────────────
    has_keyword: bool = False
    """Whether the chart asks ``input('Enter the keyword:')``."""

    has_morph: bool = False
    """Whether the chart asks ``select('Choose a morphological class:')``."""

    needs_api: bool = False
    """Whether the chart requires ``config['google_api_key']`` (YouTube)."""

    is_wordcloud: bool = False
    """Renders a wordcloud (different layout). Informational."""

    # ── ParticipationStatusFrame-specific prompts ──────────────────────
    has_pp_mode: bool = False
    """Whether ``@sorters.participation_status`` wraps this chart and
    asks ``select('Choose your mode:', ['By Time', 'Treemap'])`` first.
    """

    action_choices: Tuple[str, ...] = ()
    """Body-level ``select(..., choices)`` after the optional pp_mode.
    Examples: ``('Index', 'Components')`` for ``bots``,
    ``('Choose Media', 'Average Media', 'Treemap')`` for
    ``media_repertoire``.
    """

    msg_type_choices: Tuple[str, ...] = ()
    """Body-level ``select(..., choices)`` for charts that ask which
    message stream to plot. Currently only
    ``messages_per_actors_per_weekday`` uses
    ``('User Messages', 'System Messages')``.
    """

    has_media_whitelist: bool = False
    """Whether picking a particular ``action_choices`` value
    (``'Choose Media'`` for ``media_repertoire``) triggers a follow-up
    ``checkbox`` of media domains. The follow-up answer is only
    appended to the queue when that branch is chosen.
    """

    # ── PublicOpinionFrame-specific external dependencies ──────────────
    needs_translator: bool = False
    """Chart calls ``GoogleTranslator(target='en').translate(...)`` —
    requires network and may incur cost.
    """

    needs_en_spacy: bool = False
    """Chart loads ``spacy.load('en_core_web_sm')`` (with
    ``spacytextblob`` pipeline). The model has to be installed in the
    environment before the chart can run.
    """


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
# Sprint 3 — ParticipationStatusFrame (7 charts)
# ──────────────────────────────────────────────────────────────────────


PARTICIPATION_CHARTS: Sequence[ChartSpec] = (
    ChartSpec(
        label='Mensagens por ator',
        method='messages_per_actors',
        chart_key='Messages Per Actors',
        description=(
            'Quantos caracteres totais, líquidos e puros cada ator emitiu — '
            'comparativo do peso textual de cada participante.'
        ),
        has_pp_mode=True,
    ),
    ChartSpec(
        label='Mensagens por dia da semana',
        method='messages_per_actors_per_weekday',
        chart_key='Messages Per Actors Per Weekday',
        description=(
            'Distribuição da contagem de mensagens ao longo dos sete dias da '
            'semana. Permite escolher entre mensagens dos atores ou eventos '
            'do sistema (entradas, saídas, mudanças de título).'
        ),
        msg_type_choices=('User Messages', 'System Messages'),
    ),
    ChartSpec(
        label='Bots',
        method='bots',
        chart_key='Bots',
        description=(
            'Heurística de detecção de comportamento automatizado: pondera '
            'volume de texto, vídeos e stickers. Modo Index agrega num único '
            'score; Components mostra cada componente separado.'
        ),
        action_choices=('Index', 'Components'),
    ),
    ChartSpec(
        label='Repertório de mídia',
        method='media_repertoire',
        chart_key='Media Repertoire',
        description=(
            'Visualiza o ecossistema de domínios linkados no chat. '
            '"Choose Media" filtra por whitelist de domínios; '
            '"Average Media" plota média de URLs por ator; '
            '"Treemap" mostra todos os domínios proporcionalmente.'
        ),
        action_choices=('Choose Media', 'Average Media', 'Treemap'),
        has_media_whitelist=True,
    ),
    ChartSpec(
        label='Estatísticas',
        method='message_statistics',
        chart_key='Message Statistics',
        description=(
            'Médias e desvios-padrão de comprimento textual por ator — '
            'quão regular é o estilo de cada um (fala em explosões curtas '
            'ou em parágrafos longos?).'
        ),
        has_pp_mode=True,
    ),
    ChartSpec(
        label='Lam. por atores',
        method='laminations_per_actors',
        chart_key='Laminations Per Actors',
        description=(
            'Composição da laminação (chamadas + links + emails + emojis) '
            'por ator. Modo "Average" mostra médias e desvios; '
            '"Laminations per Actors" mostra totais com texto líquido como linha.'
        ),
        has_pp_mode=True,
        action_choices=('Laminations per Actors', 'Average Laminations'),
    ),
    ChartSpec(
        label='Fab. por atores',
        method='fabrications_per_actors',
        chart_key='Fabrications Per Actors',
        description=(
            'Composição da fabricação textual (risos + marcas + números) '
            'por ator. "Average" mostra médias e desvios; '
            '"Fabrications per Actors" mostra totais.'
        ),
        has_pp_mode=True,
        action_choices=('Fabrications per Actors', 'Average Fabrications'),
    ),
)


# ──────────────────────────────────────────────────────────────────────
# Sprint 3 — PublicOpinionFrame (2 charts)
# ──────────────────────────────────────────────────────────────────────


OPINION_CHARTS: Sequence[ChartSpec] = (
    ChartSpec(
        label='Matriz de polaridade',
        method='matrix_polarity',
        chart_key='Matrix Polarity',
        description=(
            'Scatter plot de polaridade (positivo ↔ negativo) por ator. '
            'Atores acima da média de mensagens são analisados; cada bolha '
            'é a polaridade de uma mensagem traduzida ao inglês via Google '
            'Translate e processada por TextBlob/spaCy en_core_web_sm.'
        ),
        needs_translator=True,
        needs_en_spacy=True,
    ),
    ChartSpec(
        label='Linkage temático',
        method='linkage',
        chart_key='Linkage',
        description=(
            'Score temático por grupo (Friends, Political, Religious, '
            'Family, Green, Innovation, etc.) baseado em ocorrências de '
            'palavras-chave do <em>connector.csv</em>. Palavras especiais '
            'amplificam o score em 3×.'
        ),
        needs_en_spacy=True,
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


def enumerate_media_domains(chat: Any) -> List[str]:
    """Sorted unique URL domains across every message in the chat.

    Mirrors what ``ParticipationStatusFrame.media_repertoire`` would
    offer if its CLI prompt asked the user to whitelist domains. The
    list is sorted alphabetically for stable picker UX.
    """
    from qualichat.utils import parse_domain

    domains: set = set()
    for m in chat.messages:
        try:
            for url in m['Qty_char_links']:
                domains.add(parse_domain(url))
        except (KeyError, TypeError):
            continue
    return sorted(domains)


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


def build_answers_participation(
    spec: ChartSpec,
    *,
    pp_mode: str = 'By Time',
    action: str = '',
    msg_type: str = '',
    media_whitelist: Sequence[str] = (),
) -> List[Any]:
    """Materialise the prompt-replay queue for a ParticipationStatusFrame chart.

    Order matches the order in which prompts fire at runtime:

    1. (optional) ``@sorters.participation_status`` asks
       ``select('Choose your mode:', ['By Time', 'Treemap'])`` —
       gated by ``spec.has_pp_mode``.
    2. (optional) Body asks ``select('Choose you action', spec.action_choices)``
       (charts: ``bots``, ``media_repertoire``, ``laminations_per_actors``,
       ``fabrications_per_actors``).
    3. (optional) Body asks ``select('Choose the message type:', ...)`` —
       only ``messages_per_actors_per_weekday``.
    4. (optional) ``_choose_media`` (called from ``media_repertoire`` only
       when action == 'Choose Media') asks
       ``checkbox('Choose a Media', list(all_media))`` — gated by
       ``spec.has_media_whitelist`` AND the chosen action.
    """
    answers: List[Any] = []

    if spec.has_pp_mode:
        answers.append(pp_mode)

    if spec.action_choices:
        answers.append(action)

    if spec.msg_type_choices:
        answers.append(msg_type)

    # The media checkbox is only consumed when media_repertoire branches
    # into _choose_media. Don't emit otherwise — the chart won't pop it.
    if spec.has_media_whitelist and action == 'Choose Media':
        answers.append(list(media_whitelist))

    return answers


def build_answers_opinion(spec: ChartSpec) -> List[Any]:
    """Empty answer queue for PublicOpinionFrame charts.

    Both ``matrix_polarity`` and ``linkage`` ask zero prompts. This
    function exists for symmetry with the other ``build_answers_*``
    helpers and to keep the page code uniform.
    """
    return []
