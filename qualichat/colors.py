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

from typing import Dict, List


__all__ = ('BARS', 'LINES')


BARS: Dict[int, List[str]] = {
    1: ['#08bcac'],
    2: ['#08bcac', '#38444c'],
    3: ['#fe9666', '#8ad4eb', '#666666'],
    4: ['#f2c80f', '#fd625e', '#8ad4eb', '#b887ad'],
    7: ['#796408', '#374649', '#808080', '#a66999', '#fe9666', '#fae99f', '#f5d33f']
}

LINES: Dict[int, List[str]] = {
    0: ['#ff645c'],
    1: ['#000000'],
    2: ['#ff645c', '#f8cc0c'],
    3: ['#08bcac'],
    4: ['#000000'],
    7: ['#01b8aa']
}
