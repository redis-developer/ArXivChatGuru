from qna.stats import build_attribute_rows, build_index_rows, build_stats_rows, get_index_info


def test_get_index_info_uses_redis_search_client(mocker):
    redis_client = mocker.Mock()
    redis_client.ft.return_value.info.return_value = {"index_name": "arxiv-topic"}

    index_info = get_index_info("arxiv-topic", redis_client=redis_client)

    assert index_info["index_name"] == "arxiv-topic"
    redis_client.ft.assert_called_once_with("arxiv-topic")


def test_build_index_rows_handles_index_definition_maps():
    rows = build_index_rows(
        {
            "index_name": "arxiv-topic",
            "index_definition": {"key_type": "HASH", "prefixes": ["arxiv:topic"]},
            "index_options": [],
            "indexing": 0,
        }
    )

    assert rows == [
        {
            "Index Name": "arxiv-topic",
            "Storage Type": "HASH",
            "Prefixes": ["arxiv:topic"],
            "Index Options": [],
            "Indexing": 0,
        }
    ]


def test_build_attribute_rows_collects_extra_options():
    rows = build_attribute_rows(
        {
            "attributes": [
                {
                    "identifier": "embedding",
                    "attribute": "embedding",
                    "type": "VECTOR",
                    "algorithm": "FLAT",
                }
            ]
        }
    )

    assert rows == [
        {
            "Name": "embedding",
            "Attribute": "embedding",
            "Type": "VECTOR",
            "Options": "algorithm=FLAT",
        }
    ]


def test_build_stats_rows_preserves_known_metrics():
    rows = build_stats_rows({"num_docs": 5, "vector_index_sz_mb": 1.25})

    assert {"Stat": "num_docs", "Value": 5} in rows
    assert {"Stat": "vector_index_sz_mb", "Value": 1.25} in rows
