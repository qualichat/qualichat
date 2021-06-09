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
import re
from typing import Union, List

from .models import Message, SystemMessage, Actor


CHAT_REGEX = re.compile(r'''
    ^\[(?P<datetime>\d{2}/\d{2}/\d{2}\s\d{2}:\d{2}:\d{2})\]\s
    (?P<rest>[\S\s]+?)(?=\n\[.+\]|\Z)
''', re.M | re.X)
COMMON_MESSAGE_REGEX = re.compile(r'(?P<actor>.*?):\s+(?P<message>[\s\S]+)')


def _clean_impurities(chat: str) -> str:
    # Regex will not be used since ``str.replace`` is faster and
    # simpler.

    # Cleaning empty characters.
    chat = chat.replace('\u200e', '')
    chat = chat.replace('\u202a', '')
    chat = chat.replace('\u202c', '')
    # Cleaning false space characters.
    chat = chat.replace('\xa0', ' ')
    # Cleaning false hyphen.
    chat = chat.replace('\u2011', '-')

    return chat


class Qualichat:
    """Base class for chat analysis."""

    __slots__ = ('filename', 'messages', 'system_messages',
                 '_actors', 'graphs')

    def __init__(self, path: Union[str, pathlib.Path], **kwargs):
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        if not path.is_file():
            raise FileNotFoundError(f'no such file: {str(path)!r}')

        encoding = kwargs.pop('encoding', 'utf-8')
        raw_data = _clean_impurities(path.read_text(encoding=encoding))

        self.filename = path.name

        self.messages = []
        self.system_messages = []

        self._actors = {}

        for match in CHAT_REGEX.finditer(raw_data):
            if not match:
                # An unknown message?
                # Anyway, let's just ignore it and move on.
                continue

            created_at = match.group(1)
            rest = match.group(2)

            is_common = COMMON_MESSAGE_REGEX.match(rest)

            if is_common:
                contact_name = is_common.group(1)
                content = is_common.group(2)

                if contact_name not in self._actors:
                    self._actors[contact_name] = Actor(contact_name)

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

    @property
    def actors(self) -> List[Actor]:
        """List[:class:`.Actor`]: The list of actors present in the
        chat.
        """
        return list(self._actors.values())
