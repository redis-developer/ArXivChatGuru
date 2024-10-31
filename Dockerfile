FROM python:3.11-slim-buster

RUN apt-get update && apt-get install python-tk python3-tk tk-dev -y

WORKDIR /app

# Copy all files and subdirectories from ./app to /app in the image
COPY ./app /app

RUN poetry install --no-root

LABEL org.opencontainers.image.source https://github.com/redis-developer/ArxivChatGuru

CMD ["streamlit", "run", "app.py", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false","--server.enableXsrfProtection", "false", "--server.address", "0.0.0.0"]
