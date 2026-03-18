<div align="center">
  <a href="https://github.com/redis-developer/redis-ai-resources">
    <img src="./app/assets/arxivguru_crop.png" width="30%" alt="ArXiv ChatGuru logo">
  </a>
</div>

# ArXiv ChatGuru

ArXiv ChatGuru is a Streamlit app that turns a topic from arXiv into a topic-scoped Redis vector index. It fetches papers, chunks them, stores embeddings in Redis, and lets you ask grounded questions against the papers you loaded.

This app is a learning project for academic RAG. It is intentionally simple and is meant to show how Redis fits into a paper Q&A workflow, not to act as a production-ready research assistant.

## What Redis does in this app

- Stores topic-specific paper chunks and embeddings
- Powers vector search for retrieval
- Lets you inspect the active index from the built-in stats page

## How it works

1. Enter a topic and choose how many papers to load.
2. The app pulls papers from arXiv and splits them into chunks.
3. OpenAI generates embeddings for those chunks.
4. Redis stores the chunks and embeddings in a topic-scoped index.
5. LangChain retrieves the closest chunks for each user question and sends that context to the chat model.

![Architecture diagram](app/assets/diagram.png#gh-light-mode-only)
![Architecture diagram](app/assets/diagram-dark.png#gh-dark-mode-only)

## Prerequisites

- Python 3.13 for local development
- Docker Desktop if you want the Docker-first flow
- An OpenAI API key

## Environment setup

Create a `.env` file from the template:

```bash
cp .env.template .env
```

Then set at least:

```bash
OPENAI_API_KEY=your_key_here
```

The default template uses:

- `OPENAI_CHAT_MODEL=gpt-4.1-mini`
- `OPENAI_EMBEDDING_MODEL=text-embedding-3-small`
- `REDIS_INDEX_BASENAME=arxiv`
- `REDIS_URL=redis://arxivchatguru-redis:6379`

## Run with Docker

Docker is the primary local path.

```bash
make docker-up
```

Then open:

```text
http://localhost:8501
```

To stop the stack:

```bash
make docker-down
```

## Run locally

Install Poetry if you do not already have it:

```bash
python3 -m pip install --user poetry
```

Use Python 3.13 for the project environment, install dependencies, and start the app:

```bash
python3 -m poetry env use python3.13
make install
make dev
```

Then open:

```text
http://localhost:8501
```

If you run locally outside Docker, make sure `REDIS_URL` points at a reachable Redis instance such as `redis://localhost:6379`.

## Developer commands

- `make format` formats the app and tests
- `make test` runs the test suite
- `make build` builds the Docker image
- `make dev` starts Streamlit locally
- `make docker-up` starts the app with Docker Compose

## Stats page

After you load a topic from the main page, open the Streamlit stats page to inspect the active Redis index. It shows:

- Index metadata
- Indexed fields
- Query Engine stats for the active topic

## Planned follow-ups

- Add better metadata filters such as year or author
- Improve chunking strategy for long papers
- Add chat history or memory features only if the tutorial needs them
