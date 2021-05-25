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
from typing import List


class Message:
    '''An ABC that details the common operations on a message.

    The following implement this ABC:

    - :class:`.Message`
    - :class:`.SystemMessage`

    Attributes
    -----------
    content: :class:`str`
        The content of the mes
    created_at: :class:`datetime.datetime`
        The message's creation time.
    '''

    __slots__ = ()

    content: str
    created_at: datetime.datetime

    @property
    def weekday(self) -> str:
        ''':class:`str`: The weekday on which the message was sent.'''
        return self.created_at.strftime('%A')

    @property
    def emojis(self) -> List[str]:
        '''List[:class:`str`]: Returns all the emojis contained in the message content.'''
        return []

    @property
    def urls(self) -> List[str]:
        '''List[:class:`str`]: Returns all the URLs contained in the message content.'''
        return []

    @property
    def emails(self) -> List[str]:
        '''List[:class:`str`]: Returns all the e-mails contained in the message content.'''
        return []

    @property
    def numbers(self) -> List[str]:
        '''List[:class:`str`]: Returns all the numbers contained in the message content.'''
        return []

    @property
    def laughs(self) -> List[str]:
        '''List[:class:`str`]: Returns all the laughs contained in the message content.
        This essentially checks for laughs like `haha`, `kkkk`, `hehe`, etc.
        '''
        return []

    @property
    def symbols(self) -> List[str]:
        '''List[:class:`str`]: Returns all exclamation and question 
        marks contained in the message content.
        '''
        return []

    @property
    def liquid(self) -> str:
        ''':class:`str`: Returns the net content of the message, removing URLs, emails 
        and emojis.
        '''
        return ''
