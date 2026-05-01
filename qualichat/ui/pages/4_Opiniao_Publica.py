"""Frame: Opinião Pública — wrapper Streamlit dos 2 charts em
:class:`qualichat.frames.PublicOpinionFrame`.

Os charts são *exatamente* os que já estão implementados no código
CLI; este módulo só monta a UI mínima e dispara via
:func:`qualichat.ui.runtime.run_chart`. Ambos os charts pedem zero
prompts ao usuário; a única coisa que a UI precisa fazer é avisar
sobre dependências externas (Google Translate + en_core_web_sm).
"""

from __future__ import annotations

import importlib

import streamlit as st

from qualichat.ui.components.chrome import bootstrap
from qualichat.ui.components.empty_state import empty_state
from qualichat.ui.components.chart_runner import (
    OPINION_CHARTS,
    ChartSpec,
    build_answers_opinion,
)
from qualichat.ui.runtime import PromptQueueExhausted, run_chart
from qualichat.ui.state import get_chat, get_qc, has_chat


def _spec_from_label(label: str) -> ChartSpec:
    return next(s for s in OPINION_CHARTS if s.label == label)


def _has_en_spacy() -> bool:
    """True if ``en_core_web_sm`` is importable in this environment."""
    try:
        importlib.import_module('en_core_web_sm')
        return True
    except Exception:
        return False


def _render_external_warnings(spec: ChartSpec) -> bool:
    """Emit any inline warnings about external dependencies. Returns
    ``True`` if it's safe to run the chart, ``False`` if a hard
    blocker (e.g. missing model) is detected.
    """
    can_run = True

    if spec.needs_en_spacy and not _has_en_spacy():
        st.markdown(
            '<div class="qc-notice">'
            '<div class="qc-notice-title">⚠ Modelo en_core_web_sm não instalado</div>'
            '<p>Este chart carrega <em>spacy.load("en_core_web_sm")</em> '
            'para análise NLP em inglês. Instale com '
            '<em>python -m spacy download en_core_web_sm</em> ou veja '
            'a aba Setup.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        can_run = False

    if spec.needs_translator:
        st.markdown(
            '<div class="qc-notice">'
            '<div class="qc-notice-title">⚠ Serviço externo · Google Translate</div>'
            '<p>Este chart envia trechos das mensagens ao Google Translate '
            'para tradução ao inglês (limitação do TextBlob). Cada execução '
            'gera tráfego de rede e pode incorrer em custo dependendo do '
            'volume. Apenas as primeiras 5 mensagens de atores acima da '
            'média de mensagens são analisadas.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    return can_run


def main() -> None:
    bootstrap(
        page_title='Opinião Pública',
        breadcrumb='Opinião Pública',
        active_slug='opiniao',
    )

    if not has_chat():
        empty_state()
        return

    chat = get_chat()
    qc = get_qc()

    st.markdown('# Opinião Pública')
    st.markdown(
        '<div class="qc-lede">'
        'Dois recortes do <em>PublicOpinionFrame</em> — polaridade '
        'sentimental por ator e linkage temático contra um vocabulário '
        'de grupos pré-definidos em <em>connector.csv</em>.'
        '</div>',
        unsafe_allow_html=True,
    )

    labels = [s.label for s in OPINION_CHARTS]
    chart_label = st.radio(
        'Sub-chart',
        labels,
        horizontal=True,
        label_visibility='collapsed',
    )
    spec = _spec_from_label(chart_label)

    st.markdown(f'## {spec.label}')
    st.markdown(
        f'<div class="qc-prose"><p>{spec.description}</p></div>',
        unsafe_allow_html=True,
    )

    can_run = _render_external_warnings(spec)

    if st.button(
        'Gerar chart',
        type='primary',
        disabled=not can_run,
        key=f'run_{spec.method}',
    ):
        answers = build_answers_opinion(spec)
        try:
            chart_callable = qc.frames['Public Opinion'].charts[spec.chart_key]
        except KeyError:
            st.error(
                f'Chart "{spec.chart_key}" não encontrado em '
                f'qc.frames["Public Opinion"].charts. '
                f'Disponíveis: {list(qc.frames["Public Opinion"].charts.keys())}'
            )
            return

        spinner_msg = 'Traduzindo + analisando polaridade…' if spec.needs_translator else 'Calculando…'
        with st.spinner(spinner_msg):
            try:
                figures = run_chart(chart_callable, [chat], answers)
            except PromptQueueExhausted as exc:
                st.error(
                    f'Fila de respostas exaurida: {exc}'
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


main()
