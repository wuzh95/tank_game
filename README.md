# Tank Game

A Python `pygame` tank battle game using a structured, production-style workflow.

## Quick Start (uv)

1. Create venv:
   - `uv venv tank_game`
2. Install dependencies:
   - `uv pip install --python tank_game\\Scripts\\python.exe -e .[dev]`
3. Run game:
   - `uv run --python tank_game\\Scripts\\python.exe tank-game`
4. Install git hooks:
   - `uv run --python tank_game\\Scripts\\python.exe pre-commit install`
5. Note:
   - Avoid `uv sync` without explicit environment control, as it may create a default `.venv`.

## Project Structure

```text
proj1/
├─ .github/
│  └─ workflows/
│     ├─ ci.yml
│     └─ release.yml
├─ tank_battle/
│  ├─ assets/
│  │  └─ levels.json
│  ├─ entities/
│  │  ├─ tank_base.py
│  │  ├─ player.py
│  │  ├─ enemy.py
│  │  ├─ bullet.py
│  │  └─ item.py
│  ├─ systems/
│  │  ├─ ai.py
│  │  ├─ collision.py
│  │  ├─ spawn.py
│  │  └─ level.py
│  ├─ game.py
│  ├─ main.py
│  └─ settings.py
├─ tests/
│  └─ test_imports.py
├─ .pre-commit-config.yaml
├─ Makefile
├─ justfile
├─ pyproject.toml
├─ uv.lock
└─ README.md
```

### Folder/Module Responsibilities

- `.github/workflows/`
  - `ci.yml`: runs lint (`ruff`) and tests (`pytest`) on push/PR.
  - `release.yml`: builds Windows `.exe` with `PyInstaller` and uploads/publishes artifacts.

- `tank_battle/` (main game package)
  - `main.py`: application entry point; initializes `pygame` and starts the game loop.
  - `game.py`: main state machine and runtime orchestration (`MENU/PLAYING/PAUSED/WIN/GAME_OVER`), rendering, input, and progression.
  - `settings.py`: centralized constants (screen size, speeds, colors, cooldowns, asset paths); includes packaged-exe path handling.
  - `assets/levels.json`: data-driven level definitions (spawn points, waves, wall layout, per-level enemy params).

- `tank_battle/entities/` (domain objects)
  - `tank_base.py`: shared tank movement/collision primitives.
  - `player.py`: player movement, firing cooldown, buffs, damage handling.
  - `enemy.py`: enemy data and behavior timers; firing logic.
  - `bullet.py`: projectile movement, lifetime, owner attribution.
  - `item.py`: pickup model, lifetime, rendering metadata.

- `tank_battle/systems/` (gameplay systems)
  - `ai.py`: enemy patrol/chase behavior updates.
  - `collision.py`: bullet collision resolution, enemy death/drop handling, item pickup effects.
  - `spawn.py`: wave and spawn-cap control for enemies.
  - `level.py`: level config loading/parsing from JSON into runtime objects.

- `tests/`
  - `test_imports.py`: smoke test to ensure entry import validity; baseline for CI checks.

- Root tooling/config files
  - `pyproject.toml`: project metadata, dependencies, `ruff`/`pytest` config, console entrypoint.
  - `uv.lock`: locked dependency graph for reproducible installs.
  - `.pre-commit-config.yaml`: local git hook checks (format/lint/basic hygiene).
  - `Makefile` / `justfile`: one-command developer workflow wrappers.

### Generated Artifacts (not source)

- `tank_battle/tank-game.exe`: locally built Windows executable output.
- `build/` (when present): temporary/intermediate build files from `PyInstaller`.
- `__pycache__/` (when present): Python bytecode cache files.

## Developer Commands

- Lint: `uv run --python tank_game\\Scripts\\python.exe ruff check .`
- Test: `uv run --python tank_game\\Scripts\\python.exe pytest`
- Run: `uv run --python tank_game\\Scripts\\python.exe tank-game`
- Pre-commit (all files): `uv run --python tank_game\\Scripts\\python.exe pre-commit run --all-files`

## One-Command Workflows

- Make (if installed):
  - `make install`
  - `make hooks`
  - `make verify-env`
  - `make check`
  - `make run`
- Just (if installed):
  - `just install`
  - `just hooks`
  - `just verify-env`
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

