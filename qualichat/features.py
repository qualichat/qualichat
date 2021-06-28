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

from typing import List, DefaultDict, Callable, Protocol, Any, Optional
from collections import defaultdict

from pandas import DataFrame
import matplotlib.pyplot as plt

from .chat import Chat
from .models import Message
from .colors import BARS, LINES


__all__ = ('generate_chart', 'BaseFeature', 'MessagesFeature')


class FeatureMethodProtocol(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> None:
        ...


def generate_chart(
    *,
    bars: Optional[List[str]] = None,
    lines: Optional[List[str]] = None,
    title: Optional[str] = None
):
    """A decorator that generates a chart automatically.

    Parameters
    ----------
    bars: Optional[List[:class:`str`]]
        The list of columns that will be interpreted as bars. Defaults
        to ``None``.
    lines: Optional[List[:class:`str`]]
        The list of columns that will be interpreted as lines. Defaults
        to ``None``.
    title: Optional[:class:`str`]
        The title of the chart. Defaults to ``None``.
    """    
    if bars is None:
        bars = []

    if lines is None:
        lines = []

    def decorator(
        method: Callable[[FeatureMethodProtocol], DataFrame]
    ) -> Callable[[FeatureMethodProtocol], None]:
        def generator(
            self: FeatureMethodProtocol,
            *args: Any,
            **kwargs: Any
        ) -> None:
            # TODO: Add debug logging message here.

            _, ax = plt.subplots()
            dataframe = method(self, *args, **kwargs)

            ax.set_title(title)

            if bars:
                color = BARS[len(bars)]

                bars_dataframe = dataframe.filter(bars) # type: ignore
                bars_dataframe.plot.bar( # type: ignore
                    ax=ax, rot=15, color=color
                )

            if lines:
                color = LINES[len(bars)] if bars is not None else ['#ff645c']

                lines_dataframe = dataframe.filter( # type: ignore
                    lines
                )
                lines_dataframe.plot( # type: ignore
                    ax=ax, rot=15, secondary_y=True, color=color
                )

            ax.grid(axis='y', linestyle='solid') # type: ignore
            plt.show()

        # Dummy implementation for the decorated function to inherit
        # the documentation.
        generator.__doc__ = method.__doc__
        generator.__annotations__ = method.__annotations__

        return generator

    return decorator


def get_length(obj: List[str]) -> int:
    return len(''.join(obj))


class BaseFeature:
    """Represents the base of a Qualichat feature.
    Generally, you should use the built-in features that Qualichat
    offers you. However, you can subclass this class and create your
    own features.

    .. note::

        To automatically generate charts, you must create a method
        decorated with :meth:`generate_chart` that returns a
        :class:`pandas.DataFrame`.

    Attributes
    ----------
    chats: List[:class:`.Chat`]
        All the chats loaded via :meth:`qualichat.load_chats`.
    """

    __slots__ = ('chats',)

    def __init__(self, chats: List[Chat]) -> None:
        self.chats = chats


class MessagesFeature(BaseFeature):
    """A feature that adds graphics generator related to chat messages.
    
    .. note::

        This feature is already automatically added to Qualichat.

    Attributes
    ----------
    chats: List[:class:`.Chat`]
        All the chats loaded via :meth:`qualichat.load_chats`.
    """

    @generate_chart(
        bars=['Qty_char_net', 'Qty_char_text'],
        lines=['Qty_messages'],
        title='Amount by Month'
    )
    def per_month(self) -> DataFrame:
        """Shows how many messages were sent per month."""
        chat = self.chats[0]
        data: DefaultDict[str, List[Message]] = defaultdict(list)

        columns = ['Qty_char_net', 'Qty_char_text', 'Qty_messages']
        rows: List[List[int]] = []

        for message in chat.messages:
            index = message.created_at.replace(
                day=1, hour=0, minute=0, second=0
            )
            data[index.strftime('%B %Y')].append(message)

        index = list(data.keys())

        for messages in data.values():
            net_content = 0
            pure_content = 0
            total_messages = 0

            for message in messages:
                net_content += len(message['Qty_char_net'])
                pure_content += len(message['Qty_char_text'])
                total_messages += 1

            rows.append([net_content, pure_content, total_messages])

        return DataFrame(rows, index=index, columns=columns)

    @generate_chart(
        bars=['Qty_messages'],
        lines=['Qty_char_net'],
        title='Amount by Weekday'
    )
    def per_weekday(self) -> DataFrame:
        """Shows how many messages were sent per weekday."""
        chat = self.chats[0]
        data: DefaultDict[str, List[Message]] = defaultdict(list)

        columns = ['Qty_messages', 'Qty_char_net']
        rows: List[List[int]] = []

        for message in chat.messages:
            index = message.created_at.replace(hour=0, minute=0, second=0)
            data[index.strftime('%A')].append(message)

        index = list(data.keys())

        for messages in data.values():
            total_messages = 0
            net_content = 0

            for message in messages:
                total_messages += 1
                net_content += len(message['Qty_char_net'])

            rows.append([total_messages, net_content])

        return DataFrame(rows, index=index, columns=columns)

    @generate_chart(
        bars=[
            'Qty_char_laughs', 'Qty_char_marks',
            'Qty_char_emoji', 'Qty_char_numbers'
        ],
        lines=['Qty_messages'],
        title='Amount by Month'
    )
    def by_aspects(self) -> DataFrame:
        """Shows what are the most common aspects in messages by month.

        Aspects can be interpreted as:

        - Laughs
        - Marks
        - Emojis
        - Numbers
        
        And it will be compared with the total messages sent per month.
        """
        chat = self.chats[0]
        data: DefaultDict[str, List[Message]] = defaultdict(list)

        columns = [
            'Qty_char_laughs', 'Qty_char_marks',
            'Qty_char_emoji', 'Qty_char_numbers',
            'Qty_messages'
        ]
        rows: List[List[int]] = []

        for message in chat.messages:
            index = message.created_at.replace(
                day=1, hour=0, minute=0, second=0
            )
            data[index.strftime('%B %Y')].append(message)

        index = list(data.keys())

        for messages in data.values():
            laughs = 0
            marks = 0
            emojis = 0
            numbers = 0
            total_messages = 0

            for message in messages:
                laughs += get_length(message['Qty_char_laughs'])
                marks += get_length(message['Qty_char_marks'])
                emojis += get_length(message['Qty_char_emoji'])
                numbers += get_length(message['Qty_char_numbers'])
                total_messages += 1

            rows.append([laughs, marks, emojis, numbers, total_messages])

        return DataFrame(rows, index=index, columns=columns)
