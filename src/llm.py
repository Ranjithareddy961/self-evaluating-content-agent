import os
from typing import Protocol


# ============================================================
# LLM CLIENT INTERFACE
# ============================================================

class LLMClient(Protocol):
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        ...


# ============================================================
# MOCK LLM
# ============================================================

class MockLLM:
    """
    Deterministic LLM used for tests and --mock mode.

    Behaviour:
        Attempt 1:
            Generates an intentionally incorrect lesson.

        Attempt 2:
            Generates a corrected lesson.

        Evaluation 1:
            FAIL

        Evaluation 2:
            PASS

    This allows the complete retry workflow to be tested
    without using API credits.
    """

    def __init__(self):
        self.generation_count = 0
        self.evaluation_count = 0

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        # ====================================================
        # EVALUATOR
        # ====================================================

        if (
            "strict educational content quality evaluator"
            in system_prompt.lower()
        ):

            self.evaluation_count += 1

            # -----------------------------------------------
            # FIRST EVALUATION -> FAIL
            # -----------------------------------------------

            if self.evaluation_count == 1:

                return """
{
  "overall_status": "FAIL",
  "checks": [
    {
      "id": "accuracy",
      "name": "Accuracy",
      "passed": false,
      "reason": "The lesson incorrectly says that RAG retrains the language model."
    }
  ],
  "failures": [
    "The lesson incorrectly says that RAG retrains the language model."
  ],
  "recommendations": [
    "Explain that RAG retrieves external information and provides it as context instead of retraining the model."
  ]
}
"""

            # -----------------------------------------------
            # SECOND EVALUATION -> PASS
            # -----------------------------------------------

            return """
{
  "overall_status": "PASS",
  "checks": [
    {
      "id": "accuracy",
      "name": "Accuracy",
      "passed": true,
      "reason": "The lesson correctly explains that RAG retrieves external information and provides it to the language model as context."
    }
  ],
  "failures": [],
  "recommendations": []
}
"""

        # ====================================================
        # GENERATOR
        # ====================================================

        self.generation_count += 1

        # -----------------------------------------------
        # FIRST GENERATION -> INTENTIONALLY INCORRECT
        # -----------------------------------------------

        if self.generation_count == 1:

            return """
RAG stands for Retrieval-Augmented Generation.

RAG retrains the language model whenever a user asks a question.
"""

        # -----------------------------------------------
        # RETRY GENERATION -> CORRECTED
        # -----------------------------------------------

        return """
RAG stands for Retrieval-Augmented Generation.

RAG retrieves relevant information from an external knowledge
source and gives that information to the language model as
context.

The language model then uses the retrieved information to
generate a better answer.

RAG does not retrain the language model every time a user asks
a question.
"""


# ============================================================
# OPENAI LLM
# ============================================================

class OpenAILLM:
    """
    OpenAI-backed LLM client.

    This class is used when running:

        python -m src.main

    The API key must be available in the environment as:

        OPENAI_API_KEY

    You can still use:

        python -m src.main --mock

    to run without an API key.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
    ):
        self.model = model

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. "
                "Set it before running without --mock, or use "
                "--mock for testing."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "The openai package is not installed. "
                "Install it with: pip install openai"
            ) from exc

        self.client = OpenAI(
            api_key=api_key
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0,
        )

        content = response.choices[0].message.content

        if content is None:
            raise ValueError(
                "OpenAI returned an empty response."
            )

        return content