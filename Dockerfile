FROM python:3.9.10-slim-buster

RUN apt-get update && apt-get install python-tk python3-tk tk-dev -y

WORKDIR /app

# Copy all files and subdirectories from ./app to /app in the image
COPY ./app /app

RUN pip install -r requirements.txt

LABEL org.opencontainers.image.source https://github.com/RedisVentures/ArxivChatGuru

CMD ["streamlit", "run", "app.py", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false","--server.enableXsrfProtection", "false", "--server.address", "0.0.0.0"]
