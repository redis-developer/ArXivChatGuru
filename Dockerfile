FROM python:3.11-slim-buster

RUN apt-get update && apt-get install python-tk python3-tk tk-dev curl -y

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy the deps file into the container
COPY ./poetry.lock ./pyproject.toml ./

WORKDIR /app

# Copy all files and subdirectories from ./app to /app in the image
COPY ./app /app

RUN poetry install --no-root

LABEL org.opencontainers.image.source https://github.com/redis-developer/ArxivChatGuru

CMD ["poetry", "run", "streamlit", "run", "app.py", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false","--server.enableXsrfProtection", "false", "--server.address", "0.0.0.0"]
