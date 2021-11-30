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
from typing import Callable, DefaultDict, Dict, List, Optional
from functools import partial

import questionary
from rich import print
from rich.progress import Progress

from .chat import Chat
from .models import Message
from .utils import log


__all__ = ('sort_by_modes',)


Messages = Dict[str, List[Message]]


select = partial(questionary.select, qmark='[qualichat]')
checkbox = partial(questionary.checkbox, qmark='[qualichat]')


def _sort_by_time(messages: List[Message]) -> Optional[Messages]:
    data: DefaultDict[str, List[Message]] = defaultdict(list)

    with Progress() as progress:
        for message in progress.track(messages, description='Sorting...'):
            data[message.created_at.strftime('%B %Y')].append(message)

    choices = ['All', 'Choose a specific epoch']
    selected = select('Which messages should be selected?', choices).ask()

    if selected == 'All':
        return dict(data)

    selected_epochs = checkbox('Choose a chat epoch:', data).ask()

    if not selected_epochs:
        log('error', 'No epochs were selected. Aborting.')
        return None

    return {epoch: data[epoch] for epoch in selected_epochs}


def _sort_by_actor(messages: List[Message]) -> Optional[Messages]:
    data: DefaultDict[str, List[Message]] = defaultdict(list)

    with Progress() as progress:
        for message in progress.track(messages, description='Tracking...'):
            data[message.actor.display_name].append(message)

    choices = ['All', 'Choose a specific actor']
    selected = select('Which actors should be selected?', choices).ask()

    if selected == 'All':
        return dict(data)

    selected_actors = checkbox('Choose an actor:', data).ask()

    if not selected_actors:
        log('error', 'No actors were selected. Aborting.')
        return None

    if len(selected_actors) != 1:
        ret: Dict[str, List[Message]] = {}
        others: List[Message] = []
        
        for actor in data:
            if actor not in selected_actors:
                others.extend(data[actor])
            else:
                ret[actor] = data[actor]

        ret['Others'] = others
        return ret

    actor = selected_actors[0]
    messages = data[actor]

    new_data: DefaultDict[str, List[Message]] = defaultdict(list)

    with Progress() as progress:
        for message in progress.track(messages, description='Sorting...'):
            new_data[message.created_at.strftime('%B %Y')].append(message)

    return dict(new_data)


def sort_by_modes(func: Callable[..., None]):
    """
    """

    # Hack to avoid circular imports.
    from .frames import BaseFrame    

    def decorator(self: BaseFrame, chats: List[Chat]) -> None:
        modes: Dict[str, Callable[..., Optional[Messages]]] = {
            'By Time': _sort_by_time,
            'By Actor': _sort_by_actor,
        }

        name = select('Now, choose your mode:', modes).ask()
        mode = modes[name]

        sorted_messages = {chat: mode(chat.messages) for chat in chats}
        
        if None in sorted_messages.values():
            return
        
        func(self, sorted_messages)

    return decorator


def wordcloud(func: Callable[..., None]):
    """
    """

    # Hack to avoid circular imports.
    from .frames import BaseFrame 

    def decorator(self: BaseFrame, chats: List[Chat]) -> None:
        func(self, {chat: chat.messages for chat in chats})

    return decorator
