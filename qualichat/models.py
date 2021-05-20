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

import datetime
import os
import random


time_format = r'%d/%m/%y %H:%M:%S'

def _parse_time(string: str) -> datetime.datetime:
    return datetime.datetime.strptime(string, time_format)


_path = os.path.dirname(__file__)
_books_path = os.path.join(_path, 'books.txt')

with open(_books_path) as f:
    __books__ = f.read().split('\n')


def _get_random_name() -> str:
    name = random.choice(__books__)
    __books__.remove(name)
    return name.strip()


class Actor:
    '''Represents an actor in the chat.

    Attributes
    -----------
    display_name: :class:`str`
        A representative name for this actor, this name is 
        not necessarily the user's real name.
    messages: list[:class:`Message`]
        A list containing all the messages that this user sent 
        in the chat.
    '''

    def __init__(self, contact_name: str):
        self.__contact_name__ = contact_name
        self.messages = []
        self.display_name = _get_random_name()

    def __repr__(self):
        return f'<Actor display_name={self.display_name!r} messages={len(self.messages)}>'


class Message:
    '''Represents a message sent in the chat.

    Attributes
    -----------
    actor: :class:`Actor`
        The actor who sent the message.
    content: :class:`str`
        The content of the message.
    created_at: :class:`datetime.datetime`
        The message's creation time.
    '''

    def __init__(self, *, actor: Actor, content: str, created_at: str):
        self.actor = actor
        self.content = content
        self.created_at = _parse_time(created_at)

    def __repr__(self):
        return '<Message actor={0.actor} created_at={0.created_at}>'.format(self)
