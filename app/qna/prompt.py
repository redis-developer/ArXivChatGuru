from langchain.prompts import PromptTemplate

def condense_prompt():
    _template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.

    Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:"""
    return PromptTemplate.from_template(_template)

def basic_prompt():
    # Define our prompt
    prompt_template = """You are an AI assistant for answering questions about technical topics.
    You are given the following extracted parts of long documents and a question. Provide a conversational answer.
    If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.

    Question: {question}
    =========
    {context}
    =========
    Answer in Markdown:
    """

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"],
    )
