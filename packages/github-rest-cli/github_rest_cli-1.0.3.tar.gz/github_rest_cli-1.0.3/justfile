# justfile for python

set dotenv-load := true

# Alias

alias dl := dynaconf-list
alias dv := dynaconf-validate

@setup-pre-commit:
    pre-commit install

@setup-ruff:
    uv tool install ruff

@cache:
    uv clean cache

@build-local:
    uv build

@publish-local:
    uv publish --token $PYPI_TOKEN

@sync:
    uv sync

@lint:
    ruff check .

@test:
    pytest -v

@fmt:
    ruff format .

@dynaconf-list:
    dynaconf -i github_rest_cli.config.settings list

@dynaconf-validate:
    dynaconf -i github_rest_cli.config.settings validate

@profile *args:
    pyinstrument --no-color -m github_rest_cli.main {{ args }}
