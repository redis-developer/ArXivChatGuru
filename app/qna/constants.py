import os

# Env Vars and constants
CACHE_TYPE = os.getenv("CACHE_TYPE", "semantic")
OPENAI_COMPLETIONS_ENGINE = os.getenv("OPENAI_COMPLETIONS_ENGINE", "gpt-3.5-turbo-16k")
OPENAI_EMBEDDINGS_ENGINE = os.getenv("OPENAI_EMBEDDINGS_ENGINE", "text-embedding-ada-002")

REDIS_INDEX_NAME = os.getenv("REDIS_INDEX_NAME", "arxiv")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
