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

import matplotlib
from matplotlib import pyplot as plot
from matplotlib import font_manager
from pandas import DataFrame

from .chat import Qualichat


# Add ``Inter`` font.
fonts = Path(__file__).parent / 'fonts'

for font in font_manager.findSystemFonts(str(fonts)):
    font_manager.fontManager.addfont(font)

matplotlib.rcParams['font.family'] = 'Inter'


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

    def by_messages_per_year(self):
        '''Shows the number of messages per day. Shows the number of liquid characters
        and the number of text characters.
        '''
        fig, ax = plot.subplots()
        chat = self.chats[0]

        dates = []
        columns = ['QTD_Liquido', 'QTD_Texto', 'QTD_Mensagens']

        messages_creations = [m.created_at for m in chat.messages]
        rows = []

        min_date = min(messages_creations)
        max_date = max(messages_creations)

        delta = max_date - min_date

        for i in range(delta.days + 1):
            date = min_date + datetime.timedelta(days=i)
            dates.append(date.replace(hour=0, minute=0, second=0))

            liquid = 0
            text = 0
            messages = 0

            for message in chat.messages:
                same_month = message.created_at.month == date.month
                same_day = message.created_at.day == date.day

                if not (same_day and same_month):
                    continue

                text += len(message.pure_text)
                liquid += len(message.liquid)
                messages += 25

            rows.append([liquid, text, messages])

        dataframe = DataFrame(rows, index=dates, columns=columns)
        ax2 = ax.twiny()

        bars = dataframe.drop(columns='QTD_Mensagens')
        bars.plot.bar(ax=ax)

        messages = dataframe['QTD_Mensagens']
        messages.plot(ax=ax2, secondary_y=True, legend=True, color='#000000')

        plot.show()
