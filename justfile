set shell := ["powershell.exe", "-NoLogo", "-Command"]

python := "tank_game\\Scripts\\python.exe"

install:
    uv pip install --python {{python}} -e '.[dev]'

hooks:
    uv run --python {{python}} pre-commit install

lint:
    uv run --python {{python}} ruff check .

format:
    uv run --python {{python}} ruff format .

test:
    uv run --python {{python}} pytest

check:
    uv run --python {{python}} ruff check .
    uv run --python {{python}} pytest

run:
    uv run --python {{python}} tank-game

