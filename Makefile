PYTHON ?= tank_game\Scripts\python.exe
UV_RUN = uv run --python $(PYTHON)

.PHONY: install hooks lint test check format run ci

install:
	uv pip install --python $(PYTHON) -e .[dev]

hooks:
	$(UV_RUN) pre-commit install

lint:
	$(UV_RUN) ruff check .

format:
	$(UV_RUN) ruff format .

test:
	$(UV_RUN) pytest

check: lint test

run:
	$(UV_RUN) tank-game

ci: check

