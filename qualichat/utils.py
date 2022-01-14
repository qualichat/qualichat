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
from pathlib import Path
from typing import Any, Dict


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


config = Config()
