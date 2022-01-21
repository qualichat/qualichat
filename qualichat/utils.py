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

import json
import logging
import os
import random
from pathlib import Path
from typing import Any, Dict, List, Literal
from functools import cache

from tldextract import extract # type: ignore


__all__ = ('config',)


class Config:
    """
    """

    __slots__ = ('data')

    def __init__(self) -> None:
        self.data = self.load()

    def __contains__(self, item: str) -> bool:
        return item in self.data

    def __getitem__(self, item: str) -> Any:
        return self.data[item]

    def __setitem__(self, key: str, value: Any) -> None:
        self.data[key] = value

    def load(self) -> Dict[str, Any]:
        home = Path.home()

        folder = home / '.qualichat'
        config = folder / 'config.json'

        if not folder.is_dir():
            folder.mkdir(exist_ok=True)

            with config.open('w', encoding='utf-8') as file:
                file.write(r'{}')

            return {}

        with config.open('r', encoding='utf-8') as file:
            return json.load(file)

    def save(self) -> None:
        home = Path.home()

        folder = home / '.qualichat'
        config = folder / 'config.json'

        with config.open('w', encoding='utf-8') as file:
            json.dump(self.data, file, indent=2, sort_keys=True)


def _get_all_names() -> List[str]:
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


names = _get_all_names()
config = Config()


logger = logging.getLogger('qualichat')


def log(
    level: Literal['debug', 'info', 'warn', 'error'], message: str
) -> None:
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


domains: Dict[str, str] = {
    'youtu.be': 'YouTube',
    'youtube.com': 'YouTube',
    'whatsapp.com': 'WhatsApp',
    't.me': 'Telegram',
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
    'gazetadopovo.com.br': 'Gazeta do Povo',
    'fb.me': 'Facebook',
    'fb.watch': 'Facebook',
    't.co': 'Twitter',
    'goo.gl': 'Google',
    'www.gov.br': 'Governo do Brasil',
}


@cache
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
