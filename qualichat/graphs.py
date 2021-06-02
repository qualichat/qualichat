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
from typing import Union, List
from pathlib import Path
from collections import defaultdict
from itertools import cycle, islice

import matplotlib
from matplotlib import pyplot as plot
from matplotlib import font_manager
from pandas import DataFrame

from .chat import Qualichat
from .enums import Period, SubPeriod


# Add ``Inter`` font.
fonts = Path(__file__).parent / 'fonts'

for font in font_manager.findSystemFonts(str(fonts)):
    font_manager.fontManager.addfont(font)

matplotlib.rcParams['font.family'] = 'Inter'


DEFAULT_COLORS     = ['#08bcac', '#38444c']
SECONDARY_COLORS   = ['#f2c80f', '#fd625e', '#8ad4eb', '#b887ad']
TERTIARY_COLORS    = ['#796408', '#374649', '#808080', '#a66999', '#fe9666', '#fae99f', '#f5d33f']
DEFAULT_LINE_COLOR = '#ff645c'


class GraphGenerator:
    '''This class provides the ability to generate graphs.
    
    Attributes
    ----------
    chats: List[:class:`.Qualichat`]
        The list of chats to be analyzed.
    '''
    __slots__ = ('chats',)

    def __init__(self, chats: Union[Qualichat, List[Qualichat]]):
        if isinstance(chats, Qualichat):
            chats = [chats]

        self.chats = chats

    def by_messages_per_month(self):
        '''Shows the number of messages per month. Shows the number of liquid characters
        and the number of text characters.
        '''
        fig, ax = plot.subplots()
        ax.set_title('Amount by Month')

        chat = self.chats[0]
        data = defaultdict(list)

        columns = ['QTD_Liquido', 'QTD_Texto', 'QTD_Mensagens']
        rows = []

        for message in chat.messages:
            index = message.created_at.replace(day=1, hour=0, minute=0, second=0)
            strftime = index.strftime('%B %Y')
            data[strftime].append(message)

        for values in data.values():
            liquid = 0
            text = 0
            messages = 0

            for message in values:
                liquid += len(message.liquid)
                text += len(message.pure_text)
                messages += 1

            rows.append([liquid, text, messages])

        dataframe = DataFrame(rows, index=data.keys(), columns=columns)

        bars = dataframe.drop(columns='QTD_Mensagens')
        ax2 = bars.plot.bar(ax=ax, rot=0, color=DEFAULT_COLORS)

        messages = dataframe['QTD_Mensagens']
        ax3 = messages.plot(ax=ax.twiny(), secondary_y=True, color=DEFAULT_LINE_COLOR)
        
        ax.grid(axis='y', linestyle='solid')
        ax2.legend(loc='upper right')
        ax3.legend(loc='upper left')

        plot.show()

    def by_message_aspects(self):
        '''Shows the messages aspects per month. Shows the number of laughs, marks, emojis
        and numbers characters sent per month.
        '''
        fig, ax = plot.subplots()
        ax.set_title('Amount by Month')

        chat = self.chats[0]
        data = defaultdict(list)

        columns = ['QTD_Riso', 'QTD_Pontuacao', 'QTD_Emoji', 'QTD_Numeros', 'QTD_Mensagens']
        rows = []

        for message in chat.messages:
            index = message.created_at.replace(day=1, hour=0, minute=0, second=0)
            strftime = index.strftime('%B %Y')            
            data[strftime].append(message)

        for values in data.values():
            laughs = 0
            marks = 0
            emojis = 0
            numbers = 0
            messages = 0

            for message in values:
                laughs += len(message.laughs)
                marks += len(message.question_marks) + len(message.exclamation_marks)
                emojis += len(message.emojis)
                numbers += len(message.numbers)
                messages += 1
                
            rows.append([laughs, marks, emojis, numbers, messages])

        dataframe = DataFrame(rows, index=data.keys(), columns=columns)

        bars = dataframe.drop(columns='QTD_Mensagens')
        ax2 = bars.plot.bar(ax=ax, rot=0, color=SECONDARY_COLORS)

        messages = dataframe['QTD_Mensagens']
        ax3 = messages.plot(ax=ax.twiny(), secondary_y=True, color='#000000')

        ax.grid(axis='y', linestyle='solid')
        ax2.legend(loc='upper right')
        ax3.legend(loc='upper left')

        plot.show()

    def by_weekday(self):
        '''Shows which weekdays are more active.'''
        fig, ax = plot.subplots()
        ax.set_title('Amount by Month')

        chat = self.chats[0]
        data = defaultdict(list)

        columns = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'QTD_Liquido']
        rows = []

        for message in chat.messages:
            index = message.created_at.replace(day=1, hour=0, minute=0, second=0)
            strftime = index.strftime('%B %Y')
            data[strftime].append(message)

        for values in data.values():
            liquid = 0
            weekdays = {
                'Sunday': 0,
                'Monday': 0,
                'Tuesday': 0,
                'Wednesday': 0,
                'Thursday': 0,
                'Friday': 0,
                'Saturday': 0
            }

            for message in values:
                liquid += 1
                weekdays[message.weekday] += 1

            rows.append([*weekdays.values(), liquid])

        dataframe = DataFrame(rows, index=data.keys(), columns=columns)

        bars = dataframe.drop(columns='QTD_Liquido')
        ax2 = bars.plot.bar(ax=ax, rot=0, color=TERTIARY_COLORS)

        messages = dataframe['QTD_Liquido']
        ax3 = messages.plot(ax=ax.twiny(), secondary_y=True, color='#01b8aa')

        ax.grid(axis='y', linestyle='solid')
        ax2.legend(loc='upper right')
        ax3.legend(loc='upper left')

        plot.show()

    def by_message_period(self):
        '''Shows which periods are more active.'''
        fig, ax = plot.subplots()
        ax.set_title('Amount by Month')

        chat = self.chats[0]
        data = defaultdict(list)

        columns = [c.value for c in Period]
        rows = []

        for message in chat.messages:
            index = message.created_at.replace(day=1, hour=0, minute=0, second=0)
            strftime = index.strftime('%B %Y')
            data[strftime].append(message)

        for values in data.values():
            periods = {c.value: 0 for c in Period}

            for message in values:
                periods[message.period.value] += 1

            rows.append(list(periods.values()))

        dataframe = DataFrame(rows, index=data.keys(), columns=columns)
        dataframe.plot(ax=ax, rot=0, color=SECONDARY_COLORS)

        plot.show()

    def by_message_sub_period(self):
        '''Shows which sub-periods are more active.'''
        fig, ax = plot.subplots()
        ax.set_title('Amount by Month')

        chat = self.chats[0]
        data = defaultdict(list)

        columns = [c.value for c in SubPeriod]
        rows = []

        for message in chat.messages:
            index = message.created_at.replace(day=1, hour=0, minute=0, second=0)
            strftime = index.strftime('%B %Y')
            data[strftime].append(message)

        for values in data.values():
            sub_periods = {c.value: 0 for c in SubPeriod}

            for message in values:
                sub_periods[message.sub_period.value] += 1

            rows.append(list(sub_periods.values()))

        dataframe = DataFrame(rows, index=data.keys(), columns=columns)
        dataframe.plot(ax=ax, rot=0, color=SECONDARY_COLORS)

        plot.show()

    def by_users_activity(self):
        '''Shows which users are more active in the chat.'''
        fig, ax = plot.subplots()
        ax.set_title('Amount by User')

        chat = self.chats[0]
        data = {}

        columns = ['QTD_Liquido', 'QTD_Texto', 'QTD_Mensagens']
        rows = []

        for actor in chat.actors:
            data[actor.display_name] = actor.messages

        for values in data.values():
            liquid = 0
            pure_text = 0
            
            for message in values:
                liquid += len(message.liquid)
                pure_text += len(message.pure_text)

            rows.append([liquid, pure_text, len(values)])

        temp = DataFrame(rows, index=data.keys(), columns=columns)[:10]
        dataframe = temp.sort_values(columns, ascending=False)

        bars = dataframe.drop(columns='QTD_Mensagens')
        ax2 = bars.plot.bar(ax=ax, rot=0, color=DEFAULT_COLORS)

        messages = dataframe['QTD_Mensagens']
        ax3 = messages.plot(ax=ax.twiny(), secondary_y=True, color=DEFAULT_LINE_COLOR)

        ax.grid(axis='y', linestyle='solid')
        ax2.legend(loc='upper right')
        ax3.legend(loc='upper left')

        plot.show()

    def by_users_messages_aspects(self):
        '''Shows the messages aspects per user. Shows the number of laughs, marks, 
        numbers characters sent per user.'''
        fig, ax = plot.subplots()
        ax.set_title('Amount by User')

        chat = self.chats[0]
        data = {}

        columns = ['QTD_Numero', 'QTD_Pontuacao', 'QTD_Riso', 'QTD_Mensagens']
        rows = []

        for actor in chat.actors:
            data[actor.display_name] = actor.messages

        for values in data.values():
            laughs = 0
            marks = 0
            numbers = 0

            for message in values:
                for number in message.numbers:
                    numbers += len(number)

                for exclamation_mark in message.exclamation_marks:
                    marks += len(exclamation_mark)

                for question_mark in message.question_marks:
                    marks += len(question_mark)
                
                for laugh in message.laughs:
                    laughs += len(laugh)

            rows.append([numbers, marks, laughs, len(values)])

        temp = DataFrame(rows, index=data.keys(), columns=columns)[:10]
        dataframe = temp.sort_values(columns, ascending=False)

        bars = dataframe.drop(columns='QTD_Mensagens')
        ax2 = bars.plot.bar(ax=ax, rot=0, color=SECONDARY_COLORS)

        messages = dataframe['QTD_Mensagens']
        ax3 = messages.plot(ax=ax.twiny(), secondary_y=True, color='#000000')

        ax.grid(axis='y', linestyle='solid')
        ax2.legend(loc='upper right')
        ax3.legend(loc='upper left')

        plot.show()
            
