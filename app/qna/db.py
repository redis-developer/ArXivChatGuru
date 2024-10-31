from redis import Redis
from typing import List

from langchain.schema import Document
from langchain_redis import RedisVectorStore

from qna.llm import get_embeddings
from qna.constants import CACHE_TYPE, REDIS_INDEX_NAME, REDIS_URL


def get_cache():
    # construct cache implementation based on env var
    if CACHE_TYPE == "semantic":
        from langchain_redis import RedisSemanticCache
        print("Using semantic cache")

        # TODO change to using huggingface embeddings
        # so that caching is cheaper and faster.
        embeddings = get_embeddings()

        return RedisSemanticCache(
            redis_url=REDIS_URL,
            embeddings=embeddings,
            distance_threshold=0.1
        )
    return None



def get_vectorstore(documents: List[Document]=None) -> "RedisVectorStore":
    """Create the Redis vectorstore."""

    embeddings = get_embeddings()

    cleaned_docs = [
        Document(
            page_content=doc.page_content,
            metadata={
                "title": doc.metadata["Title"],
                "authors": doc.metadata["Authors"],
                "category": doc.metadata["primary_category"],
                "links": doc.metadata["links"]
            }
        ) for doc in documents
    ]

    try:
        vectorstore = RedisVectorStore.from_existing_index(
            embedding=embeddings,
            index_name=REDIS_INDEX_NAME,
            redis_url=REDIS_URL
        )
        return vectorstore
    except:
        pass

    vectorstore = RedisVectorStore.from_documents(
        documents=cleaned_docs,
        embedding=embeddings,
        index_name=REDIS_INDEX_NAME,
        redis_url=REDIS_URL
    )
    return vectorstore