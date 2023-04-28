

<img src="./app/assets/RedisOpenAI.png" alt="Drawing" style="width: 100%;"/> </td>


# Question & Answering using LangChain, Redis & OpenAI

**LangChain** simplifies the development of LLM applications through modular components and "chains". It acts as a wrapper around several complex tools and makes us more efficient in our development workflow.

**Redis** plays a crucial role with large language models (LLMs) for a few resons. It can store and retrieve data in near realtime (for caching) and can also index vector embeddings for semantic search. Semantic search enables the LLM to attach to external memory or "knowledge" to help augment the LLM prompts and ensure greater quality in results. Redis has both the developer community and enterprise-readiness required to deploy quality AI-enabled applications in this demanding marketplace.

**OpenAI** is shaping the future of next-gen apps through it's release of powerful natural language and computer vision models that are used in a variety of downstream tasks.

This example Streamlit app gives you the tools to get up and running with **Redis** as a vector database, **OpenAI** as a LLM provider for embedding creation and text generation, and **LangChain** for application dev. *The combination of these is what makes things happen.*

![ref arch](app/assets/RedisOpenAI-QnA-Architecture.drawio.png)

____

## Create dev env (*optional*)
Use the provided conda env for development:
```bash
conda env create -f environment.yml
```

## Run the App
The example QnA application uses a dataset from wikipedia of articles about the 2020 summer olympics. The **first time you run the app** -- all docs will be downloaded, processed, and stored in Redis. This will take a few minutes to spin up initially. From that point forward, the app should be quicker to load.

### Use Docker Compose
Create your env file:
```bash
$ cp .env.template .env
```
*fill out values, most importantly, your `OPENAI_API_KEY`.*

Run with docker compose:
```bash
$ docker compose up
```
*add `-d` option to daemonize the processes to the background if you wish.*

Navigate to:
```
http://localhost:8080/
```


**NOW: Ask the app anything about the 2020 Summer Olympics!**