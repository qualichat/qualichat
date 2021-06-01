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

import datetime
from enum import Enum


class Period(Enum):
    dawn    = 'Dawn'
    morning = 'Morning'
    evening = 'Evening'
    night   = 'Night'


class SubPeriod(Enum):
    resting            = 'Resting'
    transport_morning  = 'Transport (morning)'
    work_morning       = 'Work (morning)'
    lunch              = 'Lunch'
    work_evening       = 'Work (evening)'
    transport_evening  = 'Transport (evening)'
    second_office_hour = 'Second Office Hour'


def _get_period(created_at: datetime.datetime) -> Period:
    if 0 <= created_at.hour < 6:
        period = Period.dawn
    elif 6 <= created_at.hour < 12:
        period = Period.morning
    elif 12 <= created_at.hour < 18:
        period = Period.evening
    else:
        period = Period.night

    return period


def _get_sub_period(created_at: datetime.datetime) -> SubPeriod:
    if 0 <= created_at.hour < 6:
        sub_period = SubPeriod.resting
    elif 6 <= created_at.hour < 9:
        sub_period = SubPeriod.transport_morning
    elif 9 <= created_at.hour < 12:
        sub_period = SubPeriod.work_morning
    elif 12 <= created_at.hour < 15:
        sub_period = SubPeriod.lunch
    elif 15 <= created_at.hour < 18:
        sub_period = SubPeriod.work_evening
    elif 18 <= created_at.hour < 21:
        sub_period = SubPeriod.transport_evening
    else:
        sub_period = SubPeriod.second_office_hour

    return sub_period

