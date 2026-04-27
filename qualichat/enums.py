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

import datetime
from enum import Enum, IntEnum
from typing import Dict, Tuple


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


class ChatType(Enum):
    friends    = 'Friends'
    political  = 'Political'
    religious  = 'Religious'
    scientific = 'Scientific'
    scholar    = 'Scholar'
    co_workers = 'Co-workers'
    random     = 'Random'
    family     = 'Family'
    green      = 'Green'
    innovation = 'Innovation'
    health     = 'Health'
    spiritual  = 'Spiritual'
    mentoring  = 'Mentoring'
    wellness   = 'Wellness'
    media      = 'Media'
    brand      = 'Brand'


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


# Per-MessageType detection tokens.
#
# The exact strings WhatsApp emits depend on platform (iOS / Android) and
# locale. These tables cover the most common locales we have evidence for in
# real exports: pt-BR, en, es, de, it, fr. Add to the relevant tuple if you
# encounter a new locale — please prefer the literal string the app emits
# (case-insensitive comparison is applied by ``get_message_type``).
#
# Note: most tokens are matched exactly against the trimmed message body;
# document tokens are also matched as a *suffix* because iOS prefixes them
# with the filename (e.g. ``"report.pdf • 2 pages documento omitido"``).
# The Android generic ``<media omitted>`` / ``<Mídia oculta>`` lines are
# treated as ``image_omitted`` for back-compat with previous releases.
_OMITTED_TOKENS: Dict[MessageType, Tuple[str, ...]] = {
    MessageType.image_omitted: (
        'imagem ocultada', 'imagem oculta',           # pt-BR
        'image omitted',                               # en
        'imagen omitida',                              # es
        'Bild weggelassen',                            # de
        'immagine omessa',                             # it
        'image omise',                                 # fr
        '<Media omitted>',                             # Android (en, generic)
        '<Mídia oculta>',                              # Android (pt-BR)
    ),
    MessageType.gif_omitted: (
        'GIF omitido',                                 # pt-BR
        'GIF omitted',                                 # en
        'GIF omitida', 'GIF omitida.',                 # es
        'GIF ausgeschlossen',                          # de
        'GIF omessa',                                  # it
        'GIF omise',                                   # fr
    ),
    MessageType.video_omitted: (
        'vídeo omitido',                               # pt-BR
        'video omitted',                               # en
        'video omitido',                               # es
        'Video weggelassen',                           # de
        'video omesso',                                # it
        'vidéo omise',                                 # fr
    ),
    MessageType.audio_omitted: (
        'áudio ocultado', 'áudio oculto',              # pt-BR
        'audio omitted',                               # en
        'audio omitido',                               # es
        'Audio weggelassen',                           # de
        'audio omesso',                                # it
        'audio omis',                                  # fr
    ),
    MessageType.sticker_omitted: (
        'figurinha omitida',                           # pt-BR
        'sticker omitted',                             # en
        'pegatina omitida', 'sticker omitido',         # es
        'Sticker weggelassen',                         # de
        'adesivo omesso',                              # it
        'autocollant omis',                            # fr
    ),
    MessageType.document_omitted: (
        'documento omitido',                           # pt-BR / es / it
        'document omitted',                            # en
        'Dokument weggelassen',                        # de
        'document omis',                               # fr
    ),
    MessageType.contact_card_omitted: (
        'Cartão do contato omitido',                   # pt-BR
        'Contact card omitted',                        # en
        'Tarjeta de contacto omitida',                 # es
        'Kontaktkarte weggelassen',                    # de
        'biglietto da visita omesso',                  # it
        'Carte de contact omise',                      # fr
    ),
    MessageType.deleted_message: (
        'Mensagem apagada',                            # pt-BR
        'This message was deleted',                    # en
        'Mensaje eliminado',                           # es
        'Diese Nachricht wurde gelöscht',              # de
        'Questo messaggio è stato eliminato',          # it
        'Ce message a été supprimé',                   # fr
    ),
}

# Build a lower-cased lookup once at import time so detection is cheap.
_OMITTED_LOOKUP: Dict[str, MessageType] = {
    token.casefold(): msg_type
    for msg_type, tokens in _OMITTED_TOKENS.items()
    for token in tokens
}


def get_message_type(content: str) -> MessageType:
    """Classify a message body as a media/system token or as a regular message.

    Recognises platform-/locale-specific strings WhatsApp uses for omitted
    media, deleted messages and the like. Falls back to
    :attr:`MessageType.default` for anything else (i.e. real text content).

    Detection is case-insensitive and tolerates leading/trailing whitespace.
    Document tokens additionally match as a *suffix* because iOS prefixes
    them with the filename.
    """
    if not content:
        return MessageType.default

    normalized = content.strip().casefold()

    # Exact-match against the lookup table (covers most cases).
    if (msg_type := _OMITTED_LOOKUP.get(normalized)) is not None:
        return msg_type

    # iOS document lines are "<filename> ... documento omitido" → suffix match.
    for token in _OMITTED_TOKENS[MessageType.document_omitted]:
        if normalized.endswith(token.casefold()):
            return MessageType.document_omitted

    return MessageType.default
