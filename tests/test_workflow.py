from src.llm import MockLLM
from src.models import WorkflowState
from src.workflow import run_workflow


def test_workflow_retries_after_failure():

    llm = MockLLM()

    state = WorkflowState(
        topic="Introduction to RAG",
        learner_profile=(
            "12th-grade graduate from India with limited English "
            "vocabulary and no AI background."
        ),
        reference="""
        RAG retrieves relevant external information and provides
        it to a language model as context. RAG does not retrain
        the model for every question.
        """,
        rubric={
            "criteria": [
                {
                    "id": "accuracy",
                    "name": "Accuracy",
                    "description": "The lesson must be accurate."
                }
            ]
        },
    )

    final_state = run_workflow(
        state=state,
        llm=llm,
        max_attempts=3,
    )

    assert final_state.status == "PASSED"
    assert final_state.attempt == 2
    assert len(final_state.rejection_log) == 1