import os
import pandas as pd

from langchain.vectorstores.redis import Redis
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.qa_chain import load_qa_chain


# Redis Env Vars
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Init OpenAI Embeddings and LLM
openai_embeddings = OpenAIEmbeddings()


def create_vector_db() -> Redis:
    docs = pd.read_csv("https://cdn.openai.com/API/examples/data/olympics_sections_text.csv").to_dict("records")
    texts = [doc["content"] for doc in docs]
    metadatas = {
        i: {
            "title": doc["title"],
            "heading": doc["heading"],
            "tokens": doc["tokens"]
        } for i, doc in enumerate(docs)
    }
    # Load Redis with documents
    vector_db = Redis.from_texts(
        texts=texts,
        metadatas=metadatas,
        embeddings=openai_embeddings,
        index_name="wiki",
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD
    )
    return vector_db

# Make QA
def make_qa(chain_type: str = "stuff"):
    # Prompt Template
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
    redis = create_vector_db()

    # Create QA Chain
    qa_chain = load_qa_chain(OpenAI(temperature=0), chain_type="stuff", prompt=prompt)

    # Create QA
    qa = VectorDBQA(
        combine_documents_chain=qa_chain,
        vectorstore=redis,
        return_source_documents=True
    )

    return qa