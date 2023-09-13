import os
import streamlit as st
import langchain

from dotenv import load_dotenv
load_dotenv()

from urllib.error import URLError
from qna.llm import make_qna_chain
from qna.db import get_cache, get_vectorstore
from qna.prompt import basic_prompt
from qna.data import get_olympics_docs


@st.cache_resource
def vector_db(_documents):
    return get_vectorstore(_documents)

@st.cache_resource
def fetch_llm_cache():
    return get_cache()

@st.cache_resource
def qna_chain(_vector_db, prompt, **kwargs):
    return make_qna_chain(_vector_db, prompt, **kwargs)

@st.cache_resource
def get_documents():
    return get_olympics_docs()

try:
    docs = get_documents()
    vdb = vector_db(docs)
    langchain.llm_cache = fetch_llm_cache()
    prompt = basic_prompt()
    qna_chain = qna_chain(vdb, prompt=prompt)

    default_question = ""
    default_answer = ""

    if 'question' not in st.session_state:
        st.session_state['question'] = default_question
    if 'response' not in st.session_state:
        st.session_state['response'] = {
            "choices" :[{
                "text" : default_answer
            }]
        }

    st.image(os.path.join('assets','RedisOpenAI.png'))

    col1, col2 = st.columns([4,2])
    with col1:
        st.write("# Q&A Application")
    # with col2:
    #     with st.expander("Settings"):
    #         st.tokens_response = st.slider("Tokens response length", 100, 500, 400)
    #         st.temperature = st.slider("Temperature", 0.0, 1.0, 0.1)


    question = st.text_input("*Ask thoughtful questions about the **2020 Summer Olympics***", default_question)

    if question != '':
        if question != st.session_state['question']:
            st.session_state['question'] = question
            with st.spinner("OpenAI and Redis are working to answer your question..."):
                result = qna_chain({"query": question})
                st.session_state['context'], st.session_state['response'] = result['source_documents'], result['result']
            st.write("### Response")
            st.write(f"{st.session_state['response']}")
            with st.expander("Show Q&A Context Documents"):
                if st.session_state['context']:
                    docs = "\n".join([doc.page_content for doc in st.session_state['context']])
                    st.text(docs)

    st.markdown("____")
    st.markdown("")
    st.write("## How does it work?")
    st.write("""
        The Q&A app exposes a dataset of wikipedia articles hosted by [OpenAI](https://openai.com/) (about the 2020 Summer Olympics). Ask questions like
        *"Which country won the most medals at the 2020 olympics?"* or *"Who won the men's high jump event?"*, and get answers!

        Everything is powered by OpenAI's embedding and generation APIs and [Redis](https://redis.com/redis-enterprise-cloud/overview/) as a vector database.

        There are 3 main steps:

        1. OpenAI's embedding service converts the input question into a query vector (embedding).
        2. Redis' vector search identifies relevant wiki articles in order to create a prompt.
        3. OpenAI's generative model answers the question given the prompt+context.

        See the reference architecture diagram below for more context.
    """)

    st.image(os.path.join('assets', 'RedisOpenAI-QnA-Architecture.drawio.png'))



except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )
