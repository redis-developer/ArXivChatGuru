import os
from collections import defaultdict
from pathlib import Path
from urllib.error import URLError

import langchain
import streamlit as st
from dotenv import load_dotenv

from qna.constants import get_index_name
from qna.data import get_arxiv_docs
from qna.db import clear_vectorstore, get_vectorstore
from qna.llm import get_llm, make_qna_chain
from qna.prompt import basic_prompt

load_dotenv()

if os.environ.get("QNA_DEBUG") == "true":
    langchain.debug = True

ASSETS_DIR = Path(__file__).parent / "assets"
APP_AVATAR = str(ASSETS_DIR / "arxivguru_crop.png")


def create_arxiv_index(topic_query: str, num_papers: int):
    arxiv_documents = get_arxiv_docs(topic_query, num_papers)
    arxiv_db = get_vectorstore(arxiv_documents, topic_query)
    st.session_state["arxiv_db"] = arxiv_db
    return arxiv_db


def should_reload_index(topic: str, num_papers: int) -> bool:
    return (
        st.session_state["arxiv_db"] is None
        or topic != st.session_state["loaded_topic"]
        or num_papers != st.session_state["loaded_num_papers"]
    )


def clear_chat() -> None:
    st.session_state["messages"].clear()


def reset_app() -> None:
    clear_vectorstore(st.session_state.get("arxiv_db"))
    st.session_state["arxiv_topic"] = ""
    st.session_state["messages"] = []
    st.session_state["arxiv_db"] = None
    st.session_state["loaded_topic"] = ""
    st.session_state["loaded_num_papers"] = None
    st.session_state["active_index_name"] = ""


try:
    prompt = basic_prompt()
    defaults = {
        "response": "",
        "context": [],
        "arxiv_topic": "",
        "arxiv_db": None,
        "loaded_topic": "",
        "loaded_num_papers": None,
        "active_index_name": "",
        "messages": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    with st.sidebar:
        st.write("## LLM Settings")
        st.write("Change these before you load a topic into Redis.")
        st.slider("Number of Tokens", 100, 8000, 400, key="max_tokens")

        st.write("## Retrieval Settings")
        st.write("You can change retrieval settings at any time.")
        st.slider("Number of Context Documents", 2, 20, 2, key="num_context_docs")

        st.write("## App Settings")
        st.button("Clear Chat", key="clear_chat", on_click=clear_chat)
        st.button("New Conversation", key="reset", on_click=reset_app)

    col1, col2 = st.columns(2)
    with col1:
        st.title("ArXiv ChatGuru")
        st.write(
            "Load a topic-specific paper set into Redis, then ask grounded questions about that research area."
        )
        topic = st.text_input("Topic Area", key="arxiv_topic")
        papers = st.number_input(
            "Number of Papers",
            key="num_papers",
            value=10,
            min_value=1,
            max_value=50,
            step=1,
        )
    with col2:
        st.image(APP_AVATAR)

    if st.session_state["loaded_topic"]:
        st.caption(
            f"Loaded topic: `{st.session_state['loaded_topic']}` using Redis index "
            f"`{st.session_state['active_index_name']}`."
        )

    if topic and st.session_state["loaded_topic"] and topic != st.session_state["loaded_topic"]:
        st.warning("The topic input changed. Load papers again to switch the Redis index.")

    if papers != st.session_state["loaded_num_papers"] and st.session_state["loaded_topic"]:
        st.warning("The paper count changed. Load papers again to rebuild the Redis index.")

    if st.button("Load papers into Redis"):
        topic = topic.strip()
        if not topic:
            st.warning("Enter a topic before loading papers.")
        elif should_reload_index(topic, papers):
            if st.session_state["arxiv_db"] is not None:
                clear_vectorstore(st.session_state["arxiv_db"])
            with st.spinner("Loading papers from arXiv and indexing them in Redis..."):
                arxiv_db = create_arxiv_index(topic, papers)
            st.session_state["arxiv_db"] = arxiv_db
            st.session_state["loaded_topic"] = topic
            st.session_state["loaded_num_papers"] = papers
            st.session_state["active_index_name"] = get_index_name(topic)
            st.success("Redis index is ready. Ask a question below.")
        else:
            st.info("This topic is already loaded. Ask a question below.")

    arxiv_db = st.session_state["arxiv_db"]
    if arxiv_db is None:
        st.info("Load a topic into Redis before starting the chat.")
        st.stop()

    llm = get_llm(max_tokens=st.session_state["max_tokens"])
    chain = make_qna_chain(
        llm,
        arxiv_db,
        prompt=prompt,
        k=st.session_state["num_context_docs"],
        search_type="similarity",
    )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if query := st.chat_input("What do you want to know about this topic?"):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant", avatar=APP_AVATAR):
            st.session_state["context"], st.session_state["response"] = [], ""
            result = chain({"query": query})
            st.markdown(result["result"])
            st.session_state["context"] = result["source_documents"]
            st.session_state["response"] = result["result"]

            if st.session_state["context"]:
                with st.expander("Context"):
                    context = defaultdict(list)
                    for doc in st.session_state["context"]:
                        context[doc.metadata["title"]].append(doc)
                    for i, (title, doc_list) in enumerate(context.items(), 1):
                        st.write(f"{i}. **{title}**")
                        for context_num, doc in enumerate(doc_list, 1):
                            st.write(f" - **Context {context_num}**: {doc.page_content}")

            st.session_state.messages.append(
                {"role": "assistant", "content": st.session_state["response"]}
            )

except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )
