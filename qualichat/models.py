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

import datetime
from typing import Any, Dict, Iterable, List
from types import MappingProxyType

import emojis # type: ignore

from .regex import *
from .abc import BaseMessage
from .enums import get_message_type, get_period, get_sub_period


__all__ = ('Actor', 'Message', 'SystemMessage')


TIME_FORMAT = r'%d/%m/%y %H:%M:%S'

def parse_time(string: str) -> datetime.datetime:
    """Converts the message creation time string to a
    :class:`datetime.datetime` object.
    
    Parameters
    ----------
    string: :class:`str`
        The message's creation time string.
    Returns
    -------
    :class:`datetime.datetime`
        A :class:`datetime.datetime` object of when the message was
        sent.
    """
    return datetime.datetime.strptime(string, TIME_FORMAT)


def remove_all_incidences(content: str, *iterables: Iterable[str]) -> str:
    for iterable in iterables:
        for incidence in iterable:
            content = content.replace(incidence, '')

    return content


class Actor:
    """Represents an actor in the chat.
    
    Attributes
    ----------
    display_name: :class:`str`
        A representative name for this actor, this name is not
        necessarily the actor's real name.
    messages: List[:class:`.Message`]
        A list containing all the messages that this actor sent in the
        chat.
    """

    __slots__ = ('display_name', 'messages')

    def __init__(self, display_name: str) -> None:
        self.display_name: str = display_name
        self.messages: List[Message] = []

    def __repr__(self) -> str:
        return f'<Actor display_name={self.display_name!r} ' \
               f'messages={len(self.messages)}>'


class Message(BaseMessage):
    """Represents a message sent in the chat by an actor.
    This class has a small linguistic analysis interface for message
    content. To get information about the data from this interface, you
    should use :meth:`object.__getitem__`, e.g. ::
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
        All ``?`` characters present in the message content.
    - ``Qty_char_!``: List[:class:`str`]
        All ``!`` characters present in the message content.
    - ``Qty_char_numbers``: List[:class:`str`]
        All numbers characters present in the message content.
    - ``Qty_char_laughs``: List[:class:`str`]
        All laughs characters present in the message content.
        .. warning::
            This data may not accurate as, computationally, laughs
            are difficult to detect as it does not follow an open
            pattern.
    - ``Qty_char_marks``: List[:class:`str`]
        The union of ``Qty_char_!`` and ``Qty_char_?``.
    - ``Qty_char_call``: List[:class:`str`]
        All calls found in the message content.
        .. versionadded:: 1.3
    - ``Qty_char_net``: :class:`str`
        Represents the net content of the message. This removes all
        calls, URLs, emails and emojis from the message content.
    - ``Qty_char_text``: :class:`str`
        Represents the pure content of the message. This takes the net
        content (via ``Qty_char_net``) and removes laughs, marks and
        numbers from this content.
    - ``Type``: :class:`.MessageType`
        Represents the type of message sent.
        For more information see :class:`.MessageType`.
    - ``Day_period``: :class:`.Period`
        The period of day the message was sent. These are the available
        periods (in 24h format):
        - ``Dawn`` (00:00-05:59)
        - ``Morning`` (06:00-11:59)
        - ``Evening`` (12:00-17:59)
        - ``Night`` (18:00-23:59)
        For more information see :class:`.Period`.
    - ``Day_sub_period``: :class:`.SubPeriod`
        The sub-period of the day the message was sent. These are the
        available periods (in 24-hour format):
        - ``Resting`` (00:00-05:59)
        - ``Transport (morning)`` (06:00-08:59)
        - ``Work (morning)`` (09:00-11:59)
        - ``Lunch`` (12:00-14:59)
        - ``Work (evening)`` (15:00-17:59)
        - ``Transport (evening)`` (18:00-20:59)
        - ``Second Office Hour`` (21:00-23:59)
        For more information see :class:`.SubPeriod`.
    Attributes
    ----------
    actor: :class:`.Actor`
        The actor who sent the message.
    content: :class:`str`
        The content of the message.
    created_at: :class:`datetime.datetime`
        The message's creation time.
    """

    __slots__ = ('actor', 'content', 'created_at', '_data')

    def __init__(self, actor: Actor, content: str, created_at: str) -> None:
        self.actor: Actor = actor
        self.content: str = content
        self.created_at: datetime.datetime = parse_time(created_at)

        data: Dict[str, Any] = {}
        data['Qty_char_total'] = len(self.content)

        all_emojis = list(emojis.iter(self.content)) # type: ignore
        data['Qty_char_emoji'] = all_emojis
        data['Qty_char_links'] = URL_RE.findall(self.content)
        data['Qty_char_emails'] = EMAIL_RE.findall(self.content)

        # We create a copy of the content (since we don't want to
        # change the original content) and then remove all URLs present
        # in the message, to avoid ambiguity.
        content = remove_all_incidences(self.content, *data['Qty_char_links'])

        data['Qty_char_?'] = QUESTION_MARK_RE.findall(content)
        data['Qty_char_!'] = EXCLAMATION_MARK_RE.findall(content)
        data['Qty_char_calls'] = MENTION_RE.findall(content)
        data['Qty_char_numbers'] = NUMBERS_RE.findall(content)
        data['Qty_char_laughs'] = LAUGHS_RE.findall(content)
        data['Qty_char_emoticons'] = EMOTICONS_RE.findall(content)

        all_marks: List[str] = data['Qty_char_emoji'] + data['Qty_char_emoticons']
        data['Qty_char_marks'] = all_marks

        net_incidences_fields = [
            'Qty_char_calls',
            'Qty_char_links',
            'Qty_char_emails',
            'Qty_char_emoji'
        ]

        net_incidendes = [data[i] for i in net_incidences_fields]
        net_text = remove_all_incidences(self.content, *net_incidendes)

        pure_incidences_fields = [
            'Qty_char_laughs',
            'Qty_char_marks',
            'Qty_char_numbers'
        ]

        pure_incidences = [data[i] for i in pure_incidences_fields]
        pure_text = remove_all_incidences(net_text, *pure_incidences)

        data['Qty_char_net'] = net_text
        data['Qty_char_text'] = pure_text

        data['Type'] = get_message_type(self.content)
        data['Day_period'] = get_period(self.created_at)
        data['Day_sub_period'] = get_sub_period(self.created_at)

        self._data: MappingProxyType[str, Any] = MappingProxyType(data)

    def __repr__(self) -> str:
        actor = f'actor={self.actor}'
        created_at = f'created_at={self.created_at!r}'

        return f'<Message {actor} {created_at}>'

    def __getitem__(self, key: Any) -> Any:
        if not isinstance(key, str):
            raise TypeError('indices must be strings')

        return self._data[key]


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

    def __init__(self, content: str, created_at: str) -> None:
        self.content: str = content
        self.created_at: datetime.datetime = parse_time(created_at)

    def __repr__(self) -> str:
        return f'<SystemMessage created_at={self.created_at!r}>'
