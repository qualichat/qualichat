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

import datetime as _dt
import tempfile
import zipfile
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List, Tuple, Union

from chatminer.chatparsers import WhatsAppParser
from dateutil import parser as _datetimeparser  # transitive dep of chat-miner

from .models import Actor, Message, SystemMessage
from .utils import config, get_random_name, log


__all__ = ('Chat',)


# Invisible characters frequently seen in WhatsApp exports (LRM, NBSP, etc.).
# Stripped before delegating to chat-miner so its regex-based detection is not
# thrown off by directional marks injected by iOS.
_IMPURITIES = (
    ('‎', ''),    # Left-to-Right Mark
    (' ', ''),    # En space
    ('‬', ''),    # Pop Directional Formatting
    ('‪', ''),    # Left-to-Right Embedding
    ('\xa0', ' '),     # No-Break Space → space
    ('‑', '-'),   # Non-breaking hyphen → hyphen
)


def _clean_text(content: str) -> str:
    for old, new in _IMPURITIES:
        content = content.replace(old, new)
    return content


@contextmanager
def _cleaned_copy(src: Path) -> Iterator[Path]:
    """Yield a temp file with WhatsApp invisible chars stripped from `src`."""
    raw = src.read_text(encoding='utf-8')
    cleaned = _clean_text(raw)

    fd, name = tempfile.mkstemp(suffix='.txt', prefix='qualichat_')
    tmp = Path(name)
    try:
        with open(fd, 'w', encoding='utf-8', newline='') as f:
            f.write(cleaned)
        yield tmp
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass


def _extract_txt_from_zip(zip_path: Path, dest: Path) -> Path:
    """Extract the chat .txt from a WhatsApp .zip export.

    Prefers ``_chat.txt`` (iOS convention); falls back to the first ``.txt``
    found in the archive (Android may name it ``WhatsApp Chat with X.txt``).
    """
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        candidates = [n for n in names if n.lower().endswith('.txt')]
        if not candidates:
            raise ValueError(f'No .txt file found inside {zip_path.name!r}')

        chosen = next(
            (n for n in candidates if Path(n).name.lower() == '_chat.txt'),
            candidates[0],
        )
        zf.extract(chosen, path=str(dest))
        return dest / chosen


class _CapturingWhatsAppParser(WhatsAppParser):
    """``WhatsAppParser`` subclass that ALSO retains system events.

    Upstream chat-miner returns ``None`` for any line that lacks an
    ``Author: body`` separator — group lifecycle events ("Bob added you",
    "Jimbo left", "Loris created group X"), media-omitted lines and so on
    are dropped silently. We override :meth:`_parse_message` so that
    whenever the upstream parser would skip a system event, we re-parse
    just enough to recover ``(timestamp, body)`` and stash it in
    ``self.system_events``.

    Self-destroying messages (``Author:.``) remain skipped: they carry no
    useful body.
    """

    def __init__(self, filepath: str) -> None:
        super().__init__(filepath)
        self.system_events: List[Tuple[_dt.datetime, str]] = []

    def _parse_message(self, mess: str):  # type: ignore[override]
        result = super()._parse_message(mess)
        if result is not None:
            return result

        # super() returned None: either system event or self-destroying.
        try:
            datestr, author_and_body = mess.split(self._datefmt.date_author_sep, 1)
        except ValueError:
            return None

        # Skip self-destroying ("X:.") and any line that does have a real
        # author separator (defensive — super() should have already taken it).
        if ': ' in author_and_body or ':.' in author_and_body:
            return None

        try:
            time = _datetimeparser.parse(
                datestr, dayfirst=self._datefmt.is_dayfirst, fuzzy=True,
            )
        except (ValueError, TypeError, OverflowError):
            return None

        body = author_and_body.strip()
        if body:
            self.system_events.append((time, body))
        return None


class Chat:
    """Represents a WhatsApp chat export.

    Parameters
    ----------
    path: Union[:class:`str`, :class:`pathlib.Path`]
        Path to a WhatsApp chat export. Accepts:

        - ``.txt`` plain export (Android, iOS, any locale supported by
          `chat-miner <https://github.com/joweich/chat-miner>`_)
        - ``.zip`` archive containing a chat ``.txt`` file (e.g. iOS export
          with attached media)

    Attributes
    ----------
    path: :class:`pathlib.Path`
        Resolved absolute path of the export file.
    filename: :class:`str`
        Basename of the export.
    messages: List[:class:`.Message`]
        User messages, in chronological order.
    system_messages: List[:class:`.SystemMessage`]
        Group lifecycle events (someone joined/left, group renamed,
        end-to-end notice, etc.) recovered from the export. Self-destroying
        messages are not included.
    """

    __slots__ = ('path', 'filename', 'messages', 'system_messages', '_actors')

    def __init__(self, path: Union[str, Path], **kwargs: Any) -> None:
        if not isinstance(path, Path):
            path = Path(path)

        if not path.is_file():
            raise FileNotFoundError(f'no such file: {str(path)!r}')

        self.path = path.resolve()
        self.filename = self.path.name

        log_name = f'[green]{self.path}[/]'
        log('info', f'Loading chat {log_name}...')

        df, system_events = self._parse(self.path)

        self.messages: List[Message] = []
        self.system_messages: List[SystemMessage] = [
            SystemMessage(body, ts) for ts, body in system_events
        ]
        self._actors: Dict[str, Actor] = {}

        path_key = str(self.path)
        if path_key not in config:
            config[path_key] = {}
        group: Dict[str, str] = config[path_key]

        for row in df.itertuples(index=False):
            contact_name = str(row.author)

            if contact_name not in self._actors:
                if contact_name not in group:
                    group[contact_name] = get_random_name()
                self._actors[contact_name] = Actor(group[contact_name])

            actor = self._actors[contact_name]
            message = Message(actor, str(row.message), row.timestamp)

            self.messages.append(message)
            actor.messages.append(message)

        config.save()

        log(
            'info',
            f'Loaded {len(self.messages):,} messages '
            f'({len(self.system_messages):,} system events) and '
            f'{len(self._actors):,} actors from {log_name}.',
        )

    @staticmethod
    def _parse(path: Path):
        """Run chat-miner against a (possibly zipped, possibly dirty) export.

        Returns a tuple ``(user_messages_df, system_events)`` where
        ``system_events`` is a list of ``(timestamp, body)`` tuples.
        """
        with ExitStack() as stack:
            if path.suffix.lower() == '.zip':
                tmpdir = Path(stack.enter_context(
                    tempfile.TemporaryDirectory(prefix='qualichat_zip_')
                ))
                source = _extract_txt_from_zip(path, tmpdir)
            else:
                source = path

            cleaned = stack.enter_context(_cleaned_copy(source))

            parser = _CapturingWhatsAppParser(str(cleaned))
            try:
                parser.parse_file()
                df = parser.parsed_messages.get_df(as_pandas=True)
            except (IndexError, ValueError) as exc:
                # chat-miner raises IndexError when no message line matches
                # (empty or unrecognised file). Translate to a useful error.
                raise ValueError(
                    f"No messages parsed from {path.name!r}. "
                    "Verify the file is a valid WhatsApp .txt export "
                    "(Android or iOS, any supported locale)."
                ) from exc

            system_events = list(parser.system_events)

        if df.empty:
            raise ValueError(
                f"No messages parsed from {path.name!r}. "
                "Verify the file is a valid WhatsApp .txt export "
                "(Android or iOS, any supported locale)."
            )

        return df, system_events

    @property
    def actors(self) -> List[Actor]:
        """List[:class:`.Actor`]: The list of actors present in the chat."""
        return list(self._actors.values())

    def __repr__(self) -> str:
        return (
            f'<Chat filename={self.filename!r} '
            f'actors={len(self._actors)} '
            f'messages={len(self.messages)} '
            f'system_messages={len(self.system_messages)}>'
        )
