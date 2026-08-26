from typing import Optional

from pydantic import BaseModel, Field, model_validator


# ============================================================
# EVALUATION CHECK
# ============================================================

class EvaluationCheck(BaseModel):
    """
    Represents one PASS/FAIL evaluation criterion.

    Supports both:

    New format:
        id
        name
        passed
        reason

    Legacy/test format:
        criterion
        status
        reason
    """

    # New canonical fields
    id: Optional[str] = None
    name: Optional[str] = None
    passed: Optional[bool] = None

    # Backward-compatible fields
    criterion: Optional[str] = None
    status: Optional[str] = None

    reason: str

    @model_validator(mode="after")
    def normalize_fields(self):

        # ----------------------------------------------------
        # Convert legacy → canonical
        # ----------------------------------------------------

        if self.id is None and self.criterion is not None:
            self.id = (
                self.criterion
                .lower()
                .replace(" ", "_")
            )

        if self.name is None and self.criterion is not None:
            self.name = self.criterion

        if self.passed is None and self.status is not None:
            self.passed = (
                self.status.upper() == "PASS"
            )

        # ----------------------------------------------------
        # Convert canonical → legacy
        # ----------------------------------------------------

        if self.criterion is None and self.name is not None:
            self.criterion = self.name

        if self.status is None and self.passed is not None:
            self.status = (
                "PASS"
                if self.passed
                else "FAIL"
            )

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        if self.id is None:
            raise ValueError(
                "EvaluationCheck requires either "
                "'id' or 'criterion'."
            )

        if self.name is None:
            raise ValueError(
                "EvaluationCheck requires either "
                "'name' or 'criterion'."
            )

        if self.passed is None:
            raise ValueError(
                "EvaluationCheck requires either "
                "'passed' or 'status'."
            )

        return self


# ============================================================
# EVALUATION RESULT
# ============================================================

class EvaluationResult(BaseModel):
    """
    Structured result returned by the evaluator.
    """

    overall_status: str

    checks: list[EvaluationCheck] = Field(
        default_factory=list
    )

    failures: list[str] = Field(
        default_factory=list
    )

    recommendations: list[str] = Field(
        default_factory=list
    )


# ============================================================
# WORKFLOW STATE
# ============================================================

class WorkflowState(BaseModel):
    """
    Shared state used by the LangGraph workflow.

    Flow:

        GENERATE
           ↓
        EVALUATE
         ↙     ↘
       FAIL    PASS
        ↓        ↓
     RETRY      END
    """

    # --------------------------------------------------------
    # Input
    # --------------------------------------------------------

    topic: str

    learner_profile: str

    reference: str

    rubric: dict

    # --------------------------------------------------------
    # Generated lesson
    # --------------------------------------------------------

    lesson: str = ""

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    evaluation: Optional[EvaluationResult] = None

    # --------------------------------------------------------
    # Workflow control
    # --------------------------------------------------------

    attempt: int = 0

    max_attempts: int = 3

    status: str = "RUNNING"

    # --------------------------------------------------------
    # Rejection history
    # --------------------------------------------------------

    rejection_log: list[dict] = Field(
        default_factory=list
    )