"""Tests for qualichat.utils — anonymisation pool exhaustion."""

import pytest


def test_get_random_name_returns_from_pool():
    """When the pool has names, get_random_name returns and consumes one."""
    from qualichat import utils

    initial_size = len(utils.names)
    assert initial_size > 0

    name = utils.get_random_name()
    assert isinstance(name, str)
    assert name  # not empty
    assert len(utils.names) == initial_size - 1


def test_get_random_name_does_not_raise_when_pool_exhausted():
    """A chat with more actors than `books.txt` lines must not crash mid-load."""
    from qualichat import utils

    # Force exhaustion
    utils.names.clear()
    utils._exhaustion_counter = 0

    a = utils.get_random_name()
    b = utils.get_random_name()
    c = utils.get_random_name()

    assert a == "Actor #1"
    assert b == "Actor #2"
    assert c == "Actor #3"

    # All three must be unique
    assert len({a, b, c}) == 3


def test_get_random_name_unique_within_pool():
    """While the pool has names, every call must return a different name."""
    from qualichat import utils

    seen = set()
    n = min(50, len(utils.names))
    for _ in range(n):
        name = utils.get_random_name()
        assert name not in seen, f"Duplicate display name returned: {name!r}"
        seen.add(name)
