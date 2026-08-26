from src.generator import generate_lesson
from src.llm import MockLLM


def test_generator_returns_lesson():

    llm = MockLLM()

    lesson = generate_lesson(
        llm=llm,
        topic="Introduction to RAG",
        learner_profile=(
            "12th-grade graduate from India with limited English "
            "vocabulary and no AI background."
        ),
        reference=(
            "RAG retrieves relevant external information and "
            "provides it to a language model as context."
        ),
    )

    assert isinstance(lesson, str)
    assert len(lesson) > 100


def test_generator_changes_after_second_attempt():

    llm = MockLLM()

    first_lesson = generate_lesson(
        llm=llm,
        topic="Introduction to RAG",
        learner_profile="Beginner learner",
        reference="RAG retrieves external information.",
    )

    second_lesson = generate_lesson(
        llm=llm,
        topic="Introduction to RAG",
        learner_profile="Beginner learner",
        reference="RAG retrieves external information.",
        feedback=(
            "The first lesson incorrectly said that RAG retrains "
            "the model for every question."
        ),
    )

    assert first_lesson != second_lesson