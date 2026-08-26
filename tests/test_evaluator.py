from src.evaluator import evaluate_lesson
from src.llm import MockLLM
from src.models import EvaluationResult


def test_evaluator_returns_structured_result():

    llm = MockLLM()

    lesson = """
    RAG retrains the language model whenever a user asks a question.
    """

    rubric = {
        "criteria": [
            {
                "id": "accuracy",
                "name": "Accuracy",
                "description": "The lesson must be accurate."
            }
        ]
    }

    reference = """
    RAG retrieves external information and provides it
    to a language model as context.
    """

    result = evaluate_lesson(
        llm=llm,
        topic="Introduction to RAG",
        lesson=lesson,
        reference=reference,
        rubric=rubric,
    )

    assert isinstance(result, EvaluationResult)
    assert result.overall_status == "FAIL"