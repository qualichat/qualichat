'''
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
'''

import pathlib
import logging
from typing import Union, List, Any

from .chat import Chat
from .frames import (
    MessagesFrame,
    ActorsFrame,
    TimeFrame,
    NounsFrame,
    VerbsFrame,
    EmojisFrame
)


__all__ = ('Qualichat', 'load_chats')


class Qualichat:
    """Represents a set of chats for linguistic analysis.
    
    Attributes
    ----------
    chats: List[:class:`.Chat`]
        All chats uploaded and parsed by Qualichat.
    messages: :class:`.MessagesFrame`
        A frame that adds graphics generator related to chat
        messages.
    """

    __slots__ = (
        'chats', 'messages', 'actors',
        'time', 'nouns', 'verbs',
        'emojis'
    )

    def __init__(self, chats: List[Chat]) -> None:
        self.chats = chats

        # Qualichat frames
        self.messages = MessagesFrame(chats)
        self.actors = ActorsFrame(chats)
        self.time = TimeFrame(chats)
        self.nouns = NounsFrame(chats)
        self.verbs = VerbsFrame(chats)
        self.emojis = EmojisFrame(chats)


def load_chats( # type: ignore
    *paths: Union[str, pathlib.Path],
    **kwargs: Any
) -> Qualichat:
    """Loads the given chats from a plain text files.

    Parameters
    ----------
    *paths: Union[:class:`str`, :class:`pathlib.Path`]
        The paths to the chat files.
        The files must be in plain text format.
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
    debug = kwargs.pop('debug', False)
    mode = logging.DEBUG if debug is True else logging.INFO

    logger = logging.getLogger('qualichat')
    logger.setLevel(mode)

    return Qualichat([Chat(path, **kwargs) for path in paths])
