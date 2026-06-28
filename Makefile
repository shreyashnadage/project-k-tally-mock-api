.PHONY: venv install install-dev test lint format run run-frontend clean

venv:
	python -m venv .venv

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check backend/ tests/
	mypy backend/

format:
	black backend/ tests/

run:
	uvicorn backend.main:app --host 0.0.0.0 --port 9001 --reload

run-frontend:
	cd frontend && npm run dev

clean:
	rm -rf build/ dist/ *.egg-info .mypy_cache .pytest_cache htmlcov
