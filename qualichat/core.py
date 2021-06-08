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

import pathlib
from typing import Union

from .chat import Qualichat


def load_chat(path: Union[str, pathlib.Path], *, encoding: str = 'utf-8') -> Qualichat:
    """Loads a chat from a plain text file.

    Parameters
    ----------
    path: Union[:class:`str`, :class:`pathlib.Path`]
        The path to the file.
        The file must be in plain text format.
    encoding: :class:`str`
        The encoding that will be used in the text,
        by default ``'utf-8'``.

    Returns
    -------
    :class:`.Qualichat`
        The object that will be used for analysis of the chat.

    Raises
    ------
    :class:`FileNotFoundError`
        If the file has not been found.
    """
    return Qualichat(path, encoding=encoding)
