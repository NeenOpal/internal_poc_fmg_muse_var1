"""
Email generation pipeline with automatic evaluation and refinement.
Generates email → Evaluates using metrics → Refines if needed → Returns final email.
"""

import structlog
from typing import Optional

from app.models.email import (
    PurposeEnum,
    LengthEnum,
    ToneEnum,
    ChatMessage,
    EmailGenerationResponse,
    UsageInfo,
)
from app.services.llm_service import get_llm_service
from app.evaluation.evaluation_service import get_evaluation_service

logger = structlog.get_logger()


# Thresholds for triggering auto-refinement
OVERALL_SCORE_THRESHOLD = 7.0
COMPLIANCE_THRESHOLD = 7
PURPOSE_THRESHOLD = 6

# Maximum refinement attempts (for weaker models like Llama)
MAX_REFINEMENT_ATTEMPTS = 3

# Set to False to skip evaluation and return email immediately (faster)
ENABLE_AUTO_EVALUATION = False


class EmailPipeline:
    """
    Orchestrates the full email generation pipeline:
    1. Generate initial email
    2. Evaluate against quality metrics
    3. Auto-refine if below thresholds
    4. Return final polished email
    """

    def __init__(self):
        self.llm_service = get_llm_service()
        self.eval_service = get_evaluation_service()

    def _needs_refinement(self, metrics) -> tuple[bool, list[str]]:
        """
        Determine if email needs refinement based on evaluation scores.
        Returns (needs_refinement, list_of_issues_to_fix).
        """
        issues = []

        # Check critical thresholds
        if metrics.overall_score < OVERALL_SCORE_THRESHOLD:
            issues.append(f"Overall quality score ({metrics.overall_score:.1f}) below threshold")

        if metrics.compliance.score < COMPLIANCE_THRESHOLD:
            issues.append(f"Compliance issue: {metrics.compliance.justification}")
            if metrics.compliance.suggestions:
                issues.append(f"Fix: {metrics.compliance.suggestions}")

        if metrics.purpose_alignment.score < PURPOSE_THRESHOLD:
            issues.append(f"Purpose issue: {metrics.purpose_alignment.justification}")
            if metrics.purpose_alignment.suggestions:
                issues.append(f"Fix: {metrics.purpose_alignment.suggestions}")

        # If critical checks pass but overall score is low, get top issues
        if not issues and metrics.overall_score < OVERALL_SCORE_THRESHOLD:
            # Collect issues from metrics with low scores (< 7)
            metric_checks = [
                ("tone_consistency", metrics.tone_consistency),
                ("structure_completeness", metrics.structure_completeness),
                ("clarity", metrics.clarity),
                ("professionalism", metrics.professionalism),
                ("personalization", metrics.personalization),
                ("risk_balance", metrics.risk_balance),
                ("disclaimer_accuracy", metrics.disclaimer_accuracy),
                ("length_accuracy", metrics.length_accuracy),
            ]

            for name, metric in metric_checks:
                if metric.score < 7 and metric.suggestions:
                    issues.append(f"{name.replace('_', ' ').title()}: {metric.suggestions}")
                    if len(issues) >= 3:  # Top 3 issues only
                        break

        needs_fix = len(issues) > 0
        return needs_fix, issues

    def _build_refinement_feedback(self, metrics, issues: list[str]) -> str:
        """Build focused refinement feedback from evaluation results."""
        feedback_parts = ["Please improve this email based on the following issues:"]
        feedback_parts.extend([f"- {issue}" for issue in issues[:3]])  # Top 3 only

        # Add specific improvements needed from evaluation
        if metrics.improvements_needed:
            feedback_parts.append("\nPriority improvements:")
            for improvement in metrics.improvements_needed[:2]:
                feedback_parts.append(f"- {improvement}")

        return "\n".join(feedback_parts)

    async def generate_with_quality_check(
        self,
        purpose: PurposeEnum,
        details: str,
        length: LengthEnum,
        tone: ToneEnum = None,
        model: str = None,
        history: Optional[list[ChatMessage]] = None,
    ) -> EmailGenerationResponse:
        """
        Generate an email with automatic quality evaluation and refinement.

        Flow:
        1. Generate initial email
        2. Evaluate using full metrics system
        3. If below thresholds, refine using evaluation feedback
        4. Return final email (user never sees evaluation scores)
        """
        history = history or []
        tone = tone or ToneEnum.PROFESSIONAL

        total_usage = UsageInfo(
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            cost=0.0,
        )

        # Step 1: Generate initial email
        logger.info(
            "Pipeline: Generating initial email",
            purpose=purpose.value,
            tone=tone.value,
            length=length.value,
        )

        initial_response = await self.llm_service.generate_email(
            purpose=purpose,
            details=details,
            length=length,
            tone=tone,
            model=model,
            history=history,
        )

        # Accumulate usage
        if initial_response.usage:
            total_usage.prompt_tokens += initial_response.usage.prompt_tokens
            total_usage.completion_tokens += initial_response.usage.completion_tokens
            total_usage.total_tokens += initial_response.usage.total_tokens
            total_usage.cost += initial_response.usage.cost

        # Fast path: Skip evaluation if disabled (for speed)
        if not ENABLE_AUTO_EVALUATION:
            logger.info(
                "Pipeline: Skipping evaluation (disabled for speed)",
                subject_preview=initial_response.subject[:30] if initial_response.subject else "",
            )
            return EmailGenerationResponse(
                subject=initial_response.subject,
                body=initial_response.body,
                usage=total_usage,
            )

        # Step 2: Evaluate the generated email
        logger.info(
            "Pipeline: Evaluating email quality",
            subject_preview=initial_response.subject[:30] if initial_response.subject else "",
        )

        try:
            metrics = await self.eval_service.evaluate_email(
                email_subject=initial_response.subject,
                email_body=initial_response.body,
                purpose=purpose,
                tone=tone,
                length=length,
                original_request=details,
                model=model,
            )

            logger.info(
                "Pipeline: Evaluation complete",
                overall_score=metrics.overall_score,
                compliance_score=metrics.compliance.score,
                purpose_score=metrics.purpose_alignment.score,
                pass_threshold=metrics.pass_threshold,
            )

            # Step 3: Check if refinement needed and loop until compliant or max attempts
            current_subject = initial_response.subject
            current_body = initial_response.body
            current_metrics = metrics
            refinement_attempt = 0

            while refinement_attempt < MAX_REFINEMENT_ATTEMPTS:
                needs_refinement, issues = self._needs_refinement(current_metrics)

                if not needs_refinement:
                    # Email passed quality check
                    logger.info(
                        "Pipeline: Email passed quality check",
                        overall_score=current_metrics.overall_score,
                        attempts=refinement_attempt,
                    )
                    return EmailGenerationResponse(
                        subject=current_subject,
                        body=current_body,
                        usage=total_usage,
                    )

                # Need refinement
                refinement_attempt += 1
                logger.info(
                    "Pipeline: Refinement needed",
                    attempt=refinement_attempt,
                    max_attempts=MAX_REFINEMENT_ATTEMPTS,
                    issues_count=len(issues),
                    issues=issues[:3],
                )

                # Build refinement feedback from evaluation
                refinement_feedback = self._build_refinement_feedback(current_metrics, issues)

                # Step 4: Refine the email
                refined_response = await self.llm_service.refine_email(
                    original_subject=current_subject,
                    original_body=current_body,
                    feedback=refinement_feedback,
                    model=model,
                    history=history,
                )

                # Accumulate usage
                if refined_response.usage:
                    total_usage.prompt_tokens += refined_response.usage.prompt_tokens
                    total_usage.completion_tokens += refined_response.usage.completion_tokens
                    total_usage.total_tokens += refined_response.usage.total_tokens
                    total_usage.cost += refined_response.usage.cost

                # Update current email
                current_subject = refined_response.subject
                current_body = refined_response.body

                logger.info(
                    "Pipeline: Refinement complete",
                    attempt=refinement_attempt,
                    previous_score=current_metrics.overall_score,
                )

                # Re-evaluate the refined email
                if refinement_attempt < MAX_REFINEMENT_ATTEMPTS:
                    logger.info(
                        "Pipeline: Re-evaluating refined email",
                        attempt=refinement_attempt,
                    )
                    current_metrics = await self.eval_service.evaluate_email(
                        email_subject=current_subject,
                        email_body=current_body,
                        purpose=purpose,
                        tone=tone,
                        length=length,
                        original_request=details,
                        model=model,
                    )
                    logger.info(
                        "Pipeline: Re-evaluation complete",
                        attempt=refinement_attempt,
                        new_score=current_metrics.overall_score,
                        compliance_score=current_metrics.compliance.score,
                    )

            # Max attempts reached - return best effort
            logger.warning(
                "Pipeline: Max refinement attempts reached",
                attempts=refinement_attempt,
                final_score=current_metrics.overall_score if current_metrics else "unknown",
            )
            return EmailGenerationResponse(
                subject=current_subject,
                body=current_body,
                usage=total_usage,
            )

        except Exception as eval_error:
            # If evaluation fails, return the original email
            logger.warning(
                "Pipeline: Evaluation failed, returning original email",
                error=str(eval_error),
            )
            return initial_response


# Singleton instance
_email_pipeline = None


def get_email_pipeline() -> EmailPipeline:
    """Get the singleton email pipeline instance."""
    global _email_pipeline
    if _email_pipeline is None:
        _email_pipeline = EmailPipeline()
    return _email_pipeline
