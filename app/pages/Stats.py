from urllib.error import URLError

import streamlit as st
from dotenv import load_dotenv
from redis.exceptions import ConnectionError, ResponseError

from qna.stats import build_attribute_rows, build_index_rows, build_stats_rows, get_index_info

load_dotenv()

try:
    st.title("Redis index stats")
    active_index_name = st.session_state.get("active_index_name", "")
    active_topic = st.session_state.get("loaded_topic", "")

    if not active_index_name:
        st.info("Load papers from the main app to inspect the active Redis index.")
        st.stop()

    if active_topic:
        st.caption(f"Inspecting Redis index `{active_index_name}` for topic `{active_topic}`.")

    try:
        index_info = get_index_info(active_index_name)
        st.write("## Index information")
        st.table(build_index_rows(index_info))

        st.write("## Index fields")
        st.table(build_attribute_rows(index_info))

        st.write("## Statistics")
        st.table(build_stats_rows(index_info))
    except ConnectionError as e:
        st.error(
            """
            **Could not connect to Redis**
            Connection error: %s
            """
            % e
        )
    except ResponseError as e:
        st.error(
            """
            **Could not load the active Redis index**
            Response error: %s
            """
            % e
        )

except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )
