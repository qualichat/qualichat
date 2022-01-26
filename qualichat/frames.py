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

from collections import defaultdict
import inspect
from pathlib import Path
from types import FunctionType
from typing import (
    Any,
    ClassVar,
    Counter,
    DefaultDict,
    Dict,
    List,
    Optional,
    OrderedDict,
    Pattern,
    Set,
    Tuple,
    Union
)

import spacy
from wordcloud import WordCloud # type: ignore
from pandas import DataFrame
from qualitube import Client # type: ignore
from tldextract import extract # type: ignore

from . import sorters
from .chat import Chat
from ._partials import *
from .enums import MessageType
from .models import Message
from .sorters import generate_wordcloud, generate_chart, generate_table
from .utils import config, log, parse_domain
from .regex import SHORT_YOUTUBE_LINK_RE, YOUTUBE_LINK_RE


__all__ = ('BaseFrame', 'KeysFrame', 'ParticipationStatusFrame')


nlp = spacy.load('pt_core_news_md')

keyword: Optional[str] = None
pos: Optional[str] = None

weekdays = (
    'Monday', 'Tuesday', 'Wednesday', 'Thursday',
    'Friday', 'Saturday', 'Sunday'
)


def _normalize_frame_name(name: str) -> str:
    return name.replace('_', ' ').title()


def _normalize_row(row: List[int], actor: str, chat: Chat) -> List[int]:
    if actor != 'Others':
        return row

    return [int(i / len(chat.actors)) for i in row]


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


class KeysFrame(BaseFrame):
    """
    """

    fancy_name = 'Keys'

    @sorters.keys
    def keyword(
        self, chats_data: Dict[Chat, Dict[str, List[Message]]]
    ) -> None:
        """
        """
        wordclouds: Dict[Chat, WordCloud] = {}
        title = 'Keys Frame (Keyword)'

        global keyword

        if not keyword:
            result: str = input('Enter the keyword:').ask()
            keyword = result

        for chat, data in chats_data.items():
            new_messages: List[Message] = []

            for messages in data.values():
                for message in messages:
                    if message['Type'] is not MessageType.default:
                        continue

                    if keyword.lower() not in message.content.lower():
                        continue

                    new_messages.append(message)

            messages_data: List[str] = list(_parse_nlp_messages(new_messages))
            wordclouds[chat] = _generate_wordcloud(messages_data)

        generate_wordcloud(wordclouds, title=title)

    @sorters.keys
    def messages(
        self, chats_data: Dict[Chat, Dict[str, List[Message]]]
    ) -> None:
        """
        """
        wordclouds: Dict[Chat, WordCloud] = {}
        title = 'Keys Frame (Messages)'

        for chat, data in chats_data.items():
            new_messages: List[Message] = []

            for messages in data.values():
                for message in messages:
                    if message['Type'] is not MessageType.default:
                        continue

                    new_messages.append(message)

            messages_data: List[str] = list(_parse_nlp_messages(new_messages))
            wordclouds[chat] = _generate_wordcloud(messages_data)

        generate_wordcloud(wordclouds, title=title)

    @sorters.keys
    def laminations(
        self, chats_data: Dict[Chat, Dict[str, List[Message]]]
    ) -> None:
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

    @sorters.keys
    def links(self, chats_data: Dict[Chat, Dict[str, List[Message]]]) -> None:
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

    @sorters.keys
    def mentions(
        self, chats_data: Dict[Chat, Dict[str, List[Message]]]
    ) -> None:
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

    @sorters.keys
    def emails(self, chats_data: Dict[Chat, Dict[str, List[Message]]]) -> None:
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

    @sorters.keys
    def textual_symbols(
        self, chats_data: Dict[Chat, Dict[str, List[Message]]]
    ) -> None:
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

    @sorters.keys
    def ratings(
        self, chats_data: Dict[Chat, Dict[str, List[Message]]]
    ) -> None:
        """
        """
        if not (api_key := config['google_api_key']):
            return log('error', 'No API Key provided. Please provide one.')

        client = Client(api_key)

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

        for chat, data in chats_data.items():
            rows: List[List[Any]] = []
            url_counter: Counter[str] = Counter()

            views_cache: DefaultDict[str, Optional[int]] = defaultdict(int)
            likes_cache: DefaultDict[str, Optional[int]] = defaultdict(int)
            comments_cache: DefaultDict[str, Optional[int]] = defaultdict(int)
            titles_cache: DefaultDict[str, Optional[str]] = defaultdict(str)

            all_messages: List[Message] = []
            
            for messages in data.values():
                all_messages.extend(messages)

            with progress_bar() as progress:
                for message in progress.track(all_messages):
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


class ParticipationStatusFrame(BaseFrame):
    """
    """

    fancy_name = 'Participation Status'

    @sorters.group_users
    def bots(self, chats_data: Dict[Chat, Dict[str, List[Message]]]) -> None:
        """
        """
        dataframes: Dict[Chat, DataFrame] = {}
        title = 'Participation Status (Bots - Beta)'

        bars = ['Qty_score']
        lines = ['Qty_messages']

        for chat, data in chats_data.items():
            rows: List[List[Union[int, float]]] = []

            for messages in data.values():
                chars_net = 0
                videos = 0
                stickers = 0

                for message in messages:
                    if message['Type'] is MessageType.default:
                        chars_net += len(message['Qty_char_net'].split())
                    elif message['Type'] is MessageType.video_omitted:
                        videos += 1
                    elif message['Type'] is MessageType.sticker_omitted:
                        stickers += 1

                result = ((chars_net * 1) + (videos * 2) + (stickers * 3)) / 6
                rows.append([result, len(messages)])

            index = list(data.keys())

            dataframe = DataFrame(rows, index=index, columns=bars + lines)
            dataframes[chat] = dataframe
            
        generate_chart(dataframes, bars=bars, lines=lines, title=title)

    def messages_per_actors_per_weekday(self, chats: List[Chat]) -> None:
        """
        """
        dataframes: Dict[Chat, DataFrame] = {}
        title = 'Participation Status (Messages per Actors per Weekday)'

        bars = ['Qtd_messages']

        types = {
            'User Messages': 'messages',
            'System Messages': 'system_messages'
        }

        msg = 'Choose the message type:'
        result = select(msg, list(types.keys())).ask()

        message_type = types[result]

        for chat in chats:
            data = OrderedDict({weekday: 0 for weekday in weekdays})

            for message in getattr(chat, message_type):
                data[message.created_at.strftime('%A')] += 1

            index = list(data.keys())
            rows = list(data.values())

            dataframe = DataFrame(rows, index=index, columns=bars)
            dataframes[chat] = dataframe

        generate_chart(dataframes, bars=bars, lines=[], title=title)

    def media_repertoire(self, chats: List[Chat]) -> None:
        """
        """
        # dataframes: Dict[Chat, DataFrame] = {}
        # ttitle = 'Participation Status (Media Repertoire)'

        choices = ['Choose Media', 'Average Media']

        msg = 'Choose you action'
        result = select(msg, choices).ask()

        if result == 'Choose Media':
            return _choose_media(chats)


def _choose_media(chats: List[Chat]) -> None:
    dataframes: Dict[Chat, DataFrame] = {}
    all_media: Set[str] = set()

    for chat in chats:
        for message in chat.messages:
            for url in message['Qty_char_links']:
                all_media.add(parse_domain(url))

    msg = 'Choose a Media'
    whitelist = checkbox(msg, list(all_media)).ask()

    for chat in chats:
        rows: List[List[int]] = []

        for actor in chat.actors:
            data = {domain: 0 for domain in whitelist}

            for message in actor.messages:
                for url in message['Qty_char_links']:
                    domain = parse_domain(url)

                    if domain not in whitelist:
                        continue

                    data[domain] += 1

            rows.append(list(data.values()))

        index = [actor.display_name for actor in chat.actors]

        dataframe = DataFrame(rows, index=index, columns=whitelist)
        dataframes[chat] = dataframe

    print(dataframes)
                
    # for chat in chats:
    #     for actor in chat.actors:

