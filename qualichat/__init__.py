'''
Qualichat
~~~~~~~~~

Open-source linguistic ethnography tool for
framing public opinion in mediatized groups.

:copyright: (c) 2021-present Ernest Manhein
:license: MIT, see LICENSE for more details.
'''

__title__ = 'qualichat'
__author__ = 'Ernest Manhein'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021-present Ernest Manhein'
__version__ = '0.1.0a'

from collections import namedtuple

from .core import load_chat


VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')
version_info = VersionInfo(major=0, minor=1, micro=0, releaselevel='alpha', serial=0)
