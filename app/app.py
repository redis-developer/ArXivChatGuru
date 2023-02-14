import os
import streamlit as st

from urllib.error import URLError
from qna import answer_question_with_context
from dotenv import load_dotenv
load_dotenv()

try:

    default_prompt = ""
    default_question = ""
    default_answer = ""

    if 'question' not in st.session_state:
        st.session_state['question'] = default_question
    if 'prompt' not in st.session_state:
        st.session_state['prompt'] = default_prompt
    if 'response' not in st.session_state:
        st.session_state['response'] = {
            "choices" :[{
                "text" : default_answer
            }]
        }

    col1 = st.columns([1])
    with col1:
        st.image(os.path.join('assets','RedisOpenAI.png'))

    col1, col2, col3 = st.columns([2,2,2])
    with col3:
        with st.expander("Settings"):
            st.tokens_response = st.slider("Tokens response length", 100, 500, 400)
            st.temperature = st.slider("Temperature", 0.0, 1.0, 0.1)


    question = st.text_input("Ask questions about the 2020 Summer Olympics", default_question)

    if question != '':
        if question != st.session_state['question']:
            st.session_state['question'] = question
            st.session_state['prompt'], st.session_state['response'] = answer_question_with_context(
                question,
                tokens_response=st.tokens_response,
                temperature=st.temperature
            )
            st.write(f"Q: {question}")
            st.write(st.session_state['response']['choices'][0]['text'])
            with st.expander("Show Question and Answer Context"):
                st.text(st.session_state['prompt'])
        else:
            st.write(f"Q: {st.session_state['question']}")
            st.write(f"{st.session_state['response']['choices'][0]['text']}")
            with st.expander("Question and Answer Context"):
                st.text(st.session_state['prompt'].encode().decode())


except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )
