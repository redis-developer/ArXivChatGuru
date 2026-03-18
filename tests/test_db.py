from langchain.schema import Document
from redis.exceptions import ResponseError

from qna.db import (
    clean_documents,
    clear_index,
    clear_vectorstore,
    get_index_config,
    get_vectorstore,
)


def test_clean_documents_normalizes_metadata():
    documents = [
        Document(
            page_content="paper body",
            metadata={
                "Title": "Paper title",
                "Authors": "Author One",
                "primary_category": "cs.AI",
                "links": "https://arxiv.org/abs/1234.5678",
            },
        )
    ]

    cleaned = clean_documents(documents)

    assert cleaned[0].metadata == {
        "title": "Paper title",
        "authors": "Author One",
        "category": "cs.AI",
        "links": "https://arxiv.org/abs/1234.5678",
    }


def test_clear_index_ignores_missing_indexes(mocker):
    fake_client = mocker.Mock()
    fake_client.execute_command.side_effect = ResponseError("Unknown Index name")
    mocker.patch("qna.db.get_redis_client", return_value=fake_client)

    clear_index("graph neural networks")

    fake_client.execute_command.assert_called_once()
    fake_client.close.assert_called_once()


def test_get_index_config_uses_topic_scoped_index_names(monkeypatch):
    monkeypatch.setenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    config = get_index_config("Graph neural networks")

    assert config.index_name.startswith("arxiv-")
    assert config.key_prefix.startswith("arxiv:")
    assert config.embedding_dimensions == 1536
    assert config.schema_path is None
    assert any(field["name"] == "category" for field in config.metadata_schema)


def test_get_vectorstore_rebuilds_index_before_loading_documents(mocker):
    mocker.patch("qna.db.clear_index")
    mocker.patch("qna.db.get_embeddings", return_value="embeddings")
    from_documents = mocker.patch("qna.db.RedisVectorStore.from_documents", return_value="store")

    documents = [
        Document(
            page_content="paper body",
            metadata={
                "Title": "Paper title",
                "Authors": "Author One",
                "primary_category": "cs.AI",
                "links": "https://arxiv.org/abs/1234.5678",
            },
        )
    ]

    store = get_vectorstore(documents, "Graph neural networks")

    assert store == "store"
    from_documents.assert_called_once()
    normalized_document = from_documents.call_args.kwargs["documents"][0]
    assert normalized_document.metadata["title"] == "Paper title"


def test_clear_vectorstore_ignores_missing_indexes(mocker):
    vectorstore = mocker.Mock()
    vectorstore.index.clear.side_effect = ResponseError("arxiv-topic: no such index")

    clear_vectorstore(vectorstore)
