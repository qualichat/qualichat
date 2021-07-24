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

import logging
import sys
from typing import Dict

from tldextract import extract # type: ignore
from colorama import AnsiToWin32, Fore


__all__ = ('log', 'parse_domain')


class ColorStreamHandler(logging.StreamHandler):
    """Handler that adds color support to terminal."""

    __slots__ = ('prefix',)

    def __init__(self) -> None:
        self.prefix: str = f'<color>[qualichat]<reset>'
        super().__init__(AnsiToWin32(sys.stderr)) # type: ignore

    def emit(self, record: logging.LogRecord) -> None:
        try:
            colors = {
                'INFO': Fore.GREEN,
                'DEBUG': Fore.CYAN,
                'WARNING': Fore.RED,
                'ERROR': Fore.LIGHTRED_EX
            }

            message = f'{self.prefix} {self.format(record)}'
            message = message.replace('<color>', colors[record.levelname])
            message = message.replace('<reset>', Fore.RESET)

            
            self.stream.write(message + self.terminator) # type: ignore
            self.flush()
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)


logger = logging.getLogger('qualichat')
logger.addHandler(ColorStreamHandler())


def log(level: str, *messages: str) -> None:
    """Log a message to ``qualichat`` logger.
    
    Parameters
    ----------
    level: :class:`str`
        The logger level to send.
    *args: :class:`str`
        The log messages to send.
    """
    for message in messages:
        getattr(logger, level)(message)


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
    """..."""
    float_number = 100 * (iteration / float(total))
    percent = ('{0:.' + str(decimals) + 'f}').format(float_number)
    filled = int(length * iteration // total)
    bar = fill * filled + '-' * (length - filled)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=end)

    if iteration == total:
        print()
