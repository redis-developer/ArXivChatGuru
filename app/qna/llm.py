import os

from langchain.vectorstores.redis import Redis
from langchain.schema import Document
from langchain.llms.base import LLM
from langchain.embeddings.base import Embeddings
from typing import List

# Env Vars and constants
CACHE_TYPE = os.getenv("CACHE_TYPE")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
OPENAI_API_TYPE = os.getenv("OPENAI_API_TYPE", "")
OPENAI_COMPLETIONS_ENGINE = os.getenv("OPENAI_COMPLETIONS_ENGINE", "text-davinci-003")
INDEX_NAME = "wiki"


def get_llm() -> LLM:
    if OPENAI_API_TYPE=="azure":
        from langchain.llms import AzureOpenAI
        llm=AzureOpenAI(deployment_name=OPENAI_COMPLETIONS_ENGINE)
    else:
        from langchain.llms import OpenAI
        llm=OpenAI()
    return llm


def get_embeddings() -> Embeddings:
    if OPENAI_API_TYPE=="azure":
        #currently Azure OpenAI embeddings require request for service limit increase to be useful
        #using build-in HuggingFace instead
        from langchain.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    else:
        from langchain.embeddings import OpenAIEmbeddings
        # Init OpenAI Embeddings
        embeddings = OpenAIEmbeddings()
    return embeddings


def get_cache():
    # construct cache implementation based on env var
    if CACHE_TYPE == "semantic":
        from langchain.embeddings import OpenAIEmbeddings
        from langchain.cache import RedisSemanticCache
        print("Using semantic cache")
        return RedisSemanticCache(
            redis_url=REDIS_URL,
            embedding=OpenAIEmbeddings()
        )
    elif CACHE_TYPE == "standard":
        from redis import Redis
        from langchain.cache import RedisCache
        return RedisCache(Redis.from_url(REDIS_URL))
    return None


def get_documents() -> List[Document]:
    import pandas as pd
    # Load and prepare wikipedia documents
    datasource = pd.read_csv(
        "https://cdn.openai.com/API/examples/data/olympics_sections_text.csv"
    ).to_dict("records")
    # Create documents
    documents = [
        Document(
            page_content=doc["content"],
            metadata={
                "title": doc["title"],
                "heading": doc["heading"],
                "tokens": doc["tokens"]
            }
        ) for doc in datasource
    ]
    return documents


def create_vectorstore() -> Redis:
    """Create the Redis vectorstore."""

    embeddings = get_embeddings()

    try:
        vectorstore = Redis.from_existing_index(
            embedding=embeddings,
            index_name=INDEX_NAME,
            redis_url=REDIS_URL
        )
        return vectorstore
    except:
        pass


    # Load Redis with documents
    documents = get_documents()
    vectorstore = Redis.from_documents(
        documents=documents
        embedding=embeddings,
        index_name="wiki",
        redis_url=REDIS_URL
    )
    return vectorstore


def make_qna_chain():
    """Create the QA chain."""
    from langchain.prompts import PromptTemplate
    from langchain.chains import RetrievalQA

    # TODO - get external memory working
    # from langchain.memory import ConversationBufferMemory
    # from langchain.memory import RedisChatMessageHistory

    # Persist chat history in Redis
    #message_history = RedisChatMessageHistory(url=REDIS_URL, ttl=600, session_id='my-session')

    # Set up memory model for the LLM
    # memory = ConversationBufferMemory(
    #     #chat_memory=message_history,
    #     memory_key="chat_history",
    #     return_messages=True
    # )

    # Define our prompt
    prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, say that you don't know, don't try to make up an answer.

    This should be in the following format:

    Question: [question here]
    Answer: [answer here]

    Begin!

    Context:
    ---------
    {context}
    ---------
    Question: {question}
    Answer:"""
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    # Create Redis Vector DB
    redis = create_vectorstore()

    # Create retreival QnA Chain
    chain = RetrievalQA.from_chain_type(
            llm=get_llm(),
            chain_type="stuff",
            retriever=redis.as_retriever(),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )
    return chain
