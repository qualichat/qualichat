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

import logging
import sys
import platform
from typing import List, Tuple
from argparse import ArgumentParser, Namespace, Action

import plotly # type: ignore
import spacy
from rich import print
from rich.logging import RichHandler
from spacy.cli.download import download

import qualichat
from ._partials import *
from qualichat.frames import BaseFrame
from qualichat.utils import config, log


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


def show_version() -> None:
    entries: List[str] = []
    formatter = 'v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}'

    entries.append(f'- Python {formatter.format(sys.version_info)}')
    entries.append(f'- Qualichat {formatter.format(qualichat.version_info)}')
    entries.append(f'- Plotly {plotly.__version__}')
    entries.append(f'- spaCy {spacy.__version__}') # type: ignore

    uname = platform.uname()
    entries.append('- System info: {0.system} {0.release}'.format(uname))

    print('\n'.join(entries))


def core(parser: ArgumentParser, args: Namespace) -> None:
    if args.version:
        show_version()


def loadchat(parser: ArgumentParser, args: Namespace) -> None:
    debug = args.debug
    qc = qualichat.load_chats(*args.paths, debug=debug)

    print(ascii)
    log('info', 'Welcome to Qualichat.')

    while True:
        choices = list(qc.frames.keys())
        frame_name: str = select('Choose a frame:', choices).ask()

        if not frame_name:
            return log('error', 'Operation canceled. Aborting.')

        frame: BaseFrame = qc.frames[frame_name]

        choices = list(frame.charts.keys())
        names = checkbox('Choose your charts:', choices).ask()

        if not names:
            return log('error', 'No charts were selected. Aborting.')

        for name in names:
            frame.charts[name](qc.chats)

        log('info', 'Restarting menu...')


def setup(parser: ArgumentParser, args: Namespace) -> None:
    api_key = password('Enter your Google API key:').ask()

    config['google_api_key'] = api_key
    config.save()

    with progress_bar(transient=True) as progress:
        progress.add_task('[green]Downloading spaCy models', start=False)
        download('pt_core_news_md', False, False, '-q')

    print('\n[green]✔ You can now use Qualichat.[/green]')


def add_loadchat_args(subparser: Action) -> None:
    parser_help = 'start an interactive session with Qualichat'
    parser = subparser.add_parser('load', help=parser_help) # type: ignore
    parser.set_defaults(func=loadchat) # type: ignore

    path_arg_help = 'the paths for the chats'
    parser.add_argument('paths', help=path_arg_help, nargs='+') # type: ignore

    debug_args = ('-d', '--debug')
    debug_args_help = 'set the logging level to debug'
    parser.add_argument( # type: ignore
        *debug_args, help=debug_args_help, action='store_true'
    )


def add_setup_args(subparser: Action) -> None:
    parser_help = 'setup internal libraries'
    parser = subparser.add_parser('setup', help=parser_help) # type: ignore
    parser.set_defaults(func=setup) # type: ignore


def parse_args() -> Tuple[ArgumentParser, Namespace]:
    desc = 'Tools for using Qualichat.'
    parser = ArgumentParser(prog='qualichat', description=desc)

    help = 'show the library version'
    parser.add_argument('-v', '--version', action='store_true', help=help)
    parser.set_defaults(func=core)

    subparser = parser.add_subparsers(dest='subcommand', title='subcommands')
    add_loadchat_args(subparser)
    add_setup_args(subparser)

    return (parser, parser.parse_args())


def main() -> None:
    handler = RichHandler(
        omit_repeated_times=False, show_path=False, markup=True
    )

    logger = logging.getLogger('qualichat')
    logger.addHandler(handler)

    parser, args = parse_args()
    args.func(parser, args)


if __name__ == '__main__':
    main()
