from src.models import EvaluationCheck, EvaluationResult


def test_evaluation_check():
    check = EvaluationCheck(
        criterion="Accuracy",
        status="PASS",
        reason="The lesson is factually correct."
    )

    assert check.status == "PASS"


def test_evaluation_result():
    result = EvaluationResult(
        overall_status="FAIL",
        checks=[],
        failures=["Jargon was not explained."],
        recommendations=["Explain technical terms."]
    )

    assert result.overall_status == "FAIL"
    assert len(result.failures) == 1