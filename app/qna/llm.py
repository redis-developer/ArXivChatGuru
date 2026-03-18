from typing import TYPE_CHECKING

from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.llms.base import LLM
from langchain.embeddings.base import Embeddings
from langchain_redis import RedisVectorStore
from qna.constants import (
    ensure_openai_api_key,
    get_chat_model_name,
    get_embedding_model_name,
)


def get_llm(max_tokens=100) -> LLM:
    ensure_openai_api_key()
    llm = ChatOpenAI(model=get_chat_model_name(), max_tokens=max_tokens)
    return llm


def get_embeddings() -> Embeddings:
    ensure_openai_api_key()
    embeddings = OpenAIEmbeddings(model=get_embedding_model_name())
    return embeddings


def make_qna_chain(llm: LLM, vector_db: RedisVectorStore, prompt: str = "", **kwargs):
    """Create the QA chain."""

    search_type = "similarity"
    if "search_type" in kwargs:
        search_type = kwargs.pop("search_type")

    # Create retreival QnA Chain
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_db.as_retriever(search_kwargs=kwargs, search_type=search_type),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
        verbose=True,
    )
    return chain
