import json
from pathlib import Path
from typing import Optional

import click

from . import caddy, config
from .caddy import post_caddyfile
from .exceptions import CaddyError
from .main import loop, reconfigure, get_proxy_map

log = config.get_logger()


@click.group
@click.option(
    '-l',
    '--log-level',
    default=None,
    help='https://docs.python.org/3/library/logging.html#levels (case-insensitive)',
)
@click.option(
    '-t',
    '--template',
    envvar='INGRESS_TEMPLATE',
    default=None,
    type=click.Path(exists=True, path_type=Path),
    help='Override the Jinja2 template to use when rendering',
)
def root(log_level, template: Path | None = None):
    if log_level is not None:
        log_level = log_level.upper()
    config.setup_logging(log_level)
    if template is not None:
        log.info('overriding template', path=template)
        config.get_caddyfile_template = lambda: template  # type: ignore


@root.command
def ls():
    print(get_proxy_map())


@root.command
@click.option('-o', '--output', type=Path)
def render(output: Optional[Path]):
    pm = get_proxy_map()
    result = caddy.render(pm)
    if output is not None:
        output.write_text(result)
        log.info('wrote', path=output)
    else:
        print(result)


@root.command
@click.option('--caddyfile', default='Caddyfile', type=Path)
def post(caddyfile):
    try:
        post_caddyfile(caddyfile, config.get_caddy_hostname())
    except CaddyError as e:
        log.error(e.args[0])
        raise SystemExit(1)


@root.command
def caddyfile():
    pm = get_proxy_map()
    print(caddy.render(pm))


@root.command
def caddyjson():
    print(json.dumps(caddy.get_config(config.get_caddy_hostname())))


@root.command
@click.option('--interval', default=5, help='Duration of the tick interval.')
def control_loop(interval):
    """
    Run the control loop.

    This asks Docker for Containers attached to the ingress network every INTERVAL seconds. Lowering the INTERVAL
    results in higher CPU usage, but faster reaction times.
    """
    loop(interval)


@root.command(name='reconfigure')
def reconfigure_():
    pm = get_proxy_map()
    reconfigure(pm)
