# -*- coding: utf-8 -*-

import os
from pathlib import Path


def _resolve(var, default):
    directory = os.getenv(var)
    if directory:
        return Path(directory)
    else:
        return Path.home() / default


def get_cache_dir():
    return _resolve("XDG_CACHE_HOME", ".cache") / "tuxsuite"
