import streamlit as st

from urllib.error import URLError
from redisvl.redis.utils import make_dict
from redisvl.index import SearchIndex
from redisvl.schema import IndexSchema
from redis.exceptions import ConnectionError, ResponseError
from tabulate import tabulate
from dotenv import load_dotenv
load_dotenv()

from qna.constants import REDIS_URL

STATS_KEYS = [
    "num_docs",
    "num_records",
    "number_of_uses",
    "percent_indexed",
    "total_indexing_time",
    "bytes_per_record_avg",
    "records_per_doc_avg",
    "doc_table_size_mb",
    "vector_index_sz_mb",
]


def display_stats(index_info, output_format="html"):
    # Extracting the statistics
    stats_data = [(key, str(index_info.get(key))) for key in STATS_KEYS]

    # Display the statistics in tabular format
    st.write("## Statistics:")
    st.write(
        tabulate(
            stats_data,
            headers=["Stat Key", "Value"],
            tablefmt=output_format,
            colalign=("left", "left"),
        ), unsafe_allow_html=True
    )

def display_index_stats(index_info, output_format="html"):
    attributes = index_info.get("attributes", [])
    definition = make_dict(index_info.get("index_definition"))
    index_info = [
        index_info.get("index_name"),
        definition.get("key_type"),
        definition.get("prefixes"),
        index_info.get("index_options"),
        index_info.get("indexing"),
    ]

    # Display the index information in tabular format
    st.write("## Index Information:")
    st.write(
        tabulate(
            [index_info],
            headers=[
                "Index Name",
                "Storage Type",
                "Prefixes",
                "Index Options",
                "Indexing",
            ],
            tablefmt=output_format,
        ), unsafe_allow_html=True
    )

    attr_values = []
    headers = [
        "Name",
        "Attribute",
        "Type",
    ]

    for attrs in attributes:
        attr = make_dict(attrs)

        values = [attr.get("identifier"), attr.get("attribute"), attr.get("type")]
        if len(attrs) > 5:
            options = make_dict(attrs)
            for k, v in options.items():
                if k not in ["identifier", "attribute", "type"]:
                    headers.append("Field Option")
                    headers.append("Option Value")
                    values.append(k)
                    values.append(v)
        attr_values.append(values)

    # Display the attributes in tabular format
    st.write("## Index Fields:")
    st.write(
        tabulate(
            attr_values,
            headers=headers,
            tablefmt=output_format,
        ), unsafe_allow_html=True
    )

try:

    try:
        schema = IndexSchema.from_yaml("qna/arxiv.yaml")
        index = SearchIndex.from_existing(name=schema.index.name, redis_url=REDIS_URL)
        index_info = index.info()
        display_index_stats(index_info)
        display_stats(index_info)

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
            **Could not connect to index for demo**
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
