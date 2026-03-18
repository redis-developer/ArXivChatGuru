from typing import Any

from redis import Redis

from qna.constants import REDIS_URL


STATS_KEYS = [
    "num_docs",
    "num_records",
    "number_of_uses",
    "percent_indexed",
    "total_indexing_time",
    "bytes_per_record_avg",
    "records_per_doc_avg",
    "doc_table_size_mb",
    "vector_index_sz_mb",
]


def get_redis_client() -> Redis:
    return Redis.from_url(REDIS_URL, decode_responses=True)


def get_index_info(index_name: str, redis_client: Redis | None = None) -> dict[str, Any]:
    client = redis_client or get_redis_client()
    try:
        return client.ft(index_name).info()
    finally:
        if redis_client is None:
            client.close()


def _pairs_to_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    if not isinstance(value, (list, tuple)):
        return {}

    result: dict[str, Any] = {}
    iterator = iter(value)
    for key in iterator:
        result[str(key)] = next(iterator, None)
    return result


def build_stats_rows(index_info: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"Stat": key, "Value": index_info.get(key)} for key in STATS_KEYS]


def build_index_rows(index_info: dict[str, Any]) -> list[dict[str, Any]]:
    definition = _pairs_to_dict(index_info.get("index_definition", {}))
    return [
        {
            "Index Name": index_info.get("index_name"),
            "Storage Type": definition.get("key_type"),
            "Prefixes": definition.get("prefixes"),
            "Index Options": index_info.get("index_options"),
            "Indexing": index_info.get("indexing"),
        }
    ]


def build_attribute_rows(index_info: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for attribute in index_info.get("attributes", []):
        attribute_map = _pairs_to_dict(attribute)
        extras = [
            f"{key}={value}"
            for key, value in attribute_map.items()
            if key not in {"identifier", "attribute", "type"}
        ]
        rows.append(
            {
                "Name": attribute_map.get("identifier"),
                "Attribute": attribute_map.get("attribute"),
                "Type": attribute_map.get("type"),
                "Options": ", ".join(extras),
            }
        )
    return rows
