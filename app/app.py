import os
import langchain
import streamlit as st

from collections import defaultdict
from urllib.error import URLError
from dotenv import load_dotenv
load_dotenv()

if os.environ.get("QNA_DEBUG") == "true":
    langchain.debug = True

from qna.llm import make_qna_chain, get_llm
from qna.db import get_vectorstore#, get_cache
from qna.prompt import basic_prompt
from qna.data import get_arxiv_docs
from qna.constants import REDIS_URL

# @st.cache_resource
# def fetch_llm_cache():
#     return get_cache()

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
        #clear_cache()
        arxiv_db.index.clear()


# def clear_cache():
#     if not st.session_state["llm"]:
#         st.warning("Could not find llm to clear cache of")
#     llm = st.session_state["llm"]
#     llm_string = llm._get_llm_string()
#     langchain.llm_cache.clear(llm_string=llm_string)


try:
    #langchain.llm_cache = fetch_llm_cache()
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
        "llm": None,
        "messages": [],
    }

    # Checking if keys exist in session state, if not, initializing them
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    with st.sidebar:
        st.write("## LLM Settings")
        ##st.write("### Prompt") TODO make possible to change prompt
        st.write("Change these before you run the app!")
        st.slider("Number of Tokens", 100, 8000, 400, key="max_tokens")

        st.write("## Retrieval Settings")
        st.write("Feel free to change these anytime")
        st.slider("Number of Context Documents", 2, 20, 2, key="num_context_docs")

        st.write("## App Settings")
        st.button("Clear Chat", key="clear_chat", on_click=lambda: st.session_state['messages'].clear())
        #st.button("Clear Cache", key="clear_cache", on_click=clear_cache)
        st.button("New Conversation", key="reset", on_click=reset_app)

    col1, col2 = st.columns(2)
    with col1:
        st.title("Arxiv ChatGuru")
        st.write("**Put in a topic area and a question within that area to get an answer!**")
        topic = st.text_input("Topic Area", key="arxiv_topic")
        papers = st.number_input("Number of Papers", key="num_papers", value=10, min_value=1, max_value=50, step=2)
    with col2:
        st.image("./assets/arxivguru_crop.png")



    if st.button("Chat!"):
        if is_updated(topic):
            st.session_state['previous_topic'] = topic
            with st.spinner("Loading information from Arxiv to answer your question..."):
                create_arxiv_index(st.session_state['arxiv_topic'], st.session_state['num_papers'], prompt)

    arxiv_db = st.session_state['arxiv_db']
    if st.session_state["llm"] is None:
        tokens = st.session_state["max_tokens"]
        st.session_state["llm"] = get_llm(max_tokens=tokens)
    try:
        chain = make_qna_chain(
            st.session_state["llm"],
            arxiv_db,
            prompt=prompt,
            k=st.session_state['num_context_docs'],
            search_type="similarity"
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

        with st.chat_message("assistant", avatar="./assets/arxivguru_crop.png"):
            message_placeholder = st.empty()
            st.session_state['context'], st.session_state['response'] = [], ""
            chain = st.session_state['chain']

            result = chain({"query": query})
            print(result, flush=True)
            st.markdown(result["result"])
            st.session_state['context'], st.session_state['response'] = result['source_documents'], result['result']
            if st.session_state['context']:
                with st.expander("Context"):
                    context = defaultdict(list)
                    for doc in st.session_state['context']:
                        context[doc.metadata['title']].append(doc)
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
