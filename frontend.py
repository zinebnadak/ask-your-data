from __future__ import annotations

from importlib import import_module
from pathlib import Path


_CANONICAL_PACKAGE = import_module("Frontend")
__path__ = [str(Path(__file__).resolve().parent / "Frontend")]

if __spec__ is not None:
    __spec__.submodule_search_locations = __path__


def __getattr__(name: str):
    return getattr(_CANONICAL_PACKAGE, name)
