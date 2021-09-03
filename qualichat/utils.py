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

from __future__ import annotations

import logging
import sys
import json
import os
import random
from typing import Callable, Dict, List, Any, Union, Optional, Literal
from pathlib import Path

from curtsies import CursorAwareWindow, FSArray, fsarray, Input # type: ignore
from curtsies.formatstring import FmtStr # type: ignore
from curtsies.fmtfuncs import bold # type: ignore
from tldextract import extract # type: ignore


__all__ = ('log', 'progress_bar', 'parse_domain')


logger = logging.getLogger('qualichat')
Levels = Literal['debug', 'info', 'warn', 'error']


def log(level: Levels, message: str) -> None:
    """Logs a message to ``qualichat`` logger.

    Parameters
    ----------
    level: :class:`str`
        The logging level to send. It must be one of these: `debug`,
        `info`, `warn`, `error`.
    message: :class:`str`
        The message content to send.
    """
    getattr(logger, level)(message)


def get_config() -> Dict[str, Dict[str, str]]:
    home = Path.home()

    folder = home / '.qualichat'
    config = folder / 'config.json'

    if not folder.is_dir():
        log('debug', 'Creating <color>.qualichat<reset> folder.')
        folder.mkdir(exist_ok=True)

        with config.open('w', encoding='utf-8') as f:
            f.write(r'{}')

        return {}

    with config.open('r', encoding='utf-8') as f:
        return json.load(f)


def save_config() -> None:
    log('debug', 'Saving configuration file...')
    home = Path.home()

    folder = home / '.qualichat'
    file = folder / 'config.json'

    with file.open('w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, sort_keys=True)


config = get_config()


def get_all_names() -> List[str]:
    path = os.path.dirname(__file__)
    books = os.path.join(path, 'books.txt')

    with open(books, encoding='utf-8') as f:
        return f.read().split('\n')


def get_random_name() -> str:
    name = random.choice(names)
    # Remove the book from the list so there is no risk that two 
    # actors have the same display name.
    names.remove(name)
    return name.strip()


names = get_all_names()


Choices = Union[List[str], Dict[str, Any]]
no_format: Callable[[str], str] = lambda x: x


class Choice:
    __slots__ = ('key', 'display', 'selected')

    def __init__(self, key: str, *, display: Any = None) -> None:
        self.key: str = key
        self.display: Any = display
        self.selected: bool = False

    @property
    def value(self) -> Any:
        return self.display or self.key

    def render(self, format: Callable[[str], Union[str, FmtStr]]) -> FSArray:
        return fsarray([format(line) for line in self.key.split('\n')])


class Menu:
    __slots__ = ('prompt', 'choices', 'multi', 'before', 'after', '_index')

    def __init__(
        self,
        prompt: str,
        choices: Choices,
        *,
        multi: bool = False,
        before: Optional[Callable[[], Any]] = None,
        after: Optional[Callable[..., Any]] = None
    ) -> None:
        self.prompt: str = prompt
        self.choices: List[Choice]
        self.multi: bool = multi
        self.before: Optional[Callable[[], Any]] = before
        self.after: Optional[Callable[..., Any]] = after

        if isinstance(choices, dict):
            self.choices = [Choice(k, display=v) for k, v in choices.items()]
        else:
            self.choices = [Choice(k) for k in choices]

        if self.before:
            self.choices.append(Choice('Back'))

        self._index = 0

    def __len__(self) -> int:
        return len(self.choices)

    def run(self) -> Any:
        callback: Callable[..., Any] = lambda x: x
        options = dict(out_stream=sys.stderr, extra_bytes_callback=callback)
        
        with CursorAwareWindow(**options) as window:
            options = self.start(window)

        if self.before and self.choices[self._index] == self.choices[-1]:
            return self.before()

        if self.after:
            return self.after(options)

        return options

    def start(self, window: CursorAwareWindow) -> Any:
        array = self.render(window.width)
        window.render_to_terminal(array)

        if self.prompt:
            log('info', self.prompt)

        try:
            with Input() as listener:
                for key in listener:
                    if key == '<UP>':
                        self._index = max(0, self._index - 1)
                    elif key == '<DOWN>':
                        self._index = min(len(self) - 1, self._index + 1)
                    elif key == '<SPACE>':
                        if self.multi:
                            self.toggle()
                    elif key == '<Ctrl-j>':
                        break
                    else:
                        continue

                    window.render_to_terminal(self.render(window.width))
        except KeyboardInterrupt as error:
            raise error

        return self.get_selection()

    def get_selection(self) -> Any:
        options = [item.value for item in self.choices if item.selected]

        if self.multi:
            return options
        elif options:
            return options[0]
        
        return self.choices[self._index].value
    
    def toggle(self) -> None:
        state = self.choices[self._index]
        state.selected = not state.selected

    def render(self, width: int) -> FSArray:
        array = fsarray([''], width=width)
        rows = len(array)

        for option in self.choices:
            current = self.choices[self._index] == option
            format = bold if current else no_format

            option_array = option.render(format)
            array[rows:rows + len(option_array), 2:width] = option_array

            if self.before and self.choices[-1] == option:
                state = '» '
            else:
                if self.multi:
                    state = '\u25c9 ' if option.selected else '\u25cc '
                else:
                    state = '» ' if current else '  '

            array[rows:rows + 1, 0:2] = fsarray([state])
            rows += len(option_array)

        return array


# TODO: Add return type to this function.
# TODO: Add docstring for this function.
def progress_bar(
    iteration: int,
    total: int,
    prefix: str = 'Progress',
    suffix: str = 'Complete',
    decimals: int = 1,
    length: int = 50,
    fill: str = '█',
    end: str = '\r'
) -> None:
    float_number = 100 * (iteration / float(total))
    percent = ('{0:.' + str(decimals) + 'f}').format(float_number)
    filled = int(length * iteration // total)
    bar = fill * filled + '-' * (length - filled)
    print(f'{prefix} |{bar}| {percent}% {suffix}', end=end)

    if iteration == total:
        print()


domains: Dict[str, str] = {
    'youtu.be': 'YouTube',
    'youtube.com': 'YouTube',
    'whatsapp.com': 'WhatsApp',
    't.me': 'Twitter',
    'uol.com.br': 'UOL',
    'glo.bo': 'Globo',
    'bit.ly': 'Bitly',
    'metropoles': 'Metrópoles',
    'theintercept.com': 'The Intercept',
    'estadao.com.br': 'Estadão',
    'diarioonline.com.br': 'Diário Online',
    'brasildefato.com.br': 'Brasil de Fato',
    'ig.com.br': 'IG',
    'terrabrasilnoticias.com': 'Terra Brasil Notícias',
    'folhadapolitica.com': 'Folha da Política',
    'gazetadopovo.com.br': 'Gazeta do Povo'
}


def parse_domain(url: str) -> str:
    """Parses a URL to return its sanitized domain.

    Parameters
    ----------
    url: :class:`str`
        The URL to be parsed.

    Returns
    -------
    :class:`str`
        The parsed domain name.
    """
    result = extract(url)

    domain: str = result.domain # type: ignore
    suffix: str = result.suffix # type: ignore

    website = f'{domain}.{suffix}'

    if website in domains:
        return domains[website]

    return domain.capitalize()
