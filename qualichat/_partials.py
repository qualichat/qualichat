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

from functools import partial

import questionary
from rich.progress import (
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    Progress,
)


# Custom progress bar
spinner = SpinnerColumn()
description = TextColumn("[progress.description]{task.description}")
bar = BarColumn()
percentage = TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
remaining = TimeRemainingColumn()
elapsed = TimeElapsedColumn()

# Partials
progress_bar = partial(
    Progress, spinner, description, bar, percentage, remaining, elapsed
)
input = partial(questionary.text, qmark='[qualichat]')
select = partial(questionary.select, qmark='[qualichat]')
checkbox = partial(questionary.checkbox, qmark='[qualichat]')
password = partial(questionary.password, qmark='[qualichat]')