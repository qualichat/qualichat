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


# Add ``Inter`` font.
fonts = Path(__file__).parent / 'fonts'

for font in font_manager.findSystemFonts(str(fonts)):
    font_manager.fontManager.addfont(font)

matplotlib.rcParams['font.family'] = 'Inter'


DEFAULT_COLORS = cycle(['#08bcac', '#38444c'])
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

        ax.grid(True, linestyle='--')
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
        color = list(islice(DEFAULT_COLORS, None, len(dataframe)))

        bars = dataframe.drop(columns='QTD_Mensagens')
        ax2 = bars.plot.bar(ax=ax, rot=0, color=color)

        messages = dataframe['QTD_Mensagens']
        ax3 = messages.plot(ax=ax.twiny(), secondary_y=True, color=DEFAULT_LINE_COLOR)
        
        ax2.legend(loc='upper right')
        ax3.legend(loc='upper left')

        plot.show()
