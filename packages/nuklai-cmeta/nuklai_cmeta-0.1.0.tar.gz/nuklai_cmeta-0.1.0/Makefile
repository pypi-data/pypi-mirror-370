# Makefile for cmeta (uv-only)

.PHONY: help install lint format typecheck test ci build publish clean

help:
	@echo "Targets:"
	@echo "  install    - uv sync (installs package editable + dev deps)"
	@echo "  lint       - ruff lint"
	@echo "  format     - ruff format (in-place)"
	@echo "  typecheck  - mypy type checks"
	@echo "  test       - pytest"
	@echo "  ci         - lint + typecheck + test"
	@echo "  build      - uv build (sdist/wheel)"
	@echo "  publish    - uv publish (needs PYPI_TOKEN)"
	@echo "  clean      - remove build and cache artifacts"

install:
	uv sync --extra dev

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy cmeta

test:
	uv run pytest -q

ci: lint typecheck test

build:
	uv build

publish:
	@if [ -z "$$PYPI_TOKEN" ]; then echo "PYPI_TOKEN is required"; exit 1; fi
	uv publish --token "$$PYPI_TOKEN"

clean:
	rm -rf dist build .pytest_cache .ruff_cache .mypy_cache
