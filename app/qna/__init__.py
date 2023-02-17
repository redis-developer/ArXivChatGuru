
import typing as t

from . import db
from . import llm


redis_conn = db.init()
qa_chain = llm.make_qa_chain()


def search_semantic_redis(search_query: str, n: int) -> t.List[Document]:
    """
    Search Redis using computed embeddings from OpenAI.

    Args:
        search_query (str): Text query to embed and use in document retrieval.
        n (int): Number of documents to consider.

    Returns:
        list[Document]: List of relevant Docs ordered by similarity score.
    """
    embedding = llm.openai_embeddings.embed_query(search_query)
    return db.search_redis(
        redis_conn,
        k=n,
        query_vector=embedding,
        return_fields=["title", "content", "tokens"]
    )


def answer_question_with_context(question: str) -> t.Tuple(t.List[Document], str):
    """
    Answer the question.

    Args:
        question (str): Input question from the user.

    Returns:
        input_documents (list): List of Documents used for context.
        output_text (str): Answer from the LLM.
    """
    most_relevant_docs = search_semantic_redis(question, n=5)
    result = qa_chain({"input_documents": most_relevant_docs, "question": question})
    return result['input_documents'], result['output_text']
