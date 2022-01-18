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

from pathlib import Path
from typing import Any, Dict, List, Union

from .utils import log, config, get_random_name
from .models import Actor, Message, SystemMessage
from .regex import CHAT_FORMAT_RE, USER_MESSAGE_RE


__all__ = ('Chat',)


def _clean_impurities(content: str) -> str:
    # Regex will not be used here since
    # :meth:`str.replace` is faster and simpler.
    content = content.replace('\u200e', '')
    content = content.replace('\u2002', '')
    content = content.replace('\u202c', '')
    content = content.replace('\u202a', '')

    content = content.replace('\xa0', ' ')
    content = content.replace('\u2011', '-')

    return content


class Chat:
    """
    """

    __slots__ = ('path', 'filename', 'messages', 'system_messages', '_actors')

    def __init__(self, path: Union[str, Path], **kwargs: Any) -> None:
        if not isinstance(path, Path):
            path = Path(path)

        if not path.is_file():
            raise FileNotFoundError(f'no such file: {str(path)!r}')

        self.path = path.resolve()
        self.filename = self.path.name

        name = f'[green]{str(path)}[/]'
        log('info', f'Loading chat {name}...')

        log('debug', f'Reading {name} file content...')
        encoding = kwargs.pop('encoding', 'utf-8')
        content = path.read_text(encoding=encoding)

        log('debug', f'File {name} read. Cleaning it...')
        raw_data = _clean_impurities(content)

        log('debug', f'Contents of the file {name} cleaned. Parsing it...')
        self.messages: List[Message] = []
        self.system_messages: List[SystemMessage] = []

        self._actors: Dict[str, Actor] = {}

        for match in CHAT_FORMAT_RE.finditer(raw_data):
            if not match:
                # An unknown message? Anyway, 
                # let's just ignore it and move on.
                continue

            created_at = match.group(1)
            rest = match.group(2)

            is_user_message = USER_MESSAGE_RE.match(rest)

            if is_user_message:
                contact_name = is_user_message.group(1)
                content = is_user_message.group(2)

                if contact_name not in self._actors:
                    path = str(self.path)

                    if path not in config:
                        config[path] = {}

                    group: Dict[str, str] = config[path]

                    if contact_name not in group:
                        group[contact_name] = get_random_name()

                    display_name = group[contact_name]
                    self._actors[contact_name] = Actor(display_name)

                actor = self._actors[contact_name]                
                message = Message(actor, content, created_at)

                self.messages.append(message)
                actor.messages.append(message)
            else:
                # It is a system message, indicating some group 
                # event (actor left/joined, changed the group icon,
                # etc.)
                self.system_messages.append(SystemMessage(rest, created_at))

        config.save()

        messages = len(self.messages) + len(self.system_messages)
        actors = len(self.actors)

        msg = f'Loaded {messages:,} messages and {actors:,} actors from {name}.'
        log('info', msg)

    @property
    def actors(self) -> List[Actor]:
        """List[:class:`.Actor`]: The list of actors present in the
        chat.
        """
        return list(self._actors.values())

    def __repr__(self) -> str:
        filename = f'filename={self.filename!r}'
        actors = f'actors={len(self._actors)}'
        messages = f'messages={len(self.messages)}'
        system_messages = f'system_messages={len(self.system_messages)}'

        return f'<Chat {filename} {actors} {messages} {system_messages}>'

