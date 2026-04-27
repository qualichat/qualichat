"""Tests for qualichat.enums.get_message_type — multi-locale detection."""

import pytest

from qualichat.enums import MessageType, get_message_type


@pytest.mark.parametrize(
    "content,expected",
    [
        # pt-BR (iOS)
        ("imagem ocultada",            MessageType.image_omitted),
        ("imagem oculta",              MessageType.image_omitted),
        ("GIF omitido",                MessageType.gif_omitted),
        ("vídeo omitido",              MessageType.video_omitted),
        ("áudio ocultado",             MessageType.audio_omitted),
        ("áudio oculto",               MessageType.audio_omitted),
        ("figurinha omitida",          MessageType.sticker_omitted),
        ("Cartão do contato omitido",  MessageType.contact_card_omitted),
        ("Mensagem apagada",           MessageType.deleted_message),
        # Android (en, generic)
        ("<Media omitted>",            MessageType.image_omitted),
        # Android (pt-BR)
        ("<Mídia oculta>",             MessageType.image_omitted),
        # en
        ("image omitted",              MessageType.image_omitted),
        ("video omitted",              MessageType.video_omitted),
        ("audio omitted",              MessageType.audio_omitted),
        ("sticker omitted",            MessageType.sticker_omitted),
        ("Contact card omitted",       MessageType.contact_card_omitted),
        ("This message was deleted",   MessageType.deleted_message),
        # es
        ("imagen omitida",             MessageType.image_omitted),
        ("Mensaje eliminado",          MessageType.deleted_message),
        # de
        ("Bild weggelassen",           MessageType.image_omitted),
        ("Diese Nachricht wurde gelöscht", MessageType.deleted_message),
        # it
        ("immagine omessa",            MessageType.image_omitted),
        # fr
        ("image omise",                MessageType.image_omitted),
        ("Ce message a été supprimé",  MessageType.deleted_message),
    ],
)
def test_get_message_type_locales(content, expected):
    assert get_message_type(content) == expected


def test_get_message_type_case_insensitive():
    """Detection must be case-insensitive (real exports vary capitalisation)."""
    assert get_message_type("IMAGE OMITTED") == MessageType.image_omitted
    assert get_message_type("Image Omitted") == MessageType.image_omitted
    assert get_message_type("imagem OCULTADA") == MessageType.image_omitted


def test_get_message_type_whitespace_tolerance():
    """Leading/trailing whitespace must not block detection."""
    assert get_message_type("  imagem ocultada  ") == MessageType.image_omitted
    assert get_message_type("\timage omitted\n") == MessageType.image_omitted


def test_get_message_type_document_suffix():
    """iOS document lines look like '<filename> ... documento omitido'."""
    assert get_message_type("relatorio.pdf • 2 pages documento omitido") == \
        MessageType.document_omitted
    assert get_message_type("contract.pdf document omitted") == \
        MessageType.document_omitted


def test_get_message_type_default_for_text():
    """Plain text messages should fall back to default (no false positives)."""
    assert get_message_type("Olá pessoal!") == MessageType.default
    assert get_message_type("Hello everyone!") == MessageType.default
    assert get_message_type("") == MessageType.default
    # Edge case: word "image" inside a sentence should NOT be flagged
    assert get_message_type("I love this image of the sunset") == MessageType.default


def test_get_message_type_empty_string():
    assert get_message_type("") == MessageType.default
