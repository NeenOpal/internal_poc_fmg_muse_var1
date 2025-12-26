"""
Evaluation metrics and scoring rubric for email quality assessment.
Each metric is scored 1-10 by the LLM evaluator.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class MetricScore(BaseModel):
    """Individual metric score with justification."""
    score: int = Field(..., ge=1, le=10, description="Score from 1-10")
    justification: str = Field(..., description="Brief explanation for the score")
    suggestions: Optional[str] = Field(None, description="Specific improvement suggestions")


class EvaluationMetrics(BaseModel):
    """Complete evaluation metrics for a generated email."""

    # Core Quality Metrics
    compliance: MetricScore = Field(..., description="Adherence to FINRA/SEC compliance rules")
    tone_consistency: MetricScore = Field(..., description="Match between requested and actual tone")
    length_accuracy: MetricScore = Field(..., description="Adherence to target word count")
    structure_completeness: MetricScore = Field(..., description="Proper email structure (subject, greeting, body, closing)")
    purpose_alignment: MetricScore = Field(..., description="Achievement of stated email purpose")

    # Communication Quality Metrics
    clarity: MetricScore = Field(..., description="Clear, readable language")
    professionalism: MetricScore = Field(..., description="Appropriate for financial advisor communications")
    personalization: MetricScore = Field(..., description="Proper use of placeholders and context")

    # Compliance-Specific Metrics
    risk_balance: MetricScore = Field(..., description="Balanced presentation of benefits and risks")
    disclaimer_accuracy: MetricScore = Field(..., description="Appropriate disclaimers included when needed")

    # Aggregate Scores
    overall_score: float = Field(..., description="Weighted average of all metrics")
    pass_threshold: bool = Field(..., description="Whether email meets minimum quality bar (7.0+)")

    # Summary
    strengths: list[str] = Field(default=[], description="Key strengths of the email")
    improvements_needed: list[str] = Field(default=[], description="Priority areas for improvement")
    rewrite_recommended: bool = Field(False, description="Whether a full rewrite is recommended")


# Detailed criteria for each metric - used in the evaluation prompt
EVALUATION_CRITERIA = {
    "compliance": {
        "name": "Regulatory Compliance",
        "weight": 0.20,
        "description": "Adherence to FINRA/SEC rules for financial communications",
        "scoring_guide": {
            10: "Perfect compliance. No prohibited language, all required disclaimers present.",
            8: "Minor issues. Mostly compliant with small improvements possible.",
            6: "Moderate issues. Some compliance gaps that need attention.",
            4: "Significant issues. Multiple compliance violations present.",
            2: "Major violations. Contains prohibited language or missing critical disclaimers.",
            1: "Severely non-compliant. Would likely trigger regulatory action."
        },
        "check_points": [
            "No guarantee-related terms (guaranteed, risk-free, cannot lose)",
            "No promissory returns (will return X%, will definitely)",
            "No false urgency (act now, limited time, last chance)",
            "Forward-looking statements use qualifying language (we believe, in our opinion)",
            "Performance data includes required disclaimers",
            "Risks disclosed with equal prominence to benefits",
            "No specific numerical predictions for returns",
            "Testimonials include 'individual results may vary' if applicable",
            "Volatile assets (crypto, leverage) include volatility warnings"
        ]
    },

    "tone_consistency": {
        "name": "Tone Consistency",
        "weight": 0.10,
        "description": "Match between requested tone and actual email tone",
        "scoring_guide": {
            10: "Perfect match. Tone is exactly as requested throughout.",
            8: "Strong match. Tone is consistent with minor variations.",
            6: "Acceptable. Generally correct tone with some inconsistencies.",
            4: "Mismatched. Tone frequently doesn't match request.",
            2: "Wrong tone. Email reads as different tone than requested.",
            1: "Completely misaligned. Opposite of requested tone."
        },
        "tone_expectations": {
            "professional": "Business-appropriate, clear, direct, respectful",
            "formal": "Traditional, proper titles, no contractions, 'Dear' and 'Sincerely'",
            "friendly": "Warm, personable, conversational but professional",
            "casual": "Relaxed, contractions okay, 'Hey' and 'Thanks'"
        }
    },

    "length_accuracy": {
        "name": "Length Accuracy",
        "weight": 0.08,
        "description": "Adherence to requested email length",
        "scoring_guide": {
            10: "Perfect. Within target word count range.",
            8: "Close. Within 10% of target range.",
            6: "Acceptable. Within 25% of target range.",
            4: "Off target. 25-50% deviation from target.",
            2: "Significantly off. More than 50% deviation.",
            1: "Completely wrong length. Extremely short or excessively long."
        },
        "length_targets": {
            "short": "50-100 words, 2-4 sentences",
            "medium": "100-200 words, 5-8 sentences",
            "long": "200-400 words, 9-15 sentences"
        }
    },

    "structure_completeness": {
        "name": "Structure Completeness",
        "weight": 0.10,
        "description": "Proper email structure with all required components",
        "scoring_guide": {
            10: "Complete. Subject, greeting, body paragraphs, closing, signature all present and well-formatted.",
            8: "Nearly complete. All elements present with minor formatting issues.",
            6: "Acceptable. Most elements present, one may be weak or missing.",
            4: "Incomplete. Missing one or more key elements.",
            2: "Poor structure. Multiple missing elements.",
            1: "No structure. Does not resemble a proper email."
        },
        "required_elements": [
            "Subject line that accurately reflects content",
            "Appropriate greeting for the tone",
            "Well-organized body paragraphs",
            "Clear closing statement",
            "Signature with [Your Name] placeholder"
        ]
    },

    "purpose_alignment": {
        "name": "Purpose Alignment",
        "weight": 0.15,
        "description": "Achievement of the stated email purpose",
        "scoring_guide": {
            10: "Perfectly aligned. Email clearly achieves its stated purpose.",
            8: "Well aligned. Purpose is achieved with minor additions possible.",
            6: "Adequately aligned. Purpose is partially achieved.",
            4: "Weak alignment. Email drifts from intended purpose.",
            2: "Misaligned. Email does not address the stated purpose.",
            1: "Wrong purpose. Email appears to be for a different purpose entirely."
        },
        "purpose_expectations": {
            "relationship_builder": "Strengthens connection, shows appreciation, builds rapport",
            "educational_content": "Explains concepts clearly, provides valuable information",
            "follow_up": "References previous communication, requests update or action",
            "feedback_request": "Asks for specific input politely",
            "scheduling": "Proposes or confirms meeting times",
            "other": "Achieves the specific goal stated in details"
        }
    },

    "clarity": {
        "name": "Clarity",
        "weight": 0.10,
        "description": "Clear, readable language that's easy to understand",
        "scoring_guide": {
            10: "Crystal clear. Easy to read, no ambiguity, well-organized.",
            8: "Very clear. Minor improvements possible.",
            6: "Adequately clear. Some sentences could be clearer.",
            4: "Unclear. Multiple confusing passages.",
            2: "Confusing. Difficult to understand the message.",
            1: "Incomprehensible. Cannot determine the intended message."
        },
        "check_points": [
            "Sentences are concise and well-constructed",
            "No jargon without explanation",
            "Logical flow between paragraphs",
            "Clear action items or next steps if applicable",
            "No ambiguous pronouns or references"
        ]
    },

    "professionalism": {
        "name": "Professionalism",
        "weight": 0.10,
        "description": "Appropriate for financial advisor-client communications",
        "scoring_guide": {
            10: "Highly professional. Exemplary financial services communication.",
            8: "Professional. Minor polish could improve.",
            6: "Acceptable. Professional but not exceptional.",
            4: "Unprofessional elements. Some inappropriate content or language.",
            2: "Unprofessional. Not suitable for client communication.",
            1: "Completely inappropriate. Would damage client relationships."
        },
        "check_points": [
            "Appropriate vocabulary for financial services",
            "Respectful and courteous tone",
            "No slang or inappropriate language (unless casual tone requested)",
            "Proper grammar and spelling",
            "Confidence without arrogance"
        ]
    },

    "personalization": {
        "name": "Personalization",
        "weight": 0.07,
        "description": "Proper use of placeholders and contextual details",
        "scoring_guide": {
            10: "Excellent. All placeholders clear and context well-integrated.",
            8: "Good. Placeholders appropriate with good context use.",
            6: "Acceptable. Placeholders present but could be better integrated.",
            4: "Weak. Missing important placeholders or poor context use.",
            2: "Poor. Made up specific details instead of using placeholders.",
            1: "Failed. Invented names/details, no placeholders, ignores context."
        },
        "check_points": [
            "Uses [Recipient Name], [Your Name], [Company Name] appropriately",
            "Uses [Date], [Time], [Location] for unspecified details",
            "Does not invent specific names or details",
            "Incorporates provided context naturally",
            "Placeholders are clearly identifiable"
        ]
    },

    "risk_balance": {
        "name": "Risk-Benefit Balance",
        "weight": 0.05,
        "description": "Balanced presentation when discussing investments or strategies",
        "scoring_guide": {
            10: "Perfectly balanced. Risks and benefits equally prominent.",
            8: "Well balanced. Good coverage of both sides.",
            6: "Acceptable. Some imbalance but not misleading.",
            4: "Unbalanced. Emphasizes benefits over risks.",
            2: "Significantly unbalanced. Minimizes or hides risks.",
            1: "Dangerously unbalanced. Presents investments as one-sided positive."
        },
        "check_points": [
            "Benefits and risks given equal prominence",
            "No minimization of downside potential",
            "Acknowledgment of uncertainty",
            "Appropriate caveats for any positive statements",
            "N/A for emails not discussing investments"
        ]
    },

    "disclaimer_accuracy": {
        "name": "Disclaimer Accuracy",
        "weight": 0.05,
        "description": "Appropriate disclaimers included when needed",
        "scoring_guide": {
            10: "Perfect. All necessary disclaimers present and well-placed.",
            8: "Good. Disclaimers present with minor improvements possible.",
            6: "Acceptable. Most disclaimers present.",
            4: "Incomplete. Missing important disclaimers.",
            2: "Poor. Critical disclaimers absent.",
            1: "Failed. No disclaimers where clearly required."
        },
        "required_disclaimers": {
            "performance_data": "Past performance does not guarantee future results",
            "volatile_assets": "Highly volatile, could lose some or all investment",
            "recommendations": "Suitability depends on individual circumstances",
            "testimonials": "Individual results may vary",
            "backtests": "Hypothetical results have inherent limitations"
        }
    }
}


def calculate_overall_score(metrics: dict[str, MetricScore]) -> float:
    """Calculate weighted average score from individual metrics."""
    total_weight = 0
    weighted_sum = 0

    for metric_name, score in metrics.items():
        if metric_name in EVALUATION_CRITERIA:
            weight = EVALUATION_CRITERIA[metric_name]["weight"]
            weighted_sum += score.score * weight
            total_weight += weight

    if total_weight == 0:
        return 0.0

    return round(weighted_sum / total_weight, 2)


def get_metric_names() -> list[str]:
    """Return list of all metric names."""
    return list(EVALUATION_CRITERIA.keys())


def get_metric_weights() -> dict[str, float]:
    """Return mapping of metric names to their weights."""
    return {name: criteria["weight"] for name, criteria in EVALUATION_CRITERIA.items()}
