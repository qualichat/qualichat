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

import inspect
from pathlib import Path
from types import FunctionType
from typing import Any, ClassVar, Dict, List, Optional
from functools import cache

import spacy
from wordcloud import WordCloud # type: ignore


from .chat import Chat
from ._partials import *
from .enums import MessageType
from .models import Message
from .sorters import generate_wordcloud


__all__ = ('BaseFrame', 'KeysFrame', 'ParticipationStatusFrame')


nlp = spacy.load('pt_core_news_md')

keyword: Optional[str] = None
pos: Optional[str] = None


def _normalize_frame_name(name: str) -> str:
    return name.replace('_', ' ').title()


@cache
def _parse_nlp(word: str, *, pos: str):
    doc = nlp(word)
    endings = ('ar', 'er', 'ir')

    for token in doc:
        if token.pos_ == pos:
            if pos == 'VERB' and not token.text.endswith(endings):
                continue

            yield token.text


def _parse_nlp_messages(messages: List[Message]):
    types = {'Verbs': 'VERB', 'Nouns': 'NOUN', 'Adjectives': 'ADJ'}

    global pos

    if pos is None:
        choices = list(types.keys())
        msg = 'Choose a morphological class:'

        morphological_class = select(msg, choices).ask()
        pos = types[morphological_class]

    with progress_bar() as progress:
        for message in progress.track(messages, description='Parsing...'):
            for text in _parse_nlp(message['Qty_char_text'], pos=pos):
                yield text


def _generate_wordcloud(data: List[str]):
    parent = Path(__file__).resolve().parent
    path = parent / 'fonts' / 'Roboto-Regular.ttf'

    configs: Dict[str, Any] = {}
    configs['width'] = 1920
    configs['height'] = 1080
    configs['font_path'] = str(path)
    configs['background_color'] = 'white'

    all_words = ' '.join(data)
    return WordCloud(**configs).generate(all_words) # type: ignore


class BaseFrame:
    """Represents the base of a Qualichat frame.
    Generally, you should use the built-in frames that Qualichat
    offers you. However, you can subclass this class and create your
    own frames.
    .. note::
        To automatically generate charts, you must create a method
        decorated with :meth:`generate_chart` that returns a
        :class:`pandas.DataFrame`.
    Attributes
    ----------
    chats: List[:class:`.Chat`]
        All the chats loaded via :meth:`qualichat.load_chats`.
    """

    __slots__ = ('chats', 'charts')

    fancy_name: ClassVar[str]

    def __init__(self, chats: List[Chat]) -> None:
        def predicate(o: object) -> bool:
            if inspect.ismethod(o):
                return not o.__name__.startswith('_') # type: ignore

            return False

        methods = inspect.getmembers(self, predicate=predicate)
        charts = {}

        for name, method in methods:
            charts[_normalize_frame_name(name)] = method

        self.chats = chats
        self.charts: Dict[str, FunctionType] = charts

    def __repr__(self) -> str:
        return '<%s>' % self.__class__.__name__


keyword: Optional[str] = None


class KeysFrame(BaseFrame):
    """
    """

    fancy_name = 'Keys'

    def keyword(self, chats: List[Chat]) -> None:
        """
        """
        wordclouds: Dict[Chat, WordCloud] = {}
        title = 'Keys Frame (Keyword)'

        global keyword

        if not keyword:
            result: str = input('Enter the keyword:').ask()
            keyword = result

        for chat in chats:
            new_messages: List[Message] = []

            for message in chat.messages:
                if message['Type'] is not MessageType.default:
                    continue

                if keyword.lower() not in message.content.lower():
                    continue

                new_messages.append(message)

            data: List[str] = list(_parse_nlp_messages(new_messages))
            wordclouds[chat] = _generate_wordcloud(data)

        generate_wordcloud(wordclouds, title=title)


class ParticipationStatusFrame(BaseFrame):
    """
    """

    fancy_name = 'Participation Status'
