
import typing as t


from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.prompts.base import RegexParser

from . import db
# from .models import (
#     MAX_SECTION_LEN,
#     SEPARATOR,
#     SEPARATOR_LEN,
#     get_embedding,
#     get_completion
# )

redis_conn = db.init()
openai_embeddings = OpenAIEmbeddings()
openai_llm = OpenAI(temperature=0.1)
prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, say that you don't know, don't try to make up an answer.

This should be in the following format:

Question: [question here]
Answer: [answer here]

Begin!

Context:
---------
{summaries}
---------
Question: {question}
Answer:"""
prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["summaries", "question"]
)
qa_chain = load_qa_with_sources_chain(
    openai_llm,
    chain_type="stuff",
    prompt=prompt
)


def search_semantic_redis(search_query: str, n: int) -> t.List[Document]:
    """
    Search Redis using computed embeddings from OpenAI.

    Args:
        search_query (str): Text query to embed and use in document retrieval.
        n (int): Number of documents to consider.

    Returns:
        list[Document]: List of relevant Docs ordered by similarity score.
    """
    embedding = openai_embeddings.embed_query(search_query)
    return db.search_redis(
        redis_conn,
        query_vector=embedding,
        k=n,
        return_fields=["title", "content", "tokens"]
    )

# def construct_prompt(question: str) -> str:
#     """
#     Construct full prompt based on the input question using
#     the document sections indexed in Redis.

#     Args:
#         question (str): User input question.
#         pre_filter (str, optional): Pre filter to constrain the KNN search with conditions.

#     Returns:
#         str: Full prompt string to pass along to a generative language model.
#     """
#     chosen_sections = []
#     chosen_sections_len = 0
#     chosen_sections_indexes = []

#     # Search for relevant document sections based on the question
#     most_relevant_document_sections = search_semantic_redis(question, n = 5)

#     # Iterate through results
#     for document_section in most_relevant_document_sections:
#         # Add contexts until we run out of token space
#         chosen_sections_len += int(document_section['tokens']) + SEPARATOR_LEN
#         if chosen_sections_len > MAX_SECTION_LEN:
#             break

#         chosen_sections.append(SEPARATOR + document_section['content'].replace("\n", " "))
#         chosen_sections_indexes.append(document_section['id'])

#     # Useful diagnostic information
#     print(f"Selected {len(chosen_sections)} document sections:")
#     print("\n".join(chosen_sections_indexes))

#     return PROMPT_HEADER + "".join(chosen_sections) + "\n\n Q: " + question + "\n A:"

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
    most_relevant_docs = search_semantic_redis(question, n = 5)
    result = qa_chain({"input_documents": most_relevant_docs, "question": question})
    return result #get_completion(prompt, max_tokens=tokens_response, temperature=temperature)
