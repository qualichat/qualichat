"""Exportar — placeholder for Sprint 5."""

from __future__ import annotations

import streamlit as st

from qualichat.ui.components.chrome import bootstrap
from qualichat.ui.components.empty_state import empty_state
from qualichat.ui.state import has_chat


def main() -> None:
    bootstrap(
        page_title='Exportar',
        breadcrumb='Exportar',
        active_slug='exportar',
    )

    if not has_chat():
        empty_state()
        return

    st.markdown('# Material para o paper')
    st.markdown(
        '<div class="qc-lede">'
        'Contact sheet das figuras geradas, citação canônica em BibTeX, '
        'archive da marginália desta sessão — Sprint 5.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('## Citação canônica')
    st.markdown(
        '<div class="qc-prose">'
        '<p>Use a referência abaixo no seu paper. A citação preferida em '
        '<em>CITATION.cff</em> é o paper-mãe (Cavalcante &amp; Hanke 2020), '
        'não o software — ferramentas se atualizam, conceitos permanecem.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.code(
        '@article{cavalcante2020ancoragens,\n'
        '  author    = {Cavalcante, Fernando Luiz Nobre and Hanke, Michael Mathias},\n'
        '  title     = {Ancoragens de interação em grupos midiatizados:\n'
        '               proposta quantiqualitativa},\n'
        '  journal   = {Comunicação Mídia e Consumo},\n'
        '  volume    = {17},\n'
        '  number    = {50},\n'
        '  year      = {2020},\n'
        '  doi       = {10.18568/cmc.v17i49.2227},\n'
        '}\n\n'
        '@software{qualichat,\n'
        '  author    = {Qualichat Contributors},\n'
        '  title     = {Qualichat: linguistic ethnography toolkit\n'
        '               for WhatsApp exports},\n'
        '  version   = {1.5.0},\n'
        '  year      = {2026},\n'
        '  url       = {https://github.com/qualichat/qualichat},\n'
        '}',
        language='bibtex',
    )


main()
