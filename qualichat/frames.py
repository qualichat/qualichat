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
import base64
from pathlib import Path
from typing import (
    Any,
    ClassVar,
    DefaultDict,
    Dict,
    List,
    Optional,
    Pattern,
    Tuple,
    Union,
)
from types import FunctionType
from functools import partial, cache
from io import BytesIO
from collections import defaultdict, Counter, OrderedDict

import questionary
import spacy
import qualitube # type: ignore
from pandas import DataFrame
from plotly.subplots import make_subplots # type: ignore
from plotly.graph_objs import Scatter, Figure # type: ignore
from rich.progress import Progress
from wordcloud.wordcloud import WordCloud # type: ignore
from tldextract import extract # type: ignore

from . import sorters
from .chat import Chat
from .models import Message
from .enums import MessageType
from .utils import log, parse_domain
from .regex import *


__all__ = ('BaseFrame', 'KeysFrame', 'ParticipationStatusFrame')


input = partial(questionary.text, qmark='[qualichat]')
select = partial(questionary.select, qmark='[qualichat]')


def generate_chart(
    dataframes: Dict[Chat, DataFrame],
    *,
    bars: Optional[List[str]] = None,
    lines: Optional[List[str]] = None,
    title: Optional[str] = None,
) -> None:
    """
    """
    if bars is None:
        bars = []

    if lines is None:
        lines = []

    specs = [[{'secondary_y': True}]]
    fig = make_subplots(specs=specs) # type: ignore

    buttons: List[Dict[str, Any]] = []

    for i, (chat, dataframe) in enumerate(dataframes.items()):
        index = list(dataframe.index) # type: ignore

        button: Dict[str, Any] = {}
        button['label'] = chat.filename
        button['method'] = 'update'

        args: List[Union[Dict[str, Any], List[Dict[str, Any]]]] = []

        visibility: List[bool] = []
        for j in range(len(dataframes)):
            for _ in range(len(bars + lines)):
                visibility.append(i == j)

        args.append({'visible': visibility})
        args.append({'title': {'text': f'{title} ({chat.filename})'}})

        button['args'] = args
        buttons.append(button)

        for bar in bars:
            filtered = getattr(dataframe, bar)
            options = dict(x=index, y=list(filtered), name=bar) # type: ignore
            fig.add_bar(**options) # type: ignore

        for line in lines:
            filtered = getattr(dataframe, line)
            scatter = Scatter(x=index, y=list(filtered), name=line) # type: ignore
            fig.add_trace(scatter, secondary_y=True) # type: ignore

    updatemenus = [{'buttons': buttons, 'active': 0}]
    fig.update_layout(updatemenus=updatemenus) # type: ignore

    fig.update_xaxes(rangeslider_visible=True) # type: ignore
    fig.show() # type: ignore


def generate_wordcloud(wordclouds: Dict[Chat, WordCloud], *, title: str):
    """
    """
    fig = Figure() # type: ignore
    buttons: List[Dict[str, Any]] = []

    for i, (chat, wordcloud) in enumerate(wordclouds.items()):
        button: Dict[str, Any] = {}
        button['label'] = chat.filename
        button['method'] = 'update'

        args: List[Dict[str, Any]] = []

        visibility: List[bool] = []
        for j in range(len(wordclouds)):
            visibility.append(i == j)

        args.append({'visible': visibility})
        args.append({'title': {'text': f'{title} ({chat.filename})'}})

        button['args'] = args

        buffer = BytesIO()
        image = wordcloud.to_image() # type: ignore

        image.save(buffer, format='png')
        buffer.seek(0)
        encoded_file = base64.b64encode(buffer.read()).decode('utf-8')

        source = f'data:image/png;base64, {encoded_file}'
        fig.add_image(source=source) # type: ignore

        buttons.append(button)

    updatemenus = [{'buttons': buttons, 'active': 0}]
    fig.update_layout(updatemenus=updatemenus) # type: ignore

    fig.show() # type: ignore


def generate_table(
    tables: Dict[Chat, DataFrame],
    *,
    columns: Optional[List[str]] = None,
    title: str
):
    """
    """
    if columns is None:
        columns = []

    fig = make_subplots() # type: ignore
    buttons: List[Dict[str, Any]] = []

    for chat, dataframe in tables.items():
        button: Dict[str, Any] = {}
        button['label'] = chat.filename
        button['method'] = 'update'

        args: List[Dict[str, Any]] = []
        values: List[Any] = []

        for column in columns:
            values.append(dataframe[column].to_list()) # type: ignore

        args.append({'cells': {'values': values}, 'header': {'values': columns}})
        args.append({'title': {'text': f'{title} ({chat.filename})'}})

        button['args'] = args
        buttons.append(button)

    header: Dict[str, List[str]] = {'values': []}
    cells: Dict[str, List[Any]] = {'values': []}

    fig.add_table(header=header, cells=cells) # type: ignore

    updatemenus = [{'buttons': buttons, 'active': 0}]
    fig.update_layout(updatemenus=updatemenus) # type: ignore

    fig.show() # type: ignore


def _normalize_frame_name(name: str) -> str:
    return name.replace('_', ' ').title()


def _normalize_row(row: List[int], actor: str, chat: Chat) -> List[int]:
    if actor != 'Others':
        return row

    return [int(i / len(chat.actors)) for i in row]


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
        def predicate(object: object) -> bool:
            if inspect.ismethod(object):
                return not object.__name__.startswith('_') # type: ignore

            return False

        methods = inspect.getmembers(self, predicate=predicate)
        charts = {}

        for name, method in methods:
            charts[_normalize_frame_name(name)] = method

        self.chats = chats
        self.charts: Dict[str, FunctionType] = charts

    def __repr__(self) -> str:
        return '<%s>' % self.__class__.__name__


nlp = spacy.load('pt_core_news_md')

pos: Optional[str] = None
keyword: Optional[str] = None


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
        morphological_class = select('Choose a morphological class:', types).ask()
        pos = types[morphological_class]

    with Progress() as progress:
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


class KeysFrame(BaseFrame):
    """
    """

    fancy_name = 'Keys'

    def __init__(self, chats: List[Chat], *, api_key: Optional[str]) -> None:
        self.api_key = api_key
        super().__init__(chats)

    @sorters.wordcloud
    def messages(self, chats_data: Dict[Chat, List[Message]]):
        """
        """
        wordclouds: Dict[Chat, WordCloud] = {}
        title = 'Keys Frame (Messages)'

        for chat, messages in chats_data.items():
            data: List[str] = list(_parse_nlp_messages(messages))
            wordclouds[chat] = _generate_wordcloud(data)

        generate_wordcloud(wordclouds, title=title)

    @sorters.wordcloud
    def keyword(self, chats_data: Dict[Chat, List[Message]]):
        """
        """
        wordclouds: Dict[Chat, WordCloud] = {}
        title = 'Keys Frame (Keyword)'

        global keyword

        if keyword is None:
            result: str = input('Enter the keyword:').ask()
            keyword = result

        for chat, messages in chats_data.items():
            new_messages: List[Message] = []

            for message in messages:
                if keyword.lower() not in message.content.lower():
                    continue

                new_messages.append(message)

            data: List[str] = list(_parse_nlp_messages(new_messages))
            wordclouds[chat] = _generate_wordcloud(data)

        generate_wordcloud(wordclouds, title=title)

    def ratings(self, chats: List[Chat]):
        """
        """
        if not self.api_key:
            return log('error', 'No API Key provided. Please provide one.')

        client = qualitube.Client(self.api_key)

        title = 'Keys Frame (Ratings)'
        tables: Dict[Chat, DataFrame] = {}

        columns = [
            'Media', 'Actor', 'Date', 'Link',
            'Views', 'Likes', 'Comments', 'Title'
        ]

        regexes: Dict[Tuple[str, str], Pattern[str]] = {
            ('youtu', 'be'): SHORT_YOUTUBE_LINK_RE,
            ('youtube', 'com'): YOUTUBE_LINK_RE
        }

        for chat in chats:
            rows: List[List[Any]] = []
            url_counter: Counter[str] = Counter()

            views_cache: DefaultDict[str, Optional[int]] = defaultdict(int)
            likes_cache: DefaultDict[str, Optional[int]] = defaultdict(int)
            comments_cache: DefaultDict[str, Optional[int]] = defaultdict(int)
            titles_cache: DefaultDict[str, Optional[str]] = defaultdict(str)

            with Progress() as progress:
                for message in progress.track(chat.messages):
                    created_at = str(message.created_at)
                    actor = message.actor.display_name

                    for url in message['Qty_char_links']:
                        domain = parse_domain(url)

                        if domain == 'YouTube':
                            url_counter[url] += 1

                            # Only repeated items are parsed.
                            if url_counter[url] != 2:
                                continue

                            _, domain, suffix = extract(url) # type: ignore
                            regex = regexes[(domain, suffix)] # type: ignore

                            if not (match := regex.match(url)):
                                continue

                            id = match.group(1)
                            videos = client.get_videos([id]).videos

                            if not videos:
                                continue

                            video = videos[0]
                        
                            views_cache[url] = video.view_count
                            likes_cache[url] = video.like_count
                            comments_cache[url] = video.comment_count
                            titles_cache[url] = video.title

                        views = views_cache[url] or ''
                        likes = likes_cache[url] or ''
                        comments = comments_cache[url] or ''
                        video_title = titles_cache[url]

                        rows.append([
                            domain, actor, created_at, url,
                            views, likes, comments, video_title
                        ])

            dataframe = DataFrame(rows, columns=columns)
            tables[chat] = dataframe

        generate_table(tables, columns=columns, title=title)

    @sorters.modes
    def laminations(self, chats_data: Dict[Chat, Dict[str, List[Message]]]):
        """
        """
        title = 'Keys Frame (Laminations)'
        dataframes: Dict[Chat, DataFrame] = {}

        bars = [
            'Qty_char_links', 'Qty_char_emails',
            'Qty_char_mentions', 'Qty_char_emoji'
        ]
        lines = ['Qty_messages']

        for chat, data in chats_data.items():
            rows: List[List[int]] = []

            for actor, messages in data.items():
                links = 0
                emojis = 0
                emails = 0
                mentions = 0

                for message in messages:
                    links += len(message['Qty_char_links'])
                    emojis += len(message['Qty_char_emoji'])
                    emails += len(message['Qty_char_emails'])
                    mentions += len(message['Qty_char_mentions'])

                row = [links, emojis, emails, mentions, len(messages)]
                rows.append(_normalize_row(row, actor, chat))

            index = list(data.keys())

            dataframe = DataFrame(rows, index=index, columns=bars + lines)
            dataframes[chat] = dataframe

        generate_chart(dataframes, lines=lines, bars=bars, title=title)

    @sorters.modes
    def links(self, chats_data: Dict[Chat, Dict[str, List[Message]]]):
        """
        """
        title = 'Keys Frame (Links)'
        dataframes: Dict[Chat, DataFrame] = {}

        bars = ['Qty_char_links']
        lines = ['Qty_messages']

        for chat, data in chats_data.items():
            rows: List[List[int]] = []

            for actor, messages in data.items():
                links = 0

                for message in messages:
                    links += len(message['Qty_char_links'])

                row = [links, len(messages)]
                rows.append(_normalize_row(row, actor, chat))

            index = list(data.keys())

            dataframe = DataFrame(rows, index=index, columns=bars + lines)
            dataframes[chat] = dataframe

        generate_chart(dataframes, lines=lines, bars=bars, title=title)

    @sorters.modes
    def mentions(self, chats_data: Dict[Chat, Dict[str, List[Message]]]):
        """
        """
        title = 'Keys Frame (Mentions)'
        dataframes: Dict[Chat, DataFrame] = {}

        bars = ['Qty_char_mentions']
        lines = ['Qty_messages']

        for chat, data in chats_data.items():
            rows: List[List[int]] = []

            for actor, messages in data.items():
                mentions = 0

                for message in messages:
                    mentions += len(message['Qty_char_mentions'])

                row = [mentions, len(messages)]
                rows.append(_normalize_row(row, actor, chat))

            index = list(data.keys())

            dataframe = DataFrame(rows, index=index, columns=bars + lines)
            dataframes[chat] = dataframe

        generate_chart(dataframes, lines=lines, bars=bars, title=title)

    @sorters.modes
    def emails(self, chats_data: Dict[Chat, Dict[str, List[Message]]]):
        """
        """
        title = 'Keys Frame (E-mails)'
        dataframes: Dict[Chat, DataFrame] = {}

        bars = ['Qty_char_emails']
        lines = ['Qty_messages']

        for chat, data in chats_data.items():
            rows: List[List[int]] = []

            for actor, messages in data.items():
                emails = 0

                for message in messages:
                    emails += len(message['Qty_char_emails'])

                row = [emails, len(messages)]
                rows.append(_normalize_row(row, actor, chat))

            index = list(data.keys())

            dataframe = DataFrame(rows, index=index, columns=bars + lines)
            dataframes[chat] = dataframe

        generate_chart(dataframes, lines=lines, bars=bars, title=title)

    @sorters.modes
    def textual_symbols(self, chats_data: Dict[Chat, Dict[str, List[Message]]]):
        """
        """
        title = 'Keys Frame (Textual symbols)'
        dataframes: Dict[Chat, DataFrame] = {}

        bars = ['Qty_char_marks', 'Qty_char_emoji']
        lines = ['Qty_messages']

        for chat, data in chats_data.items():
            rows: List[List[int]] = []

            for actor, messages in data.items():
                marks = 0
                emojis = 0

                for message in messages:
                    marks += len(message['Qty_char_marks'])
                    emojis += len(message['Qty_char_emoji'])

                row = [marks, emojis, len(messages)]
                rows.append(_normalize_row(row, actor, chat))

            index = list(data.keys())

            dataframe = DataFrame(rows, index=index, columns=bars + lines)
            dataframes[chat] = dataframe

        generate_chart(dataframes, lines=lines, bars=bars, title=title)


class ParticipationStatusFrame(BaseFrame):
    """
    """

    fancy_name = 'Participation Status'

    @sorters.group_messages_by_users
    def bots(self, chat_data: Dict[Chat, Dict[str, List[Message]]]) -> None:
        """
        """
        dataframes: Dict[Chat, DataFrame] = {}
        title = 'Participation Status Frame (Bots)'

        bars = ['Qty_score']
        lines = ['Qty_messages']

        for chat, data in chat_data.items():
            rows: List[List[int]] = []

            for messages in data.values():
                chars_net: int = 0
                videos: int = 0
                stickers: int = 0

                for message in messages:
                    if message['Type'] is MessageType.default:
                        chars_net += len(message['Qty_char_net'].split())
                    elif message['Type'] is MessageType.video_omitted:
                        videos += 1
                    elif message['Type'] is MessageType.sticker_omitted:
                        stickers += 1

                result = ((chars_net * 1) + (videos * 2) + (stickers * 3)) / 6
                rows.append([int(result), len(messages)])

            index = list(data.keys())

            dataframe = DataFrame(rows, index=index, columns=bars + lines)
            dataframes[chat] = dataframe

        generate_chart(dataframes, bars=bars, lines=lines, title=title)

    @sorters.group_messages_by_users
    def messages_per_actors(self, chat_data: Dict[Chat, Dict[str, List[Message]]]) -> None:
        """
        """
        dataframes: Dict[Chat, DataFrame] = {}
        title = 'Participation Status Frame (Messages per Actors)'

        bars = ['Qty_messages', 'Qty_char_text', 'Qty_char_net']
        lines: List[str] = []

        for chat, data in chat_data.items():
            rows: List[List[int]] = []

            for messages in data.values():
                chars_text: int = 0
                chars_net: int = 0

                for message in messages:
                    if message['Type'] is not MessageType.default:
                        continue

                    chars_text += len(message['Qty_char_text'].split())
                    chars_net += len(message['Qty_char_net'].split())

                rows.append([len(messages), chars_text, chars_net])

            index = list(data.keys())

            dataframe = DataFrame(rows, index=index, columns=bars + lines)
            dataframes[chat] = dataframe

        generate_chart(dataframes, bars=bars, lines=lines, title=title)

    def messages_per_actors_per_weekday(self, chats: List[Chat]) -> None:
        """
        """
        dataframes: Dict[Chat, DataFrame] = {}
        title = 'Participation Status Frame (Messages per Actors per Weekday)'

        bars = [
            'Sunday', 'Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday'
        ]

        for chat in chats:
            rows: List[List[int]] = []

            for actor in chat.actors:
                data = OrderedDict({weekday: 0 for weekday in bars})

                for message in actor.messages:
                    data[message.created_at.strftime('%A')] += 1

                rows.append(list(data.values()))

            index = [actor.display_name for actor in chat.actors]

            dataframe = DataFrame(rows, index=index, columns=bars)
            dataframes[chat] = dataframe

        generate_chart(dataframes, bars=bars, lines=[], title=title)
