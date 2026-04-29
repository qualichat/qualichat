"""
qualichat.ui.styling
~~~~~~~~~~~~~~~~~~~~

CSS injection — applies the design tokens defined in
``docs/wireframes/index.html`` (pergaminho/tinta/sépia/ocre/musgo/toga
palette + EB Garamond/Source Sans 3/JetBrains Mono typography) to the
Streamlit app via ``st.markdown(unsafe_allow_html=True)``.

Streamlit's CSS class names are not part of its stable public API, so
some of the overrides below may need adjustment between Streamlit
versions. The base palette and typography injection (via
``:root`` variables and Google Fonts) is stable.
"""

from __future__ import annotations

import streamlit as st


__all__ = ('inject_css', 'TOKENS')


TOKENS = {
    'pergaminho': '#F4EFE6',
    'pergaminho_claro': '#FAF7F1',
    'tinta_impressao': '#1A1814',
    'sepia_fieldnote': '#7A6B5A',
    'ocre_encadernacao': '#B8860B',
    'musgo_biblioteca': '#3B5249',
    'marginalia_vermelha': '#922B21',
    'toga_academica': '#1F3A5F',
}


_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Source+Sans+3:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
  :root {
    --pergaminho: #F4EFE6;
    --pergaminho-claro: #FAF7F1;
    --tinta-impressao: #1A1814;
    --sepia-fieldnote: #7A6B5A;
    --ocre-encadernacao: #B8860B;
    --musgo-biblioteca: #3B5249;
    --marginalia-vermelha: #922B21;
    --toga-academica: #1F3A5F;

    --borda-padrao: rgba(26, 24, 20, 0.08);
    --borda-emphasis: rgba(26, 24, 20, 0.18);
    --borda-focus: rgba(26, 24, 20, 0.32);

    --serif: 'EB Garamond', Georgia, 'Times New Roman', serif;
    --sans: 'Source Sans 3', system-ui, -apple-system, sans-serif;
    --mono: 'JetBrains Mono', 'Source Code Pro', Consolas, monospace;
  }

  /* Page background — pergaminho */
  .stApp { background: var(--pergaminho); color: var(--tinta-impressao); }
  [data-testid="stAppViewContainer"] { background: var(--pergaminho); }
  [data-testid="stHeader"] { background: var(--pergaminho); border-bottom: 1px solid var(--borda-padrao); }
  [data-testid="stToolbar"] { background: var(--pergaminho); }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: var(--pergaminho);
    border-right: 1px solid var(--borda-padrao);
  }
  [data-testid="stSidebar"] > div { background: var(--pergaminho); }

  /* Hide Streamlit's default page nav — we render our own via
     st.page_link calls in the sidebar (which still preserve session
     state across pages). */
  [data-testid="stSidebarNav"] { display: none; }

  /* Streamlit's emotion-CSS injects rgb(49,51,63) at higher specificity
     than plain class selectors, so sidebar text overrides need
     !important to win. The deep selectors below cover the nested
     <span><div><p>label</p></div></span> structure of stPageLink. */

  [data-testid="stSidebar"] .qc-nav-title {
    color: var(--sepia-fieldnote) !important;
  }

  /* Page link container + every descendant — force tinta-impressao */
  [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"],
  [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] *,
  [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] span,
  [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] p {
    color: var(--tinta-impressao) !important;
    font-family: var(--sans) !important;
    background: transparent !important;
  }
  [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
    padding: 6px 8px 6px 22px !important;
    position: relative;
    display: block;
    text-decoration: none;
    border: 0;
    border-radius: 2px;
  }
  [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]::before {
    content: '◇';
    position: absolute;
    left: 4px;
    top: 8px;
    color: var(--sepia-fieldnote);
    font-size: 11px;
  }
  [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover,
  [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover *,
  [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover p {
    color: var(--toga-academica) !important;
  }

  /* The decorative tree (<details>/<summary>) and tree items */
  [data-testid="stSidebar"] details summary {
    color: var(--sepia-fieldnote) !important;
    font-family: var(--serif) !important;
  }
  [data-testid="stSidebar"] ul.qc-flow li {
    color: var(--sepia-fieldnote);
  }
  [data-testid="stSidebar"] ul.qc-flow li.branch {
    color: rgba(122, 107, 90, 0.7) !important;
  }
  [data-testid="stSidebar"] ul.qc-flow li.branch.active {
    color: var(--toga-academica) !important;
  }

  /* Headlines: Garamond */
  h1, h2, h3, h4, h5, h6,
  [data-testid="stHeading"] h1,
  [data-testid="stHeading"] h2,
  [data-testid="stHeading"] h3 {
    font-family: var(--serif) !important;
    color: var(--tinta-impressao);
    letter-spacing: -0.005em;
    font-weight: 500;
  }
  h1 { font-size: 32px !important; line-height: 1.2; }
  h2 { font-size: 22px !important; }

  /* Body — keep Source Sans for readability of UI chrome,
     but our custom .body-prose blocks use Garamond */
  body, .stApp, [data-testid="stMarkdownContainer"] p {
    font-family: var(--sans);
  }

  /* Form labels (the small uppercase label above an input) */
  [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p {
    font-family: var(--sans) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--sepia-fieldnote) !important;
  }

  /* Radio + checkbox option labels — Streamlit sets rgb(49,51,63) which
     is too light against pergaminho. Force tinta-impressao for the
     option text (the rendered <p> inside the <label>). */
  [data-testid="stMainBlockContainer"] [role="radiogroup"] label p,
  [data-testid="stMainBlockContainer"] [role="radiogroup"] label,
  [data-testid="stMainBlockContainer"] [data-testid="stCheckbox"] label p,
  [data-testid="stMainBlockContainer"] [data-testid="stCheckbox"] label,
  [data-testid="stMainBlockContainer"] [data-baseweb="checkbox"] span {
    color: var(--tinta-impressao) !important;
    font-family: var(--sans) !important;
  }

  /* Multiselect & selectbox option text */
  [data-testid="stMainBlockContainer"] [data-baseweb="select"] *,
  [data-testid="stMainBlockContainer"] [data-baseweb="tag"] * {
    color: var(--tinta-impressao) !important;
  }

  /* Plain text inside markdown blocks in main content (descriptions,
     prose paragraphs) — only those NOT inside a custom .qc- container */
  [data-testid="stMainBlockContainer"] [data-testid="stMarkdownContainer"] p,
  [data-testid="stMainBlockContainer"] [data-testid="stMarkdownContainer"] li,
  [data-testid="stMainBlockContainer"] [data-testid="stMarkdownContainer"] strong {
    color: var(--tinta-impressao);
  }

  /* Buttons — toga-academica primary */
  .stButton > button {
    font-family: var(--sans);
    font-weight: 500;
    border-radius: 2px;
    background: var(--toga-academica);
    color: var(--pergaminho-claro);
    border: 1px solid var(--toga-academica);
    transition: all 120ms ease;
  }
  .stButton > button:hover {
    background: var(--tinta-impressao);
    border-color: var(--tinta-impressao);
    color: var(--pergaminho-claro);
  }
  .stButton > button[kind="secondary"] {
    background: transparent;
    color: var(--toga-academica);
  }

  /* Inputs */
  .stTextInput input, .stNumberInput input, .stTextArea textarea {
    font-family: var(--mono);
    background: var(--pergaminho-claro);
    border: 1px solid var(--borda-emphasis);
    border-radius: 2px;
    color: var(--tinta-impressao);
  }

  /* File uploader — make it serif/inviting */
  [data-testid="stFileUploader"] section {
    background: var(--pergaminho);
    border: 1px dashed var(--borda-emphasis);
    border-radius: 2px;
  }
  [data-testid="stFileUploader"] section button {
    background: transparent;
    color: var(--toga-academica);
    border: 1px solid var(--toga-academica);
  }

  /* Radio + checkbox accent */
  input[type="radio"], input[type="checkbox"] { accent-color: var(--toga-academica); }

  /* Custom blocks */
  .qc-brand {
    font-family: var(--serif);
    font-size: 28px;
    font-weight: 500;
    letter-spacing: -0.01em;
  }
  .qc-brand-sub {
    font-family: var(--serif);
    font-style: italic;
    color: var(--sepia-fieldnote);
    margin-left: 12px;
    font-size: 16px;
  }
  .qc-pill {
    font-family: var(--mono);
    font-size: 12px;
    padding: 2px 8px;
    border: 1px solid var(--borda-padrao);
    border-radius: 2px;
    color: var(--tinta-impressao);
    background: var(--pergaminho-claro);
  }
  .qc-breadcrumb {
    font-family: var(--sans);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--sepia-fieldnote);
    margin-bottom: 16px;
  }
  .qc-lede {
    font-family: var(--serif);
    font-size: 19px;
    font-style: italic;
    color: var(--sepia-fieldnote);
    line-height: 1.5;
    max-width: 60ch;
    margin: 24px 0 48px 0;
    padding-left: 24px;
    border-left: 2px solid var(--borda-emphasis);
  }
  .qc-prose {
    font-family: var(--serif);
    font-size: 17px;
    line-height: 1.7;
    max-width: 64ch;
    color: var(--tinta-impressao);
  }
  .qc-prose em { font-style: italic; color: var(--musgo-biblioteca); }
  .qc-prose p { margin: 0 0 24px 0; }

  .qc-formula {
    background: var(--pergaminho-claro);
    border: 1px solid var(--borda-padrao);
    border-left: 3px solid var(--ocre-encadernacao);
    padding: 16px 24px;
    margin: 24px 0;
    font-family: var(--serif);
    font-size: 19px;
    font-style: italic;
    color: var(--tinta-impressao);
    line-height: 1.6;
  }
  .qc-formula .var { font-weight: 500; color: var(--toga-academica); font-style: normal; }
  .qc-formula .op { color: var(--sepia-fieldnote); font-style: normal; padding: 0 4px; }
  .qc-formula-foot {
    display: block;
    font-family: var(--sans);
    font-style: normal;
    font-size: 11px;
    color: var(--sepia-fieldnote);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 6px;
  }

  .qc-notice {
    border-left: 3px solid var(--marginalia-vermelha);
    padding: 16px 24px;
    margin: 32px 0;
    background: rgba(146, 43, 33, 0.03);
  }
  .qc-notice-title {
    font-family: var(--sans);
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--marginalia-vermelha);
    margin-bottom: 6px;
  }
  .qc-notice p {
    font-family: var(--serif);
    font-size: 15px;
    line-height: 1.55;
    margin: 0;
    color: var(--tinta-impressao);
  }
  .qc-notice.qc-notice-info { border-left-color: var(--ocre-encadernacao); background: rgba(184, 134, 11, 0.04); }
  .qc-notice.qc-notice-info .qc-notice-title { color: var(--ocre-encadernacao); }

  /* Definition list (Resumo stats) */
  dl.qc-def {
    margin: 24px 0;
    padding: 0;
    display: grid;
    grid-template-columns: max-content 1fr;
    gap: 16px 32px;
  }
  dl.qc-def dt {
    font-family: var(--sans);
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--sepia-fieldnote);
    align-self: baseline;
  }
  dl.qc-def dd {
    font-family: var(--mono);
    font-size: 15px;
    color: var(--tinta-impressao);
    margin: 0;
  }
  dl.qc-def dd em {
    font-family: var(--serif);
    font-style: italic;
    color: var(--sepia-fieldnote);
    margin-left: 8px;
    font-size: 14px;
  }

  /* Stack-bar (segmented horizontal bar) */
  .qc-stack {
    display: flex;
    height: 38px;
    border: 1px solid var(--borda-padrao);
    background: var(--pergaminho-claro);
    overflow: hidden;
    margin: 16px 0;
  }
  .qc-stack .seg {
    color: var(--pergaminho-claro);
    font-family: var(--mono);
    font-size: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-right: 1px solid rgba(255,255,255,0.4);
    overflow: hidden;
    white-space: nowrap;
    padding: 0 4px;
  }
  .qc-stack .seg:last-child { border-right: 0; }
  .qc-stack-legend {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
    gap: 6px 24px;
    margin-top: 8px;
    font-family: var(--sans);
    font-size: 12px;
    color: var(--sepia-fieldnote);
  }
  .qc-stack-legend .swatch {
    display: inline-block;
    width: 10px; height: 10px;
    margin-right: 6px;
    vertical-align: middle;
  }

  /* Empty state */
  .qc-empty {
    text-align: center;
    padding: 64px 32px;
    color: var(--sepia-fieldnote);
  }
  .qc-empty .glyph {
    font-family: var(--serif);
    font-size: 64px;
    color: var(--borda-emphasis);
    margin-bottom: 16px;
    line-height: 1;
  }
  .qc-empty h2 {
    font-family: var(--serif);
    font-size: 24px;
    color: var(--tinta-impressao);
    margin: 0 0 16px 0 !important;
  }
  .qc-empty p {
    font-family: var(--serif);
    font-size: 16px;
    font-style: italic;
    max-width: 50ch;
    margin: 0 auto 32px auto;
    line-height: 1.5;
  }

  /* Sidebar nav (tree flowchart) */
  .qc-nav-title {
    font-family: var(--serif);
    font-size: 13px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--sepia-fieldnote);
    margin: 0 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--borda-padrao);
  }
  ul.qc-flow {
    list-style: none; margin: 0; padding: 0;
    font-family: var(--sans); font-size: 13px;
  }
  ul.qc-flow li { position: relative; padding: 5px 0 5px 22px; }
  ul.qc-flow li::before {
    content: '◇'; position: absolute; left: 4px; top: 6px;
    color: var(--sepia-fieldnote); font-size: 10px;
  }
  ul.qc-flow li.section { padding-top: 12px; color: var(--tinta-impressao); font-weight: 500; font-size: 14px; }
  ul.qc-flow li.section.active { color: var(--toga-academica); }
  ul.qc-flow li.section.active::before { content: '◆'; color: var(--toga-academica); }
  ul.qc-flow li.branch { padding-left: 32px; color: var(--sepia-fieldnote); font-size: 13px; }
  ul.qc-flow li.branch::before { content: '└'; left: 16px; top: 3px; font-size: 12px; color: var(--borda-emphasis); }
  ul.qc-flow li.branch.muted { color: rgba(122, 107, 90, 0.55); }
  ul.qc-flow li.branch.active { color: var(--toga-academica); font-weight: 500; }
  ul.qc-flow li.branch.active::before { content: '├'; color: var(--toga-academica); }
  ul.qc-flow li.branch .api {
    font-family: var(--mono); font-size: 9px; color: var(--ocre-encadernacao);
    margin-left: 6px; text-transform: uppercase; letter-spacing: 0.06em;
  }
  ul.qc-flow li a { color: inherit; text-decoration: none; }
  ul.qc-flow li a:hover { color: var(--tinta-impressao); }

  .qc-side-meta {
    font-family: var(--mono);
    font-size: 12px;
    color: var(--tinta-impressao);
    margin-top: 32px;
  }
  .qc-side-meta-sub {
    font-family: var(--serif);
    font-size: 13px;
    font-style: italic;
    color: var(--sepia-fieldnote);
    margin-top: 4px;
  }
</style>
"""


def inject_css() -> None:
    """Inject the design tokens and component CSS into the page.

    Call this once at the top of every page (after :func:`st.set_page_config`).
    """
    st.markdown(_CSS, unsafe_allow_html=True)
