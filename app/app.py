import os
import streamlit as st
import langchain
langchain.debug = True
from collections import defaultdict

from dotenv import load_dotenv
load_dotenv()

from urllib.error import URLError
from qna.llm import make_qna_chain
from qna.db import get_cache, get_vectorstore
from qna.prompt import basic_prompt
from qna.data import get_olympics_docs, get_arxiv_docs

def arxiv_index(_arxiv_documents):
    return get_vectorstore(_arxiv_documents)

@st.cache_resource
def fetch_llm_cache():
    return get_cache()

@st.cache_resource
def create_arxiv_index(topic_query, _num_papers, _prompt):
    arxiv_documents = get_arxiv_docs(topic_query, _num_papers)
    arxiv_db = get_vectorstore(arxiv_documents)
    st.session_state['arxiv_db'] = arxiv_db
    return arxiv_db

def is_updated(topic):
    return (
        topic != st.session_state['previous_topic']
    )

try:
    langchain.llm_cache = fetch_llm_cache()
    prompt = basic_prompt()

    # Defining default values
    default_question = ""
    default_answer = ""
    defaults = {
        "response": {
            "choices" :[{
                "text" : default_answer
            }]
        },
        "question": default_question,
        "context": [],
        "chain": None,
        "previous_topic": "",
        "arxiv_topic": "",
        "arxiv_query": "",
        "arxiv_db": None,
    }

    # Checking if keys exist in session state, if not, initializing them
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    with st.sidebar:
        st.write("## Filter by Metadata")
        st.write("-----")
        st.write("## Settings")
        st.slider("Number of Context Documents", 2, 20, 2, key="num_context_docs")
        st.slider("Number of Tokens", 100, 500, 400, key="max_tokens")

    st.image(os.path.join('assets','RedisOpenAI.png'))

    col1, col2 = st.columns([4,2])
    with col1:
        st.write("## Arxiv Document Chat Application")
    # with col2:
    #     with st.expander("Settings"):
    #         st.tokens_response = st.slider("Tokens response length", 100, 500, 400)
    #         st.temperature = st.slider("Temperature", 0.0, 1.0, 0.1)


    st.write("**Put in a topic area and a question within that area to get an answer!**")
    topic = st.text_input("Topic Area", key="arxiv_topic")
    question = st.text_input("Question", key="arxiv_query")
    papers = st.number_input("Number of Papers", key="num_papers", value=10, min_value=1, max_value=50, step=2)

    if st.button("Find Answer"):
        if is_updated(topic):
            st.session_state['previous_topic'] = topic
            with st.spinner("Loading information from Arxiv to answer your question..."):
                create_arxiv_index(st.session_state['arxiv_topic'], st.session_state['num_papers'], prompt)

        with st.spinner("Answering your question..."):
            arxiv_db = st.session_state['arxiv_db']
            chain = make_qna_chain(
                arxiv_db,
                prompt=prompt,
                max_tokens=st.session_state["max_tokens"],
                k=st.session_state['num_context_docs']
            )
            result = chain({"query": st.session_state['arxiv_query']})

            st.session_state['context'], st.session_state['response'] = result['source_documents'], result['result']
            st.write("### Response")
            st.write(f"{st.session_state['response']}")

            st.write("")
            st.write("---")
            st.write("### Context")

            # collect context together and print
            if st.session_state['context']:
                context = defaultdict(list)
                for doc in st.session_state['context']:
                    context[doc.metadata['Title']].append(doc)
                for i, doc_tuple in enumerate(context.items(), 1):
                    title, doc_list = doc_tuple[0], doc_tuple[1]
                    st.write(f"{i}. **{title}**")
                    for context_num, doc in enumerate(doc_list, 1):
                        st.write(f" - **Context {context_num}**: {doc.page_content}")















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
