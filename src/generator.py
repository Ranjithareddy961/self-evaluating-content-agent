from src.llm import LLMClient


def generate_lesson(
    llm: LLMClient,
    topic: str,
    learner_profile: str,
    reference: str,
    feedback: str = "",
    attempt: int = 1,
) -> str:
    """
    Generate a beginner-friendly lesson.

    On retry attempts, evaluator feedback is provided to the
    model so that the lesson can be improved.
    """

    retry_instruction = ""

    if feedback.strip():
        retry_instruction = f"""
PREVIOUS EVALUATOR FEEDBACK
===========================

The previous lesson did not pass the evaluator.

You MUST improve the new lesson based on the following feedback:

{feedback}

Do not repeat the problems identified by the evaluator.
"""

    system_prompt = """
You are an expert educational content designer
and GenAI engineer.

Your job is to create beginner-friendly educational
lessons for learners with no technical background.

The learner may have limited English vocabulary.

Use:
- simple English
- short sentences
- clear explanations
- practical examples
- step-by-step teaching
- minimal jargon

When technical terms are necessary, explain them
before using them.

The lesson must be factually accurate and grounded
in the provided reference material.

The lesson must explain:

1. What the topic is
2. Why it matters
3. How it works
4. A simple real-world example
5. Important key concepts
6. A short recap

Do not assume prior AI knowledge.

Return only the lesson content.
Do not return JSON.
Do not discuss these instructions.
"""

    user_prompt = f"""
TOPIC
=====
{topic}

TARGET LEARNER
==============
{learner_profile}

REFERENCE MATERIAL
==================
{reference}

GENERATION ATTEMPT
==================
{attempt}

{retry_instruction}

Create a standalone beginner lesson.

The learner should be able to understand
the topic after reading the lesson without
needing another explanation.

Make the lesson clear, accurate, practical,
and easy to follow.
"""

    return llm.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )