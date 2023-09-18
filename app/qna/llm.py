import os
from typing import List, TYPE_CHECKING

from langchain.chains import RetrievalQA
from langchain.chains import ConversationalRetrievalChain, LLMChain, StuffDocumentsChain
from langchain.llms.base import LLM
from langchain.embeddings.base import Embeddings

from qna.constants import (
    OPENAI_API_TYPE,
    OPENAI_COMPLETIONS_ENGINE,
    HUGGINGFACE_MODEL_NAME,
)
from qna.prompt import condense_prompt

if TYPE_CHECKING:
    from langchain.vectorstores.redis import Redis as RedisVDB


def get_llm(max_tokens=100) -> LLM:
    if OPENAI_API_TYPE=="azure":
        from langchain.llms import AzureOpenAI
        llm=AzureOpenAI(deployment_name=OPENAI_COMPLETIONS_ENGINE)
    else:
        from langchain.llms import OpenAI
        llm=OpenAI(model_name=OPENAI_COMPLETIONS_ENGINE, max_tokens=max_tokens)
    return llm


def get_embeddings() -> Embeddings:
    # TODO - work around rate limits for embedding providers
    if OPENAI_API_TYPE=="azure":
        #currently Azure OpenAI embeddings require request for service limit increase to be useful
        #using build-in HuggingFace instead
        from langchain.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name=HUGGINGFACE_MODEL_NAME)
    else:
        from langchain.embeddings import OpenAIEmbeddings
        # Init OpenAI Embeddings
        embeddings = OpenAIEmbeddings()
    return embeddings



def make_qna_chain(vector_db: "RedisVDB", prompt: str = "", **kwargs):
    """Create the QA chain."""

    max_tokens = 100
    if "max_tokens" in kwargs:
        max_tokens = kwargs.pop("max_tokens")

    search_type = "similarity"
    if "search_type" in kwargs:
        search_type = kwargs.pop("search_type")

    llm = get_llm(max_tokens=max_tokens)
    # TODO be able to edit search kwargs

    # Create retreival QnA Chain
    chain = RetrievalQA.from_chain_type(
        llm=get_llm(),
        chain_type="stuff",
        retriever=vector_db.as_retriever(search_kwargs=kwargs, search_type=search_type),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
        verbose=True
    )
    return chain


def make_chat_qna_chain(vector_db: "RedisVDB", prompt: str = "", **kwargs):
    """Create the QA chain."""

    max_tokens = 1000
    if "max_tokens" in kwargs:
        max_tokens = kwargs.pop("max_tokens")

    search_type = "similarity"
    if "search_type" in kwargs:
        search_type = kwargs.pop("search_type")

    llm = get_llm(max_tokens=max_tokens)

    combine_docs_chain = make_qna_chain(vector_db, prompt, **kwargs)
    question_chain = LLMChain(llm=llm, prompt=condense_prompt(), verbose=True)

    chain = ConversationalRetrievalChain.from_llm(
        llm=get_llm(),
        combine_docs_chain=combine_docs_chain,
        retriever=vector_db.as_retriever(search_kwargs=kwargs, search_type=search_type),
        question_generator=question_chain,
        verbose=True,
        return_source_documents=True,
    )
    return chain