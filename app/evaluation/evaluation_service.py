"""
LLM-based email evaluation service.
Uses the same LLM to score generated emails against quality metrics.
"""

import structlog
import json
import re
from typing import Optional

from app.models.email import PurposeEnum, ToneEnum, LengthEnum
from app.evaluation.metrics import (
    EvaluationMetrics,
    MetricScore,
    EVALUATION_CRITERIA,
    calculate_overall_score,
)
from app.evaluation.test_cases import (
    get_conversations_by_purpose,
    extract_email_from_conversation,
    format_conversation_for_prompt,
)
from app.config import get_settings

logger = structlog.get_logger()

# Use a fast model for evaluation (much faster than GPT-4o)
# GPT-4o-mini is ~3-5s vs GPT-4o ~10-15s
EVALUATION_MODEL = "openai/gpt-4o-mini"


def build_evaluation_prompt(
    email_subject: str,
    email_body: str,
    purpose: PurposeEnum,
    tone: ToneEnum,
    length: LengthEnum,
    original_request: str,
) -> str:
    """Construct the prompt for LLM-based email evaluation."""

    # Get relevant conversations for context
    reference_conversations = get_conversations_by_purpose(purpose)
    reference_conv = reference_conversations[0] if reference_conversations else None
    reference_email = extract_email_from_conversation(reference_conv) if reference_conv else None

    # Build the evaluation prompt
    prompt = f"""You are an expert email quality evaluator for financial advisor communications.
Evaluate the following generated email against strict quality and compliance standards.

=== EMAIL TO EVALUATE ===
Subject: {email_subject}

{email_body}

=== ORIGINAL REQUEST ===
Purpose: {purpose.value}
Requested Tone: {tone.value}
Requested Length: {length.value}
User's Input: {original_request}

=== LENGTH TARGETS ===
- Short: 50-100 words, 2-4 sentences
- Medium: 100-200 words, 5-8 sentences
- Long: 200-400 words, 9-15 sentences

"""

    if reference_email and reference_conv:
        prompt += f"""=== REFERENCE EXAMPLE (for comparison) ===
This is an ideal email for a similar purpose:

Subject: {reference_email["subject"]}

{reference_email["body"]}

Quality notes about the reference:
{chr(10).join('- ' + note for note in reference_conv.get("evaluation_notes", []))}

"""

    prompt += """=== EVALUATION CRITERIA ===
Score each metric from 1-10 using these standards:

1. COMPLIANCE (Weight: 20%)
   Check for:
   - No guarantee language (guaranteed, risk-free, cannot lose)
   - No specific return promises (will return X%)
   - No false urgency (act now, limited time)
   - Qualifying language for predictions (we believe, in our opinion)
   - Required disclaimers present
   - Risks balanced with benefits
   - Volatility warnings for crypto/leverage if applicable

2. TONE_CONSISTENCY (Weight: 10%)
   Does the tone match what was requested?
   - Professional: Business-appropriate, clear, direct
   - Formal: Traditional, proper titles, no contractions
   - Friendly: Warm, personable, conversational
   - Casual: Relaxed, contractions okay

3. LENGTH_ACCURACY (Weight: 8%)
   Is the email within the target word count?
   Count the body words (excluding subject).

4. STRUCTURE_COMPLETENESS (Weight: 10%)
   Check for:
   - Clear subject line
   - Appropriate greeting
   - Well-organized body
   - Clear closing
   - Signature placeholder

5. PURPOSE_ALIGNMENT (Weight: 15%)
   Does the email achieve its stated purpose?

6. CLARITY (Weight: 10%)
   Is the language clear and easy to understand?
   - Concise sentences
   - Logical flow
   - No ambiguity

7. PROFESSIONALISM (Weight: 10%)
   Is it appropriate for financial advisor communications?
   - Proper vocabulary
   - Respectful tone
   - Good grammar

8. PERSONALIZATION (Weight: 7%)
   Are placeholders used correctly?
   - [Recipient Name], [Your Name], etc.
   - No made-up specific details

9. RISK_BALANCE (Weight: 5%)
   If investments discussed, are risks and benefits balanced?
   (Score 8 if not applicable)

10. DISCLAIMER_ACCURACY (Weight: 5%)
    Are required disclaimers present when needed?
    (Score 8 if no disclaimers needed)

=== OUTPUT FORMAT ===
Respond with a JSON object in exactly this format:
```json
{
  "compliance": {"score": X, "justification": "...", "suggestions": "..."},
  "tone_consistency": {"score": X, "justification": "...", "suggestions": "..."},
  "length_accuracy": {"score": X, "justification": "...", "suggestions": "..."},
  "structure_completeness": {"score": X, "justification": "...", "suggestions": "..."},
  "purpose_alignment": {"score": X, "justification": "...", "suggestions": "..."},
  "clarity": {"score": X, "justification": "...", "suggestions": "..."},
  "professionalism": {"score": X, "justification": "...", "suggestions": "..."},
  "personalization": {"score": X, "justification": "...", "suggestions": "..."},
  "risk_balance": {"score": X, "justification": "...", "suggestions": "..."},
  "disclaimer_accuracy": {"score": X, "justification": "...", "suggestions": "..."},
  "strengths": ["strength1", "strength2", "strength3"],
  "improvements_needed": ["improvement1", "improvement2"]
}
```

IMPORTANT:
- Each score must be an integer from 1-10
- Justification should be 1-2 sentences explaining the score
- Suggestions should be specific and actionable (or null if score is 8+)
- List 2-4 strengths and 1-3 improvements
- Be strict but fair in your evaluation

Evaluate the email now:"""

    return prompt


def parse_evaluation_response(response: str) -> dict:
    """Parse the LLM's evaluation response into structured data."""
    # Try to extract JSON from the response
    try:
        # Look for JSON block
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group(0)
            else:
                raise ValueError("No JSON found in response")

        return json.loads(json_str)

    except (json.JSONDecodeError, ValueError) as e:
        logger.error("Failed to parse evaluation response", error=str(e))
        # Return default scores if parsing fails
        return {
            "compliance": {"score": 5, "justification": "Could not parse evaluation", "suggestions": "Re-run evaluation"},
            "tone_consistency": {"score": 5, "justification": "Could not parse evaluation", "suggestions": None},
            "length_accuracy": {"score": 5, "justification": "Could not parse evaluation", "suggestions": None},
            "structure_completeness": {"score": 5, "justification": "Could not parse evaluation", "suggestions": None},
            "purpose_alignment": {"score": 5, "justification": "Could not parse evaluation", "suggestions": None},
            "clarity": {"score": 5, "justification": "Could not parse evaluation", "suggestions": None},
            "professionalism": {"score": 5, "justification": "Could not parse evaluation", "suggestions": None},
            "personalization": {"score": 5, "justification": "Could not parse evaluation", "suggestions": None},
            "risk_balance": {"score": 8, "justification": "Could not parse evaluation", "suggestions": None},
            "disclaimer_accuracy": {"score": 8, "justification": "Could not parse evaluation", "suggestions": None},
            "strengths": [],
            "improvements_needed": ["Evaluation parsing failed - please re-evaluate"]
        }


class EmailEvaluationService:
    """Service for evaluating generated emails using LLM-based scoring."""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.openrouter_api_key
        self.base_url = settings.openrouter_base_url
        self.model = settings.openrouter_model

        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://fmg-muse.local",
            "X-Title": "FMG Muse Email Evaluator",
        }

    async def evaluate_email(
        self,
        email_subject: str,
        email_body: str,
        purpose: PurposeEnum,
        tone: ToneEnum,
        length: LengthEnum,
        original_request: str,
        model: Optional[str] = None,
    ) -> EvaluationMetrics:
        """Evaluate a generated email against quality metrics."""
        import httpx

        # Always use fast evaluation model (ignore user's model for eval)
        effective_model = EVALUATION_MODEL

        logger.info(
            "Starting email evaluation",
            subject_preview=email_subject[:50] if email_subject else "",
            purpose=purpose.value,
            tone=tone.value,
            length=length.value,
            model=effective_model,
        )

        # Build evaluation prompt
        prompt = build_evaluation_prompt(
            email_subject=email_subject,
            email_body=email_body,
            purpose=purpose,
            tone=tone,
            length=length,
            original_request=original_request,
        )

        # Call LLM for evaluation
        payload = {
            "model": effective_model,
            "messages": [
                {"role": "system", "content": "You are an expert email quality evaluator. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,  # Low temperature for consistent, reliable scoring
            "max_tokens": 2000,
        }

        # Minimize reasoning for evaluation
        if "gpt-5" in effective_model.lower():
            payload["reasoning"] = {"effort": "minimal"}

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                )

                if response.status_code != 200:
                    logger.error("Evaluation API error", status_code=response.status_code)
                    raise Exception(f"Evaluation API error: {response.status_code}")

                result = response.json()
                content = result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error("Evaluation failed", error=str(e))
            raise

        # Parse the evaluation response
        eval_data = parse_evaluation_response(content)

        # Build MetricScore objects
        metrics = {}
        for metric_name in EVALUATION_CRITERIA.keys():
            if metric_name in eval_data:
                metric_data = eval_data[metric_name]
                metrics[metric_name] = MetricScore(
                    score=min(10, max(1, metric_data.get("score", 5))),
                    justification=metric_data.get("justification", "No justification provided"),
                    suggestions=metric_data.get("suggestions"),
                )
            else:
                metrics[metric_name] = MetricScore(
                    score=5,
                    justification="Metric not evaluated",
                    suggestions="Re-run evaluation",
                )

        # Calculate overall score
        overall_score = calculate_overall_score(metrics)
        pass_threshold = overall_score >= 7.0

        # Determine if rewrite is recommended
        rewrite_recommended = (
            overall_score < 6.0 or
            metrics["compliance"].score < 6 or
            metrics["purpose_alignment"].score < 5
        )

        logger.info(
            "Email evaluation complete",
            overall_score=overall_score,
            pass_threshold=pass_threshold,
            rewrite_recommended=rewrite_recommended,
        )

        return EvaluationMetrics(
            compliance=metrics["compliance"],
            tone_consistency=metrics["tone_consistency"],
            length_accuracy=metrics["length_accuracy"],
            structure_completeness=metrics["structure_completeness"],
            purpose_alignment=metrics["purpose_alignment"],
            clarity=metrics["clarity"],
            professionalism=metrics["professionalism"],
            personalization=metrics["personalization"],
            risk_balance=metrics["risk_balance"],
            disclaimer_accuracy=metrics["disclaimer_accuracy"],
            overall_score=overall_score,
            pass_threshold=pass_threshold,
            strengths=eval_data.get("strengths", []),
            improvements_needed=eval_data.get("improvements_needed", []),
            rewrite_recommended=rewrite_recommended,
        )

    async def evaluate_and_suggest_improvements(
        self,
        email_subject: str,
        email_body: str,
        purpose: PurposeEnum,
        tone: ToneEnum,
        length: LengthEnum,
        original_request: str,
        model: Optional[str] = None,
    ) -> dict:
        """
        Evaluate email and return actionable improvement suggestions.
        Returns both metrics and a prioritized list of improvements.
        """
        metrics = await self.evaluate_email(
            email_subject=email_subject,
            email_body=email_body,
            purpose=purpose,
            tone=tone,
            length=length,
            original_request=original_request,
            model=model,
        )

        # Build prioritized improvement list based on weights and scores
        priority_improvements = []

        for metric_name, criteria in EVALUATION_CRITERIA.items():
            metric_score = getattr(metrics, metric_name)
            if metric_score.score < 8 and metric_score.suggestions:
                priority_improvements.append({
                    "metric": metric_name,
                    "current_score": metric_score.score,
                    "weight": criteria["weight"],
                    "priority": criteria["weight"] * (10 - metric_score.score),
                    "suggestion": metric_score.suggestions,
                    "justification": metric_score.justification,
                })

        # Sort by priority (highest first)
        priority_improvements.sort(key=lambda x: x["priority"], reverse=True)

        return {
            "metrics": metrics,
            "priority_improvements": priority_improvements[:5],  # Top 5 improvements
            "quick_wins": [
                imp for imp in priority_improvements
                if imp["current_score"] >= 6 and imp["weight"] <= 0.10
            ][:3],  # Easy improvements with smaller impact
        }


# Singleton instance
_evaluation_service = None


def get_evaluation_service() -> EmailEvaluationService:
    """Get the singleton evaluation service instance."""
    global _evaluation_service
    if _evaluation_service is None:
        _evaluation_service = EmailEvaluationService()
    return _evaluation_service
