from src.models import WorkflowState
from src.generator import generate_lesson
from src.evaluator import evaluate_lesson
from src.llm import LLMClient


# ============================================================
# GENERATE
# ============================================================

def generate_node(
    state: WorkflowState,
    llm: LLMClient,
):
    """
    Generate a lesson.

    On the first attempt, no feedback is provided.

    On subsequent attempts, evaluator recommendations are
    converted into feedback for the generator.
    """

    attempt = state.attempt + 1

    feedback = ""

    if state.evaluation is not None:
        feedback = "\n".join(
            state.evaluation.recommendations
        )

    lesson = generate_lesson(
        llm=llm,
        topic=state.topic,
        learner_profile=state.learner_profile,
        reference=state.reference,
        feedback=feedback,
    )

    state.lesson = lesson
    state.attempt = attempt
    state.status = "RUNNING"

    return state


# ============================================================
# EVALUATE
# ============================================================

def evaluate_node(
    state: WorkflowState,
    llm: LLMClient,
):
    """
    Evaluate the current lesson.
    """

    evaluation = evaluate_lesson(
        llm=llm,
        topic=state.topic,
        lesson=state.lesson,
        reference=state.reference,
        rubric=state.rubric,
    )

    state.evaluation = evaluation

    return state


# ============================================================
# RUN WORKFLOW
# ============================================================

def run_workflow(
    state: WorkflowState,
    llm: LLMClient,
    max_attempts: int = 3,
):
    """
    Run the generate -> evaluate -> retry workflow.

    Flow:

        GENERATE
           |
        EVALUATE
           |
       +---+---+
       |       |
      PASS    FAIL
       |       |
      END    RETRY
               |
          GENERATE AGAIN
    """

    state.max_attempts = max_attempts

    while state.attempt < state.max_attempts:

        # ----------------------------------------------------
        # Generate
        # ----------------------------------------------------

        state = generate_node(
            state=state,
            llm=llm,
        )

        # ----------------------------------------------------
        # Evaluate
        # ----------------------------------------------------

        state = evaluate_node(
            state=state,
            llm=llm,
        )

        # ----------------------------------------------------
        # Check result
        # ----------------------------------------------------

        if (
            state.evaluation is not None
            and state.evaluation.overall_status == "PASS"
        ):
            state.status = "PASSED"
            return state

        # ----------------------------------------------------
        # Record rejection
        # ----------------------------------------------------

        if state.evaluation is not None:

            state.rejection_log.append(
                {
                    "attempt": state.attempt,
                    "failures": list(
                        state.evaluation.failures
                    ),
                    "recommendations": list(
                        state.evaluation.recommendations
                    ),
                }
            )

        # ----------------------------------------------------
        # If maximum attempts reached
        # ----------------------------------------------------

        if state.attempt >= state.max_attempts:
            state.status = "FAILED"
            return state

        # ----------------------------------------------------
        # Otherwise loop and retry
        # ----------------------------------------------------

    state.status = "FAILED"

    return state