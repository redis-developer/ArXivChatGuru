import os

# Env Vars and constants
CACHE_TYPE = os.getenv("CACHE_TYPE")
OPENAI_API_TYPE = os.getenv("OPENAI_API_TYPE", "openai")
OPENAI_COMPLETIONS_ENGINE = os.getenv("OPENAI_COMPLETIONS_ENGINE", "text-davinci-003")
INDEX_NAME = "wiki"
HUGGINGFACE_MODEL_NAME = os.getenv("HF_MODEL", "all-MiniLM-L6-v2")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
