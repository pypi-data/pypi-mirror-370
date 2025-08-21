from docker.models.containers import Container

from .config import get_logger

log = get_logger()


def c2port(c: Container) -> int:
    try:
        return int(c.labels['ingress.port'])
    except (KeyError, TypeError):
        log.debug('missing ingress.port label; falling back to first exposed port', extra={'name': c.name})
    ports = list(c.ports.keys())
    try:
        # ['443/tcp', '5555/tcp'] --> 443
        return ports[0].split('/')[0]
    except (AttributeError, IndexError):
        return 80
