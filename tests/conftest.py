import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def isolated_home(monkeypatch, tmp_path):
    """Each test gets a fake HOME so ~/.qualichat/config.json is isolated."""
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("HOME", str(tmp_path))
    import qualichat.utils
    qualichat.utils.config = qualichat.utils.Config()
    yield tmp_path
