"""
MIT License
Copyright (c) 2021 Qualichat
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Union

from .chat import Chat
from .frames import BaseFrame, KeysFrame, ParticipationStatusFrame


__all__ = ('Qualichat', 'load_chats')



class Qualichat:
    """
    """

    __slots__: Tuple[str, ...] = ('chats', 'keys', 'participation_status')

    def __init__(self, chats: List[Chat]) -> None:
        self.chats = chats

        # Frames
        self.keys = KeysFrame(chats)
        self.participation_status = ParticipationStatusFrame(chats)

    def __repr__(self) -> str:
        return f'<Qualichat chats={self.chats}>'

    @property
    def frames(self) -> Dict[str, BaseFrame]:
        frames: Dict[str, BaseFrame] = {}

        for name in self.__slots__[1:]:
            o = getattr(self, name)
            name = o.fancy_name
            frames[name] = o

        return frames


def load_chats(*paths: Union[str, Path], debug: bool) -> Qualichat:
    """
    """
    level = logging.DEBUG if debug else logging.INFO

    logger = logging.getLogger('qualichat')
    logger.setLevel(level)

    chats = [Chat(path) for path in paths]
    return Qualichat(chats)
