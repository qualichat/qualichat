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
from typing import Tuple, Union, Any, List
from pathlib import Path

from .chat import Chat

from .frames import BaseFrame, KeysFrame


__all__ = (
    'Qualichat',
    'load_chats',
)


class Qualichat:
    """Represents a set of chats for linguistic analysis.
    
    Attributes
    ----------
    chats: List[:class:`.Chat`]
        All chats uploaded and parsed by Qualichat.
    keys: :class:`.KeysFrame`
        The Qualichat's keys frame.
    """

    __slots__: Tuple[str, ...] = ('chats', 'keys')

    def __init__(self, chats: List[Chat], api_key: str) -> None:
        self.chats = chats

        self.keys = KeysFrame(chats, api_key)

    def __repr__(self) -> str:
        return f'<Qualichat chats={self.chats}>'

    @property
    def frames(self) -> List[BaseFrame]:
        return [getattr(self, name) for name in self.__slots__[1:]]


def load_chats(
    *paths: Union[str, Path],
    debug: bool = False,
    **kwargs: Any
) -> Qualichat:
    """Loads the given chats from a plain text files.

    Parameters
    ----------
    *paths: Union[:class:`str`, :class:`pathlib.Path`]
        The paths to the chat files.
    debug: :class:`bool`
        Sets the logging level to debug.
    **kwargs: Any
        Keyword arguments that will be passed to :class:`.Chat`.

    Returns
    -------
    :class:`.Qualichat`
        The object that will be used for analysis of the chat.

    Raises
    ------
    :class:`FileNotFoundError`
        If one of the chat files could not been found.
    """
    level = logging.DEBUG if debug else logging.INFO

    logger = logging.getLogger('qualichat')
    logger.setLevel(level)

    api_key: str = kwargs.pop('api_key', None)

    return Qualichat([Chat(path, **kwargs) for path in paths], api_key)
