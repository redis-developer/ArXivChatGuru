FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN python3 -m pip install --no-cache-dir poetry==2.3.2

WORKDIR /app
COPY pyproject.toml poetry.lock README.md ./
RUN python3 -m poetry install --only main --no-root
COPY app ./app

LABEL org.opencontainers.image.source https://github.com/redis-developer/ArxivChatGuru

CMD ["python3", "-m", "poetry", "run", "streamlit", "run", "app/app.py", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false", "--server.enableXsrfProtection", "false", "--server.address", "0.0.0.0"]
