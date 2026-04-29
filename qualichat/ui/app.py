"""
qualichat.ui.app
~~~~~~~~~~~~~~~~

Streamlit entry point — the Home / Upload screen.

Run with::

    streamlit run qualichat/ui/app.py

Or via the CLI shortcut::

    python -m qualichat ui

This script is the "main" page of the multipage app. Files in the
``pages/`` subfolder (Resumo, Keys, Participação, Opinião pública,
Exportar, Setup) are auto-discovered by Streamlit.
"""

from __future__ import annotations

import streamlit as st

from qualichat.ui.components import bootstrap, empty_state  # noqa: F401  re-export
from qualichat.ui.components.chrome import bootstrap as _bootstrap
from qualichat.ui.pipeline import parse_uploaded
from qualichat.ui.state import clear_chat, has_chat, set_chat, set_qc


def _render_home() -> None:
    st.markdown('# Carregar uma exportação')
    st.markdown(
        '<div class="qc-lede">'
        'Aceita arquivos <em>.txt</em> ou <em>.zip</em> exportados do WhatsApp, '
        'para qualquer plataforma e localidade suportada por <em>chat-miner</em>.'
        '</div>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        'Arquivo .txt ou .zip',
        type=['txt', 'zip'],
        accept_multiple_files=False,
        help=(
            'iOS antigo · iOS novo · Android · pt-BR · en · es · de · it · fr '
            '· auto-detectado'
        ),
        label_visibility='collapsed',
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        anonymize = st.checkbox(
            'Substituir nomes reais por nomes de personagens',
            value=True,
            help=(
                'A primeira aparição de cada ator recebe um nome do pool '
                'bundled (767 personagens de Tolstói e Machado de Assis). '
                'Se o pool esgotar, fallback para Actor #N.'
            ),
        )
    with col2:
        # Multi-chat support is in the wireframe but still single-chat in MVP.
        st.checkbox(
            'Múltiplos chats (Sprint 2)',
            value=False,
            disabled=True,
            help='Comparar grupos lado a lado — em construção.',
        )

    if uploaded is not None:
        if st.button('Carregar exportação', type='primary'):
            with st.spinner('Parseando…'):
                try:
                    chat, qc = parse_uploaded(uploaded)
                except Exception as exc:  # noqa: BLE001
                    st.error(f'Falha ao parsear: {exc}')
                    return
            set_chat(chat, uploaded.name)
            set_qc(qc)
            st.success(
                f'Carregado: {len(chat.messages):,} mensagens · '
                f'{len(chat.actors)} atores · '
                f'{len(chat.system_messages):,} eventos de sistema.'
                .replace(',', '.')
            )
            st.markdown(
                '<div style="margin-top: 16px;">'
                'Próximo: abra a aba <strong>Resumo</strong> na barra lateral '
                'para ver os indicadores agregados.'
                '</div>',
                unsafe_allow_html=True,
            )
            if st.button('Abrir Resumo →'):
                st.switch_page('pages/1_Resumo.py')

    if not anonymize:
        st.markdown(
            '<div class="qc-notice">'
            '<div class="qc-notice-title">⚠ Anonimização desligada</div>'
            '<p>Sem anonimização, nomes reais aparecem nos charts. Recomendamos '
            'manter ligado para preservar a privacidade dos atores.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    # ─── Caderno de campo preview ────────────────────────────────────
    st.markdown('## Caderno de campo')
    st.markdown(
        '<div class="qc-prose">'
        '<p>Cada gráfico tem ao lado um espaço para você anotar observações '
        'enquanto analisa — datadas, salvas localmente em '
        '<em>~/.qualichat/notes/</em> como Markdown editável.</p>'
        '<p style="font-style: italic; color: var(--sepia-fieldnote); font-size: 15px;">'
        'Pesquisa qualitativa exige paciência. As anotações são o trabalho; '
        'os gráficos são insumos. (Implementação na Sprint 4.)</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ─── Sobre ───────────────────────────────────────────────────────
    st.markdown('## Sobre o que é isto')
    st.markdown(
        '<div class="qc-prose">'
        '<p><em>Qualichat</em> é uma ferramenta open-source de etnografia '
        'linguística para análise de exports do WhatsApp, baseada na proposta '
        'quantiqualitativa de Cavalcante &amp; Hanke (2020) sobre ancoragens '
        'em grupos midiatizados. Não é um analisador genérico; é instrumento '
        'de pesquisa.</p>'
        '<p>Os dados ficam na sua máquina. O parser, a anonimização, a '
        'geração de gráficos e as anotações são todos locais. O único serviço '
        'externo opcional é o Google Translate, e apenas no frame de '
        '<em>Opinião Pública</em> com tradução automática opt-in.</p>'
        '</div>',
        unsafe_allow_html=True,
    )


def _render_chat_loaded() -> None:
    st.markdown('# Chat carregado')
    st.markdown(
        '<div class="qc-prose">'
        f'<p>Já existe um chat na sessão: <em>{st.session_state.get("qc_chat_filename", "")}</em>.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button('Ir para Resumo →', type='primary', use_container_width=True):
            st.switch_page('pages/1_Resumo.py')
    with col2:
        if st.button('Carregar outro chat', use_container_width=True):
            clear_chat()
            st.rerun()


def main() -> None:
    _bootstrap(page_title='Início', breadcrumb='Início', active_slug='home')
    if has_chat():
        _render_chat_loaded()
    else:
        _render_home()


if __name__ == '__main__':
    main()
