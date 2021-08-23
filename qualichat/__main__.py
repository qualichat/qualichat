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

import argparse
from qualichat.frames import BaseFrame
import sys
import platform
from typing import Any, Callable, Dict, Tuple, List

import plotly # type: ignore
import colorama

import qualichat
from .utils import log, Menu
from .frames import sort_by_day, sort_by_month


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


# "qualichat load [...]" command.

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


def loadchat(
    parser: argparse.ArgumentParser,
    args: argparse.Namespace
) -> None:
    qc = qualichat.load_chats(*args.paths, debug=args.debug)
    frames = {f.fancy_name: f for f in qc.frames}

    print(ascii)
    log('info', 'Welcome to Qualichat.')

    def frames_menu():
        menu = Menu('Please, choose your frame:', frames, after=charts_menu)
        menu.run()

    def charts_menu(frame: BaseFrame):
        charts: Dict[str, Callable[..., Any]] = {}

        for chart_name, method in frame.charts.items():
            name = chart_name.replace('_', ' ')
            name = name.capitalize()
            charts[name] = method

        message = f'Great! Now, please, choose a chart:'

        menu = Menu(message, charts, multi=True, before=frames_menu)
        charts = menu.run()

        if not charts:
            return log('info', 'No charts were selected. Closing...')

        modes = {'By day': sort_by_day, 'By month': sort_by_month}

        menu = Menu('Please, choose your time sorting mode:', modes)
        sorting_mode = menu.run()

        for chart in charts:
            chart(sorting_mode) # type: ignore

    frames_menu()


def add_loadchat_args(subparser) -> None: # type: ignore
    parser_help = 'Loads the given chat.'
    parser = subparser.add_parser('load', help=parser_help) # type: ignore
    parser.set_defaults(func=loadchat) # type: ignore

    path_arg_help = 'The paths to the chats.'
    parser.add_argument('paths', help=path_arg_help, nargs='+') # type: ignore

    debug_arg_help = 'Sets the logging level to debug.'
    parser.add_argument( # type: ignore
        '-d', '--debug',
        help=debug_arg_help,
        action='store_true'
    )


def parse_args() -> Tuple[argparse.ArgumentParser, argparse.Namespace]:
    desc = 'Tools for using Qualichat.'
    parser = argparse.ArgumentParser(prog='qualichat', description=desc)

    help = 'Shows the library version.'
    parser.add_argument('-v', '--version', action='store_true', help=help)
    parser.set_defaults(func=core)

    subparser = parser.add_subparsers(dest='subcommand', title='subcommands')
    add_loadchat_args(subparser)

    return parser, parser.parse_args()


def main() -> None:
    parser, args = parse_args()
    args.func(parser, args)


if __name__ == '__main__':
    main()
