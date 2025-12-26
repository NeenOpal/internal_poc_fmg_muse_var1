"""Email evaluation module for quality assessment and improvement."""

from app.evaluation.test_cases import (
    IDEAL_TEST_CASES,
    get_test_case_by_id,
    get_test_cases_by_purpose,
    get_test_cases_by_tone,
    get_all_test_cases,
)
from app.evaluation.metrics import (
    EvaluationMetrics,
    MetricScore,
    EVALUATION_CRITERIA,
)
from app.evaluation.evaluation_service import (
    EmailEvaluationService,
    get_evaluation_service,
)

__all__ = [
    "IDEAL_TEST_CASES",
    "get_test_case_by_id",
    "get_test_cases_by_purpose",
    "get_test_cases_by_tone",
    "get_all_test_cases",
    "EvaluationMetrics",
    "MetricScore",
    "EVALUATION_CRITERIA",
    "EmailEvaluationService",
    "get_evaluation_service",
]
