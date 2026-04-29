"""Frame: Opinião Pública — placeholder for Sprint 3."""

from __future__ import annotations

import streamlit as st

from qualichat.ui.components.chrome import bootstrap
from qualichat.ui.components.empty_state import empty_state
from qualichat.ui.state import has_chat


def main() -> None:
    bootstrap(
        page_title='Opinião Pública',
        breadcrumb='Opinião Pública',
        active_slug='opiniao',
    )

    if not has_chat():
        empty_state()
        return

    st.markdown('# Opinião Pública')
    st.markdown(
        '<div class="qc-lede">'
        'Matriz de polaridade e Linkage temático — Sprint 3.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="qc-notice">'
        '<div class="qc-notice-title">⚠ Serviço externo · Google Translate</div>'
        '<p>Quando esta tela for ativada, a análise de polaridade enviará '
        'trechos de mensagens ao Google Translate para tradução automática '
        'ao inglês (limitação do TextBlob). O aviso aparecerá inline antes '
        'de qualquer chamada externa.</p>'
        '</div>',
        unsafe_allow_html=True,
    )


main()
