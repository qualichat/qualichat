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

import base64
from io import BytesIO
from collections import defaultdict
from typing import Any, Callable, DefaultDict, Dict, List, Optional

from wordcloud import WordCloud # type: ignore
from plotly.graph_objs import Figure # type: ignore

from .chat import Chat
from .models import Message
from .utils import log
from ._partials import progress_bar, select, checkbox


__all__ = ('generate_wordcloud', 'keys')


# chart_type: Optional[Callable[..., None]] = None
sorter_type: Optional[None] = None


def _sort_by_time(chats: List[Chat]) -> Dict[Chat, Dict[str, List[Message]]]:
    ret: Dict[Chat, Dict[str, List[Message]]] = {}

    def sort(messages: List[Message]):
        data: DefaultDict[str, List[Message]] = defaultdict(list)

        with progress_bar() as progress:
            for m in progress.track(messages, description='Sorting...'):
                data[m.created_at.strftime('%B %Y')].append(m)

        choices = ['All', 'Choose an epoch']
        message = f'[{chat.filename}] Which messages should be selected?'
        selected = select(message, choices).ask()

        if selected == 'All':
            return dict(data)

        choices = list(data.keys())
        if not (epochs := checkbox('Choose an epoch:', choices).ask()):
            raise KeyError()

        return {epoch: data[epoch] for epoch in epochs}

    for chat in chats:
        ret[chat] = sort(chat.messages)

    return ret


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


def keys(func: Callable[..., None]):
    """
    """

    # Hack to avoid circular imports.
    from .frames import BaseFrame

    def decorator(self: BaseFrame, chats: List[Chat]) -> None:
        global sorter_type

        if sorter_type is None:
            modes = {'By Time': _sort_by_time}
            choices = list(modes.keys())

            name = select('Choose your mode:', choices).ask()

            try:
                sorted_messages = modes[name](chats)
            except (KeyError, TypeError):
                return log('error', 'Option not selected. Aborting.')

            func(self, sorted_messages)

    return decorator
