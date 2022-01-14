"""
Qualichat
~~~~~~~~~

Open-source linguistic ethnography tool for
framing public opinion in mediatized groups.

:copyright: (c) 2021-present Ernest Manheim
:license: MIT, see LICENSE for more details.
"""

__title__ = 'qualichat'
__author__ = 'Ernest Manheim'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021-present Ernest Manheim'
__version__ = '1.3.7'


__all__ = ()


from typing import NamedTuple
from functools import partial

from rich.progress import (
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    Progress,
)


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: str
    serial: int

version_info = VersionInfo(1, 3, 7, 'stable', 0)

# Custom progress bar
spinner = SpinnerColumn()
description = TextColumn("[progress.description]{task.description}")
bar = BarColumn()
percentage = TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
remaining = TimeRemainingColumn()
elapsed = TimeElapsedColumn()

progress = partial(
    Progress,
    spinner,
    description,
    bar,
    percentage,
    remaining,
    elapsed,
    transient=True
)
