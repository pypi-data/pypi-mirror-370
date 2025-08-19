from importlib import import_module
from typing import Any

class LazyLoader:
    def __init__(self, lib_name: str):
        self.lib_name = lib_name
        self._lib = None

    def __getattr__(self, name: str) -> Any:
        if self._lib is None:
            self._lib = import_module(self.lib_name)
        return getattr(self._lib, name)