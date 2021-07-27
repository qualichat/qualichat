'''
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
'''

import argparse
import sys
from typing import Tuple, List, Dict, Optional

from colorama import Fore
from enquiries import choose # type: ignore

import qualichat
from .frames import BaseFrame
from .utils import log


GREEN = Fore.GREEN
RESET = Fore.RESET


def show_version():
    entries: List[str] = []
    fmt = 'v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}'

    entries.append('- Python ' + fmt.format(sys.version_info))

    version_info = qualichat.version_info
    entries.append('- Qualichat ' + fmt.format(version_info))
    
    print('\n'.join(entries))


def core(parser: argparse.ArgumentParser, args: argparse.Namespace):
    if args.version:
        show_version()


qc_ascii = '''
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


def loadchat(parser: argparse.ArgumentParser, args: argparse.Namespace):
    qc = qualichat.load_chats(*args.path, debug=args.debug)
    frames: Dict[Optional[str], BaseFrame] = {}

    for attr in dir(qc):
        if attr.startswith('_'):
            continue

        if attr == 'chats':
            continue

        obj: BaseFrame = getattr(qc, attr)
        frames[obj.fancy_name] = obj

    print(qc_ascii)
    log('info', 'Welcome to Qualichat.')

    options = list(frames.keys())
    choice: str = choose(f'Choose your frame:', options) # type: ignore

    frame = frames[choice]
    name_to_key: Dict[str, str] = {}

    for chart_name in frame.charts.keys():
        name = chart_name.replace('_', ' ')
        name = name.capitalize()

        name_to_key[name] = chart_name

    choices: List[str] = choose(f'Great! Now choose a chart:', list(name_to_key.keys()), multi=True)
    log('info', 'Loading charts...')

    for choice in choices:
        getattr(frame, name_to_key[choice])()


def add_loadchat_args(subparser): # type: ignore
    parser = subparser.add_parser('load', help='loads the given chat') # type: ignore
    parser.set_defaults(func=loadchat) # type: ignore

    parser.add_argument('path', help='the path of the chat', nargs='+') # type: ignore
    parser.add_argument('--debug', '-D', help='sets the logging level to debug', action='store_true') # type: ignore


def parse_args() -> Tuple[argparse.ArgumentParser, argparse.Namespace]:
    parser = argparse.ArgumentParser(prog='qualichat', description='Tools for helping with Qualichat')
    parser.add_argument('-v', '--version', action='store_true', help='shows the library version')
    parser.set_defaults(func=core)

    subparser = parser.add_subparsers(dest='subcommand', title='subcommands')
    add_loadchat_args(subparser)

    return parser, parser.parse_args()


def main():
    parser, args = parse_args()
    args.func(parser, args)


if __name__ == '__main__':
    main()
