import pickle
from pathlib import Path

from .models import ProxyMap


class PickleRepo:
    def __init__(self, path: Path):
        self.path = path

    def save(self, pm: ProxyMap):
        with self.path.open('wb') as f:
            pickle.dump(pm, f)

    def load(self) -> ProxyMap:
        try:
            with self.path.open('rb') as f:
                return pickle.load(f)
        except OSError:
            return ProxyMap.empty()


class InMemoryRepo:
    _pm: ProxyMap

    def __init__(self):
        self._pm = ProxyMap.empty()

    def save(self, pm: ProxyMap):
        self._pm = pm

    def load(self) -> ProxyMap:
        return self._pm
