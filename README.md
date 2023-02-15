

<img src="./app/assets/RedisOpenAI.png" alt="Drawing" style="width: 100%;"/> </td>


# Question & Answering using Redis & OpenAI

**Redis** plays a crucial role in the LLM & GenAI wave with it's ability to store, retrieve, and search with vector spaces in a low-latency, high-availability setting. With its heritage in enterprise caching, Redis has both the developer community and enterprise-readiness required to deploy quality AI-enabled applications in this demanding marketplace.

**OpenAI** is shaping the future of next-gen apps through it's release of powerful natural language and computer vision models that are used in a variety of downstream tasks.

This example Streamlit app gives you the tools to get up and running with **Redis** as a vector database and **OpenAI** as a LLM provider for embedding creation and text generation. *The combination of the two is where the magic lies.*

![ref arch](app/assets/RedisOpenAI-QnA-Architecture.drawio.png)

____


## Run the App

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

The **first time you run the app** -- all documents will be downloaded, processed, and stored in Redis. This will take a few minutes to spin up initially. From that point forward, the app should be quicker to load.

**Ask the app anything about the 2020 Summer Olympics...**