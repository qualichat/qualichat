"""
qualichat.ui.pipeline
~~~~~~~~~~~~~~~~~~~~~

Cached parse pipeline — wraps :class:`qualichat.chat.Chat` and
:class:`qualichat.core.Qualichat` so the same uploaded file is not
re-parsed on every Streamlit rerun.

The pipeline persists uploaded files into a per-session temp directory
that survives reruns (Streamlit calls the script top-to-bottom on
every interaction). Files older than the current session are GC'd
when the user uploads a new one.
"""

from __future__ import annotations

import hashlib
import logging
import tempfile
from pathlib import Path
from typing import Any, Tuple

import streamlit as st


__all__ = ('parse_uploaded', 'TEMP_PREFIX')


TEMP_PREFIX = 'qualichat_ui_'


def _digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()[:16]


@st.cache_resource(show_spinner=False)
def _parse_path(path: str, content_hash: str) -> Tuple[Any, Any]:
    """Run :class:`Chat` + :class:`Qualichat` on a saved file, cached.

    The ``content_hash`` parameter is part of the cache key so the same
    bytes do not trigger a reparse, but two different files saved at
    the same path do.
    """
    # Defer imports so importing ``qualichat.ui.pipeline`` does not
    # transitively load spaCy and friends until really needed.
    from qualichat.chat import Chat
    from qualichat.core import Qualichat

    logging.disable(logging.WARNING)  # silence chat-miner's verbose info logs
    chat = Chat(path)
    qc = Qualichat([chat])
    return chat, qc


def parse_uploaded(uploaded_file: Any) -> Tuple[Any, Any]:
    """Save an ``UploadedFile`` to a temp path and parse it.

    Parameters
    ----------
    uploaded_file
        The object returned by :func:`st.file_uploader`.

    Returns
    -------
    Tuple[:class:`qualichat.chat.Chat`, :class:`qualichat.core.Qualichat`]
        Parsed chat and a Qualichat instance ready to render frames.
    """
    payload = uploaded_file.getvalue()
    content_hash = _digest(payload)

    tmp_dir = Path(tempfile.gettempdir()) / f'{TEMP_PREFIX}{content_hash}'
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / uploaded_file.name
    if not tmp_path.exists() or tmp_path.read_bytes() != payload:
        tmp_path.write_bytes(payload)

    return _parse_path(str(tmp_path), content_hash)
