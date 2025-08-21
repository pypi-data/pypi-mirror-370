# Ingress
Configure Caddy as an ingress for your Docker containers.


## Usage in Docker
See https://gitlab.com/hukudo/ingress for example usage.


## Usage on the CLI
```
pip install hukudo-ingress
ingress --help
```


## Development
Initial
```
mise install
pre-commit install -f
uv sync
source .venv/bin/activate
ingress --help
```

[Completion](https://click.palletsprojects.com/en/8.1.x/shell-completion/)
```
eval "$(_INGRESS_COMPLETE=bash_source ingress)"
```


## Debugging
```
LOGLEVEL=info ingress render
LOGLEVEL=info ingress reconfigure
```
