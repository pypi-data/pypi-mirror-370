import logging
import os
import socket
from pathlib import Path

import docker
from logfmter import Logfmter

logger = logging.getLogger('ingress')


# ugly workaround, but implementing it was fast
class MyLogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def _log(self, level: int, *args, **kwargs):
        try:
            kwargs['name_'] = kwargs['name']
            del kwargs['name']
        except KeyError:
            pass
        if not args:
            self.logger.log(level, kwargs)
        else:
            self.logger.log(level, *args, extra=kwargs)

    def debug(self, *args, **kwargs):
        self._log(logging.DEBUG, *args, **kwargs)

    def info(self, *args, **kwargs):
        self._log(logging.INFO, *args, **kwargs)

    def warning(self, *args, **kwargs):
        self._log(logging.WARNING, *args, **kwargs)

    def error(self, *args, **kwargs):
        self._log(logging.ERROR, *args, **kwargs)

    def critical(self, *args, **kwargs):
        self._log(logging.CRITICAL, *args, **kwargs)


def setup_logging(level=None):
    if level is None:
        level = os.environ.get('LOGLEVEL', 'WARNING').upper()
    handler = logging.StreamHandler()
    handler.setFormatter(
        Logfmter(
            keys=['logger', 'level', 'ts'],
            mapping={
                'level': 'levelname',
                'logger': 'name',
                'ts': 'asctime',
            },
        )
    )
    handler.setLevel(level)
    logger.addHandler(handler)
    logger.setLevel(level)


def get_logger() -> MyLogger:
    return MyLogger(logger)


def get_docker_client() -> docker.DockerClient:
    return docker.from_env()


def get_network_name():
    return 'ingress'


def get_caddyfile_template() -> Path:
    return Path(__file__).parent / 'templates/Caddyfile'


def get_caddyfile() -> Path:
    return Path('Caddyfile')


def get_caddy_container_name() -> str:
    return 'ingress-caddy-1'


def get_caddy_hostname():
    result = 'localhost'
    if socket.gethostname() == 'controller.ingress':
        result = 'caddy.ingress'
    return result
