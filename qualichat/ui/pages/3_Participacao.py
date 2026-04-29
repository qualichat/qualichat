"""Frame: Participação — placeholder for Sprint 3."""

from __future__ import annotations

import streamlit as st

from qualichat.ui.components.chrome import bootstrap
from qualichat.ui.components.empty_state import empty_state
from qualichat.ui.state import has_chat


def main() -> None:
    bootstrap(
        page_title='Participação',
        breadcrumb='Participação',
        active_slug='participacao',
    )

    if not has_chat():
        empty_state()
        return

    st.markdown('# Participação')
    st.markdown(
        '<div class="qc-lede">'
        'Os 7 charts da ParticipationStatusFrame — Mensagens por ator, '
        'Mensagens por semana, Bots, Repertório de mídia, Estatísticas, '
        'Lam. por atores, Fab. por atores — chegam na Sprint 3.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="qc-notice qc-notice-info">'
        '<div class="qc-notice-title">Em construção</div>'
        '<p>Sprint 3.</p>'
        '</div>',
        unsafe_allow_html=True,
    )


main()
