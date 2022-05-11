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
__version__ = '1.4.2'


from typing import NamedTuple


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: str
    serial: int

version_info = VersionInfo(1, 4, 2, 'stable', 0)
