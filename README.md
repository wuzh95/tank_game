# Tank Game

A Python `pygame` tank battle game using a structured, production-style workflow.

## Quick Start (uv)

1. Create venv:
   - `uv venv tank_game`
2. Install dependencies:
   - `uv sync --python tank_game\\Scripts\\python.exe --extra dev`
3. Run game:
   - `uv run --python tank_game\\Scripts\\python.exe tank-game`
4. Install git hooks:
   - `uv run --python tank_game\\Scripts\\python.exe pre-commit install`

## Project Structure

- `tank_battle/`: core game package
- `tank_battle/entities/`: gameplay entities (`Player`, `Enemy`, `Bullet`, etc.)
- `tank_battle/systems/`: AI, collision, spawning, and level loading systems
- `tank_battle/assets/`: level configuration and game assets
- `tests/`: test suite
- `pyproject.toml`: dependency and tooling configuration

## Developer Commands

- Lint: `uv run --python tank_game\\Scripts\\python.exe ruff check .`
- Test: `uv run --python tank_game\\Scripts\\python.exe pytest`
- Run: `uv run --python tank_game\\Scripts\\python.exe tank-game`
- Pre-commit (all files): `uv run --python tank_game\\Scripts\\python.exe pre-commit run --all-files`

## One-Command Workflows

- Make (if installed):
  - `make install`
  - `make hooks`
  - `make check`
  - `make run`
- Just (if installed):
  - `just install`
  - `just hooks`
  - `just check`
  - `just run`

## CI

- GitHub Actions workflow is defined in `.github/workflows/ci.yml`.
- On each push and pull request it runs:
  - dependency sync via `uv`
  - `ruff check .`
  - `pytest`

## Release (Windows .exe)

- Release workflow is defined in `.github/workflows/release.yml`.
- It builds a Windows executable with `pyinstaller` and publishes `tank-game-windows.zip`.
- Trigger options:
  - push a tag like `v0.1.0` to publish a GitHub Release asset
  - manual run via `workflow_dispatch` to generate workflow artifact

