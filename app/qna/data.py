from typing import List

from langchain.schema import Document
from langchain.document_loaders import ArxivLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def get_olympics_docs() -> List[Document]:
    import pandas as pd
    # Load and prepare wikipedia documents
    datasource = pd.read_csv(
        "https://cdn.openai.com/API/examples/data/olympics_sections_text.csv"
    ).to_dict("records")
    # Create documents
    documents = [
        Document(
            page_content=doc["content"],
            metadata={
                "title": doc["title"],
                "heading": doc["heading"],
                "tokens": doc["tokens"]
            }
        ) for doc in datasource
    ]
    return documents


def get_arxiv_docs(paper_topic_query, num_docs=10) -> List[Document]:
    loader = ArxivLoader(
        paper_topic_query,
        load_max_docs=num_docs,
        load_all_available_meta=True
    )
    raw_documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size = 500,
    chunk_overlap  = 10,
    length_function = len,
    add_start_index = True,
    )
    documents = text_splitter.split_documents(raw_documents)
    return documents