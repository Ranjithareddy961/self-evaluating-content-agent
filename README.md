# Self-Evaluating Lesson Content Agent

## GenAI Engineer - Content Systems Take-Home Assessment

An agentic system that generates beginner-friendly educational content,
evaluates the content against a strict rubric, and automatically
regenerates rejected content until it meets the quality bar.

### Topic

Introduction to RAG (Retrieval-Augmented Generation)

### Target Learner

A 12th-grade graduate from India with limited English vocabulary,
no AI background, and a non-English-medium educational background.

---

## Architecture

The system follows this loop:

GENERATE
   ↓
EVALUATE
   ↓
PASS → SHIP
   ↓
FAIL
   ↓
REGENERATE
   ↓
EVALUATE
   ↓
PASS / FAIL

The workflow is implemented using LangGraph.

### Main Components

- `generator.py` - generates the lesson
- `evaluator.py` - evaluates the lesson against the rubric
- `graph.py` - orchestrates the generate/evaluate/retry loop
- `workflow.py` - workflow execution logic
- `models.py` - Pydantic state and evaluation models
- `memory.py` - persistent rejection/feedback memory
- `llm.py` - MockLLM and OpenAI LLM implementations
- `prompts.py` - generation and evaluation prompts
- `main.py` - CLI entry point

---

## Evaluation Rubric

The lesson is evaluated using hard PASS/FAIL checks:

1. Accurate and grounded
2. Beginner-friendly language
3. Teaches by example
4. No unexplained jargon
5. Key points covered
6. Coherent teaching flow

There is no partial credit.

If any important criterion fails, the lesson is rejected.

---

## Retry Behaviour

The system supports a maximum number of attempts.

When an attempt fails:

1. The evaluator identifies the failed criterion.
2. The reason for failure is recorded.
3. Feedback/recommendations are passed to the generator.
4. The generator creates a revised lesson.
5. The revised lesson is evaluated again.

The workflow always terminates because `max_attempts` limits retries.

---

## Memory

The system persists rejection information so that failures can be
inspected across runs.

The rejection log records:

- attempt number
- failed criteria
- reasons
- recommendations

---

## Mock Mode

The project includes a deterministic `MockLLM`.

The mock intentionally creates:

### Attempt 1

An incorrect lesson claiming that RAG retrains the language model.

The evaluator rejects it.

### Attempt 2

The generator receives the evaluator feedback and produces a corrected
lesson explaining that RAG retrieves external information and provides it
to the language model as context.

The evaluator then approves the lesson.

This makes the complete agentic loop reproducible without API credits.

---

## Running the Tests

Activate the virtual environment:

```powershell
.venv\Scripts\activate