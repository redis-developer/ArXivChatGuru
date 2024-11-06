from typing import TYPE_CHECKING

from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.llms.base import LLM
from langchain.embeddings.base import Embeddings
from langchain_redis import RedisVectorStore
from qna.constants import (
    OPENAI_COMPLETIONS_ENGINE,
    OPENAI_EMBEDDINGS_ENGINE,
)


def get_llm(max_tokens=100) -> LLM:
    llm = ChatOpenAI(model_name=OPENAI_COMPLETIONS_ENGINE, max_tokens=max_tokens)
    return llm


def get_embeddings() -> Embeddings:
    embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDINGS_ENGINE)
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
