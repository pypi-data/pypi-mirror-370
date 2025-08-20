# -*- coding: utf-8 -*-

from pathlib import Path

from tuxsuite.xdg import get_cache_dir


def test_cache_dir_env(monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", "/path/to/cache")
    assert str(get_cache_dir()) == "/path/to/cache/tuxsuite"


def test_cache_dir_default(monkeypatch):
    assert get_cache_dir() == Path.home() / ".cache" / "tuxsuite"
