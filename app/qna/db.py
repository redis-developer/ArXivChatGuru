import os
import redis
import numpy as np
import pandas as pd
import typing as t

from redis.commands.search.query import Query
from redis.commands.search.indexDefinition import (
    IndexDefinition,
    IndexType
)
from redis.commands.search.field import (
    VectorField,
    NumericField,
    TextField
)


INDEX_NAME = "embedding-index"
NUM_VECTORS = 4000
PREFIX = "embedding"
VECTOR_DIM = 1536
DISTANCE_METRIC = "COSINE"

def create_index(redis_conn: redis.Redis):
    # Define schema
    title = TextField(name="title")
    heading = TextField(name="heading")
    content = TextField(name="content")
    tokens = NumericField(name="tokens")
    embedding = VectorField("embedding",
        "FLAT", {
            "TYPE": "FLOAT64",
            "DIM": VECTOR_DIM,
            "DISTANCE_METRIC": DISTANCE_METRIC,
            "INITIAL_CAP": NUM_VECTORS
        }
    )
    # Create index
    redis_conn.ft(INDEX_NAME).create_index(
        fields = [title, heading, content, tokens, embedding],
        definition = IndexDefinition(prefix=[PREFIX], index_type=IndexType.HASH)
    )

def process_doc(doc) -> dict:
    d = doc.__dict__
    if "vector_score" in d:
        d["vector_score"] = 1 - float(d["vector_score"])
    return d

def search_redis(
    redis_conn: redis.Redis,
    query_vector: t.List[float],
    return_fields: list = [],
    k: int = 5,
) -> t.List[dict]:
    """
    Perform KNN search in Redis.

    Args:
        query_vector (list<float>): List of floats for the embedding vector to use in the search.
        return_fields (list, optional): Fields to include in the response. Defaults to [].
        k (int, optional): Count of nearest neighbors to return. Defaults to 5.

    Returns:
        list<dict>: List of most similar documents.
    """
    # Prepare the Query
    base_query = f'*=>[KNN {k} @embedding $vector AS vector_score]'
    query = (
        Query(base_query)
         .sort_by("vector_score")
         .paging(0, k)
         .return_fields(*return_fields)
         .dialect(2)
    )
    params_dict = {"vector": np.array(query_vector, dtype=np.float64).tobytes()}
    # Vector Search in Redis
    results = redis_conn.ft(INDEX_NAME).search(query, params_dict)
    return [process_doc(doc) for doc in results.docs]

def list_docs(redis_conn: redis.Redis, k: int = NUM_VECTORS) -> pd.DataFrame:
    """
    List documents stored in Redis

    Args:
        k (int, optional): Number of results to fetch. Defaults to VECT_NUMBER.

    Returns:
        pd.DataFrame: Dataframe of results.
    """
    base_query = f'*'
    return_fields = ['title', 'heading', 'content']
    query = (
        Query(base_query)
        .paging(0, k)
        .return_fields(*return_fields)
        .dialect(2)
    )
    results = redis_conn.ft(INDEX_NAME).search(query)
    return [process_doc(doc) for doc in results.docs]

def index_documents(redis_conn: redis.Redis, embeddings_lookup: dict, documents: list):
    """
    Index a list of documents in RediSearch.

    Args:
        embeddings_lookup (dict): Doc embedding lookup dict.
        documents (list): List of docs to set in the index.
    """
    # Iterate through documents and store in Redis
    # NOTE: use async Redis client for even better throughput
    pipe = redis_conn.pipeline()
    for i, doc in enumerate(documents):
        key = f"{PREFIX}:{i}"
        embedding = embeddings_lookup[(doc["title"], doc["heading"])]
        doc["embedding"] = embedding.tobytes()
        pipe.hset(key, mapping = doc)
        if i % 150 == 0:
            pipe.execute()
    pipe.execute()

def load_documents(redis_conn: redis.Redis):
    # Load data
    docs = pd.read_csv("https://cdn.openai.com/API/examples/data/olympics_sections_text.csv")
    embeds = pd.read_csv("https://cdn.openai.com/API/examples/data/olympics_sections_document_embeddings.csv", header=0)
    max_dim = max([int(c) for c in embeds.columns if c != "title" and c != "heading"])
    embeds = {
           (r.title, r.heading): np.array([r[str(i)] for i in range(max_dim + 1)], dtype=np.float64) for _, r in embeds.iterrows()
    }
    print(f"Indexing {len(docs)} Documents")
    index_documents(
        redis_conn = redis_conn,
        embeddings_lookup = embeds,
        documents = docs.to_dict("records")
    )
    print("Redis Vector Index Created!")

def init():
    redis_conn = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=os.getenv('REDIS_PORT', 6379),
        password=os.getenv('REDIS_PASSWORD')
    )
    # Check index existence
    try:
        redis_conn.ft(INDEX_NAME).info()
        print("Index exists")
    except:
        print("Index does not exist")
        print("Creating embeddings index")
        # Create index
        create_index(redis_conn)
        load_documents(redis_conn)
    return redis_conn