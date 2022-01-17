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

import re


__all__ = (
    'CHAT_FORMAT_RE',
    'USER_MESSAGE_RE',
    'URL_RE',
    'EMAIL_RE',
    'QUESTION_MARK_RE',
    'EXCLAMATION_MARK_RE',
    'MENTION_RE',
    'NUMBERS_RE',
    'LAUGHS_RE',
    'SHORT_YOUTUBE_LINK_RE',
    'YOUTUBE_LINK_RE',
    'EMOTICONS_RE',
)


CHAT_FORMAT_RE = re.compile(r'''
    ^\[
        (?P<datetime>\d{2}/\d{2}/\d{2}\s\d{2}:\d{2}:\d{2})
    \]\s
    (?P<rest>[\S\s]+?)
    (?=\n\[.+\]|\Z)
''', re.M | re.X)

USER_MESSAGE_RE = re.compile(r'''
    (?P<actor>.*?)
    :\s+
    (?P<message>[\s\S]+)
''', re.X)

URL_RE = re.compile(r'''
    http[s]?://
    (?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F]))+
''', re.X)

EMAIL_RE = re.compile(r'''
    \b
    [A-Z0-9._%+-]+
    @
    [A-Z0-9.-]+
    \.[A-Z]{2,}
    \b
''', re.X | re.I)

QUESTION_MARK_RE = re.compile(r'''
    \?+
''', re.X)

EXCLAMATION_MARK_RE = re.compile(r'''
    !+
''', re.X)

MENTION_RE = re.compile(r'''
    @\d{8,}
''', re.X)

NUMBERS_RE = re.compile(r'''
    \d+
''', re.X)

LAUGHS_RE = re.compile(r'''
    \s
    (
        (?:he|ha|hi|hu){2,}|
        (?:hh){1,}|
        (?:ja|je|ka|rs){2,}|
        (?:k){2,}
    )
''', re.X | re.I)

SHORT_YOUTUBE_LINK_RE = re.compile(r'''
    https:\/\/youtu\.be\/([^\?|\s|\n]+)
''', re.X)

YOUTUBE_LINK_RE = re.compile(r'''
    https://www\.youtube\.com/watch\?v=([^&|\s|\n]+)
''')

EMOTICONS_RE = re.compile(r'''
    \s*(:-?\)|:-?\(|:-?D)\s*
''')
