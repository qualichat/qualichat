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

from typing import Any, List, Dict, Callable, Optional, Union, DefaultDict
from collections import defaultdict

from pandas import DataFrame
from pandas.core.generic import NDFrame
from plotly.subplots import make_subplots # type: ignore
from plotly.graph_objects import Scatter # type: ignore

from .chat import Chat
from .models import Message


__all__ = (
    'BaseFrame',
    'KeysFrame',
)


DataFrames = Dict[str, Union[DataFrame, NDFrame]]


# TODO: Add return type to this function.
# TODO: Add docstring for this function.
# TODO: Perhaps there is a way to completely automate the creation of
# charts, all you need to say is which columns Qualichat should 
# analyze.
def generate_chart(
    *,
    bars: Optional[List[str]] = None,
    lines: Optional[List[str]] = None,
    title: Optional[str] = None
):
    if bars is None:
        bars = []

    if lines is None:
        lines = []

    def decorator(method: Callable[..., DataFrames]) -> Callable[..., None]:
        def generator(self: BaseFrame, *args: Any, **kwargs: Any) -> None:
            specs = [[{'secondary_y': True}]]

            fig = make_subplots(specs=specs) # type: ignore
            dataframes = method(self, *args, **kwargs)

            # buttons: List[Dict[str, Any]] = []

            # for filename, dataframe in dataframes.items():
            #     button: Dict[str, Any] = dict()
            #     button['label'] = filename
            #     button['method'] = 'update'

            #     ranges: List[Any] = [{'title': {'text': 'Sample text'}}]
            #     button['args'] = ranges

            #     buttons.append(button)

            filename, dataframe = list(dataframes.items())[0]
            index = dataframe.index # type: ignore

            if bars is not None:
                for bar in bars:
                    filtered = getattr(dataframe, bar)
                    options = dict(x=index, y=list(filtered), name=bar) # type: ignore
                    fig.add_bar(**options) # type: ignore

            if lines is not None:
                for line in lines:
                    filtered = getattr(dataframe, line)
                    scatter = Scatter(x=index, y=list(filtered), name=line) # type: ignore
                    fig.add_trace(scatter, secondary_y=True) # type: ignore

            # menus: List[Dict[str, Any]] = [{'active': 0, 'showactive': True, 'buttons': buttons}]
            title_text = f'{title} ({filename})'

            fig.update_layout(title_text=title_text) # type: ignore
            fig.show() # type: ignore

        # Dummy implementation for the decorated function to inherit
        # the documentation.
        generator.__doc__ = method.__doc__
        generator.__annotations__ = method.__annotations__

        return generator
    return decorator


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

    fancy_name: str = ''

    def __init__(self, chats: List[Chat]) -> None:
        self.chats: List[Chat] = chats
        self.charts: Dict[str, Callable[..., Any]] = {}

        for attr in dir(self):
            if attr.startswith('_'):
                continue

            obj: Callable[..., Any] = getattr(self, attr)

            if not callable(obj):
                continue

            self.charts[attr] = obj

    def __repr__(self) -> str:
        return '<BaseFrame>'


class KeysFrame(BaseFrame):
    """A frame that adds charts generator related to chat messages.

    .. note::

        This frame is already automatically added to Qualichat.

    Attributes
    ----------
    chats: List[:class:`.Chat`]
        All the chats loaded via :meth:`qualichat.load_chats`.
    """

    __slots__ = ()

    fancy_name = 'Keys'

    def __repr__(self) -> str:
        return '<KeysFrame>'

    @generate_chart(
        bars=[
            'Qty_char_links', 'Qty_char_emails',
            'Qty_char_marks', 'Qty_char_mentions',
        ],
        lines=['Qty_messages'],
        title='Keys Frame (Laminations)'
    )
    def laminations(self) -> DataFrames:
        dataframes: DataFrames = {}

        columns = [
            'Qty_char_links', 'Qty_char_emails',
            'Qty_char_marks', 'Qty_char_mentions',
            'Qty_messages'
        ]

        for chat in self.chats:
            data: DefaultDict[str, List[Message]] = defaultdict(list)
            rows: List[List[int]] = []

            for message in chat.messages:
                data[message.created_at.strftime('%B %Y')].append(message)

            for messages in data.values():
                links = 0
                marks = 0
                emails = 0
                mentions = 0
                total_messages = 0

                for message in messages:
                    links += len(message['Qty_char_links'])
                    marks += len(message['Qty_char_marks'])
                    emails += len(message['Qty_char_emails'])
                    mentions += len(message['Qty_char_mentions'])
                    total_messages += 1

                rows.append([links, marks, emails, mentions, total_messages])

            index = list(data.keys())
            dataframe = DataFrame(rows, index=index, columns=columns)
                
            dataframes[chat.filename] = dataframe

        return dataframes
