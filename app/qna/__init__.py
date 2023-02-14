
import typing as t

from . import db
from .models import (
    MAX_SECTION_LEN,
    SEPARATOR,
    SEPARATOR_LEN,
    get_embedding,
    get_completion
)

redis_conn = db.init()
PROMPT_HEADER = """Answer the question as truthfully as possible using the provided context, and if the answer is not contained within the text below, say "I don't know."\n\nContext:\n"""

def search_semantic_redis(search_query: str, n: int) -> t.List[dict]:
    """
    Search Redis using computed embeddings from OpenAI.

    Args:
        search_query (str): Text query to embed and use in document retrieval.
        n (int): Number of documents to consider.

    Returns:
        list<dict>: List of relevant documents ordered by similarity score.
    """
    embedding = get_embedding(text=search_query)
    return db.search_redis(
        redis_conn,
        query_vector=embedding,
        k=n,
        return_fields=["title", "content", "tokens"]
    )

def construct_prompt(question: str) -> str:
    """
    Construct full prompt based on the input question using
    the document sections indexed in Redis.

    Args:
        question (str): User input question.
        pre_filter (str, optional): Pre filter to constrain the KNN search with conditions.

    Returns:
        str: Full prompt string to pass along to a generative language model.
    """
    chosen_sections = []
    chosen_sections_len = 0
    chosen_sections_indexes = []

    # Search for relevant document sections based on the question
    most_relevant_document_sections = search_semantic_redis(question, n = 5)

    # Iterate through results
    for document_section in most_relevant_document_sections:
        # Add contexts until we run out of token space
        chosen_sections_len += int(document_section['tokens']) + SEPARATOR_LEN
        if chosen_sections_len > MAX_SECTION_LEN:
            break

        chosen_sections.append(SEPARATOR + document_section['content'].replace("\n", " "))
        chosen_sections_indexes.append(document_section['id'])

    # Useful diagnostic information
    print(f"Selected {len(chosen_sections)} document sections:")
    print("\n".join(chosen_sections_indexes))

    return PROMPT_HEADER + "".join(chosen_sections) + "\n\n Q: " + question + "\n A:"

def answer_question_with_context(
    question: str,
    show_prompt: bool = False,
    explicit_prompt: str = "",
    tokens_response=100,
    temperature=0.0
) -> str:
    """
    Answer the question.

    Args:
        question (str): Input question from the user.
        show_prompt (bool, optional): Print out the prompt? Defaults to False.
        explicit_prompt (str, optional): Use an explicit prompt provided by user? Defaults to "".
        tokens_response (int, optional): Max number of tokens in the response. Defaults to 100.
        temperature (float, optional): Model temperature. Defaults to 0.0.

    Returns:
        str: _description_
    """
    if explicit_prompt == "":
        # Construct prompt with Redis Vector Search
        prompt = construct_prompt(question)
    else:
        prompt = f"{explicit_prompt}\n\n{question}"

    if show_prompt:
        print(prompt)

    return get_completion(prompt, max_tokens=tokens_response, temperature=temperature)
