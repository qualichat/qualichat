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

from typing import Union, List, Callable, DefaultDict
from collections import defaultdict
from pathlib import Path

import matplotlib
from pandas import DataFrame
from matplotlib import pyplot as plot
from matplotlib import font_manager

from .chat import Qualichat
from .models import Message
from .enums import Period, SubPeriod
from .utils import log


# Add ``Inter`` font.
fonts = Path(__file__).parent / 'fonts'

for font in font_manager.findSystemFonts(str(fonts)):
    font_manager.fontManager.addfont(font)

matplotlib.rcParams['font.family'] = 'Inter'


# Colors
BARS_COLORS = {
    2: ['#08bcac', '#38444c'],
    4: ['#f2c80f', '#fd625e', '#8ad4eb', '#b887ad'],
    7: ['#796408', '#374649', '#808080', '#a66999', '#fe9666', '#fae99f', '#f5d33f']
}

LINE_COLORS = {
    0: '#ff645c',
    2: '#ff645c',
    4: '#000000',
    7: '#01b8aa'
}


WEEKDAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
PERIODS = [c.value for c in Period]
SUB_PERIODS = [c.value for c in SubPeriod]


def generate_graph(
        *,
        bars: List[str] = [],
        lines: List[str] = [],
        title: str = None
):
    def decorator(method: Callable[[], DataFrame]):
        def wrapped(*args, **kwargs):
            log('info', f"Generating a '{method.__name__}' graph...")

            fig, ax = plot.subplots()
            dataframe = method(*args, **kwargs)

            ax.set_title(title)

            if bars:
                color = BARS_COLORS[len(bars)]

                bars_dataframe = dataframe.filter(bars)
                bars_dataframe.plot.bar(ax=ax, rot=0, color=color)

            if lines:
                color = LINE_COLORS[len(bars)]

                lines_dataframe = dataframe.filter(lines)
                lines_dataframe.plot(ax=ax, secondary_y=True, rot=15, color=color)

            ax.grid(axis='y', linestyle='solid')
            plot.show()

        return wrapped
    return decorator


class GraphGenerator:
    """This class provides the ability to generate graphs.
    
    Attributes
    ----------
    chats: List[:class:`.Qualichat`]
        The list of chats to be analyzed.
    """

    __slots__ = ('chats',)
    
    def __init__(self, chats: Union[Qualichat, List[Qualichat]]):
        if isinstance(chats, Qualichat):
            chats = [chats]

        self.chats = chats

        term = 'graph' + ('' if len(chats) == 1 else 's')
        log('info', f'Created a graph generator for {len(chats)} {term}.')

    @generate_graph(
        bars=['Qty_char_net', 'Qty_char_text'],
        lines=['Qty_messages'],
        title='Amount by Month'
    )
    def messages_per_month(self):
        """Shows the number of messages per month. Shows the number of
        liquid characters and the number of text characters.
        """
        chat = self.chats[0]
        data: DefaultDict[str, List[Message]] = defaultdict(list)

        columns = ['Qty_char_net', 'Qty_char_text', 'Qty_messages']
        rows = []

        for message in chat.messages:
            index = message.created_at.replace(day=1, hour=0, minute=0, second=0)
            data[index.strftime('%B %Y')].append(message)

        for values in data.values():
            net_content = 0
            pure_content = 0
            messages = 0

            for message in values:
                net_content += len(message['Qty_char_net'])
                pure_content += len(message['Qty_char_text'])
                messages += 1

            rows.append([net_content, pure_content, messages])

        return DataFrame(rows, index=data.keys(), columns=columns)

    @generate_graph(
        bars=[
            'Qty_char_laughs', 'Qty_char_marks',
            'Qty_char_emoji', 'Qty_char_numbers'
        ],
        lines=['Qty_messages'],
        title='Amount by Month'
    )
    def message_aspects(self):
        """Shows the messages aspects per month. Shows the number of
        laughs, marks, emojis and numbers characters sent per month.
        """
        chat = self.chats[0]
        data: DefaultDict[str, List[Message]] = defaultdict(list)

        columns = [
            'Qty_char_laughs', 'Qty_char_marks',
            'Qty_char_emoji', 'Qty_char_numbers',
            'Qty_messages'
        ]
        rows = []

        get_length = lambda x: len(''.join(x))

        for message in chat.messages:
            index = message.created_at.replace(day=1, hour=0, minute=0, second=0)
            data[index.strftime('%B %Y')].append(message)

        for values in data.values():
            laughs = 0
            marks = 0
            emojis = 0
            numbers = 0
            messages = 0

            for message in values:
                laughs += get_length(message['Qty_char_laughs'])
                marks += get_length(message['Qty_char_marks'])
                emojis += get_length(message['Qty_char_emoji'])
                numbers += get_length(message['Qty_char_numbers'])
                messages += 1
                
            rows.append([laughs, marks, emojis, numbers, messages])

        return DataFrame(rows, index=data.keys(), columns=columns)

    @generate_graph(
        bars=WEEKDAYS,
        lines=['Qty_char_net'],
        title='Amount by Month'
    )
    def weekdays(self):
        """Shows which days of the week have the most active chat."""
        chat = self.chats[0]
        data: DefaultDict[str, List[Message]] = defaultdict(list)

        columns = WEEKDAYS.copy()
        columns.append('Qty_char_net')
        rows = []

        for message in chat.messages:
            index = message.created_at.replace(day=1, hour=0, minute=0, second=0)
            data[index.strftime('%B %Y')].append(message)

        for values in data.values():
            net_content = 0
            weekdays = {w: 0 for w in WEEKDAYS}

            for message in values:
                net_content += len(message['Qty_char_net'])
                weekdays[message.created_at.strftime('%A')] += 1

            rows.append([*weekdays.values(), net_content])

        return DataFrame(rows, index=data.keys(), columns=columns)

    @generate_graph(
        bars=['Qty_char_net', 'Qty_char_text'],
        lines=['Qty_messages'],
        title='Amount by User'
    )
    def users_activity(self):
        """Shows the number of messages per user.
        It only shows the 10 most active actors.
        """
        chat = self.chats[0]
        data = {}

        columns = ['Qty_char_net', 'Qty_char_text', 'Qty_messages']
        indexes = [actor.display_name for actor in chat.actors]
        
        rows = []

        for actor in chat.actors:
            net_content = 0
            pure_content = 0

            for message in actor.messages:
                net_content += len(message['Qty_char_net'])
                pure_content += len(message['Qty_char_text'])

            rows.append([net_content, pure_content, len(actor.messages)])

        dataframe = DataFrame(rows, index=indexes, columns=columns)
        return dataframe[:10].sort_values(columns, ascending=False)

    @generate_graph(
        bars=[
            'Qty_char_laughs', 'Qty_char_marks',
            'Qty_char_emoji', 'Qty_char_numbers'
        ],
        lines=['Qty_messages'],
        title='Amount by User'
    )
    def users_messages_aspects(self):
        """Shows message aspects by user.
        It only shows the 10 most active actors.
        """
        chat = self.chats[0]
        data = {}

        columns = [
            'Qty_char_laughs', 'Qty_char_marks',
            'Qty_char_emoji', 'Qty_char_numbers',
            'Qty_messages'
        ]
        indexes = [actor.display_name for actor in chat.actors]

        rows = []

        for actor in chat.actors:
            laughs = 0
            marks = 0
            emojis = 0
            numbers = 0

            for message in actor.messages:
                laughs += len(''.join(message['Qty_char_laughs']))
                marks += len(''.join(message['Qty_char_marks']))
                emojis += len(''.join(message['Qty_char_emoji']))
                numbers += len(''.join(message['Qty_char_numbers']))

            rows.append([laughs, marks, emojis, numbers, len(actor.messages)])

        dataframe = DataFrame(rows, index=indexes, columns=columns)
        return dataframe[:10].sort_values(columns, ascending=False)

    @generate_graph(
        bars=PERIODS,
        lines=['Qty_messages'],
        title='Amount by Month'
    )
    def message_period(self):
        """Shows which periods of the day the chat is most active."""
        chat = self.chats[0]
        data = defaultdict(list)

        columns = PERIODS.copy()
        columns.append('Qty_messages')
        rows = []

        for message in chat.messages:
            index = message.created_at.replace(day=1, hour=0, minute=0, second=0)
            data[index.strftime('%B %Y')].append(message)

        for values in data.values():
            messages = 0
            periods = {c.value: 0 for c in Period}

            for message in values:
                messages += 1
                periods[message['Day_period']] += 1

            rows.append([*periods.values(), messages])

        return DataFrame(rows, index=data.keys(), columns=columns)

    @generate_graph(
        bars=SUB_PERIODS,
        lines=['Qty_messages'],
        title='Amount by Month'
    )
    def message_sub_period(self):
        """Shows which sun-periods of the day the chat is most active."""
        chat = self.chats[0]
        data = defaultdict(list)

        columns = SUB_PERIODS.copy()
        columns.append('Qty_messages')
        rows = []

        for message in chat.messages:
            index = message.created_at.replace(day=1, hour=0, minute=0, second=0)
            data[index.strftime('%B %Y')].append(message)

        for values in data.values():
            messages = 0
            periods = {c.value: 0 for c in SubPeriod}

            for message in values:
                messages += 1
                periods[message['Day_sub_period']] += 1

            rows.append([*periods.values(), messages])

        return DataFrame(rows, index=data.keys(), columns=columns)
