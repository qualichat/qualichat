"""Empty state for pages that require a loaded chat."""

from __future__ import annotations

from html import escape

import streamlit as st


__all__ = ('empty_state',)


def empty_state(
    *,
    title: str = 'Nenhum chat carregado',
    body: str = (
        'Esta tela aparece após você subir uma exportação do WhatsApp. '
        'Volte ao Início, escolha o arquivo, e os indicadores serão '
        'calculados aqui.'
    ),
    glyph: str = '◇',
) -> None:
    """Render the centered empty-state block."""
    st.markdown(
        f'''
        <div class="qc-empty">
          <div class="glyph">{escape(glyph)}</div>
          <h2>{escape(title)}</h2>
          <p>{escape(body)}</p>
        </div>
        ''',
        unsafe_allow_html=True,
    )
    if st.button('Ir para Início', type='primary'):
        st.switch_page('app.py')
