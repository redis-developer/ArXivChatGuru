from qna.prompt import basic_prompt


def test_basic_prompt_formats_question_and_context():
    prompt = basic_prompt()

    rendered = prompt.format(context="Context block", question="What is the paper about?")

    assert prompt.input_variables == ["context", "question"]
    assert "Context block" in rendered
    assert "What is the paper about?" in rendered
    assert "Answer in Markdown" in rendered
