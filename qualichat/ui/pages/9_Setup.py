"""Setup — primeira execução, baixa modelos spaCy + configura API key."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import streamlit as st

from qualichat.ui.components.chrome import bootstrap


def _spacy_available(model: str) -> bool:
    try:
        import importlib
        importlib.import_module(model)
        return True
    except (ImportError, OSError):
        return False


def _download_spacy_model(model: str) -> tuple[bool, str]:
    """Download a spaCy model in a subprocess. Returns (ok, log)."""
    proc = subprocess.run(
        [sys.executable, '-m', 'spacy', 'download', model, '-q'],
        capture_output=True, text=True, timeout=300,
    )
    return proc.returncode == 0, (proc.stdout + proc.stderr)[-2000:]


def main() -> None:
    bootstrap(
        page_title='Setup',
        breadcrumb='Setup · primeira execução',
        active_slug='setup',
    )

    st.markdown('# Configurar o qualichat')
    st.markdown(
        '<div class="qc-lede">'
        'Antes da primeira análise, três passos rápidos. Equivalente a '
        '<em>qualichat setup</em> no terminal — preferível só rodar uma vez.'
        '</div>',
        unsafe_allow_html=True,
    )

    # ─── Step 01: spaCy models ───────────────────────────────────────
    st.markdown('### 01 · Modelos de linguagem do spaCy')
    st.markdown(
        '<div class="qc-prose">'
        '<p>Baixa <em>pt_core_news_sm</em> (português, ~12 MB) e '
        '<em>en_core_web_sm</em> (inglês, ~12 MB) para análise morfológica '
        'em <em>Keys → Keyword</em> e <em>Public Opinion</em>.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        pt_ok = _spacy_available('pt_core_news_sm')
        st.markdown(
            f'`pt_core_news_sm`: {"✓ instalado" if pt_ok else "✗ não instalado"}'
        )
        if not pt_ok and st.button('Baixar pt_core_news_sm'):
            with st.spinner('Baixando…'):
                ok, log = _download_spacy_model('pt_core_news_sm')
            if ok:
                st.success('Baixado.')
            else:
                st.error('Falhou:')
                st.code(log)
    with col2:
        en_ok = _spacy_available('en_core_web_sm')
        st.markdown(
            f'`en_core_web_sm`: {"✓ instalado" if en_ok else "✗ não instalado"}'
        )
        if not en_ok and st.button('Baixar en_core_web_sm'):
            with st.spinner('Baixando…'):
                ok, log = _download_spacy_model('en_core_web_sm')
            if ok:
                st.success('Baixado.')
            else:
                st.error('Falhou:')
                st.code(log)

    # ─── Step 02: Google API key ─────────────────────────────────────
    st.markdown('### 02 · Google API key (opcional)')
    st.markdown(
        '<div class="qc-prose">'
        '<p>Necessária apenas para <em>Keys → Ratings</em> (busca metadata '
        'de vídeos do YouTube via API). Se não usar esse chart, deixe em '
        'branco. Salva em <em>~/.qualichat/config.json</em>.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    from qualichat.utils import config

    current = config['google_api_key'] if 'google_api_key' in config else ''
    new_key = st.text_input(
        'API key',
        value=current or '',
        type='password',
        placeholder='AIzaSy...',
    )
    if st.button('Salvar API key'):
        config['google_api_key'] = new_key
        config.save()
        st.success('Salva em ~/.qualichat/config.json.')

    # ─── Step 03: Data folder ────────────────────────────────────────
    st.markdown('### 03 · Pasta de dados local')
    home = Path.home() / '.qualichat'
    st.markdown(f'`{home}`')
    if home.exists():
        st.markdown(
            '<div class="qc-prose">'
            f'<p style="color: var(--musgo-biblioteca);">'
            '✓ pasta existe. Configurações e marginálias futuras serão salvas aqui.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="qc-prose">'
            '<p>A pasta será criada automaticamente quando você salvar a primeira '
            'configuração ou marginália.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    # ─── Privacy notice ──────────────────────────────────────────────
    st.markdown(
        '<div class="qc-notice qc-notice-info">'
        '<div class="qc-notice-title">Privacidade</div>'
        '<p>Os modelos do spaCy são baixados uma vez e ficam locais. A API '
        'key, se preenchida, é gravada em <em>~/.qualichat/config.json</em> '
        'e nunca deixa sua máquina, exceto nas chamadas explícitas ao '
        'Google quando você usar o chart Ratings.</p>'
        '</div>',
        unsafe_allow_html=True,
    )


main()
