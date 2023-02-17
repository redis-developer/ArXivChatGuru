import os
import openai
import typing as t





from transformers import GPT2TokenizerFast
from tenacity import (
    retry,
    wait_random_exponential,
    stop_after_attempt
)


MAX_SECTION_LEN = 750
SEPARATOR = "\n* "
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
SEPARATOR_LEN = len(tokenizer.tokenize(SEPARATOR))
print(f"Context separator contains {SEPARATOR_LEN} tokens")


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_embedding(text: str, model: str = OPENAI_EMBEDDINGS_ENGINE) -> t.List[float]:
    """
    Fetch embedding given input text from OpenAI.

    Args:
        text (str): Text input for which to create embedding.
        model (str): OpenAI model to use for embedding creation.

    Returns:
        t.List[float]: OpenAI Embedding.
    """
    # replace newlines, which can negatively affect performance.
    text = text.replace("\n", " ")
    result = openai.Embedding.create(
      engine=model,
      input=text
    )
    return result["data"][0]["embedding"]

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_completion(prompt: str, max_tokens: int = 400, temperature: float = 1.0):
    """
    Get completion for question answering from the OpenAI API.

    Args:
        prompt (str): Prompt to pass through to the OpenAI generative model.
        max_tokens (int, optional): Maximum tokens to user in the response. Defaults to 400.
        temperature (float, optional): Model temperature. Defaults to 1.0.
    """
    response = openai.Completion.create(
        engine=OPENAI_COMPLETIONS_ENGINE,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=0.5,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    print(f"{response['choices'][0]['text'].encode().decode()}\n\n\n")
    return prompt, response#, res['page'][0]
