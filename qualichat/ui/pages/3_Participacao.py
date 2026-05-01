"""Frame: Participação — wrapper Streamlit dos 7 charts existentes em
:class:`qualichat.frames.ParticipationStatusFrame`.

Os charts são *exatamente* os que já estão implementados no código
CLI; este módulo só monta os widgets de filtro, materializa a fila
de respostas via :func:`build_answers_participation` e dispara via
:func:`qualichat.ui.runtime.run_chart`.
"""

from __future__ import annotations

import streamlit as st

from qualichat.ui.components.chrome import bootstrap
from qualichat.ui.components.empty_state import empty_state
from qualichat.ui.components.chart_runner import (
    PARTICIPATION_CHARTS,
    ChartSpec,
    build_answers_participation,
    enumerate_media_domains,
)
from qualichat.ui.runtime import PromptQueueExhausted, run_chart
from qualichat.ui.state import get_chat, get_qc, has_chat


def _spec_from_label(label: str) -> ChartSpec:
    return next(s for s in PARTICIPATION_CHARTS if s.label == label)


def _render_chart_filters(spec: ChartSpec, chat) -> dict:
    """Render the widgets specific to the chart's prompt cascade.

    Returns a kwargs dict ready to pass to
    :func:`build_answers_participation`. Keys include ``pp_mode``,
    ``action``, ``msg_type``, ``media_whitelist``, all defaulted so
    the function is safe to call even if no widget renders anything.
    """
    out: dict = {
        'pp_mode': 'By Time',
        'action': '',
        'msg_type': '',
        'media_whitelist': [],
    }

    cols = []
    needed = sum([
        spec.has_pp_mode,
        bool(spec.action_choices),
        bool(spec.msg_type_choices),
    ])
    if needed:
        cols = st.columns(max(needed, 2))

    col_iter = iter(cols) if cols else None

    if spec.has_pp_mode:
        with (next(col_iter) if col_iter else st.container()):
            out['pp_mode'] = st.radio(
                'Modo de visualização',
                ['By Time', 'Treemap'],
                horizontal=True,
                help='@sorters.participation_status: select("Choose your mode")',
                key=f'pp_mode_{spec.method}',
            )

    if spec.action_choices:
        with (next(col_iter) if col_iter else st.container()):
            out['action'] = st.radio(
                'Ação',
                list(spec.action_choices),
                horizontal=True,
                help=f'frames.{spec.method}(): select("Choose you action")',
                key=f'action_{spec.method}',
            )

    if spec.msg_type_choices:
        with (next(col_iter) if col_iter else st.container()):
            out['msg_type'] = st.radio(
                'Tipo de mensagem',
                list(spec.msg_type_choices),
                horizontal=True,
                help=(
                    'User = mensagens dos atores; '
                    'System = entradas, saídas, mudanças de título.'
                ),
                key=f'msg_type_{spec.method}',
            )

    # Media whitelist: only relevant when action == 'Choose Media'.
    if spec.has_media_whitelist and out['action'] == 'Choose Media':
        domains = enumerate_media_domains(chat)
        if not domains:
            st.info(
                'Nenhum domínio de URL foi encontrado neste chat. '
                'Selecione "Average Media" ou "Treemap" em vez disso.'
            )
        else:
            out['media_whitelist'] = st.multiselect(
                f'Domínios a incluir ({len(domains)} disponíveis)',
                options=domains,
                default=domains[:5] if len(domains) > 5 else domains,
                help='checkbox("Choose a Media", all_media) na função _choose_media.',
                key=f'media_whitelist_{spec.method}',
            )

    return out


def _validate(spec: ChartSpec, filters: dict, chat) -> tuple[bool, str]:
    """Return (can_run, reason). Empty reason when can_run is True."""
    if spec.has_media_whitelist and filters['action'] == 'Choose Media':
        domains = enumerate_media_domains(chat)
        if not domains:
            return False, 'Chat sem URLs — escolha outra ação.'
        if not filters['media_whitelist']:
            return False, 'Selecione ao menos um domínio para "Choose Media".'
    return True, ''


def main() -> None:
    bootstrap(
        page_title='Participação',
        breadcrumb='Participação',
        active_slug='participacao',
    )

    if not has_chat():
        empty_state()
        return

    chat = get_chat()
    qc = get_qc()

    st.markdown('# Participação')
    st.markdown(
        '<div class="qc-lede">'
        'Sete recortes do <em>ParticipationStatusFrame</em> — quantos atores, '
        'quanto cada um fala, em que dia da semana, em que repertório de '
        'mídia, com que regularidade. Os mesmos charts da CLI, agora '
        'disparados por widgets.'
        '</div>',
        unsafe_allow_html=True,
    )

    labels = [s.label for s in PARTICIPATION_CHARTS]
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

    filters = _render_chart_filters(spec, chat)

    can_run, reason = _validate(spec, filters, chat)
    if reason:
        st.info(reason)

    if st.button('Gerar chart', type='primary', disabled=not can_run, key=f'run_{spec.method}'):
        answers = build_answers_participation(spec, **filters)
        try:
            chart_callable = qc.frames['Participation Status'].charts[spec.chart_key]
        except KeyError:
            st.error(
                f'Chart "{spec.chart_key}" não encontrado em '
                f'qc.frames["Participation Status"].charts. '
                f'Disponíveis: {list(qc.frames["Participation Status"].charts.keys())}'
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
            f'Chart gerado: <em>{spec.chart_key}</em>. '
            'Plotly figura interativa — use os controles do gráfico para '
            'PNG/HTML, ou Sprint 5 vai centralizar exports na aba Exportar.'
            '</p></div>',
            unsafe_allow_html=True,
        )


main()
