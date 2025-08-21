from collections import defaultdict
from dataclasses import dataclass
from typing import Iterator


@dataclass
class Proxy:
    """
    A simple mapping from "externally visible hostname" like `foo.0-main.de` to
    unique container hostname (the short ID, as defined by Docker) and the port to
    connect to, e.g. `82eb654ad00b` on port `5000`.
    """

    host: str
    target: str
    port: int
    authelia: bool = False

    def __str__(self):
        return f'{self.url_host()} {self.url_target()}'

    def url_host(self):
        return f'https://{self.host}'

    def url_target(self):
        return f'http://{self.target}:{self.port}'

    def verbose(self):
        result = str(self)
        if self.authelia:
            result += ' (authelia)'
        return result


class ProxyMap:
    """
    A list of proxies, that is the state we need to persist and diff.
    """

    proxies: list[Proxy]
    duplicates: list[str]

    def __init__(self, proxies: list[Proxy]):
        # naively find duplicates while keeping proxy order intact
        self.proxies = []
        self.duplicates = []
        host2count: dict[str, int] = defaultdict(int)
        for p in proxies:
            host2count[p.host] += 1
        for p in proxies:
            if host2count[p.host] == 1:
                self.proxies.append(p)
            else:
                if p.host not in self.duplicates:
                    self.duplicates.append(p.host)

    def __repr__(self):
        return repr(self.proxies)

    def __str__(self):
        return '\n'.join([str(p) for p in self.proxies])

    def __iter__(self) -> Iterator[Proxy]:
        return iter(self.proxies)

    def __len__(self):
        return len(self.proxies)

    def __eq__(self, other):
        return self.proxies == other.proxies and self.duplicates == other.duplicates

    @classmethod
    def empty(cls):
        return cls([])

    def as_dict(self):
        return {p.url_host(): p.url_target() for p in self.proxies}
