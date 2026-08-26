import json

from src.llm import LLMClient
from src.models import EvaluationResult


def evaluate_lesson(
    llm: LLMClient,
    topic: str,
    lesson: str,
    reference: str,
    rubric: dict,
) -> EvaluationResult:
    """
    Evaluate a lesson against a strict PASS/FAIL rubric.

    The evaluator must return JSON matching the
    EvaluationResult schema.
    """

    rubric_text = json.dumps(
        rubric,
        indent=2,
    )

    system_prompt = """
You are a strict educational content quality evaluator.

Your job is to evaluate a beginner lesson.

You MUST evaluate every rubric criterion.

Each criterion is either PASS or FAIL.
There is NO partial credit.

A criterion passes only when the lesson clearly
satisfies the entire requirement.

Return ONLY valid JSON.

The JSON must have exactly this structure:

{
  "overall_status": "PASS",
  "checks": [
    {
      "id": "accuracy",
      "name": "Accurate and Grounded",
      "passed": true,
      "reason": "Short explanation"
    }
  ],
  "failures": [],
  "recommendations": []
}

IMPORTANT:

- "id" must be a short identifier.
- "name" must contain the human-readable criterion name.
- "passed" must be true or false.
- "reason" must explain the decision.
- "overall_status" must be PASS only if EVERY check passes.
- If even ONE check fails, overall_status must be FAIL.
- failures must list the failed criteria and their problems.
- recommendations must explain exactly what should be changed.
- Do not use Markdown.
- Do not wrap the JSON in ```json fences.
"""

    user_prompt = f"""
TOPIC
=====
{topic}

REFERENCE MATERIAL
==================
{reference}

RUBRIC
======
{rubric_text}

LESSON TO EVALUATE
==================
{lesson}

Evaluate the lesson against every rubric criterion.

Remember:

PASS = the criterion is fully satisfied.

FAIL = the criterion is not fully satisfied.

No partial credit.

Return only valid JSON.
"""

    raw_response = llm.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    # Remove accidental Markdown fences if an LLM adds them.
    cleaned_response = raw_response.strip()

    if cleaned_response.startswith("```json"):
        cleaned_response = (
            cleaned_response[
                len("```json"):
            ]
            .strip()
        )

    if cleaned_response.endswith("```"):
        cleaned_response = (
            cleaned_response[
                :-3
            ]
            .strip()
        )

    try:
        return EvaluationResult.model_validate_json(
            cleaned_response
        )

    except Exception as exc:

        raise ValueError(
            "Evaluator returned invalid JSON "
            "or JSON that does not match the "
            "EvaluationResult schema.\n\n"
            f"Raw evaluator response:\n"
            f"{raw_response}\n\n"
            f"Validation error:\n"
            f"{exc}"
        ) from exc