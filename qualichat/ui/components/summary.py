"""
qualichat.ui.components.summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Summary widgets for the Resumo page: definition list, message-type
stack-bar, weekday × period heatmap. All derived from a parsed
:class:`qualichat.chat.Chat` instance.
"""

from __future__ import annotations

from collections import Counter
from html import escape
from typing import Any, Dict, List, Tuple

import streamlit as st


__all__ = ('summary_block',)


_PERIOD_LABEL_PT = {
    'dawn': 'Madrugada',
    'morning': 'Manhã',
    'evening': 'Tarde',
    'night': 'Noite',
}

_SUBPERIOD_LABEL_PT = {
    'resting': 'Descanso',
    'transport_morning': 'Acordar/Transporte',
    'work_morning': 'Trabalho (Manhã)',
    'lunch': 'Almoço',
    'work_evening': 'Trabalho (Tarde)',
    'transport_evening': 'Transporte',
    'second_office_hour': 'Segundo Expediente',
}

_WEEKDAYS = (
    ('Monday',    'Segunda'),
    ('Tuesday',   'Terça'),
    ('Wednesday', 'Quarta'),
    ('Thursday',  'Quinta'),
    ('Friday',    'Sexta'),
    ('Saturday',  'Sábado'),
    ('Sunday',    'Domingo'),
)

_MONTHS_PT = (
    'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
    'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro',
)


def _month_year_pt(dt: Any) -> str:
    return f'{_MONTHS_PT[dt.month - 1]} de {dt.year}'


def _fmt_int(n: int) -> str:
    """Format an integer with Brazilian thousands separator (period)."""
    return f'{n:,}'.replace(',', '.')

_PERIODS_ORDERED = ('dawn', 'morning', 'evening', 'night')


def _stat_dl(items: List[Tuple[str, str, str]]) -> str:
    """Build a HTML definition list. ``items`` is ``[(dt, dd, em), ...]``."""
    parts = ['<dl class="qc-def">']
    for dt, dd, em in items:
        em_html = f' <em>{escape(em)}</em>' if em else ''
        parts.append(f'<dt>{escape(dt)}</dt><dd>{escape(dd)}{em_html}</dd>')
    parts.append('</dl>')
    return ''.join(parts)


def _format_format_string(filename: str) -> str:
    """Best-effort label for the parsed format. We do not introspect
    chat-miner's inferred format here — keep this generic."""
    suffix = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
    if suffix == 'zip':
        return '.zip · auto-detectado'
    if suffix == 'txt':
        return '.txt · auto-detectado'
    return 'auto-detectado'


def _stack_bar(types: Counter, total: int) -> str:
    """Build the segmented horizontal bar for message types."""
    palette = (
        'var(--ocre-encadernacao)',
        'var(--musgo-biblioteca)',
        'var(--toga-academica)',
        'var(--sepia-fieldnote)',
        'var(--marginalia-vermelha)',
        'var(--ocre-encadernacao)',  # repeat with opacity for tail
    )
    label_short = {
        'default': 'texto',
        'image_omitted': 'imagem',
        'video_omitted': 'vídeo',
        'audio_omitted': 'áudio',
        'document_omitted': 'documento',
        'sticker_omitted': 'sticker',
        'gif_omitted': 'gif',
        'contact_card_omitted': 'contato',
        'deleted_message': 'apagada',
    }

    sorted_types = sorted(types.items(), key=lambda x: -x[1])
    segs = []
    legend = []
    for i, (key, count) in enumerate(sorted_types):
        if count == 0:
            continue
        color = palette[i % len(palette)]
        opacity = 1.0 if i < len(palette) else 0.5
        share = count / total * 100
        label = label_short.get(key, key)
        flex = max(count, total * 0.005)  # tiny minimum so segment is visible
        segs.append(
            f'<div class="seg" style="flex: {flex:.0f}; background: {color}; opacity: {opacity};">'
            f'{escape(label)} · {count:,}</div>'
        )
        legend.append(
            f'<span><span class="swatch" style="background: {color}; opacity: {opacity};"></span>'
            f'{escape(label)} · {count:,} ({share:.1f}%)</span>'
        )

    bar = f'<div class="qc-stack">{"".join(segs)}</div>'
    leg = f'<div class="qc-stack-legend">{"".join(legend)}</div>'
    return bar + leg


def _heatmap(messages: List[Any]) -> Any:
    """Build a Plotly heatmap of weekday × period (QTD_Liquidos médio).

    Returns the figure for ``st.plotly_chart``.
    """
    import plotly.graph_objects as go

    # Aggregate net chars by (weekday_en, period_name)
    bucket: Dict[Tuple[str, str], List[int]] = {}
    for m in messages:
        wd = m.created_at.strftime('%A')
        pd = m['Day_period'].name
        bucket.setdefault((wd, pd), []).append(len(m['Qty_char_net']))

    # Build matrix in our preferred order
    z = []
    text = []
    for wd_en, _wd_pt in _WEEKDAYS:
        row = []
        text_row = []
        for p in _PERIODS_ORDERED:
            vals = bucket.get((wd_en, p), [])
            avg = sum(vals) / len(vals) if vals else 0
            row.append(avg)
            text_row.append(f'{avg:.0f}' if avg else '0')
        z.append(row)
        text.append(text_row)

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=[_PERIOD_LABEL_PT[p] for p in _PERIODS_ORDERED],
        y=[wd_pt for _, wd_pt in _WEEKDAYS],
        text=text,
        texttemplate='%{text}',
        colorscale=[
            [0.0, '#FAF7F1'],
            [0.2, 'rgba(184, 134, 11, 0.20)'],
            [0.5, 'rgba(184, 134, 11, 0.55)'],
            [1.0, 'rgba(184, 134, 11, 0.90)'],
        ],
        showscale=False,
        xgap=1, ygap=1,
        hovertemplate='%{y} · %{x}<br>QTD_Liquidos médio: %{z:.1f}<extra></extra>',
    ))
    fig.update_layout(
        height=320,
        margin=dict(l=20, r=20, t=10, b=10),
        plot_bgcolor='#F4EFE6',
        paper_bgcolor='#F4EFE6',
        font=dict(family='Source Sans 3', size=12, color='#7A6B5A'),
    )
    fig.update_xaxes(side='top', tickfont=dict(size=11, color='#7A6B5A'))
    fig.update_yaxes(tickfont=dict(size=11, color='#7A6B5A'))
    return fig


def summary_block(chat: Any) -> None:
    """Render the full Resumo page content for a parsed Chat."""
    msgs = chat.messages
    actors = chat.actors
    sysm = chat.system_messages

    if not msgs:
        st.warning('Chat carregado mas nenhuma mensagem foi encontrada.')
        return

    mn = min(m.created_at for m in msgs)
    mx = max(m.created_at for m in msgs)
    days = max((mx - mn).days, 1)

    mtypes = Counter(m['Type'].name for m in msgs)
    subperiods = Counter(m['Day_sub_period'].name for m in msgs)

    media = sum(c for k, c in mtypes.items() if k != 'default')
    text = mtypes.get('default', 0)

    peak_sp_key, peak_sp_count = subperiods.most_common(1)[0]
    peak_sp_label = _SUBPERIOD_LABEL_PT.get(peak_sp_key, peak_sp_key)
    peak_sp_share = peak_sp_count / len(msgs) * 100

    lede = (
        f'Foram lidas <em>{_fmt_int(len(msgs))}</em> mensagens de '
        f'<em>{len(actors)}</em> atores entre '
        f'<em>{_month_year_pt(mn)}</em> e '
        f'<em>{_month_year_pt(mx)}</em>, anonimizadas por padrão. '
        f'<em>{_fmt_int(len(sysm))}</em> eventos de sistema (entrada, saída, criação) '
        'foram preservados.'
    )
    st.markdown(f'<div class="qc-lede">{lede}</div>', unsafe_allow_html=True)

    st.markdown('### Estrutura do export')
    st.markdown(_stat_dl([
        ('Formato detectado',     _format_format_string(chat.filename), 'detecção automática via chat-miner'),
        ('Período',               f'{mn.date().isoformat()} → {mx.date().isoformat()}', f'{days} dias'),
        ('Mensagens',             _fmt_int(len(msgs)), f'{_fmt_int(media)} mídia · {_fmt_int(text)} texto'),
        ('System events',         _fmt_int(len(sysm)), 'entradas, saídas, mudanças de título'),
        ('Atores',                f'{len(actors)}', 'anonimizados'),
        ('Densidade',             f'{len(msgs) / days:.1f} msgs/dia', 'média móvel'),
        ('Sub-período de pico',   peak_sp_label, f'{peak_sp_share:.1f}% do tráfego'),
    ]), unsafe_allow_html=True)

    st.markdown('### Distribuição por tipo de mensagem')
    st.markdown(_stack_bar(mtypes, len(msgs)), unsafe_allow_html=True)

    st.markdown(
        '### Atividade por dia da semana × período '
        '<span style="font-family: var(--serif); font-style: italic; '
        'text-transform: none; letter-spacing: 0; color: var(--sepia-fieldnote); '
        'font-size: 14px; font-weight: 400;">(QTD_Liquidos médio)</span>',
        unsafe_allow_html=True,
    )
    fig = _heatmap(msgs)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.markdown(
        '<div style="font-family: var(--serif); font-size: 14px; font-style: italic; '
        'color: var(--sepia-fieldnote); margin-top: -8px;">'
        'Visualização canônica derivada do relatório de tese (YLAI_V2.pdf, página 6) '
        '— sub-períodos definidos em <em>enums.py:SubPeriod</em>.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('## Próximo passo')
    st.markdown(
        '<div class="qc-prose">'
        '<p>A análise propriamente começa em <em>Frame: Keys</em>, onde os '
        'conteúdos são examinados pela ótica das três grandezas discursivas '
        '— laminação, fabricação e texto puro — segundo a fórmula central '
        'da metodologia.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="qc-formula">'
        '<span class="var">Qtd_liq_car</span>'
        '<span class="op">=</span>'
        '<span class="var">Qtd_char_total</span>'
        '<span class="op">−</span>'
        '<span>(<span class="var">chamadas</span><span class="op">+</span>'
        '<span class="var">links</span><span class="op">+</span>'
        '<span class="var">emails</span><span class="op">+</span>'
        '<span class="var">emojis</span>)</span>'
        '<span class="qc-formula-foot">'
        'Cavalcante &amp; Hanke (2020) · operacionalização em '
        '<em>models.py:Message[\'Qty_char_net\']</em>'
        '</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button('Ir para Frame: Keys →', type='primary', use_container_width=True):
            st.switch_page('pages/2_Keys.py')
    with col2:
        if st.button('Carregar outro chat', use_container_width=True):
            from ..state import clear_chat
            clear_chat()
            st.switch_page('app.py')
