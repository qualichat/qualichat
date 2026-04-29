"""Frame: Keys — 8 charts (Lamination, Links, Calls, Emails, Textual symbols,
Messages, Keyword, Ratings) driven from Streamlit widgets via
:func:`qualichat.ui.runtime.run_chart`.
"""

from __future__ import annotations

import streamlit as st

from qualichat.ui.components.chrome import bootstrap
from qualichat.ui.components.empty_state import empty_state
from qualichat.ui.components.chart_runner import (
    KEYS_CHARTS,
    ChartSpec,
    build_answers,
    enumerate_actors,
    enumerate_months,
)
from qualichat.ui.runtime import PromptQueueExhausted, run_chart
from qualichat.ui.state import get_chat, get_qc, has_chat


def _spec_from_label(label: str) -> ChartSpec:
    return next(s for s in KEYS_CHARTS if s.label == label)


def _api_key_present() -> bool:
    from qualichat.utils import config
    return bool(config['google_api_key']) if 'google_api_key' in config else False


def _render_filters(chat) -> dict:
    """Sorter + period/actor selector. Returns the values for build_answers()."""
    st.markdown('### Filtros')
    with st.container(border=False):
        col1, col2 = st.columns(2)
        with col1:
            mode_label = st.radio(
                'Sorter',
                ['Por época', 'Por ator'],
                horizontal=True,
                help='@sorters.keys decorator: select("Choose your mode")',
            )
        mode = 'time' if mode_label == 'Por época' else 'actor'

        period_filter = 'all'
        actor_filter = 'all'
        months = []
        actors = []

        if mode == 'time':
            with col2:
                period_filter_label = st.radio(
                    'Período',
                    ['todos os meses', 'escolher meses'],
                    horizontal=True,
                )
            period_filter = 'specific' if period_filter_label == 'escolher meses' else 'all'
            if period_filter == 'specific':
                month_options = enumerate_months(chat)
                months = st.multiselect(
                    f'Selecione meses ({len(month_options)} disponíveis)',
                    options=month_options,
                    help='Internal: chat-miner gera estes labels via strftime("%B %Y").',
                )
        else:
            with col2:
                actor_filter_label = st.radio(
                    'Atores',
                    ['todos', 'escolher atores'],
                    horizontal=True,
                )
            actor_filter = 'specific' if actor_filter_label == 'escolher atores' else 'all'
            if actor_filter == 'specific':
                actor_options = enumerate_actors(chat)
                actors = st.multiselect(
                    f'Selecione atores ({len(actor_options)} disponíveis)',
                    options=actor_options,
                )
    return {
        'mode': mode,
        'period_filter': period_filter,
        'months': months,
        'actor_filter': actor_filter,
        'actors': actors,
    }


def _render_chart_specific(spec: ChartSpec) -> dict:
    """Extra inputs for charts that ask additional questions."""
    keyword = ''
    morph = 'Nouns'

    if spec.has_keyword:
        keyword = st.text_input(
            'Palavra-chave a buscar',
            placeholder='ex: eleição',
            help='Match case-insensitive em message.content.',
        )
    if spec.has_morph:
        morph_label = st.radio(
            'Classe morfológica (spaCy POS)',
            ['Verbos', 'Substantivos', 'Adjetivos'],
            horizontal=True,
            index=1,
        )
        morph_map = {'Verbos': 'Verbs', 'Substantivos': 'Nouns', 'Adjetivos': 'Adjectives'}
        morph = morph_map[morph_label]

    return {'keyword': keyword, 'morph': morph}


def _formula_for(spec: ChartSpec) -> str:
    """Per-chart formula ribbon (HTML). Empty when no fórmula applies."""
    parts = {
        'Laminations': '<span class="var">Lamination</span><span class="op">=</span>'
                       '<span class="var">links</span><span class="op">+</span>'
                       '<span class="var">emails</span><span class="op">+</span>'
                       '<span class="var">chamadas</span><span class="op">+</span>'
                       '<span class="var">emojis</span>',
        'Links':       '<span class="var">QTD_Link</span> <em>por época ou ator</em>',
        'Calls':       '<span class="var">QTD_Chamada</span> <em>por época ou ator</em>',
        'Emails':      '<span class="var">QTD_Email</span> <em>por época ou ator</em>',
        'Textual Symbols': '<span class="var">marks</span><span class="op">+</span>'
                           '<span class="var">emojis</span>',
    }
    body = parts.get(spec.chart_key)
    if not body:
        return ''
    return (
        '<div class="qc-formula">'
        f'{body}'
        '<span class="qc-formula-foot">cf. Goffman (1974) · op. cit. Cavalcante &amp; Hanke (2020)</span>'
        '</div>'
    )


def main() -> None:
    bootstrap(
        page_title='Frame: Keys',
        breadcrumb='Frame: Keys',
        active_slug='keys',
    )

    if not has_chat():
        empty_state()
        return

    chat = get_chat()
    qc = get_qc()

    st.markdown('# Frame: Keys')
    st.markdown(
        '<div class="qc-lede">'
        'As oito chaves discursivas — laminação (links · emails · chamadas '
        '· emojis), fabricação textual e o léxico-base — examinadas pela '
        'lente de Goffman (1974) e Cavalcante &amp; Hanke (2020).'
        '</div>',
        unsafe_allow_html=True,
    )

    # Chart picker
    labels = [s.label for s in KEYS_CHARTS]
    chart_label = st.radio(
        'Sub-chart',
        labels,
        horizontal=True,
        label_visibility='collapsed',
    )
    spec = _spec_from_label(chart_label)

    # Description + per-chart formula ribbon
    st.markdown(f'## {spec.label}')
    st.markdown(
        f'<div class="qc-prose"><p>{spec.description}</p></div>',
        unsafe_allow_html=True,
    )
    formula_html = _formula_for(spec)
    if formula_html:
        st.markdown(formula_html, unsafe_allow_html=True)

    # External-service warning
    if spec.needs_api and not _api_key_present():
        st.markdown(
            '<div class="qc-notice">'
            '<div class="qc-notice-title">⚠ Google API key necessária</div>'
            '<p>Este chart consulta a YouTube Data API. Configure a chave '
            'em <em>Setup → 02 Google API key</em> antes de gerar.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    # Filters + chart-specific inputs
    filters = _render_filters(chat)
    extras = _render_chart_specific(spec)

    # Validation
    can_run = True
    if spec.needs_api and not _api_key_present():
        can_run = False
    if spec.has_keyword and not extras['keyword'].strip():
        st.info('Informe uma palavra-chave para gerar a wordcloud.')
        can_run = False
    if filters['period_filter'] == 'specific' and not filters['months']:
        st.info('Selecione ao menos um mês ou volte para "todos os meses".')
        can_run = False
    if filters['actor_filter'] == 'specific' and not filters['actors']:
        st.info('Selecione ao menos um ator ou volte para "todos".')
        can_run = False

    # Run button
    if st.button('Gerar chart', type='primary', disabled=not can_run):
        answers = build_answers(spec, **filters, **extras)
        try:
            chart_callable = qc.frames['Keys'].charts[spec.chart_key]
        except KeyError:
            st.error(
                f'Chart "{spec.chart_key}" não encontrado em qc.frames["Keys"].charts. '
                f'Disponíveis: {list(qc.frames["Keys"].charts.keys())}'
            )
            return

        with st.spinner('Calculando…'):
            try:
                figures = run_chart(chart_callable, [chat], answers)
            except PromptQueueExhausted as exc:
                st.error(
                    f'Fila de respostas exaurida — o chart pediu mais decisões '
                    f'do que esperávamos: {exc}'
                )
                return
            except Exception as exc:  # noqa: BLE001
                st.error(f'Erro ao gerar chart: {type(exc).__name__}: {exc}')
                return

        if not figures:
            st.warning('O chart rodou mas não produziu nenhuma figura.')
            return

        for i, fig in enumerate(figures):
            st.plotly_chart(
                fig,
                use_container_width=True,
                key=f'{spec.chart_key}_fig_{i}',
                config={'displaylogo': False},
            )

        st.markdown(
            '<div class="qc-prose" style="margin-top: 32px;">'
            f'<p style="color: var(--sepia-fieldnote); font-style: italic;">'
            f'Chart gerado: {spec.chart_key}. Plotly figura interativa — '
            f'use os controles do gráfico para PNG/HTML, ou Sprint 5 vai '
            f'centralizar exports na aba <em>Exportar</em>.'
            '</p></div>',
            unsafe_allow_html=True,
        )

    # ─── Divergence note for Lamination (D1) ────────────────────────
    if spec.chart_key == 'Laminations':
        st.markdown(
            '<div class="qc-notice">'
            '<div class="qc-notice-title">⚠ Nota de divergência D1</div>'
            '<p>No fluxograma original (Cavalcante 2021, Medium), este chart '
            'plotaria <em>Qtd_liq_car</em> como residue (texto puro '
            'remanescente). A implementação atual plota os componentes '
            'laminadores. A divergência foi mantida por retrocompatibilidade '
            'com pesquisas anteriores. Ver <em>docs/divergences.rst</em>.</p>'
            '</div>',
            unsafe_allow_html=True,
        )


main()
