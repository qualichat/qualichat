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
from enum import Enum, IntEnum


__all__ = ('Period', 'SubPeriod', 'MessageType')


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


class MessageType(IntEnum):
    default              = 0
    gif_omitted          = 1
    image_omitted        = 2
    video_omitted        = 3
    audio_omitted        = 4
    sticker_omitted      = 5
    document_omitted     = 6
    contact_card_omitted = 7
    deleted_message      = 8


def get_period(created_at: datetime.datetime) -> Period:
    if 0 <= created_at.hour < 6:
        period = Period.dawn
    elif 6 <= created_at.hour < 12:
        period = Period.morning
    elif 12 <= created_at.hour < 18:
        period = Period.evening
    else:
        period = Period.night

    return period


def get_sub_period(created_at: datetime.datetime) -> SubPeriod:
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


def get_message_type(content: str) -> MessageType:
    if content == 'image omitted':
        message_type = MessageType.image_omitted
    elif content == 'GIF omitted':
        message_type = MessageType.gif_omitted
    elif content == 'video omitted':
        message_type = MessageType.video_omitted
    elif content == 'audio omitted':
        message_type = MessageType.audio_omitted
    elif content == 'sticker omitted':
        message_type = MessageType.sticker_omitted
    elif content.endswith('document omitted'):
        message_type = MessageType.document_omitted
    elif content == 'Contact card omitted':
        message_type = MessageType.contact_card_omitted
    elif content == 'This message was deleted.':
        message_type = MessageType.deleted_message
    else:
        message_type = MessageType.default

    return message_type
