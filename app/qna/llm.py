import os

from langchain.vectorstores.redis import Redis


# Redis Env Vars
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"

INDEX_NAME = "wiki"

OPENAI_API_TYPE = os.getenv("OPENAI_API_TYPE", "")
OPENAI_COMPLETIONS_ENGINE = os.getenv("OPENAI_COMPLETIONS_ENGINE", "text-davinci-003")

def create_vectorstore() -> Redis:
    """Create the Redis vectorstore."""
    import pandas as pd


    if OPENAI_API_TYPE=="azure":
        #currently Azure OpenAI embeddings require request for service limit increase to be useful
        #using build-in HuggingFace instead
        from langchain.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    else:
        from langchain.embeddings import OpenAIEmbeddings
        # Init OpenAI Embeddings
        embeddings = OpenAIEmbeddings()

    try:
        vectorstore = Redis.from_existing_index(
            embedding=embeddings,
            index_name=INDEX_NAME,
            redis_url=REDIS_URL
        )
        return vectorstore
    except:
        pass

    # Load and prepare wikipedia documents
    docs = pd.read_csv(
        "https://cdn.openai.com/API/examples/data/olympics_sections_text.csv").to_dict("records")
    texts = [doc["content"] for doc in docs]
    metadatas = [
        {
            "title": doc["title"],
            "heading": doc["heading"],
            "tokens": doc["tokens"]
        } for doc in docs
    ]

    # Load Redis with documents
    vectorstore = Redis.from_texts(
        texts=texts,
        metadatas=metadatas,
        embedding=embeddings,
        index_name="wiki",
        redis_url=REDIS_URL
    )
    return vectorstore


def make_qna_chain():
    """Create the QA chain."""
    from langchain.prompts import PromptTemplate
    from langchain.llms import OpenAI
    # from langchain.memory import ConversationBufferMemory
    # from langchain.memory import RedisChatMessageHistory
    from langchain.chains import RetrievalQA

    # Persist chat history in Redis
    #message_history = RedisChatMessageHistory(url=REDIS_URL, ttl=600, session_id='my-session')

    # Set up memory model for the LLM
    # memory = ConversationBufferMemory(
    #     #chat_memory=message_history,
    #     memory_key="chat_history",
    #     return_messages=True
    # )

    #Define our prompt
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

    chain_type_kwargs = {"prompt": prompt}

    if OPENAI_API_TYPE=="azure":
        #Azure OpenAI requires engine parameter
        chain = RetrievalQA.from_chain_type(
            llm=OpenAI(engine=OPENAI_COMPLETIONS_ENGINE),
            chain_type="stuff",
            retriever=redis.as_retriever(),
            return_source_documents=True,
            chain_type_kwargs=chain_type_kwargs
        )
    else:
        chain = RetrievalQA.from_chain_type(
            llm=OpenAI(),
            chain_type="stuff",
            retriever=redis.as_retriever(),
            return_source_documents=True,
            chain_type_kwargs=chain_type_kwargs
        )



    return chain
