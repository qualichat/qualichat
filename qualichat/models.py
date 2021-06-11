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

import os
import re
import random
import datetime
from typing import Iterable
from types import MappingProxyType

import emojis

from .abc import BaseMessage
from .enums import _get_period, _get_sub_period


TIME_FORMAT = r'%d/%m/%y %H:%M:%S'

def parse_time(string: str) -> datetime.datetime:
    """Converts the date a message was sent to
    :class:`datetime.datetime`.

    Parameters
    ----------
    string: :class:`str`
        The date the message was sent.

    Returns
    -------
    :class:`datetime.datetime`
        A :class:`datetime.datetime` object of when the message was
        sent.
    """
    return datetime.datetime.strptime(string, TIME_FORMAT)


_path = os.path.dirname(__file__)
_books_path = os.path.join(_path, 'books.txt')

with open(_books_path) as f:
    __books__ = f.read().split('\n')


URL_REGEX = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
LAUGHS_REGEX = re.compile(r'\s((?:he|ha|hi|hu){2,}|(?:hh){1,}|(?:ja|je|ka|rs){2,}|(?:k){2,})', re.I)
EMAIL_REGEX = re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.I)
QUESTION_MARK_REGEX = re.compile(r'\?+')
EXCLAMATION_MARK_REGEX = re.compile(r'!+')
NUMBERS_REGEX = re.compile(r'\d+')


def _get_random_name() -> str:
    name = random.choice(__books__)
    # Remove the book from the list so there is no risk that two 
    # actors have the same display name.
    __books__.remove(name)
    return name.strip()


def _remove_all_incidences(text: str, iterables: Iterable[str]) -> str:
    for iterable in iterables:
        for incidence in iterable:
            text = text.replace(incidence, '')

    return text


class Actor:
    """Represents an actor in the actor.
    
    Attributes
    ----------
    display_name: :class:`str`
        A representative name for this actor, this name is not
        necessarily the actor's real name.
    messages: List[:class:`.Message`]
        A list containing all the messages that this user
        sent in the chat.
    """

    __slots__ = ('_contact_name', 'display_name', 'messages', 'data')

    def __init__(self, contact_name: str):
        self._contact_name = contact_name

        self.display_name = _get_random_name()
        self.messages = []

    def __repr__(self):
        return f'<Actor display_name={self.display_name!r} messages={len(self.messages)}>'


class Message(BaseMessage):
    """Represents a message sent in the chat by an actor.
    
    This class has a small linguistic analysis interface for message
    content. To get information about the data from this interface, you
    should use :meth:`object.__getitem__`, e. g. ::

        message['Qty_char_total']

    These are the data currently available:

    - ``Qty_char_total``: :class:`int`
        Shows the total number of characters in the message content.
        This is the same thing as doing: ::

            len(message.content)

    - ``Qty_char_emoji``: List[:class:`str`]
        All unicode emojis present in the message content.

    - ``Qty_char_links``: List[:class:`str`]
        All URLs present in the message content.

    - ``Qty_char_emails``: List[:class:`str`]
        All e-mails present in the message content.

    - ``Qty_char_?``: List[:class:`str`]
        All ``?`` character present in the message content.

    - ``Qty_char_!``: List[:class:`str`]
        All ``!`` character present in the message content.

    - ``Qty_char_numbers``: List[:class:`str`]
        All numbers characters present in the message content.

    - ``Qty_char_laughs``: List[:class:`str`]
        All laughs characters present in the message content.

        .. warning::

            This data may not be accurate as, computationally, laughs
            are difficult to detect as it does not follow an open
            pattern.

    - ``Qty_char_marks``: List[:class:`str`]
        The union of ``Qty_char_!`` and ``Qty_char_?``.

    - ``Qty_char_net``: :class:`str`
        Represents the net content of the message. This removes all
        URLs, emails and emojis from the message content.

    - ``Qty_char_text``: :class:`str`
        Represents the pure content of the message. This takes the net
        content (via ``Qty_char_net``) and removes laughs,
        marks and numbers from this content.

    - ``Day_period``: :class:`str`
        The period of day the message was sent. These are the available
        periods (in 24h format):

        - ``Dawn`` (00:00-05:59)
        - ``Morning`` (06:00-11:59)
        - ``Evening`` (12:00-17:59)
        - ``Night`` (18:00-23:59)

    - ``Day_sub_period``: :class:`str`
        The sub-period of the day the message was sent. These are the
        available periods (in 24-hour format):

        - ``Resting`` (00:00-05:59)
        - ``Transport (morning)`` (06:00-08:59)
        - ``Work (morning)`` (09:00-11:59)
        - ``Lunch`` (12:00-14:59)
        - ``Work (evening)`` (15:00-17:59)
        - ``Transport (evening)`` (18:00-20:59)
        - ``Second Office Hour`` (21:00-23:59)
    
    Attributes
    ----------
    content: :class:`str`
        The content of the message.
    created_at: :class:`datetime.datetime`
        The message's creation time.
    actor: :class:`.Actor`
        The actor who sent the message.
    data: Dict[:class:`str`, Any]
        Where is all the data from the linguistic analysis interface of
        the message. This dictionary is read-only and must not be
        changed.
    """
    
    __slots__ = ('actor', 'content', 'created_at', 'data')

    def __init__(self, actor: Actor, content: str, created_at: str):
        self.actor = actor
        self.content = content
        self.created_at = parse_time(created_at)

        data = {}
        data['Qty_char_total'] = len(self.content)
        data['Qty_char_emoji'] = list(emojis.iter(self.content))
        data['Qty_char_links'] = URL_REGEX.findall(self.content)
        data['Qty_char_emails'] = EMAIL_REGEX.findall(self.content)

        # We create a copy of the content (since we don't want to
        # change the original content) and then remove all URLs present
        # in the message, to avoid ambiguity.
        content = _remove_all_incidences(self.content, data['Qty_char_links'])

        data['Qty_char_?'] = QUESTION_MARK_REGEX.findall(content)
        data['Qty_char_!'] = EXCLAMATION_MARK_REGEX.findall(content)
        data['Qty_char_numbers'] = NUMBERS_REGEX.findall(content)
        data['Qty_char_laughs'] = LAUGHS_REGEX.findall(content)

        marks = data['Qty_char_!'] + data['Qty_char_?']
        data['Qty_char_marks'] = marks

        net_text_incidences = [
            'Qty_char_links',
            'Qty_char_emails',
            'Qty_char_emoji'
        ]

        net_iters = [data[i] for i in net_text_incidences]
        net_text = _remove_all_incidences(self.content, net_iters)

        pure_text_incidences = [
            'Qty_char_laughs',
            'Qty_char_marks',
            'Qty_char_numbers'
        ]

        pure_iters = [data[i] for i in pure_text_incidences]
        pure_text = _remove_all_incidences(net_text, pure_iters)

        data['Qty_char_net'] = net_text
        data['Qty_char_text'] = pure_text

        data['Day_period'] = _get_period(self.created_at).value
        data['Day_sub_period'] = _get_sub_period(self.created_at).value

        self.data = MappingProxyType(data)

    def __repr__(self):
        return '<Message actor={0.actor} created_at={0.created_at}>'.format(self)

    def __getitem__(self, key: str):
        if not isinstance(key, str):
            raise TypeError('indices must be strings')

        return self.data[key]


class SystemMessage(BaseMessage):
    """Represents a message sent in the chat by the system.
    
    Attributes
    ----------
    content: :class:`str`
        The content of the message.
    created_at: :class:`datetime.datetime`
        The message's creation time.
    """

    __slots__ = ('content', 'created_at')

    def __init__(self, content: str, created_at: str):
        self.content = content
        self.created_at = parse_time(created_at)

    def __repr__(self):
        return '<SystemMessage created_at={0.created_at}>'.format(self)
