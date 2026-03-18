POETRY = python3 -m poetry
STREAMLIT_FLAGS = --server.fileWatcherType none --browser.gatherUsageStats false --server.enableXsrfProtection false --server.address 0.0.0.0

.PHONY: install format test build dev docker-up docker-down

install:
	$(POETRY) install --with dev --no-root

format:
	$(POETRY) run ruff format app tests

test:
	$(POETRY) run pytest

build:
	docker compose build

dev:
	$(POETRY) run streamlit run app/app.py $(STREAMLIT_FLAGS)

docker-up:
	docker compose up --build

docker-down:
	docker compose down
