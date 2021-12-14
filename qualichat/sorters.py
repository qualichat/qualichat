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
from typing import Callable, DefaultDict, Dict, List
from functools import partial

import questionary
from rich.progress import Progress

from .chat import Chat
from .models import Message
from .enums import MessageType
from .utils import log


__all__ = ('group_messages_by_users', 'modes', 'wordcloud')


select = partial(questionary.select, qmark='[qualichat]')
checkbox = partial(questionary.checkbox, qmark='[qualichat]')


def group_messages_by_users(func: Callable[..., None]):
    """
    """

    # Hack to avoid circular imports.
    from .frames import BaseFrame 

    def decorator(self: BaseFrame, chats: List[Chat]) -> None:
        data: Dict[Chat, Dict[str, List[Message]]] = {}

        for chat in chats:
            messages = {act.display_name: act.messages for act in chat.actors}
            data[chat] = messages

        func(self, data)

    return decorator



# Data = Dict[Chat, Optional[Union[Dict[str, List[Message]], List[Message]]]]




def _sort_by_time(chats: List[Chat]) -> Dict[Chat, Dict[str, List[Message]]]:
    ret: Dict[Chat, Dict[str, List[Message]]] = {}

    def sort(messages: List[Message]):
        data: DefaultDict[str, List[Message]] = defaultdict(list)

        with Progress() as progress:
            for m in progress.track(messages, description='Sorting...'):
                data[m.created_at.strftime('%B %Y')].append(m)

        choices = ['All', 'Choose an epoch']
        message = f'[{chat.filename}] Which messages should be selected?'
        
        selected = select(message, choices).ask()

        if selected == 'All':
            return dict(data)

        if not (epochs := checkbox('Choose an epoch:', data).ask()):
            raise KeyError()

        return {epoch: data[epoch] for epoch in epochs}

    for chat in chats:
        ret[chat] = sort(chat.messages)

    return ret


def _sort_by_actor(chats: List[Chat]) -> Dict[Chat, Dict[str, List[Message]]]:
    ret: Dict[Chat, Dict[str, List[Message]]] = {}

    def sort(messages: List[Message]) -> Dict[str, List[Message]]:
        data: DefaultDict[str, List[Message]] = defaultdict(list)

        with Progress() as progress:
            for m in progress.track(messages, description='Tracking...'):
                data[m.actor.display_name].append(m)

        choices = ['All', 'Choose a specific actor']
        message = f'[{chat.filename}] Which actors should be selected?'
        selected = select(message, choices).ask()

        if selected == 'All':
            return dict(data)

        if not (actors := checkbox('Choose an actor:', data).ask()):
            raise KeyError()

        if len(actors) != 1:
            ret: Dict[str, List[Message]] = {}
            others: List[Message] = []
            
            for actor in data:
                if actor not in actors:
                    others.extend(data[actor])
                else:
                    ret[actor] = data[actor]

            ret['Others'] = others
            return ret

        actor = actors[0]
        messages = data[actor]

        new_data: DefaultDict[str, List[Message]] = defaultdict(list)

        with Progress() as progress:
            for m in progress.track(messages, description='Sorting...'):
                new_data[m.created_at.strftime('%B %Y')].append(m)

        return dict(new_data)

    for chat in chats:
        ret[chat] = sort(chat.messages)

    return ret


# def _sort_by_groups(chats: List[Chat]) -> Data:
#     choices = ['All', 'Choose a specific group']
#     selected = select('Which groups should be selected?', choices).ask()

#     if selected == 'All':
#         return {chat: chat.messages for chat in chats}

#     choices = [chat.filename for chat in chats]
#     groups = checkbox('Choose a group:', choices).ask()

#     if not groups:
#         log('error', 'No groups were selected. Aborting.')
#         return {chat: None for chat in chats}

#     return {chat: chat.messages for chat in chats if chat.filename in groups}

# def _sort_by_time_ignore_groups(chats: List[Chat]) -> Data:
    


def modes(func: Callable[..., None]):
    """
    """

    # Hack to avoid circular imports.
    from .frames import BaseFrame    

    def decorator(self: BaseFrame, chats: List[Chat]) -> None:
        modes = {'By Time': _sort_by_time, 'By Actor': _sort_by_actor}
        name = select('Now, choose your mode:', modes).ask()

        try:
            sorted_messages = modes[name](chats)
        except (KeyError, TypeError):
            return log('error', 'Option not selected. Aborting.')

        func(self, sorted_messages)

    return decorator


# def sort_by_frames(func: Callable[..., None]):
#     """
#     """

#     # Hack to avoid circular imports.
#     from .frames import BaseFrame 

#     def decorator(self: BaseFrame, chats: List[Chat]) -> None:
#         modes = {
#             'By Time': _sort_by_time,
#             'By Groups': _sort_by_groups,
#         }

#         name = select('Now, choose your frame type:', modes).ask()
#         mode = modes[name]

#         sorted_messages = mode(chats)
        
#         if None in sorted_messages.values():
#             return
        
#         func(self, sorted_messages)

#     return decorator


def wordcloud(func: Callable[..., None]):
    """
    """

    # Hack to avoid circular imports.
    from .frames import BaseFrame

    def decorator(self: BaseFrame, chats: List[Chat]) -> None:
        data: Dict[Chat, List[Message]] = {}

        for chat in chats:
            messages: List[Message] = []

            for message in chat.messages:
                if message['Type'] is not MessageType.default:
                    continue

                messages.append(message)
            data[chat] = messages

        func(self, data)

    return decorator
