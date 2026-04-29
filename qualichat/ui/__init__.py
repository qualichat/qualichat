"""
qualichat.ui
~~~~~~~~~~~~

Streamlit-based web interface for Qualichat.

The package is intentionally side-effect-free at import time so that the
core library remains usable without ``streamlit`` installed. Only
``qualichat.ui.app:main`` and the page modules touch ``streamlit``.

:copyright: (c) 2021-present Ernest Manheim
:license: MIT, see LICENSE for more details.
"""

from __future__ import annotations

from pathlib import Path


__all__ = ('APP_PATH', 'launch')


APP_PATH: Path = Path(__file__).resolve().parent / 'app.py'


def launch(*, port: int = 8501, headless: bool = False) -> int:
    """Start the Streamlit UI as a subprocess. Returns the exit code.

    Used by ``python -m qualichat ui`` (see :mod:`qualichat.__main__`).
    """
    import subprocess
    import sys

    cmd = [
        sys.executable, '-m', 'streamlit', 'run', str(APP_PATH),
        '--server.port', str(port),
    ]
    if headless:
        cmd += ['--server.headless', 'true']

    return subprocess.call(cmd)
