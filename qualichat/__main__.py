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
from typing import Tuple, List, Dict

from colorama import Fore
from enquiries.choices import choose # type: ignore

import qualichat
from .features import BaseFeature, generate_chart


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


prefix = GREEN + '[qualichat]' + RESET
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


def _print(*messages: str):
    print(f'{prefix} {" ".join(messages)}')


def loadchat(parser: argparse.ArgumentParser, args: argparse.Namespace):
    qc = qualichat.load_chats(args.path)

    features: Dict[str, BaseFeature] = {
        'Messages Feature': qc.messages,
        'Time Feature': qc.time,
        'Nouns Feature': qc.nouns,
        'Verbs Feature': qc.verbs,
        'Emojis Feature': qc.verbs
    }

    print(qc_ascii)
    _print('Welcome to Qualichat.')

    options = list(features.keys())
    choice: str = choose(f'Choose your feature.', options) # type: ignore

    feature = features[choice]
    # methods = _get_methods_with_decorator(type(feature), 'generate_chart')

    # print(methods)


def add_loadchat_args(subparser): # type: ignore
    parser = subparser.add_parser('load', help='loads the given chat') # type: ignore
    parser.set_defaults(func=loadchat) # type: ignore

    parser.add_argument('path', help='the path of the chat') # type: ignore


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
