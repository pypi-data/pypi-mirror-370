.PHONY: lint format check-version

# lint commands

lint:
	uv run ruff check .
	uv run ruff format . --diff

format:
	uv run ruff check --fix .
	uv run ruff format .

VERSION_KIND ?= patch

bump-version:
	uv run --with hatch hatch version $(VERSION_KIND)