"""Resumo page — aggregated indicators of the loaded chat."""

from __future__ import annotations

from qualichat.ui.components.chrome import bootstrap
from qualichat.ui.components.empty_state import empty_state
from qualichat.ui.components.summary import summary_block
from qualichat.ui.state import get_chat, get_chat_filename, has_chat


def main() -> None:
    bootstrap(
        page_title='Resumo',
        breadcrumb='Resumo',
        active_slug='resumo',
    )

    if not has_chat():
        empty_state()
        return

    import streamlit as st

    st.markdown(f'# {get_chat_filename()}')
    summary_block(get_chat())


main()
