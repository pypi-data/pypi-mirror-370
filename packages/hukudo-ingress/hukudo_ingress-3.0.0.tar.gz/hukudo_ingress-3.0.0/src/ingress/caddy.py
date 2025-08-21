import subprocess
from pathlib import Path

import httpx as httpx
from httpx import RequestError
from jinja2 import Template

from . import config
from .exceptions import CaddyError
from .models import ProxyMap

log = config.get_logger()


def render(pm: ProxyMap):
    path = config.get_caddyfile_template()
    template = Template(
        path.read_text(),
        # https://jinja.palletsprojects.com/en/stable/api/#jinja2.Environment
        block_start_string='[%',
        block_end_string='%]',
        variable_start_string='[[',
        variable_end_string=']]',
        comment_start_string='[#',
        comment_end_string='#]',
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return template.render(proxies=pm, auth_domain='auth.0-main.de')


def reformat(path: Path = config.get_caddyfile()):
    subprocess.run(['caddy', 'fmt', '--overwrite', str(path)], check=True)


def post_caddyfile(caddyfile: Path, host: str):
    try:
        response = httpx.post(
            f'http://{host}:2019/load',
            headers={'Content-Type': 'text/caddyfile'},
            content=caddyfile.read_bytes(),
        )
        if response.status_code != 200:
            try:
                raise CaddyError(response.json())
            except:  # noqa
                raise CaddyError(response.text)
    except RequestError:
        raise CaddyError()


def get_config(host: str) -> dict:
    try:
        return httpx.get(f'http://{host}:2019/config/').json()
    except RequestError as e:
        raise CaddyError(e)
