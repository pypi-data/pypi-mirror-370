import time

import backoff
import docker.errors
from docker.models.containers import Container
from docker.models.networks import Network

from . import caddy
from .caddy import post_caddyfile
from .config import (
    get_logger,
    get_caddyfile,
    get_caddy_hostname,
    get_caddy_container_name,
    get_docker_client,
    get_network_name,
)
from .exceptions import CaddyError
from .models import Proxy, ProxyMap
from .repo import InMemoryRepo
from .utils import c2port

log = get_logger()


class ContainerParseError(Exception):
    def __init__(self, msg, container: Container):
        self.msg = msg
        self.container = container


def iter_container2proxies(container: Container):
    container_network_alias = container.short_id
    port = c2port(container)
    has_authelia = container.labels.get('ingress.authelia', '').lower() == 'true'
    try:
        ingress_host = container.labels['ingress.host']
    except KeyError:
        raise ContainerParseError('no ingress.host', container)
    extra_hosts = container.labels.get('ingress.extra_hosts', '').split()
    _hosts = [ingress_host] + extra_hosts
    for host in _hosts:
        yield Proxy(
            host=host,
            port=port,
            target=container_network_alias,
            authelia=has_authelia,
        )


def iter_proxies():
    client = get_docker_client()
    containers: list[Container] = client.containers.list(filters={'label': 'ingress.host'})
    for container in sorted(containers, key=lambda c: c.name):
        extra = {'name': container.name, 'id': container.id}
        if container.labels.get('com.docker.compose.oneoff') == 'True':
            log.info('skipping one-off container', **extra)
            continue
        log.debug('found container', **extra)
        try:
            yield from iter_container2proxies(container)
        except ContainerParseError as e:
            log.debug(msg='skip', reason=e.msg, **extra)


def get_proxy_map() -> ProxyMap:
    return ProxyMap(list(iter_proxies()))


def set_network_aliases(net: Network, caddy_container_name: str, pm: ProxyMap):
    """
    Caddy should be reachable as the proxies' names, so other containers on the ingress network can reach services at
    their FQDN.
    For example: opening "https://foo.0-main.de" in your browser should result in the same result as "curl'ing" from
    another container.
    """
    aliases = [u.host for u in pm]
    log.debug({'aliases': aliases})
    try:
        net.disconnect(caddy_container_name)
    except docker.errors.APIError as e:
        if 'is not connected to network' in str(e):
            pass
        else:
            raise
    net.connect(caddy_container_name, aliases=aliases)
    return aliases


def reconfigure(pm: ProxyMap):
    client = get_docker_client()
    network = client.networks.get(get_network_name())
    caddy_hostname = get_caddy_hostname()
    caddy_container_name = get_caddy_container_name()
    set_network_aliases(network, caddy_container_name, pm)

    caddyfile = get_caddyfile()
    caddyfile.write_text(caddy.render(pm))
    log.debug('wrote Caddyfile', path=caddyfile)
    caddy.reformat(caddyfile)

    @backoff.on_exception(backoff.expo, CaddyError, max_time=30)
    def load_with_timeout():
        post_caddyfile(caddyfile, caddy_hostname)

    load_with_timeout()
    log.info(pm.as_dict())


def loop(tick_s):
    """
    > In robotics and automation, a control loop is a non-terminating loop that regulates the state of a system.
    https://kubernetes.io/docs/concepts/architecture/controller/

    Every tick, we run the following:

    1. ask Docker for containers attached to the `ingress` network
    2. reconfigure if there are differences to the previous state, i.e.
       - update Caddy's network aliases
       - update Caddy's config to reverse proxy the containers
    """
    repo = InMemoryRepo()
    try:
        while True:
            new = get_proxy_map()
            old = repo.load()
            if new != old:
                log.info('changes detected', extra={'diff': len(new) - len(old)})
                repo.save(new)
                reconfigure(new)
            time.sleep(tick_s)
    except KeyboardInterrupt:
        log.debug('caught SIGINT. exiting.')
        raise SystemExit(0)
