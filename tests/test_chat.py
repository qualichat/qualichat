"""Tests for qualichat.chat.Chat — multi-format WhatsApp export parsing."""

import datetime
import zipfile
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"

REAL_NAMES = {"Joel", "Mary", "Olivia"}


@pytest.mark.parametrize(
    "filename,min_messages",
    [
        ("ios_old_pt.txt", 8),
        ("ios_new_pt.txt", 8),
        ("android_pt.txt", 8),
        ("android_de.txt", 8),
        ("ios_us_12h.txt", 8),
    ],
)
def test_parses_known_format(filename, min_messages):
    from qualichat.chat import Chat

    chat = Chat(FIXTURES / filename)

    assert len(chat.messages) >= min_messages, (
        f"{filename}: expected >= {min_messages} messages, got {len(chat.messages)}"
    )
    assert len(chat.actors) >= 2, f"{filename}: expected >= 2 actors"
    assert all(m.actor.display_name for m in chat.messages)
    assert all(isinstance(m.created_at, datetime.datetime) for m in chat.messages)


def test_multiline_message_kept_together():
    """Multi-line messages must be merged into a single Message.

    chat-miner concatenates the lines without preserving newlines (its
    documented behaviour), so we check that the content contains the parts.
    """
    from qualichat.chat import Chat

    chat = Chat(FIXTURES / "multi_line.txt")
    long_message = next(
        (m for m in chat.messages if "Primeira linha" in m.content), None
    )
    assert long_message is not None, "Long message starting with 'Primeira linha' not found"
    assert "Segunda linha" in long_message.content
    assert "Terceira linha" in long_message.content
    assert "🚀" in long_message.content


def test_anonymizes_authors():
    from qualichat.chat import Chat

    chat = Chat(FIXTURES / "ios_old_pt.txt")
    display_names = {a.display_name for a in chat.actors}
    assert display_names.isdisjoint(REAL_NAMES), (
        f"Display names leaked real names: {display_names & REAL_NAMES}"
    )


def test_anonymization_persists_across_loads(tmp_path):
    """Loading the same file twice should yield the same display names."""
    from qualichat.chat import Chat

    src = FIXTURES / "ios_new_pt.txt"
    dst = tmp_path / src.name
    dst.write_bytes(src.read_bytes())

    first = Chat(dst)
    first_names = {a.display_name for a in first.actors}

    second = Chat(dst)
    second_names = {a.display_name for a in second.actors}

    assert first_names == second_names


def test_file_not_found_raises():
    from qualichat.chat import Chat

    with pytest.raises(FileNotFoundError):
        Chat(FIXTURES / "does_not_exist.txt")


def test_empty_file_raises_value_error(tmp_path):
    from qualichat.chat import Chat

    empty = tmp_path / "empty.txt"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="No messages"):
        Chat(empty)


def test_garbage_file_raises_value_error(tmp_path):
    from qualichat.chat import Chat

    garbage = tmp_path / "garbage.txt"
    garbage.write_text("this is not a whatsapp export\n" * 50, encoding="utf-8")
    with pytest.raises(ValueError, match="No messages"):
        Chat(garbage)


def test_zip_file_extraction(tmp_path):
    """Chat() should accept a .zip containing _chat.txt (iOS convention)."""
    from qualichat.chat import Chat

    zip_path = tmp_path / "chat.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.write(FIXTURES / "ios_new_pt.txt", arcname="_chat.txt")

    chat = Chat(zip_path)
    assert len(chat.messages) >= 8


def test_zip_file_with_other_txt_name(tmp_path):
    """Android exports may name the file 'WhatsApp Chat with X.txt'."""
    from qualichat.chat import Chat

    zip_path = tmp_path / "chat.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.write(FIXTURES / "android_pt.txt", arcname="WhatsApp Chat with Joel.txt")

    chat = Chat(zip_path)
    assert len(chat.messages) >= 8


def test_message_features_computed():
    """Messages should expose pre-computed lexical features (back-compat with frames.py)."""
    from qualichat.chat import Chat

    chat = Chat(FIXTURES / "ios_new_pt.txt")
    msg_with_link = next(
        (m for m in chat.messages if "https://example.com/foo" in m.content), None
    )
    assert msg_with_link is not None
    assert "https://example.com/foo" in msg_with_link["Qty_char_links"]
    assert msg_with_link["Qty_char_total"] == len(msg_with_link.content)
