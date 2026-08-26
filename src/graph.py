from typing import Callable

from langgraph.graph import StateGraph, END

from src.models import WorkflowState
from src.generator import generate_lesson
from src.evaluator import evaluate_lesson
from src.llm import LLMClient
from src.memory import MemoryStore


# ============================================================
# GENERATE NODE
# ============================================================

def generate_node(
    state: WorkflowState,
    llm: LLMClient,
    memory: MemoryStore,
):
    """
    Generate a lesson.

    On the first attempt, generate normally.

    On retry, include the evaluator's recommendations so
    the generator can improve the previous lesson.
    """

    attempt = state.attempt + 1

    feedback = ""

    if state.evaluation is not None:
        feedback = "\n".join(
            state.evaluation.recommendations
        )

    # IMPORTANT:
    # Do NOT pass attempt unless generate_lesson()
    # explicitly accepts an attempt parameter.
    lesson = generate_lesson(
        llm=llm,
        topic=state.topic,
        learner_profile=state.learner_profile,
        reference=state.reference,
        feedback=feedback,
    )

    return {
        "lesson": lesson,
        "attempt": attempt,
        "status": "RUNNING",
    }


# ============================================================
# EVALUATE NODE
# ============================================================

def evaluate_node(
    state: WorkflowState,
    llm: LLMClient,
    memory: MemoryStore,
):
    """
    Evaluate the generated lesson against the rubric.
    """

    evaluation = evaluate_lesson(
        llm=llm,
        topic=state.topic,
        lesson=state.lesson,
        reference=state.reference,
        rubric=state.rubric,
    )

    return {
        "evaluation": evaluation,
    }


# ============================================================
# DECISION NODE
# ============================================================

def route_after_evaluation(
    state: WorkflowState,
):
    """
    Decide whether the workflow should:

        PASS  -> END
        FAIL  -> RETRY
        FAIL + max attempts -> END
    """

    if state.evaluation is None:
        return "retry"

    if state.evaluation.overall_status == "PASS":
        return "pass"

    if state.attempt >= state.max_attempts:
        return "fail"

    return "retry"


# ============================================================
# PASS NODE
# ============================================================

def pass_node(
    state: WorkflowState,
):
    """
    Mark the workflow as successfully completed.
    """

    return {
        "status": "PASSED",
    }


# ============================================================
# REJECTION LOG NODE
# ============================================================

def rejection_node(
    state: WorkflowState,
):
    """
    Store evaluator feedback whenever a lesson is rejected.

    This creates the rejection_log expected by the tests.
    """

    rejection_log = list(
        getattr(state, "rejection_log", [])
    )

    if state.evaluation is not None:
        rejection_log.append(
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

    return {
        "rejection_log": rejection_log,
    }


# ============================================================
# FAIL NODE
# ============================================================

def fail_node(
    state: WorkflowState,
):
    """
    Mark the workflow as permanently failed after
    all allowed attempts have been exhausted.
    """

    return {
        "status": "FAILED",
    }


# ============================================================
# BUILD GRAPH
# ============================================================

def build_graph(
    llm: LLMClient,
    memory: MemoryStore,
    max_attempts: int = 3,
):
    """
    Build the self-evaluating content generation graph.

    Flow:

        START
          |
          v
       GENERATE
          |
          v
       EVALUATE
          |
       +--+--+
       |     |
      PASS  FAIL
       |     |
       v     v
      END  REJECT
             |
       +-----+------+
       |            |
     retry       max attempts
       |            |
       v            v
    GENERATE       FAIL
                    |
                    v
                   END
    """

    # --------------------------------------------------------
    # Create the graph
    # --------------------------------------------------------

    workflow = StateGraph(WorkflowState)

    # --------------------------------------------------------
    # Add nodes
    # --------------------------------------------------------

    workflow.add_node(
        "generate",
        lambda state: generate_node(
            state,
            llm,
            memory,
        ),
    )

    workflow.add_node(
        "evaluate",
        lambda state: evaluate_node(
            state,
            llm,
            memory,
        ),
    )

    workflow.add_node(
        "pass",
        pass_node,
    )

    workflow.add_node(
        "reject",
        rejection_node,
    )

    workflow.add_node(
        "fail",
        fail_node,
    )

    # --------------------------------------------------------
    # Entry point
    # --------------------------------------------------------

    workflow.set_entry_point("generate")

    # --------------------------------------------------------
    # Generate -> Evaluate
    # --------------------------------------------------------

    workflow.add_edge(
        "generate",
        "evaluate",
    )

    # --------------------------------------------------------
    # Evaluate -> PASS / REJECT
    # --------------------------------------------------------

    workflow.add_conditional_edges(
        "evaluate",
        route_after_evaluation,
        {
            "pass": "pass",
            "retry": "reject",
            "fail": "reject",
        },
    )

    # --------------------------------------------------------
    # PASS -> END
    # --------------------------------------------------------

    workflow.add_edge(
        "pass",
        END,
    )

    # --------------------------------------------------------
    # REJECT -> either GENERATE or FAIL
    # --------------------------------------------------------

    def route_after_rejection(
        state: WorkflowState,
    ):
        if (
            state.evaluation is not None
            and state.evaluation.overall_status == "FAIL"
            and state.attempt >= state.max_attempts
        ):
            return "fail"

        return "retry"

    workflow.add_conditional_edges(
        "reject",
        route_after_rejection,
        {
            "retry": "generate",
            "fail": "fail",
        },
    )

    # --------------------------------------------------------
    # FAIL -> END
    # --------------------------------------------------------

    workflow.add_edge(
        "fail",
        END,
    )

    # --------------------------------------------------------
    # Compile
    # --------------------------------------------------------

    graph = workflow.compile()

    return graph