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
import json
import os
import random
from typing import List, Union, Dict, Any

from .utils import log
from .regex import CHAT_RE, USER_MESSAGE_RE
from .models import Actor, Message, SystemMessage


__all__ = ('Chat',)


def _clean_impurities(text: str) -> str:
    # Regex will not be used here since 
    # :meth:`str.replace` is faster and simpler.
    text = text.replace('\u200e', '')
    text = text.replace('\u2002', '')
    text = text.replace('\u202c', '')
    text = text.replace('\u202a', '')

    text = text.replace('\xa0', ' ')
    text = text.replace('\u2011', '-')

    return text


def _get_config_file() -> Dict[Any, Any]:
    home = pathlib.Path.home()

    folder = home / '.qualichat'
    config = folder / 'config.json'

    if not folder.is_dir():
        log('debug', 'Creating <color>.qualichat<reset> folder.')
        folder.mkdir(exist_ok=True)

        with config.open('w', encoding='utf-8') as f:
            f.write(r'{}')

    with config.open('r', encoding='utf-8') as f:
        return json.load(f)

_config = _get_config_file()

def _save_config_file():
    home = pathlib.Path.home()
    config_file = home / '.qualichat' / 'config.json'

    with config_file.open('w', encoding='utf-8') as f:
        json.dump(_config, f, indent=2, sort_keys=True)


def _get_books_names() -> List[str]:
    path = os.path.dirname(__file__)
    books_path = os.path.join(path, 'books.txt')

    with open(books_path, encoding='utf-8') as f:
        return f.read().split('\n')

_books = _get_books_names()


def _get_name() -> str:
    name = random.choice(_books)
    # Remove the book from the list so there is no risk that two 
    # actors have the same display name.
    _books.remove(name)
    return name.strip()


# TODO: Update docs.
class Chat:
    """Represents an isolated chat.
    
    Attributes
    ----------
    filename: :class:`str`
        The filename of the given chat file.
    messages: List[:class:`.Message`]
        All the actor messages found by Qualichat.
    system_messages: List[:class:`.SystemMessage`]
        All the system messages found by Qualichat.
    """

    __slots__ = ('filename', 'path', 'messages', 'system_messages', '_actors')

    def __init__(self, path: Union[str, pathlib.Path], **kwargs: str) -> None:
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        if not path.is_file():
            raise FileNotFoundError(f'no such file: {str(path)!r}')

        name = f'<color>{str(path)}<reset>'
        log('info', f'Loading chat {name}.')

        log('debug', f'Reading {name} file content.')
        encoding = kwargs.pop('encoding', 'utf-8')
        text = path.read_text(encoding=encoding)

        log('debug', f'File {name} read. Cleaning it.')
        raw_data = _clean_impurities(text)

        self.filename: str = path.name
        self.path: str = str(path.resolve())
        self.messages: List[Message] = []
        self.system_messages: List[SystemMessage] = []

        self._actors: Dict[str, Actor] = {}

        log('debug', f'Contents of file {name} cleaned. Parsing it.')
        for match in CHAT_RE.finditer(raw_data):
            if not match:
                # An unknown message?
                # Anyway, let's just ignore it and move on.
                continue

            created_at = match.group(1)
            rest = match.group(2)

            is_user_message = USER_MESSAGE_RE.match(rest)

            if is_user_message:
                contact_name = is_user_message.group(1)
                content = is_user_message.group(2)

                if contact_name not in self._actors:
                    if self.path not in _config:
                        _config[self.path] = {}

                    group_names = _config[self.path]

                    if contact_name not in group_names:
                        group_names[contact_name] = _get_name()

                    display_name = group_names[contact_name]
                    actor = Actor(contact_name, display_name)

                    self._actors[contact_name] = actor

                actor = self._actors[contact_name]
                message = Message(actor, content, created_at)

                self.messages.append(message)
                actor.messages.append(message)
            else:
                # It is a system message, indicating some group 
                # event (actor left/joined, changed the group icon,
                # etc.)
                message = SystemMessage(rest, created_at)
                self.system_messages.append(message)

        _save_config_file()

        messages = len(self.messages) + len(self.system_messages)
        actors = len(self.actors)

        log('info', f'Loaded {messages:,} messages and {actors:,} actors ' \
                    f'from {name} file.')

    @property
    def actors(self) -> List[Actor]:
        """List[:class:`.Actor`]: The list of actors present in the
        chat.
        """
        return list(self._actors.values())
