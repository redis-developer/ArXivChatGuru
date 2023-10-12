import os

# Env Vars and constants
CACHE_TYPE = os.getenv("CACHE_TYPE", "semantic")
OPENAI_COMPLETIONS_ENGINE = os.getenv("OPENAI_COMPLETIONS_ENGINE", "gpt-3.5-turbo-16k")
OPENAI_EMBEDDINGS_ENGINE = os.getenv("OPENAI_EMBEDDINGS_ENGINE", "text-embedding-ada-002")

REDIS_INDEX_NAME = os.getenv("REDIS_INDEX_NAME", "arxiv")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"