
import typing as t

from . import llm


qa = llm.make_qa()

def answer_question_with_context(question: str):
    """
    Answer the question.

    Args:
        question (str): Input question from the user.

    Returns:
        source_documents (list): List of Documents used for context.
        result (str): Answer from the LLM.
    """
    result = qa({"query": question})
    return result['source_documents'], result['result']
