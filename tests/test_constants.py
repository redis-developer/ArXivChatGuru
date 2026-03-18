from qna.constants import (
    DEFAULT_CHAT_MODEL,
    get_chat_model_name,
    get_embedding_dimensions,
    get_index_name,
    get_index_prefix,
)


def test_chat_model_prefers_new_environment_variable(monkeypatch):
    monkeypatch.setenv("OPENAI_CHAT_MODEL", "gpt-4.1")
    monkeypatch.setenv("OPENAI_COMPLETIONS_ENGINE", "legacy-model")

    assert get_chat_model_name() == "gpt-4.1"


def test_chat_model_uses_default_when_no_environment_variables_exist(monkeypatch):
    monkeypatch.delenv("OPENAI_CHAT_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_COMPLETIONS_ENGINE", raising=False)

    assert get_chat_model_name() == DEFAULT_CHAT_MODEL


def test_embedding_dimensions_default_for_text_embedding_3_small(monkeypatch):
    monkeypatch.setenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    monkeypatch.delenv("OPENAI_EMBEDDING_DIMENSIONS", raising=False)

    assert get_embedding_dimensions() == 1536


def test_topic_specific_index_names_are_stable_and_unique():
    name_one = get_index_name("Graph neural networks")
    name_two = get_index_name("Database systems")

    assert name_one.startswith("arxiv-")
    assert name_two.startswith("arxiv-")
    assert name_one != name_two
    assert get_index_prefix("Graph neural networks").startswith("arxiv:")
