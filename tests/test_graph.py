from src.graph import build_graph
from src.llm import MockLLM
from src.memory import MemoryStore
from src.models import WorkflowState


def test_langgraph_retries_and_passes(tmp_path):

    llm = MockLLM()

    memory = MemoryStore(
        path=str(
            tmp_path / "memory.json"
        ),
    )

    graph = build_graph(
        llm=llm,
        memory=memory,
        max_attempts=3,
    )

    state = WorkflowState(
        topic="Introduction to RAG",

        learner_profile=(
            "12th-grade graduate from India "
            "with limited English vocabulary "
            "and no AI background."
        ),

        reference="""
        RAG retrieves relevant external information
        and provides it to a language model as context.

        RAG does not retrain the model for every question.
        """,

        rubric={
            "criteria": [
                {
                    "id": "accuracy",
                    "name": "Accuracy",
                    "description": (
                        "The lesson must be accurate."
                    ),
                }
            ]
        },
    )

    result = graph.invoke(state)

    assert result["status"] == "PASSED"

    assert result["attempt"] == 2

    assert len(
        result["rejection_log"]
    ) == 1