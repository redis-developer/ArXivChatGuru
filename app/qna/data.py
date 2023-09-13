from typing import List

from langchain.schema import Document

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
