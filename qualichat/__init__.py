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
__version__ = '1.1.0'


from collections import namedtuple

from .core import load_chat
from .graphs import GraphGenerator


VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')
version_info = VersionInfo(major=1, minor=1, micro=0, releaselevel='stable', serial=0)
