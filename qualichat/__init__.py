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
__version__ = '1.3.8'


__all__ = ('load_chats',)


from typing import NamedTuple

from .core import load_chats as load_chats


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: str
    serial: int

version_info = VersionInfo(1, 3, 8, 'stable', 0)
