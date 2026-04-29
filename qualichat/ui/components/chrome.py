"""
qualichat.ui.components.chrome
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Page-level chrome: header brand bar (top of main area), sidebar with
the "Menu Keys" tree-flowchart navigation. Both are rendered via
``st.markdown(unsafe_allow_html=True)`` so they match the wireframe
typography exactly.
"""

from __future__ import annotations

from html import escape
from typing import Optional, Sequence

import streamlit as st

import qualichat
from ..state import get_chat_filename, has_chat
from ..styling import inject_css


def _populate_secrets_into_config() -> None:
    """Mirror keys from ``st.secrets`` into the in-memory ``Config``.

    Streamlit Cloud encrypts ``[secrets]`` at rest and exposes them at
    runtime via ``st.secrets``. We copy known keys into qualichat's
    ``Config`` so charts that read ``config['google_api_key']`` work
    transparently — without writing the secret to ``~/.qualichat/config.json``
    on the (ephemeral) container disk.
    """
    try:
        secrets = dict(st.secrets)
    except Exception:
        # No secrets.toml locally and no Cloud Secrets: legitimate case.
        return
    if not secrets:
        return
    api_key = secrets.get('google_api_key', '').strip()
    if api_key:
        from qualichat.utils import config
        config['google_api_key'] = api_key
        # No `config.save()` — keep it in memory only.


__all__ = ('bootstrap', 'sidebar', 'header')


# (label, slug, kind)  — kind in {'section', 'branch'}
# slug is the page identifier — matches the routing key the page uses.
_NAV: Sequence[tuple[str, str, str, Optional[str]]] = (
    ('Início',                          'home',           'section', None),
    ('Resumo',                          'resumo',         'section', None),
    ('Frame: Keys',                     'keys',           'section', None),
    ('Lamination',                      'keys',           'branch',  None),
    ('Links',                           'keys',           'branch',  None),
    ('Calls',                           'keys',           'branch',  None),
    ('Emails',                          'keys',           'branch',  None),
    ('Textual symbols',                 'keys',           'branch',  None),
    ('Messages',                        'keys',           'branch',  None),
    ('Keyword',                         'keys',           'branch',  None),
    ('Ratings',                         'keys',           'branch',  'api'),
    ('Participação',                    'participacao',   'section', None),
    ('Mensagens por ator',              'participacao',   'branch',  None),
    ('Mensagens por semana',            'participacao',   'branch',  None),
    ('Bots',                            'participacao',   'branch',  None),
    ('Repertório de mídia',             'participacao',   'branch',  None),
    ('Estatísticas',                    'participacao',   'branch',  None),
    ('Lam. por atores',                 'participacao',   'branch',  None),
    ('Fab. por atores',                 'participacao',   'branch',  None),
    ('Opinião pública',                 'opiniao',        'section', None),
    ('Matriz de polaridade',            'opiniao',        'branch',  None),
    ('Linkage temático',                'opiniao',        'branch',  None),
    ('Exportar',                        'exportar',       'section', None),
)


def header(breadcrumb: str, *, title: Optional[str] = None) -> None:
    """Render the top brand bar with a page breadcrumb.

    The ``title`` is optional — most pages prefer ``st.title`` directly,
    but the breadcrumb sits above whatever title the page uses.
    """
    chat_pill = ''
    if has_chat():
        fn = escape(get_chat_filename())
        chat_pill = f'<span class="qc-pill">{fn}</span>'

    pill_version = f'<span class="qc-pill">v{qualichat.__version__}</span>'
    meta_right = chat_pill if chat_pill else (
        '<span style="font-family: var(--sans); font-size: 12px; '
        'color: var(--sepia-fieldnote);">tudo local · sua máquina</span>'
    )

    st.markdown(
        f'''
        <div style="display: flex; justify-content: space-between;
             align-items: baseline; padding: 8px 0 24px 0;
             border-bottom: 1px solid var(--borda-padrao); margin-bottom: 24px;">
          <div>
            <span class="qc-brand">qualichat</span>
            <span class="qc-brand-sub">após Cavalcante &amp; Hanke (2020)</span>
          </div>
          <div style="display: flex; gap: 24px; align-items: center;">
            {pill_version}
            {meta_right}
          </div>
        </div>
        <div class="qc-breadcrumb">{escape(breadcrumb)}</div>
        ''',
        unsafe_allow_html=True,
    )


def _decorative_tree(active_slug: str) -> str:
    """Build the read-only tree-flowchart HTML below the active page links.

    Sub-items per frame are listed but not interactive — they show what is
    inside each section (Sprint 2 will turn them into real pages).
    """
    chat_loaded = has_chat()
    items_html = []
    for label, slug, kind, badge in _NAV:
        if kind == 'section':
            continue  # sections are now real st.page_link entries
        cls = kind
        if slug == active_slug:
            cls += ' active'
        elif not chat_loaded:
            cls += ' muted'
        badge_html = f' <span class="api">{badge}</span>' if badge else ''
        items_html.append(f'<li class="{cls}">{escape(label)}{badge_html}</li>')

    return (
        '<details style="margin-top: 32px;"><summary style="font-family: var(--serif); '
        'font-size: 12px; font-weight: 500; text-transform: uppercase; '
        'letter-spacing: 0.12em; color: var(--sepia-fieldnote); cursor: pointer; '
        'padding-bottom: 8px; border-bottom: 1px solid var(--borda-padrao);">'
        'Sub-charts disponíveis</summary>'
        f'<ul class="qc-flow" style="margin-top: 8px;">{"".join(items_html)}</ul>'
        '</details>'
    )


def sidebar(active_slug: str) -> None:
    """Render the left sidebar with the Menu Keys navigation.

    Uses ``st.sidebar.page_link`` for the section-level links (which
    preserves Streamlit's session_state across pages) plus a collapsible
    decorative tree showing the sub-charts within each frame.
    """
    st.sidebar.markdown(
        '<h3 class="qc-nav-title">Menu Keys</h3>',
        unsafe_allow_html=True,
    )

    # Section-level links — only these are real pages. Sub-charts live
    # inside the frame pages (Keyword chart, Lamination chart, etc).
    # No emoji icons (Streamlit rejects ◇); CSS prepends the diamond glyph.
    st.sidebar.page_link('app.py',                       label='Início')
    st.sidebar.page_link('pages/1_Resumo.py',            label='Resumo')
    st.sidebar.page_link('pages/2_Keys.py',              label='Frame: Keys')
    st.sidebar.page_link('pages/3_Participacao.py',      label='Participação')
    st.sidebar.page_link('pages/4_Opiniao_Publica.py',   label='Opinião pública')
    st.sidebar.page_link('pages/5_Exportar.py',          label='Exportar')
    st.sidebar.page_link('pages/9_Setup.py',             label='Setup')

    # Decorative tree of sub-charts (collapsed by default) — same content
    # shown in the wireframe, here as a reference of what lives inside
    # each frame. Will become clickable in later sprints.
    st.sidebar.markdown(_decorative_tree(active_slug), unsafe_allow_html=True)

    if has_chat():
        st.sidebar.markdown(
            '<div class="qc-side-meta" style="margin-top: 24px;">'
            f'{escape(get_chat_filename())}</div>',
            unsafe_allow_html=True,
        )

    # Citation links (always visible at the bottom)
    st.sidebar.markdown(
        '<div style="margin-top: 32px;">'
        '<h3 class="qc-nav-title">Citar este trabalho</h3>'
        '<a href="#" style="font-family: var(--sans); font-size: 13px; '
        'color: var(--toga-academica); text-decoration: none; display: block; padding: 4px 0;">'
        '↓ BibTeX</a>'
        '<a href="#" style="font-family: var(--sans); font-size: 13px; '
        'color: var(--toga-academica); text-decoration: none; display: block; padding: 4px 0;">'
        '↓ CITATION.cff</a>'
        '</div>',
        unsafe_allow_html=True,
    )


def bootstrap(*, page_title: str, breadcrumb: str, active_slug: str) -> None:
    """One-call setup for any page: page_config, CSS, sidebar, header.

    Call this once at the very top of every page (after the
    ``st.set_page_config`` if used; this helper calls it for you when
    page_title is provided).
    """
    st.set_page_config(
        page_title=f'qualichat — {page_title}',
        page_icon='◇',
        layout='wide',
        initial_sidebar_state='expanded',
    )
    _populate_secrets_into_config()
    inject_css()
    sidebar(active_slug)
    header(breadcrumb)
