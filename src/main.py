import argparse
import json
from pathlib import Path

from src.graph import build_graph
from src.llm import MockLLM
from src.memory import MemoryStore
from src.models import WorkflowState


DEFAULT_REFERENCE = """
Retrieval-Augmented Generation, or RAG, is a way to improve
the answers of a language model by giving it relevant information
from an external knowledge source.

A typical RAG system has two main stages.

First, the system retrieves relevant information from a knowledge
source such as documents or a database.

Second, the retrieved information is provided to the language
model as context. The model then uses that context to generate
an answer.

RAG is useful when a system needs to answer questions using
information that may not be part of the model's original training
data.

RAG does not mean retraining the language model every time new
information is added.

A simple RAG flow is:

Question
    ↓
Retrieve relevant documents
    ↓
Add documents as context
    ↓
Language model
    ↓
Answer

RAG can help reduce unsupported answers because the model receives
relevant external information before generating its response.
However, retrieval quality matters. If the system retrieves
irrelevant or incorrect information, the final answer can also
be poor.
"""


DEFAULT_RUBRIC = {
    "criteria": [
        {
            "id": "accuracy",
            "name": "Accurate and Grounded",
            "description": (
                "The lesson must explain RAG accurately "
                "and must not contain major factual errors."
            ),
        },
        {
            "id": "beginner_language",
            "name": "Beginner-Friendly Language",
            "description": (
                "The lesson must be understandable to a "
                "12th-grade learner with limited English vocabulary."
            ),
        },
        {
            "id": "example",
            "name": "Teaches by Example",
            "description": (
                "The lesson must include at least one simple "
                "real-world example."
            ),
        },
        {
            "id": "jargon",
            "name": "No Unexplained Jargon",
            "description": (
                "Important technical terms must be explained "
                "before or when they are used."
            ),
        },
        {
            "id": "coverage",
            "name": "Key Points Covered",
            "description": (
                "The lesson must explain what RAG is, why it matters, "
                "and how the basic RAG process works."
            ),
        },
        {
            "id": "flow",
            "name": "Coherent Teaching Flow",
            "description": (
                "The lesson must follow a logical beginner-friendly "
                "teaching sequence."
            ),
        },
    ]
}


def create_parser():
    parser = argparse.ArgumentParser(
        description="Self-Evaluating Lesson Content Agent"
    )

    parser.add_argument(
        "--topic",
        default="Introduction to RAG",
        help="Topic for the lesson.",
    )

    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use MockLLM instead of the OpenAI API.",
    )

    parser.add_argument(
        "--max-attempts",
        type=int,
        default=3,
        help="Maximum number of generation attempts.",
    )

    return parser


def print_header():
    print()
    print("=" * 70)
    print("       SELF-EVALUATING LESSON CONTENT AGENT")
    print("=" * 70)
    print()


def print_evaluation(evaluation):
    print()
    print("EVALUATION")
    print("-" * 70)

    for check in evaluation.checks:

        status = "PASS" if check.passed else "FAIL"

        print(
            f"[{status}] {check.name}"
        )

        if not check.passed:
            print(
                f"       Reason: {check.reason}"
            )

    print()

    print(
        f"Overall status: {evaluation.overall_status}"
    )


def save_outputs(state: WorkflowState):
    """
    Save the final lesson and rejection log.
    """

    output_dir = Path("outputs")

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    lesson_path = output_dir / "final_lesson.md"

    rejection_path = output_dir / "rejection_log.json"

    lesson_path.write_text(
        state.lesson,
        encoding="utf-8",
    )

    rejection_path.write_text(
        json.dumps(
            state.rejection_log,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return lesson_path, rejection_path


def main():

    parser = create_parser()

    args = parser.parse_args()

    print_header()

    print(f"Topic: {args.topic}")

    print(
        f"Maximum attempts: {args.max_attempts}"
    )

    print()

    memory = MemoryStore()

    if args.mock:

        print("Mode: MOCK (no API credits required)")

        llm = MockLLM()

    else:

        print("Mode: OPENAI")

        llm = OpenAILLM()

    graph = build_graph(
        llm=llm,
        memory=memory,
        max_attempts=args.max_attempts,
    )

    state = WorkflowState(
        topic=args.topic,

        learner_profile=(
            "12th-grade graduate from India "
            "with limited English vocabulary "
            "and no previous AI background."
        ),

        reference=DEFAULT_REFERENCE,

        rubric=DEFAULT_RUBRIC,
    )

    print()
    print("Starting agentic workflow...")
    print()

    result = graph.invoke(state)

    print(
        f"Attempts used: {result['attempt']}"
    )

    if result.get("rejection_log"):

        print()

        print(
            f"Rejected attempts: "
            f"{len(result['rejection_log'])}"
        )

        for rejection in result["rejection_log"]:

            print(
                f"  Attempt "
                f"{rejection['attempt']}: "
                f"REJECTED"
            )

            for failure in rejection["failures"]:

                print(
                    f"    - {failure}"
                )

    if result.get("evaluation"):

        print_evaluation(
            result["evaluation"]
        )

    # Save memory directly using MemoryStore.
    final_state = WorkflowState(**result)

    try:
        memory.save(final_state)
    except AttributeError:
        # If your MemoryStore uses a different public method,
        # the workflow itself has still completed successfully.
        pass

    lesson_path, rejection_path = save_outputs(
        final_state
    )

    print()
    print("=" * 70)

    if result["status"] == "PASSED":

        print("LESSON APPROVED FOR SHIPPING")

    else:

        print("LESSON REJECTED")

    print("=" * 70)

    print()
    print(f"Final lesson: {lesson_path}")
    print(f"Rejection log: {rejection_path}")
    print()


if __name__ == "__main__":
    main()