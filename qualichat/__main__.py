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

import sys
import logging
import argparse
import platform
from datetime import datetime
from functools import partial
from collections import defaultdict
from typing import Callable, Tuple, List, DefaultDict, Dict, Optional

import plotly # type: ignore
import colorama
import questionary
from colorama import Fore, Style, AnsiToWin32
from rich.style import Style as RichStyle
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn
)

import qualichat
from .utils import log
from .models import Message
from .frames import BaseFrame


BLACK  = Fore.BLACK
BRIGHT = Style.BRIGHT
RESET  = Style.RESET_ALL

logging_colors = {'INFO': Fore.YELLOW, 'DEBUG': Fore.CYAN, 'ERROR': Fore.RED}


Messages = Dict[str, List[Message]]


class ColorStreamHandler(logging.StreamHandler):
    """Handler that adds color support to terminal."""

    def __init__(self) -> None:
        super().__init__(AnsiToWin32(sys.stderr)) # type: ignore

    def format(self, record: logging.LogRecord) -> str:
        now = datetime.now()
        time = f'{BLACK}{BRIGHT}{now.strftime("%H:%M:%S")}{RESET}'

        COLOR = logging_colors[record.levelname]
        level = f'{COLOR}[{record.levelname}]{RESET}'

        return f'{time} {level} {record.getMessage()}'


def show_version() -> None:
    entries: List[str] = []
    formatter = 'v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}'

    entries.append(f'- Python {formatter.format(sys.version_info)}')
    entries.append(f'- Qualichat {formatter.format(qualichat.version_info)}')
    entries.append(f'- Plotly {plotly.__version__}')
    entries.append(f'- Colorama {colorama.__version__}') # type: ignore

    uname = platform.uname()
    entries.append('- System info: {0.system} {0.release}'.format(uname))

    print('\n'.join(entries))


def core(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.version:
        show_version()


ascii = '''
                                ████   ███           █████                 █████   
                               ░░███  ░░░           ░░███                 ░░███    
  ████████ █████ ████  ██████   ░███  ████   ██████  ░███████    ██████   ███████  
 ███░░███ ░░███ ░███  ░░░░░███  ░███ ░░███  ███░░███ ░███░░███  ░░░░░███ ░░░███░   
░███ ░███  ░███ ░███   ███████  ░███  ░███ ░███ ░░░  ░███ ░███   ███████   ░███    
░███ ░███  ░███ ░███  ███░░███  ░███  ░███ ░███  ███ ░███ ░███  ███░░███   ░███ ███
░░███████  ░░████████░░████████ █████ █████░░██████  ████ █████░░████████  ░░█████ 
 ░░░░░███   ░░░░░░░░  ░░░░░░░░ ░░░░░ ░░░░░  ░░░░░░  ░░░░ ░░░░░  ░░░░░░░░    ░░░░░  
     ░███                                                                          
     █████                                                                         
    ░░░░░                                                                          
'''


select = partial(questionary.select, qmark='[qualichat]')
checkbox = partial(questionary.checkbox, qmark='[qualichat]')


progress_bar = Progress(
    SpinnerColumn(),
    TextColumn('[progress.description]{task.description}'),
    BarColumn(complete_style=RichStyle(color='red')),
    TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
    TimeRemainingColumn(),
    TimeElapsedColumn()
)


def sort_by_time(messages: List[Message]) -> Optional[Messages]:
    data: DefaultDict[str, List[Message]] = defaultdict(list)

    with progress_bar as progress:
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


def sort_by_actor(messages: List[Message]) -> Optional[Messages]:
    data: DefaultDict[str, List[Message]] = defaultdict(list)

    with progress_bar as progress:
        for message in progress.track(messages, description='Sorting...'):
            data[message.actor.display_name].append(message)

    choices = ['All', 'Choose a specific actor']
    selected = select('Which actors should be selected?', choices).ask()

    if selected == 'All':
        return dict(data)

    selected_actors = checkbox('Choose an actor:', data).ask()

    if not selected_actors:
        log('error', 'No actors were selected. Aborting.')
        return None
    
    return {actor: data[actor] for actor in selected_actors}


def loadchat(
    parser: argparse.ArgumentParser,
    args: argparse.Namespace
) -> None:
    debug = args.debug
    api_key = args.api_key

    qc = qualichat.load_chats(*args.paths, debug=debug, api_key=api_key)

    print(ascii)
    log('info', 'Welcome to Qualichat.')

    while True:
        frame_name: str = select('Please, choose a frame:', qc.frames).ask()

        if not frame_name:
            return log('error', 'Operation canceled')

        frame: BaseFrame = qc.frames[frame_name]

        message = 'Now, choose your charts:'
        names: List[str] = checkbox(message, frame.charts).ask()

        if not names:
            return log('error', 'No charts were selected. Aborting.')

        modes = {'By Time': sort_by_time, 'By Actor': sort_by_actor}

        mode_name: str = select('Now, choose your sorting mode:', modes).ask()
        mode: Callable[[List[Message]], Optional[Messages]] = modes[mode_name]

        sorted_messages = {chat.filename: mode(chat.messages) for chat in qc.chats}

        for name in names:
            frame.charts[name](sorted_messages)

        log('info', 'Restarting menu...')


def add_loadchat_args(
    subparser: argparse._SubParsersAction # type: ignore
) -> None:
    parser_help = 'starts an interactive session with Qualichat'
    parser = subparser.add_parser('load', help=parser_help) # type: ignore
    parser.set_defaults(func=loadchat)

    path_arg_help = 'the paths to the chats'
    parser.add_argument('paths', help=path_arg_help, nargs='+') # type: ignore

    debug_args = ('-d', '--debug')
    debug_arg_help = 'set the logging level to debug'
    parser.add_argument(*debug_args, help=debug_arg_help, action='store_true')

    api_key_args = ('-k', '--api-key')
    api_key_arg_help = 'set the YouTube API Key for video ratings'
    parser.add_argument(*api_key_args, help=api_key_arg_help, action='store')


def parse_args() -> Tuple[argparse.ArgumentParser, argparse.Namespace]:
    desc = 'Tools for using Qualichat.'
    parser = argparse.ArgumentParser(prog='qualichat', description=desc)

    help = 'show the library version'
    parser.add_argument('-v', '--version', action='store_true', help=help)
    parser.set_defaults(func=core)

    subparser = parser.add_subparsers(dest='subcommand', title='subcommands')
    add_loadchat_args(subparser)

    return parser, parser.parse_args()


def main() -> None:
    logger = logging.getLogger('qualichat')
    logger.addHandler(ColorStreamHandler())

    parser, args = parse_args()
    args.func(parser, args)


if __name__ == '__main__':
    main()
