
<div align="center">
    <a href="https://github.com/redis-developer/redis-ai-resources"><img src="./app/assets/arxivguru_crop.png" width="30%"><img></a>
</div>

# ArXiv ChatGuru

Welcome to **ArXiv ChatGuru**. This tool harnesses `LangChain` and `Redis` to make ArXiv's vast collection of scientific papers more interactive. Through this approach, we aim to make accessing and understanding research easier and more engaging, but also just to teach about how Retrieval Augmented Generation (RAG) systems work.

## 📖 How it Works

This diagram shows the process how ArXiv ChatGuru works. The user submits a topic, which is used to retrieve relevant papers from ArXiv. These papers are then chunked into smaller pieces, for which embeddings are generated. These embeddings are stored in Redis, which is used as a vector database. The user can then ask questions about the papers retrieved by the topic they submitted, and the system will return the most relevant answer.

![ref arch](app/assets/diagram.png#gh-light-mode-only)
![ref arch](app/assets/diagram-dark.png#gh-dark-mode-only)

## 🛠 Components

1. **LangChain's ArXiv Loader**: Efficiently pull scientific literature directly from ArXiv.
2. **Chunking + Embedding**: Using LangChain, we segment lengthy papers into manageable pieces (rather arbitrarily currently), for which we then generate embeddings.
3. **Redis**: Demonstrating fast and efficient vector storage, indexing, and retrieval for RAG.
4. **RetrievalQA**: Building on LangChain's RetrievalQA and OpenAI models, users can write queries about papers retrieved by the topic they submit.
5. **Python Libraries**: Making use of tools such as [`redisvl`](https://redisvl.com), [`Langchain`](https://www.langchain.com/), [`Streamlit`](https://streamlit.io/), etc

## 💡 Learning Outcomes with ArXiv ChatGuru

- **Context Window Exploration**: Learn about the importance of context window size and how it influences interaction results.
- **Vector Distance Insights**: Understand the role of vector distance in context retrieval for RAG and see how adjustments can change response specificity.
- **Document Retrieval Dynamics**: Observe how the number of documents retrieved can influence the performance of a RAG (Retriever-Augmented Generation) system.
- **Using Redis as a Vector DB and Semantic Cache**: Learn how to use Redis as a vector database for RAG systems and how to use it as a semantic cache for RAG systems.


**Note**: This **is not** a production application. It's a learning tool more than anything. We're using Streamlit to make it easy to interact with, but it's not meant to be a scalable application. It's meant to be a learning tool for understanding how RAG systems work, and how they can be used to make scientific literature more interactive. We will continue to make this better over time.


🌟 If you love what we're doing, give us a star! Contributions and feedback are always welcome. 🌌🔭

## Up Next

What we want to do next (ideas welcome!):

- [x] Pin stable versions of dependencies using poetry
- Filters for Year, Author, etc.
- More efficient chunking
- Various LLM caching toggles
- Chat history and conversational memory in Redis

____

## Run the App

### Run Locally

1. First, clone this repo and cd into it.
    ```bash
    $ git clone https://github.com/RedisVentures/ArxivChatGuru.git && cd ArxivChatGuru
    ```

2. Create your env file:
    ```bash
    $ cp .env.template .env
    ```
    *fill out values, most importantly, your `OPENAI_API_KEY`.*

3. Install dependencies with Poetry:
    ```bash
    $ poetry install --no-root
    ```

4. Run the app:
    ```bash
    $ poetry run streamlit run app.py --server.fileWatcherType none --browser.gatherUsageStats false --server.enableXsrfProtection false --server.address 0.0.0.0
    ```

5. Navigate to:
    ```
    http://localhost:8501/
    ```


### Docker Compose

First, clone the repo like above.

1. Create your env file:
    ```bash
    $ cp .env.template .env
    ```
    *fill out values, most importantly, your `OPENAI_API_KEY`.*

2. Run with docker compose:
    ```bash
    $ docker compose up
    ```
    *add `-d` option to daemonize the processes to the background if you wish.*

    Issues with dependencies? Try force-building with no-cache:
    ```
    $ docker compose build --no-cache
    ```

3. Navigate to:
    ```
    http://localhost:8501/
    ```
