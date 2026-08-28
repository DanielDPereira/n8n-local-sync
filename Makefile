.PHONY: setup test lint format docker-up docker-down build package

setup:
	pip install -e ".[dev]"

test:
	pytest tests/

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

docker-up:
	docker compose up -d

docker-down:
	docker compose down

build:
	hatch build

package: build
