from langchain.schema import Document
from langchain_redis import RedisConfig, RedisVectorStore
from redis import Redis
from redis.exceptions import ResponseError

from qna.constants import (
    REDIS_URL,
    get_embedding_dimensions,
    get_index_name,
    get_index_prefix,
)
from qna.llm import get_embeddings


METADATA_SCHEMA = [
    {"name": "title", "type": "text"},
    {"name": "authors", "type": "tag"},
    {"name": "category", "type": "tag"},
    {"name": "links", "type": "tag"},
]


def get_redis_client() -> Redis:
    return Redis.from_url(REDIS_URL, decode_responses=True)


def clean_documents(documents: list[Document]) -> list[Document]:
    return [
        Document(
            page_content=doc.page_content,
            metadata={
                "title": doc.metadata.get("Title", ""),
                "authors": doc.metadata.get("Authors", ""),
                "category": doc.metadata.get("primary_category", ""),
                "links": doc.metadata.get("links", ""),
            },
        )
        for doc in documents
    ]


def get_index_config(topic: str) -> RedisConfig:
    return RedisConfig(
        index_name=get_index_name(topic),
        key_prefix=get_index_prefix(topic),
        redis_url=REDIS_URL,
        storage_type="hash",
        content_field="text",
        embedding_field="embedding",
        metadata_schema=METADATA_SCHEMA,
        embedding_dimensions=get_embedding_dimensions(),
        legacy_key_format=False,
    )


def clear_index(topic: str) -> None:
    redis_client = get_redis_client()
    try:
        redis_client.execute_command("FT.DROPINDEX", get_index_name(topic), "DD")
    except ResponseError as exc:
        error_text = str(exc).lower()
        if "no such index" not in error_text and "unknown index name" not in error_text:
            raise
    finally:
        redis_client.close()


def clear_vectorstore(vectorstore: RedisVectorStore | None) -> None:
    if vectorstore is None:
        return

    index = getattr(vectorstore, "index", None)
    if index is None:
        return

    try:
        index.clear()
    except ResponseError as exc:
        error_text = str(exc).lower()
        if "no such index" not in error_text and "unknown index name" not in error_text:
            raise


def get_vectorstore(documents: list[Document], topic: str) -> RedisVectorStore:
    """Create a fresh Redis vector store for the requested topic."""

    if not documents:
        raise ValueError("At least one document is required to create a Redis vector store.")

    clear_index(topic)
    return RedisVectorStore.from_documents(
        documents=clean_documents(documents),
        embedding=get_embeddings(),
        redis_url=REDIS_URL,
        config=get_index_config(topic),
    )
