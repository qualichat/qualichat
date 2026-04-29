"""
qualichat.ui.state
~~~~~~~~~~~~~~~~~~

Thin wrappers over ``st.session_state`` so pages reference shared
session keys by name only — no string typos, no ``KeyError`` surprises.
"""

from __future__ import annotations

from typing import Any, Optional

import streamlit as st


__all__ = (
    'get_chat',
    'set_chat',
    'clear_chat',
    'has_chat',
    'get_qc',
    'set_qc',
    'get_chat_filename',
)


_CHAT_KEY = 'qc_chat'
_QUALICHAT_KEY = 'qc_qualichat'
_FILENAME_KEY = 'qc_chat_filename'


def get_chat() -> Optional[Any]:
    """Returns the loaded :class:`qualichat.chat.Chat` or ``None``."""
    return st.session_state.get(_CHAT_KEY)


def set_chat(chat: Any, filename: str) -> None:
    """Store the parsed Chat and its display filename in session_state."""
    st.session_state[_CHAT_KEY] = chat
    st.session_state[_FILENAME_KEY] = filename


def clear_chat() -> None:
    """Drop chat + qualichat instance + filename from session_state."""
    for key in (_CHAT_KEY, _QUALICHAT_KEY, _FILENAME_KEY):
        st.session_state.pop(key, None)


def has_chat() -> bool:
    return _CHAT_KEY in st.session_state and st.session_state[_CHAT_KEY] is not None


def get_qc() -> Optional[Any]:
    """Returns the cached Qualichat instance (frames) or ``None``."""
    return st.session_state.get(_QUALICHAT_KEY)


def set_qc(qc: Any) -> None:
    st.session_state[_QUALICHAT_KEY] = qc


def get_chat_filename() -> str:
    return st.session_state.get(_FILENAME_KEY, '')
