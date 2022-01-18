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
from typing import Any, Dict, List

from wordcloud import WordCloud # type: ignore
from plotly.graph_objs import Figure # type: ignore

from .chat import Chat


__all__ = ('generate_wordcloud',)


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
