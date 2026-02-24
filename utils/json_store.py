"""
INFERNUM AETERNA — JsonStore
Persistence JSON thread-safe avec asyncio.Lock.
"""

import json
import os
import asyncio
import logging

log = logging.getLogger("infernum")


class JsonStore:
    """Wrapper autour d'un fichier JSON avec lock async pour éviter les race conditions."""

    def __init__(self, filepath: str, default=None):
        self._filepath = filepath
        self._default = default if default is not None else {}
        self._lock = asyncio.Lock()
        self._data = self._load_sync()

    def _load_sync(self) -> dict:
        if not os.path.exists(self._filepath):
            return self._default.copy() if isinstance(self._default, dict) else self._default
        try:
            with open(self._filepath, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            log.error("JsonStore: erreur lecture %s : %s", self._filepath, e)
            return self._default.copy() if isinstance(self._default, dict) else self._default

    def _save_sync(self):
        os.makedirs(os.path.dirname(self._filepath) or ".", exist_ok=True)
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    async def save(self):
        async with self._lock:
            await asyncio.get_running_loop().run_in_executor(None, self._save_sync)

    async def load(self):
        async with self._lock:
            self._data = await asyncio.get_running_loop().run_in_executor(None, self._load_sync)
        return self._data

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __contains__(self, key):
        return key in self._data

    def get(self, key, default=None):
        return self._data.get(key, default)

    def items(self):
        return self._data.items()

    def values(self):
        return self._data.values()

    def keys(self):
        return self._data.keys()

    def setdefault(self, key, default=None):
        return self._data.setdefault(key, default)
