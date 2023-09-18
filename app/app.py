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
from qna.constants import REDIS_URL

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

def reset_app():
    st.session_state['previous_topic'] = ""
    st.session_state['arxiv_topic'] = ""
    st.session_state['arxiv_query'] = ""
    st.session_state['messages'].clear()

    arxiv_db = st.session_state['arxiv_db']
    if arxiv_db is not None:
        arxiv_db.drop_index(arxiv_db.index_name, delete_documents=True, redis_url=REDIS_URL)
        arxiv_db.client.flushall()
        st.session_state['arxiv_db'] = None


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
        "messages": [],
    }

    # Checking if keys exist in session state, if not, initializing them
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    with st.sidebar:
        st.write("## Settings")
        st.slider("Number of Context Documents", 2, 20, 2, key="num_context_docs")
        st.slider("Number of Tokens", 100, 500, 400, key="max_tokens")
        st.slider("Distance Threshold", .1, .9, .5, key="distance_threshold", step=.1)
        st.button("Clear Chat", key="clear_chat", on_click=lambda: st.session_state['messages'].clear())
        st.button("Clear Cache", key="reset", on_click=reset_app)

    st.write("## Arxiv Document Chat Application")

    st.write("**Put in a topic area and a question within that area to get an answer!**")
    topic = st.text_input("Topic Area", key="arxiv_topic")
    papers = st.number_input("Number of Papers", key="num_papers", value=10, min_value=1, max_value=50, step=2)


    if st.button("Chat!"):
        if is_updated(topic):
            st.session_state['previous_topic'] = topic
            with st.spinner("Loading information from Arxiv to answer your question..."):
                create_arxiv_index(st.session_state['arxiv_topic'], st.session_state['num_papers'], prompt)

    arxiv_db = st.session_state['arxiv_db']

    try:
        chain = make_qna_chain(
            arxiv_db,
            prompt=prompt,
            max_tokens=st.session_state["max_tokens"],
            k=st.session_state['num_context_docs'],
            search_type="similarity_distance_threshold",
            distance_threshold=st.session_state["distance_threshold"]
        )
        st.session_state['chain'] = chain
    except AttributeError:
        st.info("Please enter a topic area")
        st.stop()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if query := st.chat_input("What do you want to know about this topic?"):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            st.session_state['context'], st.session_state['response'] = [], ""
            chain = st.session_state['chain']

            result = chain({"query": query})
            st.markdown(result["result"])
            st.session_state['context'], st.session_state['response'] = result['source_documents'], result['result']
            if st.session_state['context']:
                with st.expander("Context"):
                    context = defaultdict(list)
                    for doc in st.session_state['context']:
                        context[doc.metadata['Title']].append(doc)
                    for i, doc_tuple in enumerate(context.items(), 1):
                        title, doc_list = doc_tuple[0], doc_tuple[1]
                        st.write(f"{i}. **{title}**")
                        for context_num, doc in enumerate(doc_list, 1):
                            st.write(f" - **Context {context_num}**: {doc.page_content}")

            st.session_state.messages.append({"role": "assistant", "content": st.session_state['response']})


except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )
