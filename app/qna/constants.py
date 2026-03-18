import hashlib
import os
import re
import unicodedata

DEFAULT_CHAT_MODEL = "gpt-5.4-mini"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_EMBEDDING_DIMENSIONS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}

REDIS_INDEX_BASENAME = os.getenv(
    "REDIS_INDEX_BASENAME",
    os.getenv("REDIS_INDEX_NAME", "arxiv"),
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


def get_chat_model_name() -> str:
    return os.getenv(
        "OPENAI_CHAT_MODEL",
        os.getenv("OPENAI_COMPLETIONS_ENGINE", DEFAULT_CHAT_MODEL),
    )


def get_embedding_model_name() -> str:
    return os.getenv(
        "OPENAI_EMBEDDING_MODEL",
        os.getenv("OPENAI_EMBEDDINGS_ENGINE", DEFAULT_EMBEDDING_MODEL),
    )


def get_embedding_dimensions() -> int:
    configured_dims = os.getenv("OPENAI_EMBEDDING_DIMENSIONS")
    if configured_dims:
        return int(configured_dims)
    return DEFAULT_EMBEDDING_DIMENSIONS.get(get_embedding_model_name(), 1536)


def ensure_openai_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is required. Copy .env.template to .env and add your API key."
        )


def get_topic_token(topic: str) -> str:
    normalized_topic = topic.strip().lower() or "topic"
    normalized_ascii = (
        unicodedata.normalize("NFKD", normalized_topic).encode("ascii", "ignore").decode("ascii")
    )
    slug = re.sub(r"[^a-z0-9]+", "-", normalized_ascii).strip("-") or "topic"
    digest = hashlib.sha1(normalized_topic.encode("utf-8")).hexdigest()[:8]
    return f"{slug[:32]}-{digest}"


def get_index_name(topic: str) -> str:
    return f"{REDIS_INDEX_BASENAME}-{get_topic_token(topic)}"


def get_index_prefix(topic: str) -> str:
    return f"{REDIS_INDEX_BASENAME}:{get_topic_token(topic)}"
