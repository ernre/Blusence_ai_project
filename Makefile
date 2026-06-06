.PHONY: test lint format typecheck

test:
	pytest

lint:
	ruff check src tests

format:
	black src tests
	ruff check --fix src tests

typecheck:
	mypy src/vpe
