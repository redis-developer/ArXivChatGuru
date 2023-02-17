from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.prompts.base import RegexParser

# Init OpenAI Embeddings and LLM
openai_embeddings = OpenAIEmbeddings()

# Make QA Chain
def make_qa_chain(chain_type: str = "stuff"):
    # Prompt Template
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
    # Create QA Chain
    qa_chain = load_qa_with_sources_chain(
        OpenAI(temperature=0.1),
        chain_type=chain_type,
        prompt=prompt
    )
    return qa_chain