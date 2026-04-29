"""
qualichat.ui.runtime
~~~~~~~~~~~~~~~~~~~~

Bridge between the prompt-driven CLI charts and the Streamlit UI.

Charts in :mod:`qualichat.frames` and :mod:`qualichat.sorters` ask the user
questions through ``questionary`` (via the ``select`` / ``checkbox`` /
``input`` partials), then call ``fig.show()`` to open the chart in a browser
window. Neither pattern works inside a Streamlit page where:

1. The user has already made their choices via Streamlit widgets, and
2. The figure must be rendered inline with ``st.plotly_chart`` instead.

This module provides three context managers that, used together, let us
drive the existing chart code unchanged:

* :func:`replay`           swaps select/checkbox/input for a queue.
* :func:`capture_figures`  swaps ``BaseFigure.show`` for a collector.
* :func:`silent_progress`  swaps the rich progress bar for a no-op.

:copyright: (c) 2021-present Ernest Manheim
:license: MIT
"""

from __future__ import annotations

import importlib
from contextlib import contextmanager
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    List,
    Sequence,
)


__all__ = (
    'PromptQueueExhausted',
    'replay',
    'capture_figures',
    'silent_progress',
    'run_chart',
)


# Modules that imported select/checkbox/input via ``from ._partials import *``
# need to be patched in their own namespaces — Python ``from-import`` binds
# names eagerly, so patching ``_partials.select`` alone is not enough.
_PROMPT_CONSUMERS: tuple = (
    'qualichat._partials',
    'qualichat.frames',
    'qualichat.sorters',
)


class PromptQueueExhausted(RuntimeError):
    """Raised when the chart asks more questions than answers were queued."""


class _Reply:
    """Stand-in for a ``questionary.Question``.

    The chart calls ``select(...).ask()``; we return one of these so ``.ask()``
    pops the next answer from the queue. Caller never sees the questionary
    machinery.
    """

    __slots__ = ('_value',)

    def __init__(self, value: Any) -> None:
        self._value = value

    def ask(self) -> Any:
        return self._value


class _PromptDriver:
    """Holds the queue of pre-recorded answers and serves them in order."""

    __slots__ = ('_queue', '_history')

    def __init__(self, answers: Iterable[Any]) -> None:
        # Materialise eagerly so an exhausted iterator does not surprise us.
        self._queue: List[Any] = list(answers)
        self._history: List[tuple] = []

    def __call__(self, message: str = '', *args: Any, **kwargs: Any) -> _Reply:
        if not self._queue:
            raise PromptQueueExhausted(
                f'Chart asked for an answer to {message!r} but the prompt '
                'queue is empty. Add more answers via the UI controls.'
            )
        value = self._queue.pop(0)
        self._history.append((message, value))
        return _Reply(value)

    @property
    def remaining(self) -> int:
        return len(self._queue)

    @property
    def history(self) -> Sequence[tuple]:
        return tuple(self._history)


@contextmanager
def replay(answers: Sequence[Any]) -> Iterator[_PromptDriver]:
    """Patch select/checkbox/input across qualichat to consume ``answers``.

    Usage::

        with replay(['By Actor', 'All', 'Verbs']) as driver:
            chart_callable(chats)
            assert driver.remaining == 0  # all answers consumed

    The patch covers every module that does ``from ._partials import *``
    (currently ``frames`` and ``sorters``), in addition to ``_partials``
    itself, because Python binds those names at import time.
    """
    driver = _PromptDriver(answers)

    saved: dict = {}
    targets = ('select', 'checkbox', 'input', 'password')

    try:
        for module_name in _PROMPT_CONSUMERS:
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                continue
            for name in targets:
                if hasattr(module, name):
                    saved[(module_name, name)] = getattr(module, name)
                    setattr(module, name, driver)
        yield driver
    finally:
        for (module_name, name), original in saved.items():
            module = importlib.import_module(module_name)
            setattr(module, name, original)


# ---------------------------------------------------------------------------
# Figure capture
# ---------------------------------------------------------------------------


@contextmanager
def capture_figures() -> Iterator[List[Any]]:
    """Capture every ``fig.show()`` call into a list instead of opening a tab.

    Yields a list that the chart's ``fig.show()`` calls will append to. After
    the chart returns, the list contains every plotly Figure in the order
    they were ``show``'d, ready to be passed to ``st.plotly_chart``.
    """
    from plotly.basedatatypes import BaseFigure  # type: ignore

    captured: List[Any] = []
    original = BaseFigure.show

    def _capture(self: Any, *args: Any, **kwargs: Any) -> None:
        captured.append(self)

    BaseFigure.show = _capture  # type: ignore[assignment]
    try:
        yield captured
    finally:
        BaseFigure.show = original  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Silent progress
# ---------------------------------------------------------------------------


class _NoopProgress:
    """Replacement for ``_partials.progress_bar()`` that is a silent no-op.

    The CLI uses ``rich.progress`` which writes ANSI escape codes to stdout.
    Streamlit captures stdout and renders it verbatim, producing noisy
    artefacts. Replace it with a context manager whose ``track()`` simply
    returns the iterable.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def __enter__(self) -> '_NoopProgress':
        return self

    def __exit__(self, *args: Any) -> bool:
        return False

    def track(self, iterable: Iterable[Any], *args: Any, **kwargs: Any) -> Iterable[Any]:
        return iterable

    def add_task(self, *args: Any, **kwargs: Any) -> int:
        return 0


@contextmanager
def silent_progress() -> Iterator[None]:
    """Replace ``progress_bar`` across qualichat with a no-op."""
    saved: dict = {}
    targets = ('progress_bar',)

    try:
        for module_name in _PROMPT_CONSUMERS:
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                continue
            for name in targets:
                if hasattr(module, name):
                    saved[(module_name, name)] = getattr(module, name)
                    setattr(module, name, _NoopProgress)
        yield
    finally:
        for (module_name, name), original in saved.items():
            module = importlib.import_module(module_name)
            setattr(module, name, original)


# ---------------------------------------------------------------------------
# High-level helper
# ---------------------------------------------------------------------------


def run_chart(
    chart_callable: Callable[..., Any],
    chats: Any,
    answers: Sequence[Any],
) -> List[Any]:
    """Run a CLI chart end-to-end, returning the list of captured figures.

    Parameters
    ----------
    chart_callable
        A bound chart method, e.g. ``qc.keys.charts['Laminations']``.
    chats
        The list of :class:`qualichat.chat.Chat` objects to feed the chart.
    answers
        Pre-recorded answers to every prompt the chart will issue, in order.

    Returns
    -------
    list
        The plotly figures the chart produced, in display order.
    """
    with capture_figures() as figures, silent_progress(), replay(answers):
        chart_callable(chats)
    return figures
